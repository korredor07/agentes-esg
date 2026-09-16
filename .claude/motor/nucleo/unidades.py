# -*- coding: utf-8 -*-
"""Conversion de unidades con nombres en español.

Las personas escriben las unidades como quieren ("m³", "metros cubicos", "Lts",
"toneladas"). Aqui se normalizan y se convierten sin perder precision.
"""

import re
import unicodedata

from .salida import Problema

# Valor de una unidad expresado en la unidad base de su magnitud.
MAGNITUDES = {
    "energia": {
        "base": "kwh",
        "unidades": {
            "wh": 0.001, "kwh": 1.0, "mwh": 1000.0, "gwh": 1000000.0,
            "mj": 0.2777777777777778, "gj": 277.7777777777778, "tj": 277777.7777777778,
            "kcal": 0.001163, "mcal": 1.163, "gcal": 1163.0,
            "btu": 0.00029307107, "mmbtu": 293.07107, "therm": 29.307107,
        },
    },
    "volumen": {
        "base": "l",
        "unidades": {
            "ml": 0.001, "l": 1.0, "m3": 1000.0, "cm3": 0.001, "dm3": 1.0,
            "gal": 3.785411784, "bbl": 158.987294928, "ft3": 28.316846592,
        },
    },
    "masa": {
        "base": "kg",
        "unidades": {
            "mg": 0.000001, "g": 0.001, "kg": 1.0, "t": 1000.0, "kt": 1000000.0,
            "lb": 0.45359237, "oz": 0.028349523125, "st": 907.18474,
        },
    },
    "distancia": {
        "base": "km",
        "unidades": {"mm": 0.000001, "cm": 0.00001, "m": 0.001, "km": 1.0,
                     "mi": 1.609344, "nmi": 1.852, "ft": 0.0003048},
    },
    "tiempo": {
        "base": "h",
        "unidades": {"s": 0.0002777777777777778, "min": 0.016666666666666666,
                     "h": 1.0, "dia": 24.0, "semana": 168.0},
    },
    "superficie": {
        "base": "m2",
        "unidades": {"m2": 1.0, "ha": 10000.0, "km2": 1000000.0, "ft2": 0.09290304},
    },
}

# Como escribe la gente cada unidad.
ALIAS = {
    "kwh": "kwh", "kw h": "kwh", "kw/h": "kwh", "kilowatthora": "kwh", "kilowatt hora": "kwh",
    "kilovatio hora": "kwh", "kilowatts hora": "kwh",
    "mwh": "mwh", "megawatt hora": "mwh", "megavatio hora": "mwh", "gwh": "gwh", "wh": "wh",
    "mj": "mj", "megajoule": "mj", "megajoules": "mj", "gj": "gj", "gigajoule": "gj",
    "tj": "tj", "terajoule": "tj", "kcal": "kcal", "mcal": "mcal", "gcal": "gcal",
    "btu": "btu", "mmbtu": "mmbtu", "therm": "therm", "termia": "therm",
    "l": "l", "lt": "l", "lts": "l", "litro": "l", "litros": "l",
    "m3": "m3", "m³": "m3", "metro cubico": "m3", "metros cubicos": "m3", "mc": "m3",
    "ml": "ml", "cc": "cm3", "cm3": "cm3", "dm3": "dm3",
    "gal": "gal", "galon": "gal", "galones": "gal", "gl": "gal",
    "bbl": "bbl", "barril": "bbl", "barriles": "bbl", "ft3": "ft3", "pie cubico": "ft3",
    "kg": "kg", "kilo": "kg", "kilos": "kg", "kilogramo": "kg", "kilogramos": "kg",
    "g": "g", "gr": "g", "gramo": "g", "gramos": "g", "mg": "mg", "miligramo": "mg",
    "t": "t", "ton": "t", "tons": "t", "tonelada": "t", "toneladas": "t",
    "tonelada metrica": "t", "toneladas metricas": "t", "tm": "t", "kt": "kt",
    "lb": "lb", "libra": "lb", "libras": "lb", "oz": "oz", "onza": "oz",
    "km": "km", "kms": "km", "kilometro": "km", "kilometros": "km",
    "m": "m", "metro": "m", "metros": "m", "cm": "cm", "mm": "mm",
    "mi": "mi", "milla": "mi", "millas": "mi", "nmi": "nmi", "milla nautica": "nmi",
    "millas nauticas": "nmi", "mn": "nmi", "ft": "ft", "pie": "ft", "pies": "ft",
    "s": "s", "seg": "s", "segundo": "s", "segundos": "s",
    "min": "min", "minuto": "min", "minutos": "min",
    "h": "h", "hr": "h", "hrs": "h", "hora": "h", "horas": "h",
    "dia": "dia", "dias": "dia", "semana": "semana", "semanas": "semana",
    "m2": "m2", "m²": "m2", "metro cuadrado": "m2", "metros cuadrados": "m2",
    "ha": "ha", "hectarea": "ha", "hectareas": "ha", "km2": "km2", "km²": "km2",
    "ft2": "ft2", "pie cuadrado": "ft2",
}


def _limpiar(texto):
    texto = str(texto or "").strip().lower()
    texto = texto.replace("³", "3").replace("²", "2")
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9/ ]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_unidad(texto):
    """Devuelve (magnitud, unidad) o lanza Problema si no la reconoce."""
    limpio = _limpiar(texto)
    clave = ALIAS.get(limpio) or ALIAS.get(limpio.replace(" ", "")) or limpio.replace(" ", "")
    for magnitud, definicion in MAGNITUDES.items():
        if clave in definicion["unidades"]:
            return magnitud, clave
    raise Problema(
        "No reconozco la unidad «%s»." % texto,
        "Usa una de estas: kWh, MWh, GJ, litros, m3, galones, kg, toneladas, km, millas, horas, m2 o hectareas.",
        {"unidad_recibida": texto},
    )


def convertir(valor, desde, hacia):
    """Convierte un valor entre unidades de la misma magnitud."""
    if valor is None or valor == "":
        raise Problema("Falta la cantidad que quieres convertir.", "Indica un numero, por ejemplo 1500.")
    try:
        numero = float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        raise Problema(
            "«%s» no es un numero valido." % valor,
            "Escribe solo el numero, sin texto ni simbolos (por ejemplo 1500 o 1500,5).",
        )
    magnitud_origen, unidad_origen = normalizar_unidad(desde)
    magnitud_destino, unidad_destino = normalizar_unidad(hacia)
    if magnitud_origen != magnitud_destino:
        raise Problema(
            "No se puede convertir de %s (%s) a %s (%s): miden cosas distintas."
            % (desde, magnitud_origen, hacia, magnitud_destino),
            "Revisa la unidad en la planilla; por ejemplo, litros mide volumen y kilos mide masa.",
        )
    unidades = MAGNITUDES[magnitud_origen]["unidades"]
    return numero * unidades[unidad_origen] / unidades[unidad_destino]


def misma_magnitud(una, otra):
    try:
        return normalizar_unidad(una)[0] == normalizar_unidad(otra)[0]
    except Problema:
        return False


def unidades_de(magnitud):
    return sorted(MAGNITUDES.get(magnitud, {}).get("unidades", {}).keys())
