# -*- coding: utf-8 -*-
"""Pruebas del modulo de Union Europea.

Los casos base son los ejemplos resueltos de la investigacion normativa
(docs/investigacion/07-union-europea.md), que estan transcritos del Diario
Oficial de la Union Europea:

    CBAM    500 t de acero peruano importadas en 2026, SEE 1,80 t CO2e/t,
            certificado a 75 EUR -> 22,5 certificados y 1.687,50 EUR.
    ETS     Callao-Rotterdam, 1.500 t de HFO, 8.000 TEU al 85 % -> 25,76 EUR/TEU.
    FuelEU  10.000 t de HFO en 2025 -> deficit de 975 t CO2e y 622.088 EUR.
"""

import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import union_europea as ue  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

GWP = {"ch4": 25, "n2o": 298}   # valores del ejemplo de la investigacion, no verificados


class PruebaCbam(unittest.TestCase):
    def test_ejemplo_resuelto_acero_peruano(self):
        emisiones = ue.cbam_emisiones_incorporadas("acero", 500, see=1.80)
        self.assertEqual(emisiones["emisiones_incorporadas_t_co2e"], 900.0)
        self.assertEqual(emisiones["sector"], "hierro_acero")
        self.assertFalse(emisiones["computa_indirectas"])

        costo = ue.cbam_costo_estimado(900.0, 2026, 75, cantidad_toneladas=500)
        self.assertEqual(costo["factor_cbam"], 0.975)
        self.assertAlmostEqual(costo["porcentaje_exigible"], 0.025, places=6)
        self.assertAlmostEqual(costo["certificados_a_entregar"], 22.5, places=6)
        self.assertAlmostEqual(costo["costo_eur"], 1687.50, places=2)
        self.assertAlmostEqual(costo["costo_por_tonelada_eur"], 3.375, places=3)

    def test_curva_del_factor_cbam_hasta_2034(self):
        esperado = {2026: 1687.50, 2027: 3375.00, 2028: 6750.00, 2029: 15187.50,
                    2030: 32737.50, 2031: 41175.00, 2032: 49612.50, 2033: 58050.00,
                    2034: 67500.00}
        curva = {f["anio"]: f["costo_eur"] for f in ue.cbam_curva(900.0, 75, 500)}
        for anio, costo in esperado.items():
            self.assertAlmostEqual(curva[anio], costo, places=2, msg="año %d" % anio)
        self.assertEqual(ue.factor_cbam(2034)[1], 1.0)
        self.assertEqual(ue.factor_cbam(2040)[0], 0.0)

    def test_umbral_de_50_toneladas_es_del_importador(self):
        self.assertTrue(ue.cbam_umbral_masa(50, "acero")["exento"])
        self.assertFalse(ue.cbam_umbral_masa(50.5, "acero")["exento"])
        self.assertEqual(ue.cbam_umbral_masa(10, "aluminio")["umbral_toneladas"], 50.0)
        # Electricidad e hidrogeno no tienen umbral de minimis.
        self.assertFalse(ue.cbam_umbral_masa(1, "hidrogeno")["exento"])
        self.assertIsNone(ue.cbam_umbral_masa(1, "hidrogeno")["umbral_toneladas"])

    def test_exencion_por_masa_deja_el_costo_en_cero(self):
        costo = ue.cbam_costo_estimado(900.0, 2026, 75, masa_neta_anual_importador=30, sector="acero")
        self.assertTrue(costo["exencion_por_masa"]["exento"])
        self.assertEqual(costo["costo_eur"], 0.0)

    def test_mercancia_compleja_suma_los_precursores(self):
        emisiones = ue.cbam_emisiones_incorporadas(
            "acero", 100, emisiones_directas=700, nivel_actividad=1000,
            precursores=[{"masa": 300, "see": 1.2}, {"masa": 80, "see": 0.5}])
        # (700 + 360 + 40) / 1000 = 1,1 t CO2e por tonelada
        self.assertAlmostEqual(emisiones["see_t_co2e_por_t"], 1.1, places=6)
        self.assertAlmostEqual(emisiones["emisiones_incorporadas_t_co2e"], 110.0, places=6)
        self.assertEqual(emisiones["tipo_de_mercancia"], "compleja")

    def test_cemento_exige_las_emisiones_indirectas(self):
        with self.assertRaises(Problema) as contexto:
            ue.cbam_emisiones_incorporadas("cemento", 200, emisiones_directas=60000,
                                           nivel_actividad=100000)
        self.assertIn("indirectas", contexto.exception.mensaje)
        completo = ue.cbam_emisiones_incorporadas("cemento", 200, emisiones_directas=60000,
                                                  emisiones_indirectas=9000, nivel_actividad=100000)
        self.assertTrue(completo["computa_indirectas"])
        self.assertAlmostEqual(completo["see_t_co2e_por_t"], 0.69, places=6)

    def test_acero_deja_fuera_las_indirectas_y_lo_avisa(self):
        emisiones = ue.cbam_emisiones_incorporadas("acero", 100, emisiones_directas=1800,
                                                   emisiones_indirectas=500, nivel_actividad=1000)
        self.assertAlmostEqual(emisiones["see_t_co2e_por_t"], 1.8, places=6)
        self.assertTrue(any("solo emisiones directas" in a for a in emisiones["advertencias"]))

    def test_producto_fuera_del_cbam(self):
        with self.assertRaises(Problema) as contexto:
            ue.cbam_emisiones_incorporadas("fruta", 500, see=1.0)
        self.assertIn("cemento", contexto.exception.sugerencia)

    def test_no_inventa_el_precio_del_certificado(self):
        with self.assertRaises(Problema) as contexto:
            ue.cbam_costo_estimado(900.0, 2026, None)
        self.assertIn("precio", contexto.exception.mensaje.lower())
        self.assertIn("mercado", contexto.exception.sugerencia)

    def test_deduccion_por_carbono_en_origen_se_marca_como_estimacion(self):
        costo = ue.cbam_costo_estimado(900.0, 2026, 75, precio_carbono_origen_eur_t=1)
        self.assertTrue(costo["deduccion_es_estimacion"])
        self.assertAlmostEqual(costo["deduccion_certificados"], 12.0, places=6)
        self.assertAlmostEqual(costo["certificados_a_entregar"], 10.5, places=6)
        self.assertTrue(costo["no_verificado"])
        self.assertTrue(any("art. 9" in p["que_falta"] for p in costo["no_verificado"]))

    def test_electricidad_no_se_calcula_porque_no_esta_verificada(self):
        with self.assertRaises(Problema) as contexto:
            ue.cbam_emisiones_incorporadas("electricidad", 100, see=0.4)
        self.assertIn("no voy a inventar", contexto.exception.sugerencia.lower())

    def test_periodo_transitorio_no_cobra(self):
        costo = ue.cbam_costo_estimado(900.0, 2025, 75)
        self.assertEqual(costo["costo_eur"], 0.0)
        self.assertTrue(any("transitorio" in a for a in costo["advertencias"]))
        with self.assertRaises(Problema):
            ue.factor_cbam(2020)


class PruebaEtsMaritimo(unittest.TestCase):
    def test_ejemplo_resuelto_callao_rotterdam(self):
        calculo = ue.ets_maritimo_obligacion(2026, "tercer_pais_ue", consumo_toneladas=1500,
                                             combustible="HFO", precio_eua_eur=75, teu=6800)
        self.assertAlmostEqual(calculo["emisiones_viaje_t_co2e"], 4671.0, places=3)
        self.assertEqual(calculo["cobertura_viaje"], 0.50)
        self.assertAlmostEqual(calculo["emisiones_cubiertas_t_co2e"], 2335.5, places=3)
        self.assertEqual(calculo["porcentaje_entrega"], 1.0)
        self.assertAlmostEqual(calculo["costo_eur"], 175162.50, places=2)
        self.assertAlmostEqual(calculo["recargo_por_teu_eur"], 25.76, places=2)
        self.assertAlmostEqual(calculo["recargo_por_feu_eur"], 51.52, places=2)

    def test_entrega_escalonada_por_anio(self):
        esperado = {2024: (0.40, 10.30), 2025: (0.70, 18.03), 2026: (1.00, 25.76)}
        for anio, (porcentaje, por_teu) in esperado.items():
            calculo = ue.ets_maritimo_obligacion(anio, "tercer_pais_ue", consumo_toneladas=1500,
                                                 precio_eua_eur=75, teu=6800)
            self.assertEqual(calculo["porcentaje_entrega"], porcentaje, "año %d" % anio)
            self.assertAlmostEqual(calculo["recargo_por_teu_eur"], por_teu, places=2, msg="año %d" % anio)
        self.assertEqual(ue.porcentaje_entrega_ets(2030), 1.0)

    def test_metano_y_oxido_nitroso_desde_2026(self):
        self.assertAlmostEqual(ue.factor_co2e_ttw("HFO", GWP), 3.16889, places=5)
        calculo = ue.ets_maritimo_obligacion(2026, "tercer_pais_ue", consumo_toneladas=1500,
                                             precio_eua_eur=75, teu=6800,
                                             incluir_ch4_n2o=True, gwp=GWP)
        self.assertAlmostEqual(calculo["emisiones_cubiertas_t_co2e"], 2376.7, places=1)
        self.assertAlmostEqual(calculo["costo_eur"], 178250.06, places=2)
        self.assertAlmostEqual(calculo["recargo_por_teu_eur"], 26.21, places=2)

    def test_avisa_que_falta_ch4_y_n2o_en_2026(self):
        calculo = ue.ets_maritimo_obligacion(2026, "tercer_pais_ue", consumo_toneladas=1500,
                                             precio_eua_eur=75)
        self.assertTrue(any("metano" in a for a in calculo["advertencias"]))

    def test_cobertura_segun_el_tipo_de_viaje(self):
        self.assertEqual(ue.tipo_viaje_ets("intra_ue")["cobertura"], 1.00)
        self.assertEqual(ue.tipo_viaje_ets("en_puerto")["cobertura"], 1.00)
        self.assertEqual(ue.tipo_viaje_ets("ue_tercer_pais")["cobertura"], 0.50)
        self.assertEqual(ue.tipo_viaje_ets("Chile - UE")["cobertura"], 0.50)
        with self.assertRaises(Problema):
            ue.tipo_viaje_ets("vuelo directo")

    def test_exige_los_gwp_para_incluir_metano(self):
        with self.assertRaises(Problema) as contexto:
            ue.ets_maritimo_obligacion(2026, "tercer_pais_ue", consumo_toneladas=1500,
                                       precio_eua_eur=75, incluir_ch4_n2o=True)
        self.assertIn("potencial de calentamiento global", contexto.exception.mensaje)

    def test_antes_de_2024_el_maritimo_no_estaba_en_el_mercado(self):
        with self.assertRaises(Problema) as contexto:
            ue.ets_maritimo_obligacion(2023, "tercer_pais_ue", consumo_toneladas=100, precio_eua_eur=75)
        self.assertIn("2024", contexto.exception.mensaje)


class PruebaFuelEu(unittest.TestCase):
    def test_objetivos_de_intensidad_por_periodo(self):
        esperado = {2025: 89.3368, 2029: 89.3368, 2030: 85.6904, 2035: 77.9418,
                    2040: 62.9004, 2045: 34.6408, 2050: 18.2320}
        for anio, objetivo in esperado.items():
            calculo = ue.fueleu_intensidad_objetivo(anio)
            self.assertAlmostEqual(calculo["objetivo_gco2e_mj"], objetivo, places=4, msg="año %d" % anio)
        with self.assertRaises(Problema):
            ue.fueleu_intensidad_objetivo(2024)

    def test_ejemplo_resuelto_buque_con_hfo_puro_en_2025(self):
        balance = ue.fueleu_balance(2025, consumos=[{"combustible": "HFO", "toneladas": 10000}], gwp=GWP)
        detalle = balance["detalle_intensidad"]
        self.assertAlmostEqual(detalle["wtt_gco2e_mj"], 13.5, places=4)
        self.assertAlmostEqual(detalle["ttw_gco2e_mj"], 78.2442, places=4)
        self.assertAlmostEqual(balance["intensidad_real_gco2e_mj"], 91.7442, places=4)
        self.assertAlmostEqual(balance["energia_total_mj"], 405000000.0, places=0)
        self.assertAlmostEqual(balance["balance_t_co2e"], -975.0, places=1)
        self.assertEqual(balance["estado"], "deficit")
        self.assertAlmostEqual(balance["equivalente_vlsfo_t"], 259.20, places=2)
        self.assertAlmostEqual(balance["penalizacion_eur"], 622088.0, delta=1.0)

    def test_escalada_por_reincidencia(self):
        esperado = {1: 622088.0, 2: 684296.0, 3: 746505.0, 5: 870923.0, 10: 1181967.0}
        for periodos, penalizacion in esperado.items():
            balance = ue.fueleu_balance(2025, consumos=[{"combustible": "HFO", "toneladas": 10000}],
                                        gwp=GWP, periodos_consecutivos=periodos)
            self.assertAlmostEqual(balance["multiplicador_reincidencia"], 1 + (periodos - 1) / 10.0, places=6)
            self.assertAlmostEqual(balance["penalizacion_eur"], penalizacion, delta=1.5,
                                   msg="%d periodos" % periodos)

    def test_superavit_no_genera_penalizacion(self):
        balance = ue.fueleu_balance(2025, ghgie_actual=80.0, energia_total_mj=405000000.0)
        self.assertEqual(balance["estado"], "superavit")
        self.assertEqual(balance["penalizacion_eur"], 0.0)
        self.assertTrue(any("banking" in a for a in balance["advertencias"]))

    def test_exige_los_gwp_para_calcular_la_intensidad(self):
        with self.assertRaises(Problema) as contexto:
            ue.fueleu_balance(2025, consumos=[{"combustible": "HFO", "toneladas": 10000}])
        self.assertIn("potencial de calentamiento global", contexto.exception.mensaje)

    def test_methane_slip_del_gnl_esta_en_la_tabla(self):
        self.assertEqual(ue.combustible_fueleu("GNL")["c_slip"], 3.1)
        self.assertEqual(ue.combustible_fueleu("gnl diesel baja")["c_slip"], 0.2)
        self.assertEqual(ue.combustible_fueleu("MGO")["cf_co2"], 3.206)
        otto = ue.fueleu_balance(2025, consumos=[{"combustible": "GNL_OTTO_MEDIA", "toneladas": 10000}],
                                 gwp=GWP)
        diesel = ue.fueleu_balance(2025, consumos=[{"combustible": "GNL_DIESEL_BAJA", "toneladas": 10000}],
                                   gwp=GWP)
        self.assertGreater(otto["intensidad_real_gco2e_mj"], diesel["intensidad_real_gco2e_mj"])

    def test_combustible_desconocido(self):
        with self.assertRaises(Problema) as contexto:
            ue.combustible_fueleu("petroleo de ballena")
        self.assertIn("HFO", contexto.exception.sugerencia)


class PruebaCsrd(unittest.TestCase):
    def test_umbrales_del_omnibus_son_acumulativos(self):
        dentro = ue.csrd_aplica(empleados=1200, volumen_negocios_eur=500000000, establecida_en_ue=True)
        self.assertEqual(dentro["estado"], "aplica")
        self.assertEqual(dentro["primer_ejercicio"], 2027)
        self.assertEqual(dentro["primer_informe"], 2028)
        # Supera empleados pero no facturacion: no basta.
        fuera = ue.csrd_aplica(empleados=1200, volumen_negocios_eur=100000000, establecida_en_ue=True)
        self.assertEqual(fuera["estado"], "no aplica")
        self.assertEqual(dentro["umbrales"]["volumen_negocios_eur"], 450000000.0)
        self.assertEqual(dentro["umbrales"]["empleados"], 1000)

    def test_empresa_protegida_y_tope_vsme(self):
        pyme = ue.csrd_aplica(empleados=120, tiene_filial_ue=False)
        self.assertTrue(pyme["empresa_protegida"])
        self.assertTrue(pyme["tope_vsme"]["aplica"])
        self.assertIn("VSME", pyme["tope_vsme"]["limite"])
        self.assertIn("PACTAR", pyme["tope_vsme"]["ojo"])
        grande = ue.csrd_aplica(empleados=4000, tiene_filial_ue=False)
        self.assertFalse(grande["empresa_protegida"])

    def test_matriz_de_tercer_pais(self):
        dentro = ue.csrd_aplica(volumen_negocios_en_ue_eur=500000000, filial_ue_volumen_eur=250000000)
        self.assertEqual(dentro["estado"], "aplica")
        chica = ue.csrd_aplica(volumen_negocios_en_ue_eur=20000000, filial_ue_volumen_eur=5000000)
        self.assertEqual(chica["estado"], "no aplica")
        sin_presencia = ue.csrd_aplica(empleados=120, tiene_filial_ue=False)
        self.assertEqual(sin_presencia["estado"], "no aplica")

    def test_nunca_dice_no_aplica_si_le_falta_el_dato(self):
        duda = ue.csrd_aplica(empleados=120)
        self.assertEqual(duda["estado"], "revisar")
        self.assertTrue(duda["faltan_datos"])

    def test_umbrales_de_la_csddd_tras_la_reforma(self):
        ficha = ue.csrd_aplica(empleados=120, tiene_filial_ue=False)["csddd"]
        self.assertEqual(ficha["empleados"], 5000)
        self.assertEqual(ficha["volumen_negocios_eur"], 1500000000.0)
        self.assertIn("3 %", ficha["sancion"])
        self.assertIn("2029", ficha["aplicacion"])


class PruebaEudr(unittest.TestCase):
    def test_chile_riesgo_bajo_tiene_diligencia_simplificada(self):
        calculo = ue.eudr_aplica("madera", "CL", "mediana")
        self.assertEqual(calculo["estado"], "aplica")
        self.assertEqual(calculo["riesgo_pais"], "bajo")
        self.assertEqual(calculo["diligencia"], "simplificada")
        exigibles = [p["paso"] for p in calculo["pasos_de_diligencia"] if p["exigible"]]
        self.assertEqual(exigibles, [1, 4])   # recopilar y declarar; sin arts. 10 y 11

    def test_peru_riesgo_estandar_exige_diligencia_completa(self):
        calculo = ue.eudr_aplica("cafe", "PE", "grande")
        self.assertEqual(calculo["riesgo_pais"], "estandar")
        self.assertEqual(calculo["diligencia"], "completa")
        self.assertTrue(all(p["exigible"] for p in calculo["pasos_de_diligencia"]))
        self.assertEqual(calculo["fecha_de_aplicacion"], "30 de diciembre de 2026")

    def test_fecha_de_corte_y_requisitos_acumulativos(self):
        calculo = ue.eudr_aplica("cacao", "PE", "micro")
        self.assertIn("31 de diciembre de 2020", calculo["fecha_de_corte"])
        self.assertEqual(len(calculo["requisitos_articulo_3"]), 3)
        self.assertEqual(calculo["fecha_de_aplicacion"], "30 de junio de 2027")
        con_eutr = ue.eudr_aplica("madera", "PE", "micro", cubierto_por_eutr=True)
        self.assertEqual(con_eutr["fecha_de_aplicacion"], "30 de diciembre de 2026")

    def test_pais_sin_lista_queda_en_riesgo_estandar(self):
        riesgo, listado = ue.riesgo_pais_eudr("BO")
        self.assertEqual(riesgo, "estandar")
        self.assertFalse(listado)
        self.assertEqual(ue.riesgo_pais_eudr("RU")[0], "alto")

    def test_producto_fuera_del_eudr(self):
        with self.assertRaises(Problema) as contexto:
            ue.eudr_aplica("uva de mesa", "CL", "grande")
        self.assertIn("siete", contexto.exception.sugerencia)
        self.assertEqual(ue.eudr_aplica()["estado"], "revisar")

    def test_informacion_por_lote_y_por_predio(self):
        calculo = ue.eudr_aplica("cafe", "PE", "grande")
        claves = {i["id"]: i["por"] for i in calculo["informacion_requerida"]}
        self.assertEqual(claves["geolocalizacion"], "predio")
        self.assertEqual(claves["cantidad"], "lote")
        self.assertTrue(any("4 %" in s for s in calculo["sanciones"]))


class PruebaPendientes(unittest.TestCase):
    def test_los_puntos_no_verificados_estan_declarados(self):
        for tema in ("cbam_valores_por_defecto", "cbam_deduccion_origen", "gwp_fueleu",
                     "eudr_geolocalizacion", "csrd_tope_vsme_extraterritorial", "csrd_espana"):
            ficha = ue.pendientes(tema)
            self.assertEqual(len(ficha), 1, tema)
            self.assertTrue(ficha[0]["que_falta"])
            self.assertTrue(ficha[0]["como_resolverlo"])
        self.assertEqual(ue.pendientes("inventado"), [])


class PruebaModuloEuropa(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloEuropa, self).setUp()
        from modulos import europa as modulo
        self.modulo = modulo
        espacio.crear_empresa({"nombre": "Exportadora Andina SpA", "pais": "CL",
                               "sector": "Agroindustria", "tamano": "mediana",
                               "trabajadores": 140, "anio_base": 2025, "exporta_a_ue": True},
                              raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Exportadora Andina SpA"}

    def test_acciones_registradas(self):
        self.assertEqual(sorted(self.modulo.ACCIONES),
                         ["aplica", "cbam", "eudr", "informe", "maritimo"])

    def test_aplica_y_guarda_las_respuestas(self):
        primero = self.modulo.aplica(self.opciones).resultado
        self.assertTrue(primero["exporta_a_ue"])
        self.assertTrue(any(m["id"] == "cbam" and m["estado"] == "revisar"
                            for m in primero["mecanismos"]))
        self.assertTrue(primero["preguntas_pendientes"])

        segundo = self.modulo.aplica(dict(self.opciones, exporta_bienes_cbam="no",
                                          exporta_commodities_eudr="si",
                                          envia_por_mar="si")).resultado
        por_id = {m["id"]: m for m in segundo["mecanismos"]}
        self.assertEqual(por_id["cbam"]["estado"], "no aplica")
        self.assertEqual(por_id["eudr"]["estado"], "aplica")
        self.assertEqual(por_id["maritimo"]["estado"], "aplica")
        self.assertIn("riesgo bajo", por_id["eudr"]["motivo"])

        # Las respuestas quedan guardadas para la proxima vez.
        tercero = self.modulo.aplica(self.opciones).resultado
        self.assertEqual({m["id"]: m["estado"] for m in tercero["mecanismos"]}["eudr"], "aplica")

    def test_cbam_calcula_y_deja_el_resultado_en_la_carpeta(self):
        respuesta = self.modulo.cbam(dict(self.opciones, sector="acero", cantidad="500",
                                          see="1.80", anio="2026", precio_certificado="75"))
        resultado = respuesta.resultado
        self.assertAlmostEqual(resultado["costo"]["costo_eur"], 1687.50, places=2)
        self.assertEqual(len(resultado["curva_hasta_2034"]), 9)
        self.assertTrue(os.path.isfile(resultado["archivo"]))
        self.assertTrue(any("emisiones especificas" in t.lower()
                            for t in resultado["que_entregarle_al_importador"]))

    def test_cbam_sin_sector_explica_que_falta(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.cbam(dict(self.opciones, cantidad="500", see="1.8"))
        self.assertIn("cemento", contexto.exception.sugerencia)

    def test_maritimo_calcula_el_recargo_por_contenedor(self):
        respuesta = self.modulo.maritimo(dict(self.opciones, anio="2026", consumo="1500",
                                              combustible="HFO", precio_eua="75",
                                              capacidad_teu="8000", ocupacion="0.85"))
        resultado = respuesta.resultado
        self.assertAlmostEqual(resultado["ets"]["recargo_por_teu_eur"], 25.76, places=2)
        self.assertEqual(resultado["ets"]["teu"], 6800.0)
        # Sin datos anuales del buque, FuelEU no se calcula pero se explica por que.
        self.assertIn("no_se_pudo_calcular", resultado["fueleu"])
        self.assertIn("año completo", resultado["fueleu"]["que_necesito"])

    def test_maritimo_con_datos_anuales_calcula_fueleu(self):
        respuesta = self.modulo.maritimo(dict(self.opciones, anio="2025", consumo="1500",
                                              precio_eua="75", teu="6800",
                                              consumo_anual="10000", gwp_ch4="25", gwp_n2o="298"))
        fueleu = respuesta.resultado["fueleu"]
        self.assertAlmostEqual(fueleu["penalizacion_eur"], 622088.0, delta=1.0)
        self.assertEqual(fueleu["estado"], "deficit")

    def test_maritimo_solo_fueleu_sin_viaje(self):
        # Es el ejemplo de la skill maritimo-ets: quien pregunta por FuelEU no trae un viaje.
        respuesta = self.modulo.maritimo(dict(self.opciones, anio="2025", consumo_anual="10000",
                                              combustible="HFO", precio_eua="75",
                                              gwp_ch4="25", gwp_n2o="298"))
        resultado = respuesta.resultado
        self.assertIsNone(resultado["ets"])
        self.assertAlmostEqual(resultado["fueleu"]["penalizacion_eur"], 622088.0, delta=1.0)
        self.assertIn("FuelEU", resultado["en_una_frase"])
        self.assertTrue(any(a.startswith("ETS:") for a in respuesta.advertencias))

    def test_maritimo_sin_ningun_dato_sigue_pidiendo_el_viaje(self):
        with self.assertRaises(Problema):
            self.modulo.maritimo(dict(self.opciones, anio="2026", precio_eua="75"))

    def test_eudr_entrega_la_lista_de_verificacion(self):
        respuesta = self.modulo.eudr(dict(self.opciones, producto="madera",
                                          tamano_operador="mediana"))
        resultado = respuesta.resultado
        self.assertEqual(resultado["evaluacion"]["riesgo_pais"], "bajo")
        self.assertEqual(len(resultado["lista_de_verificacion"]), 4)
        self.assertTrue(resultado["que_reunir_por_predio"])
        self.assertTrue(any("cinco años" in t for t in resultado["como_organizarlo"]))
        self.assertTrue(any("geolocalizacion" in a for a in respuesta.advertencias))

    def test_informe_html(self):
        self.modulo.aplica(dict(self.opciones, exporta_bienes_cbam="si", envia_por_mar="si"))
        self.modulo.cbam(dict(self.opciones, sector="acero", cantidad="500", see="1.80",
                              anio="2026", precio_certificado="75"))
        self.modulo.maritimo(dict(self.opciones, anio="2026", consumo="1500", precio_eua="75",
                                  teu="6800"))
        self.modulo.eudr(dict(self.opciones, producto="madera", tamano_operador="mediana"))
        respuesta = self.modulo.informe_html(self.opciones)
        archivo = respuesta.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("Normativa europea aplicable", html)
        self.assertIn("CBAM", html)
        self.assertIn("deforestacion", html.lower())
        self.assertIn("todavia no esta confirmado", html.lower())

    def test_avisa_que_no_es_asesoria_legal(self):
        respuesta = self.modulo.aplica(self.opciones)
        self.assertTrue(any("no asesoria legal" in a for a in respuesta.advertencias))


if __name__ == "__main__":
    unittest.main()
