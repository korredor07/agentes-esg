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
        self.assertIn("Categorias del alcance 3 que no se estimaron", textos)
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
        self.assertEqual(sin_a3["estado"], "cubierto")
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
