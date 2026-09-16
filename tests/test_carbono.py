# -*- coding: utf-8 -*-
"""Pruebas del calculo de huella de carbono."""

import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import carbono  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

CABECERA = ("id,alcance,categoria,recurso,pais,anio,unidad,kg_co2_por_unidad,kg_ch4_por_unidad,"
            "kg_n2o_por_unidad,kg_co2e_por_unidad,set_pcg,calidad,fuente,url,licencia,verificado_el,notas\n")

FILAS = [
    # electricidad de Chile, ya expresada en CO2e
    "cl-elec-2024,2,,electricidad,CL,2024,kWh,,,,0.30,AR6,alta,Ministerio de Energia,https://ejemplo.cl,,2026-09-15,",
    "cl-elec-2023,2,,electricidad,CL,2023,kWh,,,,0.35,AR6,alta,Ministerio de Energia,https://ejemplo.cl,,2026-09-15,",
    # diesel por litro, separado por gases
    "gen-diesel,1,,diesel,*,2024,L,2.60,0.0001,0.0002,,,media,IPCC 2006,https://ejemplo.org,,2026-09-15,",
    # gas natural en Peru
    "pe-gn,1,,gas natural,PE,2024,m3,1.90,,,,,media,MINAM,https://ejemplo.pe,,2026-09-15,",
    # refrigerante: el factor es el propio PCG
    "ref-r410a,1,,r-410a,*,2024,kg,,,,2256.0,AR6,alta,IPCC AR6,https://ejemplo.org,,2026-09-15,",
    # alcance 3 por gasto
    "gasto-hoteles,3,6,hoteles,*,2024,USD,,,,0.25,AR6,baja,EPA,https://ejemplo.gov,,2026-09-15,",
]

PCG = "gas,ar5,ar6,fuente,url\nch4,28,29.8,IPCC,https://ipcc.ch\nn2o,265,273,IPCC,https://ipcc.ch\n"


class BasePruebaCarbono(PruebaConCarpeta):
    def setUp(self):
        super(BasePruebaCarbono, self).setUp()
        self.ruta_factores = self.ruta("factores.csv")
        with open(self.ruta_factores, "w", encoding="utf-8") as archivo:
            archivo.write(CABECERA + "\n".join(FILAS) + "\n")
        self.ruta_pcg = self.ruta("pcg.csv")
        with open(self.ruta_pcg, "w", encoding="utf-8") as archivo:
            archivo.write(PCG)
        self.factores = carbono.cargar_factores(self.ruta_factores)
        self.pcg = carbono.cargar_pcg(self.ruta_pcg)


class PruebaCatalogo(BasePruebaCarbono):
    def test_carga_factores(self):
        self.assertEqual(len(self.factores), 6)
        electricidad = [f for f in self.factores if f["recurso"] == "electricidad"]
        self.assertEqual(len(electricidad), 2)
        self.assertEqual(electricidad[0]["pais"], "CL")
        self.assertEqual(electricidad[0]["alcance"], 2)

    def test_catalogo_faltante(self):
        with self.assertRaises(Problema) as contexto:
            carbono.cargar_factores(self.ruta("no-existe.csv"))
        self.assertIn("catalogo de factores", contexto.exception.mensaje)

    def test_alias_de_recursos(self):
        self.assertEqual(carbono.normalizar_recurso("Energía eléctrica"), "electricidad")
        self.assertEqual(carbono.normalizar_recurso("Petróleo Diesel"), "diesel")
        self.assertEqual(carbono.normalizar_recurso("Bencina"), "gasolina")
        self.assertEqual(carbono.normalizar_recurso("Gas Licuado"), "glp")

    def test_co2e_con_pcg(self):
        diesel = [f for f in self.factores if f["recurso"] == "diesel"][0]
        ar6, _ = carbono.kg_co2e_por_unidad(diesel, self.pcg, "AR6")
        ar5, _ = carbono.kg_co2e_por_unidad(diesel, self.pcg, "AR5")
        self.assertAlmostEqual(ar6, 2.60 + 0.0001 * 29.8 + 0.0002 * 273, places=6)
        self.assertAlmostEqual(ar5, 2.60 + 0.0001 * 28 + 0.0002 * 265, places=6)
        self.assertGreater(ar6, ar5)

    def test_co2e_directo_no_usa_pcg(self):
        electricidad = [f for f in self.factores if f["id"] == "cl-elec-2024"][0]
        valor, avisos = carbono.kg_co2e_por_unidad(electricidad, {}, "AR6")
        self.assertEqual(valor, 0.30)
        self.assertEqual(avisos, [])


class PruebaBusqueda(BasePruebaCarbono):
    def test_elige_pais_y_anio(self):
        factor, avisos = carbono.buscar_factor(self.factores, "electricidad", "kWh", "CL", 2024)
        self.assertEqual(factor["id"], "cl-elec-2024")
        self.assertEqual(avisos, [])

    def test_usa_anio_anterior_disponible(self):
        factor, avisos = carbono.buscar_factor(self.factores, "electricidad", "kWh", "CL", 2026)
        self.assertEqual(factor["id"], "cl-elec-2024")
        self.assertTrue(any("2024" in a for a in avisos))

    def test_factor_internacional_cuando_no_hay_local(self):
        factor, avisos = carbono.buscar_factor(self.factores, "diesel", "L", "CL", 2024)
        self.assertEqual(factor["pais"], "*")
        self.assertTrue(any("internacional" in a for a in avisos))

    def test_unidad_incompatible(self):
        with self.assertRaises(Problema) as contexto:
            carbono.buscar_factor(self.factores, "diesel", "kg", "CL", 2024)
        self.assertIn("esta en L", contexto.exception.mensaje)

    def test_recurso_desconocido(self):
        with self.assertRaises(Problema) as contexto:
            carbono.buscar_factor(self.factores, "hidrogeno verde", "kg", "CL", 2024)
        self.assertIn("No tengo un factor", contexto.exception.mensaje)


class PruebaCalculo(BasePruebaCarbono):
    def test_registro_simple(self):
        fila = {"_fila": 2, "periodo": "2024-03", "sitio": "Planta", "recurso": "Electricidad",
                "cantidad": 1000, "unidad": "kWh", "calidad_dato": "reportado", "pais": "CL"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg)
        self.assertAlmostEqual(resultado["kg_co2e"], 300.0)
        self.assertEqual(resultado["alcance"], 2)
        self.assertEqual(resultado["periodo"], "2024-03")
        self.assertEqual(resultado["anio"], 2024)
        self.assertEqual(resultado["calidad_dato"], "reportado")

    def test_convierte_unidades(self):
        fila = {"_fila": 3, "periodo": "2024", "recurso": "electricidad", "cantidad": 2,
                "unidad": "MWh", "pais": "CL"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg)
        self.assertAlmostEqual(resultado["kg_co2e"], 600.0)
        self.assertTrue(any("Converti" in a for a in resultado["advertencias"]))

    def test_refrigerante_usa_su_pcg(self):
        fila = {"_fila": 4, "periodo": "2024", "recurso": "R-410A", "cantidad": 3, "unidad": "kg"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg)
        self.assertAlmostEqual(resultado["kg_co2e"], 6768.0)
        self.assertEqual(resultado["alcance"], 1)

    def test_falta_cantidad(self):
        with self.assertRaises(Problema) as contexto:
            carbono.calcular_registro({"_fila": 7, "recurso": "diesel", "unidad": "L"},
                                      self.factores, self.pcg)
        self.assertIn("fila 7", contexto.exception.mensaje)

    def test_cantidad_no_numerica(self):
        with self.assertRaises(Problema):
            carbono.calcular_registro({"_fila": 8, "recurso": "diesel", "cantidad": "mucho", "unidad": "L"},
                                      self.factores, self.pcg)

    def test_falta_unidad(self):
        with self.assertRaises(Problema) as contexto:
            carbono.calcular_registro({"_fila": 9, "recurso": "diesel", "cantidad": 10},
                                      self.factores, self.pcg)
        self.assertIn("Falta la unidad", contexto.exception.mensaje)

    def test_calidad_desconocida_se_trata_como_estimada(self):
        fila = {"_fila": 10, "periodo": "2024", "recurso": "electricidad", "cantidad": 100,
                "unidad": "kWh", "pais": "CL", "calidad_dato": "mas o menos"}
        resultado = carbono.calcular_registro(fila, self.factores, self.pcg)
        self.assertEqual(resultado["calidad_dato"], "estimado")
        self.assertTrue(any("calidad de dato" in a for a in resultado["advertencias"]))

    def test_resumen_completo(self):
        registros = [
            {"_fila": 2, "periodo": "2024-01", "sitio": "Planta", "recurso": "electricidad",
             "cantidad": 1000, "unidad": "kWh", "pais": "CL", "calidad_dato": "verificado"},
            {"_fila": 3, "periodo": "2024-01", "sitio": "Planta", "recurso": "diesel",
             "cantidad": 100, "unidad": "L", "pais": "CL", "calidad_dato": "reportado"},
            {"_fila": 4, "periodo": "2024-02", "sitio": "Oficina", "recurso": "electricidad",
             "cantidad": 500, "unidad": "kWh", "pais": "CL", "calidad_dato": "estimado"},
            {"_fila": 5, "periodo": "2024-02", "recurso": "hoteles", "cantidad": 400,
             "unidad": "USD", "categoria": "6", "calidad_dato": "estimado"},
            {"_fila": 6, "periodo": "2024-02", "recurso": "queso", "cantidad": 10, "unidad": "kg"},
        ]
        resumen = carbono.calcular(registros, self.factores, self.pcg, pais="CL")
        self.assertEqual(resumen["registros_calculados"], 4)
        self.assertEqual(resumen["registros_con_problema"], 1)
        self.assertEqual(resumen["problemas"][0]["fila"], 6)
        self.assertAlmostEqual(resumen["por_alcance"]["alcance_2"]["kg_co2e"], 450.0)
        self.assertAlmostEqual(resumen["por_alcance"]["alcance_3"]["kg_co2e"], 100.0)
        self.assertAlmostEqual(resumen["por_sitio"]["Planta"]["kg_co2e"],
                               300.0 + 100 * (2.60 + 0.0001 * 29.8 + 0.0002 * 273), places=4)
        self.assertEqual(resumen["por_periodo"]["2024-01"]["registros"], 2)
        self.assertEqual(resumen["por_categoria_alcance3"]["6"]["registros"], 1)
        self.assertAlmostEqual(resumen["total_t_co2e"], resumen["total_kg_co2e"] / 1000.0)
        self.assertGreater(resumen["calidad_datos"]["porcentaje"]["verificado"], 0)
        self.assertTrue(any("Ministerio de Energia" in f for f in resumen["fuentes"]))
        self.assertTrue(resumen["advertencias"])

    def test_sin_registros(self):
        resumen = carbono.calcular([], self.factores, self.pcg)
        self.assertEqual(resumen["total_kg_co2e"], 0.0)
        self.assertEqual(resumen["registros_calculados"], 0)


if __name__ == "__main__":
    unittest.main()
