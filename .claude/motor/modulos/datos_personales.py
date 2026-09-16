# -*- coding: utf-8 -*-
"""Proteccion de datos personales: registro de actividades de tratamiento y brechas (Ley 21.719)."""

import datetime
import json
import os
import re

from nucleo import espacio, informe, word
from nucleo.salida import Problema, Respuesta

AYUDA = ("Arma el registro de actividades de tratamiento de datos personales y revisa que falta para "
         "cumplir la Ley 21.719.")

ARCHIVO = "datos_personales.json"
FUENTE = "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md"

AVISO_PRIVACIDAD = ("Aqui se describe QUE datos se tratan, no se copian datos de personas. Nunca escribas "
                    "nombres, RUT, correos, telefonos ni fichas medicas en este registro: basta con la "
                    "categoria (por ejemplo «nombre, RUT y datos de contacto de trabajadores»).")
AVISO_LEGAL = ("Orientacion de gestion, no asesoria legal. Antes de publicar una politica de privacidad o "
               "responder a la autoridad, revisala con la asesoria juridica de la empresa.")
AVISO_VIGENCIA = ("La Ley 21.719 se publico el 13 de diciembre de 2024 y su regla de entrada en vigencia es "
                  "el primer dia del mes 24 posterior a esa publicacion, es decir el 1 de diciembre de 2026. "
                  "La regla esta verificada en el texto legal; la fecha de calendario es el resultado de "
                  "aplicarla.")
AVISO_MENOR_TAMANO = ("Durante los primeros 12 meses de vigencia, las empresas de menor tamaño (Ley 20.416) "
                      "pueden recibir amonestacion escrita en lugar de sancion. Es una ventana para ordenarse, "
                      "no una exencion.")
AVISO_DELEGADO = ("Los criterios exactos que obligan a designar un delegado de proteccion de datos en el "
                  "sector privado NO estan confirmados en la investigacion de este proyecto: hay que "
                  "confirmarlos en el texto vigente y en las instrucciones de la Agencia antes de afirmar "
                  "que la empresa esta o no obligada.")
AVISO_SIMPLIFICACION = ("El texto revisado permite simplificaciones para responsables con menos de 250 "
                        "trabajadores, pero ese umbral conviene contrastarlo con el texto final antes de "
                        "apoyarse en el.")
AVISO_PERU = ("En Peru rige la Ley 29733 con el Reglamento aprobado por el DS 016-2024-JUS: exige notificar "
              "los incidentes de seguridad en un maximo de 48 horas y designar un Oficial de Datos "
              "Personales segun el tamaño de la empresa. Los montos de multa del art. 39 de la Ley 29733 NO "
              "estan verificados en este proyecto: no los des por ciertos sin confirmarlos.")
AVISO_BORRADOR = ("Es un borrador con la estructura que pide la ley: hay que completarlo con la realidad de "
                  "la empresa y revisarlo con la asesoria juridica. No es un documento listo para publicar "
                  "ni para firmar.")

BASES_LICITUD = {
    "consentimiento": ("La persona autorizo. Debe ser libre, informado, especifico, previo e inequivoco, y "
                       "revocable en cualquier momento sin explicar por que (art. 12)."),
    "contrato": "Los datos son necesarios para celebrar o cumplir un contrato con esa persona (art. 13 c).",
    "obligacion_legal": "Una ley obliga a tratar ese dato o a conservarlo (art. 13 b).",
    "interes_legitimo": ("Hay un interes legitimo de la empresa o de un tercero que no pasa por encima de los "
                         "derechos de la persona; hay que poder justificarlo (art. 13 d)."),
    "obligaciones_economicas": ("Datos de obligaciones economicas, financieras, bancarias o comerciales "
                                "(art. 13 a)."),
    "defensa_derechos": ("Necesario para formular, ejercer o defender un derecho ante tribunales u organos "
                         "publicos (art. 13 e)."),
}

CAMPOS_ACTIVIDAD = [
    ("nombre", "Como le dicen internamente a ese tratamiento."),
    ("area", "Quien lo maneja: personas, ventas, finanzas, operaciones."),
    ("titulares", "De quienes son los datos: trabajadores, postulantes, clientes, proveedores, visitas."),
    ("categorias_datos", "Que tipo de datos, en categorias. Nunca datos reales de una persona."),
    ("finalidad", "Para que se usan, en una frase."),
    ("base_licitud", "Por que la empresa puede tratarlos: %s." % ", ".join(sorted(BASES_LICITUD))),
    ("destinatarios", "Quien accede: areas internas, contadora externa, sistema o proveedor."),
    ("donde_se_guarda", "Donde viven: planilla en un computador, sistema, nube, papel en oficina."),
    ("conservacion", "Cuanto tiempo se guardan y que pasa despues."),
    ("sale_del_pais", "Si los datos salen de Chile (nube o casa matriz en el extranjero): si o no."),
]

PREGUNTAS_GUIA = [
    "¿Que datos de personas maneja esta area? Dilo en categorias, no copies datos reales.",
    "¿Para que se usan? Una frase basta.",
    "¿Por que puede la empresa usarlos: la persona autorizo, lo pide un contrato, lo obliga una ley, "
    "o hay un interes legitimo que se pueda justificar?",
    "¿Quien puede verlos dentro de la empresa, y quien fuera (contadora, sistema, proveedor)?",
    "¿Donde quedan guardados: una planilla, un sistema, la nube, papel?",
    "¿Cuanto tiempo se guardan y que pasa cuando ya no se necesitan?",
    "¿Salen de Chile? Si el correo, el sistema o la nube estan afuera, la respuesta suele ser si.",
    "¿Hay datos sensibles ahi? Salud, licencias medicas, afiliacion sindical, huella o cara para marcar "
    "asistencia, situacion socioeconomica, origen etnico, orientacion sexual, creencias.",
]

TRATAMIENTOS_TIPICOS = [
    "Personas: contratos, liquidaciones, licencias medicas, evaluaciones.",
    "Postulantes: curriculums y procesos de seleccion que quedaron guardados.",
    "Control de asistencia: reloj con huella o reconocimiento facial (son datos biometricos).",
    "Clientes: ventas, despachos, cobranza, postventa y reclamos.",
    "Proveedores y contratistas: contactos y personas que ingresan a las instalaciones.",
    "Marketing: base de correos, formularios web, concursos.",
    "Camaras de seguridad: quien ve las imagenes y cuanto tiempo se guardan.",
    "Canal de denuncias: normalmente contiene datos sensibles.",
    "Sistemas y respaldos: quien administra, donde estan alojados y quien tiene acceso.",
]

CONTENIDOS_REGISTRO = [
    "Nombre y datos de contacto del responsable, del encargado y del delegado, si lo hay.",
    "Descripcion de las operaciones de tratamiento.",
    "Categorias de datos y de titulares.",
    "Finalidades del tratamiento.",
    "Categorias de destinatarios.",
    "Plazo de conservacion.",
    "Medidas tecnicas y organizativas de seguridad.",
]

OBLIGACIONES = [
    {"id": "deber_informacion", "titulo": "Deber de informacion",
     "pregunta": "¿Hay una politica de tratamiento de datos publicada, con fecha y version, y facil de encontrar?",
     "que_exige": ("Mantener permanentemente disponible una politica con quien es el responsable, que datos "
                   "trata, para que, con que base de licitud, quien los recibe, cuanto los conserva, si salen "
                   "del pais, como se ejercen los derechos y si hay decisiones automatizadas."),
     "que_hacer": "Redactar la politica, publicarla con fecha y version, y actualizarla cuando cambie algo.",
     "base": "Ley 21.719, art. 14 ter."},
    {"id": "seguridad", "titulo": "Seguridad de los datos",
     "pregunta": "¿Hay medidas de seguridad escritas: quien tiene acceso, claves, respaldos, cifrado?",
     "que_exige": ("Medidas tecnicas y organizativas acordes al riesgo, que aseguren confidencialidad, "
                   "integridad, disponibilidad y resiliencia. La ley menciona seudonimizacion, cifrado, "
                   "restauracion rapida y verificacion periodica de que funcionan."),
     "que_hacer": ("Listar quien accede a que, poner claves y respaldos, cerrar accesos de quien ya no "
                   "trabaja, y dejarlo por escrito."),
     "base": "Ley 21.719, art. 14 quinquies."},
    {"id": "derechos", "titulo": "Respuesta a los derechos de las personas",
     "pregunta": "¿Esta definido quien responde si alguien pide ver, corregir o eliminar sus datos, y en que plazo?",
     "que_exige": ("Atender acceso, rectificacion, supresion, oposicion, portabilidad y bloqueo de forma "
                   "expedita y gratuita. El acceso es gratuito al menos una vez por trimestre. El bloqueo "
                   "temporal tiene un plazo de respuesta de 2 dias habiles."),
     "que_hacer": "Definir un correo de contacto, un responsable, un formato de respuesta y un registro de solicitudes.",
     "base": "Ley 21.719, arts. 4 a 10 (bloqueo temporal en el art. 8 ter)."},
    {"id": "vulneraciones", "titulo": "Que hacer si hay una filtracion",
     "pregunta": "¿Hay un procedimiento escrito para cuando se filtran, pierden o roban datos?",
     "que_exige": ("Registrar la vulneracion (naturaleza, efectos, categorias de datos, numero aproximado de "
                   "personas afectadas y medidas tomadas) y notificarla por los medios mas expeditos y sin "
                   "dilaciones indebidas. Hay que avisar tambien a las personas afectadas cuando se trata de "
                   "datos sensibles, de datos de menores de 14 años o de datos financieros y bancarios."),
     "que_hacer": ("Escribir el procedimiento: quien se entera, a quien avisa, que se registra, quien "
                   "notifica y como se avisa a las personas en lenguaje simple."),
     "base": "Ley 21.719, art. 14 sexies. La ley no fija un plazo en horas: dice «sin dilaciones indebidas»."},
]

POR_OBLIGACION = {o["id"]: o for o in OBLIGACIONES}
ESTADOS = ["cumple", "parcial", "no_cumple", "no_aplica"]

# Patrones de datos personales reales que no deben quedar guardados en el registro.
PATRONES_PERSONALES = [
    (re.compile(r"[^\s@]+@[^\s@]+\.[A-Za-z]{2,}"), "un correo electronico"),
    (re.compile(r"\b\d{1,3}(?:\.\d{3})+-[\dkK]\b"), "un RUT"),
    (re.compile(r"\b\d{7,8}-[\dkK]\b"), "un RUT o documento de identidad"),
    (re.compile(r"\+\d{2}\s?9?\s?\d{4}\s?\d{4}"), "un numero de telefono"),
]


# --------------------------------------------------------------------------
# Lectura y escritura
# --------------------------------------------------------------------------

def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"actividades": [], "obligaciones": {}}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo donde guardo el registro de tratamientos esta dañado.",
                "No lo edites a mano. Puedo ayudarte a rehacerlo: son pocas preguntas por cada tratamiento.",
            )
    datos.setdefault("actividades", [])
    datos.setdefault("obligaciones", {})
    return datos


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def _si_no(valor):
    """Interpreta si / no / no se. Devuelve True, False o None."""
    texto = str(valor or "").strip().lower()
    if texto in ("si", "sí", "s", "true", "1", "verdadero"):
        return True
    if texto in ("no", "n", "false", "0", "falso"):
        return False
    return None


def _revisar_privacidad(campo, texto):
    """Evita que queden datos personales reales guardados en el registro."""
    for patron, que_es in PATRONES_PERSONALES:
        if patron.search(str(texto or "")):
            raise Problema(
                "En «%s» escribiste lo que parece %s, y aqui no se guardan datos de personas reales."
                % (campo, que_es),
                "Describe la categoria en vez del dato. Por ejemplo: «correo de contacto de clientes» en "
                "lugar del correo mismo.",
            )


# --------------------------------------------------------------------------
# Actividades de tratamiento
# --------------------------------------------------------------------------

def _faltantes(actividad):
    """Campos del registro que todavia no estan respondidos."""
    faltan = []
    for campo, ayuda in CAMPOS_ACTIVIDAD:
        if campo == "sale_del_pais":
            if actividad.get("sale_del_pais") is None:
                faltan.append({"campo": campo, "que_falta": ayuda})
            continue
        if not str(actividad.get(campo) or "").strip():
            faltan.append({"campo": campo, "que_falta": ayuda})
    return faltan


def _alto_riesgo(actividad):
    """Motivos por los que un tratamiento exigiria evaluacion de impacto (art. 15 ter)."""
    motivos = []
    if actividad.get("perfilado"):
        motivos.append("Evalua de forma sistematica a las personas con decisiones automatizadas que tienen "
                       "efectos importantes para ellas.")
    if actividad.get("masivo"):
        motivos.append("Es un tratamiento masivo o a gran escala.")
    if actividad.get("videovigilancia"):
        motivos.append("Observa o monitorea de forma sistematica una zona de acceso publico.")
    if actividad.get("datos_sensibles") and actividad.get("base_licitud") not in ("consentimiento", ""):
        motivos.append("Trata datos sensibles sin apoyarse en el consentimiento de la persona.")
    return motivos


def _resumen_actividad(actividad):
    faltan = _faltantes(actividad)
    motivos = _alto_riesgo(actividad)
    return {
        "id": actividad["id"],
        "nombre": actividad.get("nombre", ""),
        "area": actividad.get("area", ""),
        "finalidad": actividad.get("finalidad", ""),
        "base_licitud": actividad.get("base_licitud", ""),
        "datos_sensibles": bool(actividad.get("datos_sensibles")),
        "sale_del_pais": actividad.get("sale_del_pais"),
        "completa": not faltan,
        "faltantes": faltan,
        "requiere_evaluacion_impacto": bool(motivos),
        "motivos_alto_riesgo": motivos,
    }


def _buscar(datos, identificador):
    clave = espacio.texto_a_slug(identificador)
    for actividad in datos["actividades"]:
        if actividad["id"] == clave:
            return actividad
    return None


def _avisos_pais(perfil):
    avisos = []
    pais = (perfil.get("pais") or "CL").upper()
    if pais == "PE":
        avisos.append(AVISO_PERU)
    elif pais != "CL":
        avisos.append("Esta revision sigue la ley chilena (Ley 21.719). Si la empresa trata datos de "
                      "personas de otro pais, hay que revisar tambien la ley de ese pais con asesoria local.")
    if perfil.get("exporta_a_ue"):
        avisos.append("La empresa marca que exporta a la Union Europea. Si ademas trata datos de personas "
                      "que estan en Europa, se suma el reglamento europeo de proteccion de datos, que no "
                      "esta verificado en la investigacion de este proyecto: confirmalo con asesoria "
                      "especializada.")
    return avisos


def inventario(opciones):
    """Guia para armar el registro de actividades de tratamiento."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    resumenes = [_resumen_actividad(a) for a in datos["actividades"]]
    incompletas = [r for r in resumenes if not r["completa"]]

    resultado = {
        "empresa": perfil.get("nombre", ""),
        "que_es": ("El registro de actividades de tratamiento es la lista de todos los usos que la empresa "
                   "le da a datos de personas. Es obligatorio y debe estar disponible para la Agencia. "
                   "No es una base de datos: es una descripcion de cada tratamiento."),
        "como_armarlo": ("Recorre area por area. Por cada uso distinto de datos, responde las preguntas de "
                         "«preguntas_por_actividad» y guarda el resultado con: datos_personales registrar."),
        "preguntas_por_actividad": PREGUNTAS_GUIA,
        "tratamientos_tipicos_que_se_olvidan": TRATAMIENTOS_TIPICOS,
        "contenidos_minimos_del_registro": CONTENIDOS_REGISTRO,
        "bases_de_licitud": BASES_LICITUD,
        "actividades_registradas": resumenes,
        "total_actividades": len(resumenes),
        "actividades_incompletas": len(incompletas),
        "ejemplo_de_registro": ("datos_personales registrar --nombre \"Ficha de trabajadores\" "
                                "--area Personas --titulares \"trabajadores y postulantes\" "
                                "--categorias-datos \"identificacion, contacto, contrato, licencias medicas\" "
                                "--finalidad \"administrar la relacion laboral\" "
                                "--base-licitud contrato --destinatarios \"jefatura de personas y contadora "
                                "externa\" --donde-se-guarda \"carpeta del servidor y sistema de "
                                "remuneraciones\" --conservacion \"mientras dure el contrato y el plazo legal "
                                "posterior\" --sale-del-pais no --datos-sensibles si"),
        "siguiente_paso": ("Cuando esten registradas todas las actividades, pide: datos_personales evaluar. "
                           "Ahi sale cuales son de alto riesgo y que falta."),
        "guardado_en": ruta_json,
    }
    avisos = [AVISO_PRIVACIDAD, AVISO_VIGENCIA, AVISO_SIMPLIFICACION, AVISO_LEGAL] + _avisos_pais(perfil)
    if not resumenes:
        avisos.append("Todavia no hay ninguna actividad registrada: parte por el area de personas, que casi "
                      "siempre es la que tiene datos sensibles.")
    return Respuesta(resultado, advertencias=avisos, fuentes=[FUENTE])


def registrar(opciones):
    """Agrega o actualiza una actividad de tratamiento."""
    perfil, ruta, ruta_json = _contexto(opciones)
    nombre = _valor(opciones, "nombre") or _valor(opciones, "actividad")
    if not nombre:
        raise Problema(
            "Falta el nombre del tratamiento que quieres registrar.",
            "Usa --nombre con algo reconocible para el equipo, por ejemplo: "
            "--nombre \"Ficha de trabajadores\".",
        )
    base = _valor(opciones, "base_licitud").lower().replace("-", "_")
    if base and base not in BASES_LICITUD:
        raise Problema(
            "No reconozco la base de licitud «%s»." % base,
            "Usa una de estas: %s. Si no sabes cual es, pregunta por que la empresa puede usar ese dato: "
            "porque la persona autorizo (consentimiento), porque hay un contrato, porque lo exige una ley, "
            "o porque hay un interes legitimo que se pueda justificar." % ", ".join(sorted(BASES_LICITUD)),
        )

    datos = _leer(ruta_json)
    actividad = _buscar(datos, nombre)
    nueva = actividad is None
    if nueva:
        actividad = {"id": espacio.texto_a_slug(nombre), "creado_el": datetime.date.today().isoformat()}
        datos["actividades"].append(actividad)
    actividad["nombre"] = nombre

    for campo in ("area", "titulares", "categorias_datos", "finalidad", "destinatarios",
                  "donde_se_guarda", "conservacion", "notas"):
        valor = _valor(opciones, campo)
        if valor:
            _revisar_privacidad(campo, valor)
            actividad[campo] = valor
    if base:
        actividad["base_licitud"] = base
    for campo in ("sale_del_pais", "datos_sensibles", "masivo", "perfilado", "videovigilancia"):
        respuesta = _si_no(opciones.get(campo))
        if respuesta is not None:
            actividad[campo] = respuesta
    destino = _valor(opciones, "pais_destino")
    if destino:
        _revisar_privacidad("pais_destino", destino)
        actividad["pais_destino"] = destino
    actividad["actualizado_el"] = datetime.date.today().isoformat()
    _guardar(ruta_json, datos)

    resumen = _resumen_actividad(actividad)
    avisos = [AVISO_PRIVACIDAD]
    if actividad.get("datos_sensibles"):
        avisos.append("Marcaste datos sensibles. Tienen regla propia: como norma general necesitan "
                      "consentimiento expreso, y si se filtran hay que avisar siempre a las personas "
                      "afectadas (arts. 16 y 14 sexies).")
    if actividad.get("sale_del_pais"):
        avisos.append("Marcaste que los datos salen del pais. Hay que informarlo en la politica y acreditar "
                      "una garantia, por ejemplo clausulas contractuales tipo con el proveedor (art. 31).")
    if resumen["requiere_evaluacion_impacto"]:
        avisos.append("Por como lo describiste, este tratamiento entraria en los casos que exigen evaluacion "
                      "de impacto (art. 15 ter). Revisalo con: datos_personales evaluar.")
    return Respuesta(
        {"mensaje": "%s el tratamiento «%s»." % ("Registrado" if nueva else "Actualizado", nombre),
         "actividad": resumen, "total_actividades": len(datos["actividades"]),
         "guardado_en": ruta_json,
         "siguiente_paso": ("Completa lo que falta con otra llamada a registrar usando el mismo nombre."
                            if resumen["faltantes"] else "Sigue con la proxima area o pide: "
                            "datos_personales evaluar.")},
        advertencias=avisos, fuentes=[FUENTE])


# --------------------------------------------------------------------------
# Evaluacion
# --------------------------------------------------------------------------

def _estado_obligaciones(guardadas):
    estados = []
    for obligacion in OBLIGACIONES:
        guardada = guardadas.get(obligacion["id"], {})
        estados.append({
            "id": obligacion["id"],
            "titulo": obligacion["titulo"],
            "estado": guardada.get("estado") or "sin_responder",
            "pregunta": obligacion["pregunta"],
            "que_exige": obligacion["que_exige"],
            "que_hacer": obligacion["que_hacer"],
            "base": obligacion["base"],
            "nota": guardada.get("nota", ""),
        })
    return estados


def evaluar(opciones):
    """Revisa que tratamientos son de alto riesgo y que obligaciones faltan."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)

    # Las cuatro obligaciones transversales se pueden responder en la misma llamada.
    for obligacion in OBLIGACIONES:
        respuesta = _valor(opciones, obligacion["id"]).lower()
        if not respuesta:
            continue
        if respuesta not in ESTADOS:
            raise Problema(
                "La respuesta «%s» para «%s» no es una de las que entiendo." % (respuesta, obligacion["titulo"]),
                "Usa cumple, parcial, no_cumple o no_aplica. Por ejemplo: --seguridad parcial.",
            )
        entrada = datos["obligaciones"].setdefault(obligacion["id"], {})
        entrada["estado"] = respuesta
        entrada["actualizado_el"] = datetime.date.today().isoformat()
        nota = _valor(opciones, "nota")
        if nota:
            entrada["nota"] = nota

    resumenes = [_resumen_actividad(a) for a in datos["actividades"]]
    alto_riesgo = [r for r in resumenes if r["requiere_evaluacion_impacto"]]
    incompletas = [r for r in resumenes if not r["completa"]]
    sensibles = [r for r in resumenes if r["datos_sensibles"]]
    salen = [r for r in resumenes if r["sale_del_pais"]]
    obligaciones = _estado_obligaciones(datos["obligaciones"])
    pendientes = [o for o in obligaciones if o["estado"] in ("sin_responder", "no_cumple", "parcial")]

    resultado = {
        "empresa": perfil.get("nombre", ""),
        "total_actividades": len(resumenes),
        "con_evaluacion_de_impacto": [{"actividad": r["nombre"], "motivos": r["motivos_alto_riesgo"]}
                                      for r in alto_riesgo],
        "cuando_se_exige_evaluacion_de_impacto": [
            "Cuando se evalua de forma sistematica a las personas con decisiones automatizadas que tienen "
            "efectos juridicos o similares para ellas.",
            "Cuando el tratamiento es masivo o a gran escala.",
            "Cuando se observa o monitorea de forma sistematica una zona de acceso publico.",
            "Cuando se tratan datos sensibles amparandose en alguna excepcion al consentimiento.",
        ],
        "actividades_incompletas": [{"actividad": r["nombre"],
                                     "falta": [f["campo"] for f in r["faltantes"]]} for r in incompletas],
        "con_datos_sensibles": [r["nombre"] for r in sensibles],
        "salen_del_pais": [r["nombre"] for r in salen],
        "obligaciones": obligaciones,
        "obligaciones_pendientes": len(pendientes),
        "estados_validos": ESTADOS,
        "como_responder": ("Guarda el estado de cada obligacion en la misma accion, por ejemplo: "
                           "datos_personales evaluar --deber-informacion parcial --seguridad no_cumple."),
        "guardado_en": ruta_json,
        "evaluado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
    datos["ultima_evaluacion"] = resultado
    _guardar(ruta_json, datos)

    avisos = [AVISO_PRIVACIDAD, AVISO_VIGENCIA, AVISO_MENOR_TAMANO, AVISO_DELEGADO, AVISO_LEGAL]
    avisos.extend(_avisos_pais(perfil))
    if alto_riesgo:
        avisos.insert(0, "Hay %d tratamiento(s) que entrarian en los casos de evaluacion de impacto: "
                         "conviene hacerla antes de que la ley este plenamente vigente." % len(alto_riesgo))
    if not resumenes:
        avisos.append("No hay tratamientos registrados todavia: la evaluacion no puede decir mucho. "
                      "Parte con: datos_personales inventario.")
    return Respuesta(resultado, advertencias=avisos, fuentes=[FUENTE])


# --------------------------------------------------------------------------
# Documentos base en Word
# --------------------------------------------------------------------------

def _encabezado(perfil, titulo, resumen):
    nombre = perfil.get("razon_social") or perfil.get("nombre", "la empresa")
    return [
        {"tipo": "titulo", "texto": titulo, "nivel": 0},
        {"tipo": "texto", "texto": "%s — Version [__] — Fecha: ____________" % nombre},
        {"tipo": "nota", "texto": "BORRADOR. %s Todo lo que aparece entre corchetes debe completarlo la "
                                  "empresa antes de publicarlo o firmarlo." % resumen},
    ]


def _bloques_politica(perfil, datos):
    nombre = perfil.get("nombre", "la empresa")
    bloques = _encabezado(
        perfil, "Politica de tratamiento de datos personales",
        "Estructura base con los contenidos que exige el art. 14 ter de la Ley 21.719.")
    bloques.extend([
        {"tipo": "titulo", "texto": "1. Quien es responsable", "nivel": 1},
        {"tipo": "texto", "texto": ("Responsable: %s, RUT [____], domicilio [____]. Representante legal: "
                                    "[nombre y cargo]. Contacto para temas de datos personales: [correo] y "
                                    "[formulario o telefono]. Delegado de proteccion de datos: [indicar si "
                                    "existe; los criterios que obligan a designarlo en el sector privado hay "
                                    "que confirmarlos]." % nombre)},
        {"tipo": "titulo", "texto": "2. Que datos tratamos, de quienes y para que", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Tratamiento", "De quienes", "Categorias de datos", "Para que",
                                       "Base de licitud"],
         "filas": _filas_actividades(datos, ["nombre", "titulares", "categorias_datos", "finalidad",
                                             "base_licitud"], 4)},
        {"tipo": "titulo", "texto": "3. Quien recibe los datos", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar areas internas, proveedores, sistemas y organismos que reciben datos.]"},
        {"tipo": "titulo", "texto": "4. Cuanto tiempo se conservan", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar el plazo de conservacion por tratamiento y que pasa al terminar.]"},
        {"tipo": "titulo", "texto": "5. Datos que salen del pais", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar si hay transferencias a otro pais u organizacion internacional, "
                                    "a donde, y que garantia las respalda: clausulas contractuales tipo, "
                                    "normas corporativas vinculantes, consentimiento informado, cifrado o "
                                    "seudonimizacion.]")},
        {"tipo": "titulo", "texto": "6. Como protegemos los datos", "nivel": 1},
        {"tipo": "texto", "texto": ("[Describir las medidas de seguridad: control de accesos, claves, "
                                    "respaldos, cifrado, revision periodica.]")},
        {"tipo": "titulo", "texto": "7. Derechos de las personas y como ejercerlos", "nivel": 1},
        {"tipo": "lista", "items": [
            "Acceso: saber si tratamos sus datos y cuales.",
            "Rectificacion: corregir datos inexactos, desactualizados o incompletos.",
            "Supresion: pedir que se eliminen cuando corresponde.",
            "Oposicion: oponerse a ciertos tratamientos, incluidos marketing directo y perfiles.",
            "Portabilidad: llevarse los datos en un formato electronico de uso comun, cuando procede.",
            "Bloqueo temporal: suspender el uso mientras se resuelve una solicitud.",
        ]},
        {"tipo": "texto", "texto": ("Estas solicitudes son gratuitas y se presentan en [canal]. Responderemos "
                                    "en [plazo comprometido por la empresa]. Tambien puede reclamar ante la "
                                    "Agencia de Proteccion de Datos Personales.")},
        {"tipo": "titulo", "texto": "8. Decisiones automatizadas", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar si hay decisiones tomadas por un sistema sin intervencion "
                                    "humana, con que logica y que consecuencias tienen para la persona. Si "
                                    "no las hay, decirlo.]")},
        {"tipo": "titulo", "texto": "9. Vigencia y cambios", "nivel": 1},
        {"tipo": "texto", "texto": "Version [__], vigente desde [fecha]. Los cambios se publican en [lugar]."},
        {"tipo": "nota", "texto": "La politica debe estar permanentemente disponible y con fecha y version "
                                  "visibles."},
    ])
    return bloques


def _filas_actividades(datos, campos, minimo):
    """Filas de tabla con las actividades registradas y filas en blanco para completar."""
    filas = []
    for actividad in datos.get("actividades", []):
        fila = []
        for campo in campos:
            valor = actividad.get(campo)
            if isinstance(valor, bool):
                valor = "si" if valor else "no"
            fila.append(str(valor) if valor not in (None, "") else "[completar]")
        filas.append(fila)
    while len(filas) < minimo:
        filas.append(["[completar]"] + [""] * (len(campos) - 1))
    return filas


def _bloques_registro(perfil, datos):
    bloques = _encabezado(
        perfil, "Registro de actividades de tratamiento",
        "Estructura base del registro obligatorio, con los contenidos minimos del art. 30 bis letra b) de "
        "la Ley 21.719.")
    bloques.extend([
        {"tipo": "titulo", "texto": "1. Identificacion", "nivel": 1},
        {"tipo": "texto", "texto": ("Responsable: %s. Contacto: [correo]. Encargado(s) de tratamiento: "
                                    "[proveedores que tratan datos por cuenta de la empresa]. Delegado de "
                                    "proteccion de datos: [si existe]."
                                    % (perfil.get("razon_social") or perfil.get("nombre", "[____]")))},
        {"tipo": "titulo", "texto": "2. Actividades de tratamiento", "nivel": 1},
        {"tipo": "tabla",
         "columnas": ["Tratamiento", "De quienes", "Categorias de datos", "Finalidad", "Base de licitud",
                      "Quien accede", "Donde se guarda", "Conservacion", "¿Sale del pais?"],
         "filas": _filas_actividades(datos, ["nombre", "titulares", "categorias_datos", "finalidad",
                                             "base_licitud", "destinatarios", "donde_se_guarda",
                                             "conservacion", "sale_del_pais"], 5)},
        {"tipo": "titulo", "texto": "3. Medidas de seguridad", "nivel": 1},
        {"tipo": "texto", "texto": ("[Describir las medidas tecnicas y organizativas: control de accesos, "
                                    "claves, respaldos, cifrado, seudonimizacion, revision periodica. Es uno "
                                    "de los contenidos minimos del registro.]")},
        {"tipo": "titulo", "texto": "4. Transferencias fuera del pais", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Tratamiento", "Pais o servicio de destino", "Garantia aplicada"],
         "filas": [["[completar]", "", ""], ["", "", ""]]},
        {"tipo": "titulo", "texto": "5. Mantencion del registro", "nivel": 1},
        {"tipo": "texto", "texto": ("Responsable de mantenerlo actualizado: [cargo]. Se revisa [periodicidad] "
                                    "y cada vez que aparece un tratamiento nuevo. Debe estar accesible a la "
                                    "Agencia de Proteccion de Datos Personales.")},
        {"tipo": "nota", "texto": "En este registro se describen tratamientos, no se copian datos de "
                                  "personas. Los responsables con menos de 250 trabajadores podrian aplicar "
                                  "simplificaciones; ese umbral conviene confirmarlo con el texto final."},
    ])
    return bloques


def _bloques_derechos(perfil, datos):
    bloques = _encabezado(
        perfil, "Procedimiento de atencion de derechos de las personas",
        "Estructura base para responder solicitudes de acceso, rectificacion, supresion, oposicion, "
        "portabilidad y bloqueo (arts. 4 a 10 de la Ley 21.719).")
    bloques.extend([
        {"tipo": "titulo", "texto": "1. Quien puede pedir y que puede pedir", "nivel": 1},
        {"tipo": "texto", "texto": ("Cualquier persona cuyos datos trate la empresa: trabajadores, "
                                    "postulantes, clientes, proveedores, visitas. Puede pedir acceso, "
                                    "rectificacion, supresion, oposicion, portabilidad y bloqueo temporal.")},
        {"tipo": "titulo", "texto": "2. Por donde se reciben las solicitudes", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar correo, formulario u oficina, y quien las revisa.]"},
        {"tipo": "titulo", "texto": "3. Como verificamos quien pide", "nivel": 1},
        {"tipo": "texto", "texto": ("[Describir como se confirma la identidad sin pedir mas datos de los "
                                    "necesarios, y como se trata la solicitud de un tercero autorizado.]")},
        {"tipo": "titulo", "texto": "4. Pasos y plazos internos", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Paso", "Responsable", "Plazo comprometido"],
         "filas": [["Acuse de recibo", "[cargo]", "[plazo]"],
                   ["Busqueda de los datos en los sistemas", "[cargo]", "[plazo]"],
                   ["Respuesta a la persona", "[cargo]", "[plazo]"],
                   ["Bloqueo temporal mientras se resuelve", "[cargo]", "2 dias habiles (plazo legal)"],
                   ["Registro de la solicitud y su respuesta", "[cargo]", "[plazo]"]]},
        {"tipo": "nota", "texto": "El unico plazo de esta tabla que fija la ley es el del bloqueo temporal: "
                                  "2 dias habiles. Los demas los define la empresa, y la ley exige que el "
                                  "ejercicio sea expedito, agil y eficaz."},
        {"tipo": "titulo", "texto": "5. Gratuidad", "nivel": 1},
        {"tipo": "texto", "texto": ("Acceso, rectificacion, supresion y oposicion son siempre gratuitos. El "
                                    "acceso es gratuito al menos una vez por trimestre; si se pide mas "
                                    "seguido, la empresa puede cobrar solo los costos directos.")},
        {"tipo": "titulo", "texto": "6. Cuando se puede rechazar una solicitud", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar los casos en que no procede la supresion, por ejemplo cuando "
                                    "hay una obligacion legal o contractual de conservar el dato, y como se "
                                    "explica esa negativa por escrito.]")},
        {"tipo": "titulo", "texto": "7. Registro de solicitudes", "nivel": 1},
        {"tipo": "tabla", "columnas": ["N°", "Fecha", "Tipo de solicitud", "Estado", "Fecha de respuesta"],
         "filas": [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""]]},
        {"tipo": "nota", "texto": "En el registro usa un codigo o las iniciales de la persona: el registro "
                                  "de solicitudes tambien contiene datos personales."},
        {"tipo": "titulo", "texto": "8. Si la persona no queda conforme", "nivel": 1},
        {"tipo": "texto", "texto": ("Se le informa que puede reclamar ante la Agencia de Proteccion de Datos "
                                    "Personales. [Indicar como se deja constancia de esa informacion.]")},
    ])
    return bloques


DOCUMENTOS = {
    "politica-privacidad": ("politica-privacidad-borrador.docx", _bloques_politica,
                            "Politica de tratamiento de datos personales"),
    "registro-actividades": ("registro-actividades-tratamiento-borrador.docx", _bloques_registro,
                             "Registro de actividades de tratamiento"),
    "procedimiento-derechos": ("procedimiento-derechos-datos-borrador.docx", _bloques_derechos,
                               "Procedimiento de atencion de derechos"),
}


def documento(opciones):
    """Redacta un documento de proteccion de datos (politica, consentimiento o registro)."""
    perfil, ruta, ruta_json = _contexto(opciones)
    tipo = _valor(opciones, "tipo").lower()
    if not tipo:
        raise Problema(
            "Falta decir que documento quieres.",
            "Usa --tipo con uno de estos: %s." % ", ".join(sorted(DOCUMENTOS)),
        )
    if tipo not in DOCUMENTOS:
        raise Problema(
            "No tengo un documento «%s»." % tipo,
            "Documentos disponibles: %s." % ", ".join(sorted(DOCUMENTOS)),
        )
    datos = _leer(ruta_json)
    nombre, constructor, titulo = DOCUMENTOS[tipo]
    destino = espacio.ruta_de(ruta, "reportes", nombre)
    word.escribir_docx(destino, constructor(perfil, datos), titulo)
    return Respuesta(
        {"mensaje": "Borrador creado: %s." % titulo, "archivo": destino, "tipo": tipo,
         "actividades_incluidas": len(datos["actividades"]),
         "siguiente_paso": ("Completa lo que esta entre corchetes y revisalo con la asesoria juridica antes "
                            "de publicarlo.")},
        advertencias=[AVISO_BORRADOR, AVISO_PRIVACIDAD, AVISO_LEGAL], fuentes=[FUENTE])


# --------------------------------------------------------------------------
# Informe HTML
# --------------------------------------------------------------------------

ETIQUETA_ESTADO = {
    "cumple": ("verde", "Listo"),
    "parcial": ("amarillo", "A medias"),
    "no_cumple": ("rojo", "Falta"),
    "no_aplica": ("gris", "No aplica"),
    "sin_responder": ("gris", "Sin responder"),
}


def _bloques_informe(resultado, perfil):
    alto = resultado["con_evaluacion_de_impacto"]
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Tratamientos registrados", "valor": resultado["total_actividades"], "unidad": ""},
            {"etiqueta": "Con evaluacion de impacto", "valor": len(alto), "unidad": "",
             "detalle": "Entran en los casos de alto riesgo", "color": "amarillo" if alto else "verde"},
            {"etiqueta": "Fichas incompletas", "valor": len(resultado["actividades_incompletas"]),
             "unidad": "", "detalle": "Les falta algun contenido minimo"},
            {"etiqueta": "Obligaciones pendientes", "valor": resultado["obligaciones_pendientes"],
             "unidad": "de 4", "color": "rojo" if resultado["obligaciones_pendientes"] else "verde"},
        ]},
        {"tipo": "titulo", "texto": "Las cuatro obligaciones que se revisan siempre", "nivel": 2},
        {"tipo": "semaforo", "items": [
            {"etiqueta": o["titulo"], "estado": ETIQUETA_ESTADO.get(o["estado"], ("gris", ""))[0],
             "estado_texto": ETIQUETA_ESTADO.get(o["estado"], ("gris", o["estado"]))[1],
             "detalle": o["que_exige"]}
            for o in resultado["obligaciones"]]},
    ]

    if alto:
        bloques.append({"tipo": "titulo", "texto": "Tratamientos que exigirian evaluacion de impacto", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Tratamiento", "Por que"],
                        "filas": [[a["actividad"], " ".join(a["motivos"])] for a in alto]})

    if resultado["actividades_incompletas"]:
        bloques.append({"tipo": "titulo", "texto": "Fichas que falta completar", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Tratamiento", "Que falta"],
                        "filas": [[a["actividad"], ", ".join(a["falta"])]
                                  for a in resultado["actividades_incompletas"]]})

    if resultado["con_datos_sensibles"]:
        bloques.append({"tipo": "titulo", "texto": "Tratamientos con datos sensibles", "nivel": 2})
        bloques.append({"tipo": "lista", "items": resultado["con_datos_sensibles"]})
        bloques.append({"tipo": "texto", "texto": ("Son datos sensibles, entre otros, los de salud, origen "
                                                   "etnico, afiliacion sindical, creencias, vida sexual, "
                                                   "datos biometricos y la situacion socioeconomica. Como "
                                                   "norma general necesitan consentimiento expreso y, si se "
                                                   "filtran, hay que avisar siempre a las personas afectadas.")})

    if resultado["salen_del_pais"]:
        bloques.append({"tipo": "titulo", "texto": "Tratamientos con datos que salen del pais", "nivel": 2})
        bloques.append({"tipo": "lista", "items": resultado["salen_del_pais"]})
        bloques.append({"tipo": "texto", "texto": ("Hay que informarlo en la politica y respaldar la "
                                                   "transferencia con una garantia, por ejemplo clausulas "
                                                   "contractuales tipo con el proveedor.")})

    bloques.extend([
        {"tipo": "titulo", "texto": "Que hacer si hay una filtracion", "nivel": 2},
        {"tipo": "lista", "ordenada": True, "items": [
            "Contener: cortar el acceso, cambiar claves, aislar el equipo o el sistema.",
            "Registrar que paso: naturaleza del hecho, efectos, categorias de datos, numero aproximado de "
            "personas afectadas y medidas tomadas.",
            "Notificar por los medios mas expeditos y sin dilaciones indebidas; la ley chilena no fija un "
            "plazo en horas.",
            "Avisar a las personas afectadas, en lenguaje simple, cuando hay datos sensibles, datos de "
            "menores de 14 años o datos financieros y bancarios.",
            "Dejar constancia de todo: es lo que despues acredita que se actuo.",
        ]},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_VIGENCIA},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_DELEGADO},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_PRIVACIDAD},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_LEGAL},
    ])
    return bloques


def informe_html(opciones):
    """Arma el informe HTML de cumplimiento en proteccion de datos personales."""
    perfil, ruta, ruta_json = _contexto(opciones)
    # Se recalcula siempre para que el informe no quede atras de lo ultimo registrado.
    resultado = evaluar(opciones).resultado
    destino = espacio.ruta_de(ruta, "reportes", "proteccion-datos-personales.html")
    informe.escribir_html(
        destino, "Proteccion de datos personales", _bloques_informe(resultado, perfil),
        marca=perfil.get("marca") or {},
        subtitulo="%s — revisado el %s" % (perfil.get("nombre", ""), resultado.get("evaluado_el", "")))
    return Respuesta(
        {"mensaje": "Informe de proteccion de datos listo.", "archivo": destino,
         "total_actividades": resultado["total_actividades"],
         "obligaciones_pendientes": resultado["obligaciones_pendientes"]},
        advertencias=[AVISO_PRIVACIDAD, AVISO_VIGENCIA, AVISO_LEGAL] + _avisos_pais(perfil),
        fuentes=[FUENTE])


ACCIONES = {"inventario": inventario, "registrar": registrar, "evaluar": evaluar,
            "documento": documento, "informe": informe_html}
