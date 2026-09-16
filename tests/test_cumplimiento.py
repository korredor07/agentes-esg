# -*- coding: utf-8 -*-
"""Pruebas de la evaluacion de normativa aplicable."""

import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import aplicabilidad  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

PERFIL_CL = {"nombre": "Prueba SpA", "pais": "CL", "sector": "Industria", "tamano": "mediana",
             "trabajadores": 120, "exporta_a_ue": False}
PERFIL_PE = dict(PERFIL_CL, pais="PE", nombre="Prueba SAC")


def _por_id(resultado):
    fichas = {}
    for grupo in ("aplican", "por_revisar", "no_aplican"):
        for ficha in resultado[grupo]:
            fichas[ficha["id"]] = ficha
    return fichas


class PruebaReglas(unittest.TestCase):
    def test_karin_aplica_a_todo_empleador_chileno(self):
        fichas = _por_id(aplicabilidad.evaluar(PERFIL_CL))
        self.assertEqual(fichas["cl-karin"]["estado"], "aplica")
        self.assertEqual(fichas["cl-karin"]["skill"], "ley-karin")

    def test_normas_chilenas_no_aplican_en_peru(self):
        fichas = _por_id(aplicabilidad.evaluar(PERFIL_PE))
        for identificador in ("cl-karin", "cl-rep", "cl-retc", "cl-inclusion"):
            self.assertEqual(fichas[identificador]["estado"], "no aplica", identificador)
        self.assertEqual(fichas["pe-hostigamiento"]["estado"], "aplica")

    def test_rep_depende_de_una_respuesta(self):
        sin_respuesta = _por_id(aplicabilidad.evaluar(PERFIL_CL))
        self.assertEqual(sin_respuesta["cl-rep"]["estado"], "revisar")
        con_si = _por_id(aplicabilidad.evaluar(PERFIL_CL, {"pone_productos_prioritarios": "si"}))
        self.assertEqual(con_si["cl-rep"]["estado"], "aplica")
        con_no = _por_id(aplicabilidad.evaluar(PERFIL_CL, {"pone_productos_prioritarios": "no"}))
        self.assertEqual(con_no["cl-rep"]["estado"], "no aplica")

    def test_inclusion_depende_del_tamano(self):
        grande = _por_id(aplicabilidad.evaluar(dict(PERFIL_CL, trabajadores=150)))
        self.assertEqual(grande["cl-inclusion"]["estado"], "aplica")
        chica = _por_id(aplicabilidad.evaluar(dict(PERFIL_CL, trabajadores=20)))
        self.assertEqual(chica["cl-inclusion"]["estado"], "no aplica")
        sin_dato = _por_id(aplicabilidad.evaluar(dict(PERFIL_CL, trabajadores=0)))
        self.assertEqual(sin_dato["cl-inclusion"]["estado"], "revisar")

    def test_normas_europeas_solo_si_exporta(self):
        sin_ue = _por_id(aplicabilidad.evaluar(PERFIL_CL))
        self.assertEqual(sin_ue["ue-cbam"]["estado"], "no aplica")
        self.assertEqual(sin_ue["ue-cadena"]["estado"], "no aplica")
        con_ue = _por_id(aplicabilidad.evaluar(dict(PERFIL_CL, exporta_a_ue=True)))
        self.assertEqual(con_ue["ue-cadena"]["estado"], "aplica")
        self.assertEqual(con_ue["ue-cbam"]["estado"], "revisar")
        con_acero = _por_id(aplicabilidad.evaluar(dict(PERFIL_CL, exporta_a_ue=True),
                                                  {"exporta_bienes_cbam": "si"}))
        self.assertEqual(con_acero["ue-cbam"]["estado"], "aplica")

    def test_retc_segun_actividad(self):
        con_calderas = _por_id(aplicabilidad.evaluar(PERFIL_CL, {"tiene_calderas": "si"}))
        self.assertEqual(con_calderas["cl-retc"]["estado"], "aplica")
        sin_nada = _por_id(aplicabilidad.evaluar(PERFIL_CL, {
            "tiene_calderas": "no", "genera_residuos_industriales": "no", "descarga_riles": "no"}))
        self.assertEqual(sin_nada["cl-retc"]["estado"], "no aplica")

    def test_orden_por_riesgo(self):
        resultado = aplicabilidad.evaluar(PERFIL_CL, {"pone_productos_prioritarios": "si"})
        riesgos = [f["riesgo"] for f in resultado["aplican"]]
        orden = {"alto": 0, "medio": 1, "bajo": 2}
        self.assertEqual(riesgos, sorted(riesgos, key=lambda r: orden[r]))

    def test_cada_ficha_trae_lo_necesario(self):
        for ficha in aplicabilidad.evaluar(PERFIL_CL)["aplican"]:
            for clave in ("norma", "que_exige", "plazos", "sancion", "skill", "fuente", "motivo"):
                self.assertTrue(ficha.get(clave), "%s sin %s" % (ficha["id"], clave))

    def test_avisa_que_no_es_asesoria_legal(self):
        self.assertIn("no es asesoria legal", aplicabilidad.evaluar(PERFIL_CL)["aviso"].lower())

    def test_preguntas_pendientes_bajan_al_responder(self):
        sin = aplicabilidad.evaluar(PERFIL_CL)
        con = aplicabilidad.evaluar(PERFIL_CL, {"descarga_riles": "no", "supervisada_cmf": "no"})
        self.assertEqual(len(con["preguntas_pendientes"]), len(sin["preguntas_pendientes"]) - 2)

    def test_no_pregunta_lo_que_ya_dice_el_perfil(self):
        # Hallazgo E2E: se preguntaba si tiene trabajadores y si exporta con el perfil ya lleno.
        claves = {p["clave"] for p in aplicabilidad.evaluar(PERFIL_CL)["preguntas_pendientes"]}
        self.assertNotIn("tiene_trabajadores", claves)
        self.assertNotIn("exporta_a_ue", claves)
        self.assertNotIn("cien_o_mas_trabajadores", claves)

    def test_no_pregunta_lo_que_depende_de_un_no(self):
        claves = {p["clave"] for p in aplicabilidad.evaluar(PERFIL_CL, {"tiene_calderas": "no"})["preguntas_pendientes"]}
        self.assertNotIn("exporta_bienes_cbam", claves)
        self.assertNotIn("exporta_commodities_eudr", claves)
        self.assertNotIn("fuente_fija_grande", claves)

    def test_sin_calderas_el_impuesto_verde_no_queda_por_confirmar(self):
        fichas = _por_id(aplicabilidad.evaluar(PERFIL_CL, {"tiene_calderas": "no"}))
        self.assertEqual(fichas["cl-impuesto-verde"]["estado"], "no aplica")

    def test_respuesta_no_se_deja_en_revisar(self):
        fichas = _por_id(aplicabilidad.evaluar(PERFIL_CL, {"pone_productos_prioritarios": "no se"}))
        self.assertEqual(fichas["cl-rep"]["estado"], "revisar")


class PruebaModuloCumplimiento(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloCumplimiento, self).setUp()
        from modulos import cumplimiento
        self.cumplimiento = cumplimiento
        espacio.crear_empresa(dict(PERFIL_CL), raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def test_flujo_completo(self):
        pendientes = self.cumplimiento.preguntas(self.opciones)
        # Pocas y utiles: el perfil ya responde trabajadores y exportacion (hallazgo E2E).
        self.assertGreaterEqual(pendientes["total"], 4)
        self.assertNotIn("exporta_a_ue", [p["clave"] for p in pendientes["preguntas"]])
        self.cumplimiento.responder(dict(self.opciones, clave="pone_productos_prioritarios", respuesta="si"))
        revision = self.cumplimiento.revisar(self.opciones).resultado
        self.assertTrue(any("REP" in f["norma"] for f in revision["aplican"]))
        informe = self.cumplimiento.informe_html(self.opciones).resultado
        self.assertTrue(os.path.isfile(informe["archivo"]))

    def test_clave_invalida(self):
        with self.assertRaises(Problema):
            self.cumplimiento.responder(dict(self.opciones, clave="inventada", respuesta="si"))

    def test_respuesta_faltante(self):
        with self.assertRaises(Problema):
            self.cumplimiento.responder(dict(self.opciones, clave="tiene_calderas"))


if __name__ == "__main__":
    unittest.main()
