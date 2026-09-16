# -*- coding: utf-8 -*-
"""Pruebas del calendario de obligaciones."""

import json
import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from modulos import calendario  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaCalendario(PruebaConCarpeta):
    def setUp(self):
        super(PruebaCalendario, self).setUp()
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria",
                               "tamano": "mediana", "trabajadores": 60, "anio_base": 2025},
                              raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def _responder(self, **respuestas):
        _, ruta = espacio.cargar_empresa("Prueba SpA", raiz=self.carpeta)
        destino = espacio.ruta_de(ruta, "seguimiento", "cumplimiento.json")
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump({"respuestas": respuestas}, archivo)

    def test_carga_el_calendario_chileno(self):
        filas = calendario.cargar("CL")
        self.assertGreater(len(filas), 8)
        self.assertTrue(all(f["obligacion"] and f["norma"] and f["fuente"] for f in filas))

    def test_pais_sin_calendario(self):
        with self.assertRaises(Problema) as contexto:
            calendario.cargar("PE")
        self.assertIn("Todavia no tengo el calendario", contexto.exception.mensaje)

    def test_sin_respuestas_todo_queda_por_confirmar(self):
        datos = calendario.proximas(dict(self.opciones, hoy="2026-09-16")).resultado
        self.assertTrue(datos["por_confirmar"])
        condicionadas = [f for f in datos["obligaciones_con_fecha"] if f["id"] == "dja-retc"]
        self.assertEqual(condicionadas, [])

    def test_respuestas_activan_obligaciones(self):
        self._responder(genera_residuos_industriales="si", tiene_calderas="si", tiene_trabajadores="si")
        datos = calendario.proximas(dict(self.opciones, hoy="2026-09-16")).resultado
        ids = {f["id"] for f in datos["obligaciones_con_fecha"]}
        self.assertIn("dja-retc", ids)
        self.assertIn("rue-fuentes-fijas", ids)

    def test_respuesta_negativa_excluye(self):
        self._responder(genera_residuos_industriales="no", tiene_calderas="no")
        datos = calendario.proximas(dict(self.opciones, hoy="2026-09-16")).resultado
        ids = {f["id"] for f in datos["obligaciones_con_fecha"]}
        self.assertNotIn("dja-retc", ids)
        self.assertNotIn("rue-fuentes-fijas", ids)

    def test_estados_segun_la_fecha(self):
        self._responder(genera_residuos_industriales="si")
        por_id = lambda datos: {f["id"]: f for f in datos["obligaciones_con_fecha"]}
        octubre = por_id(calendario.proximas(dict(self.opciones, hoy="2026-10-15")).resultado)
        self.assertEqual(octubre["dja-retc"]["estado"], "abierto")
        antes = por_id(calendario.proximas(dict(self.opciones, hoy="2026-09-16")).resultado)
        self.assertEqual(antes["dja-retc"]["estado"], "se acerca")
        despues = por_id(calendario.proximas(dict(self.opciones, hoy="2026-11-15")).resultado)
        self.assertEqual(despues["dja-retc"]["estado"], "cerrado este año")
        urgente = por_id(calendario.proximas(dict(self.opciones, hoy="2026-10-28")).resultado)
        self.assertEqual(urgente["dja-retc"]["estado"], "urgente")

    def test_obligaciones_permanentes_van_aparte(self):
        self._responder(genera_residuos_industriales="si")
        datos = calendario.proximas(dict(self.opciones, hoy="2026-09-16")).resultado
        ids = {f["id"] for f in datos["obligaciones_permanentes"]}
        self.assertIn("sidrep", ids)

    def test_escribe_alertas_para_el_tablero(self):
        self._responder(genera_residuos_industriales="si")
        calendario.proximas(dict(self.opciones, hoy="2026-10-15"))
        _, ruta = espacio.cargar_empresa("Prueba SpA", raiz=self.carpeta)
        archivo = os.path.join(ruta, "seguimiento", "alertas.json")
        with open(archivo, encoding="utf-8") as origen:
            alertas = json.load(origen)
        self.assertTrue(any(a["origen"] == "Calendario" for a in alertas))

    def test_no_borra_alertas_de_otros_modulos(self):
        _, ruta = espacio.cargar_empresa("Prueba SpA", raiz=self.carpeta)
        archivo = espacio.ruta_de(ruta, "seguimiento", "alertas.json")
        with open(archivo, "w", encoding="utf-8") as destino:
            json.dump([{"origen": "Ley Karin", "titulo": "Plazo de prueba", "vence": "2026-10-01"}], destino)
        self._responder(genera_residuos_industriales="si")
        calendario.proximas(dict(self.opciones, hoy="2026-10-15"))
        with open(archivo, encoding="utf-8") as origen:
            alertas = json.load(origen)
        self.assertTrue(any(a["origen"] == "Ley Karin" for a in alertas))
        self.assertTrue(any(a["origen"] == "Calendario" for a in alertas))

    def test_informe(self):
        self._responder(genera_residuos_industriales="si")
        resultado = calendario.informe_html(dict(self.opciones, hoy="2026-09-16"))
        self.assertTrue(os.path.isfile(resultado["archivo"]))
        with open(resultado["archivo"], encoding="utf-8") as archivo:
            contenido = archivo.read()
        self.assertIn("Calendario de obligaciones", contenido)

    def test_avisa_que_las_fechas_pueden_cambiar(self):
        respuesta = calendario.proximas(dict(self.opciones, hoy="2026-09-16"))
        self.assertTrue(any("pueden cambiar" in a for a in respuesta.advertencias))


if __name__ == "__main__":
    unittest.main()
