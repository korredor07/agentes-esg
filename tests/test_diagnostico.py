# -*- coding: utf-8 -*-
"""Pruebas del diagnostico ESG (puntaje, brechas y seguimiento)."""

import json
import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import puntaje  # noqa: E402
from nucleo import espacio  # noqa: E402


class PruebaPuntaje(PruebaConCarpeta):
    def _empresa(self, **extra):
        datos = {"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria",
                 "tamano": "pequena", "anio_base": 2025,
                 "sitios": [{"nombre": "Planta", "tipo": "planta"}]}
        datos.update(extra)
        perfil, ruta, _ = espacio.crear_empresa(datos, raiz=self.carpeta)
        return perfil, ruta

    def _huella(self, ruta, total_kg=1000.0, verificado=0.0, reportado=0.0, estimado=100.0, periodo="2025"):
        destino = espacio.ruta_de(ruta, "resultados", "huella_2025.json")
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump({
                "total_t_co2e": total_kg / 1000.0, "periodo": periodo,
                "por_alcance": {"alcance_1": {"kg_co2e": total_kg * 0.3}, "alcance_2": {"kg_co2e": total_kg * 0.2},
                                "alcance_3": {"kg_co2e": total_kg * 0.5}},
                "calidad_datos": {"porcentaje": {"verificado": verificado, "reportado": reportado,
                                                 "estimado": estimado}},
            }, archivo)

    def test_empresa_vacia_puntua_bajo(self):
        perfil, ruta = self._empresa()
        resultado = puntaje.evaluar(perfil, ruta)
        self.assertLess(resultado["puntaje_general"], 30)
        self.assertEqual(resultado["puntajes"]["social"], 0.0)
        self.assertTrue(resultado["brechas"])
        self.assertTrue(any(b["id"] == "amb-huella" for b in resultado["brechas"]))

    def test_huella_calculada_sube_ambiental(self):
        perfil, ruta = self._empresa()
        sin_huella = puntaje.evaluar(perfil, ruta)["puntajes"]["ambiental"]
        self._huella(ruta, reportado=80.0, estimado=20.0)
        con_huella = puntaje.evaluar(perfil, ruta)
        self.assertGreater(con_huella["puntajes"]["ambiental"], sin_huella)
        indicadores = {i["id"]: i for i in con_huella["indicadores"]}
        self.assertEqual(indicadores["amb-huella"]["estado"], "cumple")
        self.assertEqual(indicadores["amb-calidad"]["estado"], "cumple")
        self.assertEqual(indicadores["amb-alcance3"]["estado"], "cumple")

    def test_calidad_de_datos_parcial_y_mala(self):
        perfil, ruta = self._empresa()
        self._huella(ruta, reportado=50.0, estimado=50.0)
        indicadores = {i["id"]: i for i in puntaje.evaluar(perfil, ruta)["indicadores"]}
        self.assertEqual(indicadores["amb-calidad"]["estado"], "parcial")
        self._huella(ruta, reportado=10.0, estimado=90.0)
        indicadores = {i["id"]: i for i in puntaje.evaluar(perfil, ruta)["indicadores"]}
        self.assertEqual(indicadores["amb-calidad"]["estado"], "no_cumple")

    def test_huella_antigua_es_parcial(self):
        perfil, ruta = self._empresa()
        self._huella(ruta, periodo="2019")
        indicadores = {i["id"]: i for i in puntaje.evaluar(perfil, ruta)["indicadores"]}
        self.assertEqual(indicadores["amb-huella"]["estado"], "parcial")

    def test_indicadores_por_pais(self):
        perfil_cl, _ = self._empresa()
        ids_cl = {i["id"] for i in puntaje.indicadores_aplicables(perfil_cl)}
        self.assertIn("soc-karin", ids_cl)
        perfil_pe = dict(perfil_cl, pais="PE")
        ids_pe = {i["id"] for i in puntaje.indicadores_aplicables(perfil_pe)}
        self.assertNotIn("soc-karin", ids_pe)
        self.assertIn("gob-datos", ids_pe)

    def test_respuestas_manuales_cambian_el_puntaje(self):
        perfil, ruta = self._empresa()
        base = puntaje.evaluar(perfil, ruta)["puntajes"]["gobernanza"]
        respuestas = {"gob-etica": {"estado": "cumple"}, "gob-responsable": {"estado": "cumple"},
                      "gob-datos": {"estado": "parcial"}}
        mejor = puntaje.evaluar(perfil, ruta, respuestas)["puntajes"]["gobernanza"]
        self.assertGreater(mejor, base)

    def test_no_aplica_sale_del_calculo(self):
        perfil, ruta = self._empresa()
        todas_no_aplican = {i["id"]: {"estado": "no_aplica"}
                            for i in puntaje.indicadores_aplicables(perfil)
                            if i["dimension"] == "gobernanza" and not i.get("automatico")}
        resultado = puntaje.evaluar(perfil, ruta, todas_no_aplican)
        gobernanza = [i for i in resultado["indicadores"] if i["dimension"] == "gobernanza"]
        self.assertTrue(any(i["estado"] == "no_aplica" for i in gobernanza))
        self.assertIsNotNone(resultado["puntajes"]["gobernanza"])

    def test_brechas_ordenadas_por_prioridad(self):
        perfil, ruta = self._empresa()
        brechas = puntaje.evaluar(perfil, ruta)["brechas"]
        prioridades = [b["prioridad"] for b in brechas]
        self.assertEqual(prioridades, sorted(prioridades, reverse=True))
        self.assertTrue(all(b["prioridad"] >= 6 for b in
                            puntaje.evaluar(perfil, ruta)["brechas_criticas"]))

    def test_niveles(self):
        self.assertEqual(puntaje.nivel(90)[0], "avanzado")
        self.assertEqual(puntaje.nivel(65)[0], "en marcha")
        self.assertEqual(puntaje.nivel(45)[0], "inicial")
        self.assertEqual(puntaje.nivel(10)[0], "sin gestion")
        self.assertEqual(puntaje.nivel(None)[0], "sin evaluar")

    def test_evidencias_y_metas_detectadas(self):
        perfil, ruta = self._empresa()
        indicadores = {i["id"]: i for i in puntaje.evaluar(perfil, ruta)["indicadores"]}
        self.assertEqual(indicadores["gob-evidencias"]["estado"], "no_cumple")
        self.assertEqual(indicadores["amb-metas"]["estado"], "no_cumple")
        with open(espacio.ruta_de(ruta, "evidencias", "registro.jsonl"), "w", encoding="utf-8") as archivo:
            archivo.write('{"n": 1}\n')
        with open(espacio.ruta_de(ruta, "seguimiento", "metas.json"), "w", encoding="utf-8") as archivo:
            archivo.write("{}")
        indicadores = {i["id"]: i for i in puntaje.evaluar(perfil, ruta)["indicadores"]}
        self.assertEqual(indicadores["gob-evidencias"]["estado"], "cumple")
        self.assertEqual(indicadores["amb-metas"]["estado"], "cumple")


class PruebaModuloDiagnostico(PruebaConCarpeta):
    """Prueba el modulo tal como lo llamara el agente."""

    def setUp(self):
        super(PruebaModuloDiagnostico, self).setUp()
        from modulos import diagnostico
        self.diagnostico = diagnostico
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria",
                               "tamano": "pequena", "anio_base": 2025,
                               "sitios": [{"nombre": "Planta"}]}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def test_flujo_de_preguntas_y_respuestas(self):
        pendientes = self.diagnostico.preguntas(self.opciones)
        self.assertGreater(pendientes["total"], 5)
        primera = pendientes["preguntas"][0]
        self.assertIn("porque_importa", primera)

        self.diagnostico.responder(dict(self.opciones, indicador=primera["id"], estado="cumple",
                                        nota="Listo el año pasado"))
        despues = self.diagnostico.preguntas(self.opciones)
        self.assertEqual(despues["total"], pendientes["total"] - 1)

    def test_respuesta_invalida(self):
        from nucleo.salida import Problema
        with self.assertRaises(Problema):
            self.diagnostico.responder(dict(self.opciones, indicador="soc-karin", estado="mas o menos"))
        with self.assertRaises(Problema):
            self.diagnostico.responder(dict(self.opciones, indicador="no-existe", estado="cumple"))

    def test_seguimiento_de_brecha(self):
        from nucleo.salida import Problema
        self.diagnostico.brecha(dict(self.opciones, indicador="soc-karin", seguimiento="reconocida",
                                     responsable="Jefa de personas", fecha_compromiso="2026-12-01"))
        evaluacion = self.diagnostico.evaluar(self.opciones).resultado
        self.assertGreaterEqual(evaluacion["total_brechas"], 1)
        with self.assertRaises(Problema):
            self.diagnostico.brecha(dict(self.opciones, indicador="soc-karin", seguimiento="inventada"))

    def test_informe_y_tablero(self):
        from modulos import tablero
        informe = self.diagnostico.informe_html(self.opciones).resultado
        self.assertTrue(os.path.isfile(informe["archivo"]))
        salida = tablero.generar(self.opciones).resultado
        self.assertTrue(os.path.isfile(salida["archivo"]))
        with open(salida["archivo"], encoding="utf-8") as archivo:
            contenido = archivo.read()
        self.assertIn("Tablero ESG", contenido)
        self.assertIn("Todavia no hay huella calculada", contenido)


if __name__ == "__main__":
    unittest.main()
