# -*- coding: utf-8 -*-
"""Pruebas del motor completo, llamandolo como lo hara el agente."""

import json
import os
import subprocess
import sys
import unittest

from ayuda_pruebas import MOTOR, PruebaConCarpeta  # noqa: E402

ESG = os.path.join(MOTOR, "esg.py")


def correr(*argumentos, **extra):
    """Ejecuta el motor y devuelve (codigo, json)."""
    proceso = subprocess.run(
        [sys.executable, ESG] + [str(a) for a in argumentos],
        capture_output=True, text=True, encoding="utf-8", cwd=extra.get("cwd"))
    try:
        datos = json.loads(proceso.stdout)
    except ValueError:
        raise AssertionError("El motor no devolvio JSON.\nsalida: %s\nerror: %s"
                             % (proceso.stdout[:600], proceso.stderr[:600]))
    return proceso.returncode, datos


class PruebaContrato(unittest.TestCase):
    def test_version(self):
        codigo, datos = correr("version", "mostrar")
        self.assertEqual(codigo, 0)
        self.assertTrue(datos["ok"])
        self.assertIn("version", datos["resultado"])
        self.assertEqual(datos["advertencias"], [])

    def test_ayuda_lista_modulos(self):
        codigo, datos = correr("--ayuda")
        self.assertEqual(codigo, 0)
        modulos = datos["resultado"]["modulos"]
        for esperado in ("empresa", "plantilla", "evidencia", "version"):
            self.assertIn(esperado, modulos)
        self.assertIn("crear", modulos["empresa"]["acciones"])

    def test_modulo_inexistente(self):
        codigo, datos = correr("inventado", "algo")
        self.assertEqual(codigo, 1)
        self.assertFalse(datos["ok"])
        self.assertIn("No conozco el modulo", datos["error"].replace("ó", "o"))
        self.assertIn("empresa", datos["sugerencia"])

    def test_accion_inexistente(self):
        codigo, datos = correr("empresa", "inventar")
        self.assertEqual(codigo, 1)
        self.assertIn("no tiene la accion", datos["error"].replace("ó", "o"))

    def test_falta_accion(self):
        codigo, datos = correr("empresa")
        self.assertEqual(codigo, 1)
        self.assertIn("crear", datos["sugerencia"])


class PruebaFlujoCompleto(PruebaConCarpeta):
    """El camino que recorre una persona nueva: registrar empresa, plantilla, evidencia."""

    def test_flujo(self):
        codigo, datos = correr("empresa", "crear", "--nombre", "Alimentos del Sur SpA",
                               "--pais", "CL", "--sector", "Agroindustria", "--tamano", "mediana",
                               "--anio-base", "2025", "--raiz", self.carpeta)
        self.assertEqual(codigo, 0, datos)
        self.assertEqual(datos["resultado"]["carpeta"], "alimentos-del-sur-spa")
        self.assertTrue(os.path.isdir(os.path.join(self.carpeta, "empresas", "alimentos-del-sur-spa", "datos")))

        codigo, datos = correr("empresa", "listar", "--raiz", self.carpeta)
        self.assertEqual(datos["resultado"]["total"], 1)

        codigo, datos = correr("empresa", "ver", "--raiz", self.carpeta)
        self.assertEqual(datos["resultado"]["perfil"]["sector"], "Agroindustria")

        codigo, datos = correr("empresa", "actualizar", "--raiz", self.carpeta, "--trabajadores", "120")
        self.assertEqual(codigo, 0, datos)
        self.assertEqual(datos["resultado"]["perfil"]["trabajadores"], 120)

        codigo, datos = correr("plantilla", "crear", "--tipo", "sitios", "--raiz", self.carpeta)
        self.assertEqual(codigo, 0, datos)
        planilla = datos["resultado"]["archivo"]
        self.assertTrue(os.path.isfile(planilla))

        # la planilla recien creada se puede volver a leer
        sys.path.insert(0, MOTOR)
        from nucleo import excel
        tabla = excel.leer_tabla(planilla)
        self.assertEqual(tabla["hoja"], "Sitios")
        self.assertEqual(tabla["filas"][0]["nombre_del_sitio"], "Planta Chillan")

        codigo, datos = correr("plantilla", "crear", "--tipo", "sitios", "--raiz", self.carpeta)
        self.assertEqual(codigo, 1)
        self.assertIn("Ya existe", datos["error"])

        codigo, datos = correr("evidencia", "registrar", "--raiz", self.carpeta,
                               "--archivo", planilla, "--descripcion", "Sitios declarados")
        self.assertEqual(codigo, 0, datos)
        self.assertEqual(datos["resultado"]["entrada"]["n"], 1)
        self.assertTrue(datos["advertencias"])

        codigo, datos = correr("evidencia", "verificar", "--raiz", self.carpeta)
        self.assertTrue(datos["resultado"]["ok"])

        with open(planilla, "ab") as archivo:
            archivo.write(b"alterado")
        codigo, datos = correr("evidencia", "verificar", "--raiz", self.carpeta)
        self.assertFalse(datos["resultado"]["ok"])
        self.assertEqual(datos["resultado"]["problemas"][0]["tipo"], "archivo_modificado")

    def test_errores_utiles_para_la_persona(self):
        codigo, datos = correr("empresa", "crear", "--pais", "CL", "--raiz", self.carpeta)
        self.assertEqual(codigo, 1)
        self.assertIn("Falta el nombre", datos["error"])
        self.assertTrue(datos["sugerencia"])

        codigo, datos = correr("plantilla", "crear", "--tipo", "inventada", "--raiz", self.carpeta)
        self.assertEqual(codigo, 1)
        self.assertIn("sitios", datos["sugerencia"])

        codigo, datos = correr("empresa", "ver", "--raiz", self.carpeta)
        self.assertEqual(codigo, 1)
        self.assertIn("ninguna empresa registrada", datos["error"])

    def test_datos_desde_json(self):
        ruta_json = self.ruta("perfil.json")
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump({"nombre": "Viña Los Robles", "pais": "CL", "marcos": ["GRI", "HuellaChile"],
                       "sitios": [{"nombre": "Bodega", "tipo": "bodega"}]}, archivo, ensure_ascii=False)
        codigo, datos = correr("empresa", "crear", "--datos", ruta_json, "--raiz", self.carpeta)
        self.assertEqual(codigo, 0, datos)
        perfil = datos["resultado"]["perfil"]
        self.assertEqual(perfil["marcos"], ["GRI", "HuellaChile"])
        self.assertEqual(perfil["sitios"][0]["nombre"], "Bodega")

    def test_json_invalido_explica(self):
        ruta_json = self.ruta("malo.json")
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            archivo.write("{nombre: sin comillas}")
        codigo, datos = correr("empresa", "crear", "--datos", ruta_json, "--raiz", self.carpeta)
        self.assertEqual(codigo, 1)
        self.assertIn("JSON", datos["error"])


if __name__ == "__main__":
    unittest.main()
