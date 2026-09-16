# -*- coding: utf-8 -*-
"""Pruebas del lector y escritor de Excel."""

import datetime
import unittest
import zipfile

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from nucleo import excel  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaReferencias(unittest.TestCase):
    def test_columna_a_indice(self):
        self.assertEqual(excel.columna_a_indice("A1"), 0)
        self.assertEqual(excel.columna_a_indice("B7"), 1)
        self.assertEqual(excel.columna_a_indice("Z10"), 25)
        self.assertEqual(excel.columna_a_indice("AA3"), 26)
        self.assertEqual(excel.columna_a_indice("AB3"), 27)

    def test_indice_a_columna(self):
        self.assertEqual(excel.indice_a_columna(0), "A")
        self.assertEqual(excel.indice_a_columna(25), "Z")
        self.assertEqual(excel.indice_a_columna(26), "AA")
        for indice in (0, 5, 26, 27, 51, 52, 700):
            self.assertEqual(excel.columna_a_indice(excel.indice_a_columna(indice) + "1"), indice)

    def test_normalizar_encabezado(self):
        self.assertEqual(excel.normalizar_encabezado("Cantidad (kWh) "), "cantidad_kwh")
        self.assertEqual(excel.normalizar_encabezado("Año base"), "ano_base")
        self.assertEqual(excel.normalizar_encabezado("Razón Social"), "razon_social")
        self.assertEqual(excel.normalizar_encabezado(None), "")


class PruebaEscrituraLectura(PruebaConCarpeta):
    def test_ida_y_vuelta(self):
        ruta = self.ruta("datos.xlsx")
        excel.escribir_xlsx(ruta, [{
            "nombre": "Consumos",
            "columnas": [{"titulo": "Sitio", "ancho": 20}, {"titulo": "Cantidad (kWh)"},
                         {"titulo": "Es estimado"}, {"titulo": "Fecha"}, {"titulo": "Comentario"}],
            "filas": [
                ["Planta Sur", 1234, True, datetime.date(2026, 1, 31), "Boleta N° 5 & 6"],
                ["Oficina <Central>", 98.5, False, "2026-02-28", None],
            ],
        }])
        tabla = excel.leer_tabla(ruta)
        self.assertEqual(tabla["hoja"], "Consumos")
        self.assertEqual(tabla["encabezados"], ["sitio", "cantidad_kwh", "es_estimado", "fecha", "comentario"])
        primera = tabla["filas"][0]
        self.assertEqual(primera["sitio"], "Planta Sur")
        self.assertEqual(primera["cantidad_kwh"], 1234)
        self.assertIs(primera["es_estimado"], True)
        self.assertEqual(primera["fecha"], "2026-01-31")
        self.assertEqual(primera["comentario"], "Boleta N° 5 & 6")
        self.assertEqual(primera["_fila"], 2)
        segunda = tabla["filas"][1]
        self.assertEqual(segunda["sitio"], "Oficina <Central>")
        self.assertAlmostEqual(segunda["cantidad_kwh"], 98.5)
        self.assertIs(segunda["es_estimado"], False)
        self.assertIsNone(segunda["comentario"])
        self.assertEqual(segunda["_fila"], 3)

    def test_varias_hojas_y_orden(self):
        ruta = self.ruta("libro.xlsx")
        excel.escribir_xlsx(ruta, [
            {"nombre": "Instrucciones", "columnas": [{"titulo": "Cómo llenar"}], "filas": [["Escribe una fila por mes"]]},
            {"nombre": "Datos", "columnas": [{"titulo": "Mes"}, {"titulo": "Valor"}], "filas": [["enero", 10]]},
        ])
        libro = excel.leer_xlsx(ruta)
        self.assertEqual(list(libro.keys()), ["Instrucciones", "Datos"])
        # leer_tabla ignora la hoja de instrucciones
        tabla = excel.leer_tabla(ruta)
        self.assertEqual(tabla["hoja"], "Datos")
        self.assertEqual(tabla["filas"][0]["mes"], "enero")

    def test_hoja_pedida_por_nombre_sin_acentos(self):
        ruta = self.ruta("libro.xlsx")
        excel.escribir_xlsx(ruta, [{"nombre": "Año base", "columnas": [{"titulo": "Dato"}], "filas": [["x"]]}])
        tabla = excel.leer_tabla(ruta, hoja="ano base")
        self.assertEqual(tabla["hoja"], "Año base")

    def test_hoja_inexistente_explica_las_disponibles(self):
        ruta = self.ruta("libro.xlsx")
        excel.escribir_xlsx(ruta, [{"nombre": "Datos", "columnas": [{"titulo": "Dato"}], "filas": [["x"]]}])
        with self.assertRaises(Problema) as contexto:
            excel.leer_tabla(ruta, hoja="Emisiones")
        self.assertIn("Datos", contexto.exception.sugerencia)

    def test_filas_vacias_se_saltan(self):
        ruta = self.ruta("libro.xlsx")
        excel.escribir_xlsx(ruta, [{
            "nombre": "Datos",
            "columnas": [{"titulo": "Mes"}, {"titulo": "Valor"}],
            "filas": [["enero", 1], [None, None], ["", ""], ["marzo", 3]],
        }])
        tabla = excel.leer_tabla(ruta)
        self.assertEqual([f["mes"] for f in tabla["filas"]], ["enero", "marzo"])
        self.assertEqual(tabla["filas"][1]["_fila"], 5)

    def test_hoja_vacia_avisa(self):
        ruta = self.ruta("vacio.xlsx")
        excel.escribir_xlsx(ruta, [{"nombre": "Datos", "filas": []}])
        with self.assertRaises(Problema) as contexto:
            excel.leer_tabla(ruta)
        self.assertIn("vacia", contexto.exception.mensaje.lower())

    def test_archivo_inexistente(self):
        with self.assertRaises(Problema) as contexto:
            excel.leer_xlsx(self.ruta("no-existe.xlsx"))
        self.assertIn("No encontre", contexto.exception.mensaje)

    def test_archivo_corrupto(self):
        ruta = self.ruta("falso.xlsx")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("esto no es un excel")
        with self.assertRaises(Problema) as contexto:
            excel.leer_xlsx(ruta)
        self.assertIn("no es un Excel", contexto.exception.mensaje)


class PruebaCompatibilidadExcelReal(PruebaConCarpeta):
    """Archivos como los que genera Excel: cadenas compartidas y fechas con estilo."""

    def _crear_libro(self, hoja_xml, estilos_xml, shared=None):
        ruta = self.ruta("real.xlsx")
        with zipfile.ZipFile(ruta, "w") as zip_archivo:
            zip_archivo.writestr("[Content_Types].xml",
                                 '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                                 '<Default Extension="xml" ContentType="application/xml"/></Types>')
            zip_archivo.writestr("xl/workbook.xml",
                                 '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                                 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                                 '<sheets><sheet name="Hoja1" sheetId="1" r:id="rId1"/></sheets></workbook>')
            zip_archivo.writestr("xl/_rels/workbook.xml.rels",
                                 '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                                 'Target="worksheets/sheet1.xml"/></Relationships>')
            zip_archivo.writestr("xl/worksheets/sheet1.xml", hoja_xml)
            zip_archivo.writestr("xl/styles.xml", estilos_xml)
            if shared is not None:
                zip_archivo.writestr("xl/sharedStrings.xml", shared)
        return ruta

    def test_cadenas_compartidas_y_fecha_con_estilo(self):
        estilos = ('<?xml version="1.0"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<cellXfs count="2"><xf numFmtId="0"/><xf numFmtId="14"/></cellXfs></styleSheet>')
        shared = ('<?xml version="1.0"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="2" uniqueCount="2">'
                  '<si><t>Sitio</t></si><si><r><t>Planta </t></r><r><t>Norte</t></r></si></sst>')
        hoja = ('<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="inlineStr"><is><t>Fecha</t></is></c></row>'
                '<row r="2"><c r="A2" t="s"><v>1</v></c><c r="B2" s="1"><v>46053</v></c></row>'
                '</sheetData></worksheet>')
        ruta = self._crear_libro(hoja, estilos, shared)
        tabla = excel.leer_tabla(ruta)
        self.assertEqual(tabla["encabezados"], ["sitio", "fecha"])
        self.assertEqual(tabla["filas"][0]["sitio"], "Planta Norte")
        self.assertEqual(tabla["filas"][0]["fecha"], "2026-01-31")

    def test_celdas_salteadas_mantienen_columna(self):
        estilos = ('<?xml version="1.0"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<cellXfs count="1"><xf numFmtId="0"/></cellXfs></styleSheet>')
        hoja = ('<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                '<row r="1"><c r="A1" t="inlineStr"><is><t>Sitio</t></is></c>'
                '<c r="B1" t="inlineStr"><is><t>Cantidad</t></is></c>'
                '<c r="C1" t="inlineStr"><is><t>Unidad</t></is></c></row>'
                '<row r="2"><c r="A2" t="inlineStr"><is><t>Planta</t></is></c>'
                '<c r="C2" t="inlineStr"><is><t>kWh</t></is></c></row>'
                '</sheetData></worksheet>')
        ruta = self._crear_libro(hoja, estilos)
        tabla = excel.leer_tabla(ruta)
        fila = tabla["filas"][0]
        self.assertEqual(fila["sitio"], "Planta")
        self.assertIsNone(fila["cantidad"])
        self.assertEqual(fila["unidad"], "kWh")

    def test_rechaza_xml_con_doctype(self):
        estilos = ('<?xml version="1.0"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<cellXfs count="1"><xf numFmtId="0"/></cellXfs></styleSheet>')
        hoja = ('<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                '<row r="1"><c r="A1" t="inlineStr"><is><t>Sitio</t></is></c></row></sheetData></worksheet>')
        ruta = self._crear_libro(hoja, estilos)
        with self.assertRaises(Problema) as contexto:
            excel.leer_xlsx(ruta)
        self.assertIn("seguridad", contexto.exception.mensaje)


if __name__ == "__main__":
    unittest.main()
