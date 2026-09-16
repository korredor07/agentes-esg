# -*- coding: utf-8 -*-
"""Pruebas del modulo de mineria.

Los casos limite usan los valores exactos de la norma: revancha de 1,00 m
(art. 49 DS 248), factor de seguridad 1,20 (art. 14 letra o DS 248), oxigeno
19,5 % (art. 144 DS 132), velocidades de 15 y 150 m/min (art. 138 DS 132) y los
gases de detencion del art. 135.

Los ejemplos resueltos de la investigacion normativa que se replican aqui:
    M1.a  Silice cuarzo a 3.800 m con turno de 12 h y presion de 475 mmHg:
          Fj = 0,50; Fa = 0,63; LPP corregido = 0,0252 mg/m3.
    M1.b  CO en ppm con Fj = 0,50: 22 ppm. LPT de H2S en ppm: no se corrige.
    M2    12 personas y 600 HP diesel: 36 + 1.698 = 1.734 m3/min.
"""

import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import mineria  # noqa: E402
from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaTablaLimites(unittest.TestCase):
    def setUp(self):
        self.limites = mineria.cargar_limites()

    def test_valores_vigentes_del_articulo_66(self):
        cuarzo = mineria.buscar_limite("Silice cristalizada - cuarzo", "mg/m3", self.limites)
        self.assertEqual(cuarzo["lpp"], 0.08)
        self.assertEqual(cuarzo["carcinogeno"], "A.1")
        # El Decreto 123/2015 bajo el arsenico de 0,16 a 0,01 mg/m3.
        arsenico = mineria.buscar_limite("Arsenico y compuestos solubles (como As)", "mg/m3", self.limites)
        self.assertEqual(arsenico["lpp"], 0.01)
        self.assertNotEqual(arsenico["lpp"], 0.16)
        co_ppm = mineria.buscar_limite("Monoxido de carbono", "ppm", self.limites)
        self.assertEqual(co_ppm["lpp"], 44)
        h2s = mineria.buscar_limite("Acido sulfhidrico (sulfuro de hidrogeno)", "mg/m3", self.limites)
        self.assertEqual(h2s["lpp"], 12.3)      # se usa 12,3 y no la entrada duplicada de 12,25
        self.assertEqual(h2s["lpt"], 21)

    def test_cada_limite_trae_articulo_y_fecha_de_verificacion(self):
        for fila in self.limites:
            self.assertTrue(fila["articulo"], "falta el articulo en %s" % fila["agente"])
            self.assertTrue(fila["fuente"], "falta la fuente en %s" % fila["agente"])
            self.assertEqual(fila["verificado_el"], "2026-09-16")
            self.assertIn(fila["unidad"], ("mg/m3", "ppm", "fibras/cc"))

    def test_no_inventa_limites_que_no_tiene(self):
        with self.assertRaises(Problema) as contexto:
            mineria.buscar_limite("cianuro de hidrogeno", limites=self.limites)
        self.assertIn("no voy a inventar", contexto.exception.sugerencia.lower())

    def test_pide_la_unidad_cuando_hay_dos_filas(self):
        with self.assertRaises(Problema):
            mineria.buscar_limite("Monoxido de carbono", limites=self.limites)   # esta en ppm y en mg/m3


class PruebaCorreccionDeLimites(unittest.TestCase):
    def test_ejemplo_resuelto_silice_en_altura(self):
        # M1.a: 12 h de turno a 3.800 m con 475 mmHg
        correccion = mineria.corregir_limite(0.08, "mg/m3", "ponderado", horas_diarias=12,
                                             presion_mmhg=475, altitud_m=3800)
        self.assertEqual(correccion["fj"], 0.50)
        self.assertEqual(correccion["fa"], 0.63)
        self.assertAlmostEqual(correccion["limite_corregido"], 0.0252, places=6)

    def test_jornada_de_ocho_horas_no_se_corrige(self):
        correccion = mineria.corregir_limite(44, "ppm", "ponderado", horas_diarias=8)
        self.assertEqual(correccion["fj"], 1.0)
        self.assertEqual(correccion["limite_corregido"], 44)

    def test_caso_especial_de_la_semana_larga(self):
        correccion = mineria.corregir_limite(0.08, "mg/m3", "ponderado", horas_diarias=8,
                                             horas_semanales=48, altitud_m=500)
        self.assertEqual(correccion["fj"], 0.90)
        correccion_45 = mineria.corregir_limite(0.08, "mg/m3", "ponderado", horas_diarias=8,
                                                horas_semanales=45, altitud_m=500)
        self.assertEqual(correccion_45["fj"], 1.0)

    def test_redondeo_de_dos_decimales_del_ds_594(self):
        # 475/760 = 0,625: el tercer decimal es 5, asi que el segundo sube.
        self.assertEqual(mineria._dos_decimales(0.625), 0.63)
        self.assertEqual(mineria._dos_decimales(0.624), 0.62)
        # Fj con 9 horas: (8/9) x (15/16) = 0,8333...
        correccion = mineria.corregir_limite(1.0, "ppm", "ponderado", horas_diarias=9)
        self.assertEqual(correccion["fj"], 0.83)

    def test_la_altitud_no_corrige_valores_en_ppm(self):
        # M1.b: el CO en ppm solo se corrige por jornada.
        correccion = mineria.corregir_limite(44, "ppm", "ponderado", horas_diarias=12,
                                             presion_mmhg=475, altitud_m=3800)
        self.assertEqual(correccion["fa"], 1.0)
        self.assertEqual(correccion["limite_corregido"], 22.0)

    def test_el_limite_temporal_nunca_se_corrige_por_jornada(self):
        # M1.b: LPT de H2S en ppm no cambia; en mg/m3 solo cambia por altitud.
        ppm = mineria.corregir_limite(15, "ppm", "temporal", horas_diarias=12,
                                      presion_mmhg=475, altitud_m=3800)
        self.assertEqual(ppm["fj"], 1.0)
        self.assertEqual(ppm["limite_corregido"], 15)
        mgm3 = mineria.corregir_limite(21, "mg/m3", "temporal", horas_diarias=12,
                                       presion_mmhg=475, altitud_m=3800)
        self.assertEqual(mgm3["fj"], 1.0)
        self.assertAlmostEqual(mgm3["limite_corregido"], 13.23, places=6)

    def test_bajo_mil_metros_no_hay_correccion_por_altitud(self):
        correccion = mineria.corregir_limite(0.08, "mg/m3", "ponderado", altitud_m=1000, presion_mmhg=670)
        self.assertEqual(correccion["fa"], 1.0)

    def test_en_altura_sin_presion_medida_no_calcula_ni_inventa(self):
        correccion = mineria.corregir_limite(0.08, "mg/m3", "ponderado", horas_diarias=12, altitud_m=3800)
        self.assertIsNone(correccion["fa"])
        self.assertIsNone(correccion["limite_corregido"])
        self.assertTrue(correccion["no_calculado"])
        self.assertIn("presion", correccion["no_calculado"][0].lower())

    def test_la_presion_estimada_queda_marcada_como_estimacion(self):
        correccion = mineria.corregir_limite(0.08, "mg/m3", "ponderado", horas_diarias=12,
                                             altitud_m=3800, estimar_presion=True)
        self.assertTrue(correccion["presion_estimada"])
        self.assertIsNotNone(correccion["limite_corregido"])
        self.assertTrue(any("ESTIMACION" in a for a in correccion["advertencias"]))

    def test_rechaza_presion_en_hectopascales(self):
        with self.assertRaises(Problema) as contexto:
            mineria.corregir_limite(0.08, "mg/m3", "ponderado", presion_mmhg=1013, altitud_m=3800)
        self.assertIn("mmHg", contexto.exception.sugerencia)

    def test_rechaza_jornada_imposible(self):
        with self.assertRaises(Problema):
            mineria.corregir_limite(0.08, "mg/m3", "ponderado", horas_diarias=25)


class PruebaExposicion(unittest.TestCase):
    def test_justo_en_el_limite_cumple(self):
        resultado = mineria.evaluar_exposicion("Silice cristalizada - cuarzo", 0.08, "mg/m3",
                                               horas_diarias=8, altitud_m=500)
        self.assertEqual(resultado["porcentaje_del_limite"], 100.0)
        self.assertEqual(resultado["estado"], "cumple - en vigilancia")
        self.assertNotEqual(resultado["nivel_riesgo"], "critico")

    def test_sobre_el_limite_no_cumple_y_dice_que_hacer_primero(self):
        resultado = mineria.evaluar_exposicion("Silice cristalizada - cuarzo", 0.05, "mg/m3",
                                               horas_diarias=12, presion_mmhg=475, altitud_m=3800)
        self.assertEqual(resultado["estado"], "no cumple")
        self.assertEqual(resultado["nivel_riesgo"], "critico")
        self.assertAlmostEqual(resultado["porcentaje_del_limite"], 198.4, places=1)
        self.assertTrue(resultado["acciones_inmediatas"][0].startswith("REDUCE LA EXPOSICION"))

    def test_techo_del_articulo_60(self):
        # 5 veces el LPP de 44 ppm son 220 ppm: por encima es critico siempre.
        resultado = mineria.evaluar_exposicion("Monoxido de carbono", 260, "ppm", horas_diarias=8)
        self.assertEqual(resultado["nivel_riesgo"], "critico")
        self.assertEqual(resultado["techo_art_60"], 220.0)
        self.assertIn("SACA A LA GENTE", resultado["acciones_inmediatas"][0])

    def test_no_declara_cumplimiento_si_falta_la_presion_en_altura(self):
        resultado = mineria.evaluar_exposicion("Silice cristalizada - cuarzo", 0.01, "mg/m3",
                                               horas_diarias=12, altitud_m=3800)
        self.assertEqual(resultado["estado"], "sin_evaluar")
        self.assertIsNone(resultado["limite_corregido"])
        self.assertTrue(resultado["no_calculado"])

    def test_no_inventa_el_limite_absoluto_del_articulo_61(self):
        resultado = mineria.evaluar_exposicion("Monoxido de carbono", 100, "ppm", tipo="absoluto",
                                               horas_diarias=8)
        self.assertTrue(any("art. 61" in a for a in resultado["advertencias"]))
        self.assertIn("techo del art. 60", resultado["referencia"])

    def test_avisa_que_el_agente_es_cancerigeno(self):
        resultado = mineria.evaluar_exposicion("Benceno", 0.1, "ppm", horas_diarias=8)
        self.assertEqual(resultado["estado"], "cumple")
        self.assertTrue(any("cancerigeno comprobado" in a for a in resultado["advertencias"]))


class PruebaVentilacion(unittest.TestCase):
    def test_ejemplo_resuelto_de_la_investigacion(self):
        # M2: 12 personas y 2 LHD de 300 HP -> 36 + 1.698 = 1.734 m3/min
        resultado = mineria.evaluar_ventilacion(personas=12, hp_diesel=600, caudal_m3min=1734,
                                                oxigeno_pct=20.9, velocidad_m_min=86.7)
        self.assertEqual(resultado["caudal"]["caudal_por_personas_m3min"], 36.0)
        self.assertEqual(resultado["caudal"]["caudal_por_diesel_m3min"], 1698.0)
        self.assertEqual(resultado["caudal"]["caudal_exigido_m3min"], 1734.0)
        self.assertTrue(resultado["cumple"])
        self.assertEqual(resultado["nivel_riesgo"], "conforme")

    def test_los_caudales_se_suman_no_se_elige_el_mayor(self):
        resultado = mineria.evaluar_ventilacion(personas=20, hp_diesel=300, caudal_m3min=900,
                                                oxigeno_pct=20.5)
        self.assertEqual(resultado["caudal"]["caudal_exigido_m3min"], 909.0)   # 60 + 849
        self.assertFalse(resultado["cumple"])
        self.assertEqual(resultado["nivel_riesgo"], "critico")
        self.assertIn("AUMENTA LA VENTILACION", resultado["acciones_inmediatas"][0])

    def test_oxigeno_justo_en_el_minimo_y_bajo_el_minimo(self):
        justo = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=19.5)
        self.assertEqual(justo["cumple_por_tema"]["Oxigeno"], "conforme")
        bajo = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=19.4)
        self.assertEqual(bajo["cumple_por_tema"]["Oxigeno"], "critico")
        self.assertTrue(bajo["acciones_inmediatas"][0].startswith("EVACUAR AHORA"))

    def test_velocidad_en_los_bordes_del_articulo_138(self):
        for velocidad in (15, 150):
            resultado = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9,
                                                    velocidad_m_min=velocidad)
            self.assertEqual(resultado["cumple_por_tema"]["Velocidad media del aire"], "conforme")
        for velocidad in (14, 151):
            resultado = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9,
                                                    velocidad_m_min=velocidad)
            self.assertEqual(resultado["cumple_por_tema"]["Velocidad media del aire"], "alerta")

    def test_gases_que_obligan_a_detener_el_equipo_diesel(self):
        resultado = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9,
                                                co_ppm=40, nox_ppm=19, aldehido_ppm=1.6)
        temas = resultado["cumple_por_tema"]
        self.assertEqual(temas["Gas ambiental: monoxido de carbono (CO)"], "critico")
        self.assertEqual(temas["Gas ambiental: oxidos de nitrogeno (NOx)"], "conforme")
        self.assertEqual(temas["Gas ambiental: aldehido formico (formaldehido)"], "critico")
        self.assertTrue(any("DETENER EL EQUIPO DIESEL" in a for a in resultado["acciones_inmediatas"]))

    def test_gases_en_el_escape(self):
        resultado = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9,
                                                co_escape_ppm=2000, nox_escape_ppm=1001)
        temas = resultado["cumple_por_tema"]
        self.assertEqual(temas["Gas en el escape: monoxido de carbono (CO) en el escape"], "conforme")
        self.assertEqual(temas["Gas en el escape: oxidos de nitrogeno (NOx) en el escape"], "critico")

    def test_el_co2_se_evalua_con_el_ds_594(self):
        resultado = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9,
                                                co2_ppm=5000)
        self.assertEqual(resultado["cumple_por_tema"]["Anhidrido carbonico (CO2)"], "alerta")
        critico = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9,
                                              co2_ppm=31000)
        self.assertEqual(critico["cumple_por_tema"]["Anhidrido carbonico (CO2)"], "critico")

    def test_usa_el_caudal_del_fabricante_cuando_existe(self):
        resultado = mineria.evaluar_ventilacion(personas=10, hp_diesel=300, caudal_m3min=1000,
                                                oxigeno_pct=20.9, caudal_diesel_fabricante=700)
        self.assertEqual(resultado["caudal"]["caudal_exigido_m3min"], 730.0)   # 30 + 700
        self.assertIn("fabricante", resultado["caudal"]["origen_caudal_diesel"])

    def test_sin_personas_no_calcula(self):
        with self.assertRaises(Problema):
            mineria.evaluar_ventilacion(hp_diesel=300, caudal_m3min=900)

    def test_no_insinua_niveles_tipo_tarp(self):
        resultado = mineria.evaluar_ventilacion(personas=5, caudal_m3min=100, oxigeno_pct=20.9)
        self.assertTrue(any("TARP" in a for a in resultado["advertencias"]))
        self.assertIn("no", resultado["advertencias"][0].lower())


class PruebaRelaves(unittest.TestCase):
    def test_revancha_justo_en_un_metro_cumple(self):
        resultado = mineria.evaluar_relave(revancha_m=1.0, factor_seguridad=1.2, metodo="aguas_abajo")
        niveles = {h["tema"]: h["nivel"] for h in resultado["hallazgos"]}
        self.assertEqual(niveles["Revancha"], "conforme")
        self.assertEqual(niveles["Factor de seguridad (I)"], "conforme")
        self.assertEqual(resultado["nivel_riesgo"], "conforme")

    def test_revancha_bajo_el_minimo_es_critica(self):
        resultado = mineria.evaluar_relave(revancha_m=0.99, factor_seguridad=1.5, metodo="eje_central")
        self.assertEqual(resultado["nivel_riesgo"], "critico")
        self.assertIn("ACCION INMEDIATA", resultado["acciones_inmediatas"][0])

    def test_revancha_bajo_el_diseno_pero_sobre_el_minimo_es_alerta(self):
        resultado = mineria.evaluar_relave(revancha_m=1.2, revancha_diseno_m=2.0, factor_seguridad=1.3,
                                           metodo="aguas_abajo")
        niveles = {h["tema"]: h["nivel"] for h in resultado["hallazgos"]}
        self.assertEqual(niveles["Revancha"], "alerta")
        self.assertEqual(resultado["nivel_riesgo"], "alerta")

    def test_factor_de_seguridad_justo_en_uno_coma_dos(self):
        cumple = mineria.evaluar_relave(factor_seguridad=1.2, fase="ii", metodo="aguas_abajo")
        no_cumple = mineria.evaluar_relave(factor_seguridad=1.19, fase="ii", metodo="aguas_abajo")
        self.assertEqual({h["tema"]: h["nivel"] for h in cumple["hallazgos"]}["Factor de seguridad (II)"],
                         "conforme")
        self.assertEqual(no_cumple["nivel_riesgo"], "critico")

    def test_el_metodo_aguas_arriba_esta_prohibido(self):
        resultado = mineria.evaluar_relave(revancha_m=3.0, factor_seguridad=1.8, metodo="upstream")
        self.assertEqual(resultado["nivel_riesgo"], "critico")
        self.assertIn("PROHIBIDO", resultado["acciones_inmediatas"][0])
        self.assertIn("14 letra h", resultado["hallazgos"][0]["articulo"])

    def test_no_inventa_factor_de_seguridad_para_las_fases_iii_y_iv(self):
        for fase in ("iii", "iv"):
            resultado = mineria.evaluar_relave(factor_seguridad=1.05, fase=fase, metodo="aguas_abajo")
            hallazgo = [h for h in resultado["hallazgos"] if h["tema"].startswith("Factor de seguridad")][0]
            self.assertEqual(hallazgo["nivel"], "sin_evaluar")
            self.assertIn("No invento un valor", hallazgo["explicacion"])

    def test_no_asume_un_factor_estatico_de_uno_coma_cuatro(self):
        resultado = mineria.evaluar_relave(factor_seguridad=1.3, fase="estatico", metodo="aguas_abajo")
        texto = " ".join(resultado["no_verificado"])
        self.assertIn("1,4", texto)
        self.assertIn("No lo trates como exigencia chilena", texto)

    def test_exigencia_de_la_fase_iii_por_altura_del_muro(self):
        alto = mineria.evaluar_relave(factor_seguridad=1.5, altura_muro_m=15, metodo="aguas_abajo")
        bajo = mineria.evaluar_relave(factor_seguridad=1.5, altura_muro_m=14.9, metodo="aguas_abajo")
        self.assertTrue(alto["exige_fase_iii"])
        self.assertFalse(bajo["exige_fase_iii"])

    def test_muro_de_partida_del_articulo_54(self):
        alto = mineria.evaluar_relave(altura_final_muro_m=30, altura_muro_partida_m=3.0,
                                      metodo="aguas_abajo")
        niveles = {h["tema"]: h["nivel"] for h in alto["hallazgos"]}
        self.assertEqual(niveles["Muro de partida"], "conforme")     # 10 % de 30 m = 3 m
        bajo = mineria.evaluar_relave(altura_final_muro_m=15, altura_muro_partida_m=1.9,
                                      metodo="aguas_abajo")
        hallazgo = [h for h in bajo["hallazgos"] if h["tema"] == "Muro de partida"][0]
        self.assertEqual(hallazgo["nivel"], "critico")
        self.assertEqual(hallazgo["exigido"], "2 m")                 # piso de 2 m, no 1,5 m

    def test_metodo_desconocido(self):
        with self.assertRaises(Problema):
            mineria.evaluar_relave(revancha_m=2.0, metodo="aguas_al_lado")


class PruebaGistm(unittest.TestCase):
    def test_porcentaje_sobre_los_77_requisitos(self):
        resultado = mineria.evaluar_gistm(clasificacion="alta", requisitos_conformes=60)
        self.assertEqual(resultado["total_requisitos"], 77)
        self.assertEqual(resultado["requisitos_pendientes"], 17)
        self.assertEqual(resultado["porcentaje_conformidad"], 77.9)

    def test_criterios_de_diseno_y_plazo_por_clasificacion(self):
        extrema = mineria.evaluar_gistm(clasificacion="extrema", requisitos_conformes=77)
        self.assertEqual(extrema["criterios_diseno"]["sismico_operacion_y_cierre"], "1/10.000")
        self.assertEqual(extrema["plazo_conformidad_icmm"], "2023-08-05")
        self.assertEqual(extrema["porcentaje_conformidad"], 100.0)
        baja = mineria.evaluar_gistm(clasificacion="baja", requisitos_conformes=10)
        self.assertEqual(baja["criterios_diseno"]["crecidas_operacion_y_cierre"], "1/200")
        self.assertEqual(baja["criterios_diseno"]["crecidas_poscierre"], "1/10.000")
        self.assertEqual(baja["plazo_conformidad_icmm"], "2025-08-05")

    def test_clasificacion_sugerida_por_poblacion_en_riesgo(self):
        self.assertEqual(mineria.clasificar_por_poblacion(0)[0], "baja")
        self.assertEqual(mineria.clasificar_por_poblacion(5)[0], "significativa")
        self.assertEqual(mineria.clasificar_por_poblacion(10)[0], "alta")      # borde: la clase mas alta
        self.assertEqual(mineria.clasificar_por_poblacion(100)[0], "alta")
        self.assertEqual(mineria.clasificar_por_poblacion(1000)[0], "muy alta")
        self.assertEqual(mineria.clasificar_por_poblacion(1001)[0], "extrema")

    def test_avisa_que_no_existe_certificacion_de_terceros(self):
        resultado = mineria.evaluar_gistm(clasificacion="muy alta", requisitos_conformes=70)
        texto = " ".join(resultado["advertencias"])
        self.assertIn("no existe un esquema de certificacion GISTM", texto)
        self.assertIn("NO es ley en Chile", texto)

    def test_rechaza_datos_fuera_de_rango(self):
        with self.assertRaises(Problema):
            mineria.evaluar_gistm(clasificacion="alta", requisitos_conformes=78)
        with self.assertRaises(Problema):
            mineria.evaluar_gistm(clasificacion="gravisima")
        with self.assertRaises(Problema):
            mineria.evaluar_gistm(clasificacion="alta", principios_cubiertos=[16])


class PruebaCierre(unittest.TestCase):
    def test_regimenes_por_toneladas(self):
        self.assertEqual(mineria.regimen_cierre(10001)[0], "general")
        self.assertEqual(mineria.regimen_cierre(10000)[0], "simplificado")
        self.assertEqual(mineria.regimen_cierre(5000)[0], "declaracion_simplificada")
        self.assertEqual(mineria.regimen_cierre(5000, tiene_relaves=True)[0], "simplificado")
        self.assertEqual(mineria.regimen_cierre(5000, tiene_planta=True)[0], "simplificado")

    def test_garantia_solo_en_el_regimen_general(self):
        general = mineria.plan_cierre(toneladas_mes=15000, vida_util_anios=12)
        self.assertTrue(general["garantia"]["exige"])
        self.assertAlmostEqual(general["garantia"]["plazo_constitucion_anios"], 8.0, places=2)
        self.assertIn("BCU", general["garantia"]["tasa_descuento"])
        simple = mineria.plan_cierre(toneladas_mes=3000)
        self.assertFalse(simple["garantia"]["exige"])

    def test_plazo_de_constitucion_para_vida_util_larga(self):
        largo = mineria.plan_cierre(toneladas_mes=20000, vida_util_anios=25)
        self.assertEqual(largo["garantia"]["plazo_constitucion_anios"], 15.0)

    def test_no_calcula_las_parcialidades_no_verificadas(self):
        general = mineria.plan_cierre(toneladas_mes=15000, vida_util_anios=12)
        self.assertIn("No calculo el monto de cada parcialidad", general["garantia"]["no_calcula"])
        self.assertTrue(any("DS 15/2026" in n for n in general["no_verificado"]))

    def test_contenido_minimo_segun_el_regimen(self):
        general = mineria.plan_cierre(toneladas_mes=15000)
        simple = mineria.plan_cierre(toneladas_mes=8000)
        self.assertEqual(len(general["contenido_minimo"]), 10)
        self.assertEqual([c["letra"] for c in simple["contenido_minimo"]], ["a", "b", "e"])

    def test_sin_toneladas_no_calcula(self):
        with self.assertRaises(Problema):
            mineria.plan_cierre()


class PruebaModuloMineria(PruebaConCarpeta):
    def setUp(self):
        super(PruebaModuloMineria, self).setUp()
        from modulos import mineria as modulo
        self.modulo = modulo
        espacio.crear_empresa({"nombre": "Minera Prueba SpA", "pais": "CL", "sector": "Mineria",
                               "tamano": "grande", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Minera Prueba SpA"}

    def test_acciones_declaradas(self):
        self.assertEqual(sorted(self.modulo.ACCIONES),
                         ["cierre", "exposicion", "gistm", "informe", "relaves", "ventilacion"])

    def test_ventilacion_desde_la_linea_de_comandos(self):
        respuesta = self.modulo.ventilacion({"personas": "20", "hp_diesel": "300",
                                             "oxigeno": "20.5", "caudal": "900"})
        self.assertEqual(respuesta.resultado["caudal"]["caudal_exigido_m3min"], 909.0)
        self.assertTrue(respuesta.resultado["mensaje"].startswith("AUMENTA LA VENTILACION"))
        self.assertTrue(any("NO reemplaza" in a for a in respuesta.advertencias))

    def test_exposicion_sin_agente_ofrece_el_catalogo(self):
        respuesta = self.modulo.exposicion({})
        self.assertIn("agentes", respuesta.resultado)
        self.assertTrue(any(a["agente"].startswith("Silice") for a in respuesta.resultado["agentes"]))

    def test_informe_html(self):
        respuesta = self.modulo.informe_html(dict(self.opciones, personas="20", hp_diesel="300",
                                                  oxigeno="19.2", caudal="900", revancha="0.5",
                                                  factor_seguridad="1.1", metodo="aguas_arriba",
                                                  agente="Silice cristalizada - cuarzo",
                                                  concentracion="0.05", unidad="mg/m3", horas="12",
                                                  presion="475", altitud="3800",
                                                  toneladas_mes="15000", vida_util="12",
                                                  clasificacion="muy alta", requisitos="60"))
        archivo = respuesta.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("EVACUAR AHORA", html)
        self.assertIn("DS 248/2007", html)
        self.assertIn("77 requisitos", html)
        self.assertEqual(len(respuesta.resultado["secciones"]), 5)

    def test_informe_sin_datos_avisa_en_vez_de_inventar(self):
        with self.assertRaises(Problema):
            self.modulo.informe_html(dict(self.opciones))


if __name__ == "__main__":
    unittest.main()
