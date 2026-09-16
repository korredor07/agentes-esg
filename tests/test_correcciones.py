# -*- coding: utf-8 -*-
"""Pruebas de las correcciones que salieron de la prueba de uso real.

Cada una corresponde a un hallazgo documentado en docs/prueba-de-uso.md.
"""

import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import aplicabilidad, carbono  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaCalidadDelDato(unittest.TestCase):
    """H4: la columna «Calidad del dato» de la plantilla no se leia."""

    def setUp(self):
        self.factores = carbono.cargar_factores()
        self.pcg = carbono.cargar_pcg()

    def test_lee_la_columna_de_la_plantilla(self):
        fila = {"_fila": 2, "periodo": "2025", "recurso": "electricidad", "cantidad": 1000,
                "unidad": "kWh", "pais": "CL", "calidad_del_dato": "reportado"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg, "AR5")
        self.assertEqual(resultado["calidad_dato"], "reportado")

    def test_sigue_aceptando_la_clave_corta(self):
        fila = {"_fila": 2, "periodo": "2025", "recurso": "electricidad", "cantidad": 1000,
                "unidad": "kWh", "pais": "CL", "calidad_dato": "verificado"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg, "AR5")
        self.assertEqual(resultado["calidad_dato"], "verificado")

    def test_calidad_desconocida_avisa(self):
        fila = {"_fila": 2, "periodo": "2025", "recurso": "electricidad", "cantidad": 1000,
                "unidad": "kWh", "pais": "CL", "calidad_del_dato": "mas o menos"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg, "AR5")
        self.assertEqual(resultado["calidad_dato"], "estimado")
        self.assertTrue(any("calidad de dato" in a for a in resultado["advertencias"]))


class PruebaDensidades(unittest.TestCase):
    """H2: el gas se compra en kilos y el factor esta en litros."""

    def setUp(self):
        self.factores = carbono.cargar_factores()
        self.pcg = carbono.cargar_pcg()
        self.densidades = carbono.cargar_densidades()

    def test_tabla_de_densidades_con_fuente(self):
        chilena = carbono.densidad_de("glp", "CL", self.densidades)
        internacional = carbono.densidad_de("glp", "PE", self.densidades)
        self.assertAlmostEqual(chilena["kg_por_litro"], 0.55)
        self.assertAlmostEqual(internacional["kg_por_litro"], 0.54)
        self.assertTrue(chilena["fuente"])

    def test_convierte_kilos_de_glp_a_litros(self):
        fila = {"_fila": 14, "periodo": "2025", "recurso": "GLP", "cantidad": 540, "unidad": "kg",
                "uso": "estacionaria", "pais": "CL"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg, "AR5")
        litros = 540 / 0.55
        self.assertAlmostEqual(resultado["cantidad_en_unidad_factor"], litros, places=3)
        self.assertAlmostEqual(resultado["kg_co2e"], litros * 1.6746640209139498, places=3)
        self.assertTrue(any("densidad" in a for a in resultado["advertencias"]))

    def test_convierte_litros_a_toneladas(self):
        fila = {"_fila": 15, "periodo": "2025", "recurso": "carbon", "cantidad": 2000, "unidad": "kg",
                "uso": "estacionaria", "pais": "CL"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg, "AR5")
        self.assertAlmostEqual(resultado["cantidad_en_unidad_factor"], 2.0, places=6)

    def test_sin_densidad_sigue_avisando(self):
        fila = {"_fila": 16, "periodo": "2025", "recurso": "hotel", "cantidad": 10, "unidad": "kg",
                "pais": "CL"}
        with self.assertRaises(Problema):
            carbono.calcular_registro(fila, self.factores, self.pcg, "AR5")


class PruebaTotalIncompleto(unittest.TestCase):
    """H2: un total al que le faltan filas no puede presentarse como definitivo."""

    def test_marca_el_total_como_incompleto(self):
        registros = [
            {"_fila": 2, "periodo": "2025", "recurso": "electricidad", "cantidad": 1000, "unidad": "kWh",
             "pais": "CL"},
            {"_fila": 3, "periodo": "2025", "recurso": "hidrogeno verde", "cantidad": 10, "unidad": "kg",
             "pais": "CL"},
        ]
        resumen = carbono.calcular(registros, pais="CL", conjunto="AR5")
        self.assertFalse(resumen["completo"])
        self.assertIn("INCOMPLETO", resumen["aviso_principal"])
        self.assertEqual(resumen["registros_con_problema"], 1)

    def test_calculo_sin_problemas_queda_completo(self):
        resumen = carbono.calcular(
            [{"_fila": 2, "periodo": "2025", "recurso": "electricidad", "cantidad": 1000,
              "unidad": "kWh", "pais": "CL"}], pais="CL", conjunto="AR5")
        self.assertTrue(resumen["completo"])
        self.assertEqual(resumen["aviso_principal"], "")


class PruebaEmpresaDeEjemplo(PruebaConCarpeta):
    """H6 y H14: la empresa de demostracion no debe estorbar ni confundirse con la real."""

    def test_la_empresa_real_gana_sobre_la_de_ejemplo(self):
        espacio.crear_empresa({"nombre": "Alimentos del Sur SpA", "carpeta": "ejemplo-alimentos-del-sur",
                               "pais": "CL"}, raiz=self.carpeta)
        espacio.crear_empresa({"nombre": "Panaderia Delicias", "pais": "PE"}, raiz=self.carpeta)
        perfil, _ = espacio.cargar_empresa(None, raiz=self.carpeta)
        self.assertEqual(perfil["nombre"], "Panaderia Delicias")

    def test_si_solo_esta_el_ejemplo_se_usa_el_ejemplo(self):
        espacio.crear_empresa({"nombre": "Alimentos del Sur SpA", "carpeta": "ejemplo-alimentos-del-sur",
                               "pais": "CL"}, raiz=self.carpeta)
        perfil, _ = espacio.cargar_empresa(None, raiz=self.carpeta)
        self.assertEqual(perfil["nombre"], "Alimentos del Sur SpA")

    def test_con_dos_empresas_reales_explica_como_elegir(self):
        espacio.crear_empresa({"nombre": "Una SpA", "pais": "CL"}, raiz=self.carpeta)
        espacio.crear_empresa({"nombre": "Otra SpA", "pais": "CL"}, raiz=self.carpeta)
        with self.assertRaises(Problema) as contexto:
            espacio.cargar_empresa(None, raiz=self.carpeta)
        self.assertIn("--empresa", contexto.exception.sugerencia)


class PruebaPreguntasPorPais(unittest.TestCase):
    """H9: a una empresa peruana no se le hacen preguntas de normativa chilena."""

    def test_chile_recibe_preguntas_chilenas(self):
        claves = {p["clave"] for p in aplicabilidad.preguntas_aplicables({"pais": "CL"})}
        self.assertIn("pone_productos_prioritarios", claves)
        self.assertIn("supervisada_cmf", claves)
        self.assertNotIn("emisor_valores", claves)

    def test_peru_no_recibe_preguntas_chilenas(self):
        claves = {p["clave"] for p in aplicabilidad.preguntas_aplicables({"pais": "PE"})}
        self.assertNotIn("pone_productos_prioritarios", claves)
        self.assertNotIn("tiene_calderas", claves)
        self.assertIn("emisor_valores", claves)
        self.assertIn("exporta_a_ue", claves)

    def test_las_pendientes_tambien_se_filtran(self):
        resultado = aplicabilidad.evaluar({"pais": "PE", "trabajadores": 12})
        claves = {p["clave"] for p in resultado["preguntas_pendientes"]}
        self.assertNotIn("descarga_riles", claves)


class PruebaEscrituraDePlanillas(PruebaConCarpeta):
    """H7: el asistente necesita poder llenar la planilla por la persona."""

    def setUp(self):
        super(PruebaEscrituraDePlanillas, self).setUp()
        from modulos import datos
        self.datos = datos
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def test_escribe_y_agrega_filas(self):
        import json
        primera = self.datos.escribir(dict(self.opciones, tipo="consumos", filas=json.dumps(
            [["2025-01", "Planta", "electricidad", "electricidad", 4200, "kWh", "reportado", "", ""]]))).resultado
        self.assertEqual(primera["filas_en_la_planilla"], 1)
        segunda = self.datos.escribir(dict(self.opciones, tipo="consumos", filas=json.dumps(
            [["2025-02", "Planta", "electricidad", "electricidad", 4100, "kWh", "reportado", "", ""]]))).resultado
        self.assertEqual(segunda["filas_en_la_planilla"], 2)
        leido = self.datos.leer(dict(self.opciones, archivo="consumos.xlsx"))
        self.assertEqual(leido["total_filas"], 2)
        self.assertEqual(leido["filas"][1]["periodo"], "2025-02")

    def test_reemplazar_parte_de_cero(self):
        import json
        self.datos.escribir(dict(self.opciones, tipo="consumos", filas=json.dumps(
            [["2025-01", "Planta", "electricidad", "electricidad", 4200, "kWh", "reportado", "", ""]])))
        resultado = self.datos.escribir(dict(self.opciones, tipo="consumos", reemplazar=True, filas=json.dumps(
            [["2025-03", "Planta", "electricidad", "electricidad", 3900, "kWh", "reportado", "", ""]]))).resultado
        self.assertEqual(resultado["filas_en_la_planilla"], 1)

    def test_acepta_diccionarios(self):
        import json
        self.datos.escribir(dict(self.opciones, tipo="consumos", filas=json.dumps(
            [{"Periodo": "2025-04", "Sitio": "Planta", "Recurso": "diesel", "Uso": "movil",
              "Cantidad": 300, "Unidad": "litros", "Calidad del dato": "reportado"}])))
        leido = self.datos.leer(dict(self.opciones, archivo="consumos.xlsx"))
        self.assertEqual(leido["filas"][0]["recurso"], "diesel")

    def test_errores_utiles(self):
        with self.assertRaises(Problema):
            self.datos.escribir(dict(self.opciones, tipo="inventada", filas="[]"))
        with self.assertRaises(Problema):
            self.datos.escribir(dict(self.opciones, tipo="consumos"))
        with self.assertRaises(Problema) as contexto:
            self.datos.escribir(dict(self.opciones, tipo="consumos", filas="no es json"))
        self.assertIn("JSON", contexto.exception.sugerencia)


class PruebaNombresDescubribles(unittest.TestCase):
    """H8: elegir mal el nombre del gasto cambia el resultado varias veces."""

    def setUp(self):
        self.factores = carbono.cargar_factores()

    def test_busca_por_lo_que_se_compra(self):
        from modulos import huella
        resultado = huella.factores({"recurso": "harina"})
        self.assertEqual(resultado["coincidencia"], "por descripcion")
        self.assertEqual([f["recurso"] for f in resultado["factores"]], ["gasto agricultura"])

    def test_filtra_por_uso(self):
        from modulos import huella
        resultado = huella.factores({"uso": "gasto"})
        self.assertEqual(resultado["total"], 38)
        self.assertTrue(all(f["uso"] == "gasto" for f in resultado["factores"]))

    def test_filtra_por_alcance(self):
        from modulos import huella
        resultado = huella.factores({"alcance": "2"})
        self.assertTrue(resultado["total"])
        self.assertTrue(all(f["alcance"] == 2 for f in resultado["factores"]))

    def test_alcance_invalido_avisa(self):
        from modulos import huella
        with self.assertRaises(Problema):
            huella.factores({"alcance": "tres"})

    def test_sin_resultados_lo_dice(self):
        from modulos import huella
        resultado = huella.factores({"recurso": "glp", "uso": "gasto"})
        self.assertEqual(resultado["total"], 0)
        self.assertIn("No hay ningun factor", resultado["mensaje"])
        self.assertIn("gasto", resultado["usos_disponibles"])

    def test_el_error_ofrece_nombres_parecidos(self):
        with self.assertRaises(Problema) as contexto:
            carbono.buscar_factor(self.factores, "sacos de harina", unidad="USD", pais="CL")
        self.assertIn("gasto agricultura", contexto.exception.sugerencia)
        self.assertIn("gasto agricultura",
                      [o["recurso"] for o in contexto.exception.detalle["nombres_parecidos"]])

    def test_parecidos_corrige_un_error_de_tipeo(self):
        nombres = [o["recurso"] for o in carbono.parecidos(self.factores, "electricida")]
        self.assertIn("electricidad", nombres)

    def test_la_materia_prima_y_el_producto_no_se_confunden(self):
        notas = {f["recurso"]: f["notas"] for f in self.factores}
        self.assertIn("harina", notas["gasto_agricultura"])
        self.assertIn("gasto agricultura", notas["gasto_alimentos"])


if __name__ == "__main__":
    unittest.main()
