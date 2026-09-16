# -*- coding: utf-8 -*-
"""Pruebas de gobernanza (modelo de prevencion de delitos) y de proteccion de datos personales."""

import json
import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaGobernanza(PruebaConCarpeta):
    """El modulo tal como lo llamara el agente."""

    def setUp(self):
        super(PruebaGobernanza, self).setUp()
        from modulos import gobernanza
        self.modulo = gobernanza
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria",
                               "tamano": "pequena", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def _revisar(self, **extra):
        return self.modulo.revisar(dict(self.opciones, **extra)).resultado

    def test_revisar_parte_sin_respuestas_y_guarda_el_archivo(self):
        resultado = self._revisar()
        self.assertEqual(resultado["avance_pct"], 0.0)
        self.assertEqual(resultado["estado"], "sin gestion")
        self.assertEqual(resultado["respondidas"], 0)
        self.assertEqual(len(resultado["preguntas_pendientes"]), resultado["total_preguntas"])
        self.assertTrue(os.path.isfile(resultado["guardado_en"]))
        self.assertTrue(resultado["guardado_en"].endswith("gobernanza.json"))
        # cada pregunta pendiente llega lista para conversarla
        primera = resultado["preguntas_pendientes"][0]
        for clave in ("pregunta", "porque_importa", "si_no_lo_tiene", "base"):
            self.assertIn(clave, primera)

    def test_responder_sube_el_avance_y_reduce_las_pendientes(self):
        antes = self._revisar()
        self.modulo.responder(dict(self.opciones, pregunta="canal-denuncias", estado="cumple",
                                   nota="Correo dedicado publicado", responsable="Jefa de administracion"))
        self.modulo.responder(dict(self.opciones, pregunta="codigo-etica", estado="parcial"))
        despues = self._revisar()
        self.assertGreater(despues["avance_pct"], antes["avance_pct"])
        self.assertEqual(despues["respondidas"], 2)
        self.assertEqual(len(despues["preguntas_pendientes"]), antes["total_preguntas"] - 2)
        self.assertGreater(despues["avance_por_bloque"]["Canal de denuncias"], 0)

    def test_responder_valida_la_pregunta_y_el_estado(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.responder(dict(self.opciones, pregunta="inventada", estado="cumple"))
        self.assertIn("inventada", contexto.exception.mensaje)
        with self.assertRaises(Problema) as contexto:
            self.modulo.responder(dict(self.opciones, pregunta="encargado", estado="mas o menos"))
        self.assertIn("cumple", contexto.exception.sugerencia)
        with self.assertRaises(Problema) as contexto:
            self.modulo.responder(dict(self.opciones, estado="cumple"))
        self.assertIn("pregunta", contexto.exception.mensaje.lower())

    def test_no_aplica_sale_del_calculo(self):
        for pregunta in ("organo-revision", "conflictos-interes"):
            self.modulo.responder(dict(self.opciones, pregunta=pregunta, estado="cumple"))
        for pregunta in ("memoria-cmf", "seleccion-directores"):
            self.modulo.responder(dict(self.opciones, pregunta=pregunta, estado="no_aplica"))
        resultado = self._revisar()
        self.assertEqual(resultado["avance_por_bloque"]["Gobierno corporativo"], 100.0)
        ids = [b["id"] for b in resultado["brechas_priorizadas"]]
        self.assertNotIn("memoria-cmf", ids)

    def test_brechas_ordenadas_por_prioridad(self):
        resultado = self._revisar()
        prioridades = [b["prioridad"] for b in resultado["brechas_priorizadas"]]
        self.assertEqual(prioridades, sorted(prioridades, reverse=True))
        # lo mas caro de no tener es de riesgo legal y peso alto
        self.assertEqual(prioridades[0], 9)
        self.assertTrue(all(b["base"] for b in resultado["brechas_priorizadas"]))

    def test_documentos_son_borradores_con_estructura(self):
        for tipo in ("codigo-etica", "politica-canal-denuncias", "matriz-riesgos-delitos"):
            respuesta = self.modulo.documento(dict(self.opciones, tipo=tipo))
            self.assertTrue(os.path.isfile(respuesta.resultado["archivo"]))
            self.assertIn("borrador", " ".join(respuesta.advertencias).lower())
        with self.assertRaises(Problema):
            self.modulo.documento(dict(self.opciones, tipo="inventado"))
        with self.assertRaises(Problema) as contexto:
            self.modulo.documento(dict(self.opciones))
        self.assertIn("codigo-etica", contexto.exception.sugerencia)

    def test_informe_refleja_la_ultima_respuesta(self):
        self.modulo.responder(dict(self.opciones, pregunta="encargado", estado="cumple"))
        resultado = self.modulo.informe_html(self.opciones).resultado
        self.assertTrue(os.path.isfile(resultado["archivo"]))
        self.assertGreater(resultado["avance_pct"], 0)
        with open(resultado["archivo"], encoding="utf-8") as archivo:
            contenido = archivo.read()
        self.assertIn("Gobernanza y modelo de prevencion de delitos", contenido)
        self.assertIn("Avance por bloque", contenido)

    def test_avisa_que_la_vigencia_de_la_ley_21595_no_esta_verificada(self):
        respuesta = self.modulo.revisar(self.opciones)
        textos = " ".join(respuesta.advertencias)
        self.assertIn("21.595", textos)
        self.assertIn("NO esta confirmada", textos)
        self.assertIn("no asesoria legal", textos)
        self.assertIn("docs/investigacion/05-chile-peru-gobernanza-clima-datos.md", respuesta.fuentes)

    def test_empresa_de_otro_pais_recibe_el_aviso_correspondiente(self):
        espacio.crear_empresa({"nombre": "Prueba Peru SAC", "pais": "PE", "sector": "Industria"},
                              raiz=self.carpeta)
        opciones = {"raiz": self.carpeta, "empresa": "Prueba Peru SAC"}
        textos = " ".join(self.modulo.revisar(opciones).advertencias)
        self.assertIn("ley chilena", textos)
        self.assertIn("asesoria local", textos)


class PruebaDatosPersonales(PruebaConCarpeta):
    def setUp(self):
        super(PruebaDatosPersonales, self).setUp()
        from modulos import datos_personales
        self.modulo = datos_personales
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria",
                               "tamano": "pequena", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def _registrar_ficha(self, **extra):
        datos = {"nombre": "Ficha de trabajadores", "area": "Personas",
                 "titulares": "trabajadores y postulantes",
                 "categorias_datos": "identificacion, contacto, licencias medicas",
                 "finalidad": "administrar la relacion laboral", "base_licitud": "contrato",
                 "destinatarios": "jefatura de personas y contadora externa",
                 "donde_se_guarda": "carpeta del servidor", "conservacion": "mientras dure el contrato",
                 "sale_del_pais": "no"}
        datos.update(extra)
        return self.modulo.registrar(dict(self.opciones, **datos))

    def test_inventario_entrega_la_guia_y_los_avisos(self):
        respuesta = self.modulo.inventario(self.opciones)
        resultado = respuesta.resultado
        self.assertEqual(resultado["total_actividades"], 0)
        self.assertEqual(len(resultado["contenidos_minimos_del_registro"]), 7)
        self.assertTrue(resultado["preguntas_por_actividad"])
        self.assertIn("consentimiento", resultado["bases_de_licitud"])
        textos = " ".join(respuesta.advertencias)
        self.assertIn("1 de diciembre de 2026", textos)
        self.assertIn("no se copian datos de personas", textos)

    def test_registrar_crea_y_luego_actualiza_la_misma_actividad(self):
        primera = self._registrar_ficha().resultado
        self.assertEqual(primera["total_actividades"], 1)
        self.assertTrue(primera["actividad"]["completa"])
        segunda = self.modulo.registrar(dict(self.opciones, nombre="Ficha de trabajadores",
                                             conservacion="cinco años despues del termino")).resultado
        self.assertEqual(segunda["total_actividades"], 1)
        self.assertIn("Actualizado", segunda["mensaje"])
        with open(primera["guardado_en"], encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        self.assertEqual(guardado["actividades"][0]["conservacion"], "cinco años despues del termino")

    def test_registrar_valida_el_nombre_y_la_base_de_licitud(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.registrar(dict(self.opciones))
        self.assertIn("nombre", contexto.exception.mensaje.lower())
        with self.assertRaises(Problema) as contexto:
            self._registrar_ficha(base_licitud="porque si")
        self.assertIn("interes_legitimo", contexto.exception.sugerencia)

    def test_no_guarda_datos_personales_reales(self):
        for campo, valor in (("destinatarios", "juan.perez@empresa.cl"),
                             ("titulares", "trabajador 12.345.678-9"),
                             ("categorias_datos", "contacto +56 9 1234 5678")):
            with self.assertRaises(Problema) as contexto:
                self._registrar_ficha(**{campo: valor})
            self.assertIn("no se guardan datos de personas reales", contexto.exception.mensaje)
        resultado = self.modulo.inventario(self.opciones).resultado
        self.assertEqual(resultado["total_actividades"], 0)

    def test_actividad_incompleta_muestra_lo_que_falta(self):
        self.modulo.registrar(dict(self.opciones, nombre="Base de correos de marketing",
                                   area="Comercial", base_licitud="consentimiento"))
        evaluacion = self.modulo.evaluar(self.opciones).resultado
        incompletas = evaluacion["actividades_incompletas"]
        self.assertEqual(len(incompletas), 1)
        self.assertIn("conservacion", incompletas[0]["falta"])
        self.assertIn("sale_del_pais", incompletas[0]["falta"])

    def test_evaluar_detecta_los_tratamientos_de_alto_riesgo(self):
        self._registrar_ficha(datos_sensibles="si")
        self.modulo.registrar(dict(self.opciones, nombre="Camaras de seguridad", area="Operaciones",
                                   videovigilancia="si", base_licitud="interes_legitimo"))
        respuesta = self.modulo.evaluar(self.opciones)
        alto = {a["actividad"]: a["motivos"] for a in respuesta.resultado["con_evaluacion_de_impacto"]}
        self.assertIn("Ficha de trabajadores", alto)
        self.assertIn("Camaras de seguridad", alto)
        self.assertIn("datos sensibles", " ".join(alto["Ficha de trabajadores"]))
        self.assertIn("zona de acceso publico", " ".join(alto["Camaras de seguridad"]))
        self.assertEqual(respuesta.resultado["con_datos_sensibles"], ["Ficha de trabajadores"])

    def test_datos_sensibles_con_consentimiento_no_gatillan_la_evaluacion(self):
        self._registrar_ficha(datos_sensibles="si", base_licitud="consentimiento")
        evaluacion = self.modulo.evaluar(self.opciones).resultado
        self.assertEqual(evaluacion["con_evaluacion_de_impacto"], [])
        self.assertEqual(evaluacion["con_datos_sensibles"], ["Ficha de trabajadores"])

    def test_evaluar_guarda_las_cuatro_obligaciones_y_valida_la_respuesta(self):
        respuesta = self.modulo.evaluar(dict(self.opciones, deber_informacion="no_cumple",
                                             seguridad="parcial"))
        obligaciones = {o["id"]: o for o in respuesta.resultado["obligaciones"]}
        self.assertEqual(len(obligaciones), 4)
        self.assertEqual(obligaciones["deber_informacion"]["estado"], "no_cumple")
        self.assertEqual(obligaciones["seguridad"]["estado"], "parcial")
        self.assertEqual(obligaciones["derechos"]["estado"], "sin_responder")
        self.assertIn("sin dilaciones indebidas", obligaciones["vulneraciones"]["que_exige"])
        # la respuesta queda guardada entre llamadas
        segunda = self.modulo.evaluar(self.opciones).resultado
        self.assertEqual({o["id"]: o["estado"] for o in segunda["obligaciones"]}["deber_informacion"],
                         "no_cumple")
        with self.assertRaises(Problema):
            self.modulo.evaluar(dict(self.opciones, derechos="quizas"))

    def test_documentos_son_borradores_e_incluyen_lo_registrado(self):
        self._registrar_ficha()
        for tipo in ("politica-privacidad", "registro-actividades", "procedimiento-derechos"):
            respuesta = self.modulo.documento(dict(self.opciones, tipo=tipo))
            self.assertTrue(os.path.isfile(respuesta.resultado["archivo"]))
            self.assertIn("borrador", " ".join(respuesta.advertencias).lower())
        registro = self.modulo.documento(dict(self.opciones, tipo="registro-actividades")).resultado
        self.assertEqual(registro["actividades_incluidas"], 1)
        with self.assertRaises(Problema) as contexto:
            self.modulo.documento(dict(self.opciones, tipo="inventado"))
        self.assertIn("politica-privacidad", contexto.exception.sugerencia)

    def test_informe_html_se_escribe_y_resume_el_estado(self):
        self._registrar_ficha(datos_sensibles="si")
        resultado = self.modulo.informe_html(dict(self.opciones, seguridad="cumple")).resultado
        self.assertTrue(os.path.isfile(resultado["archivo"]))
        self.assertEqual(resultado["total_actividades"], 1)
        with open(resultado["archivo"], encoding="utf-8") as archivo:
            contenido = archivo.read()
        self.assertIn("Proteccion de datos personales", contenido)
        self.assertIn("Que hacer si hay una filtracion", contenido)
        self.assertIn("sin dilaciones indebidas", contenido)

    def test_avisos_de_peru_y_de_datos_sin_verificar(self):
        espacio.crear_empresa({"nombre": "Prueba Peru SAC", "pais": "PE", "sector": "Industria"},
                              raiz=self.carpeta)
        textos = " ".join(self.modulo.inventario(
            {"raiz": self.carpeta, "empresa": "Prueba Peru SAC"}).advertencias)
        self.assertIn("48 horas", textos)
        self.assertIn("NO", textos)
        pendiente = " ".join(self.modulo.evaluar(self.opciones).advertencias)
        self.assertIn("delegado de proteccion de datos", pendiente)
        self.assertIn("NO estan confirmados", pendiente)


if __name__ == "__main__":
    unittest.main()
