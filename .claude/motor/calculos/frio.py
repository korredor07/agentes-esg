# -*- coding: utf-8 -*-
"""Cadena de frio: temperatura cinetica media, excursiones y limites legales.

Por que no sirve el promedio. El dano termico de un producto no crece en linea
recta con la temperatura: crece exponencialmente (ley de Arrhenius). Dos horas
a 14 C hacen mucho mas dano que dos horas a 6 C de beneficio. Por eso las
farmacopeas usan la temperatura cinetica media (MKT), que es la temperatura
constante que habria producido el mismo dano que toda la serie real:

                    dH / R
    MKT = ------------------------------------------------
          -ln[ (e^(-dH/(R.T1)) + ... + e^(-dH/(R.Tn))) / n ]

    dH = 83,144 kJ/mol   entalpia de activacion por defecto (USP <1079.2>)
    R  = 8,3144e-3 kJ/(mol.K)   constante de los gases
    Ti = cada temperatura medida, en kelvin (grados C + 273,15)

Con esos dos valores por defecto, dH/R vale exactamente 10.000 K.

La MKT es siempre mayor o igual que el promedio aritmetico (desigualdad de
Jensen): si sale menor, hay un error de calculo. Ese es justamente el punto:
una bodega con promedio 24,0 C puede tener MKT 25,02 C e incumplir un limite
de 25 C que el promedio decia cumplir con holgura.

Lo que este modulo NO hace: decidir si un lote se libera o se rechaza. Eso lo
determina el titular del registro sanitario con sus datos de estabilidad.
"""

import csv
import math
import os

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_TEMPERATURAS = os.path.join(CARPETA_DATOS, "temperaturas_cl.csv")

CERO_ABSOLUTO_C = -273.15
ENTALPIA_POR_DEFECTO = 83.144        # kJ/mol, USP <1079.2>
CONSTANTE_GASES = 8.3144e-3          # kJ/(mol.K), el valor que usa USP


def _numero(valor):
    if valor in (None, ""):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _clave(texto):
    return " ".join(str(texto or "").strip().lower().split())


def temperatura_cinetica_media(temperaturas_c, entalpia=None, constante=None):
    """Temperatura cinetica media de una serie, en grados Celsius.

    Se usa log-sum-exp en vez de sumar exponenciales directamente, porque
    e^(-10000/280) vale del orden de 3e-16 y una serie larga perderia precision.
    """
    serie = [_numero(t) for t in (temperaturas_c or [])]
    serie = [t for t in serie if t is not None]
    if not serie:
        raise Problema(
            "No hay temperaturas para calcular.",
            "Necesito la serie de lecturas del registrador, en grados Celsius.",
        )
    for temperatura in serie:
        if temperatura <= CERO_ABSOLUTO_C:
            raise Problema(
                "La lectura %s C es imposible: esta bajo el cero absoluto." % temperatura,
                "Revisa la planilla: probablemente se coló un valor de otra columna.",
            )

    entalpia = entalpia if entalpia is not None else ENTALPIA_POR_DEFECTO
    constante = constante if constante is not None else CONSTANTE_GASES
    cociente = entalpia / constante

    exponentes = [-cociente / (t + 273.15) for t in serie]
    mayor = max(exponentes)
    promedio_log = mayor + math.log(sum(math.exp(e - mayor) for e in exponentes) / len(exponentes))
    mkt = cociente / (-promedio_log) - 273.15

    promedio = sum(serie) / len(serie)
    if mkt < promedio - 1e-9:
        raise Problema(
            "El calculo dio una temperatura cinetica media menor que el promedio, lo que es imposible.",
            "Es un error del motor, no de tus datos. Avisa para revisarlo.",
        )
    return {
        "mkt_c": round(mkt, 6),
        "promedio_c": round(promedio, 6),
        "diferencia_con_el_promedio": round(mkt - promedio, 6),
        "lecturas": len(serie),
        "minima_c": min(serie),
        "maxima_c": max(serie),
        "entalpia_kj_mol": entalpia,
        "constante_gases": constante,
        "metodo": "Temperatura cinetica media segun USP <1079.2>, derivada de la ecuacion de "
                  "Arrhenius. Supone lecturas a intervalos regulares.",
        "advertencias": ["Las lecturas tienen que estar tomadas a intervalos regulares. Si no lo "
                         "estan, hay que ponderarlas por su duracion o el resultado queda sesgado."],
    }


def vida_util_por_q10(vida_referencia_dias, temperatura_referencia_c, temperatura_real_c, q10):
    """Vida util restante segun la regla Q10, con parametros que aporta la empresa.

        vida(T) = vida(T_ref) x Q10 ^ ((T_ref - T) / 10)

    El Q10 es propio de cada producto (suele estar entre 2 y 3 en alimentos).
    El motor no inventa uno: un valor equivocado aqui puede liberar producto
    que no esta apto.
    """
    if not q10 or q10 <= 0:
        raise Problema(
            "Falta el Q10 del producto.",
            "El Q10 dice cuantas veces se acelera el deterioro por cada 10 C de mas, y es propio de "
            "cada producto: sale de los estudios de estabilidad del fabricante. No puedo inventarlo.",
        )
    if not vida_referencia_dias or vida_referencia_dias <= 0:
        raise Problema(
            "Falta la vida util de referencia en dias.",
            "Es la vida util que declara el fabricante a su temperatura de referencia.",
        )
    factor = q10 ** ((temperatura_referencia_c - temperatura_real_c) / 10.0)
    return {
        "vida_util_dias": round(vida_referencia_dias * factor, 2),
        "vida_util_de_referencia_dias": vida_referencia_dias,
        "temperatura_de_referencia_c": temperatura_referencia_c,
        "temperatura_real_c": temperatura_real_c,
        "q10": q10,
        "factor": round(factor, 4),
        "interpretacion": ("A %s C el producto dura %s veces %s que a los %s C de referencia."
                           % (temperatura_real_c, round(factor, 2),
                              "mas" if factor >= 1 else "menos", temperatura_referencia_c)),
        "advertencias": [
            "El Q10 y la vida util de referencia los entrego la empresa: este calculo vale lo que "
            "valga ese dato.",
            "La regla Q10 es una aproximacion de gestion. La aptitud del producto la decide quien "
            "tiene el registro sanitario, con sus estudios de estabilidad.",
        ],
    }


def cargar_limites(ruta=None):
    """Lee la tabla de temperaturas exigidas por producto y situacion."""
    ruta = ruta or ARCHIVO_TEMPERATURAS
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro la tabla de temperaturas (%s)." % os.path.basename(ruta),
            "Sin ella no puedo revisar contra la norma. Avisa para reinstalar los datos.",
        )
    limites = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if not (fila.get("id") or "").strip():
                continue
            limites.append({
                "id": fila["id"].strip(),
                "ambito": _clave(fila.get("ambito")),
                "producto": _clave(fila.get("producto")),
                "situacion": _clave(fila.get("situacion")),
                "minimo_c": _numero(fila.get("minimo_c")),
                "maximo_c": _numero(fila.get("maximo_c")),
                "tolerancia_c": _numero(fila.get("tolerancia_c")),
                "fuente": (fila.get("fuente") or "").strip(),
                "articulo": (fila.get("articulo") or "").strip(),
                "url": (fila.get("url") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
            })
    return limites


def buscar_limite(producto, situacion=None, limites=None):
    """Que temperatura exige la norma para ese producto en esa situacion."""
    limites = limites if limites is not None else cargar_limites()
    clave = _clave(producto)
    candidatos = [l for l in limites if clave and (clave in l["producto"] or l["producto"] in clave
                                                   or clave in l["id"])]
    if not candidatos:
        raise Problema(
            "No tengo la temperatura que exige la norma para «%s»." % producto,
            "Los productos que tengo cargados son: %s. El Reglamento Sanitario de los Alimentos fija "
            "temperaturas por tipo de producto, no una sola para todo: si el tuyo no esta, hay que "
            "buscar su articulo antes de afirmar nada."
            % ", ".join(sorted({l["producto"] for l in limites})),
        )
    if situacion:
        clave_situacion = _clave(situacion)
        por_situacion = [l for l in candidatos
                         if clave_situacion in l["situacion"] or l["situacion"] in clave_situacion]
        if por_situacion:
            return por_situacion[0]
        return {"varias_opciones": candidatos,
                "aviso": "Hay %d situaciones distintas para «%s» y ninguna calza con «%s»: elige una."
                         % (len(candidatos), producto, situacion)}
    if len(candidatos) == 1:
        return candidatos[0]
    return {"varias_opciones": candidatos,
            "aviso": "La norma fija temperaturas distintas segun la situacion. Dime cual es: %s."
                     % ", ".join(sorted({l["situacion"] for l in candidatos}))}


def evaluar_excursiones(lecturas, minimo_c=None, maximo_c=None, minutos_por_lectura=None):
    """Cuenta y mide las veces que la temperatura se salio del rango.

    Una excursion se juzga por tres cosas a la vez: cuanto se salio, cuanto
    tiempo estuvo fuera, y si la temperatura cinetica media del periodo completo
    sigue dentro del limite. Cumplir una sola de las tres no basta.
    """
    serie = [_numero(t) for t in (lecturas or [])]
    serie = [t for t in serie if t is not None]
    if not serie:
        raise Problema("No hay lecturas que revisar.",
                       "Necesito la serie del registrador, en grados Celsius.")
    if minimo_c is None and maximo_c is None:
        raise Problema(
            "No me dijiste que rango tiene que cumplir el producto.",
            "Dame el minimo y el maximo, o el nombre del producto para buscar su limite legal.",
        )

    fuera = []
    actual = None
    for indice, temperatura in enumerate(serie):
        se_salio = ((maximo_c is not None and temperatura > maximo_c) or
                    (minimo_c is not None and temperatura < minimo_c))
        if se_salio:
            if actual is None:
                actual = {"desde_lectura": indice + 1, "hasta_lectura": indice + 1,
                          "lecturas": 1, "maxima_c": temperatura, "minima_c": temperatura}
            else:
                actual["hasta_lectura"] = indice + 1
                actual["lecturas"] += 1
                actual["maxima_c"] = max(actual["maxima_c"], temperatura)
                actual["minima_c"] = min(actual["minima_c"], temperatura)
        elif actual is not None:
            fuera.append(actual)
            actual = None
    if actual is not None:
        fuera.append(actual)

    for excursion in fuera:
        excursion["por_encima"] = maximo_c is not None and excursion["maxima_c"] > maximo_c
        excursion["por_debajo"] = minimo_c is not None and excursion["minima_c"] < minimo_c
        if minutos_por_lectura:
            excursion["minutos"] = excursion["lecturas"] * minutos_por_lectura
            excursion["horas"] = round(excursion["lecturas"] * minutos_por_lectura / 60.0, 2)

    mkt = temperatura_cinetica_media(serie)
    lecturas_fuera = sum(e["lecturas"] for e in fuera)
    mkt_cumple = True
    if maximo_c is not None and mkt["mkt_c"] > maximo_c:
        mkt_cumple = False
    if minimo_c is not None and mkt["mkt_c"] < minimo_c:
        mkt_cumple = False

    advertencias = list(mkt["advertencias"])
    if not minutos_por_lectura:
        advertencias.append("Sin saber cada cuanto se tomo una lectura no puedo decir cuantas horas "
                            "duro cada excursion, y la duracion es parte del criterio. Pasa el "
                            "intervalo del registrador.")
    if fuera and mkt_cumple:
        advertencias.append("La temperatura cinetica media cumple, pero hubo excursiones: cumplir la "
                            "MKT no borra una excursion. Las tres condiciones se miran juntas.")

    return {
        "lecturas": len(serie),
        "rango_exigido": {"minimo_c": minimo_c, "maximo_c": maximo_c},
        "minima_registrada_c": min(serie),
        "maxima_registrada_c": max(serie),
        "excursiones": fuera,
        "total_excursiones": len(fuera),
        "lecturas_fuera_de_rango": lecturas_fuera,
        "porcentaje_fuera_de_rango": round(lecturas_fuera / float(len(serie)) * 100.0, 2),
        "mkt_c": mkt["mkt_c"],
        "promedio_c": mkt["promedio_c"],
        "mkt_dentro_del_rango": mkt_cumple,
        "sin_excursiones": not fuera,
        "resumen": _resumen_excursiones(fuera, mkt_cumple, mkt["mkt_c"], maximo_c),
        "advertencias": advertencias,
        "quien_decide": "Este resultado describe lo que paso con la temperatura. Si el producto se "
                        "libera o se rechaza lo decide el titular del registro sanitario con sus "
                        "datos de estabilidad, no este calculo.",
    }


def _resumen_excursiones(fuera, mkt_cumple, mkt, maximo_c):
    if not fuera and mkt_cumple:
        return "La temperatura se mantuvo siempre dentro del rango y la MKT tambien cumple."
    if not fuera and not mkt_cumple:
        return ("Ninguna lectura suelta se salio del rango, pero la temperatura cinetica media es "
                "%s C y eso ya incumple. Es exactamente el caso que el promedio simple esconde."
                % round(mkt, 2))
    if mkt_cumple:
        return ("Hubo %d excursion(es) fuera de rango, pero la temperatura cinetica media del periodo "
                "(%s C) sigue dentro del limite%s. Hay que revisar cuanto duro cada excursion."
                % (len(fuera), round(mkt, 2), " de %s C" % maximo_c if maximo_c is not None else ""))
    return ("Hubo %d excursion(es) y ademas la temperatura cinetica media (%s C) esta fuera del "
            "limite: esto no se resuelve solo con documentacion."
            % (len(fuera), round(mkt, 2)))
