# -*- coding: utf-8 -*-
"""Pruebas de los indicadores sociales."""

import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import social  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

FILAS = [
    {"_fila": 2, "periodo": "2025", "sitio": "Planta", "categoria": "operario", "genero": "mujer",
     "tipo_de_contrato": "indefinido", "jornada": "completa", "numero_de_personas": 40,
     "contrataciones": 5, "desvinculaciones": 4, "remuneracion_promedio": 800000,
     "horas_de_capacitacion": 120, "accidentes_con_tiempo_perdido": 1, "dias_perdidos": 10,
     "horas_trabajadas": 72000, "personas_con_discapacidad": 1},
    {"_fila": 3, "periodo": "2025", "sitio": "Planta", "categoria": "operario", "genero": "hombre",
     "tipo_de_contrato": "indefinido", "jornada": "completa", "numero_de_personas": 60,
     "contrataciones": 5, "desvinculaciones": 6, "remuneracion_promedio": 1000000,
     "horas_de_capacitacion": 180, "accidentes_con_tiempo_perdido": 2, "dias_perdidos": 20,
     "horas_trabajadas": 108000, "personas_con_discapacidad": 0},
    {"_fila": 4, "periodo": "2025", "sitio": "Oficina", "categoria": "direccion", "genero": "mujer",
     "tipo_de_contrato": "indefinido", "jornada": "completa", "numero_de_personas": 1,
     "remuneracion_promedio": 4000000, "horas_de_capacitacion": 10, "horas_trabajadas": 1800},
    {"_fila": 5, "periodo": "2024", "sitio": "Planta", "categoria": "operario", "genero": "mujer",
     "numero_de_personas": 30},
]


class PruebaIndicadores(unittest.TestCase):
    def setUp(self):
        self.indicadores = social.calcular(FILAS, "2025")

    def test_dotacion_y_composicion(self):
        self.assertEqual(self.indicadores["dotacion_total"], 101)
        self.assertEqual(self.indicadores["por_genero"]["mujer"], 41)
        self.assertEqual(self.indicadores["por_categoria"]["operario"], 100)
        self.assertEqual(self.indicadores["por_sitio"]["Planta"], 100)

    def test_filtra_por_periodo(self):
        completo = social.calcular(FILAS)
        self.assertEqual(completo["dotacion_total"], 131)

    def test_rotacion_y_contratacion(self):
        self.assertAlmostEqual(self.indicadores["tasa_rotacion_pct"], round(10 / 101.0 * 100, 1), places=1)
        self.assertAlmostEqual(self.indicadores["tasa_contratacion_pct"], round(10 / 101.0 * 100, 1), places=1)

    def test_brecha_salarial_por_categoria(self):
        brecha = self.indicadores["brecha_salarial_por_categoria"]["operario"]
        self.assertAlmostEqual(brecha["brecha_pct"], 20.0, places=1)
        self.assertAlmostEqual(brecha["razon_mujer_hombre"], 0.8, places=3)

    def test_no_calcula_brecha_sin_ambos_generos(self):
        self.assertNotIn("direccion", self.indicadores["brecha_salarial_por_categoria"])

    def test_accidentabilidad_y_tasa_registrable(self):
        self.assertAlmostEqual(self.indicadores["tasa_accidentabilidad_pct"], round(3 / 101.0 * 100, 2), places=2)
        self.assertAlmostEqual(self.indicadores["tasa_accidentes_registrables"],
                               round(3 * 200000.0 / 181800.0, 2), places=2)
        self.assertEqual(self.indicadores["dias_perdidos"], 30)

    def test_capacitacion(self):
        self.assertEqual(self.indicadores["horas_capacitacion"], 310.0)
        self.assertAlmostEqual(self.indicadores["horas_capacitacion_por_persona"],
                               round(310 / 101.0, 1), places=1)

    def test_mujeres_en_direccion(self):
        self.assertEqual(self.indicadores["mujeres_en_direccion_pct"], 100.0)

    def test_advertencias_cuando_faltan_datos(self):
        sin_horas = [dict(f, horas_trabajadas=None) for f in FILAS if f["periodo"] == "2025"]
        indicadores = social.calcular(sin_horas, "2025")
        self.assertNotIn("tasa_accidentes_registrables", indicadores)
        self.assertTrue(any("200.000 horas" in a for a in indicadores["advertencias"]))

    def test_fila_sin_personas_se_avisa(self):
        filas = [dict(FILAS[0], numero_de_personas=0)] + [FILAS[1]]
        indicadores = social.calcular(filas, "2025")
        self.assertTrue(any("no indica cuantas personas" in a for a in indicadores["advertencias"]))
        self.assertEqual(indicadores["dotacion_total"], 60)

    def test_sin_datos(self):
        with self.assertRaises(Problema):
            social.calcular([])
        with self.assertRaises(Problema):
            social.calcular(FILAS, "2019")

    def test_inclusion_chile(self):
        resultado = social.revisar_inclusion(self.indicadores, "CL")
        self.assertTrue(resultado["aplica"])
        self.assertFalse(resultado["cumple"])
        self.assertEqual(resultado["faltan"], 1)
        chica = social.revisar_inclusion({"dotacion_total": 40, "personas_con_discapacidad": 0}, "CL")
        self.assertFalse(chica["aplica"])
        peru = social.revisar_inclusion(self.indicadores, "PE")
        self.assertFalse(peru["aplica"])

    def test_nota_metodologica(self):
        self.assertIn("gestion interna", self.indicadores["nota_metodologica"])


class PruebaModuloSocial(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloSocial, self).setUp()
        from modulos import social as modulo
        from nucleo import espacio
        self.modulo = modulo
        self.espacio = espacio
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "anio_base": 2025,
                               "sector": "Industria", "tamano": "mediana"}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def test_sin_planilla_avisa(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.calcular(self.opciones)
        self.assertIn("planilla de personas", contexto.exception.mensaje)

    def test_calcula_e_informa(self):
        import os
        from nucleo import excel
        from plantillas import definiciones
        _, ruta = self.espacio.cargar_empresa("Prueba SpA", raiz=self.carpeta)
        hojas = definiciones.hojas_de(definiciones.PLANTILLAS["personas"], con_ejemplo=False)
        hojas[1]["filas"] = [
            ["2025", "Planta", "operario", "mujer", "indefinido", "completa", 40, 5, 4, 800000, 120, 1, 10, 72000, 1],
            ["2025", "Planta", "operario", "hombre", "indefinido", "completa", 60, 5, 6, 1000000, 180, 2, 20, 108000, 0],
        ]
        excel.escribir_xlsx(os.path.join(ruta, "datos", "personas.xlsx"), hojas)
        resultado = self.modulo.calcular(dict(self.opciones, periodo="2025")).resultado
        self.assertEqual(resultado["dotacion_total"], 100)
        self.assertTrue(os.path.isfile(resultado["resultado_guardado_en"]))
        informe = self.modulo.informe_html(dict(self.opciones, periodo="2025"))
        self.assertTrue(os.path.isfile(informe["archivo"]))


if __name__ == "__main__":
    unittest.main()
