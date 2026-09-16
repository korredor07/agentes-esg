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
import difflib
import os
import re
import unicodedata

from nucleo import unidades
from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_FACTORES = os.path.join(CARPETA_DATOS, "factores_emision.csv")
ARCHIVO_PCG = os.path.join(CARPETA_DATOS, "pcg.csv")
ARCHIVO_DENSIDADES = os.path.join(CARPETA_DATOS, "densidades_combustibles.csv")

CALIDADES = {"estimado": 1, "reportado": 2, "verificado": 3}

# Solo para escribir avisos que se entiendan: «un factor de Chile» y no «de CL».
PAISES_LARGOS = {"CL": "Chile", "PE": "Peru", "AR": "Argentina", "CO": "Colombia",
                 "MX": "Mexico", "BR": "Brasil", "ES": "Espana", "US": "Estados Unidos",
                 "*": "referencia internacional"}

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
    # Alcance 3: transporte de carga
    "camion": "camion_carga", "camion de carga": "camion_carga", "flete": "camion_carga",
    "flete camion": "camion_carga", "flete terrestre": "camion_carga", "transporte terrestre": "camion_carga",
    "hgv": "camion_carga", "camion carga": "camion_carga",
    "camion refrigerado": "camion_refrigerado", "transporte refrigerado": "camion_refrigerado",
    "furgon": "furgon", "furgoneta": "furgon", "van": "furgon",
    "tren de carga": "tren_carga", "ferrocarril": "tren_carga", "tren carga": "tren_carga",
    "barco": "barco_contenedor", "buque": "barco_contenedor", "contenedor": "barco_contenedor",
    "maritimo": "barco_contenedor", "flete maritimo": "barco_contenedor", "barco contenedor": "barco_contenedor",
    "granel": "granelero", "granelero": "granelero", "carga general": "barco_carga_general",
    "flete aereo": "carga_aerea", "avion carga": "carga_aerea", "carga aerea": "carga_aerea",
    # Alcance 3: viajes
    "avion": "avion_larga_distancia_economica", "vuelo": "avion_larga_distancia_economica",
    "vuelo internacional": "avion_larga_distancia_economica", "pasaje aereo": "avion_larga_distancia_economica",
    "vuelo nacional": "avion_nacional", "vuelo corto": "avion_corta_distancia",
    "auto": "auto", "vehiculo": "auto", "automovil": "auto", "camioneta": "auto",
    "taxi": "taxi", "uber": "taxi", "aplicacion de transporte": "taxi",
    "bus": "bus", "micro": "bus", "autobus": "bus", "bus interurbano": "bus_interurbano",
    "tren": "tren_pasajeros", "metro": "tren_pasajeros", "tren pasajeros": "tren_pasajeros",
    "hotel": "hotel", "alojamiento": "hotel", "hospedaje": "hotel", "noche de hotel": "hotel",
    # Alcance 3: residuos y agua
    "basura": "residuo_mixto_relleno", "residuos": "residuo_mixto_relleno",
    "residuo mixto": "residuo_mixto_relleno", "relleno sanitario": "residuo_mixto_relleno",
    "reciclaje": "residuo_mixto_reciclaje", "residuos reciclados": "residuo_mixto_reciclaje",
    "organicos": "organico_relleno", "compostaje": "organico_compostaje",
    "agua": "agua_potable", "agua potable": "agua_potable", "consumo de agua": "agua_potable",
    "alcantarillado": "agua_residual", "aguas servidas": "agua_residual", "agua residual": "agua_residual",
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


def cargar_densidades(ruta=None):
    """Densidades de combustibles para convertir litros a kilos y viceversa.

    El IPCC no publica densidades: vienen de fuentes nacionales o de la
    referencia internacional, y cada fila dice cual.
    """
    ruta = ruta or ARCHIVO_DENSIDADES
    tabla = {}
    if not os.path.isfile(ruta):
        return tabla
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            recurso = normalizar_recurso(fila.get("recurso"))
            pais = (fila.get("pais") or "*").strip().upper() or "*"
            valor = _numero(fila.get("densidad_kg_por_litro"))
            if recurso and valor:
                tabla[(recurso, pais)] = {
                    "kg_por_litro": valor, "fuente": (fila.get("fuente") or "").strip(),
                    "notas": (fila.get("notas") or "").strip(),
                }
    return tabla


def densidad_de(recurso, pais=None, densidades=None):
    """Devuelve la densidad del combustible para ese pais, o la internacional."""
    densidades = densidades if densidades is not None else cargar_densidades()
    clave = normalizar_recurso(recurso)
    pais = (pais or "").upper()
    return densidades.get((clave, pais)) or densidades.get((clave, "*"))


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


def _puente_por_densidad(una, otra):
    """Masa y volumen se pueden convertir si hay densidad del combustible."""
    try:
        magnitudes = {unidades.normalizar_unidad(una)[0], unidades.normalizar_unidad(otra)[0]}
    except Problema:
        return False
    return magnitudes == {"masa", "volumen"}


# Palabras que aparecen en muchos nombres y no ayudan a distinguir cual es cual.
PALABRAS_VAGAS = {"gasto", "compra", "compras", "servicio", "servicios", "de", "del", "la", "el"}


def parecidos(factores, recurso, limite=6):
    """Nombres del catalogo que se parecen a lo que escribio la persona.

    Busca en el nombre y tambien en la descripcion del factor, porque nadie
    escribe «gasto agricultura» cuando lo que compra es harina. Sirve para que
    un «no tengo ese factor» venga con alternativas concretas en vez de dejar a
    la persona adivinando la palabra exacta.
    """
    clave = normalizar_recurso(recurso).replace("_", " ")
    palabras = {p for p in clave.split() if len(p) > 2}
    utiles = palabras - PALABRAS_VAGAS
    unicos = {}
    for factor in factores:
        unicos.setdefault(factor["recurso"], factor)

    puntuados = []
    for nombre, factor in unicos.items():
        del_nombre = set(nombre.replace("_", " ").split())
        de_notas = set(_clave(factor["notas"]).replace("_", " ").split())
        similitud = difflib.SequenceMatcher(None, clave, nombre.replace("_", " ")).ratio()
        puntaje = similitud
        puntaje += 4.0 * len(utiles & del_nombre)
        puntaje += 3.0 * len(utiles & de_notas)
        puntaje += 1.0 * len((palabras & PALABRAS_VAGAS) & del_nombre)
        if puntaje < 0.7:
            continue
        puntuados.append((puntaje, nombre, factor))

    puntuados.sort(key=lambda p: (-p[0], p[1]))
    return [{"recurso": f["recurso_original"], "unidad": f["unidad"], "alcance": f["alcance"],
             "uso": f["uso"], "notas": f["notas"]}
            for _, _, f in puntuados[:limite]]


def _sugerencia_sin_factor(factores, recurso):
    opciones = parecidos(factores, recurso)
    if not opciones:
        return ("Mira que nombres existen con: huella factores --uso gasto, o busca por lo que se "
                "compra: huella factores --recurso <palabra>. Si de verdad no esta, puedo buscar el "
                "factor en una fuente oficial y agregarlo con su respaldo.")
    utiles = {p for p in normalizar_recurso(recurso).replace("_", " ").split()
              if len(p) > 2} - PALABRAS_VAGAS
    coincide = any(utiles & set(o["recurso"].split()) or
                   utiles & set(_clave(o["notas"]).replace("_", " ").split())
                   for o in opciones)
    listado = "; ".join("«%s» (%s%s)" % (o["recurso"], o["unidad"],
                                         ", %s" % o["notas"] if o["notas"] else "")
                        for o in opciones)
    if not coincide:
        return ("Ese nombre no existe en el catalogo y ninguno se le parece de verdad. Preguntale a la "
                "persona que compra exactamente y busca la palabra concreta con: huella factores "
                "--recurso <lo que compra>. La lista completa de los de gasto sale con: huella factores "
                "--uso gasto. Algunos del mismo tipo: %s." % listado)
    return ("En el catalogo hay nombres parecidos: %s. Preguntale a la persona cual describe mejor lo "
            "que compra (la diferencia entre uno y otro puede ser varias veces el resultado), escribelo "
            "tal cual en la planilla, y si ninguno calza dimelo para buscar el factor en una fuente "
            "oficial." % listado)


def buscar_factor(factores, recurso, unidad=None, pais=None, anio=None, alcance=None,
                  categoria=None, uso=None, permitir_densidad=False):
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
            _sugerencia_sin_factor(factores, recurso),
            {"recurso": recurso, "nombres_parecidos": parecidos(factores, recurso)},
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
            if "Tabla 8.A.1" not in (globales[0].get("fuente") or ""):
                # El potencial de calentamiento de un gas es el mismo en todas partes:
                # avisar de eso seria ruido, no informacion.
                advertencias.append(
                    "No tengo un factor propio de %s para %s: use una referencia internacional."
                    % (PAISES_LARGOS.get(pais, pais), recurso))
            candidatos = globales
        elif pais:
            prestado = candidatos[0]
            aviso = ("El factor de %s que use es de %s, no de %s: no hay uno oficial de %s en el "
                     "catalogo." % (recurso, PAISES_LARGOS.get(prestado["pais"], prestado["pais"]),
                                    PAISES_LARGOS.get(pais, pais), PAISES_LARGOS.get(pais, pais)))
            if "IPCC" in prestado.get("fuente", ""):
                aviso += (" Sale de los valores por defecto del IPCC, que son internacionales, asi "
                          "que sirve como estimacion; lo que cambia de un pais a otro es la mezcla "
                          "exacta del combustible. Se usa como estimacion y queda declarado como supuesto.")
            else:
                aviso += " Se usa como estimacion y queda declarado como supuesto."
            advertencias.append(aviso)

    if unidad:
        compatibles = [f for f in candidatos if _misma_unidad(f["unidad"], unidad)
                       or (permitir_densidad and _puente_por_densidad(f["unidad"], unidad))]
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


def calcular_registro(registro, factores, pcg, conjunto="AR6", pais=None, densidades=None):
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
    pais_registro = registro.get("pais") or pais
    densidad = densidad_de(recurso, pais_registro, densidades)
    factor, advertencias = buscar_factor(
        factores, recurso, unidad=unidad,
        pais=pais_registro, anio=anio,
        alcance=registro.get("alcance"), categoria=registro.get("categoria"),
        uso=registro.get("uso"), permitir_densidad=bool(densidad))

    por_densidad = False
    if _clave(unidad) == _clave(factor["unidad"]):
        cantidad_convertida = cantidad
    elif unidades.misma_magnitud(unidad, factor["unidad"]):
        cantidad_convertida = unidades.convertir(cantidad, unidad, factor["unidad"])
    elif densidad and _puente_por_densidad(unidad, factor["unidad"]):
        origen = unidades.normalizar_unidad(unidad)[0]
        if origen == "masa":
            litros = unidades.convertir(cantidad, unidad, "kg") / densidad["kg_por_litro"]
            cantidad_convertida = unidades.convertir(litros, "L", factor["unidad"])
        else:
            kilos = unidades.convertir(cantidad, unidad, "L") * densidad["kg_por_litro"]
            cantidad_convertida = unidades.convertir(kilos, "kg", factor["unidad"])
        # Una sola linea: antes salian dos avisos de la misma conversion.
        advertencias.append(
            "%s %s de %s se convirtieron a %s %s con una densidad de %s kg/L (%s)."
            % (cantidad, unidad, recurso, round(cantidad_convertida, 4), factor["unidad"],
               densidad["kg_por_litro"], densidad["fuente"]))
        por_densidad = True
    else:
        cantidad_convertida = unidades.convertir(cantidad, unidad, factor["unidad"])
    if not por_densidad and abs(cantidad_convertida - cantidad) > 1e-9:
        advertencias.append("%s %s se convirtieron a %s %s para usar el factor."
                            % (cantidad, unidad, round(cantidad_convertida, 4), factor["unidad"]))
    por_unidad, avisos_pcg = kg_co2e_por_unidad(factor, pcg, conjunto)
    advertencias.extend(avisos_pcg)

    calidad = _clave(registro.get("calidad_del_dato") or registro.get("calidad_dato")
                     or registro.get("calidad") or "estimado")
    if calidad not in CALIDADES:
        advertencias.append("No reconoci la calidad de dato «%s» en la fila %s: la trate como estimada."
                            % (registro.get("calidad_del_dato") or registro.get("calidad_dato"),
                               registro.get("_fila", "?")))
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
            "url": factor["url"], "uso": factor.get("uso", ""), "calidad": factor.get("calidad", ""),
            "notas": factor.get("notas", ""),
        },
        "kg_co2e": cantidad_convertida * por_unidad,
        # Por ejemplo, «aproximacion declarada»: la skill exige que llegue al informe.
        "notas_de_la_fila": str(registro.get("notas") or "").strip(),
        "calidad_dato": calidad,
        "advertencias": advertencias,
    }


def _vacio():
    return {"kg_co2e": 0.0, "registros": 0}


def _sumar(destino, clave, kg):
    casilla = destino.setdefault(clave, _vacio())
    casilla["kg_co2e"] += kg
    casilla["registros"] += 1


def calcular(registros, factores=None, pcg=None, conjunto="AR6", pais=None, continuar_con_errores=True,
             densidades=None):
    """Calcula la huella de una lista de registros y arma los resumenes."""
    factores = factores if factores is not None else cargar_factores()
    pcg = pcg if pcg is not None else cargar_pcg()
    densidades = densidades if densidades is not None else cargar_densidades()
    detalle, problemas, advertencias = [], [], []
    for registro in registros:
        try:
            detalle.append(calcular_registro(registro, factores, pcg, conjunto, pais, densidades))
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
    por_gasto = 0.0
    total = 0.0
    for fila in detalle:
        kg = fila["kg_co2e"]
        total += kg
        if (fila.get("factor") or {}).get("uso") == "gasto":
            por_gasto += kg
        _sumar(por_alcance, "alcance_%d" % fila["alcance"], kg)
        etiqueta_sitio = fila["sitio"] or ("Cadena de valor" if fila["alcance"] == 3 else "Sin sitio asignado")
        _sumar(por_sitio, etiqueta_sitio, kg)
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
        "completo": not problemas,
        "aviso_principal": ("" if not problemas else
                            "Este total esta INCOMPLETO: %d fila(s) no se pudieron calcular y sus "
                            "emisiones no estan sumadas." % len(problemas)),
        "registros_calculados": len(detalle),
        "registros_con_problema": len(problemas),
        "por_alcance": por_alcance,
        "por_sitio": por_sitio,
        "por_recurso": por_recurso,
        "por_periodo": por_periodo,
        "por_categoria_alcance3": por_categoria,
        "calidad_datos": {"kg_co2e": por_calidad, "porcentaje": calidad_pct,
                          # La calidad del dato dice si el monto esta respaldado; el metodo dice que tan
                          # fino es el factor. Un gasto bien reportado sigue siendo una estimacion gruesa.
                          "estimado_por_gasto_kg": por_gasto,
                          "estimado_por_gasto_pct": (por_gasto / total * 100.0) if total else 0.0},
        "set_pcg": conjunto,
        "detalle": detalle,
        "problemas": problemas,
        "advertencias": sorted(set(advertencias)),
        "fuentes": fuentes,
        "calculado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
