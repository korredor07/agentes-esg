# -*- coding: utf-8 -*-
"""Calculo de huella de carbono segun el GHG Protocol.

Alcance 1: lo que la empresa quema o fuga directamente (combustibles, refrigerantes).
Alcance 2: la electricidad y energia comprada (por ubicacion y por mercado).
Alcance 3: el resto de la cadena de valor (15 categorias), por actividad o por gasto.

Formula base:
    kg CO2e = cantidad (en la unidad del factor) x factor de emision

Cuando el factor viene separado por gas, se convierte a CO2 equivalente con el
potencial de calentamiento global (PCG) del set elegido (AR5 o AR6):
    kg CO2e = kg CO2 + kg CH4 x PCG(CH4) + kg N2O x PCG(N2O)
"""

import csv
import datetime
import os
import re
import unicodedata

from nucleo import unidades
from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_FACTORES = os.path.join(CARPETA_DATOS, "factores_emision.csv")
ARCHIVO_PCG = os.path.join(CARPETA_DATOS, "pcg.csv")

CALIDADES = {"estimado": 1, "reportado": 2, "verificado": 3}

# Como escribe la gente cada recurso -> clave normalizada del catalogo de factores.
ALIAS_RECURSO = {
    "electricidad": "electricidad", "energia electrica": "electricidad", "luz": "electricidad",
    "red electrica": "electricidad", "electricidad comprada": "electricidad", "kwh": "electricidad",
    "diesel": "diesel", "petroleo diesel": "diesel", "gasoil": "diesel", "gasoleo": "diesel",
    "petroleo": "diesel", "diesel b5": "diesel",
    "gasolina": "gasolina", "bencina": "gasolina", "nafta": "gasolina", "gasolina 93": "gasolina",
    "gasolina 95": "gasolina", "gasolina 97": "gasolina",
    "glp": "glp", "gas licuado": "glp", "gas licuado de petroleo": "glp", "gas de canete": "glp",
    "balon de gas": "glp", "propano": "glp",
    "gas natural": "gas_natural", "gn": "gas_natural", "gas de red": "gas_natural",
    "gnl": "gas_natural_licuado", "gnc": "gas_natural_comprimido",
    "kerosene": "kerosene", "parafina": "kerosene", "queroseno": "kerosene",
    "fuel oil": "fuel_oil", "petroleo 6": "fuel_oil", "petroleo numero 6": "fuel_oil",
    "carbon": "carbon", "carbon mineral": "carbon", "coque": "coque",
    "lena": "lena", "biomasa": "biomasa", "pellet": "pellet", "astillas": "biomasa",
    "biodiesel": "biodiesel", "etanol": "etanol",
    "vapor": "vapor", "agua caliente": "calor", "calor": "calor", "frio": "frio",
}


def _clave(texto):
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def normalizar_recurso(texto):
    clave = _clave(texto).replace("_", " ")
    return ALIAS_RECURSO.get(clave, _clave(texto))


# --------------------------------------------------------------------------
# Catalogo de factores
# --------------------------------------------------------------------------

def _numero(valor):
    if valor in (None, ""):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def cargar_pcg(ruta=None):
    """Lee la tabla de potenciales de calentamiento global."""
    ruta = ruta or ARCHIVO_PCG
    tabla = {"AR5": {}, "AR6": {}}
    if not os.path.isfile(ruta):
        return tabla
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            gas = _clave(fila.get("gas"))
            if not gas:
                continue
            for conjunto in ("AR5", "AR6"):
                valor = _numero(fila.get(conjunto.lower()))
                if valor is not None:
                    tabla[conjunto][gas] = valor
    return tabla


def cargar_factores(ruta=None):
    """Lee el catalogo de factores de emision."""
    ruta = ruta or ARCHIVO_FACTORES
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro el catalogo de factores de emision (%s)." % os.path.basename(ruta),
            "Sin factores no puedo calcular emisiones. Avisa para reinstalar los datos del motor.",
        )
    factores = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for numero, fila in enumerate(csv.DictReader(archivo), start=2):
            if not (fila.get("recurso") or "").strip():
                continue
            factores.append({
                "id": (fila.get("id") or "").strip(),
                "alcance": int(_numero(fila.get("alcance")) or 0),
                "categoria": (fila.get("categoria") or "").strip(),
                "uso": _clave(fila.get("uso")),
                "recurso": normalizar_recurso(fila.get("recurso")),
                "recurso_original": (fila.get("recurso") or "").strip(),
                "pais": (fila.get("pais") or "*").strip().upper() or "*",
                "anio": int(_numero(fila.get("anio")) or 0),
                "unidad": (fila.get("unidad") or "").strip(),
                "kg_co2": _numero(fila.get("kg_co2_por_unidad")),
                "kg_ch4": _numero(fila.get("kg_ch4_por_unidad")),
                "kg_n2o": _numero(fila.get("kg_n2o_por_unidad")),
                "kg_co2e": _numero(fila.get("kg_co2e_por_unidad")),
                "set_pcg": (fila.get("set_pcg") or "").strip().upper(),
                "calidad": (fila.get("calidad") or "").strip(),
                "fuente": (fila.get("fuente") or "").strip(),
                "url": (fila.get("url") or "").strip(),
                "licencia": (fila.get("licencia") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
                "linea": numero,
            })
    return factores


def kg_co2e_por_unidad(factor, pcg, conjunto="AR6"):
    """Convierte un factor a kg CO2e por unidad."""
    if factor.get("kg_co2e") is not None:
        return factor["kg_co2e"], []
    tabla = pcg.get(conjunto) or {}
    if not tabla:
        raise Problema(
            "No tengo la tabla de potenciales de calentamiento global (%s)." % conjunto,
            "Sin esa tabla no puedo convertir metano y oxido nitroso a CO2 equivalente.",
        )
    advertencias = []
    total = factor.get("kg_co2") or 0.0
    for gas, clave in (("kg_ch4", "ch4"), ("kg_n2o", "n2o")):
        cantidad = factor.get(gas)
        if cantidad:
            if clave not in tabla:
                advertencias.append("No tengo el PCG de %s en %s: ese gas quedo fuera del total."
                                    % (clave.upper(), conjunto))
                continue
            total += cantidad * tabla[clave]
    return total, advertencias


def _misma_unidad(una, otra):
    """Unidades equivalentes: iguales tal cual (USD, unidades, pasajeros) o convertibles."""
    if _clave(una) == _clave(otra):
        return True
    return unidades.misma_magnitud(una, otra)


def buscar_factor(factores, recurso, unidad=None, pais=None, anio=None, alcance=None,
                  categoria=None, uso=None):
    """Elige el factor mas apropiado y explica por que."""
    clave = normalizar_recurso(recurso)
    candidatos = [f for f in factores if f["recurso"] == clave]
    if alcance:
        candidatos = [f for f in candidatos if f["alcance"] == int(alcance)] or candidatos
    if categoria:
        candidatos = [f for f in candidatos if not f["categoria"] or f["categoria"] == str(categoria)] or candidatos
    if not candidatos:
        raise Problema(
            "No tengo un factor de emision para «%s»." % recurso,
            "Puedo buscarlo en una fuente oficial y agregarlo con su respaldo, o puedes indicarme uno tu.",
            {"recurso": recurso},
        )

    advertencias = []
    usos = sorted({f["uso"] for f in candidatos if f.get("uso")})
    if uso:
        clave_uso = _clave(uso)
        por_uso = [f for f in candidatos if f.get("uso") == clave_uso]
        if por_uso:
            candidatos = por_uso
        elif usos:
            advertencias.append("No tengo factor de «%s» para uso %s: use el de uso %s."
                                % (recurso, uso, usos[0]))
    elif len(usos) > 1 and "estacionaria" in usos:
        candidatos = [f for f in candidatos if f.get("uso") == "estacionaria"]
        advertencias.append(
            "Asumi uso estacionario (calderas, generadores o calefaccion) para %s. "
            "Si ese combustible es de vehiculos o maquinaria movil, dimelo y uso el factor movil."
            % recurso)

    pais = (pais or "").upper()
    del_pais = [f for f in candidatos if f["pais"] == pais] if pais else []
    if del_pais:
        candidatos = del_pais
    else:
        globales = [f for f in candidatos if f["pais"] == "*"]
        if pais and globales:
            advertencias.append(
                "No tengo factor propio de %s para %s: use un factor internacional de referencia."
                % (pais, recurso))
            candidatos = globales
        elif pais:
            advertencias.append(
                "El factor disponible para %s es de %s, no de %s."
                % (recurso, candidatos[0]["pais"], pais))

    if unidad:
        compatibles = [f for f in candidatos if _misma_unidad(f["unidad"], unidad)]
        if not compatibles:
            disponible = candidatos[0]["unidad"]
            monetaria = not unidades.misma_magnitud(disponible, disponible)
            raise Problema(
                "El factor de «%s» esta en %s y tus datos estan en %s."
                % (recurso, disponible, unidad),
                "Necesito el tipo de cambio o el monto en %s para poder usarlo." % disponible
                if monetaria else
                "Revisa la unidad en la planilla o dime en que unidad esta realmente el consumo.",
            )
        candidatos = compatibles

    if anio:
        anio = int(anio)
        anteriores = [f for f in candidatos if f["anio"] and f["anio"] <= anio]
        elegido = max(anteriores, key=lambda f: f["anio"]) if anteriores else \
            min(candidatos, key=lambda f: abs((f["anio"] or 0) - anio))
        anios_disponibles = {f["anio"] for f in candidatos if f["anio"]}
        serie_anual = len(anios_disponibles) > 1
        brecha = abs((elegido["anio"] or anio) - anio)
        if elegido["anio"] and elegido["anio"] != anio and (serie_anual or brecha >= 3):
            advertencias.append(
                "Para %s use el factor de %d, que es el mas cercano que tengo a %d."
                % (recurso, elegido["anio"], anio))
    else:
        elegido = max(candidatos, key=lambda f: f["anio"] or 0)
    return elegido, advertencias


# --------------------------------------------------------------------------
# Calculo
# --------------------------------------------------------------------------

def _periodo_y_anio(registro):
    crudo = str(registro.get("periodo") or registro.get("fecha") or "").strip()
    if not crudo:
        return "", None
    coincidencia = re.match(r"^(\d{4})", crudo)
    if coincidencia:
        return crudo[:7] if len(crudo) >= 7 and crudo[4] in "-/" else crudo[:4], int(coincidencia.group(1))
    coincidencia = re.search(r"(\d{4})", crudo)
    return crudo, int(coincidencia.group(1)) if coincidencia else None


def calcular_registro(registro, factores, pcg, conjunto="AR6", pais=None):
    """Calcula las emisiones de una fila de consumo."""
    recurso = registro.get("recurso") or registro.get("combustible") or registro.get("tipo")
    if not recurso:
        raise Problema(
            "Falta indicar que se consumio en la fila %s." % registro.get("_fila", "?"),
            "Completa la columna «Recurso» (electricidad, diesel, gas natural, ...).",
        )
    cantidad = registro.get("cantidad")
    if cantidad in (None, ""):
        raise Problema(
            "Falta la cantidad en la fila %s (%s)." % (registro.get("_fila", "?"), recurso),
            "Escribe cuanto se consumio en esa fila, o borra la fila si no aplica.",
        )
    try:
        cantidad = float(str(cantidad).replace(",", "."))
    except ValueError:
        raise Problema(
            "La cantidad «%s» de la fila %s no es un numero." % (cantidad, registro.get("_fila", "?")),
            "Escribe solo el numero, sin unidades ni texto (la unidad va en su propia columna).",
        )
    unidad = registro.get("unidad")
    if not unidad:
        raise Problema(
            "Falta la unidad en la fila %s (%s)." % (registro.get("_fila", "?"), recurso),
            "Indica la unidad: kWh, litros, m3, kg, toneladas, km...",
        )

    periodo, anio = _periodo_y_anio(registro)
    factor, advertencias = buscar_factor(
        factores, recurso, unidad=unidad,
        pais=(registro.get("pais") or pais), anio=anio,
        alcance=registro.get("alcance"), categoria=registro.get("categoria"),
        uso=registro.get("uso"))

    if _clave(unidad) == _clave(factor["unidad"]):
        cantidad_convertida = cantidad
    else:
        cantidad_convertida = unidades.convertir(cantidad, unidad, factor["unidad"])
    if abs(cantidad_convertida - cantidad) > 1e-9:
        advertencias.append("Converti %s %s a %s %s para usar el factor."
                            % (cantidad, unidad, round(cantidad_convertida, 4), factor["unidad"]))
    por_unidad, avisos_pcg = kg_co2e_por_unidad(factor, pcg, conjunto)
    advertencias.extend(avisos_pcg)

    calidad = _clave(registro.get("calidad_dato") or registro.get("calidad") or "estimado")
    if calidad not in CALIDADES:
        advertencias.append("No reconoci la calidad de dato «%s» en la fila %s: la trate como estimada."
                            % (registro.get("calidad_dato"), registro.get("_fila", "?")))
        calidad = "estimado"

    return {
        "fila": registro.get("_fila"),
        "periodo": periodo,
        "anio": anio,
        "sitio": registro.get("sitio") or "",
        "recurso": recurso,
        "uso": factor.get("uso", ""),
        "alcance": int(registro.get("alcance") or factor["alcance"] or 0),
        "categoria": str(registro.get("categoria") or factor["categoria"] or ""),
        "cantidad": cantidad,
        "unidad": unidad,
        "cantidad_en_unidad_factor": cantidad_convertida,
        "factor": {
            "id": factor["id"], "valor": por_unidad, "unidad": factor["unidad"],
            "pais": factor["pais"], "anio": factor["anio"], "fuente": factor["fuente"],
            "url": factor["url"],
        },
        "kg_co2e": cantidad_convertida * por_unidad,
        "calidad_dato": calidad,
        "advertencias": advertencias,
    }


def _vacio():
    return {"kg_co2e": 0.0, "registros": 0}


def _sumar(destino, clave, kg):
    casilla = destino.setdefault(clave, _vacio())
    casilla["kg_co2e"] += kg
    casilla["registros"] += 1


def calcular(registros, factores=None, pcg=None, conjunto="AR6", pais=None, continuar_con_errores=True):
    """Calcula la huella de una lista de registros y arma los resumenes."""
    factores = factores if factores is not None else cargar_factores()
    pcg = pcg if pcg is not None else cargar_pcg()
    detalle, problemas, advertencias = [], [], []
    for registro in registros:
        try:
            detalle.append(calcular_registro(registro, factores, pcg, conjunto, pais))
        except Problema as problema:
            if not continuar_con_errores:
                raise
            problemas.append({
                "fila": registro.get("_fila"),
                "error": problema.mensaje,
                "sugerencia": problema.sugerencia,
            })

    por_alcance, por_sitio, por_recurso, por_periodo, por_categoria = {}, {}, {}, {}, {}
    por_calidad = {"estimado": 0.0, "reportado": 0.0, "verificado": 0.0}
    total = 0.0
    for fila in detalle:
        kg = fila["kg_co2e"]
        total += kg
        _sumar(por_alcance, "alcance_%d" % fila["alcance"], kg)
        _sumar(por_sitio, fila["sitio"] or "Sin sitio", kg)
        _sumar(por_recurso, fila["recurso"], kg)
        _sumar(por_periodo, fila["periodo"] or "sin periodo", kg)
        if fila["alcance"] == 3 and fila["categoria"]:
            _sumar(por_categoria, fila["categoria"], kg)
        por_calidad[fila["calidad_dato"]] = por_calidad.get(fila["calidad_dato"], 0.0) + kg
        advertencias.extend(fila["advertencias"])

    if problemas:
        advertencias.append("%d fila(s) no se pudieron calcular: revisa el detalle de problemas." % len(problemas))

    fuentes = sorted({"%s (%s)" % (f["factor"]["fuente"], f["factor"]["anio"])
                      for f in detalle if f["factor"]["fuente"]})
    calidad_pct = {clave: (valor / total * 100.0 if total else 0.0) for clave, valor in por_calidad.items()}

    return {
        "total_kg_co2e": total,
        "total_t_co2e": total / 1000.0,
        "registros_calculados": len(detalle),
        "registros_con_problema": len(problemas),
        "por_alcance": por_alcance,
        "por_sitio": por_sitio,
        "por_recurso": por_recurso,
        "por_periodo": por_periodo,
        "por_categoria_alcance3": por_categoria,
        "calidad_datos": {"kg_co2e": por_calidad, "porcentaje": calidad_pct},
        "set_pcg": conjunto,
        "detalle": detalle,
        "problemas": problemas,
        "advertencias": sorted(set(advertencias)),
        "fuentes": fuentes,
        "calculado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
