# -*- coding: utf-8 -*-
"""Diagnostico ESG: puntaje de madurez, brechas priorizadas y su seguimiento."""

import json
import os

from calculos import puntaje as motor_puntaje
from nucleo import espacio, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Evalua el estado ESG de la empresa, prioriza brechas y hace seguimiento de su cierre."

ARCHIVO = "diagnostico.json"
AVISO = ("El puntaje es una autoevaluacion de madurez con los datos de esta carpeta: "
         "no es una calificacion ESG de mercado ni una certificacion.")


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"respuestas": {}, "ultima_evaluacion": None}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            return json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo de seguimiento del diagnostico esta dañado.",
                "Puedo volver a evaluar desde cero; se perderian solo las respuestas manuales.",
            )


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def evaluar(opciones):
    """Calcula el puntaje ESG, el nivel de madurez y las brechas por cerrar."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = motor_puntaje.evaluar(perfil, ruta, guardado.get("respuestas"))
    guardado["ultima_evaluacion"] = resultado
    _guardar(ruta_json, guardado)

    palabra, color = motor_puntaje.nivel(resultado["puntaje_general"])
    liviano = {
        "empresa": resultado["empresa"],
        "puntaje_general": resultado["puntaje_general"],
        "nivel": palabra,
        "color": color,
        "puntajes": resultado["puntajes"],
        "listo_para_auditoria_pct": resultado["listo_para_auditoria_pct"],
        "brechas_criticas": resultado["brechas_criticas"][:5],
        "total_brechas": len(resultado["brechas"]),
        "preguntas_pendientes": resultado["preguntas_pendientes"],
        "guardado_en": ruta_json,
        "metodologia": resultado["metodologia"],
    }
    advertencias = [AVISO]
    if resultado["preguntas_pendientes"]:
        advertencias.append(
            "Quedan %d preguntas sin responder: el puntaje sube o baja cuando se contesten."
            % len(resultado["preguntas_pendientes"]))
    return Respuesta(liviano, advertencias=advertencias)


def preguntas(opciones):
    """Lista los indicadores que debe responder la persona, en orden de importancia."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    respuestas = guardado.get("respuestas", {})
    pendientes = []
    for indicador in motor_puntaje.indicadores_aplicables(perfil):
        if indicador.get("automatico"):
            continue
        actual = respuestas.get(indicador["id"], {}).get("estado")
        if actual and actual != "sin_datos":
            continue
        pendientes.append({
            "id": indicador["id"],
            "dimension": indicador["dimension"],
            "titulo": indicador["titulo"],
            "porque_importa": indicador["porque"],
            "si_no_lo_tiene": indicador["como_cerrarlo"],
            "prioridad": indicador["peso"] * motor_puntaje.RIESGOS.get(indicador["riesgo"], 1),
        })
    pendientes.sort(key=lambda p: -p["prioridad"])
    return {
        "total": len(pendientes),
        "preguntas": pendientes,
        "estados_validos": ["cumple", "parcial", "no_cumple", "no_aplica"],
        "mensaje": "Preguntalas de a una, en lenguaje simple, y guarda cada respuesta con: diagnostico responder.",
    }


def responder(opciones):
    """Guarda la respuesta a uno de los indicadores del diagnostico."""
    perfil, ruta, ruta_json = _contexto(opciones)
    indicador = opciones.get("indicador")
    estado = opciones.get("estado")
    if not indicador or indicador is True:
        raise Problema("Falta decir que indicador estas respondiendo.",
                       "Usa --indicador con el id, por ejemplo soc-karin.")
    validos = {i["id"] for i in motor_puntaje.indicadores_aplicables(perfil)}
    if indicador not in validos:
        raise Problema("No conozco el indicador «%s»." % indicador,
                       "Pide la lista con: diagnostico preguntas.")
    if not estado or estado is True or estado not in ("cumple", "parcial", "no_cumple", "no_aplica"):
        raise Problema("Falta el estado de la respuesta o no es valido.",
                       "Usa --estado con: cumple, parcial, no_cumple o no_aplica.")

    guardado = _leer(ruta_json)
    entrada = guardado.setdefault("respuestas", {}).setdefault(indicador, {})
    entrada["estado"] = estado
    for campo in ("nota", "responsable", "fecha_compromiso", "seguimiento"):
        valor = opciones.get(campo)
        if valor and valor is not True:
            entrada[campo] = valor
    _guardar(ruta_json, guardado)
    return {"mensaje": "Respuesta guardada para «%s»: %s." % (indicador, estado),
            "indicador": indicador, "estado": estado}


def brecha(opciones):
    """Cambia el seguimiento de una brecha: abierta, reconocida, pospuesta o resuelta."""
    perfil, ruta, ruta_json = _contexto(opciones)
    indicador = opciones.get("indicador")
    seguimiento = opciones.get("seguimiento")
    if not indicador or indicador is True:
        raise Problema("Falta decir de que brecha hablamos.", "Usa --indicador con su id.")
    if seguimiento not in motor_puntaje.ESTADOS_BRECHA:
        raise Problema("El seguimiento «%s» no es valido." % seguimiento,
                       "Usa: %s." % ", ".join(motor_puntaje.ESTADOS_BRECHA))
    guardado = _leer(ruta_json)
    entrada = guardado.setdefault("respuestas", {}).setdefault(indicador, {})
    entrada["seguimiento"] = seguimiento
    for campo in ("responsable", "fecha_compromiso", "nota"):
        valor = opciones.get(campo)
        if valor and valor is not True:
            entrada[campo] = valor
    _guardar(ruta_json, guardado)
    return {"mensaje": "La brecha «%s» quedo como %s." % (indicador, seguimiento),
            "indicador": indicador, "seguimiento": seguimiento}


def _bloques(resultado, perfil):
    palabra, color = motor_puntaje.nivel(resultado["puntaje_general"])
    puntajes = resultado["puntajes"]
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Puntaje general", "valor": resultado["puntaje_general"], "unidad": "/100",
             "detalle": "Nivel: %s" % palabra, "color": color},
            {"etiqueta": "Ambiental", "valor": puntajes.get("ambiental"), "unidad": "/100"},
            {"etiqueta": "Social", "valor": puntajes.get("social"), "unidad": "/100"},
            {"etiqueta": "Gobernanza", "valor": puntajes.get("gobernanza"), "unidad": "/100"},
            {"etiqueta": "Listo para auditoria", "valor": resultado["listo_para_auditoria_pct"], "unidad": "%",
             "detalle": "Indicadores con dato respaldado"},
        ]},
        {"tipo": "barras", "titulo": "Puntaje por dimension", "unidad": "/100",
         "datos": [{"etiqueta": nombre, "valor": puntajes.get(clave) or 0}
                   for clave, nombre in motor_puntaje.DIMENSIONES.items()]},
    ]

    criticas = [b for b in resultado["brechas"] if b["seguimiento"] != "resuelta"][:10]
    if criticas:
        bloques.append({"tipo": "titulo", "texto": "Brechas por atender, de mayor a menor riesgo", "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Prioridad", "Brecha", "Por que importa", "Que hacer", "Seguimiento"],
                        "numericas": [0],
                        "filas": [[b["prioridad"], b["titulo"], b["porque"], b["que_hacer"], b["seguimiento"]]
                                  for b in criticas]})

    cumplidos = [i for i in resultado["indicadores"] if i["estado"] == "cumple"]
    if cumplidos:
        bloques.append({"tipo": "titulo", "texto": "Lo que ya esta resuelto", "nivel": 2})
        bloques.append({"tipo": "lista", "items": ["%s%s" % (i["titulo"], " — " + i["nota"] if i["nota"] else "")
                                                   for i in cumplidos]})

    bloques.extend([
        {"tipo": "titulo", "texto": "Como se calculo", "nivel": 2},
        {"tipo": "texto", "texto": resultado["metodologia"]},
        {"tipo": "texto", "texto": "Cada indicador vale segun su peso (1 a 3) y su estado: cumple suma todo, "
                                   "parcial la mitad, y no cumple o sin datos no suman. Los indicadores que no "
                                   "aplican al giro de la empresa salen del calculo."},
        {"tipo": "nota", "estilo": "aviso",
         "texto": "Esto es orientacion de gestion, no asesoria legal ni auditoria."},
    ])
    return bloques


def informe_html(opciones):
    """Arma el informe HTML del diagnostico ESG."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = guardado.get("ultima_evaluacion")
    if not resultado:
        resultado = motor_puntaje.evaluar(perfil, ruta, guardado.get("respuestas"))
        guardado["ultima_evaluacion"] = resultado
        _guardar(ruta_json, guardado)
    destino = espacio.ruta_de(ruta, "reportes", "diagnostico-esg.html")
    informe.escribir_html(destino, "Diagnostico ESG", _bloques(resultado, perfil),
                          marca=perfil.get("marca") or {},
                          subtitulo="%s - evaluado el %s" % (perfil.get("nombre", ""),
                                                             resultado.get("evaluado_el", "")))
    return Respuesta({"mensaje": "Diagnostico listo.", "archivo": destino,
                      "puntaje_general": resultado["puntaje_general"]},
                     advertencias=[AVISO])


ACCIONES = {"evaluar": evaluar, "preguntas": preguntas, "responder": responder,
            "brecha": brecha, "informe": informe_html}
