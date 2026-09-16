# -*- coding: utf-8 -*-
"""Huella hidrica y gestion del agua: GRI 303, ISO 14046 y metodo AWARE.

Con el agua no basta con sumar metros cubicos. Un metro cubico consumido en el
norte de Chile no pesa lo mismo que uno consumido en el sur de Brasil, porque
en un lugar queda mucha agua disponible y en el otro casi nada. Por eso este
modulo hace dos cosas distintas:

1. CONTABILIDAD (GRI 303: Agua y efluentes 2018). Cuanta agua entro, cuanta
   salio y cuanta se quedo, separando lo que ocurre en zonas con estres
   hidrico. Es lo que piden las divulgaciones 303-3, 303-4 y 303-5.

       Consumo = Extraccion - Descarga

   Metodo de calculo aceptado por GRI 303-5. OJO: la definicion de consumo del
   glosario de GRI 303 es mas amplia que esta resta. Tambien cuenta como
   consumida el agua incorporada a productos, evaporada, transpirada, bebida
   por personas o animales, ALMACENADA para un periodo posterior y la que se
   devuelve tan contaminada que ningun otro usuario puede usarla. Si a la
   empresa le pasa alguna de esas cosas, la resta subestima el consumo y hay
   que ajustarlo a mano: el modulo lo advierte.

2. IMPACTO (ISO 14046:2014 + metodo AWARE de WULCA). Convierte el consumo en
   huella de escasez, ponderando POR DONDE ocurre:

       Huella de escasez [m3 mundo-eq] = Consumo [m3] x CF_AWARE [adimensional]

   El factor AWARE (Available WAter REmaining) se interpreta como
   m3 mundo-eq / m3 consumido, va de 0,1 a 100 y vale 1 en el promedio
   mundial de referencia del metodo. Un factor de 10 significa que en esa
   cuenca y ese mes queda diez veces menos agua disponible que en ese
   promedio: consumir 1 m3 ahi equivale a consumir 10 m3 "promedio mundo".

   El insumo correcto de AWARE es el CONSUMO (GRI 303-5), nunca la extraccion.

Lo que este modulo NO hace, porque la investigacion normativa no lo respalda:

- No separa agua dulce de otras aguas. GRI 303 fija el corte en 1.000 mg/L de
  solidos disueltos totales (TDS) y la planilla de agua no tiene columna de
  salinidad. El resultado lo declara como dato faltante en vez de suponerlo.
- No decide si un sitio esta en zona de estres hidrico: eso lo marca la
  persona en la planilla, apoyandose en WRI Aqueduct o en el WWF Water Risk
  Filter, que son las herramientas que el propio GRI 303 reconoce.
- No convierte el estres hidrico de Aqueduct en un factor AWARE ni al reves:
  miden cosas distintas (riesgo de cuenca vs. impacto por m3 consumido).
- No asigna el estandar de monitoreo de extracciones (MEE) de la DGA chilena:
  eso depende de la resolucion regional aplicable. Ver modulos/agua.py.

Fuentes de las definiciones y formulas:
  - GRI 303: Water and Effluents 2018 (divulgaciones 303-3, 303-4 y 303-5 y su
    glosario). Obligatorio para reportes publicados desde el 01-01-2021.
  - ISO 14046:2014, Huella hidrica: principios, requisitos y directrices.
  - Boulay A.-M. et al. (2018), Int J Life Cycle Assess 23(2), 368-378 (AWARE).
  - Seitfudem G., Berger M., Muller Schmied H. & Boulay A.-M. (2025),
    AWARE 2.0, Journal of Industrial Ecology y dataset en Zenodo (CC BY 4.0).
"""

import csv
import datetime
import os
import re
import unicodedata

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_AWARE = os.path.join(CARPETA_DATOS, "aware_paises.csv")

VERSION_AWARE = "AWARE 2.0"

# Atribucion que exige la licencia CC BY 4.0 del conjunto de datos AWARE 2.0.
# Tiene que ir junto a cualquier resultado que use estos factores.
ATRIBUCION_AWARE = (
    "Factores AWARE 2.0 bajo licencia CC BY 4.0. "
    "Conjunto de datos: Seitfudem, G., Berger, M., Muller Schmied, H. & Boulay, A.-M. (2025), "
    "The updated and improved method for water scarcity impact assessment in LCA, AWARE2.0, "
    "Zenodo, https://doi.org/10.5281/zenodo.15133241. "
    "Publicacion: los mismos autores (2025), Journal of Industrial Ecology, "
    "https://doi.org/10.1111/jiec.70023. "
    "Metodo original: Boulay, A.-M. et al. (2018), Int J Life Cycle Assess 23(2), 368-378, "
    "https://doi.org/10.1007/s11367-017-1333-8. "
    "Modelo hidrologico: WaterGAP 2.2e, Muller Schmied, H. et al. (2024), "
    "Geosci. Model Dev. 17(23), 8817-8852, https://doi.org/10.5194/gmd-17-8817-2024. "
    "Sin cambios en los valores: solo se reorganizaron en una tabla."
)

FUENTE_GRI303 = "GRI 303: Water and Effluents 2018 (divulgaciones 303-3, 303-4 y 303-5)"
FUENTE_ISO14046 = "ISO 14046:2014 - Gestion ambiental. Huella hidrica: principios, requisitos y directrices"
FUENTE_AWARE_METODO = ("Metodo AWARE (WULCA): Boulay A.-M. et al. (2018), Int J Life Cycle Assess 23(2), "
                       "368-378; version vigente AWARE 2.0, Seitfudem et al. (2025), "
                       "Journal of Industrial Ecology")

DONDE_CONSEGUIR_AWARE = (
    "Los factores AWARE 2.0 se descargan gratis del conjunto de datos oficial en Zenodo "
    "(https://doi.org/10.5281/zenodo.15133241) o desde el sitio de WULCA "
    "(https://wulca-waterlca.org/what-is-aware/). Para un sitio concreto usa el archivo de "
    "factores por cuenca (AWARE20_Native_CFs.xlsx), no el promedio del pais."
)

# Rango en el que AWARE trunca sus factores de caracterizacion.
FACTOR_MINIMO = 0.1
FACTOR_MAXIMO = 100.0

# Formulas implementadas, con la norma de la que salen.
FORMULAS = {
    "consumo": {
        "formula": "Consumo (m3) = Extraccion (m3) - Descarga (m3)",
        "unidades": "m3 de agua en el periodo",
        "fuente": "GRI 303-5 (metodo de calculo aceptado). Definicion completa: glosario de GRI 303",
        "advertencia": (
            "La resta no cuenta el agua almacenada para otro periodo ni el agua devuelta tan "
            "contaminada que nadie mas puede usarla. GRI 303 las cuenta como consumo: si ocurren, "
            "hay que ajustar la cifra a mano."),
    },
    "megalitros": {
        "formula": "Megalitros (ML) = metros cubicos (m3) / 1.000",
        "unidades": "1 ML = 1.000 m3 = 1.000.000 litros",
        "fuente": "GRI 303-3, 303-4 y 303-5 piden los volumenes en megalitros",
    },
    "huella_de_escasez": {
        "formula": "Huella de escasez (m3 mundo-eq) = Consumo (m3) x factor AWARE (adimensional)",
        "unidades": ("El consumo va en m3; el factor AWARE es adimensional y se interpreta como "
                     "m3 mundo-eq por cada m3 consumido; el resultado queda en m3 mundo-eq"),
        "fuente": ("Metodo AWARE (WULCA). Boulay et al. 2018; version vigente AWARE 2.0, "
                   "Seitfudem et al. 2025. Aplicado dentro del marco de ISO 14046:2014"),
        "advertencia": (
            "El insumo es el consumo de GRI 303-5, no la extraccion. El factor debe ser el de la "
            "cuenca y el mes del sitio; el promedio del pais es una aproximacion gruesa."),
    },
    "porcentaje_en_estres": {
        "formula": "Porcentaje en zonas de estres (%) = volumen en zonas con estres / volumen total x 100",
        "unidades": "porcentaje del volumen del periodo",
        "fuente": "GRI 303-3-b, 303-4-b y 303-5-b piden el desglose de las zonas con estres hidrico",
    },
}

# Las cinco fuentes de extraccion que pide desglosar la divulgacion 303-3.
ORIGENES_GRI303 = {
    "agua_superficial": "Agua superficial (rio, estero, canal, lago, embalse)",
    "agua_subterranea": "Agua subterranea (pozo, noria, sondaje, dren)",
    "agua_de_mar": "Agua de mar",
    "agua_producida": "Agua producida (la que sale junto con el mineral, el petroleo o el gas)",
    "agua_de_terceros": "Agua de terceros (empresa sanitaria, APR, otra empresa)",
    "sin_clasificar": "Sin clasificar en las cinco fuentes de GRI 303-3",
}

ALIAS_ORIGEN = {
    "red publica": "agua_de_terceros", "red": "agua_de_terceros", "agua de red": "agua_de_terceros",
    "sanitaria": "agua_de_terceros", "empresa sanitaria": "agua_de_terceros",
    "agua potable": "agua_de_terceros", "agua potable de red": "agua_de_terceros",
    "apr": "agua_de_terceros", "agua potable rural": "agua_de_terceros",
    "camion aljibe": "agua_de_terceros", "aljibe": "agua_de_terceros",
    "tercero": "agua_de_terceros", "terceros": "agua_de_terceros",
    "municipal": "agua_de_terceros", "agua municipal": "agua_de_terceros",
    "pozo": "agua_subterranea", "pozo profundo": "agua_subterranea", "noria": "agua_subterranea",
    "sondaje": "agua_subterranea", "puntera": "agua_subterranea", "dren": "agua_subterranea",
    "napa": "agua_subterranea", "acuifero": "agua_subterranea", "vertiente": "agua_subterranea",
    "agua subterranea": "agua_subterranea", "subterranea": "agua_subterranea",
    "rio": "agua_superficial", "estero": "agua_superficial", "canal": "agua_superficial",
    "lago": "agua_superficial", "laguna": "agua_superficial", "embalse": "agua_superficial",
    "tranque": "agua_superficial", "superficial": "agua_superficial",
    "agua superficial": "agua_superficial", "curso de agua": "agua_superficial",
    "mar": "agua_de_mar", "agua de mar": "agua_de_mar", "marina": "agua_de_mar",
    "agua marina": "agua_de_mar", "oceano": "agua_de_mar",
    "agua producida": "agua_producida", "agua de formacion": "agua_producida",
}

# Destinos habituales de la descarga (GRI 303-4 pide desglosar por destino).
DESTINOS_GRI303 = {
    "agua_superficial": "Agua superficial (rio, estero, canal, lago)",
    "agua_subterranea": "Agua subterranea (infiltracion, pozo de inyeccion)",
    "agua_de_mar": "Agua de mar (emisario, descarga costera)",
    "a_terceros": "A un tercero (alcantarillado, planta de tratamiento de otro, riego de otro)",
    "sin_clasificar": "Sin clasificar en los destinos de GRI 303-4",
}

ALIAS_DESTINO = {
    "alcantarillado": "a_terceros", "red de alcantarillado": "a_terceros",
    "sanitaria": "a_terceros", "planta de tratamiento": "a_terceros",
    "tercero": "a_terceros", "terceros": "a_terceros", "camion": "a_terceros",
    "rio": "agua_superficial", "estero": "agua_superficial", "canal": "agua_superficial",
    "lago": "agua_superficial", "laguna": "agua_superficial", "superficial": "agua_superficial",
    "curso de agua": "agua_superficial", "cauce": "agua_superficial",
    "mar": "agua_de_mar", "emisario": "agua_de_mar", "agua de mar": "agua_de_mar",
    "infiltracion": "agua_subterranea", "pozo de infiltracion": "agua_subterranea",
    "inyeccion": "agua_subterranea", "subterranea": "agua_subterranea",
}

CALIDADES = {"estimado": 1, "reportado": 2, "verificado": 3}

RESPUESTAS_SI = {"si", "s", "sii", "yes", "true", "verdadero", "1", "x"}
RESPUESTAS_NO = {"no", "n", "false", "falso", "0"}

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

AGREGACIONES_AWARE = {
    "no_agricola": ("No agricola: se usa en mineria, industria, procesos fabriles y servicios. "
                    "Se pondera con el consumo de agua domestico, industrial, energetico y ganadero."),
    "agricola": ("Agricola: se usa cuando el agua va a riego o a produccion de cultivos. "
                 "Se pondera con los mapas de consumo de agua de riego."),
    "no_especificado": ("No especificado: solo cuando no se sabe a que sector corresponde el consumo. "
                        "Se pondera con el consumo humano total y suele dar cifras muy distintas."),
}

ALIAS_AGREGACION = {
    "no agricola": "no_agricola", "noagricola": "no_agricola", "nonagri": "no_agricola",
    "non agri": "no_agricola", "industrial": "no_agricola", "industria": "no_agricola",
    "mineria": "no_agricola", "minera": "no_agricola", "servicios": "no_agricola",
    "agricola": "agricola", "agri": "agricola", "riego": "agricola", "agricultura": "agricola",
    "no especificado": "no_especificado", "unspecified": "no_especificado",
    "desconocido": "no_especificado", "sin especificar": "no_especificado",
}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _clave(texto):
    """Convierte 'Agua Subterranea ' en 'agua_subterranea'."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def _numero(valor, campo, fila):
    """Convierte una celda en numero, con un mensaje claro si no se puede."""
    if valor in (None, ""):
        return None
    if isinstance(valor, bool):
        raise Problema(
            "En la fila %s la columna «%s» no tiene un numero." % (fila, campo),
            "Escribe solo el numero de metros cubicos, sin texto ni unidades.",
        )
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        raise Problema(
            "En la fila %s la columna «%s» dice «%s» y eso no es un numero." % (fila, campo, valor),
            "Escribe solo el numero de metros cubicos (por ejemplo 28500), sin texto ni unidades.",
        )


def normalizar_origen(texto):
    """Lleva el origen escrito por la persona a una de las fuentes de GRI 303-3."""
    clave = _clave(texto)
    if not clave:
        return "sin_clasificar"
    directo = ALIAS_ORIGEN.get(clave.replace("_", " "))
    if directo:
        return directo
    if clave in ORIGENES_GRI303:
        return clave
    return "sin_clasificar"


def normalizar_destino(texto):
    """Lleva el destino de la descarga a una categoria de GRI 303-4."""
    clave = _clave(texto)
    if not clave:
        return "sin_clasificar"
    directo = ALIAS_DESTINO.get(clave.replace("_", " "))
    if directo:
        return directo
    if clave in DESTINOS_GRI303:
        return clave
    return "sin_clasificar"


def normalizar_estres(texto):
    """Devuelve True (si), False (no) o None (no se sabe todavia)."""
    clave = _clave(texto).replace("_", " ")
    if clave in RESPUESTAS_SI:
        return True
    if clave in RESPUESTAS_NO:
        return False
    return None


def normalizar_calidad(texto):
    """verificado, reportado o estimado. Cualquier otra cosa se trata como estimado."""
    clave = _clave(texto)
    if clave in CALIDADES:
        return clave, True
    return "estimado", not clave


def normalizar_agregacion(texto):
    """Agregacion sectorial de AWARE: no_agricola, agricola o no_especificado."""
    clave = _clave(texto)
    if not clave:
        return "no_agricola"
    if clave in AGREGACIONES_AWARE:
        return clave
    elegida = ALIAS_AGREGACION.get(clave.replace("_", " "))
    if elegida:
        return elegida
    raise Problema(
        "No conozco la agregacion de AWARE «%s»." % texto,
        "Usa una de estas tres: no agricola (mineria, industria y servicios), agricola (riego) "
        "o no especificado (cuando no se sabe).",
    )


def _periodo_y_mes(registro):
    """Del texto del periodo saca la etiqueta ('2025-03') y el numero de mes."""
    crudo = str(registro.get("periodo") or registro.get("fecha") or "").strip()
    if not crudo:
        return "", None
    coincidencia = re.match(r"^(\d{4})[-/](\d{1,2})", crudo)
    if coincidencia:
        mes = int(coincidencia.group(2))
        etiqueta = "%s-%02d" % (coincidencia.group(1), mes) if 1 <= mes <= 12 else crudo
        return etiqueta, mes if 1 <= mes <= 12 else None
    coincidencia = re.match(r"^(\d{4})", crudo)
    if coincidencia:
        return coincidencia.group(1), None
    return crudo, None


def a_megalitros(metros_cubicos):
    """GRI 303 pide los volumenes en megalitros: 1 ML = 1.000 m3."""
    return (metros_cubicos or 0.0) / 1000.0


# --------------------------------------------------------------------------
# Catalogo de factores AWARE
# --------------------------------------------------------------------------

def cargar_factores_aware(ruta=None):
    """Lee el catalogo de factores AWARE por pais. Si no existe, devuelve lista vacia."""
    ruta = ruta or ARCHIVO_AWARE
    if not os.path.isfile(ruta):
        return []
    factores = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for numero, fila in enumerate(csv.DictReader(archivo), start=2):
            try:
                valor = float(str(fila.get("factor") or "").replace(",", "."))
            except ValueError:
                continue
            factores.append({
                "pais": (fila.get("pais") or "").strip().upper(),
                "iso3": (fila.get("iso3") or "").strip().upper(),
                "nombre": (fila.get("nombre") or "").strip(),
                "agregacion": _clave(fila.get("agregacion")),
                "periodo": (fila.get("periodo") or "").strip().lower(),
                "factor": valor,
                "version": (fila.get("version") or "").strip(),
                "fuente": (fila.get("fuente") or "").strip(),
                "url": (fila.get("url") or "").strip(),
                "licencia": (fila.get("licencia") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
                "linea": numero,
            })
    return factores


def paises_con_factor(factores=None):
    """Paises para los que hay factor cargado, para poder decirselo a la persona."""
    factores = factores if factores is not None else cargar_factores_aware()
    vistos = {}
    for factor in factores:
        vistos.setdefault(factor["iso3"], factor["nombre"])
    return [{"iso3": iso3, "nombre": nombre} for iso3, nombre in sorted(vistos.items())]


def buscar_factor_aware(pais, agregacion="no_agricola", mes=None, factores=None):
    """Busca el factor AWARE del pais. Devuelve (factor, advertencias).

    El factor de pais es un promedio: AWARE se define por cuenca y por mes. Por eso
    la busqueda siempre devuelve advertencias que hay que mostrarle a la persona.
    Si no hay factor para ese pais, no se inventa nada: se explica donde bajarlo.
    """
    factores = factores if factores is not None else cargar_factores_aware()
    agregacion = normalizar_agregacion(agregacion)
    codigo = str(pais or "").strip().upper()
    if not codigo:
        raise Problema(
            "No se en que pais esta el sitio, asi que no puedo proponerte un factor de escasez.",
            "Dime el pais del sitio o entregame directamente el factor AWARE con --factor. %s"
            % DONDE_CONSEGUIR_AWARE,
        )

    candidatos = [f for f in factores
                  if codigo in (f["pais"], f["iso3"]) and f["agregacion"] == agregacion]
    if not candidatos:
        disponibles = ", ".join("%s (%s)" % (p["nombre"], p["iso3"]) for p in paises_con_factor(factores))
        raise Problema(
            "No tengo el factor AWARE de %s con la agregacion «%s»." % (codigo, agregacion),
            "No voy a inventarlo. Bajalo tu y pasamelo con --factor. %s%s"
            % (DONDE_CONSEGUIR_AWARE,
               (" Paises que si tengo cargados: %s." % disponibles) if disponibles else ""),
            {"pais": codigo, "agregacion": agregacion},
        )

    advertencias = []
    elegido = None
    if mes:
        mes = int(mes)
        mensuales = [f for f in candidatos if f["periodo"] == "%02d" % mes]
        if mensuales:
            elegido = mensuales[0]
        else:
            advertencias.append(
                "No tengo el factor de %s para %s con la agregacion «%s»: use el factor anual."
                % (candidatos[0]["nombre"], MESES.get(mes, "ese mes"), agregacion))
    if elegido is None:
        anuales = [f for f in candidatos if f["periodo"] == "anual"]
        if not anuales:
            raise Problema(
                "Tengo factores mensuales de %s pero no el anual." % codigo,
                "Dime el mes del consumo o entregame el factor con --factor.",
            )
        elegido = anuales[0]

    advertencias.append(
        "El factor %s de %s es un promedio nacional. AWARE se define por cuenca: para un sitio "
        "concreto el valor de su cuenca puede ser muy distinto. Si el dato se va a publicar, usa el "
        "factor de la cuenca del sitio." % (elegido["version"] or VERSION_AWARE, elegido["nombre"]))
    if not mes and elegido["periodo"] == "anual":
        advertencias.append(
            "Use el factor anual. Si la empresa usa mucha mas agua en unos meses que en otros, el "
            "calculo mes a mes puede dar un resultado muy distinto: indicame el mes con --mes.")
    if agregacion == "no_especificado":
        advertencias.append(
            "Estas usando la agregacion «no especificado», que es la mas gruesa de las tres. "
            "Si sabes si el agua va a riego o a procesos industriales, dimelo y uso la agregacion "
            "que corresponde.")
    return elegido, advertencias


# --------------------------------------------------------------------------
# Contabilidad del agua (GRI 303)
# --------------------------------------------------------------------------

def _vacio():
    return {"extraccion_m3": 0.0, "descarga_m3": 0.0, "consumo_m3": 0.0, "registros": 0}


def _sumar(destino, clave, linea):
    casilla = destino.setdefault(clave, _vacio())
    casilla["extraccion_m3"] += linea["extraccion_m3"]
    casilla["descarga_m3"] += linea["descarga_m3"]
    casilla["consumo_m3"] += linea["consumo_m3"]
    casilla["registros"] += 1
    return casilla


def _porcentaje(parte, total):
    return (parte / total * 100.0) if total else 0.0


def preparar_fila(registro):
    """Revisa y normaliza una fila de la planilla de agua.

    Devuelve el detalle de la fila: extraccion, descarga, consumo (GRI 303-5),
    origen y destino clasificados, zona de estres y calidad del dato.
    """
    fila = registro.get("_fila", "?")
    extraccion = _numero(registro.get("extraccion_m3"), "Extraccion (m3)", fila)
    descarga = _numero(registro.get("descarga_m3"), "Descarga (m3)", fila)

    if extraccion is None and descarga is None:
        raise Problema(
            "La fila %s no tiene ni extraccion ni descarga." % fila,
            "Escribe cuantos metros cubicos entraron y cuantos salieron en ese periodo, o borra la "
            "fila si no aplica.",
        )
    advertencias = []
    if extraccion is None:
        extraccion = 0.0
        advertencias.append(
            "En la fila %s no habia extraccion: la tome como 0. Si esa agua vino de otro sitio de la "
            "empresa, anotalo en Notas para que se entienda el balance." % fila)
    if descarga is None:
        descarga = 0.0
        advertencias.append(
            "En la fila %s no habia descarga: la tome como 0, es decir, toda el agua se consumio. "
            "Si en realidad devuelven agua y no la miden, dejalo dicho en Notas." % fila)

    for nombre, valor in (("Extraccion (m3)", extraccion), ("Descarga (m3)", descarga)):
        if valor < 0:
            raise Problema(
                "En la fila %s la columna «%s» tiene un numero negativo (%s)." % (fila, nombre, valor),
                "Los volumenes de agua siempre son positivos. Revisa el dato en la planilla.",
            )

    if descarga > extraccion:
        raise Problema(
            "En la fila %s se descargan mas metros cubicos (%s) de los que se extraen (%s)."
            % (fila, descarga, extraccion),
            "Eso deja un consumo negativo, que no existe. Suele pasar cuando la descarga incluye agua "
            "de lluvia, agua de otro sitio o agua guardada de un periodo anterior. Revisa el dato o "
            "separa esa agua en su propia fila con su origen.",
        )

    periodo, mes = _periodo_y_mes(registro)
    origen_texto = str(registro.get("origen") or "").strip()
    destino_texto = str(registro.get("destino_de_la_descarga") or registro.get("destino") or "").strip()
    origen = normalizar_origen(origen_texto)
    destino = normalizar_destino(destino_texto)
    if origen == "sin_clasificar" and extraccion > 0:
        advertencias.append(
            "En la fila %s no pude clasificar el origen «%s» en las cinco fuentes que pide GRI 303-3 "
            "(superficial, subterranea, de mar, producida o de terceros). Quedo como «sin clasificar»: "
            "dime de donde sale esa agua y la ubico." % (fila, origen_texto or "(vacio)"))
    if destino == "sin_clasificar" and descarga > 0:
        advertencias.append(
            "En la fila %s no pude clasificar el destino «%s» de la descarga. Quedo como «sin "
            "clasificar»: GRI 303-4 pide decir a donde va el agua."
            % (fila, destino_texto or "(vacio)"))

    estres = normalizar_estres(registro.get("zona_de_estres_hidrico"))
    if estres is None:
        advertencias.append(
            "En la fila %s no esta definido si el sitio esta en zona de estres hidrico. Es la mitad de "
            "lo que pide GRI 303: escribe «si» o «no» en esa columna. Si no lo sabes, se puede mirar en "
            "WRI Aqueduct o en el WWF Water Risk Filter." % fila)

    calidad, reconocida = normalizar_calidad(registro.get("calidad_del_dato") or registro.get("calidad"))
    if not reconocida:
        advertencias.append(
            "En la fila %s no reconoci la calidad del dato «%s»: la trate como estimada. Las opciones "
            "son verificado, reportado o estimado."
            % (fila, registro.get("calidad_del_dato") or registro.get("calidad")))

    return {
        "fila": fila,
        "periodo": periodo,
        "mes": mes,
        "sitio": str(registro.get("sitio") or "").strip() or "Sin sitio asignado",
        "origen": origen,
        "origen_nombre": ORIGENES_GRI303[origen],
        "origen_original": origen_texto,
        "destino": destino,
        "destino_nombre": DESTINOS_GRI303[destino],
        "destino_original": destino_texto,
        "extraccion_m3": extraccion,
        "descarga_m3": descarga,
        "consumo_m3": extraccion - descarga,
        "zona_estres_hidrico": estres,
        "calidad_dato": calidad,
        "notas": str(registro.get("notas") or "").strip(),
        "advertencias": advertencias,
    }


def calcular(filas, periodo=None):
    """Contabilidad de agua del periodo, segun las definiciones de GRI 303.

    Suma extraccion, descarga y consumo (extraccion - descarga, GRI 303-5) en
    total, por sitio y por origen, y separa lo que ocurre en zonas con estres
    hidrico, que es el desglose que piden 303-3-b, 303-4-b y 303-5-b.

    Las filas que no se pueden calcular no se descartan en silencio: quedan
    listadas en «problemas», con la fila exacta y que hacer.
    """
    detalle, problemas, advertencias = [], [], []

    consideradas = list(filas or [])
    if periodo:
        buscado = str(periodo).strip()
        consideradas = [f for f in consideradas
                        if str(f.get("periodo") or "").strip().startswith(buscado)]
        if not consideradas and filas:
            raise Problema(
                "No hay filas del periodo %s en la planilla de agua." % buscado,
                "Revisa la columna «Periodo»: debe decir el año (2025) o el mes (2025-03).",
            )

    for registro in consideradas:
        try:
            linea = preparar_fila(registro)
        except Problema as problema:
            problemas.append({
                "fila": registro.get("_fila"),
                "error": problema.mensaje,
                "sugerencia": problema.sugerencia,
            })
            continue
        detalle.append(linea)
        advertencias.extend(linea["advertencias"])

    por_sitio, por_origen, por_destino, por_periodo = {}, {}, {}, {}
    estres = {
        "extraccion_m3": {"si": 0.0, "no": 0.0, "sin_definir": 0.0},
        "descarga_m3": {"si": 0.0, "no": 0.0, "sin_definir": 0.0},
        "consumo_m3": {"si": 0.0, "no": 0.0, "sin_definir": 0.0},
    }
    calidad_m3 = {"estimado": 0.0, "reportado": 0.0, "verificado": 0.0}
    calidad_registros = {"estimado": 0, "reportado": 0, "verificado": 0}
    totales = _vacio()
    estres_por_sitio = {}

    for linea in detalle:
        totales["extraccion_m3"] += linea["extraccion_m3"]
        totales["descarga_m3"] += linea["descarga_m3"]
        totales["consumo_m3"] += linea["consumo_m3"]
        totales["registros"] += 1

        casilla = _sumar(por_sitio, linea["sitio"], linea)
        casilla.setdefault("zonas_estres", set()).add(linea["zona_estres_hidrico"])
        _sumar(por_origen, linea["origen"], linea)
        if linea["descarga_m3"]:
            _sumar(por_destino, linea["destino"], linea)
        _sumar(por_periodo, linea["periodo"] or "sin periodo", linea)

        etiqueta = {True: "si", False: "no", None: "sin_definir"}[linea["zona_estres_hidrico"]]
        for campo in ("extraccion_m3", "descarga_m3", "consumo_m3"):
            estres[campo][etiqueta] += linea[campo]
        estres_por_sitio.setdefault(linea["sitio"], set()).add(linea["zona_estres_hidrico"])

        calidad_m3[linea["calidad_dato"]] += linea["extraccion_m3"]
        calidad_registros[linea["calidad_dato"]] += 1

    for sitio, casilla in por_sitio.items():
        marcas = casilla.pop("zonas_estres", set())
        if marcas == {True}:
            casilla["zona_estres_hidrico"] = "si"
        elif marcas == {False}:
            casilla["zona_estres_hidrico"] = "no"
        elif True in marcas:
            casilla["zona_estres_hidrico"] = "si (hay filas del sitio sin definir)"
        else:
            casilla["zona_estres_hidrico"] = "sin definir"
        casilla["nombre"] = sitio

    for clave, casilla in por_origen.items():
        casilla["nombre"] = ORIGENES_GRI303.get(clave, clave)
    for clave, casilla in por_destino.items():
        casilla["nombre"] = DESTINOS_GRI303.get(clave, clave)

    if problemas:
        advertencias.append(
            "%d fila(s) de la planilla de agua no se pudieron calcular y quedaron fuera de los totales: "
            "revisa la lista de problemas." % len(problemas))
    if totales["descarga_m3"] == 0 and totales["extraccion_m3"] > 0:
        advertencias.append(
            "No hay ninguna descarga registrada, asi que el calculo da que se consume toda el agua que "
            "se extrae. Si la empresa devuelve agua al alcantarillado o a un cauce, ese volumen falta.")
    if estres["extraccion_m3"]["sin_definir"] > 0:
        advertencias.append(
            "El %s%% de la extraccion esta en sitios donde no se definio si hay estres hidrico. GRI 303 "
            "pide ese desglose: sin el, el reporte queda incompleto."
            % round(_porcentaje(estres["extraccion_m3"]["sin_definir"], totales["extraccion_m3"]), 1))
    advertencias.append(FORMULAS["consumo"]["advertencia"])

    sin_clasificar = por_origen.get("sin_clasificar", {}).get("extraccion_m3", 0.0)
    if sin_clasificar:
        advertencias.append(
            "Hay %s m3 de extraccion cuyo origen no calza con las cinco fuentes de GRI 303-3. "
            "Mientras sigan asi, la divulgacion 303-3 queda incompleta." % round(sin_clasificar, 2))

    return {
        "periodo": str(periodo) if periodo else "todos los periodos cargados",
        "extraccion_m3": totales["extraccion_m3"],
        "descarga_m3": totales["descarga_m3"],
        "consumo_m3": totales["consumo_m3"],
        "extraccion_megalitros": a_megalitros(totales["extraccion_m3"]),
        "descarga_megalitros": a_megalitros(totales["descarga_m3"]),
        "consumo_megalitros": a_megalitros(totales["consumo_m3"]),
        "registros_calculados": len(detalle),
        "registros_con_problema": len(problemas),
        "por_sitio": por_sitio,
        "por_origen": por_origen,
        "por_destino": por_destino,
        "por_periodo": por_periodo,
        "zonas_estres_hidrico": {
            "metros_cubicos": estres,
            "porcentaje": {
                "extraccion": {k: _porcentaje(v, totales["extraccion_m3"])
                               for k, v in estres["extraccion_m3"].items()},
                "descarga": {k: _porcentaje(v, totales["descarga_m3"])
                             for k, v in estres["descarga_m3"].items()},
                "consumo": {k: _porcentaje(v, totales["consumo_m3"])
                            for k, v in estres["consumo_m3"].items()},
            },
            "sitios_en_estres": sorted(s for s, marcas in estres_por_sitio.items() if True in marcas),
            "sitios_sin_definir": sorted(s for s, marcas in estres_por_sitio.items()
                                         if marcas == {None}),
            "como_se_determina": (
                "Lo marca la persona en la planilla. GRI 303 reconoce como herramientas publicas el WRI "
                "Aqueduct Water Risk Atlas y el WWF Water Risk Filter, y considera zona con estres "
                "hidrico aquella con estres hidrico de referencia alto (40-80%) o extremadamente alto "
                "(mas de 80%). El estandar tambien permite marcarla por problemas de calidad o de "
                "acceso al agua, dejando anotada la razon."),
        },
        "calidad_datos": {
            "metros_cubicos_extraidos": calidad_m3,
            "porcentaje": {k: _porcentaje(v, totales["extraccion_m3"]) for k, v in calidad_m3.items()},
            "registros": calidad_registros,
        },
        "desglose_agua_dulce_y_otras": {
            "disponible": False,
            "que_pide_el_estandar": (
                "GRI 303-3 y 303-4 piden separar agua dulce (hasta 1.000 mg/L de solidos disueltos "
                "totales) de otras aguas (mas de 1.000 mg/L)."),
            "por_que_falta": (
                "La planilla de agua no tiene una columna de salinidad o de solidos disueltos totales, "
                "y no se puede deducir del origen sin un analisis."),
            "que_hacer": (
                "Si la empresa reporta con GRI, pide el analisis de calidad del agua de cada fuente "
                "(o el informe del laboratorio) y anota el desglose a mano en el reporte."),
        },
        "formulas": FORMULAS,
        "detalle": detalle,
        "problemas": problemas,
        "advertencias": sorted(set(a for a in advertencias if a)),
        "fuentes": [FUENTE_GRI303],
        "calculado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }


# --------------------------------------------------------------------------
# Huella de escasez hidrica (ISO 14046 + AWARE)
# --------------------------------------------------------------------------

def huella_de_escasez(consumo_m3, factor_aware, factor_mundial=None):
    """Huella de escasez hidrica ponderada por donde ocurre el consumo.

        Huella [m3 mundo-eq] = Consumo [m3] x CF_AWARE [adimensional]

    Unidades:
      - consumo_m3: metros cubicos consumidos en el periodo (definicion de
        GRI 303-5). No se usa la extraccion: el agua que se devuelve al mismo
        lugar en condiciones de uso no genera escasez.
      - factor_aware: factor de caracterizacion AWARE, adimensional, que se
        interpreta como m3 mundo-eq por cada m3 consumido. Va de 0,1 a 100
        (AWARE trunca en esos dos extremos) y vale 1 en el promedio mundial de
        referencia del metodo.
      - resultado: metros cubicos equivalentes mundiales (m3 mundo-eq).

    factor_mundial es opcional: si se entrega el factor de la region GLO de la
    misma agregacion, se agrega la comparacion «cuantas veces mas impacto que
    en un lugar promedio del mundo».

    Metodo AWARE (WULCA), aplicado dentro del marco de ISO 14046:2014.
    """
    if consumo_m3 in (None, ""):
        raise Problema(
            "No me dijiste cuanta agua se consumio, asi que no puedo calcular la huella de escasez.",
            "Primero calcula el consumo con: agua calcular. O dime los metros cubicos con --consumo.",
        )
    try:
        consumo = float(str(consumo_m3).replace(",", "."))
    except (TypeError, ValueError):
        raise Problema(
            "El consumo «%s» no es un numero." % consumo_m3,
            "Escribe solo los metros cubicos consumidos, por ejemplo 1200000.",
        )
    if consumo < 0:
        raise Problema(
            "El consumo de agua no puede ser negativo (me llego %s m3)." % consumo,
            "Revisa la planilla: si la descarga es mayor que la extraccion, hay un dato mal anotado.",
        )

    if factor_aware in (None, ""):
        raise Problema(
            "Falta el factor de escasez AWARE del lugar donde se consume el agua.",
            "Sin ese factor la huella de escasez no se puede calcular y no voy a inventarlo. %s "
            "Cuando lo tengas, pasamelo con --factor." % DONDE_CONSEGUIR_AWARE,
        )
    try:
        factor = float(str(factor_aware).replace(",", "."))
    except (TypeError, ValueError):
        raise Problema(
            "El factor AWARE «%s» no es un numero." % factor_aware,
            "Es un numero entre 0,1 y 100, por ejemplo 45,5. %s" % DONDE_CONSEGUIR_AWARE,
        )
    if factor < FACTOR_MINIMO or factor > FACTOR_MAXIMO:
        raise Problema(
            "El factor AWARE %s esta fuera del rango del metodo (%s a %s)."
            % (factor, FACTOR_MINIMO, FACTOR_MAXIMO),
            "AWARE corta los valores en 0,1 y 100, asi que un numero fuera de ese rango no es un factor "
            "AWARE. Revisa de donde lo sacaste. %s" % DONDE_CONSEGUIR_AWARE,
        )

    huella = consumo * factor
    resultado = {
        "consumo_m3": consumo,
        "factor_aware": factor,
        "huella_m3_mundo_eq": huella,
        "unidad": "m3 mundo-eq (metros cubicos equivalentes mundiales)",
        "formula": FORMULAS["huella_de_escasez"]["formula"],
        "unidades_de_la_formula": FORMULAS["huella_de_escasez"]["unidades"],
        "metodo": ("Metodo AWARE (Available WAter REmaining) de WULCA, aplicado dentro del marco de "
                   "ISO 14046:2014. Version de los factores: %s." % VERSION_AWARE),
        "que_significa": (
            "Consumir 1 m3 en ese lugar afecta la disponibilidad de agua tanto como consumir %s m3 en "
            "el lugar de referencia del metodo." % round(factor, 3)),
        "fuentes": [FUENTE_ISO14046, FUENTE_AWARE_METODO],
    }

    if factor_mundial not in (None, ""):
        try:
            mundial = float(str(factor_mundial).replace(",", "."))
        except (TypeError, ValueError):
            raise Problema(
                "El factor mundial de comparacion «%s» no es un numero." % factor_mundial,
                "Usa el factor de la region GLO de la misma agregacion, o no lo entregues.",
            )
        if mundial <= 0:
            raise Problema(
                "El factor mundial de comparacion tiene que ser mayor que cero.",
                "Usa el factor de la region GLO de la misma agregacion de AWARE.",
            )
        resultado["comparacion_con_el_promedio_mundial"] = {
            "factor_mundial": mundial,
            "huella_m3_mundo_eq": consumo * mundial,
            "veces_el_promedio_mundial": factor / mundial,
            "en_palabras": (
                "El mismo consumo en un lugar promedio del mundo daria una huella %s veces menor."
                % round(factor / mundial, 2)) if factor >= mundial else (
                "El mismo consumo en un lugar promedio del mundo daria una huella %s veces mayor."
                % round(mundial / factor, 2)),
        }
    return resultado


# --------------------------------------------------------------------------
# Indicadores del estandar de reporte (GRI 303-3, 303-4 y 303-5)
# --------------------------------------------------------------------------

def _redondear(valor, decimales=3):
    return round(float(valor or 0.0), decimales)


def indicadores_gri303(resumen):
    """Arma los datos de las divulgaciones 303-3, 303-4 y 303-5 de GRI 303.

    Las tres son metricas cuantitativas y se reportan en MEGALITROS. Lo que
    pide cada una esta descrito con palabras propias; el texto del estandar no
    se reproduce.

    Cada divulgacion trae tres partes: «que_pide», «lo_que_tengo» y
    «lo_que_falta», para que la persona vea de inmediato que puede publicar y
    que tiene que salir a buscar.
    """
    if not isinstance(resumen, dict):
        raise Problema(
            "Para armar los indicadores de GRI 303 necesito el resultado de un calculo de agua.",
            "Primero ejecuta: agua calcular. Despues armo los indicadores con ese resultado.",
        )

    por_origen = resumen.get("por_origen") or {}
    por_destino = resumen.get("por_destino") or {}
    estres = (resumen.get("zonas_estres_hidrico") or {}).get("metros_cubicos") or {}
    estres_extraccion = estres.get("extraccion_m3") or {}
    estres_descarga = estres.get("descarga_m3") or {}
    estres_consumo = estres.get("consumo_m3") or {}

    falta_dulce = ("Separar agua dulce (hasta 1.000 mg/L de solidos disueltos totales) de otras aguas "
                   "(mas de 1.000 mg/L). La planilla no trae ese dato.")
    falta_estres = None
    if estres_extraccion.get("sin_definir"):
        falta_estres = ("Definir si cada sitio esta en zona de estres hidrico: quedan %s m3 de "
                        "extraccion sin esa marca." % _redondear(estres_extraccion.get("sin_definir")))

    sin_clasificar_origen = por_origen.get("sin_clasificar", {}).get("extraccion_m3", 0.0)
    sin_clasificar_destino = por_destino.get("sin_clasificar", {}).get("descarga_m3", 0.0)

    faltantes_303_3 = [falta_dulce]
    if falta_estres:
        faltantes_303_3.append(falta_estres)
    if sin_clasificar_origen:
        faltantes_303_3.append(
            "Clasificar el origen de %s m3 que no calzan con las cinco fuentes del estandar."
            % _redondear(sin_clasificar_origen))

    faltantes_303_4 = [
        falta_dulce,
        ("Declarar si se descargan sustancias prioritarias de preocupacion y, si las hay, cuales son, "
         "como se fijaron sus limites y cuanto se descargo. Ese dato viene del monitoreo de la "
         "descarga, no de esta planilla."),
    ]
    if sin_clasificar_destino:
        faltantes_303_4.append(
            "Indicar a donde va la descarga de %s m3 que quedaron sin clasificar."
            % _redondear(sin_clasificar_destino))
    if estres_descarga.get("sin_definir"):
        faltantes_303_4.append(
            "Definir la zona de estres hidrico de %s m3 de descarga."
            % _redondear(estres_descarga.get("sin_definir")))

    faltantes_303_5 = [
        ("Revisar si hubo agua almacenada de un periodo a otro o agua devuelta tan contaminada que "
         "nadie mas puede usarla: GRI 303-5 las cuenta como consumo y la resta extraccion menos "
         "descarga no las incluye."),
        ("Declarar si los cambios en el almacenamiento de agua son un impacto significativo y, en ese "
         "caso, cuanto cambiaron."),
    ]
    if estres_consumo.get("sin_definir"):
        faltantes_303_5.append(
            "Definir la zona de estres hidrico de %s m3 de consumo."
            % _redondear(estres_consumo.get("sin_definir")))

    return {
        "estandar": FUENTE_GRI303,
        "vigencia": "Obligatorio para reportes publicados desde el 1 de enero de 2021.",
        "unidad": "megalitros (ML). 1 ML = 1.000 m3",
        "periodo": resumen.get("periodo"),
        "303-3": {
            "titulo": "303-3 Extraccion de agua",
            "que_pide": ("Cuanta agua tomo la organizacion de todas las fuentes durante el periodo, "
                         "sea cual sea el uso que le dio, desglosada por tipo de fuente (superficial, "
                         "subterranea, de mar, producida y de terceros), mas el mismo desglose "
                         "referido solo a las zonas con estres hidrico, separando en ambos casos el "
                         "agua dulce de las otras aguas."),
            "total_megalitros": _redondear(resumen.get("extraccion_megalitros")),
            "por_fuente_megalitros": {
                clave: {"nombre": datos.get("nombre", clave),
                        "megalitros": _redondear(a_megalitros(datos.get("extraccion_m3")))}
                for clave, datos in sorted(por_origen.items()) if datos.get("extraccion_m3")
            },
            "en_zonas_con_estres_hidrico_megalitros": _redondear(a_megalitros(estres_extraccion.get("si"))),
            "fuera_de_zonas_con_estres_hidrico_megalitros": _redondear(a_megalitros(estres_extraccion.get("no"))),
            "sin_definir_megalitros": _redondear(a_megalitros(estres_extraccion.get("sin_definir"))),
            "agua_dulce_y_otras_aguas": "no disponible",
            "lo_que_falta": faltantes_303_3,
        },
        "303-4": {
            "titulo": "303-4 Descarga de agua",
            "que_pide": ("Cuanta agua devolvio la organizacion durante el periodo y a donde fue, "
                         "separando agua dulce de otras aguas, indicando cuanto se descargo en zonas "
                         "con estres hidrico y declarando las sustancias prioritarias de preocupacion "
                         "que contienen esas descargas."),
            "total_megalitros": _redondear(resumen.get("descarga_megalitros")),
            "por_destino_megalitros": {
                clave: {"nombre": datos.get("nombre", clave),
                        "megalitros": _redondear(a_megalitros(datos.get("descarga_m3")))}
                for clave, datos in sorted(por_destino.items()) if datos.get("descarga_m3")
            },
            "en_zonas_con_estres_hidrico_megalitros": _redondear(a_megalitros(estres_descarga.get("si"))),
            "fuera_de_zonas_con_estres_hidrico_megalitros": _redondear(a_megalitros(estres_descarga.get("no"))),
            "sin_definir_megalitros": _redondear(a_megalitros(estres_descarga.get("sin_definir"))),
            "agua_dulce_y_otras_aguas": "no disponible",
            "sustancias_prioritarias_de_preocupacion": "no disponible",
            "lo_que_falta": faltantes_303_4,
        },
        "303-5": {
            "titulo": "303-5 Consumo de agua",
            "que_pide": ("Cuanta de esa agua se quedo, es decir, no volvio a la superficie, al "
                         "subsuelo, al mar ni a un tercero, cuanto de ese consumo ocurrio en zonas con "
                         "estres hidrico, y si los cambios en el agua almacenada son un impacto "
                         "significativo."),
            "total_megalitros": _redondear(resumen.get("consumo_megalitros")),
            "en_zonas_con_estres_hidrico_megalitros": _redondear(a_megalitros(estres_consumo.get("si"))),
            "fuera_de_zonas_con_estres_hidrico_megalitros": _redondear(a_megalitros(estres_consumo.get("no"))),
            "sin_definir_megalitros": _redondear(a_megalitros(estres_consumo.get("sin_definir"))),
            "metodo_de_calculo": FORMULAS["consumo"]["formula"],
            "cambio_en_el_almacenamiento": "no disponible",
            "lo_que_falta": faltantes_303_5,
        },
        "divulgaciones_de_gestion_que_no_son_numeros": [
            ("303-1 Interaccion con el agua como recurso compartido: contar de donde saca el agua la "
             "empresa, que impactos genera, como los aborda (tambien los de su cadena de valor) y como "
             "se hace cargo del contexto local de cada zona con estres hidrico."),
            ("303-2 Gestion de los impactos de la descarga: decir que estandares minimos de calidad "
             "cumple el agua que devuelve, como se fijaron esos estandares y como se considera la "
             "calidad del cuerpo de agua que la recibe."),
        ],
        "fuentes": [FUENTE_GRI303],
    }
