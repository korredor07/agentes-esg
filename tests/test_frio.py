# -*- coding: utf-8 -*-
"""Pruebas de la cadena de frio: temperatura cinetica media y excursiones."""

import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import frio  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

# Casos resueltos en la investigacion (docs/investigacion/09, seccion 6.2).
BODEGA_AMBIENTE = [18.0, 19.5, 22.0, 24.0, 26.0, 29.0, 31.0, 30.0, 27.0, 23.0, 20.0, 18.5]
CADENA_CON_EXCURSION = [4.0, 4.5, 5.0, 5.2, 4.8, 6.0, 12.0, 14.0, 9.0, 5.5, 4.2, 4.0]
TRES_PUNTOS = [20.0, 25.0, 30.0]


class PruebaTemperaturaCineticaMedia(unittest.TestCase):

    def test_caso_a_bodega_a_temperatura_ambiente(self):
        resultado = frio.temperatura_cinetica_media(BODEGA_AMBIENTE)
        self.assertAlmostEqual(resultado["mkt_c"], 25.017245, places=6)
        self.assertAlmostEqual(resultado["promedio_c"], 24.0, places=6)

    def test_caso_b_cadena_de_frio_con_excursion(self):
        resultado = frio.temperatura_cinetica_media(CADENA_CON_EXCURSION)
        self.assertAlmostEqual(resultado["mkt_c"], 7.227880, places=6)

    def test_caso_c_serie_de_tres_puntos(self):
        resultado = frio.temperatura_cinetica_media(TRES_PUNTOS)
        self.assertAlmostEqual(resultado["mkt_c"], 25.858208, places=6)

    def test_el_promedio_habria_dicho_que_cumple_y_la_mkt_dice_que_no(self):
        # Este es el motivo entero por el que existe la MKT.
        resultado = frio.temperatura_cinetica_media(BODEGA_AMBIENTE)
        self.assertLess(resultado["promedio_c"], 25.0)
        self.assertGreater(resultado["mkt_c"], 25.0)

    def test_la_mkt_nunca_es_menor_que_el_promedio(self):
        for serie in (BODEGA_AMBIENTE, CADENA_CON_EXCURSION, TRES_PUNTOS,
                      [-20.0, -18.0, -12.0], [0.5, 0.6, 0.4], [35.0, 40.0, 45.0]):
            resultado = frio.temperatura_cinetica_media(serie)
            self.assertGreaterEqual(resultado["mkt_c"], resultado["promedio_c"] - 1e-9)

    def test_con_temperatura_constante_la_mkt_es_esa_temperatura(self):
        resultado = frio.temperatura_cinetica_media([5.0] * 10)
        self.assertAlmostEqual(resultado["mkt_c"], 5.0, places=9)
        self.assertAlmostEqual(resultado["diferencia_con_el_promedio"], 0.0, places=9)

    def test_funciona_con_temperaturas_de_congelado(self):
        resultado = frio.temperatura_cinetica_media([-18.0, -18.5, -15.0, -20.0])
        self.assertGreaterEqual(resultado["mkt_c"], resultado["promedio_c"])

    def test_una_entalpia_mayor_da_una_mkt_mayor(self):
        baja = frio.temperatura_cinetica_media(CADENA_CON_EXCURSION, entalpia=60.0)["mkt_c"]
        media = frio.temperatura_cinetica_media(CADENA_CON_EXCURSION)["mkt_c"]
        alta = frio.temperatura_cinetica_media(CADENA_CON_EXCURSION, entalpia=100.0)["mkt_c"]
        self.assertLess(baja, media)
        self.assertLess(media, alta)
        self.assertAlmostEqual(baja, 7.0, places=1)
        self.assertAlmostEqual(alta, 7.4, places=1)

    def test_serie_vacia(self):
        with self.assertRaises(Problema):
            frio.temperatura_cinetica_media([])

    def test_una_lectura_imposible_se_detecta(self):
        with self.assertRaises(Problema) as contexto:
            frio.temperatura_cinetica_media([4.0, -300.0])
        self.assertIn("cero absoluto", contexto.exception.mensaje)

    def test_avisa_que_los_intervalos_deben_ser_regulares(self):
        resultado = frio.temperatura_cinetica_media(TRES_PUNTOS)
        self.assertTrue(any("regulares" in a for a in resultado["advertencias"]))


class PruebaExcursiones(unittest.TestCase):

    def test_detecta_la_excursion_y_su_duracion(self):
        resultado = frio.evaluar_excursiones(CADENA_CON_EXCURSION, 2, 8, minutos_por_lectura=60)
        self.assertEqual(resultado["total_excursiones"], 1)
        excursion = resultado["excursiones"][0]
        self.assertEqual(excursion["lecturas"], 3)
        self.assertAlmostEqual(excursion["maxima_c"], 14.0)
        self.assertAlmostEqual(excursion["horas"], 3.0)
        self.assertTrue(excursion["por_encima"])

    def test_la_mkt_puede_cumplir_aunque_haya_excursion(self):
        resultado = frio.evaluar_excursiones(CADENA_CON_EXCURSION, 2, 8, 60)
        self.assertTrue(resultado["mkt_dentro_del_rango"])
        self.assertFalse(resultado["sin_excursiones"])
        self.assertTrue(any("no borra una excursion" in a for a in resultado["advertencias"]))

    def test_sin_excursiones_pero_con_mkt_fuera(self):
        # Todas las lecturas bajo 25, pero la MKT se pasa: el caso que el promedio esconde.
        resultado = frio.evaluar_excursiones(BODEGA_AMBIENTE, None, 31.0)
        self.assertTrue(resultado["sin_excursiones"])
        resultado = frio.evaluar_excursiones([24.0, 26.0, 24.0, 26.0], None, 26.5)
        self.assertTrue(resultado["sin_excursiones"])

    def test_cuenta_dos_excursiones_separadas(self):
        resultado = frio.evaluar_excursiones([4, 12, 4, 4, 13, 4], 2, 8)
        self.assertEqual(resultado["total_excursiones"], 2)

    def test_detecta_tambien_el_frio_de_mas(self):
        resultado = frio.evaluar_excursiones([4, 4, -2, 4], 2, 8)
        self.assertEqual(resultado["total_excursiones"], 1)
        self.assertTrue(resultado["excursiones"][0]["por_debajo"])

    def test_una_excursion_al_final_de_la_serie_se_cuenta(self):
        resultado = frio.evaluar_excursiones([4, 4, 12, 14], 2, 8)
        self.assertEqual(resultado["total_excursiones"], 1)
        self.assertEqual(resultado["excursiones"][0]["lecturas"], 2)

    def test_todo_dentro_de_rango(self):
        resultado = frio.evaluar_excursiones([4, 4.5, 5, 4.8], 2, 8, 15)
        self.assertTrue(resultado["sin_excursiones"])
        self.assertTrue(resultado["mkt_dentro_del_rango"])
        self.assertEqual(resultado["porcentaje_fuera_de_rango"], 0.0)

    def test_sin_intervalo_avisa_que_falta_la_duracion(self):
        resultado = frio.evaluar_excursiones(CADENA_CON_EXCURSION, 2, 8)
        self.assertTrue(any("cuantas horas" in a for a in resultado["advertencias"]))

    def test_sin_rango_no_calcula(self):
        with self.assertRaises(Problema):
            frio.evaluar_excursiones([4, 5], None, None)

    def test_dice_quien_decide(self):
        resultado = frio.evaluar_excursiones([4, 5], 2, 8)
        self.assertIn("registro sanitario", resultado["quien_decide"])


class PruebaLimitesLegales(unittest.TestCase):

    def setUp(self):
        self.limites = frio.cargar_limites()

    def test_cada_limite_cita_su_articulo_y_su_fuente(self):
        for limite in self.limites:
            self.assertTrue(limite["fuente"], "El limite %s no tiene fuente." % limite["id"])
            self.assertTrue(limite["articulo"], "El limite %s no cita articulo." % limite["id"])
            self.assertTrue(limite["verificado_el"])

    def test_los_congelados_van_a_menos_dieciocho(self):
        limite = frio.buscar_limite("alimento congelado", "almacenamiento", self.limites)
        self.assertAlmostEqual(limite["maximo_c"], -18.0)
        self.assertEqual(limite["articulo"], "189")

    def test_el_transporte_local_tolera_menos_doce(self):
        limite = frio.buscar_limite("alimento congelado", "transporte local", self.limites)
        self.assertAlmostEqual(limite["tolerancia_c"], -12.0)

    def test_el_transporte_interurbano_tolera_menos_quince(self):
        limite = frio.buscar_limite("alimento congelado", "transporte interurbano", self.limites)
        self.assertAlmostEqual(limite["tolerancia_c"], -15.0)

    def test_las_comidas_calientes_tienen_minimo_no_maximo(self):
        limite = frio.buscar_limite("comidas y platos preparados calientes", None, self.limites)
        self.assertAlmostEqual(limite["minimo_c"], 65.0)
        self.assertIsNone(limite["maximo_c"])

    def test_no_hay_una_sola_temperatura_de_refrigerado(self):
        # El reglamento fija temperaturas por producto: 2, 4, 5, 6, 8 y 12 grados.
        maximos = {l["maximo_c"] for l in self.limites if l["ambito"] == "alimentos"}
        self.assertIn(5.0, maximos)
        self.assertIn(6.0, maximos)
        self.assertIn(12.0, maximos)
        self.assertGreater(len(maximos), 4)

    def test_varias_situaciones_pide_elegir(self):
        resultado = frio.buscar_limite("alimento congelado", None, self.limites)
        self.assertIn("varias_opciones", resultado)

    def test_producto_desconocido_no_se_inventa(self):
        with self.assertRaises(Problema) as contexto:
            frio.buscar_limite("helado artesanal de lucuma", None, self.limites)
        self.assertIn("por tipo de producto", contexto.exception.sugerencia)

    def test_los_datos_secundarios_estan_marcados(self):
        nt208 = [l for l in self.limites if l["id"] == "nt208-refrigerado"][0]
        self.assertIn("SECUNDARIA", nt208["notas"])


class PruebaVidaUtil(unittest.TestCase):

    def test_mas_frio_alarga_la_vida_util(self):
        resultado = frio.vida_util_por_q10(20, 8, 4, 2.5)
        self.assertGreater(resultado["vida_util_dias"], 20)

    def test_mas_calor_la_acorta(self):
        resultado = frio.vida_util_por_q10(20, 4, 8, 2.5)
        self.assertLess(resultado["vida_util_dias"], 20)

    def test_a_la_temperatura_de_referencia_no_cambia(self):
        resultado = frio.vida_util_por_q10(20, 5, 5, 3.0)
        self.assertAlmostEqual(resultado["vida_util_dias"], 20.0)

    def test_sin_q10_se_niega_a_inventarlo(self):
        with self.assertRaises(Problema) as contexto:
            frio.vida_util_por_q10(20, 4, 8, None)
        self.assertIn("estabilidad", contexto.exception.sugerencia)

    def test_avisa_que_el_dato_es_de_la_empresa(self):
        resultado = frio.vida_util_por_q10(20, 4, 8, 2.5)
        self.assertTrue(any("registro sanitario" in a for a in resultado["advertencias"]))


class PruebaModulo(PruebaConCarpeta):

    def setUp(self):
        super(PruebaModulo, self).setUp()
        from modulos import frio as modulo
        self.modulo = modulo
        espacio.crear_empresa({"nombre": "Frigorifico Prueba", "pais": "CL"}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Frigorifico Prueba"}

    def test_calcula_desde_lo_que_se_escribe_en_el_comando(self):
        respuesta = self.modulo.mkt(dict(self.opciones, temperaturas="20.0 25.0 30.0"))
        self.assertAlmostEqual(respuesta.resultado["mkt_c"], 25.858208, places=6)

    def test_calcula_desde_la_planilla(self):
        self.modulo.plantilla(dict(self.opciones))
        respuesta = self.modulo.mkt(dict(self.opciones, registro="Camara 1 enero"))
        self.assertEqual(respuesta.resultado["lecturas"], 3)

    def test_registro_inexistente_lo_dice(self):
        self.modulo.plantilla(dict(self.opciones))
        with self.assertRaises(Problema) as contexto:
            self.modulo.mkt(dict(self.opciones, registro="Camara 9"))
        self.assertIn("Camara 1 enero", contexto.exception.sugerencia)

    def test_revisa_contra_el_limite_legal(self):
        respuesta = self.modulo.revisar(dict(self.opciones, temperaturas="-19 -18 -13 -18",
                                             producto="alimento congelado",
                                             situacion="transporte local"))
        self.assertFalse(respuesta.resultado["sin_excursiones"])
        self.assertIn("977", respuesta.resultado["origen_del_rango"])

    def test_sin_producto_ni_rango_no_revisa(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.revisar(dict(self.opciones, temperaturas="4 5 6"))
        self.assertIn("--producto", contexto.exception.sugerencia)

    def test_lista_los_limites(self):
        resultado = self.modulo.limites(dict(self.opciones))
        self.assertGreater(resultado["total"], 15)
        self.assertIn("por tipo de producto", resultado["mensaje"])

    def test_el_informe_queda_escrito(self):
        import os
        respuesta = self.modulo.informe_html(dict(self.opciones, temperaturas="4 5 12 14 5",
                                                  minimo="2", maximo="8", registro="Envio 1"))
        self.assertTrue(os.path.isfile(respuesta.resultado["archivo"]))

    def test_no_sobrescribe_la_planilla(self):
        self.modulo.plantilla(dict(self.opciones))
        with self.assertRaises(Problema):
            self.modulo.plantilla(dict(self.opciones))

    def test_serie_mal_escrita_se_explica(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.mkt(dict(self.opciones, temperaturas="cuatro grados"))
        self.assertIn("--temperaturas", contexto.exception.sugerencia)


if __name__ == "__main__":
    unittest.main()
