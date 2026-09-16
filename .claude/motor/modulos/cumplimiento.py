# -*- coding: utf-8 -*-
"""Que normativa le aplica a la empresa y en que esta al dia."""

import json
import os

from calculos import aplicabilidad
from nucleo import espacio, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Identifica que normas le aplican a la empresa, con que plazos y que arriesga si no cumple."

ARCHIVO = "cumplimiento.json"


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"respuestas": {}}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            return json.load(archivo)
        except ValueError:
            return {"respuestas": {}}


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def preguntas(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = aplicabilidad.evaluar(perfil, guardado.get("respuestas"))
    return {
        "total": len(resultado["preguntas_pendientes"]),
        "preguntas": resultado["preguntas_pendientes"],
        "respuestas_validas": ["si", "no", "no se"],
        "mensaje": ("Preguntalas de a una, en lenguaje cotidiano, y guarda cada respuesta con: "
                    "cumplimiento responder --clave <clave> --respuesta si|no."),
    }


def responder(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    clave = opciones.get("clave")
    respuesta = opciones.get("respuesta")
    validas = {p["clave"] for p in aplicabilidad.preguntas_aplicables(perfil)}
    if not clave or clave is True or clave not in validas:
        raise Problema(
            "No reconozco la pregunta «%s»." % clave,
            "Pide la lista con: cumplimiento preguntas. Claves validas: %s." % ", ".join(sorted(validas)),
        )
    if respuesta in (None, True):
        raise Problema("Falta la respuesta.", "Usa --respuesta si, no, o «no se».")
    guardado = _leer(ruta_json)
    guardado.setdefault("respuestas", {})[clave] = respuesta
    _guardar(ruta_json, guardado)
    return {"mensaje": "Respuesta guardada: %s = %s." % (clave, respuesta), "clave": clave}


def revisar(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = aplicabilidad.evaluar(perfil, guardado.get("respuestas"))
    guardado["ultima_revision"] = resultado
    _guardar(ruta_json, guardado)
    liviano = {
        "empresa": perfil.get("nombre"),
        "resumen": resultado["resumen"],
        "aplican": [{"norma": f["norma"], "riesgo": f["riesgo"], "motivo": f["motivo"],
                     "plazos": f["plazos"], "skill": f["skill"]} for f in resultado["aplican"]],
        "por_revisar": [{"norma": f["norma"], "motivo": f["motivo"]} for f in resultado["por_revisar"]],
        "preguntas_pendientes": resultado["preguntas_pendientes"],
        "no_aplican": [f["norma"] for f in resultado["no_aplican"]],
    }
    return Respuesta(liviano, advertencias=[resultado["aviso"]])


def informe_html(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = guardado.get("ultima_revision") or aplicabilidad.evaluar(perfil, guardado.get("respuestas"))

    colores = {"alto": "rojo", "medio": "amarillo", "bajo": "verde"}
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Normas que aplican", "valor": len(resultado["aplican"]), "unidad": "",
             "detalle": "Identificadas con el perfil actual"},
            {"etiqueta": "Por confirmar", "valor": len(resultado["por_revisar"]), "unidad": "",
             "detalle": "Falta un dato para decidir", "color": "amarillo"},
            {"etiqueta": "Riesgo alto", "valor": len([f for f in resultado["aplican"] if f["riesgo"] == "alto"]),
             "unidad": "", "color": "rojo"},
        ]},
        {"tipo": "titulo", "texto": "Normas que le aplican", "nivel": 2},
        {"tipo": "semaforo", "items": [
            {"etiqueta": f["norma"], "estado": colores.get(f["riesgo"], "gris"),
             "estado_texto": "Riesgo %s" % f["riesgo"], "detalle": "%s %s" % (f["motivo"], f["plazos"])}
            for f in resultado["aplican"]]},
    ]
    for ficha in resultado["aplican"]:
        bloques.append({"tipo": "titulo", "texto": ficha["norma"], "nivel": 3})
        bloques.append({"tipo": "lista", "items": ficha["que_exige"]})
        bloques.append({"tipo": "texto", "texto": "Plazos: %s Riesgo si no se cumple: %s"
                                                  % (ficha["plazos"], ficha["sancion"])})
    if resultado["por_revisar"]:
        bloques.append({"tipo": "titulo", "texto": "Falta confirmar", "nivel": 2})
        bloques.append({"tipo": "lista", "items": ["%s — %s" % (f["norma"], f["motivo"])
                                                   for f in resultado["por_revisar"]]})
    bloques.append({"tipo": "nota", "estilo": "aviso", "texto": resultado["aviso"]})

    destino = espacio.ruta_de(ruta, "reportes", "normativa-aplicable.html")
    informe.escribir_html(destino, "Normativa aplicable", bloques, marca=perfil.get("marca") or {},
                          subtitulo=perfil.get("nombre", ""))
    return Respuesta({"mensaje": "Informe de normativa aplicable listo.", "archivo": destino,
                      "aplican": len(resultado["aplican"])},
                     advertencias=[resultado["aviso"]])


ACCIONES = {"preguntas": preguntas, "responder": responder, "revisar": revisar, "informe": informe_html}
