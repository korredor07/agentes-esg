# -*- coding: utf-8 -*-
"""Pruebas del calculo de emisiones de transporte segun ISO 14083."""

import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import logistica  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaFactores(unittest.TestCase):

    def setUp(self):
        self.factores = logistica.cargar_factores()

    def test_cada_factor_separa_operacion_y_provision(self):
        for factor in self.factores.values():
            self.assertAlmostEqual(factor["operacion"] + factor["provision"], factor["total"],
                                   places=6,
                                   msg="El factor %s no cuadra: operacion + provision != total"
                                       % factor["id"])

    def test_cada_factor_dice_de_donde_sale(self):
        for factor in self.factores.values():
            self.assertTrue(factor["fuente"], "El factor %s no tiene fuente." % factor["id"])
            self.assertTrue(factor["licencia"], "El factor %s no declara licencia." % factor["id"])
            self.assertTrue(factor["verificado_el"])

    def test_ningun_factor_viene_del_glec(self):
        # La licencia del GLEC Framework no permite redistribuir sus valores.
        for factor in self.factores.values():
            self.assertNotIn("glec", factor["fuente"].lower(),
                             "El factor %s dice venir del GLEC y eso no se puede redistribuir."
                             % factor["id"])
            self.assertNotIn("smart freight", factor["fuente"].lower())

    def test_encuentra_el_vehiculo_como_lo_dice_la_gente(self):
        self.assertEqual(logistica.buscar_factor(self.factores, "camion")["id"], "desnz-hgv-promedio")
        self.assertEqual(logistica.buscar_factor(self.factores, "camion refrigerado")["id"],
                         "desnz-hgv-refrigerado")
        self.assertEqual(logistica.buscar_factor(self.factores, "barco")["id"], "desnz-contenedor")
        self.assertEqual(logistica.buscar_factor(self.factores, "flete aereo")["id"],
                         "desnz-aereo-corto")

    def test_vehiculo_desconocido_lo_dice(self):
        with self.assertRaises(Problema) as contexto:
            logistica.buscar_factor(self.factores, "teletransportador")
        self.assertIn("intensidad", contexto.exception.sugerencia)

    def test_el_refrigerado_emite_mas_que_el_normal(self):
        normal = self.factores["desnz-hgv-promedio"]["total"]
        frio = self.factores["desnz-hgv-refrigerado"]["total"]
        self.assertGreater(frio, normal)


class PruebaDistancias(unittest.TestCase):
    """El error mas comun del metodo es mezclar tipos de distancia."""

    def test_carretera_desde_linea_recta_suma_cinco_por_ciento(self):
        ajuste = logistica.distancia_de_actividad(1000, "carretera", "GCD")
        self.assertAlmostEqual(ajuste["distancia_km"], 1050.0)
        self.assertAlmostEqual(ajuste["daf"], 1.05)

    def test_maritimo_desde_linea_recta_suma_quince_por_ciento(self):
        ajuste = logistica.distancia_de_actividad(1000, "maritimo", "GCD")
        self.assertAlmostEqual(ajuste["distancia_km"], 1150.0)

    def test_distancia_real_se_convierte_a_la_mas_corta(self):
        # 235 km de odometro sobre una intensidad calculada en ruta corta.
        ajuste = logistica.distancia_de_actividad(235, "carretera", "REAL")
        self.assertAlmostEqual(ajuste["distancia_km"], 223.8095, places=3)

    def test_la_ruta_mas_corta_no_se_ajusta(self):
        ajuste = logistica.distancia_de_actividad(220, "carretera", "SFD")
        self.assertAlmostEqual(ajuste["distancia_km"], 220.0)
        self.assertAlmostEqual(ajuste["daf"], 1.0)

    def test_ferrocarril_no_necesita_ajuste(self):
        self.assertAlmostEqual(logistica.distancia_de_actividad(500, "ferrocarril", "GCD")["daf"], 1.0)

    def test_aereo_suma_noventa_y_cinco_kilometros(self):
        ajuste = logistica.distancia_de_actividad(9000, "aereo", "GCD")
        self.assertAlmostEqual(ajuste["distancia_km"], 9095.0)

    def test_aereo_avisa_si_no_le_dan_linea_recta(self):
        ajuste = logistica.distancia_de_actividad(9000, "aereo", "SFD")
        self.assertTrue(ajuste["advertencias"])

    def test_modo_desconocido_lo_dice(self):
        with self.assertRaises(Problema):
            logistica.distancia_de_actividad(100, "teleferico de carga", "SFD")


class PruebaMasa(unittest.TestCase):

    def test_contenedores_sin_peso_usan_diez_toneladas(self):
        supuesto = logistica.masa_de_contenedores(3)
        self.assertAlmostEqual(supuesto["toneladas"], 30.0)
        self.assertIn("asumieron", supuesto["supuesto"].lower())

    def test_carga_ligera_y_pesada(self):
        self.assertAlmostEqual(logistica.masa_de_contenedores(2, "ligera")["toneladas"], 12.0)
        self.assertAlmostEqual(logistica.masa_de_contenedores(2, "pesada")["toneladas"], 29.0)

    def test_carga_desconocida_lo_dice(self):
        with self.assertRaises(Problema):
            logistica.masa_de_contenedores(1, "mediana tirando a pesada")


class PruebaCadenaMultimodal(unittest.TestCase):
    """Reproduce el ejemplo resuelto de la investigacion, al centavo.

    12 toneladas de fruta refrigerada de Curico a Venlo, con dos hubs.
    """

    TRAMOS = [
        {"tipo": "transporte", "modo": "carretera", "vehiculo": "camion refrigerado",
         "toneladas": 12, "km": 220, "descripcion": "Curico a San Antonio"},
        {"tipo": "hub", "descripcion": "Terminal San Antonio", "toneladas": 12},
        {"tipo": "transporte", "modo": "maritimo", "vehiculo": "barco",
         "toneladas": 12, "km": 12000, "descripcion": "San Antonio a Rotterdam"},
        {"tipo": "hub", "descripcion": "Terminal Rotterdam", "toneladas": 12},
        {"tipo": "transporte", "modo": "carretera", "vehiculo": "camion refrigerado",
         "toneladas": 12, "km": 150, "descripcion": "Rotterdam a Venlo"},
    ]

    def setUp(self):
        self.resultado = logistica.calcular_cadena(self.TRAMOS, "Fruta a Venlo")

    def test_el_total_coincide_con_la_investigacion(self):
        self.assertAlmostEqual(self.resultado["total_kg_co2e"], 3508.0404, places=4)

    def test_la_actividad_coincide(self):
        self.assertAlmostEqual(self.resultado["actividad_t_km"], 148440.0, places=4)

    def test_la_intensidad_coincide(self):
        self.assertAlmostEqual(self.resultado["intensidad_g_co2e_por_t_km"], 23.633, places=3)

    def test_separa_operacion_y_provision(self):
        self.assertAlmostEqual(self.resultado["emisiones_de_operacion_kg"], 2859.4968, places=4)
        self.assertAlmostEqual(self.resultado["emisiones_de_provision_kg"], 648.5436, places=4)
        self.assertAlmostEqual(self.resultado["porcentaje_de_provision"], 18.5, places=1)

    def test_cada_tramo_por_separado(self):
        tramos = {t["descripcion"]: t for t in self.resultado["tramos"]}
        self.assertAlmostEqual(tramos["Curico a San Antonio"]["kg_co2e_total"], 393.1224, places=4)
        self.assertAlmostEqual(tramos["San Antonio a Rotterdam"]["kg_co2e_total"], 2846.88, places=2)
        self.assertAlmostEqual(tramos["Rotterdam a Venlo"]["kg_co2e_total"], 268.038, places=3)

    def test_los_hubs_faltan_y_el_total_lo_dice(self):
        self.assertFalse(self.resultado["completo"])
        self.assertIn("INCOMPLETO", self.resultado["aviso_principal"])
        hubs = [t for t in self.resultado["tramos"] if t["tipo"] == "hub"]
        self.assertEqual(len(hubs), 2)
        for hub in hubs:
            self.assertFalse(hub["calculado"])
            self.assertIsNone(hub["kg_co2e_total"])
            self.assertIn("ISO 14083", hub["motivo"])

    def test_el_barco_hace_casi_toda_la_distancia_pero_no_las_emisiones(self):
        maritimo = self.resultado["por_modo"]["maritimo"]
        carretera = self.resultado["por_modo"]["carretera"]
        self.assertAlmostEqual(maritimo["porcentaje_de_la_actividad"], 97.0, places=0)
        self.assertAlmostEqual(maritimo["porcentaje_de_las_emisiones"], 81.2, places=1)
        self.assertAlmostEqual(carretera["porcentaje_de_las_emisiones"], 18.8, places=1)

    def test_con_intensidad_de_hub_el_total_queda_completo(self):
        tramos = [dict(t) for t in self.TRAMOS]
        for tramo in tramos:
            if tramo["tipo"] == "hub":
                tramo["intensidad"] = 3.5
        resultado = logistica.calcular_cadena(tramos, "Fruta a Venlo")
        self.assertTrue(resultado["completo"])
        self.assertAlmostEqual(resultado["total_kg_co2e"], 3508.0404 + 2 * 12 * 3.5, places=4)


class PruebaTramos(unittest.TestCase):

    def setUp(self):
        self.factores = logistica.cargar_factores()

    def test_falta_la_masa(self):
        with self.assertRaises(Problema) as contexto:
            logistica.calcular_tramo({"_fila": 1, "vehiculo": "camion", "km": 100}, self.factores)
        self.assertIn("palets", contexto.exception.sugerencia)

    def test_falta_la_distancia(self):
        with self.assertRaises(Problema):
            logistica.calcular_tramo({"_fila": 1, "vehiculo": "camion", "toneladas": 5},
                                     self.factores)

    def test_usa_los_teu_cuando_no_hay_peso(self):
        tramo = logistica.calcular_tramo(
            {"_fila": 1, "vehiculo": "barco", "teu": 2, "km": 1000}, self.factores)
        self.assertAlmostEqual(tramo["toneladas"], 20.0)
        self.assertTrue(any("supuso" in a or "asumieron" in a for a in tramo["advertencias"]))

    def test_la_intensidad_del_transportista_manda(self):
        tramo = logistica.calcular_tramo(
            {"_fila": 1, "modo": "carretera", "toneladas": 10, "km": 100, "intensidad": 0.08},
            self.factores)
        self.assertAlmostEqual(tramo["kg_co2e_total"], 10 * 100 * 0.08)
        self.assertTrue(any("transportista" in a for a in tramo["advertencias"]))

    def test_intensidad_propia_sin_modo_no_se_puede(self):
        with self.assertRaises(Problema) as contexto:
            logistica.calcular_tramo({"_fila": 1, "toneladas": 10, "km": 100, "intensidad": 0.08},
                                     self.factores)
        self.assertIn("modo", contexto.exception.mensaje)

    def test_un_numero_mal_escrito_se_explica(self):
        with self.assertRaises(Problema) as contexto:
            logistica.calcular_tramo({"_fila": 3, "vehiculo": "camion", "toneladas": "doce",
                                      "km": 100}, self.factores)
        self.assertIn("tramo 3", contexto.exception.mensaje)


class PruebaComparacion(unittest.TestCase):

    def test_ordena_del_mas_limpio_al_mas_sucio(self):
        resultado = logistica.comparar_modos(12, 500)
        emisiones = [o["kg_co2e"] for o in resultado["opciones"]]
        self.assertEqual(emisiones, sorted(emisiones))
        self.assertEqual(resultado["opciones"][0]["modo"], "maritimo")
        self.assertEqual(resultado["opciones"][-1]["modo"], "aereo")

    def test_dice_cuantas_veces_mas_emite_cada_uno(self):
        resultado = logistica.comparar_modos(12, 500)
        self.assertAlmostEqual(resultado["opciones"][0]["veces_el_mas_limpio"], 1.0)
        self.assertGreater(resultado["opciones"][-1]["veces_el_mas_limpio"], 100)

    def test_avisa_que_no_mira_costo_ni_plazo(self):
        self.assertIn("costo", logistica.comparar_modos(1, 1)["aviso"])


class PruebaModulo(PruebaConCarpeta):

    def setUp(self):
        super(PruebaModulo, self).setUp()
        from modulos import logistica as modulo
        self.modulo = modulo
        espacio.crear_empresa({"nombre": "Exportadora Prueba", "pais": "CL"}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Exportadora Prueba"}

    def test_calcula_desde_la_planilla(self):
        self.modulo.plantilla(dict(self.opciones))
        resultado = self.modulo.calcular(dict(self.opciones)).resultado
        self.assertAlmostEqual(resultado["total_kg_co2e"], 3508.0404, places=4)
        self.assertFalse(resultado["completo"])

    def test_no_sobrescribe_la_planilla(self):
        self.modulo.plantilla(dict(self.opciones))
        with self.assertRaises(Problema) as contexto:
            self.modulo.plantilla(dict(self.opciones))
        self.assertIn("--sobrescribir", contexto.exception.sugerencia)

    def test_sin_planilla_lo_dice(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.calcular(dict(self.opciones))
        self.assertIn("logistica plantilla", contexto.exception.sugerencia)

    def test_un_tramo_suelto(self):
        respuesta = self.modulo.tramo(dict(self.opciones, vehiculo="camion refrigerado",
                                           toneladas="12", km="220"))
        self.assertAlmostEqual(respuesta.resultado["kg_co2e_total"], 393.1224, places=4)

    def test_el_informe_queda_escrito(self):
        import os
        self.modulo.plantilla(dict(self.opciones))
        respuesta = self.modulo.informe_html(dict(self.opciones))
        self.assertTrue(os.path.isfile(respuesta.resultado["archivo"]))

    def test_comparar_pide_los_datos(self):
        with self.assertRaises(Problema):
            self.modulo.comparar(dict(self.opciones, toneladas="12"))

    def test_lista_los_vehiculos_de_un_modo(self):
        resultado = self.modulo.factores(dict(self.opciones, modo="maritimo"))
        self.assertTrue(resultado["total"])
        self.assertTrue(all(v["modo"] == "maritimo" for v in resultado["vehiculos"]))


if __name__ == "__main__":
    unittest.main()
