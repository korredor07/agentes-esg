# -*- coding: utf-8 -*-
"""Pruebas de la Ley REP (Ley 20.920).

Los casos numericos son los ejemplos resueltos de la investigacion normativa
(docs/investigacion/04-ley-rep-retc.md), calculados a mano:

- Envases domiciliarios 2026: 500 t de plastico en 2025, meta 11% -> 55 t.
- Neumaticos categoria A 2026: 1.000 t en 2025 x FD 0,84 = 840 t de base;
  recoleccion 80% -> 672 t y valorizacion 60% -> 504 t.
- Aceites lubricantes 2027: 200 t en 2026 x (1 - 0,3) = 140 t de base.
- Pilas y AEE 2028: promedio de tres anios y meta prorrateada a 7/12.
"""

import json
import os
import subprocess
import sys
import unittest

from ayuda_pruebas import MOTOR, PruebaConCarpeta  # noqa: E402

from calculos import rep  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

ESG = os.path.join(MOTOR, "esg.py")


def por_llave(items):
    """Indexa los resultados por categoria, material y tipo de meta."""
    return {(i["categoria"], i["material"], i["tipo_meta"]): i for i in items}


class PruebaTablaDeMetas(unittest.TestCase):
    def setUp(self):
        self.metas = rep.cargar_metas()

    def test_carga_la_tabla_con_los_cuatro_decretos(self):
        self.assertTrue(self.metas)
        productos = {m["producto"] for m in self.metas}
        self.assertEqual(productos, {"envases", "neumaticos", "pilas_y_aee"})
        decretos = {m["decreto"] for m in self.metas}
        self.assertEqual(decretos, {"DS 12/2020 MMA", "DS 8/2019 MMA", "DS 22/2025 MMA"})
        for fila in self.metas:
            self.assertTrue(fila["articulo"], "toda meta debe citar su articulo")
            self.assertTrue(fila["url"], "toda meta debe traer su fuente")

    def test_metas_de_envases_2026_son_las_del_decreto(self):
        datos = rep.metas_de("envases", 2026, metas=self.metas)
        self.assertTrue(datos["hay_metas"])
        valores = {(m["categoria"], m["material"]): m["meta_valorizacion_pct"] for m in datos["metas"]}
        self.assertEqual(valores[("domiciliario", "plastico")], 11.0)
        self.assertEqual(valores[("domiciliario", "vidrio")], 22.0)
        self.assertEqual(valores[("domiciliario", "papel_y_carton")], 18.0)
        self.assertEqual(valores[("no_domiciliario", "metal")], 51.0)
        self.assertEqual(valores[("no_domiciliario", "papel_y_carton")], 65.0)
        self.assertEqual(datos["metas"][0]["articulo"], "Art. 21 del DS 12/2020")

    def test_neumaticos_tienen_metas_distintas_de_recoleccion_y_valorizacion(self):
        datos = rep.metas_de("neumaticos", 2026, categoria="A", metas=self.metas)
        meta = datos["metas"][0]
        self.assertEqual(meta["meta_recoleccion_pct"], 80.0)
        self.assertEqual(meta["meta_valorizacion_pct"], 60.0)
        self.assertFalse(meta["meta_unica"])
        # En categoria B la recoleccion se entiende cumplida al valorizar (art. 21).
        categoria_b = rep.metas_de("neumaticos", 2026, categoria="B", metas=self.metas)["metas"][0]
        self.assertTrue(categoria_b["meta_unica"])
        self.assertEqual(categoria_b["meta_valorizacion_pct"], 25.0)

    def test_meta_que_rige_de_un_anio_en_adelante(self):
        # El DS 8/2019 fija 90% "a contar del octavo anio de vigencia" (2030).
        for anio in (2030, 2033, 2040):
            meta = rep.metas_de("neumaticos", anio, categoria="a", metas=self.metas)["metas"][0]
            self.assertEqual(meta["meta_recoleccion_pct"], 90.0)
            self.assertEqual(meta["anio_de_la_tabla"], "2030+")

    def test_prorrateo_del_primer_anio_de_envases(self):
        # Vigencia 16-09-2023 -> MO = 3 -> la meta de 3% queda en 0,75%.
        meta = rep.metas_de("envases", 2023, categoria="domiciliario", material="plastico",
                            metas=self.metas)["metas"][0]
        self.assertEqual(meta["meta_de_tabla_valorizacion_pct"], 3.0)
        self.assertAlmostEqual(meta["meta_valorizacion_pct"], 0.75)
        self.assertTrue(meta["prorrateada"])
        self.assertIn("art. 1", meta["explicacion_prorrateo"].lower())
        # En 2024 ya no se prorratea.
        siguiente = rep.metas_de("envases", 2024, categoria="domiciliario", material="plastico",
                                 metas=self.metas)["metas"][0]
        self.assertEqual(siguiente["meta_valorizacion_pct"], 6.0)
        self.assertFalse(siguiente["prorrateada"])

    def test_prorrateo_del_primer_anio_de_pilas_y_aee(self):
        # Vigencia 07-05-2028 -> MO = 7 -> la meta general de 3% queda en 1,75%.
        meta = rep.metas_de("pilas", 2028, metas=self.metas)["metas"][0]
        self.assertEqual(meta["meta_de_tabla_valorizacion_pct"], 3.0)
        self.assertAlmostEqual(meta["meta_valorizacion_pct"], 1.75)
        self.assertTrue(meta["prorrateada"])

    def test_pilas_no_arrastran_las_metas_de_aee(self):
        # Las metas especificas de AIT y de paneles fotovoltaicos son de AEE.
        pilas = rep.metas_de("pilas", 2030, metas=self.metas)
        self.assertEqual([m["categoria"] for m in pilas["metas"]], ["general"])
        aee = rep.metas_de("aee", 2030, metas=self.metas)
        self.assertEqual(sorted(m["categoria"] for m in aee["metas"]), ["ait", "general", "pfv"])
        valores = {m["categoria"]: m["meta_valorizacion_pct"] for m in aee["metas"]}
        self.assertEqual(valores, {"general": 8.0, "ait": 6.0, "pfv": 10.0})

    def test_anio_sin_meta(self):
        # Antes de que rijan las metas.
        antes = rep.metas_de("envases", 2022, metas=self.metas)
        self.assertFalse(antes["hay_metas"])
        self.assertEqual(antes["motivo_clave"], "antes_de_vigencia")
        self.assertIn("2 transitorio", antes["que_hacer"])
        # Despues del ultimo anio de la tabla.
        despues = rep.metas_de("envases", 2040, metas=self.metas)
        self.assertFalse(despues["hay_metas"])
        self.assertEqual(despues["motivo_clave"], "fuera_de_tabla")
        self.assertIn("2034", despues["motivo"])
        # Anio en que el decreto dice expresamente que no hay meta especifica.
        ait = rep.metas_de("aee", 2028, categoria="ait", metas=self.metas)
        self.assertFalse(ait["hay_metas"])
        self.assertTrue(ait["metas"][0]["sin_meta_este_anio"])

    def test_producto_desconocido(self):
        with self.assertRaises(Problema) as contexto:
            rep.metas_de("pilaz", 2026, metas=self.metas)
        self.assertIn("pilaz", contexto.exception.mensaje)
        self.assertIn("Envases y embalajes", contexto.exception.sugerencia)

    def test_aceites_no_inventan_metas(self):
        datos = rep.metas_de("aceites lubricantes", 2027, metas=self.metas)
        self.assertFalse(datos["hay_metas"])
        self.assertEqual(datos["metas"], [])
        self.assertEqual(datos["motivo_clave"], "sin_tabla_verificada")
        self.assertIn("imagen", datos["motivo"])
        self.assertIn("No voy a inventar", datos["motivo"])

    def test_baterias_no_tienen_decreto(self):
        datos = rep.metas_de("baterias", 2026, metas=self.metas)
        self.assertFalse(datos["hay_metas"])
        self.assertEqual(datos["motivo_clave"], "sin_decreto")
        self.assertIn("declarar", datos["que_hacer"])

    def test_productos_prioritarios(self):
        catalogo = rep.productos_prioritarios()
        self.assertEqual(len(catalogo), 6)
        self.assertEqual([p["producto"] for p in catalogo],
                         ["aceites_lubricantes", "aee", "baterias", "envases", "neumaticos", "pilas"])
        con_metas = [p["producto"] for p in catalogo if p["tiene_metas_cargadas"]]
        self.assertEqual(sorted(con_metas), ["aee", "envases", "neumaticos", "pilas"])


class PruebaFormulas(unittest.TestCase):
    """Un ejemplo numerico resuelto a mano por cada formula de decreto."""

    def setUp(self):
        self.metas = rep.cargar_metas()

    def calcular(self, declaraciones, anio, producto, **extra):
        return rep.calcular_cumplimiento(declaraciones, anio, producto, metas=self.metas, **extra)

    def test_f1_envases_domiciliarios(self):
        # 500 t de plastico en 2025, meta 2026 = 11% -> 55 t exigidas.
        # Se valorizan 60 t -> 60 x 100 / 500 = 12% -> cumple.
        declaraciones = [
            {"_fila": 2, "producto": "envases", "categoria": "domiciliario", "material": "plastico",
             "anio": 2025, "toneladas_puestas_en_el_mercado": 500},
            {"_fila": 3, "producto": "envases", "categoria": "domiciliario", "material": "plastico",
             "anio": 2026, "toneladas_recolectadas": 60, "toneladas_valorizadas": 60},
        ]
        item = self.calcular(declaraciones, 2026, "envases")["items"][0]
        self.assertEqual(item["anios_base"], [2025])
        self.assertEqual(item["toneladas_puestas_en_el_mercado"], 500.0)
        self.assertEqual(item["factor_denominador"], 1.0)
        self.assertEqual(item["meta_aplicable_pct"], 11.0)
        self.assertEqual(item["toneladas_exigidas"], 55.0)
        self.assertEqual(item["toneladas_gestionadas"], 60.0)
        self.assertEqual(item["porcentaje_logrado"], 12.0)
        self.assertEqual(item["brecha_t"], 0.0)
        self.assertEqual(item["estado"], "cumple")
        self.assertEqual(item["tipo_meta"], "recoleccion y valorizacion")

    def test_f2_envases_no_domiciliarios(self):
        # 1.000 t de plastico no domiciliario en 2025, meta 2026 = 32% -> 320 t.
        # Se valorizan 300 t -> falta 20 t.
        declaraciones = [
            {"_fila": 2, "producto": "envases", "categoria": "no domiciliario", "material": "plastico",
             "anio": 2025, "toneladas_puestas_en_el_mercado": 1000},
            {"_fila": 3, "producto": "envases", "categoria": "no domiciliario", "material": "plastico",
             "anio": 2026, "toneladas_valorizadas": 300},
        ]
        item = self.calcular(declaraciones, 2026, "envases", categoria="no domiciliario",
                             material="plastico")["items"][0]
        self.assertEqual(item["meta_aplicable_pct"], 32.0)
        self.assertEqual(item["toneladas_exigidas"], 320.0)
        self.assertEqual(item["brecha_t"], 20.0)
        self.assertEqual(item["estado"], "no cumple")
        self.assertEqual(item["porcentaje_logrado"], 30.0)

    def test_f4_neumaticos_aplican_el_factor_de_desgaste(self):
        # 1.000 t categoria A en 2025 -> base 1.000 x 0,84 = 840 t.
        # Recoleccion 80% = 672 t y valorizacion 60% = 504 t.
        declaraciones = [
            {"_fila": 2, "producto": "neumaticos", "categoria": "A", "anio": 2025,
             "toneladas_puestas_en_el_mercado": 1000},
            {"_fila": 3, "producto": "neumaticos", "categoria": "A", "anio": 2026,
             "toneladas_recolectadas": 700, "toneladas_valorizadas": 520},
        ]
        items = por_llave(self.calcular(declaraciones, 2026, "neumaticos")["items"])
        recoleccion = items[("a", "", "recoleccion")]
        valorizacion = items[("a", "", "valorizacion")]
        self.assertEqual(recoleccion["factor_denominador"], 0.84)
        self.assertEqual(recoleccion["base_de_calculo_t"], 840.0)
        self.assertEqual(recoleccion["toneladas_exigidas"], 672.0)
        self.assertEqual(recoleccion["estado"], "cumple")
        self.assertEqual(valorizacion["toneladas_exigidas"], 504.0)
        self.assertAlmostEqual(valorizacion["porcentaje_logrado"], 61.9048, places=3)
        self.assertEqual(valorizacion["estado"], "cumple")
        # El error frecuente: 520 / 1.000 = 52% daria un falso incumplimiento.
        self.assertGreater(valorizacion["porcentaje_logrado"], 60.0)

    def test_f4_categoria_b_usa_otro_factor(self):
        declaraciones = [
            {"_fila": 2, "producto": "neumaticos", "categoria": "B", "anio": 2025,
             "toneladas_puestas_en_el_mercado": 1000},
            {"_fila": 3, "producto": "neumaticos", "categoria": "B", "anio": 2026,
             "toneladas_valorizadas": 180},
        ]
        item = self.calcular(declaraciones, 2026, "neumaticos", categoria="b")["items"][0]
        self.assertEqual(item["factor_denominador"], 0.75)
        self.assertEqual(item["base_de_calculo_t"], 750.0)      # 1.000 x 0,75
        self.assertEqual(item["meta_aplicable_pct"], 25.0)
        self.assertEqual(item["toneladas_exigidas"], 187.5)
        self.assertEqual(item["brecha_t"], 7.5)
        self.assertEqual(item["estado"], "no cumple")

    def test_f5_aceites_usan_la_tasa_de_perdida_pero_no_inventan_la_meta(self):
        # 200 t en 2026 -> base 200 x (1 - 0,3) = 140 t. 72 t valorizadas = 51,43%.
        declaraciones = [
            {"_fila": 2, "producto": "aceites lubricantes", "anio": 2026,
             "toneladas_puestas_en_el_mercado": 200},
            {"_fila": 3, "producto": "aceites lubricantes", "anio": 2027,
             "toneladas_valorizadas": 72},
        ]
        calculo = self.calcular(declaraciones, 2027, "aceites")
        item = calculo["items"][0]
        self.assertAlmostEqual(item["factor_denominador"], 0.7)
        self.assertEqual(item["base_de_calculo_t"], 140.0)
        self.assertAlmostEqual(item["porcentaje_logrado"], 51.4286, places=3)
        self.assertIsNone(item["meta_aplicable_pct"])
        self.assertIsNone(item["toneladas_exigidas"])
        self.assertEqual(item["estado"], "sin meta verificada")
        self.assertIn("imagen", item["motivo"])
        # Sin la tasa de perdida seria 72/200 = 36%: el factor evita ese falso incumplimiento.
        self.assertGreater(item["porcentaje_logrado"], 36.0)

    def test_f6_pilas_y_aee_promedian_tres_anios(self):
        # 100 + 200 + 300 = 600 -> promedio 200 t. Meta 2028 = 3% x 7/12 = 1,75% -> 3,5 t.
        declaraciones = [
            {"_fila": 2, "producto": "aee", "categoria": "otros", "anio": 2025,
             "toneladas_puestas_en_el_mercado": 100},
            {"_fila": 3, "producto": "aee", "categoria": "otros", "anio": 2026,
             "toneladas_puestas_en_el_mercado": 200},
            {"_fila": 4, "producto": "aee", "categoria": "otros", "anio": 2027,
             "toneladas_puestas_en_el_mercado": 300},
            {"_fila": 5, "producto": "aee", "categoria": "otros", "anio": 2028,
             "toneladas_valorizadas": 4},
        ]
        item = self.calcular(declaraciones, 2028, "aee")["items"][0]
        self.assertEqual(item["anios_base"], [2027, 2026, 2025])
        self.assertEqual(item["toneladas_puestas_suma"], 600.0)
        self.assertEqual(item["toneladas_puestas_en_el_mercado"], 200.0)
        self.assertAlmostEqual(item["meta_aplicable_pct"], 1.75)
        self.assertEqual(item["toneladas_exigidas"], 3.5)
        self.assertEqual(item["estado"], "cumple")
        self.assertTrue(item["prorrateada"])

    def test_f7_y_f8_metas_especificas_de_aee(self):
        # AIT: 60 t cada anio -> promedio 60, meta 2030 = 6% -> 3,6 t.
        # Meta general: 60 + 140 = 200 t de promedio, meta 8% -> 16 t, y las
        # toneladas de AIT tambien cuentan para ella (art. 23).
        # PFV: 50 t de promedio, meta 10% -> 5 t, solo con residuos de PFV.
        declaraciones = []
        fila = 1
        for anio in (2027, 2028, 2029):
            for categoria, toneladas in (("ait", 60), ("otros", 140), ("pfv", 50)):
                fila += 1
                declaraciones.append({"_fila": fila, "producto": "aee", "categoria": categoria,
                                      "anio": anio, "toneladas_puestas_en_el_mercado": toneladas})
        declaraciones += [
            {"_fila": 20, "producto": "aee", "categoria": "ait", "anio": 2030, "toneladas_valorizadas": 4},
            {"_fila": 21, "producto": "aee", "categoria": "otros", "anio": 2030, "toneladas_valorizadas": 13},
            {"_fila": 22, "producto": "aee", "categoria": "pfv", "anio": 2030, "toneladas_valorizadas": 2},
        ]
        items = por_llave(self.calcular(declaraciones, 2030, "aee")["items"])
        general = items[("general", "", "recoleccion y valorizacion")]
        ait = items[("ait", "", "recoleccion y valorizacion")]
        pfv = items[("pfv", "", "recoleccion y valorizacion")]

        self.assertEqual(general["toneladas_puestas_en_el_mercado"], 200.0)   # AIT + otros, sin PFV
        self.assertEqual(general["toneladas_exigidas"], 16.0)
        self.assertEqual(general["toneladas_gestionadas"], 17.0)              # 4 de AIT + 13 de otros
        self.assertEqual(general["estado"], "cumple")

        self.assertEqual(ait["toneladas_puestas_en_el_mercado"], 60.0)
        self.assertEqual(ait["toneladas_exigidas"], 3.6)
        self.assertEqual(ait["estado"], "cumple")

        self.assertEqual(pfv["toneladas_puestas_en_el_mercado"], 50.0)
        self.assertEqual(pfv["toneladas_exigidas"], 5.0)
        self.assertEqual(pfv["brecha_t"], 3.0)
        self.assertEqual(pfv["estado"], "no cumple")

    def test_incumplimiento_con_brecha_en_toneladas(self):
        # 300 t de vidrio en 2025, meta 2026 = 22% -> 66 t. Se valorizan 50 -> faltan 16.
        declaraciones = [
            {"_fila": 2, "producto": "envases", "categoria": "domiciliario", "material": "vidrio",
             "anio": 2025, "toneladas_puestas_en_el_mercado": 300},
            {"_fila": 3, "producto": "envases", "categoria": "domiciliario", "material": "vidrio",
             "anio": 2026, "toneladas_valorizadas": 50},
        ]
        calculo = self.calcular(declaraciones, 2026, "envases", material="vidrio")
        item = calculo["items"][0]
        self.assertEqual(item["toneladas_exigidas"], 66.0)
        self.assertEqual(item["brecha_t"], 16.0)
        self.assertEqual(item["estado"], "no cumple")
        self.assertEqual(calculo["resumen"]["no_cumple"], 1)
        self.assertEqual(calculo["resumen"]["brecha_total_t"], 16.0)

    def test_sin_toneladas_del_anio_base_no_calcula(self):
        declaraciones = [
            {"_fila": 2, "producto": "envases", "categoria": "domiciliario", "material": "metal",
             "anio": 2026, "toneladas_valorizadas": 10},
        ]
        calculo = self.calcular(declaraciones, 2026, "envases", material="metal")
        item = calculo["items"][0]
        self.assertEqual(item["estado"], "sin datos")
        self.assertIsNone(item["toneladas_exigidas"])
        self.assertTrue(any("2025" in a for a in calculo["advertencias"]))

    def test_avisa_los_anios_que_faltan_en_el_promedio_movil(self):
        declaraciones = [
            {"_fila": 2, "producto": "pilas", "anio": 2025, "toneladas_puestas_en_el_mercado": 100},
            {"_fila": 3, "producto": "pilas", "anio": 2027, "toneladas_puestas_en_el_mercado": 300},
            {"_fila": 4, "producto": "pilas", "anio": 2028, "toneladas_valorizadas": 2},
        ]
        calculo = self.calcular(declaraciones, 2028, "pilas")
        item = calculo["items"][0]
        self.assertAlmostEqual(item["toneladas_puestas_en_el_mercado"], 133.3333, places=3)
        self.assertTrue(any("2026" in a and "dividir" in a for a in calculo["advertencias"]))


class PruebaErroresUtiles(unittest.TestCase):
    """Los mensajes los lee una persona sin conocimientos tecnicos."""

    def test_falta_la_categoria_del_envase(self):
        with self.assertRaises(Problema) as contexto:
            rep.calcular_cumplimiento(
                [{"_fila": 7, "producto": "envases", "anio": 2026,
                  "toneladas_puestas_en_el_mercado": 10}], 2026, "envases")
        self.assertIn("fila 7", contexto.exception.mensaje)
        self.assertIn("domiciliario", contexto.exception.sugerencia)

    def test_material_desconocido_explica_los_envases_compuestos(self):
        with self.assertRaises(Problema) as contexto:
            rep.calcular_cumplimiento(
                [{"_fila": 8, "producto": "envases", "categoria": "domiciliario", "material": "corcho",
                  "anio": 2026, "toneladas_puestas_en_el_mercado": 1}], 2026, "envases")
        self.assertIn("corcho", contexto.exception.mensaje)
        self.assertIn("85%", contexto.exception.sugerencia)

    def test_cantidad_que_no_es_numero(self):
        with self.assertRaises(Problema) as contexto:
            rep.calcular_cumplimiento(
                [{"_fila": 9, "producto": "neumaticos", "categoria": "A", "anio": 2025,
                  "toneladas_puestas_en_el_mercado": "mil kilos"}], 2026, "neumaticos")
        self.assertIn("no es un numero", contexto.exception.mensaje)
        self.assertIn("deja la celda vacia", contexto.exception.sugerencia)

    def test_toneladas_negativas(self):
        with self.assertRaises(Problema) as contexto:
            rep.calcular_cumplimiento(
                [{"_fila": 10, "producto": "neumaticos", "categoria": "A", "anio": 2025,
                  "toneladas_puestas_en_el_mercado": -5}], 2026, "neumaticos")
        self.assertIn("negativo", contexto.exception.mensaje)

    def test_anio_mal_escrito(self):
        with self.assertRaises(Problema) as contexto:
            rep.metas_de("envases", "el proximo")
        self.assertIn("cuatro digitos", contexto.exception.sugerencia)

    def test_acepta_numeros_escritos_a_la_chilena(self):
        declaraciones = [
            {"_fila": 2, "producto": "neumaticos", "categoria": "a", "anio": 2025,
             "toneladas_puestas_en_el_mercado": "1.000"},
            {"_fila": 3, "producto": "neumaticos", "categoria": "a", "anio": 2026,
             "toneladas_valorizadas": "520,5"},
        ]
        items = por_llave(rep.calcular_cumplimiento(declaraciones, 2026, "neumaticos")["items"])
        self.assertEqual(items[("a", "", "valorizacion")]["base_de_calculo_t"], 840.0)
        self.assertEqual(items[("a", "", "valorizacion")]["toneladas_gestionadas"], 520.5)


class PruebaModuloRep(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloRep, self).setUp()
        from modulos import plantilla as modulo_plantilla
        from modulos import rep as modulo
        self.modulo = modulo
        self.plantilla = modulo_plantilla
        espacio.crear_empresa({"nombre": "Envasadora Prueba SpA", "pais": "CL", "sector": "Alimentos",
                               "tamano": "mediana", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Envasadora Prueba SpA"}

    def test_metas_no_necesita_empresa(self):
        respuesta = self.modulo.metas({"producto": "envases", "anio": "2026"})
        self.assertTrue(respuesta.resultado["hay_metas"])
        self.assertEqual(len(respuesta.resultado["metas"]), 8)
        self.assertTrue(any("plastico" in t.lower() for t in respuesta.resultado["en_palabras"]))
        self.assertTrue(respuesta.fuentes)
        self.assertTrue(any("no asesoria legal" in a for a in respuesta.advertencias))

    def test_metas_sin_producto(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.metas({})
        self.assertIn("envases", contexto.exception.sugerencia)

    def test_calcular_sin_planilla(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.calcular(dict(self.opciones, anio="2026"))
        self.assertIn("rep.xlsx", contexto.exception.mensaje)
        self.assertIn("plantilla crear --tipo rep", contexto.exception.sugerencia)

    def test_flujo_completo_desde_la_planilla(self):
        creada = self.plantilla.crear(dict(self.opciones, tipo="rep"))
        self.assertTrue(os.path.isfile(creada["archivo"]))

        respuesta = self.modulo.calcular(dict(self.opciones, anio="2026"))
        resultado = respuesta.resultado
        self.assertEqual(resultado["total"]["metas_evaluadas"], 4)
        self.assertEqual(resultado["total"]["cumple"], 3)
        self.assertEqual(resultado["total"]["no_cumple"], 1)
        self.assertEqual(resultado["total"]["brecha_total_t"], 16.0)
        self.assertTrue(os.path.isfile(resultado["resultado_guardado_en"]))
        with open(resultado["resultado_guardado_en"], encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        self.assertEqual(guardado["anio"], 2026)

        solo_neumaticos = self.modulo.calcular(dict(self.opciones, anio="2026",
                                                    producto="neumaticos")).resultado
        self.assertEqual([p["producto"] for p in solo_neumaticos["productos"]], ["neumaticos"])
        self.assertEqual(solo_neumaticos["total"]["metas_evaluadas"], 2)

    def test_obligaciones_segun_el_perfil(self):
        self.plantilla.crear(dict(self.opciones, tipo="rep"))
        respuesta = self.modulo.obligaciones(self.opciones)
        resultado = respuesta.resultado
        productos = [p["producto"] for p in resultado["productos_que_le_aplican"]]
        self.assertEqual(sorted(productos), ["envases", "neumaticos"])
        self.assertIn("importa", resultado["quien_es_productor"]["importadores"])
        self.assertTrue(any("31 de octubre" in p["fecha"] for p in resultado["calendario_anual"]))
        self.assertEqual(len(resultado["sanciones"]["rangos"]), 3)
        self.assertIn("10.000", resultado["sanciones"]["rangos"][0]["sancion"])
        self.assertFalse(resultado["umbral_de_envases"]["bajo_el_umbral"])
        # La declaracion anual del productor no tiene fecha reglamentaria confirmada.
        self.assertTrue(any("convocatoria" in a for a in respuesta.advertencias))

    def test_obligaciones_avisa_si_la_empresa_no_es_chilena(self):
        espacio.crear_empresa({"nombre": "Andina Peru SAC", "pais": "PE"}, raiz=self.carpeta)
        respuesta = self.modulo.obligaciones({"raiz": self.carpeta, "empresa": "Andina Peru SAC"})
        self.assertTrue(any("chilena" in a for a in respuesta.advertencias))

    def test_el_motor_responde_json_valido_por_la_linea_de_comandos(self):
        proceso = subprocess.run(
            [sys.executable, ESG, "rep", "metas", "--producto", "envases", "--anio", "2026"],
            capture_output=True, text=True, encoding="utf-8")
        datos = json.loads(proceso.stdout)
        self.assertEqual(proceso.returncode, 0)
        self.assertTrue(datos["ok"])
        self.assertEqual(datos["resultado"]["decreto"], "DS 12/2020 MMA")
        self.assertTrue(datos["fuentes"])


if __name__ == "__main__":
    unittest.main()
