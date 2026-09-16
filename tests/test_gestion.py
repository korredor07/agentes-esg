# -*- coding: utf-8 -*-
"""Pruebas de los tres modulos de gestion: proveedores, academia y CRM.

No dependen de normativa: revisan que se guarden los registros, que las
prioridades salgan bien ordenadas y que los errores expliquen que hacer.
"""

import json
import os
import subprocess
import sys
import unittest

from ayuda_pruebas import MOTOR, PruebaConCarpeta  # noqa: E402

from nucleo import espacio  # noqa: E402
from nucleo.salida import Problema  # noqa: E402

ESG = os.path.join(MOTOR, "esg.py")


class BaseGestion(PruebaConCarpeta):
    """Crea una empresa de prueba y deja las opciones listas."""

    def setUp(self):
        super(BaseGestion, self).setUp()
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL", "sector": "Alimentos",
                               "tamano": "pequena", "anio_base": 2025}, raiz=self.carpeta)
        self.opciones = {"raiz": self.carpeta, "empresa": "Prueba SpA"}

    def con(self, **extra):
        return dict(self.opciones, **extra)


# --------------------------------------------------------------------------
# Proveedores
# --------------------------------------------------------------------------

class PruebaProveedores(BaseGestion):
    def setUp(self):
        super(PruebaProveedores, self).setUp()
        from modulos import proveedores
        self.modulo = proveedores

    def _cargar_tres(self):
        self.modulo.registrar(self.con(nombre="Envases del Sur", categoria="envases",
                                       gasto_anual="18000000", entrego="si", huella_declarada="0,85",
                                       unidad="kg CO2e por kg", calidad="reportado",
                                       certificaciones="ISO 14001, ISO 9001", contacto="Luis Soto"))
        self.modulo.registrar(self.con(nombre="Transportes Norte", categoria="fletes",
                                       gasto_anual="9000000", contacto="Rosa Lagos"))
        self.modulo.registrar(self.con(nombre="Insumos Menores", categoria="varios", gasto_anual="200000"))

    def test_cuestionario_y_carta_quedan_en_reportes(self):
        cuestionario = self.modulo.cuestionario(self.con(proveedor="Envases del Sur", plazo="30-10-2026",
                                                         responsable="Ana Rojas", correo="ana@empresa.cl"))
        carta = self.modulo.carta(self.con(proveedor="Envases del Sur", plazo="30-10-2026",
                                           responsable="Ana Rojas", correo="ana@empresa.cl"))
        self.assertTrue(os.path.isfile(cuestionario.resultado["archivo"]))
        self.assertTrue(os.path.isfile(carta.resultado["archivo"]))
        self.assertTrue(cuestionario.resultado["archivo"].endswith(".docx"))
        self.assertIn("datos de personas", " ".join(carta.advertencias))

    def test_cuestionario_avisa_si_faltan_los_datos_de_contacto(self):
        respuesta = self.modulo.cuestionario(self.opciones)
        textos = " ".join(respuesta.advertencias)
        self.assertIn("corchetes", textos)
        self.assertIn("plazo", textos)

    def test_registrar_sin_nombre_explica_que_falta(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.registrar(self.opciones)
        self.assertIn("nombre del proveedor", contexto.exception.mensaje)
        self.assertIn("--nombre", contexto.exception.sugerencia)

    def test_registrar_guarda_y_luego_actualiza_al_mismo_proveedor(self):
        primero = self.modulo.registrar(self.con(nombre="Envases del Sur", categoria="envases",
                                                 gasto_anual="18.000.000")).resultado
        self.assertEqual(primero["proveedor"]["estado"], "sin datos")
        self.assertEqual(primero["proveedor"]["gasto_anual"], 18000000.0)
        self.assertEqual(primero["total_proveedores"], 1)

        segundo = self.modulo.registrar(self.con(nombre="Envases del Sur", entrego="si",
                                                 huella_declarada="0,85", unidad="kg CO2e por kg",
                                                 calidad="verificado",
                                                 certificaciones="ISO 14001")).resultado
        self.assertEqual(segundo["total_proveedores"], 1, "no debe duplicar al mismo proveedor")
        self.assertEqual(segundo["proveedor"]["estado"], "con datos")
        self.assertEqual(segundo["proveedor"]["calidad_dato"], "verificado")
        self.assertEqual(segundo["proveedor"]["certificaciones"], ["ISO 14001"])
        self.assertEqual(segundo["proveedor"]["gasto_anual"], 18000000.0, "no debe perder el gasto")
        self.assertEqual(len(segundo["proveedor"]["bitacora"]), 2)

    def test_calidad_de_dato_invalida_ofrece_las_validas(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.registrar(self.con(nombre="Envases del Sur", entrego="si", calidad="excelente"))
        self.assertIn("estimado", contexto.exception.sugerencia)
        self.assertIn("verificado", contexto.exception.sugerencia)

    def test_evaluar_pone_primero_al_grande_que_no_entrega_datos(self):
        self._cargar_tres()
        resultado = self.modulo.evaluar(self.opciones).resultado
        self.assertEqual(resultado["total"], 3)
        self.assertEqual(resultado["con_datos"], 1)
        self.assertEqual(resultado["proveedores"][0]["nombre"], "Transportes Norte")
        self.assertEqual(resultado["proveedores"][0]["prioridad"], "alta")
        self.assertEqual(resultado["foco_de_esta_semana"], ["Transportes Norte"])
        chicos = [p for p in resultado["proveedores"] if p["nombre"] == "Insumos Menores"][0]
        self.assertFalse(chicos["explica_80_pct"])
        self.assertEqual(chicos["prioridad"], "baja")
        self.assertEqual(resultado["explican_80_pct"], 2)

    def test_evaluar_sin_proveedores_dice_como_empezar(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.evaluar(self.opciones)
        self.assertIn("proveedores registrar", contexto.exception.sugerencia)

    def test_informe_de_la_cadena_se_escribe_en_html(self):
        self._cargar_tres()
        respuesta = self.modulo.informe_html(self.opciones)
        archivo = respuesta.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("Transportes Norte", html)
        self.assertIn("cadena de suministro", html.lower())
        self.assertEqual(respuesta.resultado["cobertura_del_impacto_pct"], 66.2)


# --------------------------------------------------------------------------
# Academia
# --------------------------------------------------------------------------

class PruebaCatalogoAcademia(unittest.TestCase):
    def setUp(self):
        from modulos import academia
        self.modulo = academia
        self.lecciones = academia.cargar_lecciones()

    def test_hay_al_menos_cuatro_rutas_de_cuatro_a_seis_lecciones(self):
        cursos = self.modulo.cursos({})
        self.assertGreaterEqual(cursos["total_cursos"], 4)
        for ficha in cursos["cursos"]:
            self.assertGreaterEqual(ficha["lecciones"], 4, ficha["curso"])
            self.assertLessEqual(ficha["lecciones"], 6, ficha["curso"])
            self.assertGreater(ficha["minutos_total"], 0, ficha["curso"])

    def test_cada_leccion_trae_contenido_y_una_pregunta_resoluble(self):
        for leccion in self.lecciones:
            etiqueta = "%s / %s" % (leccion["curso"], leccion["leccion"])
            self.assertTrue(leccion["objetivo"], etiqueta)
            self.assertGreater(len(leccion["contenido_clave"]), 200, etiqueta)
            self.assertTrue(leccion["pregunta"].endswith("?"), etiqueta)
            self.assertGreaterEqual(len(leccion["opciones"]), 3, etiqueta)
            self.assertIn(leccion["respuesta_correcta"], leccion["opciones"], etiqueta)
            self.assertTrue(leccion["explicacion"], etiqueta)

    def test_curso_inexistente_ofrece_la_lista(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.cursos({"curso": "inventado"})
        self.assertIn("Fundamentos ESG", contexto.exception.sugerencia)

    def test_una_leccion_sola_llega_con_todo_lo_necesario_para_ensenarla(self):
        detalle = self.modulo.cursos({"curso": "Huella de carbono", "leccion": "2"})
        leccion = detalle["leccion"]
        self.assertEqual(leccion["numero"], 2)
        self.assertIn("contenido_clave", leccion)
        self.assertIn("explicacion", leccion)


class PruebaAcademia(BaseGestion):
    def setUp(self):
        super(PruebaAcademia, self).setUp()
        from modulos import academia
        self.modulo = academia

    def _completar_curso(self, persona="Ana Perez", area="Operaciones", curso="Fundamentos ESG"):
        ficha = self.modulo.cursos({"curso": curso})
        ultima = None
        for leccion in ficha["lecciones"]:
            ultima = self.modulo.avance(self.con(persona=persona, area=area, curso=curso,
                                                 leccion=str(leccion["numero"]),
                                                 respuesta=leccion["respuesta_correcta"]))
        return ultima

    def test_avance_corrige_la_respuesta_y_cuenta_lo_que_falta(self):
        ficha = self.modulo.cursos({"curso": "Fundamentos ESG"})
        primera = ficha["lecciones"][0]
        equivocada = [k for k in primera["opciones"] if k != primera["respuesta_correcta"]][0]

        mala = self.modulo.avance(self.con(persona="Ana Perez", area="Operaciones",
                                           curso="Fundamentos ESG", leccion="1", respuesta=equivocada))
        self.assertEqual(mala.resultado["avance"]["resultado"], "incorrecto")
        self.assertIn("aprenda", " ".join(mala.advertencias))
        self.assertTrue(mala.resultado["explicacion"])
        self.assertEqual(mala.resultado["completadas"], 1)
        self.assertEqual(len(mala.resultado["pendientes"]), len(ficha["lecciones"]) - 1)

        buena = self.modulo.avance(self.con(persona="Ana Perez", curso="Fundamentos ESG",
                                            leccion="1", respuesta=primera["respuesta_correcta"]))
        self.assertEqual(buena.resultado["avance"]["resultado"], "correcto")
        self.assertEqual(buena.resultado["completadas"], 1, "repetir la leccion no la duplica")
        self.assertEqual(buena.resultado["avance"]["area"], "Operaciones", "recuerda el area anterior")

    def test_avance_rechaza_una_alternativa_que_no_existe(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.avance(self.con(persona="Ana Perez", curso="Fundamentos ESG",
                                        leccion="1", respuesta="z"))
        self.assertIn("alternativas", contexto.exception.sugerencia)

    def test_avance_exige_persona_curso_y_leccion(self):
        with self.assertRaises(Problema):
            self.modulo.avance(self.con(curso="Fundamentos ESG", leccion="1"))
        with self.assertRaises(Problema):
            self.modulo.avance(self.con(persona="Ana Perez", leccion="1"))
        with self.assertRaises(Problema):
            self.modulo.avance(self.con(persona="Ana Perez", curso="Fundamentos ESG"))

    def test_certificado_pide_terminar_el_curso_antes_de_emitirlo(self):
        self.modulo.avance(self.con(persona="Ana Perez", curso="Fundamentos ESG",
                                    leccion="1", respuesta="b"))
        with self.assertRaises(Problema) as contexto:
            self.modulo.certificado(self.con(persona="Ana Perez", curso="Fundamentos ESG"))
        self.assertIn("faltan", contexto.exception.mensaje.lower())
        self.assertTrue(contexto.exception.sugerencia)

    def test_certificado_en_html_y_en_word_avisa_que_no_es_oficial(self):
        self._completar_curso()
        html = self.modulo.certificado(self.con(persona="Ana Perez", curso="Fundamentos ESG"))
        documento = self.modulo.certificado(self.con(persona="Ana Perez", curso="Fundamentos ESG",
                                                     formato="word", fecha="2026-09-16"))
        self.assertTrue(os.path.isfile(html.resultado["archivo"]))
        self.assertTrue(html.resultado["archivo"].endswith(".html"))
        self.assertTrue(os.path.isfile(documento.resultado["archivo"]))
        self.assertTrue(documento.resultado["archivo"].endswith(".docx"))
        self.assertEqual(documento.resultado["fecha"], "2026-09-16")
        with open(html.resultado["archivo"], encoding="utf-8") as origen:
            contenido = origen.read()
        self.assertIn("Ana Perez", contenido)
        self.assertIn("registro interno de capacitacion", contenido)
        self.assertIn("No es una certificacion oficial", " ".join(html.advertencias))

    def test_certificado_en_formato_desconocido_explica_las_opciones(self):
        self._completar_curso()
        with self.assertRaises(Problema) as contexto:
            self.modulo.certificado(self.con(persona="Ana Perez", curso="Fundamentos ESG",
                                             formato="pdf"))
        self.assertIn("html", contexto.exception.sugerencia)

    def test_ranking_por_persona_y_por_area_con_aviso_de_trato(self):
        self._completar_curso()
        self.modulo.avance(self.con(persona="Beto Soto", area="Finanzas", curso="Huella de carbono",
                                    leccion="1", respuesta="a"))

        personas = self.modulo.ranking(self.con(por="persona"))
        nombres = [f["nombre"] for f in personas.resultado["filas"]]
        self.assertEqual(nombres[0], "Ana Perez", "arriba va quien mas avanzo")
        self.assertEqual(personas.resultado["filas"][0]["cursos_completos"], 1)
        self.assertEqual(personas.resultado["filas"][1]["lecciones_completadas"], 1)
        self.assertIn("en privado", " ".join(personas.advertencias))

        areas = self.modulo.ranking(self.con(por="area"))
        self.assertEqual(areas.resultado["agrupado_por"], "area")
        self.assertEqual({f["nombre"] for f in areas.resultado["filas"]}, {"Operaciones", "Finanzas"})

    def test_ranking_sin_avances_no_falla(self):
        vacio = self.modulo.ranking(self.con(por="persona"))
        self.assertEqual(vacio.resultado["total"], 0)
        self.assertIn("Todavia nadie", vacio.resultado["mensaje"])


# --------------------------------------------------------------------------
# CRM
# --------------------------------------------------------------------------

class PruebaCrm(BaseGestion):
    def setUp(self):
        super(PruebaCrm, self).setUp()
        from modulos import crm
        self.modulo = crm

    def _dos_prospectos(self):
        self.modulo.registrar(self.con(prospecto="Vina Los Robles", contacto="Marta Diaz",
                                       sector="Vitivinicola", tamano="mediana", origen="recomendacion",
                                       necesidad="un cliente europeo le pide la huella",
                                       estado="nuevo", hoy="2026-09-01"))
        self.modulo.registrar(self.con(prospecto="Pesquera Austral", contacto="Jorge Rivas",
                                       sector="Pesca", origen="feria", necesidad="reporte GRI",
                                       estado="propuesta", valor_estimado="4500000", hoy="2026-09-14"))

    def test_registrar_y_listar_el_embudo(self):
        self._dos_prospectos()
        listado = self.modulo.listar(self.con(hoy="2026-09-16"))
        self.assertEqual(listado["total"], 2)
        self.assertEqual(listado["por_estado"]["nuevo"], 1)
        self.assertEqual(listado["por_estado"]["propuesta"], 1)
        self.assertEqual(listado["prospectos"][0]["id"], "CRM-0001")
        self.assertEqual(listado["prospectos"][0]["dias_sin_movimiento"], 15)
        self.assertEqual(len(listado["estados_del_embudo"]), 7)

        filtrado = self.modulo.listar(self.con(estado="propuesta", hoy="2026-09-16"))
        self.assertEqual(filtrado["total"], 1)
        self.assertEqual(filtrado["prospectos"][0]["empresa"], "Pesquera Austral")

    def test_registrar_sin_nombre_explica_la_diferencia_con_empresa(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.registrar(self.opciones)
        self.assertIn("--prospecto", contexto.exception.sugerencia)
        self.assertIn("espacio de trabajo", contexto.exception.sugerencia)

    def test_no_se_registra_dos_veces_el_mismo_prospecto(self):
        self._dos_prospectos()
        with self.assertRaises(Problema) as contexto:
            self.modulo.registrar(self.con(prospecto="vina los robles"))
        self.assertIn("CRM-0001", contexto.exception.mensaje)
        self.assertIn("crm mover", contexto.exception.sugerencia)

    def test_estado_desconocido_ofrece_los_del_embudo(self):
        with self.assertRaises(Problema) as contexto:
            self.modulo.registrar(self.con(prospecto="Otra Empresa", estado="tibio"))
        self.assertIn("negociacion", contexto.exception.sugerencia)

    def test_mover_cambia_el_estado_y_deja_bitacora(self):
        self._dos_prospectos()
        movido = self.modulo.mover(self.con(prospecto="CRM-0001", estado="contactado",
                                            nota="llamada inicial", hoy="2026-09-16"))
        self.assertEqual(movido.resultado["estado_anterior"], "nuevo")
        self.assertEqual(movido.resultado["estado"], "contactado")
        self.assertTrue(movido.resultado["siguiente_paso"])
        bitacora = movido.resultado["bitacora"]
        self.assertEqual(bitacora[-1]["nota"], "llamada inicial")
        self.assertEqual(bitacora[-1]["de"], "nuevo")

        listado = self.modulo.listar(self.con(hoy="2026-09-16"))
        self.assertEqual(listado["por_estado"]["contactado"], 1)
        self.assertEqual(listado["por_estado"]["nuevo"], 0)

    def test_cerrar_como_perdido_exige_anotar_la_razon(self):
        self._dos_prospectos()
        with self.assertRaises(Problema) as contexto:
            self.modulo.mover(self.con(prospecto="CRM-0002", estado="perdido"))
        self.assertIn("por que", contexto.exception.mensaje)
        cerrado = self.modulo.mover(self.con(prospecto="CRM-0002", estado="perdido",
                                             nota="lo haran con equipo propio", hoy="2026-09-20"))
        self.assertEqual(cerrado.resultado["estado"], "perdido")
        self.assertIn("cerrado", " ".join(cerrado.advertencias))

    def test_prospecto_inexistente_ofrece_los_registrados(self):
        self._dos_prospectos()
        with self.assertRaises(Problema) as contexto:
            self.modulo.mover(self.con(prospecto="CRM-9999", estado="contactado"))
        self.assertIn("Pesquera Austral", contexto.exception.sugerencia)

    def test_siguiente_ordena_por_tiempo_sin_movimiento(self):
        self._dos_prospectos()
        al_dia = self.modulo.siguiente(self.con(hoy="2026-09-15")).resultado
        self.assertEqual(al_dia["para_hoy"], 1, "solo el nuevo lleva demasiado tiempo parado")

        atrasados = self.modulo.siguiente(self.con(hoy="2026-10-20")).resultado
        self.assertEqual(atrasados["total_activos"], 2)
        self.assertEqual(atrasados["acciones"][0]["empresa"], "Vina Los Robles")
        self.assertEqual(atrasados["acciones"][0]["urgencia"], "detenido")
        self.assertTrue(atrasados["acciones"][0]["accion_sugerida"])

        self.modulo.mover(self.con(prospecto="CRM-0001", estado="ganado", nota="firmaron",
                                   hoy="2026-10-20"))
        despues = self.modulo.siguiente(self.con(hoy="2026-10-20")).resultado
        self.assertEqual(despues["total_activos"], 1)
        self.assertEqual(despues["cerrados"], 1)

    def test_informe_del_embudo_se_escribe_y_guarda_la_razon_de_la_perdida(self):
        self._dos_prospectos()
        self.modulo.mover(self.con(prospecto="CRM-0002", estado="perdido", nota="precio fuera de rango",
                                   hoy="2026-09-20"))
        respuesta = self.modulo.informe_html(self.con(hoy="2026-09-30"))
        archivo = respuesta.resultado["archivo"]
        self.assertTrue(os.path.isfile(archivo))
        with open(archivo, encoding="utf-8") as origen:
            html = origen.read()
        self.assertIn("precio fuera de rango", html)
        self.assertIn("Embudo por estado", html)
        self.assertEqual(respuesta.resultado["perdidos"], 1)
        self.assertEqual(respuesta.resultado["conversion_pct"], 0.0)
        self.assertIn("datos de personas", " ".join(respuesta.advertencias))

    def test_privacidad_declarada_al_registrar(self):
        respuesta = self.modulo.registrar(self.con(prospecto="Vina Los Robles", contacto="Marta Diaz"))
        textos = " ".join(respuesta.advertencias)
        self.assertIn("se quedan en este computador", textos.lower())
        self.assertIn("necesidad detectada", textos)

    def test_todo_queda_en_el_archivo_de_seguimiento(self):
        self._dos_prospectos()
        ruta = os.path.join(self.carpeta, "empresas", "prueba-spa", "seguimiento", "crm.json")
        self.assertTrue(os.path.isfile(ruta))
        with open(ruta, encoding="utf-8") as origen:
            datos = json.load(origen)
        self.assertEqual(len(datos["prospectos"]), 2)
        self.assertEqual(datos["prospectos"][0]["necesidad"], "un cliente europeo le pide la huella")


# --------------------------------------------------------------------------
# Los tres modulos vistos desde la linea de comandos
# --------------------------------------------------------------------------

class PruebaDesdeElMotor(PruebaConCarpeta):
    def correr(self, *argumentos):
        proceso = subprocess.run([sys.executable, ESG] + [str(a) for a in argumentos],
                                 capture_output=True, text=True, encoding="utf-8")
        try:
            datos = json.loads(proceso.stdout)
        except ValueError:
            raise AssertionError("El motor no devolvio JSON.\nsalida: %s\nerror: %s"
                                 % (proceso.stdout[:600], proceso.stderr[:600]))
        return proceso.returncode, datos

    def test_los_tres_modulos_aparecen_en_la_ayuda(self):
        codigo, datos = self.correr("--ayuda")
        self.assertEqual(codigo, 0)
        modulos = datos["resultado"]["modulos"]
        for nombre, accion in (("proveedores", "evaluar"), ("academia", "certificado"), ("crm", "siguiente")):
            self.assertIn(nombre, modulos)
            self.assertIn(accion, modulos[nombre]["acciones"])
            self.assertTrue(modulos[nombre]["descripcion"])

    def test_academia_cursos_responde_sin_empresa_registrada(self):
        codigo, datos = self.correr("academia", "cursos")
        self.assertEqual(codigo, 0, datos)
        self.assertTrue(datos["ok"])
        self.assertGreaterEqual(datos["resultado"]["total_cursos"], 4)

    def test_crm_listar_en_un_espacio_vacio_no_se_cae(self):
        espacio.crear_empresa({"nombre": "Prueba SpA", "pais": "CL"}, raiz=self.carpeta)
        codigo, datos = self.correr("crm", "listar", "--raiz", self.carpeta, "--empresa", "prueba-spa")
        self.assertEqual(codigo, 0, datos)
        self.assertEqual(datos["resultado"]["total"], 0)
        self.assertIn("crm registrar", datos["resultado"]["mensaje"])


if __name__ == "__main__":
    unittest.main()
