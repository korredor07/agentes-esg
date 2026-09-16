# -*- coding: utf-8 -*-
"""Gobernanza corporativa y modelo de prevencion de delitos (Ley 20.393 / Ley 21.595)."""

import datetime
import json
import os

from nucleo import espacio, informe, word
from nucleo.salida import Problema, Respuesta

AYUDA = ("Revisa el modelo de prevencion de delitos y el gobierno corporativo, prioriza las brechas "
         "y prepara los documentos base.")

ARCHIVO = "gobernanza.json"
FUENTE = "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md"

ESTADOS = ["cumple", "parcial", "no_cumple", "no_aplica"]
FACTOR_ESTADO = {"cumple": 1.0, "parcial": 0.5, "no_cumple": 0.0}
RIESGOS = {"legal": 3, "reputacional": 2, "gestion": 1}

BLOQUES = {
    "politicas": "Politicas y reglas escritas",
    "canal_denuncias": "Canal de denuncias",
    "encargado": "Encargado de prevencion",
    "capacitacion": "Capacitacion y difusion",
    "supervision": "Supervision del modelo",
    "gobierno_corporativo": "Gobierno corporativo",
}

AVISO_LEGAL = ("Orientacion de gestion, no asesoria legal ni certificacion del modelo. La revision final "
               "la hace un abogado o la asesoria de la empresa.")
AVISO_VIGENCIA = ("La fecha exacta en que empezaron a regir las modificaciones de la Ley 21.595 a la "
                  "Ley 20.393 NO esta confirmada en fuente oficial en la investigacion de este proyecto: "
                  "confirmala con tu asesoria juridica antes de usarla como argumento o como plazo.")
AVISO_PROPORCIONAL = ("La ley pide un modelo 'en la medida exigible' al objeto social, giro, tamaño, "
                      "complejidad y recursos de la empresa (art. 4 de la Ley 20.393): una pyme no necesita "
                      "el mismo despliegue que una gran empresa, pero si dejar por escrito por que ese "
                      "alcance es el exigible.")
AVISO_OTRO_PAIS = ("Esta revision esta construida sobre la ley chilena (Ley 20.393 modificada por la "
                   "Ley 21.595). Otros paises tienen su propia ley de responsabilidad de las personas "
                   "juridicas, que no esta verificada en la investigacion de este proyecto: confirmala con "
                   "asesoria local antes de darla por cumplida.")
AVISO_BORRADOR = ("Es un borrador con la estructura que pide la ley: hay que completarlo con la realidad de "
                  "la empresa y revisarlo con la asesoria juridica. No es un documento listo para firmar.")

# Cuestionario guiado. Cada pregunta se responde con: cumple, parcial, no_cumple o no_aplica.
PREGUNTAS = [
    # ---------------------------------------------------------------- Politicas
    {"id": "codigo-etica", "bloque": "politicas", "peso": 3, "riesgo": "legal",
     "titulo": "Codigo de etica o de conducta vigente y difundido",
     "pregunta": "¿Tienen un codigo de etica o de conducta escrito, aprobado y entregado a todo el equipo?",
     "porque": "Es la base escrita del modelo y lo primero que piden un cliente grande, un banco o un fiscal.",
     "que_hacer": "Redactarlo, aprobarlo por la administracion, difundirlo y guardar el acuse de recibo.",
     "base": "Ley 20.393, art. 4 N°2 (protocolos y procedimientos de prevencion)."},
    {"id": "matriz-riesgos", "bloque": "politicas", "peso": 3, "riesgo": "legal",
     "titulo": "Matriz de riesgos de delitos del giro",
     "pregunta": ("¿Revisaron alguna vez en que partes del negocio podria cometerse un delito "
                  "(compras, ventas, permisos, residuos, pagos, contrataciones, tributario)?"),
     "porque": "La ley parte por ahi: sin identificar los riesgos, el resto del modelo no tiene a que apuntar.",
     "que_hacer": "Listar los procesos, marcar donde hay riesgo y dejar un control por cada riesgo alto.",
     "base": "Ley 20.393, art. 4 N°1 (identificacion de actividades y procesos riesgosos)."},
    {"id": "sanciones-internas", "bloque": "politicas", "peso": 2, "riesgo": "legal",
     "titulo": "Sanciones internas escritas por incumplir el modelo",
     "pregunta": "¿El reglamento interno o los contratos dicen que pasa si alguien se salta estas reglas?",
     "porque": "La ley exige que el modelo contemple sanciones internas; sin ellas el modelo queda cojo.",
     "que_hacer": "Incorporar las sanciones al reglamento interno y a los contratos de trabajo.",
     "base": "Ley 20.393, art. 4 N°2 (sanciones internas por incumplimiento)."},
    {"id": "terceros", "bloque": "politicas", "peso": 2, "riesgo": "legal",
     "titulo": "Obligaciones de cumplimiento en los contratos con terceros",
     "pregunta": ("¿Los contratos con quienes hacen gestiones a nombre de la empresa (agentes, gestores, "
                  "distribuidores, corredores) incluyen estas obligaciones?"),
     "porque": ("La responsabilidad alcanza a quien presta servicios gestionando asuntos de la empresa ante "
                "terceros, aunque no sea trabajador."),
     "que_hacer": "Agregar una clausula de cumplimiento y de denuncia a los contratos con esos terceros.",
     "base": "Ley 20.393, art. 3 (vinculo funcional con la persona juridica)."},
    # ---------------------------------------------------------- Canal denuncias
    {"id": "canal-denuncias", "bloque": "canal_denuncias", "peso": 3, "riesgo": "legal",
     "titulo": "Canal de denuncias seguro y conocido",
     "pregunta": "¿Hay una via para denunciar de forma confidencial, y la gente sabe cual es y como usarla?",
     "porque": "La ley exige canales seguros de denuncia; ademas es la principal fuente de deteccion temprana.",
     "que_hacer": ("Habilitar un correo o formulario con acceso restringido, publicarlo y explicar quien lo "
                   "revisa y en que plazo se responde."),
     "base": "Ley 20.393, art. 4 N°2 (canales seguros de denuncia)."},
    {"id": "sin-represalias", "bloque": "canal_denuncias", "peso": 2, "riesgo": "legal",
     "titulo": "Proteccion de quien denuncia",
     "pregunta": "¿Esta escrito y comunicado que no habra represalias contra quien denuncia de buena fe?",
     "porque": "Sin esa garantia el canal no se usa, y un canal que nadie usa no acredita nada.",
     "que_hacer": "Dejarlo por escrito en la politica del canal y repetirlo cada vez que se difunde.",
     "base": "Ley 20.393, art. 4 N°2; se conecta con el protocolo de la Ley 21.643 (Ley Karin)."},
    {"id": "investigacion-interna", "bloque": "canal_denuncias", "peso": 2, "riesgo": "gestion",
     "titulo": "Procedimiento escrito para investigar una denuncia",
     "pregunta": "¿Esta escrito quien investiga una denuncia, en que plazos y como se deja constancia?",
     "porque": "Improvisar la investigacion es lo que despues no resiste una revision externa.",
     "que_hacer": "Escribir el procedimiento: recepcion, resguardos, investigacion, decision y registro.",
     "base": "Ley 20.393, art. 4 N°2 (procedimientos de deteccion)."},
    # ------------------------------------------------------------- Encargado
    {"id": "encargado", "bloque": "encargado", "peso": 3, "riesgo": "legal",
     "titulo": "Encargado de prevencion designado por escrito",
     "pregunta": "¿Hay una persona designada por escrito como responsable de que esto funcione?",
     "porque": "La ley exige uno o mas responsables de aplicar los protocolos; sin nombre no hay modelo.",
     "que_hacer": "Designarlo por acta o carta de la administracion, con sus funciones y su periodo.",
     "base": "Ley 20.393, art. 4 N°3 (sujetos responsables de la aplicacion)."},
    {"id": "independencia", "bloque": "encargado", "peso": 2, "riesgo": "legal",
     "titulo": "Independencia y acceso directo a la administracion",
     "pregunta": "¿Esa persona puede hablar directo con la gerencia o el directorio, sin pedir permiso a su jefatura?",
     "porque": "La ley pide independencia, facultades efectivas de direccion y supervision, y acceso directo.",
     "que_hacer": "Dejar por escrito el reporte directo y una reunion periodica con la administracion.",
     "base": "Ley 20.393, art. 4 N°3 (independencia y acceso directo a la administracion)."},
    {"id": "recursos", "bloque": "encargado", "peso": 2, "riesgo": "legal",
     "titulo": "Recursos y tiempo asignados al encargado",
     "pregunta": "¿Tiene tiempo, presupuesto o apoyo asignado para hacer la pega, y quedo registrado?",
     "porque": ("La ley obliga a proveer los medios materiales e inmateriales necesarios, considerando el "
                "tamaño y la capacidad economica de la empresa."),
     "que_hacer": "Dejar constancia de las horas, el presupuesto o el apoyo externo asignado cada año.",
     "base": "Ley 20.393, art. 4 N°3 (recursos y medios)."},
    # ---------------------------------------------------------- Capacitacion
    {"id": "capacitacion", "bloque": "capacitacion", "peso": 2, "riesgo": "legal",
     "titulo": "Capacitacion al equipo con registro de asistencia",
     "pregunta": "¿Se le explico al equipo que dice el modelo, y quedo la lista de quienes asistieron?",
     "porque": "La implementacion efectiva se acredita con evidencia, y la capacitacion es la mas facil de mostrar.",
     "que_hacer": "Hacer una charla al año por area, guardar la lista firmada y el material usado.",
     "base": "Ley 20.393, art. 4 (implementacion efectiva del modelo)."},
    {"id": "induccion", "bloque": "capacitacion", "peso": 1, "riesgo": "gestion",
     "titulo": "Induccion a quien entra a la empresa",
     "pregunta": "¿Quien entra a trabajar recibe el codigo de etica y la informacion del canal de denuncias?",
     "porque": "Es la forma mas barata de mantener el modelo vivo sin depender de campañas grandes.",
     "que_hacer": "Sumar el codigo y el canal a la carpeta de bienvenida, con firma de recepcion.",
     "base": "Ley 20.393, art. 4 N°2 (difusion de protocolos)."},
    # ---------------------------------------------------------- Supervision
    {"id": "evaluacion-tercero", "bloque": "supervision", "peso": 2, "riesgo": "legal",
     "titulo": "Evaluacion periodica por un tercero independiente",
     "pregunta": "¿Alguien de afuera reviso el modelo alguna vez, o esta programado que lo haga?",
     "porque": "La ley pide evaluaciones periodicas por terceros independientes.",
     "que_hacer": ("Acordar una revision externa proporcional al tamaño: puede ser la asesoria contable o "
                   "juridica, con un informe corto y fechado."),
     "base": "Ley 20.393, art. 4 N°4 (evaluaciones periodicas por terceros independientes)."},
    {"id": "actualizacion", "bloque": "supervision", "peso": 2, "riesgo": "legal",
     "titulo": "Mecanismo de actualizacion del modelo",
     "pregunta": "¿Esta definido cada cuanto se revisa el modelo y quien lo actualiza si cambia el negocio o la ley?",
     "porque": "Un modelo escrito una vez y guardado en un cajon no acredita implementacion efectiva.",
     "que_hacer": "Fijar una revision anual con responsable y dejar acta de cada actualizacion.",
     "base": "Ley 20.393, art. 4 N°4 (mecanismos de perfeccionamiento y actualizacion)."},
    {"id": "evidencia-operando", "bloque": "supervision", "peso": 3, "riesgo": "legal",
     "titulo": "Evidencia de que el modelo esta operando",
     "pregunta": "¿Existen actas, registros o reportes que muestren que esto se usa, y no solo que esta escrito?",
     "porque": "La ley no exige tener el documento: exige que el modelo este implementado de manera efectiva.",
     "que_hacer": "Guardar actas, reportes del encargado, registros de capacitacion y casos del canal.",
     "base": "Ley 20.393, arts. 3 y 4 (falta de implementacion efectiva como base de la responsabilidad)."},
    # ------------------------------------------------------ Gobierno corporativo
    {"id": "organo-revision", "bloque": "gobierno_corporativo", "peso": 2, "riesgo": "gestion",
     "titulo": "Alguien revisa el cumplimiento de forma periodica",
     "pregunta": "¿El directorio, un comite o la dueña o dueño revisan estos temas al menos una vez al año?",
     "porque": "Sin una instancia que lo mire, el modelo se cae apenas cambia la persona a cargo.",
     "que_hacer": "Agendar un punto anual de cumplimiento en la reunion de administracion y dejar acta.",
     "base": "Ley 20.393, art. 4 N°3 (acceso directo a la administracion) y practica de gobierno corporativo."},
    {"id": "conflictos-interes", "bloque": "gobierno_corporativo", "peso": 2, "riesgo": "reputacional",
     "titulo": "Politica de conflictos de interes",
     "pregunta": "¿Las personas con poder de decision declaran sus relaciones con proveedores, clientes o parientes?",
     "porque": "Es la brecha mas comun en empresas familiares y la primera que revisa un cliente grande.",
     "que_hacer": "Pedir una declaracion anual simple y definir que se hace cuando aparece un conflicto.",
     "base": "Ley 20.393, art. 4 N°2; NCG 461 de la CMF en materia de etica y cumplimiento."},
    {"id": "memoria-cmf", "bloque": "gobierno_corporativo", "peso": 2, "riesgo": "legal",
     "titulo": "Gobierno corporativo y sostenibilidad en la memoria anual (NCG 461)",
     "pregunta": ("Si la empresa es supervisada por la CMF: ¿la memoria anual informa directorio, comites, "
                  "gestion de riesgos, etica y cumplimiento como pide la NCG 461?"),
     "porque": "La NCG 461 convirtio la memoria anual en un reporte integrado con esos contenidos.",
     "que_hacer": "Mapear las 8 areas de contenido de la NCG 461 contra la memoria actual y cerrar las brechas.",
     "base": "NCG 461 de la CMF (2021), modificada por la NCG 519 (2024).",
     "cuando_aplica": "Solo para entidades supervisadas por la CMF. Si no lo es, responde no_aplica."},
    {"id": "seleccion-directores", "bloque": "gobierno_corporativo", "peso": 1, "riesgo": "legal",
     "titulo": "Politica de cuota de genero y proceso de seleccion de directores",
     "pregunta": ("Si la empresa es supervisada por la CMF: ¿tiene politica de cuota de genero en el directorio "
                  "y describe como elige a sus directores?"),
     "porque": "La NCG 519 agrego esa divulgacion a la memoria anual.",
     "que_hacer": "Acordar la politica en el directorio y describir el proceso de seleccion en la memoria.",
     "base": "NCG 519 de la CMF (29 de octubre de 2024).",
     "cuando_aplica": "Solo para entidades supervisadas por la CMF. Si no lo es, responde no_aplica."},
]

POR_ID = {p["id"]: p for p in PREGUNTAS}


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
        return {"respuestas": {}, "ultima_revision": None}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo donde guardo las respuestas de gobernanza esta dañado.",
                "No lo edites a mano. Podemos volver a responder el cuestionario; son pocas preguntas.",
            )
    datos.setdefault("respuestas", {})
    return datos


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def _nivel(porcentaje):
    """Traduce el avance a una palabra que la persona entienda."""
    if porcentaje is None:
        return "sin revisar", "gris"
    if porcentaje >= 80:
        return "consolidado", "verde"
    if porcentaje >= 60:
        return "en marcha", "verde"
    if porcentaje >= 40:
        return "inicial", "amarillo"
    return "sin gestion", "rojo"


# --------------------------------------------------------------------------
# Evaluacion del cuestionario
# --------------------------------------------------------------------------

def _evaluar(perfil, respuestas):
    """Calcula el avance por bloque, las brechas priorizadas y lo que falta responder."""
    respuestas = respuestas or {}
    detalle = []
    for pregunta in PREGUNTAS:
        guardada = respuestas.get(pregunta["id"], {})
        estado = guardada.get("estado") or "sin_responder"
        detalle.append({
            "id": pregunta["id"],
            "bloque": pregunta["bloque"],
            "bloque_titulo": BLOQUES[pregunta["bloque"]],
            "titulo": pregunta["titulo"],
            "estado": estado,
            "nota": guardada.get("nota", ""),
            "responsable": guardada.get("responsable", ""),
            "fecha_compromiso": guardada.get("fecha_compromiso", ""),
            "prioridad": pregunta["peso"] * RIESGOS[pregunta["riesgo"]],
            "base": pregunta["base"],
            "que_hacer": pregunta["que_hacer"],
            "porque": pregunta["porque"],
        })

    por_bloque = {}
    for clave in BLOQUES:
        items = [d for d in detalle if d["bloque"] == clave and d["estado"] != "no_aplica"]
        if not items:
            por_bloque[clave] = None
            continue
        obtenido = sum(FACTOR_ESTADO.get(d["estado"], 0.0) * POR_ID[d["id"]]["peso"] for d in items)
        posible = sum(POR_ID[d["id"]]["peso"] for d in items)
        por_bloque[clave] = round(obtenido / posible * 100, 1) if posible else None

    considerados = [d for d in detalle if d["estado"] != "no_aplica"]
    obtenido = sum(FACTOR_ESTADO.get(d["estado"], 0.0) * POR_ID[d["id"]]["peso"] for d in considerados)
    posible = sum(POR_ID[d["id"]]["peso"] for d in considerados)
    avance = round(obtenido / posible * 100, 1) if posible else None

    brechas = [d for d in detalle if d["estado"] in ("no_cumple", "parcial", "sin_responder")]
    brechas.sort(key=lambda d: (-d["prioridad"], d["id"]))

    pendientes = []
    for pregunta in PREGUNTAS:
        if respuestas.get(pregunta["id"], {}).get("estado"):
            continue
        item = {
            "id": pregunta["id"],
            "bloque": BLOQUES[pregunta["bloque"]],
            "pregunta": pregunta["pregunta"],
            "porque_importa": pregunta["porque"],
            "si_no_lo_tiene": pregunta["que_hacer"],
            "base": pregunta["base"],
            "prioridad": pregunta["peso"] * RIESGOS[pregunta["riesgo"]],
        }
        if pregunta.get("cuando_aplica"):
            item["cuando_aplica"] = pregunta["cuando_aplica"]
        pendientes.append(item)
    pendientes.sort(key=lambda p: (-p["prioridad"], p["id"]))

    palabra, color = _nivel(avance)
    return {
        "empresa": perfil.get("nombre", ""),
        "pais": perfil.get("pais", ""),
        "avance_pct": avance,
        "estado": palabra,
        "color": color,
        "por_bloque": por_bloque,
        "respondidas": len(PREGUNTAS) - len(pendientes),
        "total_preguntas": len(PREGUNTAS),
        "detalle": detalle,
        "brechas": brechas,
        "preguntas_pendientes": pendientes,
        "revisado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }


def _advertencias(perfil, resultado):
    avisos = [AVISO_LEGAL, AVISO_PROPORCIONAL, AVISO_VIGENCIA]
    if (perfil.get("pais") or "CL").upper() != "CL":
        avisos.insert(0, AVISO_OTRO_PAIS)
    if resultado["preguntas_pendientes"]:
        avisos.append("Quedan %d preguntas sin responder: el avance cambia cuando se contesten."
                      % len(resultado["preguntas_pendientes"]))
    return avisos


def revisar(opciones):
    """Cuestionario guiado del modelo de prevencion y del gobierno corporativo."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = _evaluar(perfil, guardado.get("respuestas"))
    guardado["ultima_revision"] = resultado
    _guardar(ruta_json, guardado)

    liviano = {
        "empresa": resultado["empresa"],
        "avance_pct": resultado["avance_pct"],
        "estado": resultado["estado"],
        "color": resultado["color"],
        "respondidas": resultado["respondidas"],
        "total_preguntas": resultado["total_preguntas"],
        "avance_por_bloque": {BLOQUES[c]: v for c, v in resultado["por_bloque"].items()},
        "brechas_priorizadas": [{"id": b["id"], "brecha": b["titulo"], "estado": b["estado"],
                                 "prioridad": b["prioridad"], "que_hacer": b["que_hacer"],
                                 "porque": b["porque"], "base": b["base"]}
                                for b in resultado["brechas"][:8]],
        "total_brechas": len(resultado["brechas"]),
        "preguntas_pendientes": resultado["preguntas_pendientes"],
        "estados_validos": ESTADOS,
        "guardado_en": ruta_json,
        "como_responder": ("Pregunta de a una, en lenguaje cotidiano, y guarda cada respuesta con: "
                           "gobernanza responder --pregunta <id> --estado cumple|parcial|no_cumple|no_aplica."),
        "quien_queda_obligado": ("La Ley 20.393 alcanza a toda persona juridica de derecho privado, sin "
                                 "umbral de tamaño; lo que cambia con el tamaño es el alcance exigible al "
                                 "modelo, no la obligacion."),
    }
    return Respuesta(liviano, advertencias=_advertencias(perfil, resultado), fuentes=[FUENTE])


def responder(opciones):
    """Guarda la respuesta de una pregunta del cuestionario."""
    perfil, ruta, ruta_json = _contexto(opciones)
    pregunta = _valor(opciones, "pregunta") or _valor(opciones, "id")
    estado = _valor(opciones, "estado")
    if not pregunta:
        raise Problema(
            "Falta decir que pregunta estas respondiendo.",
            "Usa --pregunta con su identificador, por ejemplo: --pregunta canal-denuncias. "
            "La lista completa sale con: gobernanza revisar.",
        )
    if pregunta not in POR_ID:
        raise Problema(
            "No conozco la pregunta «%s»." % pregunta,
            "Preguntas disponibles: %s." % ", ".join(sorted(POR_ID)),
        )
    if estado not in ESTADOS:
        raise Problema(
            "Falta el estado de la respuesta o no es uno de los que entiendo.",
            "Usa --estado con: cumple, parcial, no_cumple o no_aplica. "
            "«parcial» sirve cuando existe algo pero incompleto o sin difundir.",
        )

    guardado = _leer(ruta_json)
    entrada = guardado.setdefault("respuestas", {}).setdefault(pregunta, {})
    entrada["estado"] = estado
    entrada["actualizado_el"] = datetime.date.today().isoformat()
    for campo in ("nota", "responsable", "fecha_compromiso"):
        valor = _valor(opciones, campo)
        if valor:
            entrada[campo] = valor
    _guardar(ruta_json, guardado)
    return {"mensaje": "Respuesta guardada para «%s»: %s." % (POR_ID[pregunta]["titulo"], estado),
            "pregunta": pregunta, "estado": estado,
            "siguiente_paso": "Cuando termines de responder, pide: gobernanza revisar."}


# --------------------------------------------------------------------------
# Documentos base en Word
# --------------------------------------------------------------------------

def _encabezado(perfil, titulo, resumen):
    nombre = perfil.get("razon_social") or perfil.get("nombre", "la empresa")
    return [
        {"tipo": "titulo", "texto": titulo, "nivel": 0},
        {"tipo": "texto", "texto": "%s — Version [__] — Fecha de aprobacion: ____________" % nombre},
        {"tipo": "nota", "texto": "BORRADOR. %s Todo lo que aparece entre corchetes debe completarlo la "
                                  "empresa antes de aprobarlo o firmarlo." % resumen},
    ]


def _bloques_codigo_etica(perfil):
    nombre = perfil.get("nombre", "la empresa")
    bloques = _encabezado(
        perfil, "Codigo de etica y conducta",
        "Estructura base de un codigo de etica dentro de un modelo de prevencion de delitos "
        "(Ley 20.393, art. 4 N°2).")
    bloques.extend([
        {"tipo": "titulo", "texto": "1. Proposito y a quienes aplica", "nivel": 1},
        {"tipo": "texto", "texto": ("Este codigo reune las reglas de conducta de %s. Aplica a toda persona "
                                    "que trabaja en la empresa, cualquiera sea su cargo o tipo de contrato, "
                                    "y a [indicar si aplica a contratistas, agentes, distribuidores y demas "
                                    "terceros que gestionan asuntos de la empresa ante terceros]." % nombre)},
        {"tipo": "titulo", "texto": "2. Valores y compromisos", "nivel": 1},
        {"tipo": "texto", "texto": "[Escribir en 3 a 5 frases los valores de la empresa, con palabras propias.]"},
        {"tipo": "titulo", "texto": "3. Conductas esperadas y conductas prohibidas", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Tema", "Que se espera", "Que esta prohibido"],
         "filas": [["Regalos y atenciones", "[Regla de la empresa]", "[Limite o prohibicion]"],
                   ["Relacion con funcionarios publicos", "[Regla]", "[Prohibicion]"],
                   ["Compras y proveedores", "[Regla]", "[Prohibicion]"],
                   ["Registros contables y tributarios", "[Regla]", "[Prohibicion]"],
                   ["Cumplimiento ambiental y sanitario", "[Regla]", "[Prohibicion]"],
                   ["Uso de informacion y datos personales", "[Regla]", "[Prohibicion]"],
                   ["Conflictos de interes", "[Regla]", "[Prohibicion]"]]},
        {"tipo": "titulo", "texto": "4. Conflictos de interes", "nivel": 1},
        {"tipo": "texto", "texto": ("[Definir que se entiende por conflicto de interes en esta empresa, quien "
                                    "debe declararlo, con que frecuencia y que se hace cuando aparece uno.]")},
        {"tipo": "titulo", "texto": "5. Como denunciar", "nivel": 1},
        {"tipo": "texto", "texto": ("Las dudas y las denuncias se canalizan por [indicar el canal: correo, "
                                    "formulario, telefono] a cargo de [cargo responsable]. Las denuncias se "
                                    "tratan en reserva y no habra represalias contra quien denuncie de buena fe.")},
        {"tipo": "titulo", "texto": "6. Consecuencias del incumplimiento", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar las sanciones internas segun el Reglamento Interno de Orden, "
                                    "Higiene y Seguridad y los contratos de trabajo, y quien las aplica. "
                                    "La ley exige que el modelo contemple sanciones internas.]")},
        {"tipo": "titulo", "texto": "7. Vigencia, difusion y actualizacion", "nivel": 1},
        {"tipo": "texto", "texto": ("Aprobado por [organo o cargo] el [fecha]. Se entrega a cada persona al "
                                    "ingresar y se revisa al menos [periodicidad]. Responsable de su "
                                    "actualizacion: [cargo].")},
        {"tipo": "titulo", "texto": "8. Acuse de recibo", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Nombre", "Cargo", "Fecha", "Firma"],
         "filas": [["", "", "", ""], ["", "", "", ""], ["", "", "", ""]]},
    ])
    return bloques


def _bloques_canal_denuncias(perfil):
    nombre = perfil.get("nombre", "la empresa")
    bloques = _encabezado(
        perfil, "Politica y procedimiento del canal de denuncias",
        "Estructura base del canal seguro de denuncias que exige la Ley 20.393 (art. 4 N°2).")
    bloques.extend([
        {"tipo": "titulo", "texto": "1. Para que existe este canal", "nivel": 1},
        {"tipo": "texto", "texto": ("%s pone a disposicion un canal para recibir denuncias sobre posibles "
                                    "delitos, incumplimientos del codigo de etica o conductas contrarias a "
                                    "sus reglas internas." % nombre)},
        {"tipo": "titulo", "texto": "2. Quienes pueden denunciar y que se puede denunciar", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar si pueden usarlo trabajadores, contratistas, proveedores y "
                                    "clientes, y que materias cubre. Si la denuncia es de acoso laboral, "
                                    "acoso sexual o violencia en el trabajo, se aplica el procedimiento de "
                                    "la Ley 21.643 (Ley Karin), con sus propios plazos.]")},
        {"tipo": "titulo", "texto": "3. Vias de denuncia", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Via", "Dato de contacto", "Quien la recibe"],
         "filas": [["Correo electronico", "[correo dedicado]", "[cargo]"],
                   ["Formulario o buzon", "[enlace o ubicacion]", "[cargo]"],
                   ["Presencial", "[lugar y horario]", "[cargo]"]]},
        {"tipo": "titulo", "texto": "4. Denuncia anonima y confidencialidad", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar si se aceptan denuncias anonimas.] El acceso al canal esta "
                                    "restringido a [cargos]. La identidad de quien denuncia se mantiene en "
                                    "reserva y solo se comparte cuando la ley lo exige.")},
        {"tipo": "titulo", "texto": "5. Prohibicion de represalias", "nivel": 1},
        {"tipo": "texto", "texto": ("No se tomara ninguna medida en contra de quien denuncie de buena fe ni "
                                    "de quien declare en una investigacion. [Indicar como se resguarda esto "
                                    "y a quien recurrir si igual ocurre.]")},
        {"tipo": "titulo", "texto": "6. Que pasa despues de la denuncia", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Paso", "Responsable", "Plazo interno comprometido"],
         "filas": [["Acuse de recibo a quien denuncia", "[cargo]", "[plazo]"],
                   ["Evaluacion inicial y medidas de resguardo", "[cargo]", "[plazo]"],
                   ["Investigacion y entrevistas", "[cargo]", "[plazo]"],
                   ["Decision y medidas", "[cargo]", "[plazo]"],
                   ["Informe al encargado de prevencion y a la administracion", "[cargo]", "[plazo]"]]},
        {"tipo": "nota", "texto": "Los plazos de esta tabla los define la empresa. No los confundas con los "
                                  "plazos legales de la Ley 21.643 (Ley Karin), que son perentorios y se "
                                  "revisan en la skill correspondiente."},
        {"tipo": "titulo", "texto": "7. Registro de denuncias", "nivel": 1},
        {"tipo": "tabla", "columnas": ["N°", "Fecha", "Materia", "Estado", "Resultado", "Fecha de cierre"],
         "filas": [["1", "", "", "", "", ""], ["2", "", "", "", "", ""], ["3", "", "", "", "", ""]]},
        {"tipo": "nota", "texto": "En el registro usa un codigo o iniciales, no nombres completos: son datos "
                                  "de personas y varios pueden ser datos sensibles."},
        {"tipo": "titulo", "texto": "8. Difusion", "nivel": 1},
        {"tipo": "texto", "texto": ("[Indicar como y cada cuanto se recuerda la existencia del canal: "
                                    "induccion, cartelera, correo, reuniones.]")},
    ])
    return bloques


def _bloques_matriz_riesgos(perfil):
    sector = perfil.get("sector") or "[giro de la empresa]"
    bloques = _encabezado(
        perfil, "Matriz de riesgos de delitos",
        "Estructura base de la identificacion de actividades y procesos con riesgo de conducta delictiva "
        "(Ley 20.393, art. 4 N°1). Los riesgos de ejemplo son solo para ordenar la conversacion.")
    bloques.extend([
        {"tipo": "titulo", "texto": "1. Alcance de la revision", "nivel": 1},
        {"tipo": "texto", "texto": ("Giro: %s. Sitios y operaciones cubiertas: [listar]. Fecha de la revision: "
                                    "[fecha]. Participantes: [nombres y cargos]." % sector)},
        {"tipo": "titulo", "texto": "2. Como se completa", "nivel": 1},
        {"tipo": "lista", "ordenada": True, "items": [
            "Lista los procesos reales de la empresa (comprar, vender, contratar, pagar, permisos, residuos).",
            "En cada proceso pregunta: si alguien quisiera hacer algo indebido aqui, ¿como lo haria?",
            "Anota que control existe hoy y cual falta.",
            "Marca probabilidad e impacto con tres niveles (bajo, medio, alto), sin inventar porcentajes.",
            "Asigna responsable y fecha a cada control que falta.",
        ]},
        {"tipo": "titulo", "texto": "3. Matriz", "nivel": 1},
        {"tipo": "tabla",
         "columnas": ["Proceso", "Que podria pasar", "Probabilidad", "Impacto", "Control actual",
                      "Control que falta", "Responsable", "Fecha"],
         "filas": [["Compras y pagos a proveedores", "[Descripcion]", "[bajo/medio/alto]", "[bajo/medio/alto]",
                    "[Control]", "[Control]", "[Cargo]", "[Fecha]"],
                   ["Tramites y permisos ante la autoridad", "", "", "", "", "", "", ""],
                   ["Gestion ambiental: emisiones, residuos y descargas", "", "", "", "", "", "", ""],
                   ["Obligaciones tributarias y aduaneras", "", "", "", "", "", "", ""],
                   ["Contratacion de personal y remuneraciones", "", "", "", "", "", "", ""],
                   ["Ventas, licitaciones y relacion con clientes", "", "", "", "", "", "", ""],
                   ["Manejo de dinero en efectivo y caja", "", "", "", "", "", "", ""],
                   ["Uso de informacion y datos personales", "", "", "", "", "", "", ""],
                   ["[Otro proceso propio del giro]", "", "", "", "", "", "", ""]]},
        {"tipo": "titulo", "texto": "4. Riesgo ambiental: revision especifica", "nivel": 1},
        {"tipo": "texto", "texto": ("La Ley 21.595 incorporo delitos ambientales al Codigo Penal, y esos "
                                    "delitos pueden gatillar la responsabilidad penal de la empresa. Revisa y "
                                    "responde por escrito: ¿toda actividad que lo requiere fue sometida a "
                                    "evaluacion de impacto ambiental? ¿se cumplen las normas de emision y las "
                                    "condiciones de la resolucion de calificacion ambiental? [Respuesta y "
                                    "evidencia.]")},
        {"tipo": "titulo", "texto": "5. Terceros que actuan por la empresa", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Tercero", "Que gestiona por la empresa", "Riesgo", "Clausula en contrato"],
         "filas": [["[Agente, gestor, distribuidor]", "", "", "[si/no]"], ["", "", "", ""]]},
        {"tipo": "titulo", "texto": "6. Conclusion y plan", "nivel": 1},
        {"tipo": "texto", "texto": ("[Resumir los tres riesgos mas altos y el plan para cerrarlos, con "
                                    "responsable y fecha. Indicar cuando se volvera a revisar esta matriz.]")},
        {"tipo": "nota", "texto": "El alcance de esta matriz debe ser proporcional al tamaño, giro, "
                                  "complejidad y recursos de la empresa, y conviene dejar escrito por que se "
                                  "eligio ese alcance."},
    ])
    return bloques


DOCUMENTOS = {
    "codigo-etica": ("codigo-etica-borrador.docx", _bloques_codigo_etica, "Codigo de etica y conducta"),
    "politica-canal-denuncias": ("politica-canal-denuncias-borrador.docx", _bloques_canal_denuncias,
                                 "Politica y procedimiento del canal de denuncias"),
    "matriz-riesgos-delitos": ("matriz-riesgos-delitos-borrador.docx", _bloques_matriz_riesgos,
                               "Matriz de riesgos de delitos"),
}


def documento(opciones):
    """Redacta un documento del modelo de prevencion de delitos."""
    perfil, ruta, _ = _contexto(opciones)
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
    nombre, constructor, titulo = DOCUMENTOS[tipo]
    destino = espacio.ruta_de(ruta, "reportes", nombre)
    word.escribir_docx(destino, constructor(perfil), titulo)
    return Respuesta(
        {"mensaje": "Borrador creado: %s." % titulo, "archivo": destino, "tipo": tipo,
         "siguiente_paso": ("Completa lo que esta entre corchetes con la realidad de la empresa y revisalo "
                            "con la asesoria juridica antes de aprobarlo.")},
        advertencias=[AVISO_BORRADOR, AVISO_LEGAL], fuentes=[FUENTE])


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
    palabra, color = _nivel(resultado["avance_pct"])
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Avance del modelo", "valor": resultado["avance_pct"], "unidad": "%",
             "detalle": "Estado: %s" % palabra, "color": color},
            {"etiqueta": "Preguntas respondidas", "valor": resultado["respondidas"],
             "unidad": "de %d" % resultado["total_preguntas"]},
            {"etiqueta": "Brechas abiertas", "valor": len(resultado["brechas"]), "unidad": "",
             "detalle": "Ordenadas por riesgo"},
        ]},
        {"tipo": "texto", "texto": ("El avance mide cuanto de la estructura que pide la ley esta hecho y "
                                    "documentado. No es una certificacion del modelo ni una opinion legal.")},
        {"tipo": "barras", "titulo": "Avance por bloque", "unidad": "%",
         "datos": [{"etiqueta": BLOQUES[clave], "valor": valor or 0}
                   for clave, valor in resultado["por_bloque"].items()]},
    ]

    if resultado["brechas"]:
        bloques.append({"tipo": "titulo", "texto": "Brechas por atender, de mayor a menor riesgo", "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Prioridad", "Brecha", "Estado", "Que hacer", "En que se basa"],
                        "numericas": [0],
                        "filas": [[b["prioridad"], b["titulo"],
                                   ETIQUETA_ESTADO.get(b["estado"], ("gris", b["estado"]))[1],
                                   b["que_hacer"], b["base"]]
                                  for b in resultado["brechas"][:12]]})

    listos = [d for d in resultado["detalle"] if d["estado"] == "cumple"]
    if listos:
        bloques.append({"tipo": "titulo", "texto": "Lo que ya esta resuelto", "nivel": 2})
        bloques.append({"tipo": "lista",
                        "items": ["%s%s" % (d["titulo"], " — " + d["nota"] if d["nota"] else "")
                                  for d in listos]})

    bloques.extend([
        {"tipo": "titulo", "texto": "Estado pregunta por pregunta", "nivel": 2},
        {"tipo": "semaforo", "items": [
            {"etiqueta": "%s — %s" % (d["bloque_titulo"], d["titulo"]),
             "estado": ETIQUETA_ESTADO.get(d["estado"], ("gris", ""))[0],
             "estado_texto": ETIQUETA_ESTADO.get(d["estado"], ("gris", d["estado"]))[1],
             "detalle": d["base"]}
            for d in resultado["detalle"]]},
        {"tipo": "titulo", "texto": "Que dice la ley, en corto", "nivel": 2},
        {"tipo": "lista", "items": [
            "Responden penalmente las personas juridicas de derecho privado, sin umbral de tamaño "
            "(Ley 20.393, art. 2).",
            "La empresa responde cuando el delito se ve favorecido o facilitado por la falta de "
            "implementacion efectiva de un modelo adecuado de prevencion (art. 3).",
            "El modelo adecuado tiene cuatro piezas (art. 4): identificar riesgos; protocolos con canal "
            "seguro de denuncias y sanciones internas; uno o mas responsables con independencia, recursos y "
            "acceso directo a la administracion; y evaluaciones periodicas por terceros independientes con "
            "actualizacion.",
            "Todo eso se exige 'en la medida exigible' al objeto social, giro, tamaño, complejidad y "
            "recursos de la empresa.",
        ]},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_VIGENCIA},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_LEGAL},
    ])
    return bloques


def informe_html(opciones):
    """Arma el informe HTML de gobernanza y prevencion de delitos."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    # Se recalcula siempre: asi el informe nunca queda atras de la ultima respuesta guardada.
    resultado = _evaluar(perfil, guardado.get("respuestas"))
    guardado["ultima_revision"] = resultado
    _guardar(ruta_json, guardado)
    destino = espacio.ruta_de(ruta, "reportes", "gobernanza-modelo-prevencion.html")
    informe.escribir_html(
        destino, "Gobernanza y modelo de prevencion de delitos", _bloques_informe(resultado, perfil),
        marca=perfil.get("marca") or {},
        subtitulo="%s — revisado el %s" % (perfil.get("nombre", ""), resultado.get("revisado_el", "")))
    return Respuesta(
        {"mensaje": "Informe de gobernanza listo.", "archivo": destino,
         "avance_pct": resultado["avance_pct"], "estado": resultado["estado"]},
        advertencias=_advertencias(perfil, resultado), fuentes=[FUENTE])


ACCIONES = {"revisar": revisar, "responder": responder, "documento": documento, "informe": informe_html}
