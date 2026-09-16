# -*- coding: utf-8 -*-
"""Pruebas de la huella hidrica y la gestion del agua (GRI 303, ISO 14046 y AWARE).

Los numeros de cada prueba estan resueltos a mano en el comentario que va junto
a ellos, para poder revisarlos sin ejecutar nada.
"""

import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import agua  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


# Planilla de ejemplo, tal como la deja nucleo.excel.leer_tabla:
#
#   fila  periodo   sitio          origen        extrae  descarga  estres  calidad
#   2     2025-01   Planta Norte   pozo            1000       400   si      reportado
#   3     2025-01   Planta Norte   red publica      500       500   si      verificado
#   4     2025-02   Oficina Sur    red publica      200       150   no      estimado
#   5     2025-02   Campo          rio              300         0   no se   estimado
#
# Extraccion total = 1000 + 500 + 200 + 300 = 2.000 m3
# Descarga total   =  400 + 500 + 150 +   0 = 1.050 m3
# Consumo total    = 2.000 - 1.050          =   950 m3
FILAS = [
    {"_fila": 2, "periodo": "2025-01", "sitio": "Planta Norte", "origen": "pozo",
     "extraccion_m3": 1000, "descarga_m3": 400, "destino_de_la_descarga": "alcantarillado",
     "zona_de_estres_hidrico": "si", "calidad_del_dato": "reportado", "notas": "Flujometro"},
    {"_fila": 3, "periodo": "2025-01", "sitio": "Planta Norte", "origen": "red publica",
     "extraccion_m3": 500, "descarga_m3": 500, "destino_de_la_descarga": "alcantarillado",
     "zona_de_estres_hidrico": "si", "calidad_del_dato": "verificado", "notas": "Boletas"},
    {"_fila": 4, "periodo": "2025-02", "sitio": "Oficina Sur", "origen": "red publica",
     "extraccion_m3": 200, "descarga_m3": 150, "destino_de_la_descarga": "alcantarillado",
     "zona_de_estres_hidrico": "no", "calidad_del_dato": "estimado", "notas": ""},
    {"_fila": 5, "periodo": "2025-02", "sitio": "Campo", "origen": "rio",
     "extraccion_m3": 300, "descarga_m3": 0, "destino_de_la_descarga": "riego",
     "zona_de_estres_hidrico": "no se", "calidad_del_dato": "estimado", "notas": ""},
]

CABECERA_AWARE = ("pais,iso3,nombre,agregacion,periodo,factor,version,fuente,url,licencia,"
                  "verificado_el,notas\n")


class PruebaContabilidad(unittest.TestCase):
    """Extraccion, descarga y consumo segun las definiciones de GRI 303."""

    def test_consumo_de_una_fila_es_extraccion_menos_descarga(self):
        # Fila 2: 1.000 - 400 = 600 m3 de consumo (GRI 303-5).
        linea = agua.preparar_fila(FILAS[0])
        self.assertEqual(linea["extraccion_m3"], 1000.0)
        self.assertEqual(linea["descarga_m3"], 400.0)
        self.assertEqual(linea["consumo_m3"], 600.0)
        self.assertEqual(linea["origen"], "agua_subterranea")
        self.assertEqual(linea["destino"], "a_terceros")
        self.assertTrue(linea["zona_estres_hidrico"])
        self.assertEqual(linea["calidad_dato"], "reportado")

    def test_totales_y_paso_a_megalitros(self):
        # 2.000 m3 extraidos, 1.050 descargados, 950 consumidos.
        # En megalitros (1 ML = 1.000 m3): 2,0 / 1,05 / 0,95.
        resumen = agua.calcular(FILAS)
        self.assertEqual(resumen["extraccion_m3"], 2000.0)
        self.assertEqual(resumen["descarga_m3"], 1050.0)
        self.assertEqual(resumen["consumo_m3"], 950.0)
        self.assertAlmostEqual(resumen["extraccion_megalitros"], 2.0, places=6)
        self.assertAlmostEqual(resumen["descarga_megalitros"], 1.05, places=6)
        self.assertAlmostEqual(resumen["consumo_megalitros"], 0.95, places=6)
        self.assertEqual(resumen["registros_calculados"], 4)
        self.assertEqual(resumen["registros_con_problema"], 0)

    def test_desglose_por_las_cinco_fuentes_de_gri_303_3(self):
        # pozo -> subterranea 1.000; red publica -> terceros 500 + 200 = 700; rio -> superficial 300.
        resumen = agua.calcular(FILAS)
        por_origen = resumen["por_origen"]
        self.assertEqual(por_origen["agua_subterranea"]["extraccion_m3"], 1000.0)
        self.assertEqual(por_origen["agua_de_terceros"]["extraccion_m3"], 700.0)
        self.assertEqual(por_origen["agua_superficial"]["extraccion_m3"], 300.0)
        self.assertNotIn("sin_clasificar", por_origen)
        # El destino "riego" no calza con los destinos del estandar, pero esa fila
        # no descarga nada, asi que no aparece en el desglose de la 303-4.
        self.assertEqual(sorted(resumen["por_destino"]), ["a_terceros"])
        self.assertEqual(resumen["por_destino"]["a_terceros"]["descarga_m3"], 1050.0)

    def test_resumen_por_sitio_y_por_periodo(self):
        # Planta Norte: 1.500 extraidos, 900 descargados, 600 consumidos.
        resumen = agua.calcular(FILAS)
        norte = resumen["por_sitio"]["Planta Norte"]
        self.assertEqual(norte["extraccion_m3"], 1500.0)
        self.assertEqual(norte["descarga_m3"], 900.0)
        self.assertEqual(norte["consumo_m3"], 600.0)
        self.assertEqual(norte["registros"], 2)
        self.assertEqual(norte["zona_estres_hidrico"], "si")
        self.assertEqual(resumen["por_sitio"]["Campo"]["zona_estres_hidrico"], "sin definir")
        self.assertEqual(resumen["por_periodo"]["2025-01"]["extraccion_m3"], 1500.0)
        self.assertEqual(resumen["por_periodo"]["2025-02"]["consumo_m3"], 350.0)

    def test_porcentajes_en_zonas_de_estres_hidrico(self):
        # Extraccion: 1.500 en zona de estres de 2.000 -> 75 %. 200 fuera -> 10 %.
        # 300 sin definir -> 15 %. Consumo en estres: 600 de 950 -> 63,16 %.
        resumen = agua.calcular(FILAS)
        porcentaje = resumen["zonas_estres_hidrico"]["porcentaje"]
        self.assertAlmostEqual(porcentaje["extraccion"]["si"], 75.0, places=6)
        self.assertAlmostEqual(porcentaje["extraccion"]["no"], 10.0, places=6)
        self.assertAlmostEqual(porcentaje["extraccion"]["sin_definir"], 15.0, places=6)
        self.assertAlmostEqual(porcentaje["consumo"]["si"], 600.0 / 950.0 * 100.0, places=6)
        self.assertEqual(resumen["zonas_estres_hidrico"]["sitios_en_estres"], ["Planta Norte"])
        self.assertEqual(resumen["zonas_estres_hidrico"]["sitios_sin_definir"], ["Campo"])
        self.assertTrue(any("estres hidrico" in a for a in resumen["advertencias"]))

    def test_calidad_de_los_datos_se_pondera_por_el_agua_extraida(self):
        # reportado 1.000, verificado 500, estimado 200 + 300 = 500, sobre 2.000 m3.
        resumen = agua.calcular(FILAS)
        calidad = resumen["calidad_datos"]
        self.assertEqual(calidad["metros_cubicos_extraidos"]["reportado"], 1000.0)
        self.assertEqual(calidad["metros_cubicos_extraidos"]["verificado"], 500.0)
        self.assertEqual(calidad["metros_cubicos_extraidos"]["estimado"], 500.0)
        self.assertAlmostEqual(calidad["porcentaje"]["reportado"], 50.0, places=6)
        self.assertAlmostEqual(calidad["porcentaje"]["verificado"], 25.0, places=6)
        self.assertEqual(calidad["registros"]["estimado"], 2)

    def test_filtra_por_periodo(self):
        # Solo enero: 1.500 extraidos, 900 descargados, 600 consumidos.
        resumen = agua.calcular(FILAS, "2025-01")
        self.assertEqual(resumen["registros_calculados"], 2)
        self.assertEqual(resumen["extraccion_m3"], 1500.0)
        self.assertEqual(resumen["consumo_m3"], 600.0)
        self.assertEqual(resumen["periodo"], "2025-01")
        # Filtrando por el anio completo entran las cuatro filas.
        self.assertEqual(agua.calcular(FILAS, "2025")["registros_calculados"], 4)

    def test_periodo_sin_filas_avisa_donde_mirar(self):
        with self.assertRaises(Problema) as contexto:
            agua.calcular(FILAS, "2024")
        self.assertIn("2024", contexto.exception.mensaje)
        self.assertIn("Periodo", contexto.exception.sugerencia)

    def test_el_desglose_de_agua_dulce_se_declara_faltante(self):
        # GRI 303 separa agua dulce (hasta 1.000 mg/L de TDS) de otras aguas, y la
        # planilla no trae ese dato: se dice, no se inventa.
        resumen = agua.calcular(FILAS)
        dulce = resumen["desglose_agua_dulce_y_otras"]
        self.assertFalse(dulce["disponible"])
        self.assertIn("1.000 mg/L", dulce["que_pide_el_estandar"])
        self.assertIn("salinidad", dulce["por_que_falta"])


class PruebaFilasConProblemas(unittest.TestCase):
    """Los errores de la planilla se explican con la fila y que hacer."""

    def test_descargar_mas_de_lo_extraido_queda_como_problema(self):
        filas = FILAS + [{"_fila": 6, "periodo": "2025-02", "sitio": "Bodega",
                          "origen": "red publica", "extraccion_m3": 100, "descarga_m3": 180,
                          "destino_de_la_descarga": "alcantarillado",
                          "zona_de_estres_hidrico": "no", "calidad_del_dato": "estimado"}]
        resumen = agua.calcular(filas)
        # La fila mala no entra en los totales: siguen siendo 2.000 y 950 m3.
        self.assertEqual(resumen["registros_calculados"], 4)
        self.assertEqual(resumen["registros_con_problema"], 1)
        self.assertEqual(resumen["extraccion_m3"], 2000.0)
        self.assertEqual(resumen["consumo_m3"], 950.0)
        problema = resumen["problemas"][0]
        self.assertEqual(problema["fila"], 6)
        self.assertIn("fila 6", problema["error"])
        self.assertIn("consumo negativo", problema["sugerencia"])

    def test_texto_en_vez_de_numero_dice_la_fila_y_la_columna(self):
        with self.assertRaises(Problema) as contexto:
            agua.preparar_fila({"_fila": 9, "origen": "pozo", "extraccion_m3": "bastante",
                                "descarga_m3": 10})
        self.assertIn("fila 9", contexto.exception.mensaje)
        self.assertIn("Extraccion (m3)", contexto.exception.mensaje)
        self.assertIn("metros cubicos", contexto.exception.sugerencia)

    def test_fila_sin_extraccion_ni_descarga(self):
        with self.assertRaises(Problema) as contexto:
            agua.preparar_fila({"_fila": 11, "sitio": "Planta", "origen": "pozo"})
        self.assertIn("fila 11", contexto.exception.mensaje)
        self.assertIn("borra la fila", contexto.exception.sugerencia)

    def test_volumen_negativo_se_rechaza(self):
        with self.assertRaises(Problema) as contexto:
            agua.preparar_fila({"_fila": 12, "origen": "pozo", "extraccion_m3": -5,
                                "descarga_m3": 0})
        self.assertIn("negativo", contexto.exception.mensaje)

    def test_origen_desconocido_queda_sin_clasificar_y_avisa(self):
        linea = agua.preparar_fila({"_fila": 13, "periodo": "2025", "sitio": "Planta",
                                    "origen": "agua de lluvia", "extraccion_m3": 50,
                                    "descarga_m3": 0, "zona_de_estres_hidrico": "no",
                                    "calidad_del_dato": "estimado"})
        self.assertEqual(linea["origen"], "sin_clasificar")
        self.assertTrue(any("GRI 303-3" in a for a in linea["advertencias"]))

    def test_calidad_y_estres_desconocidos_se_avisan(self):
        linea = agua.preparar_fila({"_fila": 14, "periodo": "2025", "sitio": "Planta",
                                    "origen": "pozo", "extraccion_m3": 10, "descarga_m3": 0,
                                    "zona_de_estres_hidrico": "ni idea",
                                    "calidad_del_dato": "mas o menos"})
        self.assertIsNone(linea["zona_estres_hidrico"])
        self.assertEqual(linea["calidad_dato"], "estimado")
        self.assertTrue(any("calidad del dato" in a for a in linea["advertencias"]))
        self.assertTrue(any("WRI Aqueduct" in a for a in linea["advertencias"]))


class PruebaHuellaDeEscasez(unittest.TestCase):
    """Metodo AWARE dentro del marco de ISO 14046."""

    def test_ejemplo_resuelto_de_una_faena_en_chile(self):
        # Extraccion 1.500.000 m3, descarga 300.000 m3 -> consumo 1.200.000 m3.
        # Factor AWARE 2.0 de Chile, agregacion no agricola, anual: 45,5.
        # Huella = 1.200.000 x 45,5 = 54.600.000 m3 mundo-eq.
        # Contra el promedio mundial no agricola (17,9): 1.200.000 x 17,9 = 21.480.000,
        # es decir 45,5 / 17,9 = 2,54 veces mas impacto.
        consumo = 1500000 - 300000
        self.assertEqual(consumo, 1200000)
        resultado = agua.huella_de_escasez(consumo, 45.5, 17.9)
        self.assertAlmostEqual(resultado["huella_m3_mundo_eq"], 54600000.0, delta=0.01)
        self.assertEqual(resultado["unidad"], "m3 mundo-eq (metros cubicos equivalentes mundiales)")
        comparacion = resultado["comparacion_con_el_promedio_mundial"]
        self.assertAlmostEqual(comparacion["huella_m3_mundo_eq"], 21480000.0, delta=0.01)
        self.assertAlmostEqual(comparacion["veces_el_promedio_mundial"], 45.5 / 17.9, places=9)
        self.assertIn("menor", comparacion["en_palabras"])

    def test_la_estacionalidad_cambia_el_resultado(self):
        # Mismo consumo de 1.200.000 m3 en Chile, factores mensuales no agricolas:
        # enero 84,9 -> 101.880.000 m3 mundo-eq; junio 5,19 -> 6.228.000 m3 mundo-eq.
        enero = agua.huella_de_escasez(1200000, 84.9)
        junio = agua.huella_de_escasez(1200000, 5.19)
        self.assertAlmostEqual(enero["huella_m3_mundo_eq"], 101880000.0, delta=0.01)
        self.assertAlmostEqual(junio["huella_m3_mundo_eq"], 6228000.0, delta=0.01)
        self.assertGreater(enero["huella_m3_mundo_eq"], junio["huella_m3_mundo_eq"] * 16)

    def test_sin_factor_pide_el_dato_y_dice_donde_buscarlo(self):
        with self.assertRaises(Problema) as contexto:
            agua.huella_de_escasez(1000, None)
        self.assertIn("factor de escasez AWARE", contexto.exception.mensaje)
        self.assertIn("zenodo", contexto.exception.sugerencia.lower())

    def test_factor_fuera_del_rango_del_metodo(self):
        # AWARE corta sus factores entre 0,1 y 100: 250 no es un factor AWARE.
        with self.assertRaises(Problema) as contexto:
            agua.huella_de_escasez(1000, 250)
        self.assertIn("fuera del rango", contexto.exception.mensaje)
        with self.assertRaises(Problema):
            agua.huella_de_escasez(1000, 0.05)

    def test_consumo_negativo_o_no_numerico(self):
        with self.assertRaises(Problema) as contexto:
            agua.huella_de_escasez(-10, 45.5)
        self.assertIn("no puede ser negativo", contexto.exception.mensaje)
        with self.assertRaises(Problema):
            agua.huella_de_escasez("harta agua", 45.5)


class PruebaCatalogoAware(unittest.TestCase):
    """El catalogo que se redistribuye bajo licencia CC BY 4.0."""

    def setUp(self):
        self.factores = agua.cargar_factores_aware()

    def test_factores_de_chile_y_del_promedio_mundial(self):
        chile, avisos = agua.buscar_factor_aware("CL", "no_agricola", None, self.factores)
        self.assertEqual(chile["factor"], 45.5)
        self.assertEqual(chile["iso3"], "CHL")
        self.assertEqual(chile["licencia"], "CC BY 4.0")
        self.assertTrue(any("promedio nacional" in a for a in avisos))
        mundo, _ = agua.buscar_factor_aware("*", "no_agricola", None, self.factores)
        self.assertEqual(mundo["factor"], 17.9)
        peru, _ = agua.buscar_factor_aware("PE", "no_agricola", None, self.factores)
        self.assertEqual(peru["factor"], 24.4)

    def test_factor_mensual_y_agregacion(self):
        # Chile, no agricola: enero 84,9 y junio 5,19. Anual agricola: 91,3.
        enero, _ = agua.buscar_factor_aware("CL", "no_agricola", 1, self.factores)
        junio, _ = agua.buscar_factor_aware("CL", "no_agricola", 6, self.factores)
        self.assertEqual(enero["factor"], 84.9)
        self.assertEqual(junio["factor"], 5.19)
        agricola, _ = agua.buscar_factor_aware("CL", "agricola", None, self.factores)
        self.assertEqual(agricola["factor"], 91.3)
        no_especificado, avisos = agua.buscar_factor_aware("CL", "no especificado", None, self.factores)
        self.assertEqual(no_especificado["factor"], 88.1)
        self.assertTrue(any("mas gruesa" in a for a in avisos))

    def test_pais_sin_factor_no_se_inventa(self):
        with self.assertRaises(Problema) as contexto:
            agua.buscar_factor_aware("UY", "no_agricola", None, self.factores)
        self.assertIn("No tengo el factor AWARE de UY", contexto.exception.mensaje)
        self.assertIn("No voy a inventarlo", contexto.exception.sugerencia)
        self.assertIn("Chile", contexto.exception.sugerencia)

    def test_agregacion_desconocida(self):
        with self.assertRaises(Problema) as contexto:
            agua.normalizar_agregacion("forestal")
        self.assertIn("agregacion", contexto.exception.mensaje)

    def test_atribucion_de_la_licencia(self):
        # CC BY 4.0 obliga a nombrar autores, fuente y licencia.
        self.assertIn("CC BY 4.0", agua.ATRIBUCION_AWARE)
        self.assertIn("Seitfudem", agua.ATRIBUCION_AWARE)
        self.assertIn("zenodo.15133241", agua.ATRIBUCION_AWARE)


class PruebaCatalogoDePrueba(PruebaConCarpeta):
    """El catalogo se lee de un CSV: se prueba con uno propio."""

    def test_lee_un_catalogo_propio_y_usa_el_anual_si_falta_el_mes(self):
        ruta = self.ruta("aware.csv")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(CABECERA_AWARE)
            archivo.write("XX,XXX,Pais de prueba,no_agricola,anual,10,AWARE 2.0,Fuente,"
                          "https://ejemplo.org,CC BY 4.0,2026-09-16,Nota\n")
            archivo.write("XX,XXX,Pais de prueba,no_agricola,03,20,AWARE 2.0,Fuente,"
                          "https://ejemplo.org,CC BY 4.0,2026-09-16,Nota\n")
        factores = agua.cargar_factores_aware(ruta)
        self.assertEqual(len(factores), 2)
        marzo, _ = agua.buscar_factor_aware("XX", "no_agricola", 3, factores)
        self.assertEqual(marzo["factor"], 20.0)
        # Julio no esta cargado: cae al anual y lo avisa.
        julio, avisos = agua.buscar_factor_aware("XXX", "no_agricola", 7, factores)
        self.assertEqual(julio["factor"], 10.0)
        self.assertTrue(any("julio" in a for a in avisos))
        # 1.500 m3 x 20 = 30.000 m3 mundo-eq.
        self.assertAlmostEqual(agua.huella_de_escasez(1500, marzo["factor"])["huella_m3_mundo_eq"],
                               30000.0, delta=0.01)

    def test_sin_archivo_no_hay_factores_y_se_pide_el_dato(self):
        factores = agua.cargar_factores_aware(self.ruta("no-existe.csv"))
        self.assertEqual(factores, [])
        with self.assertRaises(Problema) as contexto:
            agua.buscar_factor_aware("CL", "no_agricola", None, factores)
        self.assertIn("--factor", contexto.exception.sugerencia)


class PruebaIndicadoresGri303(unittest.TestCase):
    """Las tres divulgaciones cuantitativas del estandar, en megalitros."""

    def setUp(self):
        self.indicadores = agua.indicadores_gri303(agua.calcular(FILAS))

    def test_extraccion_303_3(self):
        # 2.000 m3 = 2,0 ML. En zonas de estres 1.500 m3 = 1,5 ML. Sin definir 300 m3 = 0,3 ML.
        tres = self.indicadores["303-3"]
        self.assertAlmostEqual(tres["total_megalitros"], 2.0, places=6)
        self.assertAlmostEqual(tres["en_zonas_con_estres_hidrico_megalitros"], 1.5, places=6)
        self.assertAlmostEqual(tres["fuera_de_zonas_con_estres_hidrico_megalitros"], 0.2, places=6)
        self.assertAlmostEqual(tres["sin_definir_megalitros"], 0.3, places=6)
        self.assertAlmostEqual(tres["por_fuente_megalitros"]["agua_subterranea"]["megalitros"],
                               1.0, places=6)
        self.assertEqual(tres["agua_dulce_y_otras_aguas"], "no disponible")

    def test_descarga_303_4(self):
        # Descargas: 400 + 500 en zona de estres = 900 m3 = 0,9 ML; 150 m3 fuera = 0,15 ML.
        cuatro = self.indicadores["303-4"]
        self.assertAlmostEqual(cuatro["total_megalitros"], 1.05, places=6)
        self.assertAlmostEqual(cuatro["en_zonas_con_estres_hidrico_megalitros"], 0.9, places=6)
        self.assertAlmostEqual(cuatro["por_destino_megalitros"]["a_terceros"]["megalitros"],
                               1.05, places=6)
        self.assertEqual(cuatro["sustancias_prioritarias_de_preocupacion"], "no disponible")
        self.assertTrue(any("sustancias prioritarias" in f for f in cuatro["lo_que_falta"]))

    def test_consumo_303_5(self):
        # 950 m3 = 0,95 ML, de los cuales 600 m3 = 0,6 ML en zonas de estres.
        cinco = self.indicadores["303-5"]
        self.assertAlmostEqual(cinco["total_megalitros"], 0.95, places=6)
        self.assertAlmostEqual(cinco["en_zonas_con_estres_hidrico_megalitros"], 0.6, places=6)
        self.assertAlmostEqual(cinco["sin_definir_megalitros"], 0.3, places=6)
        self.assertEqual(cinco["metodo_de_calculo"],
                         "Consumo (m3) = Extraccion (m3) - Descarga (m3)")
        self.assertTrue(any("almacenada" in f for f in cinco["lo_que_falta"]))

    def test_menciona_las_divulgaciones_de_gestion_y_la_unidad(self):
        self.assertIn("megalitros", self.indicadores["unidad"])
        gestion = " ".join(self.indicadores["divulgaciones_de_gestion_que_no_son_numeros"])
        self.assertIn("303-1", gestion)
        self.assertIn("303-2", gestion)

    def test_sin_calculo_previo_lo_dice_claro(self):
        with self.assertRaises(Problema) as contexto:
            agua.indicadores_gri303(None)
        self.assertIn("agua calcular", contexto.exception.sugerencia)


class PruebaNormalizacion(unittest.TestCase):
    """Como escribe la gente vs. las categorias del estandar."""

    def test_origenes(self):
        self.assertEqual(agua.normalizar_origen("Pozo profundo"), "agua_subterranea")
        self.assertEqual(agua.normalizar_origen("Río"), "agua_superficial")
        self.assertEqual(agua.normalizar_origen("red publica"), "agua_de_terceros")
        self.assertEqual(agua.normalizar_origen("APR"), "agua_de_terceros")
        self.assertEqual(agua.normalizar_origen("mar"), "agua_de_mar")
        self.assertEqual(agua.normalizar_origen("agua producida"), "agua_producida")
        self.assertEqual(agua.normalizar_origen("no se"), "sin_clasificar")

    def test_destinos_y_estres(self):
        self.assertEqual(agua.normalizar_destino("Alcantarillado"), "a_terceros")
        self.assertEqual(agua.normalizar_destino("infiltracion"), "agua_subterranea")
        self.assertEqual(agua.normalizar_destino("emisario"), "agua_de_mar")
        self.assertTrue(agua.normalizar_estres("Sí"))
        self.assertFalse(agua.normalizar_estres("no"))
        self.assertIsNone(agua.normalizar_estres("no se"))
        self.assertIsNone(agua.normalizar_estres(""))

    def test_megalitros_y_agregaciones(self):
        self.assertAlmostEqual(agua.a_megalitros(2500), 2.5, places=6)
        self.assertEqual(agua.normalizar_agregacion("Minería"), "no_agricola")
        self.assertEqual(agua.normalizar_agregacion("riego"), "agricola")
        self.assertEqual(agua.normalizar_agregacion(""), "no_agricola")


if __name__ == "__main__":
    unittest.main()
