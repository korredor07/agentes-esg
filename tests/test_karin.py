# -*- coding: utf-8 -*-
"""Pruebas de los plazos de la Ley Karin.

El caso base es el ejemplo resuelto de la investigacion normativa: denuncia el
martes 15-09-2026 con investigacion interna. Los feriados de esos dias son el
viernes 18-09 y el sabado 19-09 de 2026, y el lunes 12-10-2026.
"""

import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import karin  # noqa: E402
from nucleo import espacio, fechas  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaFeriados(unittest.TestCase):
    def test_carga_feriados_nacionales(self):
        feriados = karin.cargar_feriados()
        self.assertIn(fechas.parsear_fecha("2026-09-18"), feriados)
        self.assertIn(fechas.parsear_fecha("2027-09-17"), feriados)   # feriado adicional
        self.assertIn(fechas.parsear_fecha("2027-06-28"), feriados)   # San Pedro trasladado
        self.assertNotIn(fechas.parsear_fecha("2026-12-31"), feriados)  # feriado bancario, no general

    def test_feriados_regionales_solo_si_corresponde(self):
        nacionales = karin.cargar_feriados()
        arica = karin.cargar_feriados("Arica y Parinacota")
        morro = fechas.parsear_fecha("2025-06-07")
        self.assertNotIn(morro, nacionales)
        self.assertIn(morro, arica)


class PruebaPlazos(unittest.TestCase):
    def setUp(self):
        self.calculo = karin.plazos("2026-09-15", hoy="2026-09-16")
        self.por_id = {h["id"]: h for h in self.calculo["hitos"]}

    def test_ejemplo_resuelto_de_la_investigacion(self):
        self.assertEqual(self.por_id["informar_dt"]["vence"], "2026-09-21")
        self.assertEqual(self.por_id["conclusion_investigacion"]["vence"], "2026-10-29")
        self.assertEqual(self.por_id["remision_informe"]["vence"], "2026-11-02")
        self.assertEqual(self.por_id["pronunciamiento_dt"]["vence"], "2026-12-15")
        self.assertEqual(self.por_id["aplicar_medidas"]["vence"], "2026-12-30")

    def test_tipos_de_dias(self):
        self.assertEqual(self.por_id["conclusion_investigacion"]["tipo_de_dias"], "habiles")
        self.assertEqual(self.por_id["aplicar_medidas"]["tipo_de_dias"], "corridos")
        self.assertEqual(self.por_id["medidas_resguardo"]["tipo_de_dias"], "inmediato")

    def test_medidas_de_resguardo_son_inmediatas(self):
        hito = self.por_id["medidas_resguardo"]
        self.assertIn("inmediato", hito["estado"])
        self.assertEqual(hito["vence"], "2026-09-15")

    def test_hitos_proyectados_se_marcan(self):
        self.assertFalse(self.por_id["informar_dt"]["proyectado"])
        self.assertTrue(self.por_id["remision_informe"]["proyectado"])

    def test_evento_real_recalcula_los_siguientes(self):
        con_evento = karin.plazos("2026-09-15", {"conclusion_investigacion": "2026-10-20"}, hoy="2026-10-21")
        por_id = {h["id"]: h for h in con_evento["hitos"]}
        self.assertEqual(por_id["conclusion_investigacion"]["estado"], "cumplido a tiempo")
        self.assertEqual(por_id["remision_informe"]["vence"], "2026-10-22")
        self.assertFalse(por_id["remision_informe"]["proyectado"])

    def test_detecta_cumplimiento_fuera_de_plazo(self):
        tarde = karin.plazos("2026-09-15", {"informar_dt": "2026-09-30"}, hoy="2026-10-01")
        por_id = {h["id"]: h for h in tarde["hitos"]}
        self.assertEqual(por_id["informar_dt"]["estado"], "cumplido fuera de plazo")

    def test_estado_vencido_y_por_vencer(self):
        tarde = karin.plazos("2026-09-15", hoy="2026-09-25")
        por_id = {h["id"]: h for h in tarde["hitos"]}
        self.assertEqual(por_id["informar_dt"]["estado"], "vencido")
        cerca = karin.plazos("2026-09-15", hoy="2026-09-17")
        por_id = {h["id"]: h for h in cerca["hitos"]}
        self.assertEqual(por_id["informar_dt"]["estado"], "por vencer")

    def test_region_cambia_los_feriados(self):
        # 07-06-2027 es lunes y feriado solo en Arica y Parinacota
        nacional = karin.plazos("2027-06-04", hoy="2027-06-04")
        arica = karin.plazos("2027-06-04", region="Arica y Parinacota", hoy="2027-06-04")
        por_id_nacional = {h["id"]: h for h in nacional["hitos"]}
        por_id_arica = {h["id"]: h for h in arica["hitos"]}
        self.assertNotEqual(por_id_nacional["informar_dt"]["vence"], por_id_arica["informar_dt"]["vence"])

    def test_declara_el_supuesto_del_dia_inicial(self):
        self.assertIn("Ley 19.880", self.calculo["supuesto"])
        self.assertIn("no se suspenden", self.calculo["nota_feriados"])

    def test_hito_desconocido(self):
        with self.assertRaises(Problema):
            karin.validar_evento("inventado")


class PruebaModuloKarin(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloKarin, self).setUp()
        from modulos import karin as modulo
        self.modulo = modulo
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria",
                               "tamano": "pequena", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def test_flujo_de_un_caso(self):
        creado = self.modulo.crear(dict(self.opciones, fecha_denuncia="15-09-2026",
                                        tipo="acoso laboral", denunciante="A.P.")).resultado
        self.assertEqual(creado["caso"], "KARIN-2026-001")

        listado = self.modulo.listar(self.opciones)
        self.assertEqual(listado["total"], 1)

        self.modulo.evento(dict(self.opciones, caso="KARIN-2026-001", hito="informar_dt", fecha="17-09-2026"))
        detalle = self.modulo.ver(dict(self.opciones, caso="KARIN-2026-001", hoy="2026-09-18")).resultado
        por_id = {h["id"]: h for h in detalle["plazos"]}
        self.assertEqual(por_id["informar_dt"]["cumplido_el"], "2026-09-17")
        self.assertEqual(len(detalle["caso"]["bitacora"]), 2)

        alertas = self.modulo.alertas(self.opciones).resultado
        self.assertTrue(os.path.isfile(alertas["archivo"]))
        self.assertTrue(any(a["origen"] == "Ley Karin" for a in alertas["alertas"]))

    def test_cierra_el_caso_al_aplicar_medidas(self):
        self.modulo.crear(dict(self.opciones, fecha_denuncia="15-09-2026"))
        self.modulo.evento(dict(self.opciones, caso="KARIN-2026-001", hito="aplicar_medidas",
                                fecha="30-12-2026"))
        listado = self.modulo.listar(self.opciones)
        self.assertEqual(listado["casos"][0]["estado"], "cerrado")

    def test_falta_fecha_de_denuncia(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.crear(self.opciones)
        self.assertIn("fecha", contexto.exception.mensaje.lower())

    def test_caso_inexistente(self):
        with self.assertRaises(Problema):
            self.modulo.ver(dict(self.opciones, caso="KARIN-2026-999"))

    def test_documentos_base(self):
        protocolo = self.modulo.documento(dict(self.opciones, tipo="protocolo")).resultado
        informe = self.modulo.documento(dict(self.opciones, tipo="informe")).resultado
        self.assertTrue(os.path.isfile(protocolo["archivo"]))
        self.assertTrue(os.path.isfile(informe["archivo"]))
        with self.assertRaises(Problema):
            self.modulo.documento(dict(self.opciones, tipo="inventado"))

    def test_avisos_de_privacidad_y_legal(self):
        respuesta = self.modulo.crear(dict(self.opciones, fecha_denuncia="15-09-2026"))
        textos = " ".join(respuesta.advertencias)
        self.assertIn("datos sensibles", textos)
        self.assertIn("no asesoria legal", textos)


if __name__ == "__main__":
    unittest.main()
