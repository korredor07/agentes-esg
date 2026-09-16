# -*- coding: utf-8 -*-
"""Pruebas del escritor de documentos Word."""

import unittest
import zipfile

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from nucleo import word  # noqa: E402


class PruebaDocx(PruebaConCarpeta):
    def _documento(self, bloques, titulo="Documento"):
        ruta = word.escribir_docx(self.ruta("reporte.docx"), bloques, titulo)
        with zipfile.ZipFile(ruta) as archivo:
            self.nombres = archivo.namelist()
            return archivo.read("word/document.xml").decode("utf-8")

    def test_estructura_del_archivo(self):
        xml = self._documento([{"tipo": "titulo", "texto": "Reporte de sostenibilidad", "nivel": 0}])
        for pieza in ("[Content_Types].xml", "_rels/.rels", "word/document.xml",
                      "word/styles.xml", "word/_rels/document.xml.rels", "docProps/core.xml"):
            self.assertIn(pieza, self.nombres)
        self.assertIn('<w:pStyle w:val="Title"/>', xml)
        self.assertIn("Reporte de sostenibilidad", xml)

    def test_niveles_de_titulo(self):
        xml = self._documento([
            {"tipo": "titulo", "texto": "Uno", "nivel": 1},
            {"tipo": "titulo", "texto": "Dos", "nivel": 2},
            {"tipo": "titulo", "texto": "Tres", "nivel": 3},
        ])
        self.assertIn('<w:pStyle w:val="Heading1"/>', xml)
        self.assertIn('<w:pStyle w:val="Heading2"/>', xml)
        self.assertIn('<w:pStyle w:val="Heading3"/>', xml)

    def test_escapa_caracteres(self):
        xml = self._documento([{"tipo": "texto", "texto": "Riesgo alto & <critico>"}])
        self.assertIn("Riesgo alto &amp; &lt;critico&gt;", xml)
        self.assertNotIn("<critico>", xml)

    def test_saltos_de_linea_y_negrita(self):
        xml = self._documento([{"tipo": "texto", "texto": "Linea 1\nLinea 2", "negrita": True}])
        self.assertIn("<w:br/>", xml)
        self.assertIn("<w:b/>", xml)

    def test_lista_y_tabla(self):
        xml = self._documento([
            {"tipo": "lista", "items": ["Primero", "Segundo"]},
            {"tipo": "lista", "items": ["Paso uno"], "ordenada": True},
            {"tipo": "tabla", "columnas": ["Alcance", "tCO2e"], "filas": [["Alcance 1", "120,4"]]},
        ])
        self.assertIn("• Primero", xml)
        self.assertIn("1. Paso uno", xml)
        self.assertIn("<w:tbl>", xml)
        self.assertIn('<w:shd w:val="clear" w:fill="D8F3DC"/>', xml)
        self.assertIn("120,4", xml)

    def test_salto_de_pagina_y_nota(self):
        xml = self._documento([{"tipo": "salto_pagina"}, {"tipo": "nota", "texto": "Aviso legal"}])
        self.assertIn('<w:br w:type="page"/>', xml)
        self.assertIn('<w:pStyle w:val="Nota"/>', xml)

    def test_celdas_faltantes_se_rellenan(self):
        xml = self._documento([{"tipo": "tabla", "columnas": ["a", "b", "c"], "filas": [["1"]]}])
        self.assertEqual(xml.count("<w:tc>"), 6)


class PruebaMarkdown(unittest.TestCase):
    def test_convierte_markdown_sencillo(self):
        bloques = word.desde_markdown(
            "# Titulo\n\nUn parrafo largo\nque sigue.\n\n## Seccion\n\n- uno\n- dos\n\n"
            "| Alcance | tCO2e |\n|---|---|\n| 1 | 120 |\n| 2 | 80 |\n")
        tipos = [b["tipo"] for b in bloques]
        self.assertEqual(tipos, ["titulo", "texto", "titulo", "lista", "tabla"])
        self.assertEqual(bloques[0]["nivel"], 1)
        self.assertEqual(bloques[2]["nivel"], 2)
        self.assertEqual(bloques[1]["texto"], "Un parrafo largo que sigue.")
        self.assertEqual(bloques[3]["items"], ["uno", "dos"])
        self.assertEqual(bloques[4]["columnas"], ["Alcance", "tCO2e"])
        self.assertEqual(bloques[4]["filas"], [["1", "120"], ["2", "80"]])

    def test_texto_vacio(self):
        self.assertEqual(word.desde_markdown(""), [])


if __name__ == "__main__":
    unittest.main()
