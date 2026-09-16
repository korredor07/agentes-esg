# -*- coding: utf-8 -*-
"""Pruebas de unidades, espacio de trabajo, evidencias y fechas."""

import datetime
import json
import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from nucleo import espacio, evidencias, fechas, unidades  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaUnidades(unittest.TestCase):
    def test_conversiones_conocidas(self):
        self.assertAlmostEqual(unidades.convertir(1, "MWh", "kWh"), 1000.0)
        self.assertAlmostEqual(unidades.convertir(1, "m3", "litros"), 1000.0)
        self.assertAlmostEqual(unidades.convertir(1000, "kg", "toneladas"), 1.0)
        self.assertAlmostEqual(unidades.convertir(1, "milla", "km"), 1.609344)
        self.assertAlmostEqual(unidades.convertir(1, "GJ", "kWh"), 277.7777777777778, places=6)
        self.assertAlmostEqual(unidades.convertir(1, "galon", "litros"), 3.785411784)
        self.assertAlmostEqual(unidades.convertir(1, "ha", "m2"), 10000.0)

    def test_acepta_como_escribe_la_gente(self):
        self.assertAlmostEqual(unidades.convertir(2, "Lts", "litros"), 2.0)
        self.assertAlmostEqual(unidades.convertir(1, "metros cúbicos", "L"), 1000.0)
        self.assertAlmostEqual(unidades.convertir(1, "m³", "L"), 1000.0)
        self.assertAlmostEqual(unidades.convertir(1, "Toneladas métricas", "kg"), 1000.0)
        self.assertAlmostEqual(unidades.convertir("1,5", "kWh", "Wh"), 1500.0)

    def test_unidad_desconocida(self):
        with self.assertRaises(Problema) as contexto:
            unidades.convertir(1, "cucharadas", "litros")
        self.assertIn("No reconozco la unidad", contexto.exception.mensaje)
        self.assertIn("kWh", contexto.exception.sugerencia)

    def test_magnitudes_distintas(self):
        with self.assertRaises(Problema) as contexto:
            unidades.convertir(1, "litros", "kg")
        self.assertIn("miden cosas distintas", contexto.exception.mensaje)

    def test_valor_no_numerico(self):
        with self.assertRaises(Problema):
            unidades.convertir("mucho", "kWh", "MWh")

    def test_misma_magnitud(self):
        self.assertTrue(unidades.misma_magnitud("kWh", "GJ"))
        self.assertFalse(unidades.misma_magnitud("kWh", "kg"))
        self.assertFalse(unidades.misma_magnitud("kWh", "no existe"))


class PruebaEspacio(PruebaConCarpeta):
    def test_crea_estructura_y_perfil(self):
        perfil, ruta, advertencias = espacio.crear_empresa(
            {"nombre": "Alimentos del Sur SpA", "pais": "CL", "sector": "Agroindustria",
             "tamano": "mediana", "anio_base": 2025}, raiz=self.carpeta)
        self.assertTrue(ruta.endswith(os.path.join("empresas", "alimentos-del-sur-spa")))
        for carpeta in espacio.CARPETAS:
            self.assertTrue(os.path.isdir(os.path.join(ruta, carpeta)), carpeta)
        with open(os.path.join(ruta, "empresa.json"), encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        self.assertEqual(guardado["nombre"], "Alimentos del Sur SpA")
        self.assertEqual(guardado["moneda"], "CLP")
        self.assertEqual(guardado["marca"]["color_primario"], "#1B4332")
        # Solo avisa lo que de verdad no se sabe: si vende a la Union Europea.
        self.assertEqual(len(advertencias), 1)
        self.assertIn("Union Europea", advertencias[0])
        self.assertIsNone(perfil["exporta_a_ue"])
        self.assertEqual(perfil["anio_base"], 2025)

    def test_lo_que_no_se_sabe_no_se_guarda_como_no(self):
        # Hallazgo E2E: «no se» terminaba guardado como «no exporta» y el año base se inventaba callado.
        perfil, _, advertencias = espacio.crear_empresa({"nombre": "Duda SpA", "pais": "CL"}, raiz=self.carpeta)
        self.assertIsNone(perfil["exporta_a_ue"])
        self.assertTrue(any("año base provisorio" in a for a in advertencias))

    def test_un_no_explicito_se_guarda_como_no(self):
        perfil, _, advertencias = espacio.crear_empresa(
            {"nombre": "Local SpA", "pais": "CL", "anio_base": 2024, "exporta_a_ue": False}, raiz=self.carpeta)
        self.assertIs(perfil["exporta_a_ue"], False)
        self.assertEqual(advertencias, [])

    def test_pais_por_defecto_avisa(self):
        _, _, advertencias = espacio.crear_empresa({"nombre": "Sin Pais"}, raiz=self.carpeta)
        self.assertTrue(any("Chile" in a for a in advertencias))

    def test_nombre_obligatorio(self):
        with self.assertRaises(Problema) as contexto:
            espacio.crear_empresa({"pais": "CL"}, raiz=self.carpeta)
        self.assertIn("Falta el nombre", contexto.exception.mensaje)

    def test_pais_invalido(self):
        with self.assertRaises(Problema) as contexto:
            espacio.crear_empresa({"nombre": "X", "pais": "XX"}, raiz=self.carpeta)
        self.assertIn("No reconozco el pais", contexto.exception.mensaje)

    def test_no_duplica_empresa(self):
        espacio.crear_empresa({"nombre": "Repetida"}, raiz=self.carpeta)
        with self.assertRaises(Problema) as contexto:
            espacio.crear_empresa({"nombre": "Repetida"}, raiz=self.carpeta)
        self.assertIn("Ya existe", contexto.exception.mensaje)

    def test_cargar_por_nombre_o_carpeta(self):
        espacio.crear_empresa({"nombre": "Viña Los Robles"}, raiz=self.carpeta)
        perfil, _ = espacio.cargar_empresa("Viña Los Robles", raiz=self.carpeta)
        self.assertEqual(perfil["nombre"], "Viña Los Robles")
        perfil, _ = espacio.cargar_empresa("vina-los-robles", raiz=self.carpeta)
        self.assertEqual(perfil["nombre"], "Viña Los Robles")

    def test_unica_empresa_se_asume(self):
        espacio.crear_empresa({"nombre": "Unica"}, raiz=self.carpeta)
        perfil, _ = espacio.cargar_empresa(None, raiz=self.carpeta)
        self.assertEqual(perfil["nombre"], "Unica")

    def test_varias_empresas_pide_elegir(self):
        espacio.crear_empresa({"nombre": "Una"}, raiz=self.carpeta)
        espacio.crear_empresa({"nombre": "Otra"}, raiz=self.carpeta)
        with self.assertRaises(Problema) as contexto:
            espacio.cargar_empresa(None, raiz=self.carpeta)
        self.assertIn("Una", contexto.exception.sugerencia)
        self.assertIn("Otra", contexto.exception.sugerencia)

    def test_empresa_inexistente(self):
        with self.assertRaises(Problema) as contexto:
            espacio.cargar_empresa("Fantasma", raiz=self.carpeta)
        self.assertIn("No encontre la empresa", contexto.exception.mensaje)

    def test_listar_empresas(self):
        espacio.crear_empresa({"nombre": "Alfa"}, raiz=self.carpeta)
        espacio.crear_empresa({"nombre": "Beta"}, raiz=self.carpeta)
        nombres = [e["nombre"] for e in espacio.listar_empresas(raiz=self.carpeta)]
        self.assertEqual(nombres, ["Alfa", "Beta"])

    def test_ruta_de_crea_carpeta(self):
        _, ruta, _ = espacio.crear_empresa({"nombre": "Gamma"}, raiz=self.carpeta)
        destino = espacio.ruta_de(ruta, "reportes", "informe.html")
        self.assertTrue(destino.endswith(os.path.join("reportes", "informe.html")))
        with self.assertRaises(Problema):
            espacio.ruta_de(ruta, "inventada")


class PruebaEvidencias(PruebaConCarpeta):
    def _archivo(self, nombre, contenido):
        ruta = self.ruta(nombre)
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return ruta

    def test_cadena_valida(self):
        carpeta = self.ruta("evidencias")
        primero = self._archivo("boleta.txt", "consumo enero 1500 kWh")
        segundo = self._archivo("planilla.txt", "datos 2025")
        uno = evidencias.registrar(carpeta, primero, "Boleta de luz de enero")
        dos = evidencias.registrar(carpeta, segundo, "Planilla de consumos")
        self.assertEqual(uno["n"], 1)
        self.assertEqual(uno["huella_anterior"], evidencias.GENESIS)
        self.assertEqual(dos["huella_anterior"], uno["huella_registro"])
        resultado = evidencias.verificar(carpeta)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["total"], 2)
        self.assertEqual(resultado["archivos_intactos"], 2)

    def test_detecta_archivo_modificado(self):
        carpeta = self.ruta("evidencias")
        ruta = self._archivo("boleta.txt", "1500 kWh")
        evidencias.registrar(carpeta, ruta, "Boleta")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("150 kWh")
        resultado = evidencias.verificar(carpeta)
        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["problemas"][0]["tipo"], "archivo_modificado")

    def test_detecta_archivo_faltante(self):
        carpeta = self.ruta("evidencias")
        ruta = self._archivo("temporal.txt", "x")
        evidencias.registrar(carpeta, ruta, "Temporal")
        os.remove(ruta)
        resultado = evidencias.verificar(carpeta)
        self.assertEqual(resultado["problemas"][0]["tipo"], "archivo_faltante")

    def test_detecta_registro_alterado(self):
        carpeta = self.ruta("evidencias")
        ruta = self._archivo("informe.txt", "contenido")
        evidencias.registrar(carpeta, ruta, "Informe original")
        registro = os.path.join(carpeta, evidencias.NOMBRE_REGISTRO)
        with open(registro, encoding="utf-8") as archivo:
            entrada = json.loads(archivo.read().strip())
        entrada["descripcion"] = "Informe adulterado"
        with open(registro, "w", encoding="utf-8") as archivo:
            archivo.write(json.dumps(entrada, ensure_ascii=False) + "\n")
        resultado = evidencias.verificar(carpeta)
        self.assertEqual(resultado["problemas"][0]["tipo"], "registro_alterado")

    def test_detecta_cadena_rota(self):
        carpeta = self.ruta("evidencias")
        for nombre in ("a.txt", "b.txt", "c.txt"):
            evidencias.registrar(carpeta, self._archivo(nombre, nombre), nombre)
        registro = os.path.join(carpeta, evidencias.NOMBRE_REGISTRO)
        with open(registro, encoding="utf-8") as archivo:
            lineas = archivo.readlines()
        del lineas[1]
        with open(registro, "w", encoding="utf-8") as archivo:
            archivo.writelines(lineas)
        resultado = evidencias.verificar(carpeta)
        self.assertTrue(any(p["tipo"] == "cadena_rota" for p in resultado["problemas"]))

    def test_archivo_inexistente_al_registrar(self):
        with self.assertRaises(Problema):
            evidencias.registrar(self.ruta("evidencias"), self.ruta("no-esta.txt"), "x")

    def test_listar(self):
        carpeta = self.ruta("evidencias")
        evidencias.registrar(carpeta, self._archivo("a.txt", "a"), "Primera")
        listado = evidencias.listar(carpeta)
        self.assertEqual(listado[0]["descripcion"], "Primera")
        self.assertEqual(len(listado[0]["sha256"]), 64)


class PruebaFechas(unittest.TestCase):
    FERIADOS = {
        datetime.date(2026, 9, 18): "Independencia",
        datetime.date(2026, 9, 19): "Glorias del Ejercito",
    }

    def test_parsear_formatos(self):
        esperado = datetime.date(2026, 1, 31)
        for texto in ("2026-01-31", "31-01-2026", "31/01/2026", "31.01.2026", "31 de enero de 2026"):
            self.assertEqual(fechas.parsear_fecha(texto), esperado, texto)
        self.assertEqual(fechas.parsear_fecha(esperado), esperado)

    def test_fecha_invalida(self):
        with self.assertRaises(Problema) as contexto:
            fechas.parsear_fecha("el martes")
        self.assertIn("No entiendo la fecha", contexto.exception.mensaje)

    def test_dia_habil(self):
        self.assertTrue(fechas.es_habil("2026-09-15"))            # martes
        self.assertFalse(fechas.es_habil("2026-09-19"))           # sabado
        self.assertFalse(fechas.es_habil("2026-09-20"))           # domingo
        self.assertTrue(fechas.es_habil("2026-09-19", sabado_habil=True))
        self.assertFalse(fechas.es_habil("2026-09-18", self.FERIADOS))

    def test_suma_saltando_fin_de_semana_y_feriados(self):
        # jueves 17-09-2026: el 18 y 19 son feriados, 20 domingo -> 1 dia habil = lunes 21
        self.assertEqual(fechas.sumar_dias_habiles("2026-09-17", 1, self.FERIADOS), datetime.date(2026, 9, 21))
        # sin feriados, viernes 18 seria habil
        self.assertEqual(fechas.sumar_dias_habiles("2026-09-17", 1), datetime.date(2026, 9, 18))
        self.assertEqual(fechas.sumar_dias_habiles("2026-09-17", 3, self.FERIADOS), datetime.date(2026, 9, 23))

    def test_dias_habiles_entre(self):
        self.assertEqual(fechas.dias_habiles_entre("2026-09-17", "2026-09-21", self.FERIADOS), 1)
        self.assertEqual(fechas.dias_habiles_entre("2026-09-21", "2026-09-17", self.FERIADOS), -1)

    def test_plazo_habiles_y_corridos(self):
        resultado = fechas.plazo("2026-09-17", 30, "habiles", self.FERIADOS, hoy="2026-09-17")
        self.assertEqual(resultado["tipo"], "habiles")
        self.assertEqual(resultado["dias_restantes"], 30)
        self.assertEqual(resultado["estado"], "vigente")
        corrido = fechas.plazo("2026-09-17", 10, "corridos", hoy="2026-09-25")
        self.assertEqual(corrido["vence"], "2026-09-27")
        self.assertEqual(corrido["dias_restantes"], 2)
        self.assertEqual(corrido["estado"], "por_vencer")
        vencido = fechas.plazo("2026-08-01", 5, "corridos", hoy="2026-09-15")
        self.assertEqual(vencido["estado"], "vencido")
        self.assertLess(vencido["dias_restantes"], 0)

    def test_tipo_de_plazo_invalido(self):
        with self.assertRaises(Problema):
            fechas.plazo("2026-09-17", 5, "lunares")

    def test_cargar_feriados_desde_csv(self):
        import tempfile
        ruta = os.path.join(tempfile.mkdtemp(), "feriados.csv")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("fecha,nombre,irrenunciable\n2026-09-18,Independencia,si\n2026-12-25,Navidad,si\n")
        cargados = fechas.cargar_feriados(ruta)
        self.assertEqual(cargados[datetime.date(2026, 9, 18)], "Independencia")
        self.assertEqual(len(cargados), 2)
        self.assertEqual(fechas.cargar_feriados("no-existe.csv"), {})


if __name__ == "__main__":
    unittest.main()
