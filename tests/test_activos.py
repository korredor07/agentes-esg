# -*- coding: utf-8 -*-
"""Pruebas de activos fijos: vida util del SII, depreciacion y correccion monetaria.

Los valores esperados vienen de la investigacion normativa
(docs/investigacion/09-finanzas-logistica-frio.md, seccion SII):

  - tabla de vida util de la Res. Ex. SII N 43 de 26.12.2002 y de la
    Res. Ex. SII N 56 de 09.06.2021,
  - reglas de los arts. 31 N 5, 31 N 5 bis, 14 D) N 3 y 41 de la Ley de la Renta,
  - factores de correccion monetaria del ejercicio 2025 (Circular SII N 5 de 2026),

y de ejemplos numericos resueltos a mano que se explican en cada prueba.
"""

import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import activos  # noqa: E402
from nucleo import espacio, excel  # noqa: E402
from nucleo.salida import Problema  # noqa: E402


class PruebaTablaVidaUtil(unittest.TestCase):
    """La tabla cargada tiene que ser identica a la del SII."""

    @classmethod
    def setUpClass(cls):
        cls.tabla = activos.cargar_tabla()
        cls.por_codigo = {b["codigo"]: b for b in cls.tabla}

    def test_cada_fila_trae_su_fuente(self):
        for bien in self.tabla:
            self.assertTrue(bien["codigo"], bien)
            self.assertTrue(bien["resolucion"], bien["bien"])
            self.assertTrue(bien["fuente"], bien["bien"])
            self.assertTrue(bien["verificado_el"], bien["bien"])
            self.assertIn(bien["actividad"], ("generico", "agricola"))

    def test_la_acelerada_de_la_tabla_es_un_tercio(self):
        """La columna acelerada del SII es max(1, parte entera de normal/3)."""
        for bien in self.tabla:
            normal = bien["vida_util_normal"]
            if normal is None:
                continue
            self.assertEqual(bien["vida_util_acelerada"], max(1, normal // 3),
                             "%s (%s)" % (bien["bien"], bien["codigo"]))

    def test_valores_conocidos_de_la_resolucion_43(self):
        esperado = {
            "sii-gen-01": (80, 26), "sii-gen-02": (50, 16), "sii-gen-05": (20, 6),
            "sii-gen-10": (7, 2), "sii-gen-15": (15, 5), "sii-gen-16": (9, 3),
            "sii-gen-17": (10, 3), "sii-gen-19": (3, 1), "sii-gen-23": (6, 2),
        }
        for codigo, (normal, acelerada) in esperado.items():
            bien = self.por_codigo[codigo]
            self.assertEqual((bien["vida_util_normal"], bien["vida_util_acelerada"]),
                             (normal, acelerada), codigo)

    def test_vehiculos_electricos_de_la_resolucion_56(self):
        electrico = self.por_codigo["sii-gen-30"]
        self.assertEqual((electrico["vida_util_normal"], electrico["vida_util_acelerada"]), (3, 1))
        self.assertIn("56", electrico["resolucion"])
        self.assertIn("2031", electrico["notas"])

    def test_los_vinedos_quedan_sin_numero_unico(self):
        """La tabla fija entre 11 y 23 anios segun la variedad: no se inventa uno."""
        vinedos = self.por_codigo["sii-agr-13"]
        self.assertIsNone(vinedos["vida_util_normal"])
        self.assertTrue(vinedos["requiere_confirmacion"])
        self.assertIn("contador", vinedos["notas"])

    def test_no_carga_nominas_sin_verificar(self):
        """Mineria, construccion y transporte quedaron con lectura parcial: no van."""
        actividades = {bien["actividad"] for bien in self.tabla}
        self.assertEqual(actividades, {"generico", "agricola"})
        for pendiente in ("mineria", "construccion", "telecomunicaciones"):
            self.assertIn(pendiente, activos.AVISO_NOMINAS)


class PruebaBusqueda(unittest.TestCase):
    """Buscar el bien como lo escribe una persona, no como lo escribe el SII."""

    def test_camioneta(self):
        resultado = activos.buscar_vida_util("camioneta")
        self.assertTrue(resultado["encontrado"])
        elegido = resultado["eleccion_unica"]
        self.assertEqual(elegido["codigo"], "sii-gen-10")
        self.assertEqual(elegido["vida_util_normal"], 7)
        self.assertIn("43", elegido["resolucion"])

    def test_computador_y_notebook_llegan_al_mismo_item(self):
        for consulta in ("computador", "notebook", "computadores"):
            elegido = activos.buscar_vida_util(consulta)["eleccion_unica"]
            self.assertEqual(elegido["codigo"], "sii-gen-23", consulta)
            self.assertEqual(elegido["vida_util_normal"], 6)

    def test_galpon_y_camara_de_frio(self):
        self.assertEqual(activos.buscar_vida_util("galpon")["eleccion_unica"]["vida_util_normal"], 20)
        self.assertEqual(activos.buscar_vida_util("camara de frio")["eleccion_unica"]["codigo"],
                         "sii-gen-17")

    def test_varias_opciones_para_elegir(self):
        """Herramientas pesadas o livianas: el motor no elige por la persona."""
        resultado = activos.buscar_vida_util("herramientas")
        codigos = [c["codigo"] for c in resultado["coincidencias"]]
        self.assertIn("sii-gen-18", codigos)
        self.assertIn("sii-gen-19", codigos)
        self.assertIsNone(resultado["eleccion_unica"])
        self.assertIn("opciones", resultado["mensaje"])

    def test_filtrar_por_actividad_agricola(self):
        resultado = activos.buscar_vida_util("camioneta", actividad="agricultura")
        self.assertEqual(resultado["actividad"], "agricola")
        self.assertEqual(resultado["eleccion_unica"]["codigo"], "sii-agr-06")
        self.assertEqual(resultado["eleccion_unica"]["vida_util_normal"], 6)

    def test_cuando_no_encuentra_lo_dice(self):
        resultado = activos.buscar_vida_util("panel solar fotovoltaico")
        self.assertFalse(resultado["encontrado"])
        self.assertEqual(resultado["coincidencias"], [])
        self.assertIn("contador", resultado["mensaje"])
        self.assertIn("camioneta", resultado["ejemplos"])

    def test_terreno_no_se_deprecia(self):
        resultado = activos.buscar_vida_util("terreno de la planta")
        self.assertFalse(resultado["se_deprecia"])
        self.assertIn("no se deprecian", resultado["mensaje"])
        self.assertIn("31 N 5", resultado["no_se_deprecia"]["fuente"])

    def test_software_no_se_deprecia(self):
        resultado = activos.buscar_vida_util("software de gestion")
        self.assertFalse(resultado["se_deprecia"])
        self.assertIn("intangibles", resultado["no_se_deprecia"]["titulo"])

    def test_actividad_no_cargada(self):
        with self.assertRaises(Problema) as contexto:
            activos.buscar_vida_util("chancadora", actividad="mineria")
        self.assertIn("mineria", contexto.exception.mensaje)

    def test_consulta_vacia(self):
        with self.assertRaises(Problema):
            activos.buscar_vida_util("")


class PruebaVidasUtilesTributarias(unittest.TestCase):
    """Formulas de los arts. 31 N 5 y 31 N 5 bis."""

    def test_acelerada_es_un_tercio_truncado(self):
        # 80/3 = 26,67 -> 26; 50/3 = 16,67 -> 16; 7/3 = 2,33 -> 2; 3/3 = 1.
        for normal, esperado in ((80, 26), (50, 16), (20, 6), (15, 5), (7, 2), (6, 2), (3, 1)):
            resultado = activos.vida_util_acelerada(normal)
            self.assertTrue(resultado["aplica"])
            self.assertEqual(resultado["anios"], esperado, normal)

    def test_acelerada_no_corre_bajo_tres_anios(self):
        resultado = activos.vida_util_acelerada(2)
        self.assertFalse(resultado["aplica"])
        self.assertIsNone(resultado["anios"])
        self.assertIn("3 anios", resultado["motivo"])

    def test_cinco_bis_un_decimo(self):
        # 15/10 = 1,5 -> 1; 20/10 = 2; 50/10 = 5; 80/10 = 8; 7/10 = 0,7 -> minimo 1.
        for normal, esperado in ((15, 1), (20, 2), (50, 5), (80, 8), (7, 1)):
            resultado = activos.vida_util_5_bis(normal, 90000)
            self.assertTrue(resultado["aplica"])
            self.assertEqual(resultado["anios"], esperado, normal)
            self.assertEqual(resultado["bienes"], "nuevos o importados")

    def test_cinco_bis_hasta_25000_uf_es_un_anio(self):
        resultado = activos.vida_util_5_bis(80, 24000)
        self.assertEqual(resultado["anios"], 1)
        self.assertEqual(resultado["bienes"], "nuevos o usados")

    def test_cinco_bis_no_aplica_sobre_100000_uf(self):
        resultado = activos.vida_util_5_bis(15, 150000)
        self.assertFalse(resultado["aplica"])
        self.assertIn("100.000 UF", resultado["motivo"])

    def test_vida_util_invalida(self):
        with self.assertRaises(Problema):
            activos.vida_util_acelerada(0)


class PruebaDepreciacion(unittest.TestCase):
    """Ejemplos resueltos a mano."""

    def test_normal_siete_anios(self):
        # (7.000.001 - 1) / 7 = 1.000.000 por anio, desde enero de 2024.
        resultado = activos.depreciacion(7000001, 7, anio_inicio=2024)
        self.assertEqual(resultado["vida_util_aplicada"], 7)
        self.assertAlmostEqual(resultado["cuota_anual"], 1000000.0, places=2)
        self.assertEqual(len(resultado["tabla"]), 7)
        self.assertEqual(resultado["tabla"][0]["anio"], 2024)
        self.assertAlmostEqual(resultado["tabla"][0]["valor_libro"], 6000001.0, places=2)
        self.assertAlmostEqual(resultado["tabla"][-1]["valor_libro"], 1.0, places=2)
        self.assertAlmostEqual(resultado["total_depreciado"], 7000000.0, places=2)
        self.assertIn("31 N 5", resultado["articulo"])

    def test_primer_ejercicio_proporcional_a_los_meses(self):
        # Puesto en uso en abril: 9 meses de uso al 31.12 -> 1.000.000 x 9/12 = 750.000.
        resultado = activos.depreciacion(7000001, 7, anio_inicio=2024, mes_inicio=4)
        self.assertEqual(resultado["meses_primer_ejercicio"], 9)
        self.assertAlmostEqual(resultado["tabla"][0]["cuota"], 750000.0, places=2)
        self.assertEqual(len(resultado["tabla"]), 8)
        self.assertAlmostEqual(resultado["tabla"][-1]["cuota"], 250000.0, places=2)
        self.assertAlmostEqual(resultado["tabla"][-1]["valor_libro"], 1.0, places=2)

    def test_acelerada_de_una_camioneta(self):
        # Vida normal 7 -> acelerada 2 anios; (14.000.001 - 1) / 2 = 7.000.000.
        resultado = activos.depreciacion(14000001, 7, metodo="acelerada")
        self.assertEqual(resultado["vida_util_aplicada"], 2)
        self.assertAlmostEqual(resultado["cuota_anual"], 7000000.0, places=2)
        self.assertEqual(len(resultado["tabla"]), 2)
        self.assertTrue(any("nuevo" in a for a in resultado["advertencias"]))

    def test_acelerada_no_disponible_avisa(self):
        with self.assertRaises(Problema) as contexto:
            activos.depreciacion(1000000, 2, metodo="acelerada")
        self.assertIn("3 anios", contexto.exception.mensaje)
        self.assertIn("normal", contexto.exception.sugerencia)

    def test_cinco_bis_necesita_los_ingresos(self):
        resultado = activos.depreciacion(5000001, 50, metodo="5_bis", ingresos_uf=90000)
        self.assertEqual(resultado["vida_util_aplicada"], 5)
        self.assertAlmostEqual(resultado["cuota_anual"], 1000000.0, places=2)
        with self.assertRaises(Problema):
            activos.depreciacion(5000001, 50, metodo="5_bis")

    def test_propyme_deprecia_todo_en_un_ejercicio(self):
        resultado = activos.depreciacion(5000000, 15, metodo="propyme", anio_inicio=2025)
        self.assertEqual(len(resultado["tabla"]), 1)
        self.assertAlmostEqual(resultado["tabla"][0]["cuota"], 5000000.0, places=2)
        self.assertAlmostEqual(resultado["tabla"][0]["valor_libro"], 0.0, places=2)
        self.assertTrue(any("pagado" in a for a in resultado["advertencias"]))
        self.assertTrue(any("correccion monetaria" in a for a in resultado["advertencias"]))

    def test_valor_residual_de_un_peso_con_su_aviso(self):
        resultado = activos.depreciacion(1000001, 10)
        self.assertAlmostEqual(resultado["valor_residual"], 1.0, places=2)
        self.assertTrue(any("$1" in a for a in resultado["advertencias"]))

    def test_valores_invalidos(self):
        with self.assertRaises(Problema):
            activos.depreciacion(0, 7)
        with self.assertRaises(Problema):
            activos.depreciacion(1000000, 0)
        with self.assertRaises(Problema):
            activos.depreciacion(1000000, 7, metodo="degresiva")
        with self.assertRaises(Problema):
            activos.depreciacion(1000, 7, valor_residual=5000)

    def test_lee_numeros_escritos_a_la_chilena(self):
        self.assertAlmostEqual(activos.numero("12.000.000"), 12000000.0)
        self.assertAlmostEqual(activos.numero("$ 1.234.567"), 1234567.0)
        self.assertAlmostEqual(activos.numero("1.234,56"), 1234.56)
        with self.assertRaises(Problema):
            activos.numero("bastante")


class PruebaCorreccionMonetaria(unittest.TestCase):
    """Factores oficiales del ejercicio 2025 (Circular SII N 5 de 21.01.2026)."""

    def test_bien_existente_al_inicio_del_ejercicio(self):
        # Reajuste del capital propio inicial 2025: 3,4 %. 10.000.000 x 1,034.
        resultado = activos.correccion_monetaria(10000000, 2025)
        self.assertAlmostEqual(resultado["porcentaje"], 3.4, places=4)
        self.assertAlmostEqual(resultado["valor_actualizado"], 10340000.0, places=2)
        self.assertAlmostEqual(resultado["mayor_valor"], 340000.0, places=2)
        self.assertIn("30 de noviembre", resultado["regla"])
        self.assertIn("41", resultado["articulo"])

    def test_bien_comprado_durante_el_ejercicio(self):
        # Compra de marzo 2025: factor 1,022. 5.000.000 x 1,022 = 5.110.000.
        resultado = activos.correccion_monetaria(5000000, 2025, mes_adquisicion=3, anio_adquisicion=2025)
        self.assertAlmostEqual(resultado["factor"], 1.022, places=6)
        self.assertAlmostEqual(resultado["valor_actualizado"], 5110000.0, places=2)
        self.assertTrue(resultado["comprado_en_el_ejercicio"])

    def test_compra_de_diciembre_no_se_reajusta(self):
        resultado = activos.correccion_monetaria(5000000, 2025, mes_adquisicion="diciembre",
                                                 anio_adquisicion=2025)
        self.assertAlmostEqual(resultado["factor"], 1.0, places=6)
        self.assertAlmostEqual(resultado["valor_actualizado"], 5000000.0, places=2)

    def test_porcentaje_negativo_se_iguala_a_cero(self):
        resultado = activos.correccion_monetaria(1000000, 2025, porcentaje=-2.5)
        self.assertEqual(resultado["porcentaje"], 0.0)
        self.assertAlmostEqual(resultado["valor_actualizado"], 1000000.0, places=2)
        self.assertTrue(any("negativo" in a for a in resultado["advertencias"]))

    def test_sin_factores_verificados_pide_el_dato(self):
        with self.assertRaises(Problema) as contexto:
            activos.correccion_monetaria(1000000, 2027)
        self.assertIn("2027", contexto.exception.mensaje)
        self.assertIn("contador", contexto.exception.sugerencia)
        self.assertIn("--porcentaje", contexto.exception.sugerencia)

    def test_compra_en_el_ejercicio_sin_mes(self):
        with self.assertRaises(Problema) as contexto:
            activos.correccion_monetaria(1000000, 2025, anio_adquisicion=2025)
        self.assertIn("mes", contexto.exception.mensaje)

    def test_compra_posterior_al_ejercicio(self):
        with self.assertRaises(Problema):
            activos.correccion_monetaria(1000000, 2025, mes_adquisicion=3, anio_adquisicion=2026)

    def test_termino_de_giro_2026(self):
        resultado = activos.porcentaje_termino_giro(2026, 4)
        self.assertAlmostEqual(resultado["porcentaje"], 1.3, places=4)
        with self.assertRaises(Problema) as contexto:
            activos.porcentaje_termino_giro(2026, 10)
        self.assertIn("SII", contexto.exception.sugerencia)


class PruebaPrimeroActualizarDespuesDepreciar(unittest.TestCase):
    """Hallazgo de la prueba E2E: la cuota se calculaba sobre el valor historico.

    Reproduce los dos ejemplos resueltos de docs/investigacion/09, seccion 8.3.
    """

    def test_bien_existente_al_inicio_del_ejercicio(self):
        tabla = activos.depreciacion(32000000, 15, anio_inicio=2023, mes_inicio=1, valor_residual=0)
        correccion = activos.correccion_monetaria(32000000, 2025, porcentaje=3.4)
        rehecha = activos.depreciar_con_correccion(tabla, correccion)
        fila = [f for f in rehecha["tabla"] if f["anio"] == 2025][0]
        self.assertAlmostEqual(fila["cuota"], 2205867, delta=1)
        self.assertAlmostEqual(fila["valor_libro"], 26470399, delta=2)
        self.assertEqual(rehecha["valor_actualizado"], 33088000)

    def test_bien_comprado_durante_el_ejercicio(self):
        tabla = activos.depreciacion(5000000, 15, anio_inicio=2025, mes_inicio=7, valor_residual=0)
        correccion = activos.correccion_monetaria(5000000, 2025, mes_adquisicion=7, anio_adquisicion=2025)
        rehecha = activos.depreciar_con_correccion(tabla, correccion)
        self.assertAlmostEqual(rehecha["tabla"][0]["cuota"], 169500, delta=0.5)

    def test_los_ejercicios_anteriores_no_se_tocan(self):
        tabla = activos.depreciacion(32000000, 15, anio_inicio=2023, mes_inicio=1, valor_residual=0)
        correccion = activos.correccion_monetaria(32000000, 2025, porcentaje=3.4)
        rehecha = activos.depreciar_con_correccion(tabla, correccion)
        self.assertEqual(rehecha["tabla"][0], tabla["tabla"][0])
        self.assertEqual(rehecha["tabla"][1], tabla["tabla"][1])

    def test_avisa_que_los_anios_siguientes_necesitan_su_factor(self):
        tabla = activos.depreciacion(32000000, 7, anio_inicio=2025, mes_inicio=3)
        correccion = activos.correccion_monetaria(32000000, 2025, mes_adquisicion=3, anio_adquisicion=2025)
        rehecha = activos.depreciar_con_correccion(tabla, correccion)
        self.assertTrue(any("cada año hay que volver a actualizarlos" in a for a in rehecha["advertencias"]))
        self.assertFalse(any(a.startswith("Esta tabla esta en pesos") for a in rehecha["advertencias"]))

    def test_ejercicio_fuera_de_la_tabla_no_cambia_nada(self):
        tabla = activos.depreciacion(1000000, 3, anio_inicio=2019, mes_inicio=1)
        correccion = activos.correccion_monetaria(1000000, 2025, porcentaje=3.4)
        rehecha = activos.depreciar_con_correccion(tabla, correccion)
        self.assertEqual(rehecha["tabla"], tabla["tabla"])


class PruebaCartera(unittest.TestCase):
    """Totales de la cartera para un ejercicio, resueltos a mano."""

    CARTERA = [
        {"nombre": "Camioneta", "bien": "camioneta", "categoria": "flota",
         "valor": 7000001, "fecha_compra": "2024-01-15", "metodo": "normal"},
        {"nombre": "Computador", "bien": "computador", "categoria": "oficina",
         "valor": 6000001, "fecha_compra": "2025-07-01", "metodo": "normal"},
    ]

    def setUp(self):
        self.resultado = activos.resumen_cartera(self.CARTERA, anio=2025)

    def test_totales_del_ejercicio(self):
        # Camioneta: 1.000.000 al anio desde enero 2024 -> 2025 acumula 2.000.000.
        # Computador: 1.000.000 al anio desde julio 2025 -> 2025 solo 6 meses = 500.000.
        totales = self.resultado["totales"]
        self.assertAlmostEqual(totales["inversion"], 13000002.0, places=2)
        self.assertAlmostEqual(totales["depreciacion_del_ejercicio"], 1500000.0, places=2)
        self.assertAlmostEqual(totales["depreciacion_acumulada"], 2500000.0, places=2)
        self.assertAlmostEqual(totales["valor_libro"], 10500002.0, places=2)

    def test_detalle_por_activo(self):
        camioneta = self.resultado["activos"][0]
        self.assertEqual(camioneta["vida_util_aplicada"], 7)
        self.assertEqual(camioneta["anios_de_uso"], 2)
        self.assertEqual(camioneta["anios_restantes"], 5)
        self.assertAlmostEqual(camioneta["valor_libro"], 5000001.0, places=2)
        self.assertIn("sii-gen-10", camioneta["vida_util_segun"])

    def test_agrupa_por_categoria(self):
        categorias = {g["categoria"]: g for g in self.resultado["por_categoria"]}
        self.assertEqual(sorted(categorias), ["flota", "oficina"])
        self.assertAlmostEqual(categorias["flota"]["inversion"], 7000001.0, places=2)

    def test_marca_los_activos_por_renovar(self):
        cartera = list(self.CARTERA) + [
            {"nombre": "Camara antigua", "bien": "camara de frio", "categoria": "equipos",
             "valor": 4000000, "fecha_compra": "2010-01-01"}]
        resultado = activos.resumen_cartera(cartera, anio=2025)
        renovar = [a["activo"] for a in resultado["renovacion"]]
        self.assertIn("Camara antigua", renovar)
        self.assertTrue(resultado["renovacion"][0]["vida_util_terminada"])
        self.assertTrue(any("eficientes" in a for a in resultado["advertencias"]))

    def test_no_calcula_lo_que_no_puede_y_lo_explica(self):
        cartera = list(self.CARTERA) + [
            {"nombre": "Paneles solares", "bien": "panel solar", "valor": 9000000,
             "fecha_compra": "2024-01-01"},
            {"nombre": "Prensa sin fecha", "bien": "maquinaria", "valor": 5000000},
        ]
        resultado = activos.resumen_cartera(cartera, anio=2025)
        motivos = {p["activo"]: p["motivo"] for p in resultado["activos_con_problema"]}
        self.assertIn("Paneles solares", motivos)
        self.assertIn("Prensa sin fecha", motivos)
        self.assertIn("contador", motivos["Paneles solares"])
        self.assertEqual(resultado["cantidad"], 2)

    def test_excluye_los_dados_de_baja(self):
        cartera = list(self.CARTERA) + [
            {"nombre": "Camion vendido", "bien": "camion", "valor": 20000000,
             "fecha_compra": "2020-01-01", "estado": "vendido"}]
        resultado = activos.resumen_cartera(cartera, anio=2025)
        self.assertEqual(resultado["cantidad"], 2)

    def test_usa_la_vida_util_indicada_por_la_persona(self):
        cartera = [{"nombre": "Maquina especial", "bien": "maquinaria", "valor": 10000001,
                    "fecha_compra": "2025-01-01", "vida_util_normal": 10}]
        resultado = activos.resumen_cartera(cartera, anio=2025)
        activo = resultado["activos"][0]
        self.assertEqual(activo["vida_util_aplicada"], 10)
        self.assertEqual(activo["vida_util_segun"], "indicada por ti")
        self.assertAlmostEqual(activo["depreciacion_del_ejercicio"], 1000000.0, places=2)

    def test_cartera_vacia(self):
        with self.assertRaises(Problema):
            activos.resumen_cartera([])


class PruebaModuloActivos(PruebaConCarpeta):
    """El modulo tal como lo llama el agente."""

    FILAS = [
        ["Camioneta", "camioneta", "generico", "flota", "Planta", "2024-01-15", "", 7000001,
         "nuevo", "normal", "", "en uso", ""],
        ["Computador", "computador", "generico", "oficina", "Oficina", "2025-07-01", "", 6000001,
         "nuevo", "normal", "", "en uso", ""],
    ]

    def setUp(self):
        super(PruebaModuloActivos, self).setUp()
        from modulos import activos as modulo
        self.modulo = modulo
        perfil, self.ruta_empresa, _ = espacio.crear_empresa(
            {"nombre": "Prueba SpA", "pais": "CL", "anio_base": 2024, "tamano": "pequena"},
            raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def _escribir_planilla(self, filas=None):
        ruta = espacio.ruta_de(self.ruta_empresa, "datos", self.modulo.PLANILLA)
        excel.escribir_xlsx(ruta, [{"nombre": self.modulo.HOJA,
                                    "columnas": self.modulo.COLUMNAS,
                                    "filas": [list(f) for f in (filas or self.FILAS)]}])
        return ruta

    def test_vida_util_desde_el_modulo(self):
        respuesta = self.modulo.vida_util(dict(self.opciones, bien="camioneta"))
        self.assertEqual(respuesta.resultado["eleccion_unica"]["vida_util_normal"], 7)
        self.assertTrue(any("contador" in a for a in respuesta.advertencias))
        self.assertTrue(respuesta.fuentes)

    def test_vida_util_sin_bien(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.vida_util(dict(self.opciones))
        self.assertIn("vida-util", contexto.exception.sugerencia)

    def test_crea_la_planilla_cuando_no_existe(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.cartera(dict(self.opciones))
        ruta = espacio.ruta_de(self.ruta_empresa, "datos", self.modulo.PLANILLA)
        self.assertTrue(os.path.isfile(ruta))
        self.assertIn("acabo de crear", contexto.exception.mensaje)
        tabla = excel.leer_tabla(ruta, hoja=self.modulo.HOJA)
        self.assertIn("valor_de_compra", tabla["encabezados"])
        self.assertIn("bien_segun_la_tabla_del_sii", tabla["encabezados"])

    def test_cartera_desde_la_planilla(self):
        self._escribir_planilla()
        respuesta = self.modulo.cartera(dict(self.opciones, anio=2025))
        totales = respuesta.resultado["totales"]
        self.assertEqual(respuesta.resultado["cantidad"], 2)
        self.assertAlmostEqual(totales["depreciacion_del_ejercicio"], 1500000.0, places=2)
        self.assertTrue(os.path.isfile(respuesta.resultado["resultado_guardado_en"]))

    def test_cartera_con_correccion_monetaria(self):
        self._escribir_planilla()
        respuesta = self.modulo.cartera(dict(self.opciones, anio=2025, corregir=True))
        camioneta = respuesta.resultado["activos"][0]
        # Bien que ya estaba al inicio del ejercicio 2025: 7.000.001 x 1,034.
        self.assertAlmostEqual(camioneta["valor_actualizado"], 7238001.03, places=2)

    def test_depreciar_un_activo(self):
        respuesta = self.modulo.depreciar(dict(self.opciones, valor="7.000.001", bien="camioneta",
                                               anio_inicio=2024))
        self.assertAlmostEqual(respuesta.resultado["cuota_anual"], 1000000.0, places=2)
        self.assertEqual(respuesta.resultado["codigo_sii"], "sii-gen-10")

    def test_depreciar_toda_la_planilla(self):
        self._escribir_planilla()
        respuesta = self.modulo.depreciar(dict(self.opciones))
        self.assertEqual(respuesta.resultado["cantidad"], 2)
        self.assertEqual(len(respuesta.resultado["activos"][0]["tabla"]), 7)

    def test_depreciar_con_bien_ambiguo(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.depreciar(dict(self.opciones, valor=1000000, bien="herramientas"))
        self.assertIn("--vida-util", contexto.exception.sugerencia)

    def test_informe_html(self):
        self._escribir_planilla()
        respuesta = self.modulo.informe_html(dict(self.opciones, anio=2025))
        archivo = respuesta.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as html:
            contenido = html.read()
        self.assertIn("Activos fijos y depreciacion", contenido)
        self.assertIn("Camioneta", contenido)

    def test_acciones_publicadas(self):
        for accion in ("vida-util", "depreciar", "cartera", "informe"):
            self.assertIn(accion, self.modulo.ACCIONES)


if __name__ == "__main__":
    unittest.main()
