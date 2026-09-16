# -*- coding: utf-8 -*-
"""Pruebas del modulo de reportes de sostenibilidad (marcos, cobertura, borrador e indice)."""

import json
import os
import unittest
import zipfile

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import reportes  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaCatalogoDeMarcos(unittest.TestCase):
    """El catalogo marcos_reporte.csv y las funciones de calculos/reportes.py."""

    def test_csv_se_carga_con_todas_sus_columnas(self):
        contenidos = reportes.cargar_contenidos()
        self.assertGreater(len(contenidos), 100)
        for contenido in contenidos:
            self.assertTrue(contenido["marco"])
            self.assertTrue(contenido["codigo"])
            self.assertTrue(contenido["titulo"], contenido["codigo"])
            self.assertTrue(contenido["descripcion"], contenido["codigo"])
            self.assertTrue(contenido["fuente"], contenido["codigo"])
            self.assertTrue(contenido["url"].startswith("http"), contenido["codigo"])
            self.assertTrue(contenido["verificado_el"], contenido["codigo"])
            self.assertIn(contenido["dimension"], reportes.DIMENSIONES)
            self.assertIn(contenido["obligatorio"], reportes.OBLIGATORIEDAD)

    def test_marcos_disponibles_trae_los_principales(self):
        disponibles = reportes.marcos_disponibles()
        nombres = [m["marco"] for m in disponibles]
        for esperado in ("GRI", "NIIF S1", "NIIF S2", "NCG 461", "NCG 519", "ESRS", "VSME"):
            self.assertIn(esperado, nombres)
        for marco in disponibles:
            self.assertTrue(marco["para_quien"], marco["marco"])
            self.assertTrue(marco["cuando_usarlo"], marco["marco"])
            self.assertGreater(marco["contenidos"], 0)
            self.assertEqual(marco["contenidos"],
                             marco["salen_de_tus_datos"] + marco["los_redacta_la_empresa"])

    def test_los_codigos_no_se_repiten_dentro_de_un_marco(self):
        vistos = set()
        for contenido in reportes.cargar_contenidos():
            clave = (contenido["marco"], contenido["codigo"])
            self.assertNotIn(clave, vistos)
            vistos.add(clave)

    def test_cada_dato_fuente_es_un_dato_que_el_motor_reconoce(self):
        for contenido in reportes.cargar_contenidos():
            for dato in contenido["dato_fuente"]:
                dato = reportes.dato_sin_marca(dato)
                self.assertIn(dato, reportes.DATOS_CONOCIDOS,
                              "%s usa un dato desconocido: %s" % (contenido["codigo"], dato))

    def test_contenidos_de_acepta_el_nombre_escrito_de_cualquier_forma(self):
        uno = reportes.contenidos_de("NIIF S2")
        self.assertEqual([c["codigo"] for c in uno], [c["codigo"] for c in reportes.contenidos_de("niif-s2")])
        self.assertEqual([c["codigo"] for c in uno], [c["codigo"] for c in reportes.contenidos_de("  niifs2 ")])
        codigos_gri = {c["codigo"] for c in reportes.contenidos_de("gri")}
        for esperado in ("2-1", "3-3", "302-1", "305-1", "306-3", "401-1", "403-9", "405-2", "418-1"):
            self.assertIn(esperado, codigos_gri)

    def test_marco_desconocido_explica_que_hacer(self):
        with self.assertRaises(Problema) as capturado:
            reportes.contenidos_de("Marco Inventado")
        self.assertIn("Marco Inventado", capturado.exception.mensaje)
        self.assertIn("GRI", capturado.exception.sugerencia)
        with self.assertRaises(Problema):
            reportes.evaluar_cobertura("Marco Inventado", ["empresa.json"])

    def test_cobertura_sin_datos_deja_todo_pendiente(self):
        resultado = reportes.evaluar_cobertura("NIIF S2", [])
        self.assertEqual(resultado["porcentaje_cobertura"], 0.0)
        self.assertEqual(len(resultado["pendientes"]), resultado["total"])
        self.assertEqual(resultado["cubiertos"], [])
        self.assertEqual(resultado["datos_usados"], [])
        self.assertTrue(all(f["estado"] == "pendiente" for f in resultado["contenidos"]))

    def test_cobertura_con_huella_marca_cubiertos_los_alcances(self):
        datos = ["huella.por_alcance.alcance_1", "huella.por_alcance.alcance_2",
                 "huella.por_alcance.alcance_3", "huella.por_categoria_alcance3"]
        resultado = reportes.evaluar_cobertura("NIIF S2", datos)
        estados = {f["codigo"]: f["estado"] for f in resultado["contenidos"]}
        self.assertEqual(estados["S2-alcance-1"], "cubierto")
        self.assertEqual(estados["S2-alcance-2"], "cubierto")
        self.assertEqual(estados["S2-alcance-3"], "cubierto")
        self.assertGreater(resultado["porcentaje_cobertura"], 0.0)
        self.assertIn("huella.por_alcance.alcance_1", resultado["datos_usados"])

    def test_un_dato_de_dos_deja_el_contenido_a_medias(self):
        resultado = reportes.evaluar_cobertura("NIIF S2", ["huella.total_t_co2e"])
        ficha = [f for f in resultado["contenidos"] if f["codigo"] == "S2-metricas-metas"][0]
        self.assertEqual(ficha["estado"], "parcial")
        self.assertEqual(ficha["encontrados"], ["huella.total_t_co2e"])
        self.assertEqual(ficha["faltan"], ["metas"])
        self.assertIn("Metas registradas", ficha["motivo"])

    def test_el_porcentaje_cuenta_lo_parcial_como_medio(self):
        fichas = [{"estado": "cubierto"}, {"estado": "parcial"}, {"estado": "pendiente"},
                  {"estado": "pendiente"}]
        self.assertEqual(reportes.porcentaje_cubierto(fichas), 37.5)
        self.assertEqual(reportes.porcentaje_cubierto([]), 0.0)

    def test_datos_que_mas_suman_van_primero(self):
        resultado = reportes.evaluar_cobertura("GRI", [])
        ganancias = resultado["datos_que_mas_suman"]
        self.assertTrue(ganancias)
        valores = [d["contenidos_que_desbloquea"] for d in ganancias]
        self.assertEqual(valores, sorted(valores, reverse=True))
        self.assertIn(ganancias[0]["dato"], reportes.DATOS_CONOCIDOS)

    def test_catalogo_faltante_avisa_en_lenguaje_simple(self):
        with self.assertRaises(Problema) as capturado:
            reportes.cargar_contenidos(os.path.join("no", "existe", "marcos_reporte.csv"))
        self.assertIn("marcos_reporte.csv", capturado.exception.mensaje)
        self.assertTrue(capturado.exception.sugerencia)


class PruebaModuloReporte(PruebaConCarpeta):
    """Prueba el modulo tal como lo llamara el agente."""

    def setUp(self):
        super(PruebaModuloReporte, self).setUp()
        from modulos import reporte
        self.reporte = reporte
        espacio.crear_empresa({"nombre": "Alimentos del Sur SpA", "pais": "CL", "sector": "Alimentos",
                               "tamano": "pequena", "anio_base": 2025, "periodo_actual": "2025",
                               "marcos": ["GRI"]}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Alimentos del Sur SpA"}
        self.ruta_empresa = espacio.resolver_ruta("Alimentos del Sur SpA", raiz=self.carpeta)

    def _huella(self, periodo="2025"):
        destino = espacio.ruta_de(self.ruta_empresa, "resultados", "huella_%s.json" % periodo)
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump({
                "total_t_co2e": 412.5, "periodo": periodo, "set_pcg": "AR5",
                "por_alcance": {"alcance_1": {"kg_co2e": 120000.0}, "alcance_2": {"kg_co2e": 92500.0},
                                "alcance_3": {"kg_co2e": 200000.0}},
                "por_categoria_alcance3": {"1": {"kg_co2e": 100000.0}, "6": {"kg_co2e": 100000.0}},
                "por_sitio": {"Planta Chillan": {"kg_co2e": 300000.0}},
                "por_periodo": {"2024": {"kg_co2e": 1.0}, "2025": {"kg_co2e": 2.0}},
                "calidad_datos": {"porcentaje": {"verificado": 0, "reportado": 70, "estimado": 30}},
            }, archivo)
        return destino

    def _personas(self):
        from nucleo import excel
        from plantillas import definiciones
        destino = espacio.ruta_de(self.ruta_empresa, "datos", "personas.xlsx")
        # Las cifras del ejemplo, pero de otro sitio: asi son datos de la empresa y no filas de ejemplo.
        definicion = dict(definiciones.PLANTILLAS["personas"])
        definicion["ejemplo"] = [[fila[0], "Planta Talca"] + list(fila[2:]) for fila in definicion["ejemplo"]]
        excel.escribir_xlsx(destino, definiciones.hojas_de(definicion))
        return destino

    def _diagnostico(self):
        destino = espacio.ruta_de(self.ruta_empresa, "seguimiento", "diagnostico.json")
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump({"ultima_evaluacion": {
                "puntaje_general": 42.0,
                "puntajes": {"ambiental": 50.0, "social": 30.0, "gobernanza": 46.0},
                "brechas": [{"id": "amb-metas"}, {"id": "gob-etica"}]}}, archivo)
        return destino

    def _texto_docx(self, ruta):
        with zipfile.ZipFile(ruta) as documento:
            return documento.read("word/document.xml").decode("utf-8")

    def test_marcos_funciona_sin_empresa_registrada(self):
        resultado = self.reporte.marcos({})
        nombres = [m["marco"] for m in resultado["marcos"]]
        self.assertIn("GRI", nombres)
        self.assertIn("NIIF S2", nombres)
        self.assertIn("VSME", nombres)
        self.assertTrue(resultado["como_elegir"])
        self.assertIn("verificacion", resultado["recordatorio"])

    def test_marcos_con_detalle_explica_cada_contenido(self):
        resultado = self.reporte.marcos({"marco": "vsme"})
        self.assertEqual(resultado["marco"], "VSME")
        codigos = [c["codigo"] for c in resultado["contenidos"]]
        self.assertIn("B1", codigos)
        self.assertIn("B3", codigos)
        self.assertIn("C9", codigos)
        for contenido in resultado["contenidos"]:
            self.assertTrue(contenido["que_pide"])
            self.assertTrue(contenido["de_donde_sale"])

    def test_cobertura_de_empresa_sin_datos(self):
        salida = self.reporte.cobertura(dict(self.opciones, marco="NIIF S2"))
        resultado = salida.resultado
        self.assertEqual(resultado["porcentaje_cobertura"], 0.0)
        self.assertEqual(resultado["cubiertos"], 0)
        self.assertEqual(resultado["pendientes"], resultado["total_contenidos"])
        self.assertIsNone(resultado["huella_usada"])
        self.assertTrue(any("huella calcular" in aviso for aviso in salida.advertencias))
        self.assertTrue(any("no es un reporte final" in aviso for aviso in salida.advertencias))

    def test_cobertura_sube_cuando_hay_datos_cargados(self):
        antes = self.reporte.cobertura(dict(self.opciones, marco="GRI")).resultado
        self._huella()
        self._personas()
        self._diagnostico()
        despues = self.reporte.cobertura(dict(self.opciones, marco="GRI")).resultado
        self.assertGreater(despues["porcentaje_cobertura"], antes["porcentaje_cobertura"])
        self.assertEqual(despues["huella_usada"], "huella_2025.json")
        codigos = [c["codigo"] for c in despues["ya_puedes_reportar"]]
        self.assertIn("305-1", codigos)
        self.assertTrue(any("personas" in dato.lower() for dato in despues["datos_encontrados"]))

    def test_cobertura_usa_el_marco_del_perfil_si_no_le_dicen_cual(self):
        resultado = self.reporte.cobertura(dict(self.opciones)).resultado
        self.assertEqual(resultado["marco"], "GRI")

    def test_borrador_genera_word_con_las_partes_por_escribir(self):
        self._huella()
        self._personas()
        salida = self.reporte.borrador(dict(self.opciones, marco="NIIF S2", periodo="2025"))
        archivo = salida.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        self.assertTrue(archivo.endswith("borrador-niif-s2-2025.docx"))
        texto = self._texto_docx(archivo)
        self.assertIn("Alimentos del Sur SpA", texto)
        self.assertIn("[Escribe aqui", texto)
        self.assertIn("Emisiones brutas de Alcance 1", texto)
        self.assertIn("greenwashing", texto)
        self.assertGreater(salida.resultado["con_dato_listo"], 0)
        self.assertEqual(salida.resultado["secciones_incluidas"],
                         salida.resultado["con_dato_listo"] + salida.resultado["a_medias"]
                         + salida.resultado["por_completar"])

    def test_borrador_de_empresa_sin_datos_queda_todo_por_completar(self):
        salida = self.reporte.borrador(dict(self.opciones, marco="VSME"))
        resultado = salida.resultado
        self.assertTrue(os.path.isfile(resultado["archivo"]))
        self.assertEqual(resultado["con_dato_listo"], 0)
        self.assertEqual(resultado["por_completar"] + resultado["a_medias"],
                         resultado["secciones_incluidas"])
        self.assertLess(resultado["porcentaje_cobertura"], 10.0)
        texto = self._texto_docx(resultado["archivo"])
        self.assertIn("Que falta para cerrar este borrador", texto)

    def test_borrador_se_puede_acotar_a_unos_temas(self):
        salida = self.reporte.borrador(dict(self.opciones, marco="GRI", temas="305"))
        self.assertEqual(salida.resultado["secciones_incluidas"], 7)
        solo_obligatorios = self.reporte.borrador(dict(self.opciones, marco="GRI", solo_obligatorios=True))
        self.assertEqual(solo_obligatorios.resultado["secciones_incluidas"], 12)
        with self.assertRaises(Problema):
            self.reporte.borrador(dict(self.opciones, marco="GRI", temas="999"))

    def test_indice_html_dice_que_esta_cubierto_y_que_no(self):
        self._huella()
        salida = self.reporte.indice(dict(self.opciones, marco="GRI", temas="305"))
        archivo = salida.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as documento:
            html = documento.read()
        self.assertIn("Indice de contenidos GRI", html)
        self.assertIn("305-1", html)
        self.assertIn("Cubierto", html)
        self.assertIn("Pendiente", html)
        self.assertEqual(salida.resultado["cubiertos"] + salida.resultado["parciales"]
                         + salida.resultado["pendientes"], salida.resultado["contenidos"])
        self.assertTrue(any("no es un reporte final" in aviso for aviso in salida.advertencias))

    def test_marco_desconocido_en_cualquier_accion(self):
        for accion in (self.reporte.cobertura, self.reporte.borrador, self.reporte.indice):
            with self.assertRaises(Problema) as capturado:
                accion(dict(self.opciones, marco="Marco Inventado"))
            self.assertIn("Marco Inventado", capturado.exception.mensaje)
            self.assertIn("GRI", capturado.exception.sugerencia)

    def test_sin_marco_ni_perfil_pide_elegir_uno(self):
        espacio.crear_empresa({"nombre": "Sin Marcos SpA", "pais": "PE"}, raiz=self.carpeta)
        opciones = {"raiz": self.carpeta, "empresa": "Sin Marcos SpA"}
        with self.assertRaises(Problema) as capturado:
            self.reporte.cobertura(opciones)
        self.assertIn("marco", capturado.exception.mensaje.lower())
        self.assertIn("GRI", capturado.exception.sugerencia)

    def test_resultado_dañado_no_rompe_el_reporte(self):
        destino = espacio.ruta_de(self.ruta_empresa, "resultados", "huella_2025.json")
        with open(destino, "w", encoding="utf-8") as archivo:
            archivo.write("{esto no es json")
        salida = self.reporte.cobertura(dict(self.opciones, marco="NIIF S2"))
        self.assertEqual(salida.resultado["porcentaje_cobertura"], 0.0)
        self.assertTrue(any("huella_2025.json" in aviso for aviso in salida.advertencias))


if __name__ == "__main__":
    unittest.main()
