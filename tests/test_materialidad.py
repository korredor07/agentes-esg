# -*- coding: utf-8 -*-
"""Pruebas de la doble materialidad (calculo de los dos ejes y modulo del motor)."""

import json
import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import materialidad  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


def asunto(nombre, escala, alcance, irremediabilidad, probabilidad_impacto,
           magnitud_financiera, probabilidad_financiera, **extra):
    """Arma un asunto evaluado con las seis notas."""
    datos = {
        "id": espacio.texto_a_slug(nombre), "nombre": nombre, "dimension": "ambiental",
        "escala": escala, "alcance": alcance, "irremediabilidad": irremediabilidad,
        "probabilidad_impacto": probabilidad_impacto,
        "magnitud_financiera": magnitud_financiera,
        "probabilidad_financiera": probabilidad_financiera,
    }
    datos.update(extra)
    return datos


CUATRO_CASOS = [
    asunto("Las dos cosas", 5, 5, 5, 5, 5, 5),
    asunto("Solo impacto", 4, 5, 3, 2, 2, 2),
    asunto("Solo dinero", 1, 1, 1, 1, 5, 4),
    asunto("Ninguna de las dos", 1, 1, 1, 1, 1, 1),
]


class PruebaCalculo(unittest.TestCase):

    def test_asuntos_sugeridos_mezcla_comunes_y_rubro(self):
        agro = materialidad.asuntos_sugeridos("Agroindustria - conservas de fruta")
        ids = [a["id"] for a in agro]
        self.assertIn("clima-energia", ids)
        self.assertIn("inocuidad", ids)
        self.assertEqual(len(ids), len(set(ids)), "no puede haber asuntos repetidos")
        self.assertTrue(all(a.get("nombre") and a.get("dimension") for a in agro))
        generica = materialidad.asuntos_sugeridos("")
        self.assertNotIn("inocuidad", [a["id"] for a in generica])
        self.assertIn("clima-energia", [a["id"] for a in generica])

    def test_familia_de_sector(self):
        self.assertEqual(materialidad.familia_de_sector("Minera de cobre")[0], "mineria")
        self.assertEqual(materialidad.familia_de_sector("Constructora de viviendas")[0], "construccion")
        self.assertEqual(materialidad.familia_de_sector("Tecnología y software")[0], "tecnologia")
        self.assertEqual(materialidad.familia_de_sector("")[0], "general")
        self.assertEqual(materialidad.familia_de_sector(None)[0], "general")

    def test_formulas_de_los_dos_ejes(self):
        gravedad, impacto = materialidad.puntaje_impacto(4, 5, 3, 2)
        self.assertEqual(gravedad, 4.0)
        self.assertEqual(impacto, 3.4)  # 0,7 x 4 + 0,3 x 2
        self.assertEqual(materialidad.puntaje_financiero(4, 1), 2.0)  # raiz de 4 x 1
        self.assertEqual(materialidad.puntaje_financiero(5, 5), 5.0)

    def test_en_derechos_humanos_la_gravedad_manda(self):
        _, sin_bandera = materialidad.puntaje_impacto(5, 5, 5, 1)
        _, con_bandera = materialidad.puntaje_impacto(5, 5, 5, 1, derechos_humanos=True)
        self.assertEqual(sin_bandera, 3.8)
        self.assertEqual(con_bandera, 5.0)

    def test_cuadrantes_y_orden(self):
        resultado = materialidad.evaluar(CUATRO_CASOS, umbral=3)
        nombres = [a["nombre"] for a in resultado["asuntos"]]
        self.assertEqual(nombres, ["Las dos cosas", "Solo dinero", "Solo impacto", "Ninguna de las dos"])
        cuadrantes = {a["nombre"]: a["cuadrante"] for a in resultado["asuntos"]}
        self.assertEqual(cuadrantes["Las dos cosas"], "doble")
        self.assertEqual(cuadrantes["Solo impacto"], "impacto")
        self.assertEqual(cuadrantes["Solo dinero"], "financiera")
        self.assertEqual(cuadrantes["Ninguna de las dos"], "no_material")
        self.assertEqual(resultado["total_materiales"], 3)
        self.assertEqual([a["nombre"] for a in resultado["no_materiales"]], ["Ninguna de las dos"])

    def test_el_umbral_cambia_que_es_material(self):
        blando = materialidad.evaluar(CUATRO_CASOS, umbral=3)
        exigente = materialidad.evaluar(CUATRO_CASOS, umbral=4.5)
        self.assertEqual(blando["total_materiales"], 3)
        self.assertEqual(exigente["total_materiales"], 1)
        self.assertEqual(exigente["umbral"], 4.5)
        por_defecto = materialidad.evaluar(CUATRO_CASOS)
        self.assertEqual(por_defecto["umbral"], materialidad.UMBRAL_POR_DEFECTO)

    def test_asunto_incompleto_queda_pendiente_y_no_se_inventa(self):
        a_medias = dict(CUATRO_CASOS[0])
        del a_medias["magnitud_financiera"]
        resultado = materialidad.evaluar([a_medias, CUATRO_CASOS[1]], umbral=3)
        self.assertEqual(resultado["total_evaluados"], 1)
        self.assertEqual(len(resultado["pendientes"]), 1)
        pendiente = resultado["pendientes"][0]
        self.assertIn("magnitud del efecto financiero", pendiente["faltan"])
        self.assertIn("--magnitud-financiera", pendiente["faltan_opciones"])
        self.assertNotIn("puntaje_impacto", pendiente)

    def test_notas_invalidas_dan_mensaje_util(self):
        with self.assertRaises(Problema) as caja:
            materialidad.evaluar([asunto("Agua", 4, 4, 4, 4, 4, 9)])
        self.assertIn("1 al 5", caja.exception.mensaje + caja.exception.sugerencia)
        with self.assertRaises(Problema):
            materialidad.evaluar([asunto("Agua", 4, 4, 4, 4, 4, "bastante")])
        with self.assertRaises(Problema):
            materialidad.evaluar([{"nombre": "", "escala": 3}])
        with self.assertRaises(Problema):
            materialidad.evaluar(CUATRO_CASOS, umbral="mucho")
        with self.assertRaises(Problema):
            materialidad.evaluar(CUATRO_CASOS, umbral=9)

    def test_acepta_notas_escritas_con_coma_y_texto(self):
        resultado = materialidad.evaluar([asunto("Agua", "4,5", "4", 4, 4, "3", 3)], umbral=3)
        self.assertEqual(resultado["total_evaluados"], 1)
        self.assertEqual(resultado["asuntos"][0]["criterios"]["escala"], 4.5)

    def test_matriz_entrega_un_punto_por_asunto(self):
        matriz = materialidad.matriz(CUATRO_CASOS, umbral=3)
        self.assertEqual(len(matriz["puntos"]), 4)
        primero = matriz["puntos"][0]
        self.assertEqual(primero["nombre"], "Las dos cosas")
        self.assertEqual((primero["x"], primero["y"]), (5.0, 5.0))
        self.assertTrue(primero["color"].startswith("#"))
        self.assertEqual(matriz["eje_x"]["maximo"], 5.0)
        self.assertEqual(matriz["sin_evaluar"], [])

    def test_matriz_avisa_de_los_asuntos_sin_evaluar(self):
        incompleto = dict(CUATRO_CASOS[1])
        del incompleto["probabilidad_financiera"]
        matriz = materialidad.matriz([CUATRO_CASOS[0], incompleto], umbral=3)
        self.assertEqual(len(matriz["puntos"]), 1)
        self.assertEqual(matriz["sin_evaluar"], ["Solo impacto"])

    def test_el_resultado_viaja_con_su_metodo_y_su_aviso(self):
        resultado = materialidad.evaluar(CUATRO_CASOS, umbral=3)
        self.assertIn("umbral", resultado["metodologia"])
        self.assertIn("decisiones de la empresa", resultado["aviso"])
        self.assertIn("06-marcos-reporte", resultado["fuente"])


class PruebaModuloMaterialidad(PruebaConCarpeta):
    """Prueba el modulo tal como lo llamara el agente."""

    def setUp(self):
        super(PruebaModuloMaterialidad, self).setUp()
        from modulos import materialidad as modulo
        self.modulo = modulo
        espacio.crear_empresa({"nombre": "Conservas Prueba", "pais": "CL",
                               "sector": "Agroindustria - conservas", "tamano": "pequena",
                               "anio_base": 2025, "sitios": [{"nombre": "Planta"}]}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Conservas Prueba"}

    def _registrar(self, nombre, notas=(5, 5, 5, 5, 5, 5), **extra):
        datos = dict(zip(materialidad.CRITERIOS, notas))
        datos.update(extra)
        return self.modulo.registrar(dict(self.opciones, asunto=nombre, **datos))

    def test_propone_la_lista_segun_el_sector(self):
        salida = self.modulo.asuntos(self.opciones)
        self.assertEqual(salida.resultado["actividad_reconocida"], "Alimentos, bebidas y agroindustria")
        ids = [a["id"] for a in salida.resultado["asuntos"]]
        self.assertIn("inocuidad", ids)
        self.assertTrue(all(a["estado"] == "sin evaluar" for a in salida.resultado["asuntos"]))
        self.assertEqual(len(salida.resultado["preguntas"]), 6)

    def test_registrar_y_evaluar_de_punta_a_punta(self):
        self._registrar("agua", (5, 4, 4, 5, 4, 4), nota="La planta esta en zona de escasez")
        self._registrar("inocuidad", (2, 2, 1, 1, 2, 1))
        salida = self.modulo.evaluar(self.opciones)
        resultado = salida.resultado
        self.assertEqual(resultado["total_evaluados"], 2)
        self.assertEqual(resultado["total_materiales"], 1)
        self.assertEqual(resultado["materiales"][0]["nombre"], "Agua: consumo y descargas")
        self.assertTrue(os.path.isfile(resultado["guardado_en"]))
        with open(resultado["guardado_en"], encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        self.assertIn("agua", guardado["asuntos"])
        self.assertEqual(guardado["asuntos"]["agua"]["nota"], "La planta esta en zona de escasez")
        self.assertTrue(guardado["ultima_evaluacion"]["asuntos"])

    def test_se_puede_evaluar_en_dos_tandas(self):
        self.modulo.registrar(dict(self.opciones, asunto="agua", escala=4, alcance=4,
                                   irremediabilidad=3, probabilidad_impacto=4))
        salida = self.modulo.evaluar(self.opciones)
        self.assertEqual(salida.resultado["total_evaluados"], 0)
        self.assertEqual(salida.resultado["pendientes"][0]["nombre"], "Agua: consumo y descargas")
        self.modulo.registrar(dict(self.opciones, asunto="agua", magnitud_financiera=4,
                                   probabilidad_financiera=4))
        salida = self.modulo.evaluar(self.opciones)
        self.assertEqual(salida.resultado["total_evaluados"], 1)
        self.assertEqual(salida.resultado["pendientes"], [])

    def test_acepta_el_nombre_completo_y_los_asuntos_propios(self):
        self._registrar("Agua: consumo y descargas", (4, 4, 4, 4, 4, 4))
        salida = self._registrar("Olor de la planta en verano", (4, 4, 3, 5, 3, 3))
        self.assertTrue(any("no estaba en la lista sugerida" in a for a in salida.advertencias))
        lista = self.modulo.asuntos(self.opciones).resultado["asuntos"]
        propios = [a for a in lista if a["origen"] == "agregado por la empresa"]
        self.assertEqual(len(propios), 1)
        self.assertEqual(propios[0]["nombre"], "Olor de la planta en verano")
        evaluacion = self.modulo.evaluar(self.opciones).resultado
        self.assertEqual(evaluacion["total_evaluados"], 2)

    def test_errores_explicados_para_una_persona_no_tecnica(self):
        with self.assertRaises(Problema) as caja:
            self.modulo.registrar(dict(self.opciones))
        self.assertIn("--asunto", caja.exception.sugerencia)
        with self.assertRaises(Problema) as caja:
            self.modulo.registrar(dict(self.opciones, asunto="agua"))
        self.assertIn("seis notas", caja.exception.sugerencia)
        with self.assertRaises(Problema) as caja:
            self.modulo.registrar(dict(self.opciones, asunto="agua", escala=True))
        self.assertIn("--escala", caja.exception.mensaje)
        with self.assertRaises(Problema):
            self.modulo.registrar(dict(self.opciones, asunto="agua", escala=4, dimension="economica"))
        with self.assertRaises(Problema) as caja:
            self.modulo.evaluar(self.opciones)
        self.assertIn("materialidad asuntos", caja.exception.sugerencia)
        with self.assertRaises(Problema):
            self.modulo.informe_html(self.opciones)

    def test_el_umbral_queda_guardado(self):
        self._registrar("agua", (4, 4, 4, 4, 4, 4))
        self.modulo.evaluar(dict(self.opciones, umbral="4,5"))
        salida = self.modulo.evaluar(self.opciones)
        self.assertEqual(salida.resultado["umbral"], 4.5)
        self.assertEqual(salida.resultado["total_materiales"], 0)
        self.assertTrue(any("ningun asunto quedo como material" in a for a in salida.advertencias))

    def test_informe_dibuja_la_matriz(self):
        self._registrar("agua", (5, 4, 4, 5, 4, 4))
        self._registrar("clima-energia", (3, 3, 3, 3, 4, 4))
        self._registrar("etica-anticorrupcion", (1, 1, 1, 1, 1, 1))
        salida = self.modulo.informe_html(self.opciones)
        archivo = salida.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as fuente:
            contenido = fuente.read()
        self.assertIn("Doble materialidad", contenido)
        self.assertIn("Matriz de doble materialidad", contenido)
        self.assertIn("<svg", contenido)
        self.assertIn("Agua: consumo y descargas", contenido)
        self.assertIn("Como se calculo", contenido)


if __name__ == "__main__":
    unittest.main()
