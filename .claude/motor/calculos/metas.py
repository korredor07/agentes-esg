# -*- coding: utf-8 -*-
"""Metas de reduccion de emisiones: trayectoria, validaciones y probabilidad.

Trayectoria de contraccion absoluta lineal (criterio SBTi):

    E_t = E_base x (1 - r x (t - t_base))

La reduccion acumulada es r x (t - t_base) y NO se compone. Ojo: una reduccion
lineal de 42 % en 10 años equivale a una tasa compuesta de 5,302 % anual;
confundirlas es un error frecuente al comparar con metas expresadas en CAGR.

Tasas minimas de la ruta transversal (ajustables): 4,2 % anual para alcances
1 y 2 (alineamiento 1,5 C) y 2,5 % anual para alcance 3. Los estandares de
SBTi cambiaron en 2026 (Corporate Net-Zero Standard V2.0): este motor calcula
la matematica y advierte que la validacion formal la hace SBTi, no nosotros.

La probabilidad de cumplir se estima con simulacion de Monte Carlo sobre las
variables que la empresa no controla del todo (crecimiento, descarbonizacion de
la red electrica, eficiencia y ejecucion de proyectos).
"""

import datetime
import math
import random

from nucleo.salida import Problema

TASA_ALCANCE_1_2 = 0.042
TASA_ALCANCE_3 = 0.025
REDUCCION_LARGO_PLAZO = 0.90
UMBRAL_ALCANCE_3 = 0.40
COBERTURA_MINIMA_ALCANCE_3 = 0.67
ANIO_BASE_MINIMO = 2015
UMBRAL_CREDIBILIDAD = 0.80


def _numero(valor, nombre):
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        raise Problema("«%s» no es un numero valido para %s." % (valor, nombre),
                       "Escribe solo el numero, por ejemplo 12500.")


def trayectoria(emisiones_base, anio_base, anio_meta, tasa=TASA_ALCANCE_1_2):
    """Devuelve la trayectoria anual de emisiones permitidas."""
    base = _numero(emisiones_base, "las emisiones del año base")
    anio_base = int(anio_base)
    anio_meta = int(anio_meta)
    tasa = _numero(tasa, "la tasa de reduccion")
    if anio_meta <= anio_base:
        raise Problema("El año meta (%d) debe ser posterior al año base (%d)." % (anio_meta, anio_base),
                       "Por ejemplo: año base 2025 y meta al 2030.")
    filas = []
    for anio in range(anio_base, anio_meta + 1):
        transcurridos = anio - anio_base
        acumulada = min(tasa * transcurridos, 1.0)
        filas.append({
            "anio": anio,
            "anios_desde_base": transcurridos,
            "reduccion_acumulada_pct": round(acumulada * 100.0, 2),
            "emisiones_permitidas": round(base * (1 - acumulada), 2),
        })
    reduccion_total = tasa * (anio_meta - anio_base)
    compuesta = 1 - (1 - reduccion_total) ** (1.0 / (anio_meta - anio_base)) if reduccion_total < 1 else 1.0
    return {
        "emisiones_base": base, "anio_base": anio_base, "anio_meta": anio_meta,
        "tasa_anual_lineal_pct": round(tasa * 100.0, 3),
        "reduccion_total_pct": round(reduccion_total * 100.0, 2),
        "emisiones_meta": round(base * (1 - min(reduccion_total, 1.0)), 2),
        "tasa_compuesta_equivalente_pct": round(compuesta * 100.0, 3),
        "trayectoria": filas,
    }


def ratio_alcance3(alcance1, alcance2, alcance3):
    total = _numero(alcance1, "alcance 1") + _numero(alcance2, "alcance 2") + _numero(alcance3, "alcance 3")
    if total <= 0:
        return 0.0
    return _numero(alcance3, "alcance 3") / total


def meta_largo_plazo(emisiones_base, reduccion=REDUCCION_LARGO_PLAZO):
    base = _numero(emisiones_base, "las emisiones del año base")
    residuales = base * (1 - reduccion)
    return {
        "emisiones_base": base,
        "reduccion_exigida_pct": round(reduccion * 100.0, 1),
        "emisiones_maximas_2050": round(residuales, 2),
        "nota": ("Las emisiones residuales deben neutralizarse con remociones permanentes para poder "
                 "declarar net-zero."),
    }


def validar_meta(datos):
    """Revisa los criterios formales de una meta antes de comprometerla."""
    revisiones = []

    def revisar(clave, cumple, mensaje, referencia):
        revisiones.append({"criterio": clave, "cumple": bool(cumple), "detalle": mensaje,
                           "referencia": referencia})

    anio_base = int(datos.get("anio_base") or 0)
    anio_meta = int(datos.get("anio_meta") or 0)
    hoy = int(datos.get("anio_actual") or datetime.date.today().year)

    revisar("año base", anio_base >= ANIO_BASE_MINIMO,
            "El año base es %d; debe ser %d o posterior." % (anio_base, ANIO_BASE_MINIMO),
            "Criterio C13 de SBTi")
    horizonte = anio_meta - hoy
    revisar("horizonte", 5 <= horizonte <= 10 or anio_meta == 2030,
            "La meta esta a %d años; el criterio pide entre 5 y 10 años (salvo metas al 2030)." % horizonte,
            "Criterio C13 de SBTi")

    alcance1 = _numero(datos.get("alcance_1") or 0, "alcance 1")
    alcance2 = _numero(datos.get("alcance_2") or 0, "alcance 2")
    alcance3 = _numero(datos.get("alcance_3") or 0, "alcance 3")
    ratio = ratio_alcance3(alcance1, alcance2, alcance3)
    exige_alcance3 = ratio >= UMBRAL_ALCANCE_3
    revisar("meta de alcance 3",
            (not exige_alcance3) or bool(datos.get("meta_alcance_3")),
            ("El alcance 3 es el %.1f%% del total: la meta de alcance 3 es obligatoria." % (ratio * 100)
             if exige_alcance3 else
             "El alcance 3 es el %.1f%% del total: la meta de alcance 3 no es obligatoria, pero se recomienda."
             % (ratio * 100)),
            "Criterio C4 de SBTi")
    if exige_alcance3:
        cobertura = _numero(datos.get("cobertura_alcance_3") or 0, "la cobertura de alcance 3")
        revisar("cobertura de alcance 3", cobertura >= COBERTURA_MINIMA_ALCANCE_3 * 100,
                "La meta cubre el %.0f%% del alcance 3; se exige al menos %.0f%%."
                % (cobertura, COBERTURA_MINIMA_ALCANCE_3 * 100),
                "Criterio C6 de SBTi")

    exclusiones = _numero(datos.get("exclusiones_pct") or 0, "las exclusiones")
    revisar("exclusiones", exclusiones <= 5,
            "Se excluye el %.1f%% de las emisiones; el limite es 5%%." % exclusiones,
            "Criterio C5 de SBTi")
    revisar("sin compensaciones", not datos.get("usa_creditos"),
            "Los creditos de carbono y las emisiones evitadas no cuentan como avance de la meta.",
            "Criterios C11 y C12 de SBTi")

    pendientes = [r for r in revisiones if not r["cumple"]]
    return {
        "revisiones": revisiones,
        "cumple_todo": not pendientes,
        "pendientes": pendientes,
        "ratio_alcance_3_pct": round(ratio * 100.0, 1),
        "exige_meta_alcance_3": exige_alcance3,
        "aviso": ("Estas revisiones son la matematica de los criterios publicos. La validacion formal de "
                  "una meta la hace la propia iniciativa (SBTi), con su proceso y sus tarifas."),
    }


# --------------------------------------------------------------------------
# Monte Carlo
# --------------------------------------------------------------------------

def _sortear(definicion, azar):
    """Sortea un valor segun la distribucion indicada."""
    tipo = str(definicion.get("tipo", "fijo")).lower()
    if tipo == "fijo":
        return float(definicion.get("valor", 0.0))
    if tipo == "normal":
        return azar.gauss(float(definicion.get("media", 0.0)), float(definicion.get("desviacion", 0.0)))
    if tipo == "triangular":
        return azar.triangular(float(definicion.get("min", 0.0)), float(definicion.get("max", 0.0)),
                               float(definicion.get("moda", definicion.get("min", 0.0))))
    if tipo == "uniforme":
        return azar.uniform(float(definicion.get("min", 0.0)), float(definicion.get("max", 0.0)))
    raise Problema("No conozco la distribucion «%s»." % tipo,
                   "Usa: fijo, normal, triangular o uniforme.")


def _percentil(ordenados, fraccion):
    if not ordenados:
        return 0.0
    posicion = fraccion * (len(ordenados) - 1)
    bajo = int(math.floor(posicion))
    alto = min(bajo + 1, len(ordenados) - 1)
    peso = posicion - bajo
    return ordenados[bajo] * (1 - peso) + ordenados[alto] * peso


def monte_carlo(configuracion, iteraciones=20000, semilla=20260915):
    """Estima la probabilidad de cumplir la meta.

    Modelo anual, aplicado sobre las emisiones del año anterior:

        E = E x (1 + crecimiento) x (1 - descarbonizacion) x (1 - eficiencia)
        y, si el proyecto se ejecuta ese año, x (1 - reduccion del proyecto)

    Todas las variables se sortean en cada iteracion y en cada año.
    """
    base = _numero(configuracion.get("emisiones_actuales"), "las emisiones actuales")
    anio_inicio = int(configuracion.get("anio_inicio") or datetime.date.today().year)
    anio_meta = int(configuracion.get("anio_meta") or (anio_inicio + 5))
    objetivo = _numero(configuracion.get("emisiones_meta"), "las emisiones meta")
    if anio_meta <= anio_inicio:
        raise Problema("El año meta debe ser posterior al año de inicio.",
                       "Por ejemplo: inicio 2026 y meta 2030.")
    azar = random.Random(semilla)
    horizonte = anio_meta - anio_inicio
    crecimiento = configuracion.get("crecimiento") or {"tipo": "fijo", "valor": 0.0}
    descarbonizacion = configuracion.get("descarbonizacion_red") or {"tipo": "fijo", "valor": 0.0}
    eficiencia = configuracion.get("eficiencia") or {"tipo": "fijo", "valor": 0.0}
    proyectos = configuracion.get("proyectos") or []

    finales = []
    cumplen = 0
    for _ in range(int(iteraciones)):
        emisiones = base
        for paso in range(1, horizonte + 1):
            anio = anio_inicio + paso
            emisiones *= (1 + _sortear(crecimiento, azar))
            emisiones *= (1 - _sortear(descarbonizacion, azar))
            emisiones *= (1 - _sortear(eficiencia, azar))
            for proyecto in proyectos:
                if int(proyecto.get("anio") or 0) != anio:
                    continue
                if azar.random() <= float(proyecto.get("probabilidad", 1.0)):
                    emisiones *= (1 - _sortear(proyecto.get("reduccion") or {"tipo": "fijo", "valor": 0.0}, azar))
            emisiones = max(emisiones, 0.0)
        finales.append(emisiones)
        if emisiones <= objetivo:
            cumplen += 1

    finales.sort()
    probabilidad = cumplen / float(len(finales))
    media = sum(finales) / len(finales)
    varianza = sum((x - media) ** 2 for x in finales) / max(len(finales) - 1, 1)
    mediana = _percentil(finales, 0.5)
    def _sin_supuesto(definicion):
        return (definicion.get("tipo", "fijo") == "fijo" and float(definicion.get("valor", 0.0) or 0.0) == 0.0)

    # Sin crecimiento, eficiencia, red ni proyectos no hay nada que sortear: el resultado no es una
    # probabilidad, es lo que pasa si nada cambia. Presentarlo como «0 % en 20.000 escenarios» engaña.
    escenario_sin_cambios = (not proyectos and _sin_supuesto(crecimiento) and _sin_supuesto(descarbonizacion)
                             and _sin_supuesto(eficiencia))
    if escenario_sin_cambios:
        lectura = ("Esto no es una probabilidad todavia: sin supuestos de crecimiento, eficiencia ni proyectos, "
                   "solo muestra que si nada cambia las emisiones quedan en %s y la meta pide %s. Para estimar "
                   "una probabilidad hacen falta las medidas de reduccion y sus supuestos."
                   % (round(base, 1), round(objetivo, 1)))
    elif probabilidad >= UMBRAL_CREDIBILIDAD:
        lectura = "La meta es creible con el plan actual."
    elif probabilidad >= 0.5:
        lectura = "La meta es alcanzable, pero el plan todavia no da seguridad suficiente."
    else:
        lectura = "Con el plan actual la meta no es creible: falta un plan de reduccion concreto."
    return {
        "iteraciones": len(finales),
        "semilla": semilla,
        "anio_meta": anio_meta,
        "emisiones_meta": objetivo,
        "probabilidad_pct": None if escenario_sin_cambios else round(probabilidad * 100.0, 1),
        "es_una_estimacion": not escenario_sin_cambios,
        "cumple_si_nada_cambia": base <= objetivo,
        "media": round(media, 1),
        "desviacion_estandar": round(math.sqrt(varianza), 1),
        "percentiles": {clave: round(_percentil(finales, valor), 1) for clave, valor in
                        (("p5", 0.05), ("p10", 0.10), ("p25", 0.25), ("p50", 0.50),
                         ("p75", 0.75), ("p90", 0.90), ("p95", 0.95))},
        "brecha_mediana": round(max(mediana - objetivo, 0.0), 1),
        "lectura": lectura,
        "umbral_credibilidad_pct": UMBRAL_CREDIBILIDAD * 100,
        "supuestos": {
            "crecimiento": crecimiento, "descarbonizacion_red": descarbonizacion,
            "eficiencia": eficiencia, "proyectos": proyectos,
        },
        "aviso": ("El resultado depende por completo de los supuestos de arriba: si cambian, cambia la "
                  "probabilidad. Publica los supuestos junto con la meta."),
    }
