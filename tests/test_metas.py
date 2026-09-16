# -*- coding: utf-8 -*-
"""Pruebas de metas de reduccion y curva de costos de abatimiento.

Los valores esperados vienen de los ejemplos resueltos de la investigacion
normativa (docs/investigacion/06-marcos-reporte-metas-greenwashing.md).
"""

import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import macc, metas  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

MEDIDAS = [
    {"medida": "Iluminacion LED", "capex": 45000, "vida_util": 10, "opex": 1200,
     "ahorros": 14000, "tco2e_evitadas": 38},
    {"medida": "Motores eficientes", "capex": 120000, "vida_util": 12, "opex": 3000,
     "ahorros": 26000, "tco2e_evitadas": 70},
    {"medida": "Solar FV", "capex": 320000, "vida_util": 20, "opex": 6500,
     "ahorros": 52000, "tco2e_evitadas": 160},
    {"medida": "Recuperador de calor", "capex": 210000, "vida_util": 15, "opex": 8000,
     "ahorros": 22000, "tco2e_evitadas": 130},
    {"medida": "Electrificacion de flota", "capex": 480000, "vida_util": 8, "opex": 12000,
     "ahorros": 40000, "tco2e_evitadas": 145},
]


class PruebaTrayectoria(unittest.TestCase):
    def setUp(self):
        self.resultado = metas.trayectoria(12500, 2024, 2034, 0.042)

    def test_ejemplo_de_la_investigacion(self):
        por_anio = {f["anio"]: f for f in self.resultado["trayectoria"]}
        self.assertAlmostEqual(por_anio[2025]["emisiones_permitidas"], 11975.0, places=1)
        self.assertAlmostEqual(por_anio[2030]["emisiones_permitidas"], 9350.0, places=1)
        self.assertAlmostEqual(por_anio[2034]["emisiones_permitidas"], 7250.0, places=1)
        self.assertAlmostEqual(por_anio[2030]["reduccion_acumulada_pct"], 25.2, places=1)

    def test_reduccion_lineal_no_compuesta(self):
        self.assertAlmostEqual(self.resultado["reduccion_total_pct"], 42.0, places=1)
        self.assertAlmostEqual(self.resultado["tasa_compuesta_equivalente_pct"], 5.302, places=2)

    def test_incluye_el_anio_base(self):
        self.assertEqual(self.resultado["trayectoria"][0]["anio"], 2024)
        self.assertAlmostEqual(self.resultado["trayectoria"][0]["emisiones_permitidas"], 12500.0)

    def test_anio_meta_invalido(self):
        with self.assertRaises(Problema):
            metas.trayectoria(1000, 2030, 2025)

    def test_base_no_numerica(self):
        with self.assertRaises(Problema):
            metas.trayectoria("bastante", 2024, 2030)


class PruebaCriterios(unittest.TestCase):
    def test_ratio_alcance_3(self):
        self.assertAlmostEqual(metas.ratio_alcance3(3000, 9500, 41000) * 100, 76.6, places=1)
        self.assertEqual(metas.ratio_alcance3(0, 0, 0), 0.0)

    def test_meta_largo_plazo(self):
        resultado = metas.meta_largo_plazo(12500)
        self.assertAlmostEqual(resultado["emisiones_maximas_2050"], 1250.0)
        self.assertIn("remociones permanentes", resultado["nota"])

    def test_validacion_completa(self):
        resultado = metas.validar_meta({
            "anio_base": 2024, "anio_meta": 2030, "anio_actual": 2026,
            "alcance_1": 3000, "alcance_2": 9500, "alcance_3": 41000,
            "meta_alcance_3": True, "cobertura_alcance_3": 70, "exclusiones_pct": 2,
        })
        self.assertTrue(resultado["cumple_todo"], resultado["pendientes"])
        self.assertTrue(resultado["exige_meta_alcance_3"])

    def test_detecta_falta_de_meta_alcance_3(self):
        resultado = metas.validar_meta({
            "anio_base": 2024, "anio_meta": 2030, "anio_actual": 2026,
            "alcance_1": 3000, "alcance_2": 9500, "alcance_3": 41000,
        })
        self.assertFalse(resultado["cumple_todo"])
        self.assertTrue(any("alcance 3" in p["criterio"] for p in resultado["pendientes"]))

    def test_detecta_anio_base_antiguo_y_creditos(self):
        resultado = metas.validar_meta({
            "anio_base": 2010, "anio_meta": 2030, "anio_actual": 2026,
            "alcance_1": 100, "alcance_2": 100, "alcance_3": 10,
            "exclusiones_pct": 9, "usa_creditos": True,
        })
        criterios = {p["criterio"] for p in resultado["pendientes"]}
        self.assertIn("año base", criterios)
        self.assertIn("exclusiones", criterios)
        self.assertIn("sin compensaciones", criterios)

    def test_alcance_3_bajo_no_lo_exige(self):
        resultado = metas.validar_meta({
            "anio_base": 2024, "anio_meta": 2030, "anio_actual": 2026,
            "alcance_1": 500, "alcance_2": 500, "alcance_3": 100,
        })
        self.assertFalse(resultado["exige_meta_alcance_3"])


class PruebaMonteCarlo(unittest.TestCase):
    CONFIG = {
        "emisiones_actuales": 12500, "anio_inicio": 2024, "anio_meta": 2030, "emisiones_meta": 9350,
        "crecimiento": {"tipo": "normal", "media": 0.025, "desviacion": 0.015},
        "descarbonizacion_red": {"tipo": "triangular", "min": 0.01, "moda": 0.025, "max": 0.045},
        "eficiencia": {"tipo": "triangular", "min": 0.0, "moda": 0.02, "max": 0.03},
        "proyectos": [{"nombre": "Solar", "probabilidad": 0.7, "anio": 2027,
                       "reduccion": {"tipo": "triangular", "min": 0.03, "moda": 0.06, "max": 0.09}}],
    }

    def test_resultado_reproducible(self):
        primero = metas.monte_carlo(self.CONFIG, iteraciones=3000)
        segundo = metas.monte_carlo(self.CONFIG, iteraciones=3000)
        self.assertEqual(primero["probabilidad_pct"], segundo["probabilidad_pct"])
        self.assertEqual(primero["percentiles"]["p50"], segundo["percentiles"]["p50"])

    def test_meta_dificil_da_probabilidad_baja(self):
        resultado = metas.monte_carlo(self.CONFIG, iteraciones=3000)
        self.assertLess(resultado["probabilidad_pct"], 30)
        self.assertGreater(resultado["brecha_mediana"], 0)
        self.assertIn("no es creible", resultado["lectura"])

    def test_meta_facil_da_probabilidad_alta(self):
        facil = dict(self.CONFIG, emisiones_meta=13000)
        resultado = metas.monte_carlo(facil, iteraciones=3000)
        self.assertGreater(resultado["probabilidad_pct"], 80)
        self.assertEqual(resultado["brecha_mediana"], 0.0)
        self.assertIn("creible", resultado["lectura"])

    def test_percentiles_ordenados(self):
        resultado = metas.monte_carlo(self.CONFIG, iteraciones=3000)
        percentiles = resultado["percentiles"]
        valores = [percentiles[c] for c in ("p5", "p10", "p25", "p50", "p75", "p90", "p95")]
        self.assertEqual(valores, sorted(valores))

    def test_distribucion_desconocida(self):
        malo = dict(self.CONFIG, crecimiento={"tipo": "caotica"})
        with self.assertRaises(Problema):
            metas.monte_carlo(malo, iteraciones=10)

    def test_publica_los_supuestos(self):
        resultado = metas.monte_carlo(self.CONFIG, iteraciones=1000)
        self.assertIn("crecimiento", resultado["supuestos"])
        self.assertIn("supuestos", resultado["aviso"])


class PruebaMacc(unittest.TestCase):
    def test_factor_recuperacion_capital(self):
        self.assertAlmostEqual(macc.factor_recuperacion_capital(0.10, 10), 0.16275, places=5)
        self.assertAlmostEqual(macc.factor_recuperacion_capital(0.10, 20), 0.11746, places=5)
        self.assertAlmostEqual(macc.factor_recuperacion_capital(0.0, 10), 0.1, places=5)

    def test_costo_marginal_ejemplo(self):
        resultado = macc.costo_marginal(MEDIDAS[0])
        self.assertAlmostEqual(resultado["capex_anualizado"], 7323.8, places=0)
        self.assertAlmostEqual(resultado["costo_por_tonelada"], -144.1, places=1)
        self.assertTrue(resultado["ahorra_dinero"])

    def test_curva_ordenada_y_acumulada(self):
        resultado = macc.curva(MEDIDAS)
        nombres = [m["medida"] for m in resultado["medidas"]]
        self.assertEqual(nombres[0], "Iluminacion LED")
        self.assertEqual(nombres[-1], "Electrificacion de flota")
        self.assertAlmostEqual(resultado["medidas"][2]["abatimiento_acumulado"], 268.0, places=0)
        self.assertAlmostEqual(resultado["potencial_total"], 543.0, places=0)
        self.assertAlmostEqual(resultado["potencial_con_ahorro"], 268.0, places=0)

    def test_plan_para_cubrir_la_brecha(self):
        resultado = macc.curva(MEDIDAS, brecha=250)
        plan = resultado["plan_para_la_brecha"]
        self.assertTrue(plan["alcanza"])
        self.assertEqual(plan["medidas"], ["Iluminacion LED", "Motores eficientes", "Solar FV"])
        self.assertEqual(plan["faltante"], 0.0)

    def test_brecha_mayor_que_el_potencial(self):
        plan = macc.curva(MEDIDAS, brecha=900)["plan_para_la_brecha"]
        self.assertFalse(plan["alcanza"])
        self.assertGreater(plan["faltante"], 0)

    def test_medida_sin_abatimiento(self):
        with self.assertRaises(Problema) as contexto:
            macc.costo_marginal({"medida": "Cambiar ampolletas", "capex": 1000})
        self.assertIn("toneladas", contexto.exception.mensaje)

    def test_sin_medidas(self):
        with self.assertRaises(Problema):
            macc.curva([])

    def test_vida_util_invalida(self):
        with self.assertRaises(Problema):
            macc.factor_recuperacion_capital(0.1, 0)


class PruebaModuloMeta(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloMeta, self).setUp()
        from modulos import meta
        self.meta = meta
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "anio_base": 2024,
                               "sector": "Industria", "tamano": "pequena"}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def test_definir_y_ver_trayectoria(self):
        definida = self.meta.definir(dict(self.opciones, base=12500, anio_base=2024,
                                          anio_meta=2034, tasa=0.042)).resultado
        self.assertAlmostEqual(definida["meta"]["emisiones_meta"], 7250.0, places=1)
        trayecto = self.meta.trayectoria(self.opciones).resultado
        self.assertEqual(len(trayecto["trayectoria"]), 11)

    def test_probabilidad_necesita_meta(self):
        with self.assertRaises(Problema):
            self.meta.probabilidad(self.opciones)

    def test_probabilidad_y_informe(self):
        self.meta.definir(dict(self.opciones, base=12500, anio_base=2024, anio_meta=2030))
        resultado = self.meta.probabilidad(dict(self.opciones, iteraciones=1000)).resultado
        self.assertIn("probabilidad_pct", resultado)
        informe = self.meta.informe_html(self.opciones)
        import os
        self.assertTrue(os.path.isfile(informe["archivo"]))

    def test_plan_sin_planilla(self):
        with self.assertRaises(Problema) as contexto:
            self.meta.plan(self.opciones)
        self.assertIn("medidas", contexto.exception.mensaje.lower())


if __name__ == "__main__":
    unittest.main()
