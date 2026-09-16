# -*- coding: utf-8 -*-
"""Emisiones del transporte de carga segun ISO 14083:2023.

La cadena de transporte (TC) se parte en tramos (TCE). Cada tramo es o bien
un vehiculo moviendo la carga, o bien el paso por un nodo logistico (hub):

    Curico --camion--> San Antonio --hub--> [barco] --hub--> Rotterdam --camion--> Venlo
      TCE 1               TCE 2      TCE 3    TCE 4              TCE 5

Formulas (ISO 14083:2023, clausulas 6 y 7):

    Actividad del tramo            T = masa_toneladas x distancia_km          [t.km]
    Emision del tramo de transporte G = T x intensidad_del_TOC x DAF          [kg CO2e]
    Emision del tramo de hub        G = toneladas_que_salen x intensidad_HOC  [kg CO2e]
    Emision de la cadena            G_TC = suma de todos los tramos
    Intensidad de la cadena         g_TC = G_TC / T_TC                        [g CO2e/t.km]

ISO 14083 exige reportar la suma de dos cosas, y no solo la primera:

    - emisiones de operacion (lo que sale del tubo de escape, antes «TTW»)
    - emisiones de provision de energia (producir y llevar el combustible o la
      electricidad hasta el vehiculo, antes «WTT»)

Reportar solo la operacion subestima entre un 15 % y un 30 % segun el modo.

Sobre las licencias: la metodologia de ISO 14083 y del GLEC Framework no es
objeto de copyright y aqui esta reimplementada con redaccion propia, pero los
valores por defecto del GLEC Framework NO son redistribuibles. Este modulo se
alimenta de DESNZ (Open Government Licence v3.0). Si una empresa tiene su
propia tabla GLEC puede cargarla ella, bajo su propia licencia.
"""

import csv
import os

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_FACTORES = os.path.join(CARPETA_DATOS, "transporte_iso14083.csv")

# Factor de ajuste de distancia (DAF): corrige la distancia real para dejarla
# comparable con la distancia mas corta practicable, que es sobre la que se
# calculan las intensidades. ISO 14083, tabla de tipos de distancia.
AJUSTE_DISTANCIA = {
    "carretera": {"factor": 1.05, "tipo": "SFD",
                  "explicacion": "La ruta real de un camion es un 5 % mas larga que la mas corta."},
    "maritimo": {"factor": 1.15, "tipo": "SFD",
                 "explicacion": "La ruta real de un buque es un 15 % mas larga que la mas corta."},
    "ferrocarril": {"factor": 1.0, "tipo": "SFD",
                    "explicacion": "La via fija el recorrido: no hace falta ajustar."},
    "fluvial": {"factor": 1.0, "tipo": "SFD",
                "explicacion": "La via fija el recorrido: no hace falta ajustar."},
    "aereo": {"factor": 1.0, "tipo": "GCD", "suma_km": 95.0,
              "explicacion": "Se usa la distancia en linea recta mas 95 km por el rodaje, "
                             "el despegue y la aproximacion."},
}

# Masa por contenedor cuando no se conoce el peso real de la carga.
TONELADAS_POR_TEU = {"ligera": 6.0, "promedio": 10.0, "pesada": 14.5}

MODOS = ("carretera", "ferrocarril", "maritimo", "aereo", "fluvial")

# Como escribe la gente cada modo o vehiculo -> id del factor.
ALIAS = {
    "camion": "desnz-hgv-promedio", "camion de carga": "desnz-hgv-promedio",
    "flete": "desnz-hgv-promedio", "flete terrestre": "desnz-hgv-promedio",
    "hgv": "desnz-hgv-promedio", "camion promedio": "desnz-hgv-promedio",
    "camion rigido": "desnz-hgv-rigido", "rigido": "desnz-hgv-rigido",
    "camion articulado": "desnz-hgv-articulado", "tracto": "desnz-hgv-articulado",
    "semirremolque": "desnz-hgv-articulado", "articulado": "desnz-hgv-articulado",
    "camion refrigerado": "desnz-hgv-refrigerado", "refrigerado": "desnz-hgv-refrigerado",
    "camion frigorifico": "desnz-hgv-refrigerado", "cadena de frio": "desnz-hgv-refrigerado",
    "furgon": "desnz-furgon", "furgoneta": "desnz-furgon", "van": "desnz-furgon",
    "reparto": "desnz-furgon", "ultima milla": "desnz-furgon",
    "tren": "desnz-tren", "tren de carga": "desnz-tren", "ferrocarril": "desnz-tren",
    "barco": "desnz-contenedor", "buque": "desnz-contenedor", "contenedor": "desnz-contenedor",
    "portacontenedores": "desnz-contenedor", "maritimo": "desnz-contenedor",
    "flete maritimo": "desnz-contenedor",
    "granelero": "desnz-granelero", "granel": "desnz-granelero",
    "carga general": "desnz-carga-general", "roro": "desnz-roro", "transbordador": "desnz-roro",
    "avion": "desnz-aereo-corto", "aereo": "desnz-aereo-corto", "flete aereo": "desnz-aereo-corto",
    "avion nacional": "desnz-aereo-nacional", "vuelo nacional": "desnz-aereo-nacional",
}


def _clave(texto):
    return " ".join(str(texto or "").strip().lower().split())


def _numero(valor, campo, fila=None):
    if valor in (None, ""):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        raise Problema(
            "«%s» no es un numero valido para %s%s." % (valor, campo,
                                                        " en el tramo %s" % fila if fila else ""),
            "Escribe solo el numero, sin unidades ni texto.",
        )


def cargar_factores(ruta=None):
    """Lee la tabla de intensidades de transporte, con operacion y provision separadas."""
    ruta = ruta or ARCHIVO_FACTORES
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro la tabla de factores de transporte (%s)." % os.path.basename(ruta),
            "Sin ella no puedo calcular emisiones de logistica. Avisa para reinstalar los datos.",
        )
    factores = {}
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if not (fila.get("id") or "").strip():
                continue
            factores[fila["id"].strip()] = {
                "id": fila["id"].strip(),
                "modo": _clave(fila.get("modo")),
                "vehiculo": _clave(fila.get("vehiculo")),
                "detalle": (fila.get("detalle") or "").strip(),
                "unidad": (fila.get("unidad") or "t.km").strip(),
                "operacion": float(fila["kg_co2e_ttw"]),
                "provision": float(fila["kg_co2e_wtt"]),
                "total": float(fila["kg_co2e_wtw"]),
                "anio": int(fila.get("anio") or 0),
                "fuente": (fila.get("fuente") or "").strip(),
                "url": (fila.get("url") or "").strip(),
                "licencia": (fila.get("licencia") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
            }
    return factores


def buscar_factor(factores, vehiculo, modo=None):
    """Encuentra la intensidad del vehiculo, escrito como lo diria la persona."""
    clave = _clave(vehiculo)
    if clave in factores:
        return factores[clave]
    if clave in ALIAS and ALIAS[clave] in factores:
        return factores[ALIAS[clave]]
    candidatos = [f for f in factores.values()
                  if clave and (clave in f["vehiculo"] or clave in _clave(f["detalle"]))]
    if modo:
        del_modo = [f for f in candidatos if f["modo"] == _clave(modo)]
        candidatos = del_modo or candidatos
    if len(candidatos) == 1:
        return candidatos[0]
    if candidatos:
        raise Problema(
            "Hay varios vehiculos que calzan con «%s»." % vehiculo,
            "Elige uno: %s." % ", ".join(sorted(f["id"] for f in candidatos)),
        )
    raise Problema(
        "No tengo la intensidad de emision de «%s»." % vehiculo,
        "Los vehiculos disponibles son: %s. Tambien puedes darme el dato real del transportista "
        "con --intensidad (kg CO2e por t.km)." % ", ".join(sorted(ALIAS)),
    )


def distancia_de_actividad(distancia_km, modo, tipo_distancia="SFD"):
    """Deja la distancia comparable con la que se uso para calcular la intensidad.

    ISO 14083 pide que la distancia del tramo y la de la intensidad sean del
    mismo tipo. Mezclarlas es el error mas comun del metodo.
    """
    modo = _clave(modo)
    if modo not in AJUSTE_DISTANCIA:
        raise Problema(
            "No conozco el modo de transporte «%s»." % modo,
            "Los modos son: %s." % ", ".join(sorted(AJUSTE_DISTANCIA)),
        )
    regla = AJUSTE_DISTANCIA[modo]
    tipo = str(tipo_distancia or "SFD").strip().upper()
    avisos = []

    if modo == "aereo":
        if tipo != "GCD":
            avisos.append("El transporte aereo se calcula siempre sobre la distancia en linea recta "
                          "(GCD). Tome la distancia dada como si lo fuera.")
        ajustada = distancia_km + regla["suma_km"]
        return {"distancia_km": round(ajustada, 4), "daf": 1.0, "suma_km": regla["suma_km"],
                "tipo_usado": "GCD", "explicacion": regla["explicacion"], "advertencias": avisos}

    if tipo == "REAL":
        # La distancia del odometro ya incluye el rodeo: se divide para volver a SFD.
        ajustada = distancia_km / regla["factor"] if regla["factor"] else distancia_km
        return {"distancia_km": round(ajustada, 4), "daf": 1.0 / regla["factor"],
                "tipo_usado": "SFD",
                "explicacion": "Se convirtio la distancia real del recorrido a la distancia mas corta "
                               "practicable, que es la base de la intensidad. " + regla["explicacion"],
                "advertencias": avisos}

    if tipo == "GCD":
        ajustada = distancia_km * regla["factor"]
        return {"distancia_km": round(ajustada, 4), "daf": regla["factor"], "tipo_usado": "SFD",
                "explicacion": "Se ajusto la distancia en linea recta al recorrido practicable. "
                               + regla["explicacion"],
                "advertencias": avisos}

    return {"distancia_km": round(distancia_km, 4), "daf": 1.0, "tipo_usado": "SFD",
            "explicacion": "La distancia ya es la mas corta practicable: no necesita ajuste.",
            "advertencias": avisos}


def masa_de_contenedores(teu, carga="promedio"):
    """Toneladas que se asumen por contenedor cuando no se conoce el peso real."""
    clave = _clave(carga) or "promedio"
    if clave not in TONELADAS_POR_TEU:
        raise Problema(
            "No se que tan cargado viene el contenedor: «%s»." % carga,
            "Puede ser ligera, promedio o pesada. Mejor todavia: dime las toneladas reales.",
        )
    return {
        "toneladas": teu * TONELADAS_POR_TEU[clave],
        "toneladas_por_teu": TONELADAS_POR_TEU[clave],
        "supuesto": "Se asumieron %s toneladas por contenedor (carga %s) porque no se dio el peso real."
                    % (TONELADAS_POR_TEU[clave], clave),
    }


def calcular_tramo(tramo, factores):
    """Emisiones de un tramo de la cadena: un vehiculo, o el paso por un hub."""
    numero = tramo.get("_fila") or tramo.get("tramo") or "?"
    tipo = _clave(tramo.get("tipo")) or "transporte"

    toneladas = _numero(tramo.get("toneladas") or tramo.get("masa_t"), "las toneladas", numero)
    if toneladas is None:
        teu = _numero(tramo.get("teu"), "los contenedores", numero)
        if teu:
            supuesto = masa_de_contenedores(teu, tramo.get("carga") or "promedio")
            toneladas = supuesto["toneladas"]
            aviso_masa = [supuesto["supuesto"]]
        else:
            raise Problema(
                "Al tramo %s le faltan las toneladas de carga." % numero,
                "Escribe la masa de la mercancia incluido el embalaje del vendedor, pero sin los "
                "palets ni el contenedor. Si solo sabes cuantos contenedores son, pon los TEU.",
            )
    else:
        aviso_masa = []

    if tipo in ("hub", "nodo", "terminal", "bodega", "puerto"):
        intensidad = _numero(tramo.get("intensidad"), "la intensidad del hub", numero)
        if intensidad is None:
            return {
                "tramo": numero, "tipo": "hub", "descripcion": tramo.get("descripcion") or "Hub",
                "toneladas": toneladas, "t_km": 0.0,
                "kg_co2e_operacion": None, "kg_co2e_provision": None, "kg_co2e_total": None,
                "calculado": False,
                "motivo": "No hay un factor publico y redistribuible de emisiones de hub. "
                          "ISO 14083 exige incluirlos, asi que este total queda incompleto: "
                          "pidele al operador del terminal su intensidad en kg CO2e por tonelada "
                          "y pasala con la columna Intensidad.",
                "advertencias": aviso_masa,
            }
        total = toneladas * intensidad
        return {
            "tramo": numero, "tipo": "hub", "descripcion": tramo.get("descripcion") or "Hub",
            "toneladas": toneladas, "t_km": 0.0, "intensidad": intensidad,
            "kg_co2e_operacion": None, "kg_co2e_provision": None, "kg_co2e_total": total,
            "calculado": True,
            "fuente": tramo.get("fuente") or "Dato entregado por el operador del hub",
            "advertencias": aviso_masa + [
                "La intensidad del hub la entrego la empresa, no sale de una fuente publica: "
                "guarda el respaldo."],
        }

    distancia = _numero(tramo.get("km") or tramo.get("distancia_km") or tramo.get("distancia"),
                        "la distancia", numero)
    if distancia is None:
        raise Problema(
            "Al tramo %s le falta la distancia en kilometros." % numero,
            "Si no la conoces, se puede estimar entre las dos ciudades o los dos puertos, pero hay "
            "que anotarlo como supuesto.",
        )

    modo = _clave(tramo.get("modo"))
    intensidad_dada = _numero(tramo.get("intensidad"), "la intensidad", numero)
    factor = None
    if intensidad_dada is None:
        factor = buscar_factor(factores, tramo.get("vehiculo") or tramo.get("modo"), modo)
        modo = modo or factor["modo"]
    elif not modo:
        raise Problema(
            "Al tramo %s le falta el modo de transporte." % numero,
            "Cuando das tu propia intensidad tengo que saber si es carretera, ferrocarril, "
            "maritimo, fluvial o aereo, para ajustar bien la distancia.",
        )

    ajuste = distancia_de_actividad(distancia, modo, tramo.get("tipo_distancia") or "SFD")
    t_km = toneladas * ajuste["distancia_km"]

    if intensidad_dada is not None:
        operacion = None
        provision = None
        total = t_km * intensidad_dada
        avisos = ["La intensidad del tramo %s la entrego el transportista: es mejor dato que el "
                  "promedio, pero guarda el respaldo. Confirma que incluya la provision de energia "
                  "y no solo la combustion, como exige ISO 14083." % numero]
        origen = tramo.get("fuente") or "Dato entregado por el transportista"
    else:
        operacion = t_km * factor["operacion"]
        provision = t_km * factor["provision"]
        total = operacion + provision
        avisos = []
        origen = "%s (%s)" % (factor["fuente"], factor["anio"])

    return {
        "tramo": numero, "tipo": "transporte",
        "descripcion": tramo.get("descripcion") or (factor["detalle"] if factor else modo),
        "modo": modo, "vehiculo": factor["id"] if factor else "dato propio",
        "toneladas": toneladas,
        "distancia_declarada_km": distancia,
        "distancia_de_actividad_km": ajuste["distancia_km"],
        "ajuste_de_distancia": ajuste["daf"],
        "tipo_de_distancia": ajuste["tipo_usado"],
        "t_km": t_km,
        "kg_co2e_operacion": operacion,
        "kg_co2e_provision": provision,
        "kg_co2e_total": total,
        "calculado": True,
        "fuente": origen,
        "advertencias": aviso_masa + avisos + ajuste["advertencias"],
    }


def calcular_cadena(tramos, nombre=None):
    """Emisiones de una cadena de transporte completa, tramo por tramo."""
    if not tramos:
        raise Problema(
            "No hay tramos que calcular.",
            "Una cadena es al menos un tramo: quien mueve la carga, cuantas toneladas y cuantos km.",
        )
    factores = cargar_factores()
    calculados = []
    problemas = []
    for numero, tramo in enumerate(tramos, start=1):
        ficha = dict(tramo)
        ficha.setdefault("_fila", numero)
        try:
            calculados.append(calcular_tramo(ficha, factores))
        except Problema as problema:
            problemas.append({"tramo": numero, "error": problema.mensaje,
                              "que_hacer": problema.sugerencia})

    con_dato = [t for t in calculados if t["calculado"]]
    sin_dato = [t for t in calculados if not t["calculado"]]
    total = sum(t["kg_co2e_total"] for t in con_dato)
    operacion = sum(t["kg_co2e_operacion"] for t in con_dato if t["kg_co2e_operacion"] is not None)
    provision = sum(t["kg_co2e_provision"] for t in con_dato if t["kg_co2e_provision"] is not None)
    actividad = sum(t["t_km"] for t in calculados)

    por_modo = {}
    for tramo in con_dato:
        clave = tramo.get("modo") or tramo["tipo"]
        casilla = por_modo.setdefault(clave, {"kg_co2e": 0.0, "t_km": 0.0, "tramos": 0})
        casilla["kg_co2e"] += tramo["kg_co2e_total"]
        casilla["t_km"] += tramo["t_km"]
        casilla["tramos"] += 1
    for clave, casilla in por_modo.items():
        casilla["porcentaje_de_las_emisiones"] = round(casilla["kg_co2e"] / total * 100.0, 1) if total else 0.0
        casilla["porcentaje_de_la_actividad"] = round(casilla["t_km"] / actividad * 100.0, 1) if actividad else 0.0

    advertencias = []
    for tramo in calculados:
        advertencias.extend(tramo.get("advertencias") or [])
    completo = not sin_dato and not problemas
    if sin_dato:
        advertencias.insert(0, "Faltan %d tramo(s) de hub: ISO 14083 exige incluirlos, asi que este "
                               "total es un piso, no la cifra final." % len(sin_dato))
    if problemas:
        advertencias.insert(0, "Hay %d tramo(s) que no pude calcular: el total esta incompleto."
                            % len(problemas))

    fuentes = sorted({t["fuente"] for t in con_dato if t.get("fuente")})
    return {
        "cadena": nombre or "Cadena de transporte",
        "tramos": calculados,
        "problemas": problemas,
        "completo": completo,
        "aviso_principal": "" if completo else
                           "TOTAL INCOMPLETO: faltan tramos por calcular o por dato de hub.",
        "total_kg_co2e": total,
        "total_t_co2e": total / 1000.0,
        "emisiones_de_operacion_kg": operacion,
        "emisiones_de_provision_kg": provision,
        "porcentaje_de_provision": round(provision / total * 100.0, 1) if total else 0.0,
        "actividad_t_km": actividad,
        "intensidad_g_co2e_por_t_km": round(total / actividad * 1000.0, 3) if actividad else None,
        "por_modo": por_modo,
        "advertencias": advertencias,
        "fuentes": fuentes,
        "metodo": "ISO 14083:2023. El total suma las emisiones de operar los vehiculos y las de "
                  "producir y distribuir su energia, como exige la norma.",
    }


def comparar_modos(toneladas, km, factores=None, candidatos=None):
    """Que pasaria si la misma carga fuera en otro modo de transporte."""
    factores = factores or cargar_factores()
    candidatos = candidatos or ["desnz-hgv-promedio", "desnz-hgv-refrigerado", "desnz-tren",
                                "desnz-contenedor", "desnz-granelero", "desnz-aereo-corto"]
    opciones = []
    for identificador in candidatos:
        factor = factores.get(identificador)
        if not factor:
            continue
        ajuste = distancia_de_actividad(km, factor["modo"], "SFD")
        t_km = toneladas * ajuste["distancia_km"]
        opciones.append({
            "vehiculo": factor["id"], "detalle": factor["detalle"], "modo": factor["modo"],
            "t_km": t_km,
            "kg_co2e": t_km * factor["total"],
            "intensidad_g_por_t_km": factor["total"] * 1000.0,
        })
    opciones.sort(key=lambda o: o["kg_co2e"])
    if opciones:
        menor = opciones[0]["kg_co2e"]
        for opcion in opciones:
            opcion["veces_el_mas_limpio"] = round(opcion["kg_co2e"] / menor, 1) if menor else None
    return {
        "toneladas": toneladas, "km": km, "opciones": opciones,
        "aviso": "La comparacion es solo de emisiones: no considera plazo, costo ni si la ruta existe. "
                 "Sirve para ver el orden de magnitud, no para decidir sola.",
    }
