# -*- coding: utf-8 -*-
"""Fechas, dias habiles y plazos legales.

Los plazos de la Ley Karin, de la Ley REP o del RETC se cuentan en dias
habiles o corridos. Aqui esta la aritmetica; los feriados se cargan desde
.claude/motor/datos/feriados_chile.csv (o el archivo que corresponda al pais).
"""

import csv
import datetime
import os
import re

from .salida import Problema

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}


def parsear_fecha(valor):
    """Acepta date, 2026-01-31, 31-01-2026, 31/01/2026 o '31 de enero de 2026'."""
    if isinstance(valor, datetime.datetime):
        return valor.date()
    if isinstance(valor, datetime.date):
        return valor
    texto = str(valor or "").strip()
    if not texto:
        raise Problema("Falta la fecha.", "Escribela como 31-01-2026 o 2026-01-31.")
    texto = texto.split(" ")[0] if re.match(r"^\d{4}-\d{2}-\d{2} ", texto) else texto
    for formato in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    coincidencia = re.match(r"^(\d{1,2})\s+de\s+([a-zA-Záéíóú]+)\s+(?:de\s+)?(\d{4})$", str(valor).strip(), re.IGNORECASE)
    if coincidencia:
        dia, mes, anio = coincidencia.groups()
        clave = mes.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        if clave in MESES:
            return datetime.date(int(anio), MESES[clave], int(dia))
    raise Problema(
        "No entiendo la fecha «%s»." % valor,
        "Escribela como 31-01-2026, 2026-01-31 o «31 de enero de 2026».",
    )


def cargar_feriados(ruta_csv):
    """Lee un CSV con columna 'fecha' (AAAA-MM-DD) y devuelve un conjunto de fechas."""
    feriados = {}
    if not ruta_csv or not os.path.isfile(ruta_csv):
        return feriados
    with open(ruta_csv, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            claves = {(k or "").strip().lower(): (v or "").strip() for k, v in fila.items()}
            crudo = claves.get("fecha")
            if not crudo:
                continue
            try:
                feriados[parsear_fecha(crudo)] = claves.get("nombre", "Feriado")
            except Problema:
                continue
    return feriados


def es_habil(fecha, feriados=None, sabado_habil=False):
    fecha = parsear_fecha(fecha)
    feriados = feriados or {}
    if fecha.weekday() == 6:                      # domingo
        return False
    if fecha.weekday() == 5 and not sabado_habil:  # sabado
        return False
    return fecha not in feriados


def sumar_dias_habiles(desde, cantidad, feriados=None, sabado_habil=False):
    """Suma dias habiles a una fecha (el dia inicial no se cuenta)."""
    fecha = parsear_fecha(desde)
    try:
        restantes = int(cantidad)
    except (TypeError, ValueError):
        raise Problema("«%s» no es un numero de dias valido." % cantidad, "Indica un numero entero, por ejemplo 30.")
    paso = 1 if restantes >= 0 else -1
    restantes = abs(restantes)
    while restantes > 0:
        fecha += datetime.timedelta(days=paso)
        if es_habil(fecha, feriados, sabado_habil):
            restantes -= 1
    return fecha


def dias_habiles_entre(desde, hasta, feriados=None, sabado_habil=False):
    """Cuenta dias habiles entre dos fechas, sin incluir la inicial."""
    inicio = parsear_fecha(desde)
    fin = parsear_fecha(hasta)
    paso = 1 if fin >= inicio else -1
    total = 0
    fecha = inicio
    while fecha != fin:
        fecha += datetime.timedelta(days=paso)
        if es_habil(fecha, feriados, sabado_habil):
            total += paso
    return total


def plazo(desde, cantidad, tipo="habiles", feriados=None, sabado_habil=False, hoy=None):
    """Calcula el vencimiento de un plazo y en que estado esta.

    tipo: 'habiles' o 'corridos'.
    Devuelve fecha de inicio, vencimiento, dias restantes y estado
    (vigente, por_vencer cuando faltan 3 dias o menos, o vencido).
    """
    inicio = parsear_fecha(desde)
    tipo = str(tipo or "habiles").lower()
    if tipo.startswith("corr"):
        try:
            vence = inicio + datetime.timedelta(days=int(cantidad))
        except (TypeError, ValueError):
            raise Problema("«%s» no es un numero de dias valido." % cantidad, "Indica un numero entero, por ejemplo 30.")
    elif tipo.startswith("hab"):
        vence = sumar_dias_habiles(inicio, cantidad, feriados, sabado_habil)
    else:
        raise Problema("No conozco el tipo de plazo «%s»." % tipo, "Usa «habiles» o «corridos».")

    referencia = parsear_fecha(hoy) if hoy else datetime.date.today()
    if tipo.startswith("corr"):
        restantes = (vence - referencia).days
    else:
        restantes = dias_habiles_entre(referencia, vence, feriados, sabado_habil)
    if restantes < 0:
        estado = "vencido"
    elif restantes <= 3:
        estado = "por_vencer"
    else:
        estado = "vigente"
    return {
        "inicio": inicio.isoformat(),
        "vence": vence.isoformat(),
        "dias": int(cantidad),
        "tipo": "corridos" if tipo.startswith("corr") else "habiles",
        "dias_restantes": restantes,
        "estado": estado,
        "referencia": referencia.isoformat(),
    }
