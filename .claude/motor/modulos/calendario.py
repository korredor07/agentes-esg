# -*- coding: utf-8 -*-
"""Calendario anual de obligaciones: que hay que declarar y cuando.

Las fechas salen de `datos/calendario_<pais>.csv`, donde cada fila lleva su
norma y su fuente. Una obligacion se muestra cuando la empresa cumple la
condicion que la activa (por ejemplo, tener calderas o poner productos en el
mercado), tomada de las respuestas guardadas por el modulo de cumplimiento.
"""

import csv
import datetime
import json
import os

from nucleo import espacio, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Muestra el calendario de declaraciones y obligaciones del año, con lo que viene primero."

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
DIAS_AVISO = 45


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _respuestas(ruta_empresa):
    archivo = os.path.join(ruta_empresa, "seguimiento", "cumplimiento.json")
    if not os.path.isfile(archivo):
        return {}
    try:
        with open(archivo, encoding="utf-8") as origen:
            return json.load(origen).get("respuestas", {})
    except (ValueError, OSError):
        return {}


def _si(valor):
    if valor is None:
        return None
    texto = str(valor).strip().lower()
    if texto in ("si", "sí", "true", "1"):
        return True
    if texto in ("no", "false", "0"):
        return False
    return None


def cargar(pais="CL"):
    ruta = os.path.join(CARPETA_DATOS, "calendario_%s.csv" % str(pais).lower())
    if not os.path.isfile(ruta):
        raise Problema(
            "Todavia no tengo el calendario de obligaciones de %s." % pais,
            "Por ahora esta disponible el de Chile. Puedo buscar las fechas de tu pais con el agente investigador.",
        )
    filas = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            filas.append({clave: (valor or "").strip() for clave, valor in fila.items()})
    return filas


def _fecha_de(texto, anio):
    if not texto:
        return None
    try:
        mes, dia = texto.split("-")
        return datetime.date(anio, int(mes), int(dia))
    except (ValueError, TypeError):
        return None


def _estado(inicio, fin, hoy):
    if fin is None:
        return "permanente", None
    if hoy > fin:
        return "cerrado este año", (fin - hoy).days
    dias = (fin - hoy).days
    if inicio and hoy < inicio:
        # la ventana todavia no abre
        return ("se acerca" if dias <= DIAS_AVISO else "por abrir"), dias
    if dias <= 7:
        return "urgente", dias
    if inicio and inicio <= hoy <= fin:
        return "abierto", dias
    return ("se acerca" if dias <= DIAS_AVISO else "programado"), dias


def proximas(opciones):
    """Muestra que obligaciones vencen pronto y cuales ya estan abiertas."""
    perfil, ruta = _contexto(opciones)
    hoy = opciones.get("hoy")
    hoy = datetime.date.fromisoformat(hoy) if hoy and hoy is not True else datetime.date.today()
    respuestas = _respuestas(ruta)
    filas = cargar(perfil.get("pais") or "CL")

    aplican, por_confirmar, sin_fecha = [], [], []
    for fila in filas:
        condicion = fila.get("condicion")
        estado_condicion = _si(respuestas.get(condicion)) if condicion else True
        inicio = _fecha_de(fila.get("inicio"), hoy.year)
        fin = _fecha_de(fila.get("fin"), hoy.year)
        estado, dias = _estado(inicio, fin, hoy)
        ficha = {
            "id": fila["id"], "obligacion": fila["obligacion"], "sujeto": fila["sujeto"],
            "norma": fila["norma"], "skill": fila.get("skill", ""), "frecuencia": fila.get("frecuencia", ""),
            "ventana": ("%s a %s" % (fila.get("inicio") or "", fila.get("fin") or "")).strip(" a "),
            "vence": fin.isoformat() if fin else "",
            "dias_restantes": dias, "estado": estado, "notas": fila.get("notas", ""),
            "fuente": fila.get("fuente", ""),
        }
        if estado_condicion is True:
            (aplican if fin else sin_fecha).append(ficha)
        elif estado_condicion is None:
            ficha["falta_confirmar"] = condicion
            por_confirmar.append(ficha)

    orden = {"urgente": 0, "abierto": 1, "se acerca": 2, "programado": 3, "por abrir": 4, "cerrado este año": 5}
    aplican.sort(key=lambda f: (orden.get(f["estado"], 9), f["vence"]))

    if not opciones.get("sin_alertas"):
        archivo = espacio.ruta_de(ruta, "seguimiento", "alertas.json")
        otras = []
        if os.path.isfile(archivo):
            try:
                with open(archivo, encoding="utf-8") as origen:
                    otras = [a for a in json.load(origen) if a.get("origen") != "Calendario"]
            except ValueError:
                otras = []
        nuevas = [{
            "origen": "Calendario", "titulo": f["obligacion"], "vence": f["vence"],
            "estado": f["estado"], "por_vencer": f["estado"] in ("urgente", "se acerca"),
            "detalle": "%s. %s" % (f["norma"], f["notas"]),
        } for f in aplican if f["estado"] in ("urgente", "abierto", "se acerca")]
        with open(archivo, "w", encoding="utf-8") as destino:
            json.dump(otras + nuevas, destino, ensure_ascii=False, indent=2)

    urgentes = [f for f in aplican if f["estado"] in ("urgente", "abierto")]
    proximas_semanas = [f for f in aplican if f["estado"] == "se acerca"]
    return Respuesta(
        {
            "empresa": perfil.get("nombre"), "hoy": hoy.isoformat(), "pais": perfil.get("pais"),
            "obligaciones_con_fecha": aplican,
            "obligaciones_permanentes": sin_fecha,
            "por_confirmar": por_confirmar,
            "urgentes": urgentes,
            "proximas_semanas": proximas_semanas,
            "mensaje": ("Hay %d obligacion(es) abiertas o por vencer ahora." % len(urgentes) if urgentes
                        else ("Hay %d obligacion(es) que se acercan en las proximas semanas."
                              % len(proximas_semanas) if proximas_semanas
                              else "No hay obligaciones con fecha proxima.")),
        },
        advertencias=(["Quedan %d obligaciones sin confirmar: responde las preguntas de cumplimiento para "
                       "saber si le aplican." % len(por_confirmar)] if por_confirmar else []) +
                     ["Las fechas pueden cambiar por convocatoria o resolucion del año: confirmalas en el "
                      "portal del organismo antes de planificar."])


def informe_html(opciones):
    """Arma el informe HTML del calendario de obligaciones."""
    perfil, ruta = _contexto(opciones)
    datos = proximas(dict(opciones, sin_alertas=True)).resultado
    colores = {"urgente": "rojo", "abierto": "rojo", "se acerca": "amarillo",
               "programado": "verde", "por abrir": "verde", "cerrado este año": "gris"}
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Obligaciones que le aplican", "valor": len(datos["obligaciones_con_fecha"]), "unidad": ""},
            {"etiqueta": "Abiertas o urgentes", "valor": len(datos["urgentes"]), "unidad": "",
             "color": "rojo" if datos["urgentes"] else "verde"},
            {"etiqueta": "Por confirmar", "valor": len(datos["por_confirmar"]), "unidad": "", "color": "amarillo"},
        ]},
        {"tipo": "titulo", "texto": "Calendario del año", "nivel": 2},
        {"tipo": "semaforo", "items": [
            {"etiqueta": f["obligacion"], "estado": colores.get(f["estado"], "gris"),
             "estado_texto": f["estado"],
             "detalle": "Ventana %s. %s" % (f["ventana"] or "sin fecha fija", f["norma"])}
            for f in datos["obligaciones_con_fecha"]]},
    ]
    if datos["obligaciones_permanentes"]:
        bloques.append({"tipo": "titulo", "texto": "Obligaciones permanentes o por operacion", "nivel": 2})
        bloques.append({"tipo": "lista", "items": ["%s — %s (%s)" % (f["obligacion"], f["frecuencia"], f["norma"])
                                                   for f in datos["obligaciones_permanentes"]]})
    if datos["por_confirmar"]:
        bloques.append({"tipo": "titulo", "texto": "Falta confirmar si le aplican", "nivel": 2})
        bloques.append({"tipo": "lista", "items": ["%s — %s" % (f["obligacion"], f["norma"])
                                                   for f in datos["por_confirmar"]]})
    bloques.append({"tipo": "nota", "estilo": "aviso",
                    "texto": "Las fechas pueden cambiar cada año por convocatoria o resolucion. Confirmalas "
                             "en el portal del organismo. Esto es orientacion, no asesoria legal."})

    destino = espacio.ruta_de(ruta, "reportes", "calendario-obligaciones.html")
    informe.escribir_html(destino, "Calendario de obligaciones", bloques, marca=perfil.get("marca") or {},
                          subtitulo="%s - %s" % (perfil.get("nombre", ""), datos["hoy"]))
    return {"mensaje": "Calendario listo.", "archivo": destino,
            "urgentes": len(datos["urgentes"])}


ACCIONES = {"proximas": proximas, "informe": informe_html}
