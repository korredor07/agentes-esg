# -*- coding: utf-8 -*-
"""Pruebas de los hallazgos de la prueba E2E con agentes (docs/prueba-e2e.md).

Seis conversaciones simuladas de personas reales encontraron resultados que
decian algo que no era cierto o que no se podian obtener. Cada clase fija la
correccion para que no vuelva a pasar.
"""

import io
import json
import os
import unittest

from ayuda_pruebas import PruebaConCarpeta  # noqa: E402

from calculos import aplicabilidad  # noqa: E402
from nucleo import espacio  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PruebaDesconocidoNoEsNo(unittest.TestCase):
    """Si nadie dijo si la empresa vende a Europa, lo europeo queda por confirmar."""

    PERFIL = {"nombre": "Duda SpA", "pais": "CL", "trabajadores": 40, "exporta_a_ue": None}

    def test_ninguna_regla_europea_queda_fuera(self):
        resultado = aplicabilidad.evaluar(self.PERFIL)
        fuera = [f["id"] for f in resultado["no_aplican"]
                 if "Union Europea" in f["motivo"] or "Union Europea" in f["norma"]]
        self.assertEqual(fuera, [])
        self.assertTrue(any("Union Europea" in f["motivo"] for f in resultado["por_revisar"]))

    def test_la_respuesta_de_la_persona_gana_sobre_el_perfil(self):
        perfil = dict(self.PERFIL, exporta_a_ue=False)
        resultado = aplicabilidad.evaluar(perfil, {"exporta_a_ue": "si", "exporta_bienes_cbam": "si"})
        self.assertTrue(any("frontera" in f["motivo"] for f in resultado["aplican"]))


class PruebaEuropa(PruebaConCarpeta):

    def setUp(self):
        super(PruebaEuropa, self).setUp()
        from modulos import europa
        self.europa = europa
        espacio.crear_empresa({"nombre": "Fruticola Prueba", "pais": "CL", "trabajadores": 85,
                               "exporta_a_ue": True}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Fruticola Prueba"}

    def test_la_csddd_es_del_cliente_no_del_exportador(self):
        resultado = self.europa.aplica(dict(self.opciones)).resultado
        csddd = [m for m in resultado["mecanismos"] if m["id"] == "csddd"][0]
        self.assertEqual(csddd["estado"], "por el cliente")
        self.assertNotIn(csddd["norma"], resultado["aplican"])

    def test_sin_saber_si_va_en_barco_el_recargo_queda_por_confirmar(self):
        resultado = self.europa.aplica(dict(self.opciones)).resultado
        maritimo = [m for m in resultado["mecanismos"] if m["id"] == "maritimo"][0]
        self.assertEqual(maritimo["estado"], "revisar")
        self.assertIn("envia_por_mar", [p["clave"] for p in resultado["preguntas_pendientes"]])

    def test_lo_que_no_aplica_no_deja_tareas(self):
        resultado = self.europa.aplica(dict(self.opciones, exporta_bienes_cbam="no",
                                            exporta_commodities_eudr="no")).resultado
        for mecanismo in resultado["mecanismos"]:
            if mecanismo["estado"] == "no aplica":
                self.assertTrue(mecanismo["que_hacer"].startswith("Nada"), mecanismo["id"])

    def test_cbam_sin_datos_de_planta_igual_orienta(self):
        resultado = self.europa.cbam(dict(self.opciones, sector="acero", cantidad="30",
                                          masa_anual_importador="30")).resultado
        self.assertTrue(resultado["umbral_del_importador"]["exento"])
        self.assertEqual(resultado["cubierto_por_el_cbam"], "confirmar codigo arancelario")
        self.assertIn("Anexo I", resultado["en_una_frase"])
        self.assertIsNone(resultado["emisiones"])

    def test_cbam_sin_masa_explica_el_umbral(self):
        resultado = self.europa.cbam(dict(self.opciones, sector="cemento", cantidad="100")).resultado
        self.assertIn("50 t", resultado["en_una_frase"])
        self.assertIs(resultado["cubierto_por_el_cbam"], True)


class PruebaTableroSinAlertasFantasma(PruebaConCarpeta):
    """Un archivo de alertas viejo no puede mostrar plazos de un caso que no existe."""

    def test_quita_alertas_de_casos_inexistentes(self):
        from modulos import tablero
        _, ruta, _ = espacio.crear_empresa({"nombre": "Tablero SpA", "pais": "CL", "trabajadores": 20},
                                           raiz=self.carpeta)
        archivo = os.path.join(ruta, "seguimiento", "alertas.json")
        with io.open(archivo, "w", encoding="utf-8") as destino:
            json.dump([{"origen": "Ley Karin", "caso": "KARIN-2026-001", "titulo": "Plazo fantasma",
                        "vence": "2026-09-15", "estado": "vencido", "por_vencer": False, "detalle": ""}],
                      destino)
        tablero.generar({"raiz": self.carpeta, "empresa": "Tablero SpA"})
        with io.open(archivo, encoding="utf-8") as origen:
            actuales = json.load(origen)
        self.assertFalse([a for a in actuales if a.get("caso") == "KARIN-2026-001"])


class PruebaPlantillaSinEjemplos(PruebaConCarpeta):
    """Agregar datos a una planilla recien creada no puede arrastrar a la empresa de ejemplo."""

    def test_las_filas_de_ejemplo_no_quedan_mezcladas(self):
        from modulos import datos, plantilla
        espacio.crear_empresa({"nombre": "Nueva SpA", "pais": "CL"}, raiz=self.carpeta)
        opciones = {"raiz": self.carpeta, "empresa": "Nueva SpA"}
        plantilla.crear(dict(opciones, tipo="consumos"))
        respuesta = datos.escribir(dict(opciones, tipo="consumos", filas=json.dumps(
            [["2025-01", "Local", "electricidad", "electricidad", 1000, "kWh", "reportado", "", ""]])))
        self.assertGreater(respuesta.resultado["filas_de_ejemplo_quitadas"], 0)
        self.assertEqual(respuesta.resultado["filas_en_la_planilla"], 1)
        leido = datos.leer(dict(opciones, archivo="consumos.xlsx"))
        self.assertEqual([f["sitio"] for f in leido["filas"]], ["Local"])

    def test_listar_plantillas_trae_las_columnas(self):
        from plantillas import definiciones
        consumos = [p for p in definiciones.listar() if p["tipo"] == "consumos"][0]
        self.assertIn("Calidad del dato", consumos["columnas"])


class PruebaAyudaCompleta(unittest.TestCase):
    """La ayuda tiene que mostrar las opciones que las skills le ensenan al asistente."""

    def setUp(self):
        import esg
        self.esg = esg

    def _opciones(self, modulo, accion):
        return self.esg.ayuda_de_modulo(modulo)["acciones"][accion]["opciones"]

    def test_opciones_leidas_en_otra_funcion(self):
        self.assertIn("--correccion", self._opciones("activos", "depreciar"))
        self.assertIn("--fase", self._opciones("mineria", "informe"))
        self.assertIn("--anio-meta", self._opciones("meta", "definir"))

    def test_opciones_leidas_de_una_lista(self):
        self.assertIn("--exporta-bienes-cbam", self._opciones("europa", "aplica"))


class PruebaMetas(PruebaConCarpeta):
    """La meta se dice en porcentaje, y sin supuestos no hay probabilidad que mostrar."""

    def setUp(self):
        super(PruebaMetas, self).setUp()
        from modulos import meta
        self.meta = meta
        espacio.crear_empresa({"nombre": "Metas SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Metas SpA"}

    def test_reduccion_total_en_porcentaje(self):
        resultado = self.meta.definir(dict(self.opciones, base="330.69", anio_base="2025", anio_meta="2030",
                                           reduccion="42")).resultado
        self.assertAlmostEqual(resultado["meta"]["emisiones_meta"], 191.8, delta=0.1)
        self.assertEqual(resultado["meta"]["reduccion_pedida_pct"], 42.0)

    def test_reduccion_imposible_se_rechaza(self):
        from nucleo.salida import Problema
        with self.assertRaises(Problema):
            self.meta.definir(dict(self.opciones, base="100", anio_meta="2030", reduccion="150"))

    def test_sin_supuestos_no_inventa_una_probabilidad(self):
        self.meta.definir(dict(self.opciones, base="330.69", anio_base="2025", anio_meta="2030", reduccion="42"))
        resultado = self.meta.probabilidad(dict(self.opciones, iteraciones="200")).resultado
        self.assertIsNone(resultado["probabilidad_pct"])
        self.assertFalse(resultado["es_una_estimacion"])
        self.assertIn("no es una probabilidad", resultado["lectura"])
        informe = self.meta.informe_html(dict(self.opciones))
        informe = getattr(informe, "resultado", informe)
        self.assertTrue(os.path.isfile(informe["archivo"]))


class PruebaPlanDeMedidas(PruebaConCarpeta):
    """El plan lee la planilla que crea la plantilla (capa 1: buscaba otro nombre y nunca la encontraba)."""

    def setUp(self):
        super(PruebaPlanDeMedidas, self).setUp()
        from modulos import datos, meta, plantilla
        self.datos, self.meta, self.plantilla = datos, meta, plantilla
        espacio.crear_empresa({"nombre": "Plan SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Plan SpA"}
        self.plantilla.crear(dict(self.opciones, tipo="medidas"))

    def test_el_flujo_de_la_skill_llega_al_plan(self):
        self.datos.escribir(dict(self.opciones, tipo="medidas", filas=json.dumps(
            [["Paneles solares", 80000, 1500, 12000, 20, 45, "Gerencia", ""]])))
        respuesta = self.meta.plan(dict(self.opciones, brecha="30"))
        self.assertTrue(respuesta.resultado["archivo"].endswith("medidas.xlsx"))
        nombres = json.dumps(respuesta.resultado, ensure_ascii=False)
        self.assertIn("Paneles solares", nombres)
        self.assertNotIn("Iluminacion LED en planta", nombres)

    def test_solo_con_los_ejemplos_no_arma_un_plan_inventado(self):
        from nucleo.salida import Problema
        with self.assertRaises(Problema) as contexto:
            self.meta.plan(self.opciones)
        self.assertIn("ejemplo", contexto.exception.mensaje)

    def test_los_ejemplos_que_quedaron_en_excel_no_entran(self):
        from nucleo import excel
        from plantillas import definiciones
        _, definicion = definiciones.obtener("medidas")
        ruta = os.path.join(espacio.cargar_empresa("Plan SpA", raiz=self.carpeta)[1], "datos", "medidas.xlsx")
        hojas = definiciones.hojas_de(definicion, con_ejemplo=True)
        hojas[1]["filas"] = list(hojas[1]["filas"]) + [["Paneles solares", 80000, 1500, 12000, 20, 45, "", ""]]
        excel.escribir_xlsx(ruta, hojas)
        respuesta = self.meta.plan(dict(self.opciones, brecha="30"))
        self.assertIn("Paneles solares", json.dumps(respuesta.resultado, ensure_ascii=False))
        self.assertNotIn("Iluminacion LED en planta", json.dumps(respuesta.resultado, ensure_ascii=False))
        self.assertTrue(any("fila(s) de ejemplo" in a for a in respuesta.advertencias))


class PruebaInformeDeHuella(PruebaConCarpeta):
    """El informe va a un cliente: sin instrucciones para el asistente y diciendo lo que quedo fuera."""

    FILAS = [{"_fila": 2, "periodo": "2025-01", "recurso": "glp", "uso": "estacionaria", "cantidad": 45,
              "unidad": "kg", "pais": "PE"},
             {"_fila": 3, "periodo": "2025-01", "recurso": "gasto agricultura", "cantidad": 9000,
              "unidad": "USD", "alcance": 3, "categoria": "1"}]

    def test_los_avisos_no_le_hablan_al_asistente(self):
        from calculos import carbono
        resumen = carbono.calcular(self.FILAS, pais="PE", conjunto="AR5")
        for aviso in resumen["advertencias"]:
            self.assertNotIn("en el informe", aviso)

    def test_dice_cuanto_se_estimo_por_gasto(self):
        from calculos import carbono
        resumen = carbono.calcular(self.FILAS, pais="PE", conjunto="AR5")
        self.assertGreater(resumen["calidad_datos"]["estimado_por_gasto_pct"], 50)

    def test_el_informe_lista_las_categorias_no_estimadas(self):
        from modulos import huella
        resumen = __import__("calculos.carbono", fromlist=["calcular"]).calcular(self.FILAS, pais="PE",
                                                                                  conjunto="AR5")
        bloques = huella._bloques_informe(dict(resumen, periodo="2025"), {"nombre": "Prueba"})
        textos = json.dumps(bloques, ensure_ascii=False)
        self.assertIn("Categorías del alcance 3 que no se estimaron", textos)
        self.assertIn("15. Inversiones", textos)
        self.assertIn("se estimo por gasto", textos)


class PruebaLogisticaDictada(PruebaConCarpeta):
    """El viaje dictado en la conversacion se calcula sin planilla, y el informe no inventa ajustes."""

    TRAMOS = [{"vehiculo": "camion refrigerado", "modo": "carretera", "toneladas": 12, "km": 220},
              {"tipo": "hub", "toneladas": 12, "descripcion": "Puerto San Antonio"},
              {"vehiculo": "barco", "modo": "maritimo", "toneladas": 12, "km": 12000},
              {"vehiculo": "camion refrigerado", "modo": "carretera", "toneladas": 12, "km": 150}]

    def setUp(self):
        super(PruebaLogisticaDictada, self).setUp()
        from modulos import logistica
        self.logistica = logistica
        espacio.crear_empresa({"nombre": "Exportadora SpA", "pais": "CL"}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Exportadora SpA"}

    def test_calcula_los_tramos_del_comando(self):
        resultado = self.logistica.calcular(dict(self.opciones, cadena="Manzanas",
                                                 tramos=json.dumps(self.TRAMOS))).resultado
        self.assertAlmostEqual(resultado["total_kg_co2e"], 3508.0404, places=4)
        self.assertFalse(resultado["completo"])

    def test_el_informe_no_dice_que_ajusto_lo_que_no_ajusto(self):
        respuesta = self.logistica.informe_html(dict(self.opciones, cadena="Manzanas",
                                                     tramos=json.dumps(self.TRAMOS)))
        with io.open(respuesta.resultado["archivo"], encoding="utf-8") as origen:
            html = origen.read()
        self.assertNotIn("%%", html)
        self.assertIn("no hizo falta ajustarlas", html)

    def test_json_mal_formado_se_explica(self):
        from nucleo.salida import Problema
        with self.assertRaises(Problema) as contexto:
            self.logistica.calcular(dict(self.opciones, tramos="no es json"))
        self.assertIn("--tramos", contexto.exception.sugerencia)


class PruebaBorradorDeReporte(unittest.TestCase):
    """El borrador VSME tiene que usar los datos que ya existen y no pisar el anterior."""

    def test_el_alcance_3_es_opcional_en_b3(self):
        from calculos import reportes
        b3 = [c for c in reportes.contenidos_de("VSME") if c["codigo"] == "B3"][0]
        disponibles = {"consumos.xlsx", "huella.por_alcance.alcance_1", "huella.por_alcance.alcance_2",
                       "huella.total_t_co2e"}
        sin_a3 = reportes._ficha(b3, disponibles)
        con_a3 = reportes._ficha(b3, disponibles | {"huella.por_alcance.alcance_3"})
        # Sin alcance 3 no falta ningun dato; queda parcial porque B3 pide ademas energia en MWh e intensidad.
        self.assertEqual(sin_a3["faltan"], [])
        self.assertEqual(sin_a3["estado"], "parcial")
        self.assertIn("huella.por_alcance.alcance_3", con_a3["encontrados"])

    def test_el_agua_ya_calculada_responde_b6_y_gri_303(self):
        from calculos import reportes
        for marco, codigo in (("VSME", "B6"), ("GRI", "303-3"), ("GRI", "303-5")):
            contenido = [c for c in reportes.contenidos_de(marco) if c["codigo"] == codigo][0]
            self.assertEqual(reportes._ficha(contenido, {"agua.indicadores"})["estado"], "cubierto", codigo)


class PruebaBorradorEnCarpeta(PruebaConCarpeta):

    def setUp(self):
        super(PruebaBorradorEnCarpeta, self).setUp()
        from modulos import reporte
        self.reporte = reporte
        espacio.crear_empresa({"nombre": "Reporte SpA", "pais": "CL", "periodo_actual": "2026",
                               "trabajadores": 10, "exporta_a_ue": False}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Reporte SpA", "marco": "VSME", "periodo": "2025"}

    def test_no_pisa_un_borrador_anterior(self):
        primero = self.reporte.borrador(dict(self.opciones)).resultado["archivo"]
        segundo = self.reporte.borrador(dict(self.opciones)).resultado["archivo"]
        self.assertNotEqual(primero, segundo)
        self.assertTrue(segundo.endswith("-v2.docx"))
        self.assertTrue(os.path.isfile(primero))

    def test_la_ficha_usa_el_periodo_del_reporte(self):
        perfil, ruta = espacio.cargar_empresa("Reporte SpA", raiz=self.carpeta)
        _, detalle, _, _ = self.reporte.datos_disponibles(perfil, ruta, "2025")
        self.assertIn("periodo 2025", detalle["empresa.json"])


class PruebaProductorRep(unittest.TestCase):
    """En envases, el productor REP es quien vende el producto envasado, no quien fabrica el envase vacio."""

    def test_la_regla_explica_la_definicion_verificada(self):
        resultado = aplicabilidad.evaluar({"nombre": "Envases SpA", "pais": "CL", "trabajadores": 60,
                                           "exporta_a_ue": False}, {"pone_productos_prioritarios": "si"})
        rep = [f for f in resultado["aplican"] if f["id"] == "cl-rep"][0]
        self.assertIn("envase vacio", rep["motivo"])
        self.assertNotIn("sea fabricandolos", rep["motivo"])


class PruebaCartaAProveedores(PruebaConCarpeta):
    """La carta no puede exigir respuesta si la empresa no lo decidio (agente-proveedores)."""

    def setUp(self):
        super(PruebaCartaAProveedores, self).setUp()
        from modulos import proveedores
        self.proveedores = proveedores
        espacio.crear_empresa({"nombre": "Compras SpA", "pais": "CL", "exporta_a_ue": False,
                               "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Compras SpA"}

    def _texto(self, archivo):
        import re
        import zipfile
        with zipfile.ZipFile(archivo) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        return " ".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S))

    def test_por_defecto_no_condiciona(self):
        respuesta = self.proveedores.carta(dict(self.opciones, proveedor="Molino Central"))
        texto = self._texto(respuesta.resultado["archivo"])
        self.assertNotIn("necesitamos que exista una respuesta", texto)
        self.assertTrue(any("--condicionar" in a for a in respuesta.advertencias))

    def test_condiciona_solo_si_se_pide(self):
        respuesta = self.proveedores.carta(dict(self.opciones, proveedor="Molino Central", condicionar=True))
        self.assertIn("necesitamos que exista una respuesta", self._texto(respuesta.resultado["archivo"]))

    def test_sin_motivo_no_afirma_que_una_norma_lo_exige(self):
        # Ronda 2 E2E: el pedido venia de un cliente y el VSME no es obligatorio.
        respuesta = self.proveedores.carta(dict(self.opciones, proveedor="Molino Central"))
        texto = self._texto(respuesta.resultado["archivo"])
        self.assertNotIn("normas", texto)
        self.assertIn("datos reales", texto)
        con_motivo = self.proveedores.carta(dict(self.opciones, proveedor="Envases Sur",
                                                 motivo="un cliente nos pidio un reporte VSME."))
        self.assertIn("un cliente nos pidio un reporte VSME.", self._texto(con_motivo.resultado["archivo"]))


class PruebaRutasLargas(unittest.TestCase):
    """En Windows, una ruta de mas de 260 caracteres fallaba con un «no encontre el archivo»."""

    def test_explica_el_problema_y_como_resolverlo(self):
        from unittest import mock
        from nucleo.salida import Problema
        larga = "C:\\" + "carpeta-muy-larga\\" * 20 + "carta.docx"
        with mock.patch.object(espacio.os, "name", "nt"), \
                mock.patch.object(espacio, "_rutas_largas_habilitadas", return_value=False), \
                mock.patch.object(espacio.os.path, "abspath", side_effect=lambda r: r):
            with self.assertRaises(Problema) as contexto:
                espacio.revisar_largo_de_ruta(larga)
        self.assertIn("260", contexto.exception.mensaje)
        self.assertIn("raiz del disco", contexto.exception.sugerencia)

    def test_una_ruta_normal_pasa(self):
        espacio.revisar_largo_de_ruta("C:\\agentes-esg\\empresas\\x\\reportes\\carta.docx")


class PruebaCalendarioDePeru(PruebaConCarpeta):
    """Revisar plazos es el primer paso del asistente: para Peru no puede ser un error."""

    def test_pais_sin_calendario_responde_ok(self):
        from modulos import calendario
        espacio.crear_empresa({"nombre": "Panaderia SAC", "pais": "PE", "exporta_a_ue": False,
                               "anio_base": 2025}, raiz=self.carpeta)
        respuesta = calendario.proximas({"raiz": self.carpeta, "empresa": "Panaderia SAC"})
        self.assertFalse(respuesta.resultado["calendario_disponible"])
        self.assertEqual(respuesta.resultado["urgentes"], [])
        self.assertIn("no puedo avisar plazos", respuesta.resultado["mensaje"])


class PruebaProximaAccionEnCrm(PruebaConCarpeta):

    def test_registra_la_proxima_accion_y_su_fecha(self):
        from modulos import crm
        espacio.crear_empresa({"nombre": "Consultora SpA", "pais": "CL", "exporta_a_ue": False,
                               "anio_base": 2025}, raiz=self.carpeta)
        respuesta = crm.registrar({"raiz": self.carpeta, "empresa": "Consultora SpA",
                                   "prospecto": "Vina Santa Rita", "necesidad": "huella de carbono",
                                   "fecha_contacto": "2026-09-15", "proxima_accion": "Enviar propuesta",
                                   "fecha_proxima": "2026-09-18"})
        prospecto = respuesta.resultado["prospecto"]
        self.assertEqual(prospecto["proxima_accion"], "Enviar propuesta")
        self.assertEqual(prospecto["fecha_proxima_accion"], "2026-09-18")
        self.assertEqual(prospecto["bitacora"][0]["fecha"], "2026-09-15")

    def test_fecha_invalida_se_explica(self):
        from modulos import crm
        from nucleo.salida import Problema
        espacio.crear_empresa({"nombre": "Consultora SpA", "pais": "CL"}, raiz=self.carpeta)
        with self.assertRaises(Problema):
            crm.registrar({"raiz": self.carpeta, "empresa": "Consultora SpA", "prospecto": "X",
                           "fecha_proxima": "el viernes"})


class PruebaDerivacionLeyKarin(PruebaConCarpeta):
    """Segunda ronda E2E: el motor dejaba investigar internamente cuando la ley obliga a derivar."""

    def setUp(self):
        super(PruebaDerivacionLeyKarin, self).setUp()
        from modulos import karin
        self.karin = karin
        espacio.crear_empresa({"nombre": "Envases SpA", "pais": "CL", "trabajadores": 60,
                               "exporta_a_ue": False, "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Envases SpA", "fecha_denuncia": "2026-09-01"}

    def test_sin_reglamento_actualizado_hay_que_derivar(self):
        respuesta = self.karin.crear(dict(self.opciones, reglamento_actualizado="no"))
        self.assertTrue(respuesta.resultado["derivacion_obligatoria"])
        self.assertIn("transitorio", respuesta.resultado["motivo_derivacion"])
        self.assertEqual(respuesta.resultado["proximos_pasos"][0]["id"], "derivar_dt")
        self.assertTrue(respuesta.advertencias[0].startswith("IMPORTANTE"))

    def test_contra_un_gerente_siempre_se_deriva(self):
        respuesta = self.karin.crear(dict(self.opciones, reglamento_actualizado="si", contra_representante="si"))
        self.assertTrue(respuesta.resultado["derivacion_obligatoria"])
        self.assertIn("art. 12 inc. 5", respuesta.resultado["motivo_derivacion"])

    def test_con_todo_en_regla_no_obliga_a_derivar(self):
        respuesta = self.karin.crear(dict(self.opciones, reglamento_actualizado="si", contra_representante="no"))
        self.assertFalse(respuesta.resultado["derivacion_obligatoria"])

    def test_derivada_los_30_dias_corren_desde_la_recepcion_en_la_dt(self):
        from calculos import karin as motor
        sin_recepcion = {h["id"]: h for h in motor.plazos("2026-09-01", {}, via="derivada")["hitos"]}
        self.assertIsNone(sin_recepcion["conclusion_investigacion"]["vence"])
        self.assertIn("certificado de recepcion", sin_recepcion["conclusion_investigacion"]["estado"])
        con_recepcion = {h["id"]: h for h in motor.plazos("2026-09-01", {"recepcion_dt": "2026-09-10"},
                                                          via="derivada")["hitos"]}
        interna = {h["id"]: h for h in motor.plazos("2026-09-01", {})["hitos"]}
        self.assertEqual(con_recepcion["conclusion_investigacion"]["cuenta_desde"], "recepcion_dt")
        self.assertGreater(con_recepcion["conclusion_investigacion"]["vence"],
                           interna["conclusion_investigacion"]["vence"])

    def test_la_recepcion_se_puede_registrar_como_evento(self):
        caso = self.karin.crear(dict(self.opciones, via="derivada", reglamento_actualizado="no")).resultado["caso"]
        respuesta = self.karin.evento(dict(self.opciones, caso=caso, hito="recepcion_dt", fecha="2026-09-03"))
        por_id = {h["id"]: h for h in respuesta.resultado["plazos"]}
        self.assertEqual(por_id["conclusion_investigacion"]["cuenta_desde"], "recepcion_dt")
        self.assertEqual(por_id["conclusion_investigacion"]["responsable"], "Direccion del Trabajo")


class PruebaRevisionLeyKarin(PruebaConCarpeta):
    """Revision independiente: respuestas ambiguas, derivacion tardia y datos dañados no pueden pasar en silencio."""

    def setUp(self):
        super(PruebaRevisionLeyKarin, self).setUp()
        from modulos import karin
        from nucleo.salida import Problema
        self.karin, self.Problema = karin, Problema
        espacio.crear_empresa({"nombre": "Envases SpA", "pais": "CL", "trabajadores": 60,
                               "exporta_a_ue": False, "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Envases SpA"}
        self.denuncia = dict(self.opciones, fecha_denuncia="2026-09-01")

    def _plazos(self, respuesta):
        return {h["id"]: h for h in respuesta.resultado["plazos"]}

    def test_una_opcion_sin_valor_es_si(self):
        respuesta = self.karin.crear(dict(self.denuncia, reglamento_actualizado="si", contra_representante=True))
        self.assertTrue(respuesta.resultado["derivacion_obligatoria"])

    def test_una_respuesta_que_no_se_entiende_se_pregunta_y_no_se_guarda(self):
        with self.assertRaises(self.Problema):
            self.karin.crear(dict(self.denuncia, reglamento_actualizado="si",
                                  contra_representante="sí, es el gerente general"))
        self.assertEqual(self.karin.listar(self.opciones)["total"], 0)

    def test_con_una_respuesta_desconocida_no_da_por_hecho_que_se_investiga(self):
        respuesta = self.karin.crear(dict(self.denuncia, contra_representante="no"))
        self.assertIsNone(respuesta.resultado["derivacion_obligatoria"])
        self.assertTrue(respuesta.advertencias[0].startswith("Antes de investigar internamente"))
        self.assertEqual(respuesta.resultado["proximos_pasos"][0]["id"], "confirmar_derivacion")
        actualizada = self.karin.actualizar(dict(self.opciones, caso="KARIN-2026-001", reglamento_actualizado="no"))
        self.assertEqual(actualizada.resultado["camino"], "derivada")
        self.assertTrue(actualizada.advertencias[0].startswith("IMPORTANTE"))

    def test_la_derivacion_se_registra_despues_de_crear_y_cambia_todo_el_camino(self):
        self.karin.crear(dict(self.denuncia, reglamento_actualizado="no", contra_representante="no"))
        caso = dict(self.opciones, caso="KARIN-2026-001")
        visto = self.karin.ver(caso)
        self.assertTrue(visto.advertencias[0].startswith("IMPORTANTE"))

        derivada = self.karin.evento(dict(caso, hito="derivacion_dt", fecha="2026-09-02"))
        plazos = self._plazos(derivada)
        self.assertEqual(plazos["derivar_dt"]["cumplido_el"], "2026-09-02")
        self.assertIsNone(plazos["conclusion_investigacion"]["vence"])
        for hito in ("designar_investigador", "remision_informe", "pronunciamiento_dt"):
            self.assertTrue(plazos[hito]["estado"].startswith("no aplica"), hito)
        self.assertFalse(self.karin.ver(caso).advertencias[0].startswith("IMPORTANTE"))

        recibida = self._plazos(self.karin.evento(dict(caso, hito="recepcion_dt", fecha="2026-09-03")))
        self.assertEqual(recibida["conclusion_investigacion"]["cuenta_desde"], "recepcion_dt")
        self.assertEqual(recibida["conclusion_investigacion"]["responsable"], "Direccion del Trabajo")
        self.assertIsNone(recibida["aplicar_medidas"]["vence"])

        cerrada = self._plazos(self.karin.evento(dict(caso, hito="conclusiones_dt", fecha="2026-10-20")))
        self.assertEqual(cerrada["aplicar_medidas"]["vence"], "2026-11-04")
        self.assertEqual(cerrada["aplicar_medidas"]["tipo_de_dias"], "corridos")

    def test_la_recepcion_en_un_caso_interno_se_rechaza_sin_guardar(self):
        self.karin.crear(dict(self.denuncia, reglamento_actualizado="si", contra_representante="no"))
        caso = dict(self.opciones, caso="KARIN-2026-001")
        with self.assertRaises(self.Problema) as contexto:
            self.karin.evento(dict(caso, hito="recepcion_dt", fecha="2026-09-03"))
        self.assertIn("derivacion_dt", contexto.exception.sugerencia)
        self.assertEqual(self.karin.ver(caso).resultado["caso"]["eventos"], {})

    def test_un_hito_de_investigacion_interna_no_se_registra_si_hay_que_derivar(self):
        self.karin.crear(dict(self.denuncia, reglamento_actualizado="si", contra_representante="si"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.opciones, caso="KARIN-2026-001", hito="designar_investigador",
                                   fecha="2026-09-02"))

    def test_una_fecha_mal_escrita_no_queda_guardada(self):
        self.karin.crear(dict(self.denuncia, reglamento_actualizado="si", contra_representante="no"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.opciones, caso="KARIN-2026-001", hito="informar_dt", fecha="15 sept. 2026"))
        listado = self.karin.listar(self.opciones)
        self.assertEqual((listado["total"], listado["con_error"]), (1, 0))

    def test_la_via_se_normaliza_o_se_pregunta(self):
        respuesta = self.karin.crear(dict(self.denuncia, via="DT", reglamento_actualizado="si",
                                          contra_representante="no"))
        self.assertEqual(respuesta.resultado["camino"], "derivada")
        self.assertEqual(self.karin.ver(dict(self.opciones, caso="KARIN-2026-001")).resultado["caso"]["via"],
                         "derivada")
        with self.assertRaises(self.Problema):
            self.karin.crear(dict(self.denuncia, via="mediacion"))

    def test_un_caso_dañado_no_esconde_a_los_demas_ni_se_esconde(self):
        self.karin.crear(dict(self.denuncia, reglamento_actualizado="si", contra_representante="no"))
        self.karin.crear(dict(self.denuncia, reglamento_actualizado="si", contra_representante="no"))
        ruta = self.karin._contexto(self.opciones)[2]
        with io.open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        datos["casos"][0]["eventos"]["informar_dt"] = "15 sept. 2026"
        with io.open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo)
        listado = self.karin.listar(self.opciones)
        self.assertEqual((listado["total"], listado["con_error"]), (2, 1))
        alertas = self.karin.alertas(self.opciones).resultado["alertas"]
        self.assertTrue(any(a["estado"] == "error" and a["caso"] == "KARIN-2026-001" for a in alertas))
        self.assertTrue(any(a["caso"] == "KARIN-2026-002" for a in alertas))

    def test_el_tablero_muestra_que_no_pudo_actualizar_las_alertas(self):
        from unittest import mock
        from modulos import tablero
        with mock.patch.object(self.karin, "alertas", side_effect=self.Problema("Archivo dañado.", "Reconstruyelo.")):
            errores, fallidas = tablero._refrescar_alertas(dict(self.opciones))
        self.assertTrue(any("Ley Karin" in e and "Archivo dañado." in e for e in errores))
        self.assertEqual(fallidas, {"Ley Karin"})
        ruta = espacio.cargar_empresa("Envases SpA", raiz=self.carpeta)[1]
        with io.open(os.path.join(ruta, "seguimiento", "alertas.json"), "w", encoding="utf-8") as archivo:
            json.dump([{"origen": "Ley Karin", "titulo": "Plazo viejo", "vence": "2026-09-04", "estado": "vencido"}],
                      archivo)
        vistas = tablero._alertas(ruta, fallidas)
        self.assertTrue(vistas[0]["detalle"].startswith("[Puede estar desactualizada"))


class PruebaFilasDeEjemploFueraDeLosCalculos(PruebaConCarpeta):
    """Revision independiente: el filtro de ejemplos estaba solo en el plan de medidas."""

    def setUp(self):
        super(PruebaFilasDeEjemploFueraDeLosCalculos, self).setUp()
        from nucleo import excel
        from plantillas import definiciones
        self.excel, self.definiciones = excel, definiciones
        espacio.crear_empresa({"nombre": "Real SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Real SpA"}
        self.datos = os.path.join(espacio.cargar_empresa("Real SpA", raiz=self.carpeta)[1], "datos")

    def _planilla(self, tipo, filas_reales, cambiar_nota_del_ejemplo=False):
        definicion = self.definiciones.PLANTILLAS[tipo]
        hojas = self.definiciones.hojas_de(definicion, con_ejemplo=True)
        ejemplos = [list(fila) for fila in hojas[1]["filas"]]
        if cambiar_nota_del_ejemplo:
            ejemplos[0][-1] = "la persona le escribio una nota"
        hojas[1]["filas"] = ejemplos + filas_reales
        ruta = os.path.join(self.datos, "%s.xlsx" % tipo)
        self.excel.escribir_xlsx(ruta, hojas)
        return ruta

    def test_la_huella_no_suma_los_ejemplos_que_quedaron_en_excel(self):
        from modulos import huella
        self._planilla("consumos", [["2025-01", "Local", "electricidad", "electricidad", 1000, "kWh",
                                     "reportado", "", ""]], cambiar_nota_del_ejemplo=True)
        respuesta = huella.calcular(dict(self.opciones, periodo="2025"))
        self.assertEqual(respuesta.resultado["registros_calculados"], 1)
        self.assertTrue(any("fila(s) de ejemplo" in a for a in respuesta.advertencias))

    def test_solo_con_ejemplos_no_hay_huella(self):
        from modulos import huella
        from nucleo.salida import Problema
        self._planilla("consumos", [])
        with self.assertRaises(Problema) as contexto:
            huella.calcular(dict(self.opciones))
        self.assertIn("ejemplo", contexto.exception.mensaje)

    def test_los_activos_de_ejemplo_no_entran_a_la_cartera(self):
        from modulos import activos
        from nucleo.salida import Problema
        with self.assertRaises(Problema):
            activos.cartera(dict(self.opciones))  # la primera vez crea la planilla con ejemplos
        with self.assertRaises(Problema) as contexto:
            activos.cartera(dict(self.opciones))
        self.assertIn("ejemplo", contexto.exception.mensaje)

    def test_la_empresa_de_ejemplo_conserva_sus_datos(self):
        demo = os.path.join(RAIZ, "empresas", "ejemplo-alimentos-del-sur", "datos", "agua.xlsx")
        tabla, aviso = self.definiciones.leer_sin_ejemplos(demo)
        self.assertIsNone(aviso)
        self.assertEqual(len(tabla["filas"]), 1)

    def test_datos_leer_dice_que_quedan_ejemplos(self):
        from modulos import datos
        self._planilla("consumos", [])
        leido = datos.leer(dict(self.opciones, archivo="consumos.xlsx"))
        self.assertEqual(leido["filas_de_ejemplo"], 4)
        self.assertIn("ejemplo", leido["aviso"])

    def test_el_reporte_no_rellena_un_periodo_con_otros_anios(self):
        from modulos import reporte
        definicion = self.definiciones.PLANTILLAS["personas"]
        filas = [["2024", "Planta Talca"] + list(fila[2:]) for fila in definicion["ejemplo"]]
        self.excel.escribir_xlsx(os.path.join(self.datos, "personas.xlsx"),
                                 self.definiciones.hojas_de(dict(definicion, ejemplo=filas)))
        perfil, ruta = espacio.cargar_empresa("Real SpA", raiz=self.carpeta)
        claves, _, avisos, _ = reporte.datos_disponibles(perfil, ruta, periodo="2025")
        self.assertNotIn("personas.xlsx", claves)
        self.assertTrue(any("no tiene filas del periodo 2025" in a for a in avisos))


class PruebaCoberturaQueNoSeSobrestima(PruebaConCarpeta):
    """Revision independiente: tener el archivo no es tener la respuesta, y una huella incompleta no es el total."""

    def setUp(self):
        super(PruebaCoberturaQueNoSeSobrestima, self).setUp()
        from calculos import reportes
        from modulos import reporte
        self.reportes, self.reporte = reportes, reporte

    def _ficha(self, marco, codigo, disponibles):
        contenido = [c for c in self.reportes.contenidos_de(marco) if c["codigo"] == codigo][0]
        return self.reportes._ficha(contenido, set(disponibles))

    def test_cada_contenido_con_datos_declara_si_responden_todo_o_una_parte(self):
        for contenido in self.reportes.cargar_contenidos():
            nombre = "%s %s" % (contenido["marco"], contenido["codigo"])
            if contenido["dato_fuente"]:
                self.assertIn(contenido["responde"], ("todo", "parte"), nombre)
            else:
                self.assertEqual(contenido["responde"], "", nombre)

    def test_lo_que_ningun_dato_responde_no_toma_un_dato_prestado(self):
        for marco, codigo in (("GRI", "401-3"), ("GRI", "205-2"), ("GRI", "403-5"), ("GRI", "403-8"),
                              ("GRI", "302-2"), ("GRI", "102-3"), ("NCG 519", "519-excepcion-tamano")):
            self.assertEqual(self._ficha(marco, codigo, {"personas.xlsx", "alcance3.xlsx", "empresa.json"})["estado"],
                             "pendiente", codigo)

    def test_la_ficha_de_la_empresa_no_cubre_forma_juridica_ni_propiedad(self):
        self.assertEqual(self._ficha("GRI", "2-1", {"empresa.json"})["estado"], "parcial")
        self.assertEqual(self._ficha("NCG 461", "461-perfil", {"empresa.json"})["estado"], "parcial")
        self.assertEqual(self._ficha("GRI", "405-2", {"personas.remuneracion"})["estado"], "cubierto")
        # Tener la planilla de personas no basta: cada contenido pide su indicador.
        self.assertEqual(self._ficha("GRI", "404-1", {"personas.xlsx"})["estado"], "pendiente")

    def test_no_recomienda_cargar_un_texto(self):
        resultado = self.reportes.evaluar_cobertura("VSME", set())
        self.assertFalse(any(d["dato"] == "texto_de_la_empresa" for d in resultado["datos_que_mas_suman"]))

    def test_una_huella_incompleta_queda_parcial_y_marcada_en_el_word(self):
        import zipfile
        espacio.crear_empresa({"nombre": "Harinera SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        opciones = {"raiz": self.carpeta, "empresa": "Harinera SpA", "periodo": "2025", "marco": "GRI"}
        ruta = espacio.cargar_empresa("Harinera SpA", raiz=self.carpeta)[1]
        with io.open(espacio.ruta_de(ruta, "resultados", "huella_2025.json"), "w", encoding="utf-8") as archivo:
            json.dump({"version_calculo": 2, "total_t_co2e": 12.3, "periodo": "2025", "completo": False,
                       "registros_con_problema": 2,
                       "por_alcance": {"alcance_1": {"kg_co2e": 12300.0}}}, archivo)
        cobertura = self.reporte.cobertura(dict(opciones)).resultado
        self.assertNotIn("305-1", [c["codigo"] for c in cobertura["ya_puedes_reportar"]])
        self.assertIn("305-1", [c["codigo"] for c in cobertura["te_falta"]])
        respuesta = self.reporte.borrador(dict(opciones))
        self.assertTrue(any("esta incompleta" in a for a in respuesta.advertencias))
        with zipfile.ZipFile(respuesta.resultado["archivo"]) as documento:
            texto = documento.read("word/document.xml").decode("utf-8")
        self.assertIn("INCOMPLETA", texto)
        self.assertIn("Antes de publicar, revisa esto", texto)


class PruebaAvisosQueNoSePierden(PruebaConCarpeta):
    """Revision independiente: advertencias que quedaban en el JSON y no llegaban al documento ni a la persona."""

    def setUp(self):
        super(PruebaAvisosQueNoSePierden, self).setUp()
        from nucleo.salida import Problema
        self.Problema = Problema
        espacio.crear_empresa({"nombre": "Revision SpA", "pais": "CL", "anio_base": 2025, "exporta_a_ue": True},
                              raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Revision SpA"}
        self.ruta = espacio.cargar_empresa("Revision SpA", raiz=self.carpeta)[1]

    def _texto_docx(self, ruta):
        import re
        import zipfile
        with zipfile.ZipFile(ruta) as documento:
            xml = documento.read("word/document.xml").decode("utf-8")
        return " ".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S))

    def test_carta_y_cuestionario_sin_motivo_no_invocan_a_clientes_ni_autoridades(self):
        from modulos import proveedores
        carta = proveedores.carta(dict(self.opciones, proveedor="Molino Central")).resultado["archivo"]
        cuestionario = proveedores.cuestionario(dict(self.opciones, proveedor="Molino Central")).resultado["archivo"]
        for archivo in (carta, cuestionario):
            texto = self._texto_docx(archivo)
            self.assertNotIn("autoridad", texto)
            self.assertNotIn("requerimientos", texto)

    def test_cbam_y_eudr_no_aplican_sin_saber_si_vende_a_europa(self):
        from modulos import europa
        espacio.crear_empresa({"nombre": "Duda Europa SpA", "pais": "CL"}, raiz=self.carpeta)
        resultado = europa.aplica({"raiz": self.carpeta, "empresa": "Duda Europa SpA", "exporta_a_ue": "no se",
                                   "exporta_bienes_cbam": "si", "exporta_commodities_eudr": "si"}).resultado
        estados = {m["id"]: m["estado"] for m in resultado["mecanismos"]}
        self.assertEqual(estados["cbam"], "revisar")
        self.assertEqual(estados["eudr"], "revisar")

    def test_el_informe_europeo_no_usa_un_veredicto_guardado_viejo(self):
        from modulos import europa
        europa.aplica(dict(self.opciones))
        ruta_json = europa._contexto(self.opciones)[2]
        with io.open(ruta_json, encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        for mecanismo in guardado["aplica"]["mecanismos"]:
            if mecanismo["id"] == "maritimo":
                # Como lo guardaba la version anterior del motor.
                mecanismo["estado"] = "aplica"
                mecanismo["motivo"] = "VEREDICTO GUARDADO POR UNA VERSION ANTERIOR"
        with io.open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(guardado, archivo)
        archivo = europa.informe_html(dict(self.opciones)).resultado["archivo"]
        with io.open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertNotIn("VEREDICTO GUARDADO POR UNA VERSION ANTERIOR", html)
        self.assertIn("Falta confirmar si la carga viaja a Europa por barco", html)

    def test_depreciar_un_bien_ambiguo_avisa_de_las_nominas_no_cargadas(self):
        from modulos import activos
        with self.assertRaises(self.Problema) as contexto:
            activos.depreciar(dict(self.opciones, bien="cargador frontal", valor="450000000", anio="2024"))
        self.assertIn("mineria", contexto.exception.sugerencia)

    def test_el_informe_de_mineria_dice_que_el_gistm_no_es_ley(self):
        from modulos import mineria
        archivo = mineria.informe_html(dict(self.opciones, clasificacion="alta", requisitos="40")).resultado["archivo"]
        with io.open(archivo, encoding="utf-8") as origen:
            self.assertIn("NO es ley en Chile", origen.read())

    def test_el_plan_no_rellena_celdas_vacias_ni_trunca_la_vida_util(self):
        from modulos import datos, meta, plantilla
        plantilla.crear(dict(self.opciones, tipo="medidas"))
        datos.escribir(dict(self.opciones, tipo="medidas", filas=json.dumps([
            ["Paneles solares", 80000, 1500, 12000, 2.5, 45, "", ""],
            ["Caldera nueva", "", "", 9000, 10, 30, "", "Falta cotizacion"],
            ["Aislacion", 20000, 0, 3000, "", 10, "", ""],
        ])))
        respuesta = meta.plan(dict(self.opciones, brecha="30"))
        calculadas = {m["medida"]: m for m in respuesta.resultado["medidas"]}
        self.assertEqual(list(calculadas), ["Paneles solares"])
        self.assertEqual(calculadas["Paneles solares"]["vida_util"], 2.5)
        fuera = {p["medida"] for p in respuesta.resultado["medidas_con_problema"]}
        self.assertEqual(fuera, {"Caldera nueva", "Aislacion"})
        self.assertTrue(respuesta.advertencias[0].startswith("2 medida(s) quedaron fuera"))

    def test_el_informe_de_huella_muestra_todos_los_factores_y_los_supuestos(self):
        from modulos import huella
        from nucleo import excel
        from plantillas import definiciones
        hojas = definiciones.hojas_de(definiciones.PLANTILLAS["consumos"], con_ejemplo=False)
        hojas[1]["filas"] = [["2025-01", "Planta", "electricidad", "electricidad", 1000, "kWh", "reportado", "",
                              "Aproximacion declarada: medidor compartido"]]
        excel.escribir_xlsx(os.path.join(self.ruta, "datos", "consumos.xlsx"), hojas)
        huella.calcular(dict(self.opciones, periodo="2025"))
        # Resultado guardado por una version anterior: sin version ni notas de los factores.
        guardado = os.path.join(self.ruta, "resultados", "huella_2025.json")
        with io.open(guardado, encoding="utf-8") as archivo:
            viejo = json.load(archivo)
        viejo.pop("version_calculo")
        for fila in viejo["detalle"]:
            fila["factor"].pop("notas", None)
        with io.open(guardado, "w", encoding="utf-8") as archivo:
            json.dump(viejo, archivo)
        respuesta = huella.reporte(dict(self.opciones, periodo="2025"))
        self.assertTrue(any("se recalculo" in a for a in respuesta.advertencias))
        with io.open(respuesta.resultado["archivo"], encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("Factores usados y lo que dice su fuente", html)
        self.assertIn("Aproximacion declarada: medidor compartido", html)


class PruebaSegundaRevision(PruebaConCarpeta):
    """Segunda revision independiente: lo que las correcciones anteriores dejaron pasar."""

    def setUp(self):
        super(PruebaSegundaRevision, self).setUp()
        from calculos import karin as motor
        from modulos import karin
        from nucleo.salida import Problema
        self.motor, self.karin, self.Problema = motor, karin, Problema
        espacio.crear_empresa({"nombre": "Segunda SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Segunda SpA"}
        self.caso = dict(self.opciones, caso="KARIN-2026-001")

    def _plazos(self, respuesta):
        return {h["id"]: h for h in respuesta.resultado["plazos"]}

    def test_una_palabra_sin_comillas_no_se_pierde(self):
        import esg
        with self.assertRaises(self.Problema) as contexto:
            esg.despachar(["karin", "crear", "--fecha-denuncia", "2026-09-10", "--reglamento-actualizado", "si",
                           "--contra-representante", "no", "se"])
        self.assertIn("comillas", contexto.exception.sugerencia)

    def test_las_fechas_de_los_hitos_van_en_orden(self):
        self.karin.crear(dict(self.opciones, fecha_denuncia="2026-09-01", reglamento_actualizado="si",
                              contra_representante="no"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.caso, hito="informar_dt", fecha="2026-08-20"))
        self.karin.evento(dict(self.caso, hito="conclusion_investigacion", fecha="2026-10-10"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.caso, hito="remision_informe", fecha="2026-09-02"))
        eventos = self.karin.ver(self.caso).resultado["caso"]["eventos"]
        self.assertEqual(eventos, {"conclusion_investigacion": "2026-10-10"})

    def test_la_derivacion_tambien_va_en_orden(self):
        self.karin.crear(dict(self.opciones, fecha_denuncia="2026-09-01", reglamento_actualizado="no",
                              contra_representante="no"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.caso, hito="conclusiones_dt", fecha="2026-10-20"))
        self.karin.evento(dict(self.caso, hito="derivacion_dt", fecha="2026-09-03"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.caso, hito="recepcion_dt", fecha="2026-09-02"))

    def test_la_fecha_del_hito_no_se_supone_en_silencio(self):
        self.karin.crear(dict(self.opciones, fecha_denuncia="2026-09-01", reglamento_actualizado="si",
                              contra_representante="no"))
        with self.assertRaises(self.Problema):
            self.karin.evento(dict(self.caso, hito="informar_dt", fecha=True))
        sin_fecha = self.karin.evento(dict(self.caso, hito="medidas_resguardo"))
        self.assertTrue(sin_fecha.advertencias[0].startswith("No indicaste --fecha"))

    def test_lo_registrado_antes_de_derivar_no_desaparece(self):
        self.karin.crear(dict(self.opciones, fecha_denuncia="2026-09-01", reglamento_actualizado="si",
                              contra_representante="no"))
        self.karin.evento(dict(self.caso, hito="designar_investigador", fecha="2026-09-02"))
        plazos = self._plazos(self.karin.actualizar(dict(self.caso, contra_representante="si")))
        self.assertTrue(plazos["designar_investigador"]["estado"].startswith("no aplica"))
        self.assertEqual(plazos["designar_investigador"]["cumplido_el"], "2026-09-02")
        heredado = {h["id"]: h for h in self.motor.plazos("2026-09-01", {"informar_dt": "2026-09-02"},
                                                          via="derivada")["hitos"]}
        self.assertEqual(heredado["derivar_dt"]["cumplido_el"], "2026-09-02")

    def test_las_alertas_muestran_la_espera_de_la_dt_y_lo_condicional(self):
        self.karin.crear(dict(self.opciones, fecha_denuncia="2026-09-01", reglamento_actualizado="no",
                              contra_representante="no"))
        self.karin.evento(dict(self.caso, hito="derivacion_dt", fecha="2026-09-02"))
        self.karin.crear(dict(self.opciones, fecha_denuncia="2026-09-10", contra_representante="no"))
        alertas = self.karin.alertas(self.opciones).resultado["alertas"]
        self.assertTrue(any(a["caso"] == "KARIN-2026-001" and a["estado"] == "pendiente" for a in alertas))
        condicionales = [a for a in alertas if a["caso"] == "KARIN-2026-002" and "investigadora" in a["titulo"]]
        self.assertTrue(condicionales and condicionales[0]["titulo"].startswith("Solo si no corresponde derivar"))

    def test_la_carpeta_de_una_empresa_es_la_real(self):
        ruta = espacio.cargar_empresa("Segunda SpA", raiz=self.carpeta)[1]
        archivo = os.path.join(ruta, "empresa.json")
        with io.open(archivo, encoding="utf-8") as origen:
            perfil = json.load(origen)
        perfil["carpeta"] = "ejemplo-alimentos-del-sur"
        with io.open(archivo, "w", encoding="utf-8") as destino:
            json.dump(perfil, destino)
        self.assertEqual(espacio.cargar_empresa("Segunda SpA", raiz=self.carpeta)[0]["carpeta"],
                         os.path.basename(ruta))

    def test_ninguna_marca_apaga_el_filtro_de_ejemplos(self):
        from nucleo import excel
        from plantillas import definiciones
        ruta = espacio.cargar_empresa("Segunda SpA", raiz=self.carpeta)[1]
        archivo = os.path.join(ruta, "empresa.json")
        with io.open(archivo, encoding="utf-8") as origen:
            perfil = json.load(origen)
        perfil["empresa_de_ejemplo"] = True
        with io.open(archivo, "w", encoding="utf-8") as destino:
            json.dump(perfil, destino)
        planilla = os.path.join(ruta, "datos", "consumos.xlsx")
        excel.escribir_xlsx(planilla, definiciones.hojas_de(definiciones.PLANTILLAS["consumos"]))
        tabla, aviso = definiciones.leer_sin_ejemplos(planilla)
        self.assertEqual(tabla["filas"], [])
        self.assertIsNotNone(aviso)

    def test_el_plan_no_concluye_con_medidas_fuera(self):
        from calculos import macc
        medidas = [
            {"medida": "LED", "capex": 45000, "vida_util": 10, "opex": 1200, "ahorros": 14000, "tco2e_evitadas": 38},
            {"medida": "Recuperador", "capex": 210000, "vida_util": "", "opex": 8000, "ahorros": 22000,
             "tco2e_evitadas": 130},
        ]
        plan = macc.curva(medidas, brecha=150)["plan_para_la_brecha"]
        self.assertIsNone(plan["alcanza"])
        self.assertTrue(plan["incompleto"])
        self.assertEqual(plan["medidas_fuera"], ["Recuperador"])
        with self.assertRaises(self.Problema):
            macc.costo_marginal(dict(medidas[0], capex="45.000"))

    def test_el_informe_de_huella_no_se_arma_con_un_resultado_viejo_que_no_se_puede_rehacer(self):
        from modulos import huella
        ruta = espacio.cargar_empresa("Segunda SpA", raiz=self.carpeta)[1]
        with io.open(os.path.join(ruta, "resultados", "huella_2025.json"), "w", encoding="utf-8") as archivo:
            json.dump({"total_t_co2e": 31.4, "total_kg_co2e": 31400.0, "periodo": "2025", "completo": True,
                       "por_alcance": {}, "calidad_datos": {"porcentaje": {}}, "detalle": []}, archivo)
        with self.assertRaises(self.Problema) as contexto:
            huella.reporte(dict(self.opciones, periodo="2025"))
        self.assertIn("version anterior", contexto.exception.mensaje)


class PruebaCasosKarinHeredados(PruebaConCarpeta):
    """Un caso guardado por la version anterior se lee, dice que campo esta mal y se puede reparar."""

    def setUp(self):
        super(PruebaCasosKarinHeredados, self).setUp()
        from modulos import karin
        self.karin = karin
        espacio.crear_empresa({"nombre": "Heredada SpA", "pais": "CL", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Heredada SpA"}
        ruta_json = karin._contexto(self.opciones)[2]
        with io.open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump({"casos": [
                {"id": "KARIN-2026-001", "fecha_denuncia": "01-09-2026", "tipo": "acoso laboral",
                 "via": "derivada a la DT", "estado": "en investigacion", "eventos": {"informar_dt": "ayer"},
                 "bitacora": []},
                {"id": "KARIN-2026-002", "fecha_denuncia": "2026-09-05", "tipo": "acoso laboral",
                 "via": "mediacion", "estado": "en investigacion", "eventos": {}, "bitacora": []},
            ]}, archivo)

    def test_listar_nombra_el_campo_que_esta_mal(self):
        listado = self.karin.listar(self.opciones)
        errores = {c["id"]: c["error"] for c in listado["casos"] if c.get("error")}
        self.assertIn("informar_dt", errores["KARIN-2026-001"])
        self.assertIn("--via", errores["KARIN-2026-002"])

    def test_la_fecha_ilegible_se_corrige_y_la_via_libre_se_interpreta_con_aviso(self):
        caso = dict(self.opciones, caso="KARIN-2026-001")
        corregido = self.karin.evento(dict(caso, hito="informar_dt", fecha="2026-09-02"))
        self.assertTrue(any("se leyo como «derivada»" in a for a in corregido.advertencias))
        visto = self.karin.ver(caso)
        self.assertEqual(visto.resultado["camino"], "derivada")
        plazos = {h["id"]: h for h in visto.resultado["plazos"]}
        self.assertEqual(plazos["derivar_dt"]["cumplido_el"], "2026-09-02")

    def test_la_via_que_no_se_entiende_se_corrige_con_actualizar(self):
        caso = dict(self.opciones, caso="KARIN-2026-002")
        respuesta = self.karin.actualizar(dict(caso, via="interna"))
        self.assertEqual(respuesta.resultado["camino"], "interna")
        with io.open(self.karin._contexto(self.opciones)[2], encoding="utf-8") as archivo:
            guardado = json.load(archivo)
        self.assertEqual(guardado["casos"][1]["via"], "interna")
        self.assertFalse(any(clave.startswith("_avisos") for clave in guardado["casos"][0]))


class PruebaResultadosYPeriodos(PruebaConCarpeta):
    """Segunda revision: cifras de otro periodo, de una version anterior o incompletas no llegan calladas a un informe."""

    def setUp(self):
        super(PruebaResultadosYPeriodos, self).setUp()
        from nucleo import excel
        from plantillas import definiciones
        self.excel, self.definiciones = excel, definiciones
        espacio.crear_empresa({"nombre": "Periodos SpA", "pais": "CL", "anio_base": 2025, "periodo_actual": "2025",
                               "exporta_a_ue": True}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Periodos SpA"}
        self.ruta = espacio.cargar_empresa("Periodos SpA", raiz=self.carpeta)[1]

    def _huella(self, nombre, total, version=2):
        datos = {"total_t_co2e": total, "total_kg_co2e": total * 1000, "periodo": nombre, "completo": True,
                 "por_alcance": {"alcance_1": {"kg_co2e": total * 1000}}}
        if version:
            datos["version_calculo"] = version
        with io.open(os.path.join(self.ruta, "resultados", "huella_%s.json" % nombre), "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo)

    def _personas(self, filas):
        definicion = self.definiciones.PLANTILLAS["personas"]
        self.excel.escribir_xlsx(os.path.join(self.ruta, "datos", "personas.xlsx"),
                                 self.definiciones.hojas_de(dict(definicion, ejemplo=filas)))

    def test_el_borrador_no_usa_la_huella_de_otro_periodo(self):
        from modulos import reporte
        self._huella("completa", 59.6)
        claves, detalle, avisos, _ = reporte.datos_disponibles(
            espacio.cargar_empresa("Periodos SpA", raiz=self.carpeta)[0], self.ruta, periodo="2025")
        self.assertNotIn("huella.total_t_co2e", claves)
        self.assertTrue(any("del periodo 2025" in a for a in avisos))

    def test_una_huella_de_una_version_anterior_sin_datos_para_rehacerla_no_se_usa(self):
        from modulos import reporte
        self._huella("2025", 999, version=None)
        claves, _, avisos, _ = reporte.datos_disponibles(
            espacio.cargar_empresa("Periodos SpA", raiz=self.carpeta)[0], self.ruta, periodo="2025")
        self.assertNotIn("huella.total_t_co2e", claves)
        self.assertTrue(any("version anterior" in a for a in avisos))

    def test_el_indice_sin_periodo_usa_el_de_la_ficha_y_no_suma_años(self):
        from modulos import reporte
        fila = ["", "Planta Talca", "operario", "mujer", "indefinido", "completa", 20, 0, 0, "", "", "", "", "", ""]
        self._personas([["2024"] + fila[1:], ["2025"] + fila[1:]])
        archivo = reporte.indice(dict(self.opciones, marco="GRI")).resultado["archivo"]
        with io.open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("Dotacion: 20 personas", html)
        self.assertNotIn("Dotacion: 40 personas", html)

    def test_la_planilla_de_personas_no_cubre_lo_que_no_trae(self):
        from modulos import reporte
        fila = ["2025", "Planta Talca", "operario", "mujer", "indefinido", "completa", 20, 0, 0, "", "", "", "", "", ""]
        self._personas([fila])
        cobertura = reporte.cobertura(dict(self.opciones, marco="GRI")).resultado
        listos = [c["codigo"] for c in cobertura["ya_puedes_reportar"]]
        self.assertNotIn("404-1", listos)
        self.assertNotIn("405-2", listos)

    def test_el_agua_incompleta_no_sale_cubierta_y_su_informe_trae_los_avisos(self):
        from modulos import agua, reporte
        definicion = self.definiciones.PLANTILLAS["agua"]
        filas = [["2025", "Planta Talca", "red publica", 5000, 1000, "alcantarillado", "si", "reportado", ""],
                 ["2025", "Planta Talca", "pozo", "mucha", 0, "riego", "", "estimado", ""]]
        self.excel.escribir_xlsx(os.path.join(self.ruta, "datos", "agua.xlsx"),
                                 self.definiciones.hojas_de(dict(definicion, ejemplo=filas)))
        agua.calcular(dict(self.opciones, periodo="2025"))
        cobertura = reporte.cobertura(dict(self.opciones, marco="VSME")).resultado
        self.assertNotIn("B6", [c["codigo"] for c in cobertura["ya_puedes_reportar"]])
        respuesta = agua.informe_html(dict(self.opciones, periodo="2025"))
        with io.open(respuesta.resultado["archivo"], encoding="utf-8") as origen:
            self.assertIn("Supuestos y avisos del calculo", origen.read())

    def test_los_avisos_de_la_tabla_del_sii_llegan_desde_la_planilla(self):
        from calculos import activos
        avisos = []
        activos.vida_util_del_activo({"bien": "cargador frontal"}, avisos)
        self.assertTrue(any("mineria" in aviso for aviso in avisos))

    def test_el_informe_europeo_no_muestra_secciones_de_lo_que_no_aplica(self):
        from modulos import europa
        europa.eudr(dict(self.opciones, producto="cafe"))
        europa.aplica(dict(self.opciones, exporta_a_ue="no"))
        archivo = europa.informe_html(dict(self.opciones)).resultado["archivo"]
        with io.open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("No venden a la Union Europea.", html)
        self.assertNotIn("EUDR — productos libres de deforestacion", html)

    def test_el_tablero_elige_la_huella_del_periodo_y_no_el_acumulado(self):
        from modulos import tablero
        self._huella("2025", 40.0)
        self._huella("completa", 90.0)
        self.assertEqual(tablero._ultima_huella(self.ruta)["total_t_co2e"], 40.0)


class PruebaSinCaracteresDeControl(unittest.TestCase):
    """Un caracter de control escrito por error rompe una expresion regular sin que se vea."""

    def test_ningun_archivo_del_proyecto_los_tiene(self):
        permitidos = {"\n", "\r", "\t"}
        culpables = []
        for carpeta in (".claude", "tests", "docs"):
            for base, _, archivos in os.walk(os.path.join(RAIZ, carpeta)):
                if "__pycache__" in base:
                    continue
                for nombre in archivos:
                    if not nombre.endswith((".py", ".md", ".csv", ".json")):
                        continue
                    ruta = os.path.join(base, nombre)
                    with io.open(ruta, encoding="utf-8", errors="replace") as origen:
                        texto = origen.read()
                    if any(ord(c) < 32 and c not in permitidos for c in texto):
                        culpables.append(os.path.relpath(ruta, RAIZ))
        self.assertFalse(culpables, "Archivos con caracteres de control: %s" % culpables)


if __name__ == "__main__":
    unittest.main()
