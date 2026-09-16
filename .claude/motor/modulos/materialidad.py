# -*- coding: utf-8 -*-
"""Doble materialidad: que asuntos ESG son importantes para la empresa y por que."""

import datetime
import json
import os

from calculos import materialidad as motor_materialidad
from nucleo import espacio, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Define que asuntos ESG son importantes, por su impacto en el mundo y por su efecto en el negocio."

ARCHIVO = "materialidad.json"
DIMENSIONES = ("ambiental", "social", "gobernanza")
AVISO = motor_materialidad.AVISO

# Columnas del grafico de dispersion: del 1 al 5 en tramos de un tercio de punto.
ETIQUETAS_EJE = ["1", "", "", "2", "", "", "3", "", "", "4", "", "", "5"]


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _valor(opciones, clave, por_defecto=None):
    valor = opciones.get(clave)
    return valor if valor not in (None, True, "") else por_defecto


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"asuntos": {}, "umbral": motor_materialidad.UMBRAL_POR_DEFECTO, "ultima_evaluacion": None}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            guardado = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo donde guardo la materialidad esta dañado.",
                "Puedo volver a levantar las evaluaciones contigo; se pierden solo las notas ya puestas.",
            )
    guardado.setdefault("asuntos", {})
    guardado.setdefault("umbral", motor_materialidad.UMBRAL_POR_DEFECTO)
    return guardado


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _lista_de_asuntos(guardado):
    """Las evaluaciones guardadas como lista, en el orden en que se registraron."""
    asuntos = guardado.get("asuntos") or {}
    return [dict(valor, id=clave) for clave, valor in
            sorted(asuntos.items(), key=lambda par: par[1].get("registrado_el", ""))]


def _estado(evaluacion):
    faltan = [c for c in motor_materialidad.CRITERIOS if evaluacion.get(c) in (None, "")]
    if not faltan:
        return "evaluado"
    if len(faltan) == len(motor_materialidad.CRITERIOS):
        return "sin evaluar"
    return "a medias"


# --------------------------------------------------------------------------
# Acciones
# --------------------------------------------------------------------------

def asuntos(opciones):
    """Propone la lista inicial de asuntos segun el sector de la empresa."""
    perfil, _ruta, ruta_json = _contexto(opciones)
    sector = _valor(opciones, "sector") or perfil.get("sector") or ""
    clave, etiqueta = motor_materialidad.familia_de_sector(sector)
    propuesta = motor_materialidad.asuntos_sugeridos(sector)

    guardado = _leer(ruta_json)
    guardados = guardado.get("asuntos") or {}
    listado = []
    vistos = set()
    for asunto in propuesta:
        ficha = dict(asunto)
        ficha["estado"] = _estado(guardados.get(asunto["id"], {}))
        listado.append(ficha)
        vistos.add(asunto["id"])
    for clave_guardada, evaluacion in sorted(guardados.items()):
        if clave_guardada in vistos:
            continue
        listado.append({
            "id": clave_guardada,
            "nombre": evaluacion.get("nombre", clave_guardada),
            "dimension": evaluacion.get("dimension", ""),
            "que_impacta": "", "que_arriesga": "", "marcos": "",
            "derechos_humanos": bool(evaluacion.get("derechos_humanos")),
            "origen": "agregado por la empresa",
            "estado": _estado(evaluacion),
        })

    advertencias = [AVISO]
    if clave == "general":
        advertencias.append(
            "No reconoci el rubro a partir del sector «%s», asi que esta es la lista general. "
            "Pregunta que otros asuntos propios del negocio hay que agregar." % (sector or "sin indicar"))

    return Respuesta({
        "empresa": perfil.get("nombre"),
        "sector": sector,
        "actividad_reconocida": etiqueta,
        "total": len(listado),
        "asuntos": listado,
        "preguntas": motor_materialidad.PREGUNTAS,
        "escala": "Todas las notas van del 1 al 5: 1 es muy bajo, 3 es medio y 5 es muy alto.",
        "mensaje": ("Muestra la lista y pregunta primero que asuntos sobran y cuales faltan. Despues evalua "
                    "de a un asunto con las seis preguntas y guarda cada uno con: materialidad registrar."),
    }, advertencias=advertencias)


def registrar(opciones):
    """Guarda la evaluacion de un asunto: las cuatro notas de impacto y las dos financieras."""
    perfil, _ruta, ruta_json = _contexto(opciones)
    nombre = _valor(opciones, "asunto")
    if not nombre:
        raise Problema(
            "Falta decir que asunto estas evaluando.",
            "Usa --asunto con su nombre, por ejemplo: --asunto \"Agua: consumo y descargas\". "
            "La lista de asuntos se pide con: materialidad asuntos.",
        )

    catalogo = {a["id"]: a for a in motor_materialidad.asuntos_sugeridos(perfil.get("sector"))}
    clave = str(nombre).strip()
    if clave not in catalogo:
        por_nombre = {espacio.texto_a_slug(a["nombre"]): a for a in catalogo.values()}
        candidato = espacio.texto_a_slug(clave)
        clave = por_nombre[candidato]["id"] if candidato in por_nombre else candidato
    base = catalogo.get(clave)

    guardado = _leer(ruta_json)
    entrada = guardado.setdefault("asuntos", {}).setdefault(clave, {})
    nuevo = not entrada
    if nuevo:
        entrada["registrado_el"] = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
        entrada["nombre"] = base["nombre"] if base else str(nombre).strip()
        entrada["dimension"] = base.get("dimension", "") if base else ""
        entrada["derechos_humanos"] = bool(base.get("derechos_humanos")) if base else False
        entrada["origen"] = base.get("origen", "") if base else "agregado por la empresa"

    dimension = _valor(opciones, "dimension")
    if dimension:
        if str(dimension).strip().lower() not in DIMENSIONES:
            raise Problema(
                "El tema «%s» no es uno de los tres de siempre." % dimension,
                "Usa uno de estos: %s." % ", ".join(DIMENSIONES),
            )
        entrada["dimension"] = str(dimension).strip().lower()
    if opciones.get("derechos_humanos"):
        entrada["derechos_humanos"] = True

    entregadas = 0
    for criterio in motor_materialidad.CRITERIOS:
        crudo = _valor(opciones, criterio)
        if crudo is None:
            continue
        entrada[criterio] = motor_materialidad.valor_escala(crudo, criterio, entrada["nombre"])
        entregadas += 1
    if _valor(opciones, "nota"):
        entrada["nota"] = _valor(opciones, "nota")
    entrada["actualizado_el"] = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")

    if nuevo and not entregadas:
        del guardado["asuntos"][clave]
        raise Problema(
            "No me diste ninguna nota para «%s», asi que no guarde nada." % entrada["nombre"],
            "Cada asunto se evalua con seis notas del 1 al 5: --escala, --alcance, --irremediabilidad, "
            "--probabilidad-impacto, --magnitud-financiera y --probabilidad-financiera.",
        )

    _guardar(ruta_json, guardado)
    faltan = [motor_materialidad.OPCIONES[c] for c in motor_materialidad.CRITERIOS
              if entrada.get(c) in (None, "")]
    advertencias = []
    if faltan:
        advertencias.append("A «%s» todavia le faltan estas notas: %s. Mientras falten, el asunto no entra "
                            "en la matriz." % (entrada["nombre"], ", ".join(faltan)))
    if not base:
        advertencias.append("«%s» no estaba en la lista sugerida: lo agregue como asunto propio de la empresa."
                            % entrada["nombre"])
    return Respuesta({
        "mensaje": "Evaluacion guardada para «%s»." % entrada["nombre"],
        "asunto": clave,
        "nombre": entrada["nombre"],
        "estado": _estado(entrada),
        "faltan": faltan,
        "guardado_en": ruta_json,
        "empresa": perfil.get("nombre"),
    }, advertencias=advertencias)


def evaluar(opciones):
    """Calcula los dos puntajes de todos los asuntos guardados y marca los materiales."""
    perfil, _ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    lista = _lista_de_asuntos(guardado)
    if not lista:
        raise Problema(
            "Todavia no hay ningun asunto evaluado para esta empresa.",
            "Pide la lista con: materialidad asuntos, y guarda cada evaluacion con: materialidad registrar.",
        )
    umbral = _valor(opciones, "umbral", guardado.get("umbral"))
    resultado = motor_materialidad.evaluar(lista, umbral)
    guardado["umbral"] = resultado["umbral"]
    guardado["ultima_evaluacion"] = resultado
    guardado["evaluado_el"] = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
    _guardar(ruta_json, guardado)

    advertencias = [AVISO]
    if resultado["pendientes"]:
        advertencias.append(
            "Hay %d asunto(s) sin terminar de evaluar: %s. Quedan fuera de la matriz hasta completarlos."
            % (len(resultado["pendientes"]), ", ".join(a["nombre"] for a in resultado["pendientes"])))
    if not resultado["materiales"] and resultado["total_evaluados"]:
        advertencias.append(
            "Con el umbral %g ningun asunto quedo como material. Conversa si las notas quedaron bajas o si "
            "el umbral esta demasiado alto." % resultado["umbral"])

    return Respuesta({
        "empresa": perfil.get("nombre"),
        "umbral": resultado["umbral"],
        "resumen": resultado["resumen"],
        "total_evaluados": resultado["total_evaluados"],
        "total_materiales": resultado["total_materiales"],
        "materiales": [{"nombre": a["nombre"], "dimension": a["dimension"],
                        "puntaje_impacto": a["puntaje_impacto"], "puntaje_financiero": a["puntaje_financiero"],
                        "resultado": a["resultado"]} for a in resultado["materiales"]],
        "no_materiales": [a["nombre"] for a in resultado["no_materiales"]],
        "pendientes": [{"nombre": a["nombre"], "faltan": a["faltan"]} for a in resultado["pendientes"]],
        "por_cuadrante": resultado["por_cuadrante"],
        "guardado_en": ruta_json,
        "metodologia": resultado["metodologia"],
    }, advertencias=advertencias, fuentes=[resultado["fuente"]])


# --------------------------------------------------------------------------
# Informe
# --------------------------------------------------------------------------

def _serie_de_punto(punto):
    """Convierte un asunto en una serie de un solo punto, para dibujar la dispersion."""
    total = len(ETIQUETAS_EJE)
    posicion = (float(punto["x"]) - motor_materialidad.ESCALA_MINIMA) / (
        motor_materialidad.ESCALA_MAXIMA - motor_materialidad.ESCALA_MINIMA)
    indice = max(0, min(total - 1, int(round(posicion * (total - 1)))))
    puntos = [(ETIQUETAS_EJE[i], None) for i in range(total)]
    puntos[indice] = (ETIQUETAS_EJE[indice], punto["y"])
    return {"nombre": punto["nombre"], "color": punto["color"], "puntos": puntos}


def _bloques(resultado, matriz):
    umbral = informe.formatear_numero(resultado["umbral"], 1)
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Asuntos evaluados", "valor": resultado["total_evaluados"]},
            {"etiqueta": "Asuntos materiales", "valor": resultado["total_materiales"],
             "detalle": "Entran al reporte y al plan", "color": "verde"},
            {"etiqueta": "Importan por las dos razones", "valor": len(resultado["por_cuadrante"]["doble"]),
             "detalle": "Impacto y dinero"},
            {"etiqueta": "Umbral usado", "valor": umbral, "unidad": "de 5",
             "detalle": "Decision de la empresa"},
        ]},
        {"tipo": "texto", "texto": resultado["resumen"]},
    ]

    if matriz["puntos"]:
        bloques.append({
            "tipo": "lineas",
            "titulo": "Matriz de doble materialidad (horizontal: impacto en el mundo; vertical: efecto en el negocio)",
            "series": [_serie_de_punto(p) for p in matriz["puntos"]],
        })
        bloques.append({"tipo": "texto", "texto": matriz["leyenda"]})

    bloques.append({"tipo": "titulo", "texto": "Todos los asuntos, del mas al menos importante", "nivel": 2})
    bloques.append({
        "tipo": "tabla",
        "columnas": ["Asunto", "Tema", "Impacto en el mundo", "Efecto en el negocio", "Resultado"],
        "numericas": [2, 3],
        "nota": "Las dos columnas de puntaje van de 1 a 5. Es material el asunto que llega a %s en cualquiera "
                "de las dos." % umbral,
        "filas": [[a["nombre"], a["dimension"] or "—", a["puntaje_impacto"], a["puntaje_financiero"],
                   a["resultado"]] for a in resultado["asuntos"]],
    })

    if resultado["materiales"]:
        bloques.append({"tipo": "titulo", "texto": "Asuntos materiales: lo que hay que gestionar y reportar",
                        "nivel": 2})
        bloques.append({"tipo": "lista", "items": [
            "%s — %s (impacto %s; negocio %s)"
            % (a["nombre"], a["resultado"],
               informe.formatear_numero(a["puntaje_impacto"], 1),
               informe.formatear_numero(a["puntaje_financiero"], 1))
            for a in resultado["materiales"]]})
    else:
        bloques.append({"tipo": "nota", "estilo": "aviso",
                        "texto": "Con este umbral ningun asunto quedo como material. Revisa las notas o baja "
                                 "el umbral antes de dar por cerrado el ejercicio."})

    if resultado["pendientes"]:
        bloques.append({"tipo": "titulo", "texto": "Asuntos por terminar de evaluar", "nivel": 2})
        bloques.append({"tipo": "lista", "items": [
            "%s — faltan: %s" % (a["nombre"], ", ".join(a["faltan"])) for a in resultado["pendientes"]]})

    bloques.extend([
        {"tipo": "titulo", "texto": "Como se calculo", "nivel": 2},
        {"tipo": "texto", "texto": resultado["metodologia"]},
        {"tipo": "texto", "texto": "Un asunto es material si lo es por cualquiera de las dos vias: basta con "
                                   "una. Asi lo plantea el marco europeo de reporte de sostenibilidad."},
        {"tipo": "nota", "estilo": "aviso", "texto": resultado["aviso"]},
    ])
    return bloques


def informe_html(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    resultado = guardado.get("ultima_evaluacion")
    if not resultado:
        lista = _lista_de_asuntos(guardado)
        if not lista:
            raise Problema(
                "Todavia no hay asuntos evaluados, asi que no puedo armar la matriz.",
                "Pide la lista con: materialidad asuntos, evalua cada asunto con: materialidad registrar, "
                "y despues vuelve a pedir el informe.",
            )
        resultado = motor_materialidad.evaluar(lista, guardado.get("umbral"))
        guardado["ultima_evaluacion"] = resultado
        _guardar(ruta_json, guardado)

    matriz = motor_materialidad.matriz(resultado["asuntos"], resultado["umbral"])
    destino = espacio.ruta_de(ruta, "reportes", "doble-materialidad.html")
    informe.escribir_html(
        destino, "Doble materialidad", _bloques(resultado, matriz),
        marca=perfil.get("marca") or {},
        subtitulo="%s — %d asuntos evaluados, %d materiales"
                  % (perfil.get("nombre", ""), resultado["total_evaluados"], resultado["total_materiales"]))
    return Respuesta({
        "mensaje": "Matriz de doble materialidad lista.",
        "archivo": destino,
        "total_materiales": resultado["total_materiales"],
        "umbral": resultado["umbral"],
    }, advertencias=[AVISO], fuentes=[resultado["fuente"]])


ACCIONES = {"asuntos": asuntos, "evaluar": evaluar, "registrar": registrar, "informe": informe_html}
