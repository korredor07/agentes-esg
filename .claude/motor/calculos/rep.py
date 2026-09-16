# -*- coding: utf-8 -*-
"""Ley REP (Ley 20.920 de Chile): metas por producto prioritario y cumplimiento.

La Ley 20.920, publicada el 01-06-2016, obliga al productor -y el importador es
productor- a organizar y financiar la recoleccion y valorizacion de los residuos
de seis productos prioritarios (art. 10). Cada producto tiene su propio decreto
de metas y CADA DECRETO USA UNA FORMULA DISTINTA: no son intercambiables.

Formulas implementadas, con el articulo de donde salen:

F1. Envases domiciliarios - art. 22 del DS 12/2020 MMA

        PDi = (EDGi * 100) / EDTIMi-1

    EDGi: toneladas de la subcategoria recolectadas Y valorizadas en el anio i.
    EDTIMi-1: toneladas de esa subcategoria introducidas en el mercado el anio
    anterior (en un sistema colectivo, la suma de todos sus integrantes).

F2. Envases no domiciliarios - art. 25 del DS 12/2020 MMA

        PNDi = 100 * (ENDGi + ENDCIi) / ENDTIMi-1

    ENDCIi son las toneladas valorizadas por consumidores industriales que se
    imputan al sistema (art. 24 letra b). Si la empresa las tiene certificadas,
    se suman a las toneladas valorizadas de la planilla.

F3. Prorrateo del primer anio de metas - art. 1 transitorio del DS 12/2020 y
    art. 1 transitorio del DS 22/2025

        M1 = (Mi * MO) / 12

    MO son los meses entre el primer dia del mes siguiente a la entrada en
    vigencia y enero del anio siguiente.
    Envases: las metas rigen desde el 16-09-2023, MO = 3, luego M1 = Mi * 0,25.
    Pilas y AEE: rigen desde el 07-05-2028, MO = 7, luego M1 = Mi * 7/12.
    NO aplica a aceites lubricantes: sus metas rigen desde el 1 de enero.
    NO aplica a neumaticos: el DS 8/2019 fija las metas por anio calendario de
    vigencia del titulo, sin regla de prorrateo.

F4. Neumaticos - art. 24 del DS 8/2019 MMA

        Pi = (NGi * 100) / (NCi-1 * FD)

    FD es el factor de desgaste por uso: 0,84 en categoria A y 0,75 en
    categoria B. Olvidar FD es el error mas frecuente: hace ver como
    incumplimiento algo que si cumple.

F5. Aceites lubricantes - art. 23 del DS 47/2023 MMA

        PCi = ((AGi + ACONSINDi) * 100) / (ACi-1 * (1 - TP))

    TP es la tasa de perdida del aceite durante su uso: 0,3 (considerando 16).

F6. Pilas y AEE, meta general - art. 22 del DS 22/2025 MMA

        PGi = 100 * (RGi + RCIi) / TIM_Prom3anios

    El denominador NO es el anio anterior: es el promedio de los tres anios
    inmediatamente anteriores (la suma de los tres dividida por 3).

F7. Pilas y AEE, meta especifica de aparatos de intercambio de temperatura -
    art. 24 del DS 22/2025: misma estructura que F6, calculada solo con
    residuos y toneladas de AIT.

F8. Pilas y AEE, meta especifica de paneles fotovoltaicos - art. 26 del
    DS 22/2025: misma estructura que F6, solo con residuos de PFV.

Lo que este motor NO calcula, porque la investigacion normativa no lo pudo
verificar, y que el modulo le dice al usuario en vez de inventarlo:

- La tabla de metas del art. 21 del DS 47/2023 (aceites lubricantes) esta
  publicada como imagen en el Diario Oficial N 43.995 y no se pudo transcribir.
  El motor aplica igual la formula F5 y muestra el porcentaje logrado, pero no
  dice si se cumple: no hay porcentaje oficial con el cual compararlo.
- Baterias es producto prioritario (art. 10 letra c) pero no tiene decreto de
  metas publicado. Solo corre la obligacion de declarar las toneladas puestas
  en el mercado (art. 2 transitorio de la Ley 20.920).
- No hay fecha reglamentaria fija para la declaracion anual del productor: el
  MMA la abre por convocatoria (en 2026, anunciada para el ultimo trimestre).
- Las metas regionales de recoleccion de neumaticos (art. 20 letra A), los
  puntos limpios (art. 35 del DS 12/2020) y la recoleccion puerta a puerta
  (art. 36) recaen en los sistemas de gestion colectivos, no en el productor
  individual: no se calculan aqui.
"""

import csv
import datetime
import os
import re
import unicodedata

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_METAS = os.path.join(CARPETA_DATOS, "rep_metas.csv")

LEY = "Ley 20.920, publicada el 01-06-2016"
VENTANILLA_UNICA = "https://portalvu.mma.gob.cl/"

# Factores del denominador que trae cada decreto.
FACTOR_DESGASTE_NEUMATICOS = {"a": 0.84, "b": 0.75}   # FD, art. 24 del DS 8/2019
TASA_PERDIDA_ACEITES = 0.3                            # TP, art. 23 del DS 47/2023

ESTADOS = ["cumple", "no cumple", "sin meta", "sin meta verificada", "sin datos"]


def _clave(texto):
    """Convierte 'Papel y carton ' en 'papel_y_carton'."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


# --------------------------------------------------------------------------
# Los seis productos prioritarios del art. 10 de la Ley 20.920
# --------------------------------------------------------------------------

PRODUCTOS = {
    "aceites_lubricantes": {
        "nombre": "Aceites lubricantes",
        "letra": "a)",
        "decreto": "DS 47/2023 MMA",
        "publicacion_decreto": "11-11-2024",
        "metas_desde": "01-01-2027",
        "primer_anio_metas": 2027,
        "prorrateo_meses": None,
        "nota_prorrateo": ("No se prorratea el primer anio: las metas rigen desde el 1 de enero "
                           "(art. 1 transitorio del DS 47/2023)."),
        "anios_base": 1,
        "formula": "PCi = ((AGi + ACONSINDi) * 100) / (ACi-1 * (1 - TP))",
        "articulo_formula": "Art. 23 del DS 47/2023",
        "tabla": None,
        "motivo_sin_tabla": ("La tabla de metas del art. 21 del DS 47/2023 esta publicada como imagen en el "
                             "Diario Oficial N 43.995 y no se pudo transcribir con certeza, asi que no la "
                             "tengo cargada. No voy a inventar porcentajes."),
        "que_hacer_sin_tabla": ("Puedo calcular las toneladas base y el porcentaje que estas logrando, pero el "
                                "porcentaje exigido hay que pedirselo al Ministerio del Medio Ambiente o al "
                                "sistema de gestion al que adhieras."),
        "categorias": {},
        "materiales": {},
        "exige_categoria": False,
        "exige_material": False,
        "unidad_umbral": "litros",
        "exenciones": [
            "Quedan fuera de la REP los productores que introduzcan 66 litros o menos de aceites "
            "lubricantes al anio (art. 5 del DS 47/2023).",
            "Los aceites de dos tiempos y de cadenillas no estan sujetos a metas (art. 4 del DS 47/2023).",
        ],
        "valorizacion": ("Las metas de recoleccion de los aceites lubricantes usados se entienden cumplidas "
                         "al momento de su valorizacion (art. 21 del DS 47/2023)."),
    },
    "aee": {
        "nombre": "Aparatos electricos y electronicos (AEE)",
        "letra": "b)",
        "decreto": "DS 22/2025 MMA",
        "publicacion_decreto": "07-05-2026",
        "metas_desde": "07-05-2028",
        "primer_anio_metas": 2028,
        "prorrateo_meses": 7,
        "nota_prorrateo": ("El primer anio de metas (2028) se prorratea: M1 = (Mi x 7)/12, segun el art. 1 "
                           "transitorio del DS 22/2025."),
        "anios_base": 3,
        "formula": "PGi = 100 * (RGi + RCIi) / TIM_Prom3anios",
        "articulo_formula": "Arts. 22, 24 y 26 del DS 22/2025",
        "tabla": "pilas_y_aee",
        "motivo_sin_tabla": "",
        "que_hacer_sin_tabla": "",
        "categorias": {
            "general": "Otros aparatos electricos y electronicos (meta general del art. 21)",
            "ait": "Aparatos de intercambio de temperatura (AIT)",
            "pfv": "Paneles fotovoltaicos (PFV)",
        },
        "materiales": {},
        "exige_categoria": False,
        "exige_material": False,
        "unidad_umbral": "",
        "exenciones": [
            "No estan sujetos a metas los productores que califiquen como microempresa segun la "
            "Ley 20.416 (art. 6 del DS 22/2025), pero igual deben informar (art. 9).",
            "El DS 22/2025 no fija un umbral en kilos ni en unidades, a diferencia de envases y aceites.",
        ],
        "valorizacion": ("Las metas se cumplen con preparacion para la reutilizacion y reciclaje material "
                         "(art. 27). Solo las metas de paneles fotovoltaicos admiten cualquier operacion de "
                         "valorizacion. Solo cuentan residuos recolectados y valorizados en Chile por gestor "
                         "autorizado y registrado (art. 28)."),
    },
    "baterias": {
        "nombre": "Baterias",
        "letra": "c)",
        "decreto": "",
        "publicacion_decreto": "",
        "metas_desde": "",
        "primer_anio_metas": None,
        "prorrateo_meses": None,
        "nota_prorrateo": "",
        "anios_base": 1,
        "formula": "",
        "articulo_formula": "",
        "tabla": None,
        "motivo_sin_tabla": ("Las baterias son producto prioritario (art. 10 letra c de la Ley 20.920), pero "
                             "todavia no hay decreto de metas publicado, asi que no existen porcentajes que "
                             "cumplir."),
        "que_hacer_sin_tabla": ("Mientras no rija un decreto de metas, el productor debe declarar cada anio las "
                                "toneladas de baterias puestas en el mercado (art. 2 transitorio de la "
                                "Ley 20.920), a traves de la Ventanilla Unica del RETC."),
        "categorias": {},
        "materiales": {},
        "exige_categoria": False,
        "exige_material": False,
        "unidad_umbral": "",
        "exenciones": [],
        "valorizacion": "",
    },
    "envases": {
        "nombre": "Envases y embalajes",
        "letra": "d)",
        "decreto": "DS 12/2020 MMA",
        "publicacion_decreto": "16-03-2021",
        "metas_desde": "16-09-2023",
        "primer_anio_metas": 2023,
        "prorrateo_meses": 3,
        "nota_prorrateo": ("El primer anio de metas (2023) se prorratea: M1 = (Mi x 3)/12, segun el art. 1 "
                           "transitorio del DS 12/2020."),
        "anios_base": 1,
        "formula": "PDi = (EDGi * 100) / EDTIMi-1  |  PNDi = 100 * (ENDGi + ENDCIi) / ENDTIMi-1",
        "articulo_formula": "Arts. 22 y 25 del DS 12/2020",
        "tabla": "envases",
        "motivo_sin_tabla": "",
        "que_hacer_sin_tabla": "",
        "categorias": {
            "domiciliario": "Envases domiciliarios",
            "no_domiciliario": "Envases no domiciliarios",
        },
        "materiales": {
            "carton_para_liquidos": "Carton para liquidos",
            "metal": "Metal",
            "papel_y_carton": "Papel y carton",
            "plastico": "Plastico",
            "vidrio": "Vidrio",
            "otros": "Otros materiales (subcategoria residual)",
        },
        "exige_categoria": True,
        "exige_material": True,
        "unidad_umbral": "kilogramos",
        "exenciones": [
            "No estan sujetos a la REP los productores que califiquen como microempresa segun la "
            "Ley 20.416 (art. 7 del DS 12/2020); el art. 10 inciso final tambien los exime de informar.",
            "Quien introduzca menos de 300 kilogramos de envases al anio no debe cumplir metas, pero si "
            "debe informar cada anio (arts. 7 y 10 del DS 12/2020).",
            "Los envases reutilizables no se consideran introducidos en el mercado para las metas "
            "(art. 3), pero tienen un contenido especial que informar (art. 10 inciso 3).",
            "La subcategoria residual otros no esta sujeta a metas, pero si a informar "
            "(art. 10 inciso 2).",
        ],
        "valorizacion": ("En envases las metas solo pueden cumplirse mediante reciclaje material: quedan fuera "
                         "los procesos que usan el residuo como fuente de energia o para producir combustible "
                         "(art. 28 del DS 12/2020)."),
    },
    "neumaticos": {
        "nombre": "Neumaticos",
        "letra": "e)",
        "decreto": "DS 8/2019 MMA",
        "publicacion_decreto": "20-01-2021",
        "metas_desde": "20-01-2023",
        "primer_anio_metas": 2023,
        "prorrateo_meses": None,
        "nota_prorrateo": ("El DS 8/2019 fija las metas por anio calendario de vigencia del titulo y no "
                           "contempla prorrateo del primer anio."),
        "anios_base": 1,
        "formula": "Pi = (NGi * 100) / (NCi-1 * FD)",
        "articulo_formula": "Art. 24 del DS 8/2019",
        "tabla": "neumaticos",
        "motivo_sin_tabla": "",
        "que_hacer_sin_tabla": "",
        "categorias": {
            "a": "Categoria A: aro inferior a 57 pulgadas, salvo los de aro igual a 45, 49 y 51 pulgadas",
            "b": "Categoria B: aro igual a 45, 49 o 51 pulgadas y aros iguales o mayores a 57 pulgadas",
        },
        "materiales": {},
        "exige_categoria": True,
        "exige_material": False,
        "unidad_umbral": "",
        "exenciones": [
            "Quedan excluidos los neumaticos de bicicletas, de sillas de ruedas y similares, y los "
            "neumaticos macizos.",
            "El DS 8/2019 no fija un umbral de toneladas bajo el cual el productor quede exento de metas.",
        ],
        "valorizacion": ("Se aceptan recauchaje, reciclaje material, coprocesamiento y valorizacion energetica "
                         "(art. 22), pero al menos el 60% de lo valorizado debe ser reciclaje material o "
                         "recauchaje (art. 20 letra B inciso final)."),
    },
    "pilas": {
        "nombre": "Pilas",
        "letra": "f)",
        "decreto": "DS 22/2025 MMA",
        "publicacion_decreto": "07-05-2026",
        "metas_desde": "07-05-2028",
        "primer_anio_metas": 2028,
        "prorrateo_meses": 7,
        "nota_prorrateo": ("El primer anio de metas (2028) se prorratea: M1 = (Mi x 7)/12, segun el art. 1 "
                           "transitorio del DS 22/2025."),
        "anios_base": 3,
        "formula": "PGi = 100 * (RGi + RCIi) / TIM_Prom3anios",
        "articulo_formula": "Art. 22 del DS 22/2025",
        "tabla": "pilas_y_aee",
        "motivo_sin_tabla": "",
        "que_hacer_sin_tabla": "",
        "categorias": {"general": "Pilas (categoria unica)"},
        "materiales": {},
        "exige_categoria": False,
        "exige_material": False,
        "unidad_umbral": "",
        "exenciones": [
            "No estan sujetos a metas los productores que califiquen como microempresa segun la "
            "Ley 20.416 (art. 6 del DS 22/2025), pero igual deben informar (art. 9).",
            "Las pilas que vienen dentro de un aparato y se pueden sacar a mano o con herramientas "
            "comunes de casa se cuentan como pilas; las demas se cuentan como parte del aparato "
            "(art. 5 del DS 22/2025).",
        ],
        "valorizacion": ("Las metas se cumplen con preparacion para la reutilizacion y reciclaje material "
                         "(art. 27), con residuos recolectados y valorizados en Chile por gestor autorizado "
                         "y registrado (art. 28)."),
    },
}

ORDEN_ARTICULO_10 = ["aceites_lubricantes", "aee", "baterias", "envases", "neumaticos", "pilas"]

# La meta general del DS 22/2025 es conjunta de pilas y AEE: la misma tabla sirve
# a los dos productos prioritarios.
TABLAS_COMPARTIDAS = {"pilas_y_aee": ("pilas", "aee")}


def _construir_alias(crudo):
    alias = {}
    for destino, nombres in crudo.items():
        for nombre in nombres:
            alias[_clave(nombre)] = destino
    return alias


ALIAS_PRODUCTO = _construir_alias({
    "aceites_lubricantes": ["aceites", "aceite", "aceite lubricante", "aceites lubricantes",
                            "lubricantes", "lubricante", "alu", "aceites usados"],
    "aee": ["aee", "aparatos electricos y electronicos", "aparatos electricos",
            "aparatos electronicos", "electronicos", "electrodomesticos", "raee"],
    "baterias": ["baterias", "bateria", "baterias de plomo"],
    "envases": ["envases", "envase", "envases y embalajes", "embalajes", "embalaje"],
    "neumaticos": ["neumaticos", "neumatico", "llantas", "llanta", "nfu"],
    "pilas": ["pilas", "pila"],
})

ALIAS_CATEGORIA = {
    "envases": _construir_alias({
        "domiciliario": ["domiciliario", "domiciliarios", "domiciliaria", "domiciliarias",
                         "hogar", "domestico"],
        "no_domiciliario": ["no domiciliario", "no domiciliarios", "no domiciliaria",
                            "no domiciliarias", "nodomiciliario", "industrial"],
    }),
    "neumaticos": _construir_alias({
        "a": ["a", "categoria a", "cat a", "tipo a"],
        "b": ["b", "categoria b", "cat b", "tipo b", "minero", "mineros"],
    }),
    "pilas_y_aee": _construir_alias({
        "general": ["general", "pilas", "pila", "aee", "otros", "otro",
                    "otros aparatos electricos y electronicos", "otros aee"],
        "ait": ["ait", "aparatos de intercambio de temperatura", "intercambio de temperatura"],
        "pfv": ["pfv", "paneles fotovoltaicos", "panel fotovoltaico", "fotovoltaico",
                "fotovoltaicos", "paneles solares"],
    }),
}

ALIAS_MATERIAL = _construir_alias({
    "carton_para_liquidos": ["carton para liquidos", "carton liquidos", "cartones para liquidos",
                             "tetra", "tetrapak", "tetra pak"],
    "metal": ["metal", "metales", "aluminio", "hojalata", "lata", "latas", "acero"],
    "papel_y_carton": ["papel y carton", "papel", "carton", "papel carton", "cartones"],
    "plastico": ["plastico", "plasticos", "pet", "hdpe", "polietileno", "polipropileno"],
    "vidrio": ["vidrio", "vidrios"],
    "otros": ["otros", "otro", "otros materiales", "madera", "textil"],
})


# --------------------------------------------------------------------------
# Normalizacion de lo que escribe la persona
# --------------------------------------------------------------------------

def _lista(nombres):
    return ", ".join(nombres)


def normalizar_producto(texto, donde=""):
    """Traduce lo que escribio la persona a uno de los seis productos prioritarios."""
    clave = _clave(texto)
    if not clave:
        raise Problema(
            "Falta indicar de que producto prioritario se trata%s." % donde,
            "Los productos de la Ley REP son: %s." % _lista(
                PRODUCTOS[p]["nombre"] for p in ORDEN_ARTICULO_10),
        )
    if clave in PRODUCTOS:
        return clave
    if clave in ALIAS_PRODUCTO:
        return ALIAS_PRODUCTO[clave]
    raise Problema(
        "No reconozco el producto prioritario «%s»%s." % (texto, donde),
        "La Ley REP cubre solo estos seis: %s. Si tu producto no esta en la lista, la Ley REP "
        "no le pone metas." % _lista(PRODUCTOS[p]["nombre"] for p in ORDEN_ARTICULO_10),
    )


def _tabla_de(clave_producto):
    return PRODUCTOS[clave_producto]["tabla"]


def normalizar_categoria(clave_producto, texto, donde=""):
    """Traduce la categoria escrita por la persona a la del decreto."""
    info = PRODUCTOS[clave_producto]
    tabla = info["tabla"] or clave_producto
    alias = ALIAS_CATEGORIA.get(tabla, {})
    clave = _clave(texto)
    if not clave:
        if info["exige_categoria"]:
            raise Problema(
                "Falta la categoria de %s%s." % (info["nombre"].lower(), donde),
                "Completa la columna Categoria con una de estas: %s."
                % _lista("%s (%s)" % (c, n) for c, n in sorted(info["categorias"].items())),
            )
        return "general" if tabla == "pilas_y_aee" else ""
    if clave in info["categorias"]:
        return clave
    if clave in alias:
        return alias[clave]
    if not info["categorias"]:
        return ""
    raise Problema(
        "No reconozco la categoria «%s» de %s%s." % (texto, info["nombre"].lower(), donde),
        "Usa una de estas: %s." % _lista("%s (%s)" % (c, n) for c, n in sorted(info["categorias"].items())),
    )


def normalizar_material(texto, clave_producto="envases", donde=""):
    """Traduce la subcategoria de material de envases."""
    info = PRODUCTOS.get(clave_producto, PRODUCTOS["envases"])
    clave = _clave(texto)
    if not clave:
        if info["exige_material"]:
            raise Problema(
                "Falta el material del envase%s." % donde,
                "Completa la columna Material con una de estas subcategorias: %s."
                % _lista(sorted(PRODUCTOS["envases"]["materiales"])),
            )
        return ""
    if not info["exige_material"]:
        return ""
    if clave in PRODUCTOS["envases"]["materiales"]:
        return clave
    if clave in ALIAS_MATERIAL:
        return ALIAS_MATERIAL[clave]
    raise Problema(
        "No reconozco el material «%s»%s." % (texto, donde),
        "Para envases usa: carton para liquidos, metal, papel y carton, plastico, vidrio u otros. "
        "Si el envase es de varios materiales, el art. 6 del DS 12/2020 lo asigna al material que sea "
        "al menos el 85% de su masa; si ninguno llega a ese 85%, se reparte entre los materiales en "
        "proporcion a su composicion y se declara en filas separadas.",
    )


def anio_valido(valor, donde=""):
    """Acepta 2026, '2026' o '2026-03' y devuelve el anio como numero."""
    texto = str(valor if valor not in (None, True) else "").strip()
    coincidencia = re.match(r"^(\d{4})", texto)
    if not coincidencia:
        raise Problema(
            "No entiendo el anio «%s»%s." % (valor, donde),
            "Escribe solo el anio con cuatro digitos, por ejemplo 2026.",
        )
    anio = int(coincidencia.group(1))
    if anio < 2016 or anio > 2100:
        raise Problema(
            "El anio %d esta fuera de lo que cubre la Ley REP%s." % (anio, donde),
            "La Ley 20.920 se publico el 01-06-2016. Usa un anio entre 2016 y 2100.",
        )
    return anio


def _numero(valor, campo, donde=""):
    """Lee toneladas escritas como 1250, 1250.5, 1250,5 o 1.250,5."""
    if valor in (None, "", True):
        return 0.0
    texto = str(valor).strip()
    if re.match(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$", texto):   # 1.250,5 al estilo chileno
        texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    try:
        numero = float(texto)
    except ValueError:
        raise Problema(
            "El valor «%s» de la columna %s no es un numero%s." % (valor, campo, donde),
            "Escribe solo el numero de toneladas, sin la unidad ni texto. Si no tienes el dato, "
            "deja la celda vacia y cuentamelo.",
        )
    if numero < 0:
        raise Problema(
            "La columna %s tiene un numero negativo (%s)%s." % (campo, valor, donde),
            "Las toneladas no pueden ser negativas. Corrige la celda o dejala vacia.",
        )
    return numero


# --------------------------------------------------------------------------
# Tabla de metas
# --------------------------------------------------------------------------

def _anio_de_tabla(texto, linea):
    """Lee '2026' o '2030+' (2030 en adelante) de la columna anio."""
    crudo = str(texto or "").strip()
    en_adelante = crudo.endswith("+")
    if en_adelante:
        crudo = crudo[:-1]
    if not crudo.isdigit():
        raise Problema(
            "La tabla de metas de la Ley REP tiene un anio mal escrito en la linea %d: «%s»." % (linea, texto),
            "El anio debe ser de cuatro digitos, con un + al final si la meta rige de ese anio en adelante.",
        )
    return int(crudo), en_adelante


def cargar_metas(ruta=None):
    """Lee la tabla de metas por producto, categoria, material y anio."""
    ruta = ruta or ARCHIVO_METAS
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro la tabla de metas de la Ley REP (%s)." % os.path.basename(ruta),
            "Sin esa tabla no puedo decirte que porcentaje te exige el decreto. "
            "Avisa para reinstalar los datos del motor.",
        )
    metas = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for linea, fila in enumerate(csv.DictReader(archivo), start=2):
            producto = _clave(fila.get("producto"))
            if not producto:
                continue
            anio, en_adelante = _anio_de_tabla(fila.get("anio"), linea)
            metas.append({
                "producto": producto,
                "categoria": _clave(fila.get("categoria")),
                "material": _clave(fila.get("material")),
                "anio": anio,
                "en_adelante": en_adelante,
                "anio_tabla": (fila.get("anio") or "").strip(),
                "meta_recoleccion_pct": _valor_meta(fila.get("meta_recoleccion_pct")),
                "meta_valorizacion_pct": _valor_meta(fila.get("meta_valorizacion_pct")),
                "decreto": (fila.get("decreto") or "").strip(),
                "articulo": (fila.get("articulo") or "").strip(),
                "fuente": (fila.get("fuente") or "").strip(),
                "url": (fila.get("url") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
                "linea": linea,
            })
    return metas


def _valor_meta(valor):
    if valor in (None, ""):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


def _categorias_validas(clave_producto):
    """Categorias de la tabla que le corresponden a este producto prioritario."""
    info = PRODUCTOS[clave_producto]
    if clave_producto == "pilas":
        return {"general"}          # las metas de AIT y PFV son de AEE, no de pilas
    if info["categorias"]:
        return set(info["categorias"])
    return set()


def _factor_denominador(clave_producto, categoria):
    """Devuelve (factor, explicacion) del ajuste del denominador de cada decreto."""
    if clave_producto == "neumaticos":
        factor = FACTOR_DESGASTE_NEUMATICOS.get(categoria)
        if factor is None:
            raise Problema(
                "No se de que categoria es el neumatico, y el factor de desgaste depende de eso.",
                "Indica la categoria A o B: el art. 24 del DS 8/2019 usa FD = 0,84 en la categoria A "
                "y FD = 0,75 en la categoria B.",
            )
        return factor, ("Factor de desgaste por uso FD = %s de la categoria %s (art. 24 del DS 8/2019): "
                        "las toneladas puestas en el mercado se multiplican por ese factor antes de "
                        "aplicar la meta." % (str(factor).replace(".", ","), categoria.upper()))
    if clave_producto == "aceites_lubricantes":
        return 1 - TASA_PERDIDA_ACEITES, (
            "Tasa de perdida TP = 0,3 (art. 23 del DS 47/2023): del aceite puesto en el mercado se "
            "pierde un 30% durante su uso, asi que la meta se aplica sobre el 70% restante.")
    if clave_producto in ("pilas", "aee"):
        return 1.0, ("El denominador no lleva factor de ajuste, pero es el promedio de los tres anios "
                     "anteriores (art. 22 del DS 22/2025), no el anio anterior.")
    return 1.0, "El denominador es simplemente lo puesto en el mercado el anio anterior, sin ajustes."


def explicacion_denominador(clave_producto, categoria=None):
    """Explica en palabras como se arma el denominador, sin exigir la categoria."""
    if clave_producto == "neumaticos" and not categoria:
        return ("El denominador se multiplica por el factor de desgaste por uso FD del art. 24 del "
                "DS 8/2019: 0,84 en la categoria A y 0,75 en la categoria B.")
    return _factor_denominador(clave_producto, categoria)[1]


def _prorratear(clave_producto, anio, meta):
    """Aplica el prorrateo del primer anio de metas (F3), si el decreto lo manda."""
    info = PRODUCTOS[clave_producto]
    meses = info.get("prorrateo_meses")
    if meta is None or not meses or anio != info.get("primer_anio_metas"):
        return meta, False, ""
    efectiva = meta * meses / 12.0
    return efectiva, True, (
        "Primer anio de metas: se aplica el prorrateo M1 = (Mi x MO)/12 del art. 1 transitorio del %s, "
        "con MO = %d meses, porque las metas empezaron a regir el %s. La meta de tabla de %s%% queda en "
        "%s%% para este anio."
        % (info["decreto"], meses, info["metas_desde"], formatear_numero(meta), formatear_numero(efectiva)))


def formatear_numero(valor):
    if valor is None:
        return "-"
    return ("%.4f" % valor).rstrip("0").rstrip(".").replace(".", ",")


def metas_de(producto, anio, material=None, categoria=None, metas=None):
    """Metas que le rigen a un producto prioritario en un anio determinado.

    Devuelve siempre un diccionario: cuando no hay metas explica por que
    (todavia no rigen, no hay decreto, la tabla del decreto no esta verificada o
    el anio quedo fuera de la tabla) en vez de devolver un numero inventado.
    """
    clave = normalizar_producto(producto)
    info = PRODUCTOS[clave]
    anio = anio_valido(anio)
    metas = metas if metas is not None else cargar_metas()

    filtro_categoria = normalizar_categoria(clave, categoria) if categoria else None
    filtro_material = normalizar_material(material, clave) if material else None

    resultado = {
        "producto": clave,
        "nombre": info["nombre"],
        "letra_articulo_10": info["letra"],
        "anio": anio,
        "decreto": info["decreto"],
        "publicacion_decreto": info["publicacion_decreto"],
        "metas_vigentes_desde": info["metas_desde"],
        "formula": info["formula"],
        "articulo_formula": info["articulo_formula"],
        "anios_base": info["anios_base"],
        "como_se_calcula_el_denominador": explicacion_denominador(clave, filtro_categoria),
        "hay_metas": False,
        "motivo": "",
        "motivo_clave": "",
        "que_hacer": "",
        "metas": [],
        "advertencias": [],
        "fuentes": [],
    }

    if not info["tabla"]:
        resultado["motivo"] = info["motivo_sin_tabla"]
        resultado["motivo_clave"] = "sin_decreto" if not info["decreto"] else "sin_tabla_verificada"
        resultado["que_hacer"] = info["que_hacer_sin_tabla"]
        resultado["advertencias"].append(info["motivo_sin_tabla"])
        return resultado

    if info["primer_anio_metas"] and anio < info["primer_anio_metas"]:
        resultado["motivo"] = (
            "Las metas del %s rigen desde el %s, asi que en %d todavia no hay porcentaje que cumplir."
            % (info["decreto"], info["metas_desde"], anio))
        resultado["motivo_clave"] = "antes_de_vigencia"
        resultado["que_hacer"] = (
            "Mientras tanto corre igual la obligacion de declarar cada anio las toneladas puestas en el "
            "mercado (art. 2 transitorio de la Ley 20.920), a traves de la Ventanilla Unica del RETC.")
        return resultado

    validas = _categorias_validas(clave)
    elegidas = {}
    for fila in metas:
        if fila["producto"] != info["tabla"]:
            continue
        if validas and fila["categoria"] and fila["categoria"] not in validas:
            continue
        if filtro_categoria and fila["categoria"] != filtro_categoria:
            continue
        if filtro_material and fila["material"] != filtro_material:
            continue
        if fila["anio"] == anio or (fila["en_adelante"] and fila["anio"] < anio):
            llave = (fila["categoria"], fila["material"])
            anterior = elegidas.get(llave)
            if anterior is None or fila["anio"] > anterior["anio"]:
                elegidas[llave] = fila

    if not elegidas:
        ultimo = max([f["anio"] for f in metas if f["producto"] == info["tabla"]] or [0])
        if filtro_categoria or filtro_material:
            resultado["motivo"] = (
                "No tengo metas del %s para %d con esa categoria o ese material."
                % (info["decreto"], anio))
            resultado["que_hacer"] = ("Revisa como escribiste la categoria y el material, o pideme las metas "
                                      "del producto completo sin filtrarlas.")
        else:
            resultado["motivo"] = (
                "La tabla del %s que tengo cargada llega hasta el anio %d, y me estas pidiendo %d."
                % (info["decreto"], ultimo, anio))
            resultado["que_hacer"] = ("El decreto no fija metas mas alla de ese anio, o todavia no se publican. "
                                      "No voy a inventar un porcentaje.")
        resultado["motivo_clave"] = "fuera_de_tabla"
        return resultado

    fuentes = set()
    for (categoria_fila, material_fila), fila in sorted(elegidas.items()):
        recoleccion, prorrateada, explicacion = _prorratear(clave, anio, fila["meta_recoleccion_pct"])
        valorizacion, _, _ = _prorratear(clave, anio, fila["meta_valorizacion_pct"])
        resultado["metas"].append({
            "producto": clave,
            "categoria": categoria_fila,
            "categoria_nombre": info["categorias"].get(categoria_fila, ""),
            "material": material_fila,
            "material_nombre": PRODUCTOS["envases"]["materiales"].get(material_fila, ""),
            "anio": anio,
            "anio_de_la_tabla": fila["anio_tabla"],
            "meta_de_tabla_recoleccion_pct": fila["meta_recoleccion_pct"],
            "meta_de_tabla_valorizacion_pct": fila["meta_valorizacion_pct"],
            "meta_recoleccion_pct": recoleccion,
            "meta_valorizacion_pct": valorizacion,
            "meta_unica": fila["meta_recoleccion_pct"] == fila["meta_valorizacion_pct"],
            "prorrateada": prorrateada,
            "explicacion_prorrateo": explicacion,
            "sin_meta_este_anio": fila["meta_recoleccion_pct"] is None and fila["meta_valorizacion_pct"] is None,
            "decreto": fila["decreto"],
            "articulo": fila["articulo"],
            "fuente": fila["fuente"],
            "url": fila["url"],
            "verificado_el": fila["verificado_el"],
            "notas": fila["notas"],
        })
        if explicacion and explicacion not in resultado["advertencias"]:
            resultado["advertencias"].append(explicacion)
        fuentes.add("%s - %s - %s" % (fila["decreto"], fila["articulo"], fila["url"]))

    resultado["hay_metas"] = any(not m["sin_meta_este_anio"] for m in resultado["metas"])
    resultado["fuentes"] = sorted(fuentes)
    if not resultado["hay_metas"]:
        resultado["motivo"] = ("El decreto no fija meta para %d en esa categoria: el propio decreto dice que "
                               "los primeros anios de vigencia van sin meta especifica." % anio)
        resultado["motivo_clave"] = "sin_meta_ese_anio"
    if info["valorizacion"]:
        resultado["advertencias"].append(info["valorizacion"])
    return resultado


def productos_prioritarios():
    """Los seis productos prioritarios del art. 10, con el estado de su decreto."""
    catalogo = []
    for clave in ORDEN_ARTICULO_10:
        info = PRODUCTOS[clave]
        catalogo.append({
            "producto": clave,
            "nombre": info["nombre"],
            "letra_articulo_10": info["letra"],
            "decreto": info["decreto"] or "sin decreto de metas publicado",
            "publicacion_decreto": info["publicacion_decreto"],
            "metas_vigentes_desde": info["metas_desde"] or "todavia no rigen metas",
            "tiene_metas_cargadas": bool(info["tabla"]),
            "motivo_sin_metas": info["motivo_sin_tabla"],
            "formula": info["formula"],
            "articulo_formula": info["articulo_formula"],
            "anios_base_del_denominador": info["anios_base"],
            "categorias": info["categorias"],
            "materiales": info["materiales"],
            "exenciones": info["exenciones"],
            "como_se_valoriza": info["valorizacion"],
        })
    return catalogo


# --------------------------------------------------------------------------
# Calculo de cumplimiento
# --------------------------------------------------------------------------

def _primero(fila, claves):
    for clave in claves:
        if fila.get(clave) not in (None, ""):
            return fila.get(clave)
    return ""


def normalizar_declaracion(fila):
    """Convierte una fila de la planilla en un registro comparable con las metas."""
    numero = fila.get("_fila") or fila.get("fila")
    donde = " (fila %s de la planilla)" % numero if numero else ""
    producto = normalizar_producto(_primero(fila, ["producto", "producto_prioritario", "prioritario"]), donde)
    anio = anio_valido(_primero(fila, ["anio", "ano", "periodo", "anio_calendario"]), donde)
    categoria = normalizar_categoria(producto, _primero(fila, ["categoria", "categoria_del_producto"]), donde)
    material = normalizar_material(_primero(fila, ["material", "subcategoria"]), producto, donde)
    return {
        "fila": numero,
        "producto": producto,
        "categoria": categoria,
        "material": material,
        "anio": anio,
        "puestas": _numero(_primero(fila, ["toneladas_puestas_en_el_mercado", "toneladas_puestas",
                                           "puestas_en_el_mercado", "toneladas"]),
                           "Toneladas puestas en el mercado", donde),
        "recolectadas": _numero(_primero(fila, ["toneladas_recolectadas", "recolectadas"]),
                                "Toneladas recolectadas", donde),
        "valorizadas": _numero(_primero(fila, ["toneladas_valorizadas", "valorizadas"]),
                               "Toneladas valorizadas", donde),
        "sistema": str(_primero(fila, ["sistema_de_gestion", "sistema"]) or "").strip(),
    }


def _coincide(registro, clave_producto, categoria, material):
    """Decide si una declaracion entra en el calculo de una meta.

    La meta general del DS 22/2025 es conjunta de pilas y AEE y excluye los
    paneles fotovoltaicos (art. 21); las metas de AIT y PFV usan solo sus
    propios residuos (arts. 23 y 25).
    """
    if clave_producto in ("pilas", "aee"):
        if not categoria:
            return registro["producto"] in ("pilas", "aee")
        if categoria == "general":
            return registro["producto"] in ("pilas", "aee") and registro["categoria"] != "pfv"
        return registro["producto"] == "aee" and registro["categoria"] == categoria
    if registro["producto"] != clave_producto:
        return False
    if categoria and registro["categoria"] != categoria:
        return False
    if material and registro["material"] != material:
        return False
    return True


def _evaluaciones(meta, recolectadas, valorizadas):
    """Une o separa la meta de recoleccion y la de valorizacion segun el decreto."""
    if meta is None:
        return [("recoleccion y valorizacion", None, valorizadas)]
    recoleccion = meta["meta_recoleccion_pct"]
    valorizacion = meta["meta_valorizacion_pct"]
    if recoleccion is None and valorizacion is None:
        return [("recoleccion y valorizacion", None, valorizadas)]
    if recoleccion == valorizacion:
        # El decreto fija una sola meta: la recoleccion se entiende cumplida al valorizar.
        return [("recoleccion y valorizacion", valorizacion, valorizadas)]
    return [("recoleccion", recoleccion, recolectadas),
            ("valorizacion", valorizacion, valorizadas)]


def _evaluar_combinacion(clave_producto, categoria, material, meta, seleccion, anio,
                         estado_sin_meta, motivo_sin_meta):
    info = PRODUCTOS[clave_producto]
    anios_base = [anio - salto for salto in range(1, info["anios_base"] + 1)]
    puestas_por_anio = {}
    faltantes = []
    for base in anios_base:
        filas = [r for r in seleccion if r["anio"] == base]
        puestas_por_anio[str(base)] = sum(r["puestas"] for r in filas)
        if not filas:
            faltantes.append(base)

    advertencias = []
    suma = sum(puestas_por_anio.values())
    promedio = suma / float(info["anios_base"])
    if faltantes and info["anios_base"] > 1:
        advertencias.append(
            "No declaraste toneladas puestas en el mercado de %s. El art. 22 del DS 22/2025 manda dividir "
            "la suma por 3 igual, asi que el promedio -y con el la meta en toneladas- queda mas bajo de lo "
            "que corresponderia. Completa esos anios para tener el numero real."
            % _lista(str(a) for a in faltantes))
    elif faltantes:
        advertencias.append(
            "No declaraste toneladas puestas en el mercado de %d, que es el anio base de la meta de %d. "
            "Sin ese dato no puedo calcular cuantas toneladas te exige el decreto."
            % (faltantes[0], anio))

    factor, explicacion_factor = _factor_denominador(clave_producto, categoria)
    base_calculo = promedio * factor
    recolectadas = sum(r["recolectadas"] for r in seleccion if r["anio"] == anio)
    valorizadas = sum(r["valorizadas"] for r in seleccion if r["anio"] == anio)

    motivo = motivo_sin_meta
    if meta is not None and meta.get("sin_meta_este_anio"):
        motivo = meta.get("notas") or motivo_sin_meta

    items = []
    for tipo, meta_pct, gestionadas in _evaluaciones(meta, recolectadas, valorizadas):
        if meta_pct is None:
            estado, exigidas, brecha = estado_sin_meta, None, None
        elif base_calculo <= 0:
            estado, exigidas, brecha = "sin datos", None, None
        else:
            exigidas = base_calculo * meta_pct / 100.0
            brecha = max(0.0, exigidas - gestionadas)
            estado = "cumple" if gestionadas + 1e-9 >= exigidas else "no cumple"
        items.append({
            "producto": clave_producto,
            "producto_nombre": info["nombre"],
            "categoria": categoria,
            "categoria_nombre": info["categorias"].get(categoria, ""),
            "material": material,
            "material_nombre": PRODUCTOS["envases"]["materiales"].get(material, ""),
            "anio": anio,
            "anios_base": anios_base,
            "toneladas_puestas_en_el_mercado": round(promedio, 4),
            "toneladas_puestas_suma": round(suma, 4),
            "toneladas_puestas_por_anio": puestas_por_anio,
            "factor_denominador": factor,
            "explicacion_denominador": explicacion_factor,
            "base_de_calculo_t": round(base_calculo, 4),
            "tipo_meta": tipo,
            "meta_aplicable_pct": round(meta_pct, 4) if meta_pct is not None else None,
            "meta_de_tabla_pct": (meta.get("meta_de_tabla_valorizacion_pct") if tipo != "recoleccion"
                                  else meta.get("meta_de_tabla_recoleccion_pct")) if meta else None,
            "prorrateada": bool(meta and meta.get("prorrateada")),
            "toneladas_exigidas": round(exigidas, 4) if exigidas is not None else None,
            "toneladas_gestionadas": round(gestionadas, 4),
            "porcentaje_logrado": round(gestionadas * 100.0 / base_calculo, 4) if base_calculo > 0 else None,
            "brecha_t": round(brecha, 4) if brecha is not None else None,
            "excedente_t": (round(gestionadas - exigidas, 4)
                            if exigidas is not None and gestionadas > exigidas else 0.0),
            "estado": estado,
            "motivo": motivo if meta_pct is None else "",
            "formula": info["formula"],
            "articulo": meta["articulo"] if meta else info["articulo_formula"],
            "decreto": meta["decreto"] if meta else info["decreto"],
            "fuente": meta["fuente"] if meta else "",
            "url": meta["url"] if meta else "",
            "notas": meta["notas"] if meta else "",
            "advertencias": list(advertencias),
        })
    return items


def calcular_cumplimiento(declaraciones, anio, producto, categoria=None, material=None, metas=None):
    """Compara lo declarado con la meta del decreto, producto por producto.

    declaraciones: filas de la planilla (producto, categoria, material, anio,
    toneladas puestas en el mercado, recolectadas y valorizadas).

    Devuelve, por cada combinacion con meta, las toneladas puestas en el
    mercado, la meta aplicable, las toneladas exigidas, las gestionadas, la
    brecha y el estado. Cuando no hay meta verificada lo dice en el estado en
    vez de calcular un cumplimiento inventado.
    """
    clave = normalizar_producto(producto)
    info = PRODUCTOS[clave]
    anio = anio_valido(anio)
    metas = metas if metas is not None else cargar_metas()

    registros = [normalizar_declaracion(fila) for fila in (declaraciones or [])]
    propios = [r for r in registros if _coincide(r, clave, None, None)]

    datos_metas = metas_de(clave, anio, material=material, categoria=categoria, metas=metas)
    estado_sin_meta = ("sin meta verificada"
                       if datos_metas["motivo_clave"] in ("sin_tabla_verificada", "sin_decreto")
                       else "sin meta")

    filtro_categoria = normalizar_categoria(clave, categoria) if categoria else None
    filtro_material = normalizar_material(material, clave) if material else None

    combinaciones = []
    for meta in datos_metas["metas"]:
        combinaciones.append((meta["categoria"], meta["material"], meta))
    vistas = {(c, m) for c, m, _ in combinaciones}
    for registro in propios:
        llave = (registro["categoria"], registro["material"])
        if llave in vistas:
            continue
        if filtro_categoria and registro["categoria"] != filtro_categoria:
            continue
        if filtro_material and registro["material"] != filtro_material:
            continue
        vistas.add(llave)
        combinaciones.append((llave[0], llave[1], None))

    items, sin_declarar, advertencias = [], [], list(datos_metas["advertencias"])
    for categoria_combo, material_combo, meta in combinaciones:
        seleccion = [r for r in registros if _coincide(r, clave, categoria_combo, material_combo)]
        if not seleccion:
            sin_declarar.append({
                "categoria": categoria_combo,
                "material": material_combo,
                "meta_pct": meta["meta_valorizacion_pct"] if meta else None,
                "articulo": meta["articulo"] if meta else "",
            })
            continue
        items.extend(_evaluar_combinacion(clave, categoria_combo, material_combo, meta, seleccion,
                                          anio, estado_sin_meta, datos_metas["motivo"]))

    if clave in ("pilas", "aee") and items:
        advertencias.append(
            "La meta general del art. 21 del DS 22/2025 es conjunta: se calcula sumando las pilas y los "
            "aparatos electricos y electronicos que no sean paneles fotovoltaicos. Por eso da lo mismo si "
            "preguntas por pilas o por AEE: la meta general sale igual.")

    con_meta = [i for i in sin_declarar if i["meta_pct"] is not None]
    if con_meta:
        advertencias.append(
            "Hay metas de %s para %d que no aparecen en tu planilla: %s. Si la empresa puso esas toneladas "
            "en el mercado, faltan filas por declarar."
            % (info["nombre"].lower(), anio,
               _lista(" ".join(x for x in (i["categoria"], i["material"]) if x).replace("_", " ")
                      for i in con_meta)))
    for item in items:
        for aviso in item["advertencias"]:
            if aviso not in advertencias:
                advertencias.append(aviso)

    resumen = {
        "metas_evaluadas": len(items),
        "cumple": len([i for i in items if i["estado"] == "cumple"]),
        "no_cumple": len([i for i in items if i["estado"] == "no cumple"]),
        "sin_meta": len([i for i in items if i["estado"] in ("sin meta", "sin meta verificada")]),
        "sin_datos": len([i for i in items if i["estado"] == "sin datos"]),
        "brecha_total_t": round(sum(i["brecha_t"] or 0.0 for i in items), 4),
    }
    return {
        "producto": clave,
        "producto_nombre": info["nombre"],
        "anio": anio,
        "decreto": info["decreto"],
        "metas_vigentes_desde": info["metas_desde"],
        "formula": info["formula"],
        "articulo_formula": info["articulo_formula"],
        "hay_metas": datos_metas["hay_metas"],
        "motivo": datos_metas["motivo"],
        "que_hacer": datos_metas["que_hacer"],
        "items": items,
        "metas_sin_declarar": sin_declarar,
        "resumen": resumen,
        "advertencias": advertencias,
        "fuentes": datos_metas["fuentes"],
        "calculado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }


# --------------------------------------------------------------------------
# Obligaciones, plazos y sanciones
# --------------------------------------------------------------------------

SANCIONES = {
    "quien_fiscaliza": ("La Superintendencia del Medio Ambiente verifica el cumplimiento de las metas y de "
                        "las obligaciones asociadas (art. 38 de la Ley 20.920) y clasifica las infracciones "
                        "en gravisimas, graves y leves (art. 39)."),
    "articulo": "Art. 40 de la Ley 20.920",
    "rangos": [
        {"gravedad": "gravisima", "sancion": "Multa de hasta 10.000 unidades tributarias anuales (UTA)"},
        {"gravedad": "grave", "sancion": "Multa de hasta 5.000 UTA"},
        {"gravedad": "leve", "sancion": "Amonestacion por escrito o multa de hasta 1.000 UTA"},
    ],
    "aviso": ("El monto exacto lo determina la SMA caso a caso. Este motor no estima multas: solo muestra "
              "los rangos que fija la ley."),
}

PLAZOS_ANUALES = [
    {"fecha": "30 de marzo", "obligacion": "Declarar al SINADER los residuos generados el anio anterior",
     "sujeto": "Establecimientos que generen mas de 12 toneladas de residuos al anio",
     "articulo": "Art. 25 del DS 1/2013 MMA", "verificado": True},
    {"fecha": "31 de mayo", "obligacion": ("Informe final del sistema de gestion por el anio anterior, "
                                           "certificado y con nueva garantia"),
     "sujeto": "Sistemas de gestion",
     "articulo": "Art. 18 del DS 12/2020; art. 17 del DS 8/2019; art. 16 del DS 22/2025",
     "verificado": True},
    {"fecha": "30 de junio", "obligacion": ("Informar al Ministerio el cambio de sistema de gestion para el "
                                            "anio siguiente"),
     "sujeto": "Productores de envases", "articulo": "Art. 9 del DS 12/2020", "verificado": True},
    {"fecha": "30 de septiembre", "obligacion": "Informe de avance del sistema de gestion (1 de enero a 30 de junio)",
     "sujeto": "Sistemas de gestion",
     "articulo": "Art. 18 del DS 12/2020; art. 17 del DS 8/2019; art. 16 del DS 22/2025",
     "verificado": True},
    {"fecha": "1 al 31 de octubre", "obligacion": ("Declaracion Jurada Anual (DJA) del RETC: confirmar bajo "
                                                   "juramento todo lo reportado en los sistemas sectoriales"),
     "sujeto": "El encargado de cada establecimiento registrado (no un delegado ni el representante legal)",
     "articulo": "Art. 16 del DS 1/2013 MMA; art. 35 letra m) de la Ley 20.417", "verificado": True},
    {"fecha": "Sin fecha reglamentaria fija", "obligacion": ("Declaracion anual de productos prioritarios "
                                                             "puestos en el mercado, en la Ventanilla Unica"),
     "sujeto": "Productores de productos prioritarios",
     "articulo": "Art. 11 y art. 2 transitorio de la Ley 20.920",
     "verificado": False,
     "nota": ("No se identifico una fecha limite reglamentaria: el Ministerio del Medio Ambiente abre la "
              "declaracion por convocatoria anual. Para 2026 la anuncio para el ultimo trimestre, pero eso "
              "hay que confirmarlo en portalvu.mma.gob.cl.")},
    {"fecha": "4 meses desde la primera introduccion al mercado",
     "obligacion": "Inscribirse en el RETC y adherir a un sistema de gestion",
     "sujeto": "Productores nuevos de envases", "articulo": "Art. 9 del DS 12/2020", "verificado": True},
    {"fecha": "Al cursar la declaracion de importacion",
     "obligacion": ("Acreditar ante el Servicio Nacional de Aduanas que se forma parte de un sistema de "
                    "gestion autorizado"),
     "sujeto": "Importadores de neumaticos", "articulo": "DS 8/2019", "verificado": True},
]

OBLIGACIONES_DEL_PRODUCTOR = [
    {"obligacion": "Inscribirse en el Registro de Emisiones y Transferencias de Contaminantes (RETC), "
                   "en la Ventanilla Unica",
     "articulo": "Art. 9 letra a) en relacion con el art. 37 de la Ley 20.920; art. 18 letra h) del DS 1/2013",
     "donde": VENTANILLA_UNICA},
    {"obligacion": "Cumplir las metas a traves de un sistema de gestion, individual o colectivo",
     "articulo": "Art. 19 de la Ley 20.920", "donde": ""},
    {"obligacion": "Si el sistema es individual, contratar gestores autorizados y registrados",
     "articulo": "Art. 21 de la Ley 20.920", "donde": ""},
    {"obligacion": "Organizar y financiar la recoleccion y la valorizacion de los residuos en todo el "
                   "territorio nacional",
     "articulo": "Decretos de metas de cada producto prioritario", "donde": ""},
    {"obligacion": "Declarar cada anio la informacion del art. 11: directamente al RETC si el sistema es "
                   "individual, o a traves del sistema colectivo",
     "articulo": "Art. 11 de la Ley 20.920; art. 9 del DS 12/2020; art. 8 del DS 22/2025",
     "donde": VENTANILLA_UNICA},
    {"obligacion": "Mientras no rijan las metas del decreto respectivo, declarar igual cada anio las "
                   "cantidades puestas en el mercado",
     "articulo": "Art. 2 transitorio de la Ley 20.920", "donde": VENTANILLA_UNICA},
]

DEFINICION_PRODUCTOR = {
    "articulo": "Art. 3 N 21 de la Ley 20.920",
    "es_productor": [
        "Quien enajena un producto prioritario por primera vez en el mercado nacional.",
        "Quien enajena bajo marca propia un producto prioritario comprado a un tercero que no es el "
        "primer distribuidor.",
        "Quien importa un producto prioritario para su propio uso profesional.",
    ],
    "importadores": ("El importador queda capturado: por la letra a) cuando vende por primera vez en Chile lo "
                     "que importo, y por la letra c) cuando importa para su propio uso profesional. En envases "
                     "y embalajes es productor quien introduce al mercado el bien de consumo envasado o "
                     "embalado, aunque el envase lo haya comprado a otro."),
}
