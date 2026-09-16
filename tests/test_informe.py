# -*- coding: utf-8 -*-
"""Pruebas del generador de informes HTML."""

import re
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from nucleo import informe  # noqa: E402


BLOQUES_DEMO = [
    {"tipo": "titulo", "texto": "Resumen del año", "nivel": 2},
    {"tipo": "texto", "texto": "Estas son las emisiones de la empresa."},
    {"tipo": "kpi", "items": [
        {"etiqueta": "Huella total", "valor": 1234.5, "unidad": "tCO2e", "detalle": "2025", "color": "verde"},
        {"etiqueta": "Intensidad", "valor": 0.42, "unidad": "tCO2e/MM$", "detalle": "por ingresos"},
    ]},
    {"tipo": "tabla", "columnas": ["Alcance", "tCO2e"], "filas": [["Alcance 1", 120.4], ["Alcance 2", 89.75]],
     "numericas": [1], "nota": "Metodologia GHG Protocol."},
    {"tipo": "barras", "titulo": "Emisiones por sitio", "unidad": "tCO2e",
     "datos": [{"etiqueta": "Planta Sur", "valor": 300}, {"etiqueta": "Oficina", "valor": 45.2}]},
    {"tipo": "lineas", "titulo": "Evolucion mensual", "unidad": "tCO2e",
     "series": [{"nombre": "2025", "puntos": [("ene", 10), ("feb", 12), ("mar", 9)]},
                {"nombre": "Meta", "puntos": [("ene", 9), ("feb", 9), ("mar", 9)], "punteada": True}]},
    {"tipo": "dona", "titulo": "Reparto", "unidad": "tCO2e",
     "datos": [{"etiqueta": "Alcance 1", "valor": 120}, {"etiqueta": "Alcance 2", "valor": 80}]},
    {"tipo": "semaforo", "items": [
        {"etiqueta": "Ley REP", "estado": "rojo", "detalle": "Sin declaracion"},
        {"etiqueta": "Alcance 1", "estado": "verde", "detalle": "Completo"},
    ]},
    {"tipo": "lista", "items": ["Cargar datos de enero", "Revisar factores"]},
    {"tipo": "nota", "texto": "Esto es orientacion, no asesoria legal.", "estilo": "aviso"},
    {"tipo": "separador"},
]


class PruebaFormatoNumeros(unittest.TestCase):
    def test_formato_chileno(self):
        self.assertEqual(informe.formatear_numero(1234567.891), "1.234.567,9")
        self.assertEqual(informe.formatear_numero(300.0), "300")
        self.assertEqual(informe.formatear_numero(12.345), "12,3")
        self.assertEqual(informe.formatear_numero(0.1234), "0,123")
        self.assertEqual(informe.formatear_numero(None), "—")
        self.assertEqual(informe.formatear_numero(1500, 2), "1.500,00")


class PruebaRender(unittest.TestCase):
    def setUp(self):
        self.html = informe.render("Huella de carbono 2025", BLOQUES_DEMO,
                                   marca={"nombre": "Alimentos del Sur", "color_primario": "#123456"},
                                   subtitulo="Informe de prueba")

    def test_estructura_basica(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="es">', self.html)
        self.assertIn("<title>Huella de carbono 2025</title>", self.html)
        self.assertIn("Alimentos del Sur", self.html)
        self.assertIn("#123456", self.html)

    def test_no_depende_de_internet(self):
        self.assertNotIn("<script", self.html)
        self.assertNotIn("<link", self.html)
        self.assertNotIn("<img", self.html)
        # la unica URL admitida es el espacio de nombres de SVG, que no descarga nada
        urls = re.findall(r"https?://[^\"' )]+", self.html)
        self.assertEqual(set(urls), {"http://www.w3.org/2000/svg"})

    def test_escapa_contenido_peligroso(self):
        html = informe.render("Reporte", [{"tipo": "texto", "texto": "<script>alert('x')</script>"}])
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)

    def test_kpi_y_tabla(self):
        self.assertIn("Huella total", self.html)
        self.assertIn("1.234,5", self.html)          # formato chileno
        self.assertIn("Metodologia GHG Protocol.", self.html)
        self.assertIn('<td class="num">120,4</td>', self.html)

    def test_graficos_svg_con_datos(self):
        self.assertEqual(self.html.count("<svg"), 3)
        self.assertIn("Planta Sur", self.html)
        self.assertIn("Evolucion mensual", self.html)
        self.assertIn("stroke-dasharray=\"6 4\"", self.html)  # serie punteada de la meta
        self.assertIn("(60,0%)", self.html)                    # reparto de la dona

    def test_semaforo_y_avisos(self):
        self.assertIn("Sin declaracion", self.html)
        self.assertIn("Critico", self.html)
        self.assertIn("no asesoria legal", self.html)

    def test_bloques_vacios_no_rompen(self):
        html = informe.render("Vacio", [
            {"tipo": "barras", "titulo": "Sin datos", "datos": []},
            {"tipo": "dona", "datos": []},
            {"tipo": "lineas", "series": []},
            {"tipo": "tabla", "columnas": ["a"], "filas": []},
        ])
        self.assertEqual(html.count("Sin datos para graficar."), 3)
        self.assertIn("Sin datos todavia.", html)


class PruebaEscritura(PruebaConCarpeta):
    def test_escribe_archivo(self):
        ruta = informe.escribir_html(self.ruta("sub", "informe.html"), "Informe", BLOQUES_DEMO)
        with open(ruta, encoding="utf-8") as archivo:
            contenido = archivo.read()
        self.assertIn("Informe", contenido)
        self.assertGreater(len(contenido), 2000)


if __name__ == "__main__":
    unittest.main()
