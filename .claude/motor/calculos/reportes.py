# -*- coding: utf-8 -*-
"""Marcos de reporte de sostenibilidad: que pide cada uno y cuanto alcanza a cubrir la empresa.

El catalogo vive en datos/marcos_reporte.csv. Cada fila es un contenido que el
marco pide, con el dato del espacio de trabajo del que puede salir (columna
dato_fuente). Si la columna esta vacia, es un texto que tiene que escribir la
empresa: ningun calculo lo puede inventar.

La cobertura se mide asi:
    cubierto  = estan todos los datos que ese contenido necesita
    parcial   = esta alguno, pero no todos
    pendiente = no esta ninguno, o el contenido se redacta a mano

    porcentaje = (cubiertos + 0.5 x parciales) / total x 100

Es la misma regla que usa el diagnostico ESG: lo completo suma todo, lo que va a
medias suma la mitad.
"""

import csv
import os
import re
import unicodedata

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_MARCOS = os.path.join(CARPETA_DATOS, "marcos_reporte.csv")

ESTADOS = ("cubierto", "parcial", "pendiente")

DIMENSIONES = {
    "general": "Informacion general de la organizacion",
    "gobernanza": "Gobernanza",
    "economico": "Economico",
    "ambiental": "Ambiental",
    "social": "Social",
}
ORDEN_DIMENSIONES = ["general", "gobernanza", "economico", "ambiental", "social"]

OBLIGATORIEDAD = {
    "si": "Se reporta siempre",
    "no": "Opcional o disponible como alivio",
    "segun_materialidad": "Se reporta si el tema es material para la empresa",
    "segun_actividad": "Se reporta solo si la empresa hace esa actividad",
}

# Datos del espacio de trabajo que el motor sabe reconocer. La columna
# dato_fuente del CSV solo puede usar estas claves.
DATOS_CONOCIDOS = {
    "empresa.json": "Ficha de la empresa (empresa.json)",
    "sitios.xlsx": "Planilla de sitios (datos/sitios.xlsx)",
    "consumos.xlsx": "Planilla de consumos de energia (datos/consumos.xlsx)",
    "alcance3.xlsx": "Planilla de cadena de valor (datos/alcance3.xlsx)",
    "personas.xlsx": "Planilla de personas (datos/personas.xlsx)",
    "huella.total_t_co2e": "Huella total calculada (resultados/huella_*.json)",
    "huella.por_alcance.alcance_1": "Emisiones de alcance 1 calculadas",
    "huella.por_alcance.alcance_2": "Emisiones de alcance 2 calculadas",
    "huella.por_alcance.alcance_3": "Emisiones de alcance 3 calculadas",
    "huella.por_categoria_alcance3": "Alcance 3 abierto por categoria del GHG Protocol",
    "huella.por_sitio": "Emisiones repartidas por sitio",
    "huella.por_periodo": "Emisiones de mas de un periodo, para comparar",
    "huella.calidad_datos": "Calidad de los datos de la huella",
    "huella.set_pcg": "Metodologia y potenciales de calentamiento global usados",
    "agua.indicadores": "Indicadores de agua calculados (resultados/agua_*.json)",
    "diagnostico": "Diagnostico ESG (seguimiento/diagnostico.json)",
    "metas": "Metas registradas (seguimiento/metas.json)",
}

# Para que sirve cada marco, en palabras de la persona que va a reportar.
# Las fechas y obligaciones vienen de docs/investigacion/06-marcos-reporte-metas-greenwashing.md
# y, para la NCG 461, de docs/investigacion/05-chile-peru-gobernanza-clima-datos.md.
GUIA_MARCOS = {
    "GRI": {
        "nombre_largo": "GRI Standards (Global Reporting Initiative)",
        "para_quien": "Clientes, comunidad, trabajadores y publico general.",
        "cuando_usarlo": "Cuando la empresa quiere contar como afecta al entorno y a las personas, "
                         "y un cliente grande o una licitacion pide una memoria de sostenibilidad.",
        "mira": "Materialidad de impacto: que efectos genera la empresa sobre las personas y el ambiente.",
        "obligatorio_en": "Ningun pais lo exige por ley; es el estandar voluntario mas usado en el mundo.",
        "ojo_con": "Se puede reportar 'de conformidad con' (nueve requisitos, incluido el indice de contenidos) "
                   "o 'con referencia a' (tres requisitos). Lo segundo es un buen primer paso.",
    },
    "NIIF S1": {
        "nombre_largo": "NIIF S1 - Requisitos generales de informacion financiera sobre sostenibilidad (ISSB)",
        "para_quien": "Inversionistas, bancos, aseguradoras y reguladores de valores.",
        "cuando_usarlo": "Cuando quien pide la informacion quiere saber como la sostenibilidad puede afectar "
                         "la plata de la empresa: sus flujos, su financiamiento y su costo de capital.",
        "mira": "Materialidad financiera: riesgos y oportunidades que afectan el valor de la empresa.",
        "obligatorio_en": "Aplica a periodos anuales que comienzan desde el 1-ene-2024. En Chile la CMF lo hizo "
                          "obligatorio por la NCG 519, con vigencia movida por la NCG 572 a las memorias del "
                          "ano 2027.",
        "ojo_con": "Exige una declaracion explicita de cumplimiento; si no se cumple todo, hay que decir que es "
                   "aplicacion parcial y que quedo fuera.",
    },
    "NIIF S2": {
        "nombre_largo": "NIIF S2 - Informacion a revelar sobre clima (ISSB)",
        "para_quien": "Inversionistas, bancos, aseguradoras y reguladores de valores.",
        "cuando_usarlo": "Es la parte climatica de NIIF S1 y se aplican juntas. Es el marco que pide la CMF "
                         "en Chile y el que absorbio las recomendaciones del TCFD.",
        "mira": "Riesgos y oportunidades del clima con efecto financiero, mas las emisiones de los tres alcances.",
        "obligatorio_en": "Periodos anuales que comienzan desde el 1-ene-2024. En Chile, memorias del ano 2027 "
                          "(NCG 519 con la prorroga de la NCG 572).",
        "ojo_con": "Las emisiones se miden con el GHG Protocol y el alcance 2 se informa por ubicacion. En el "
                   "primer ano de aplicacion no se exige alcance 3.",
    },
    "NCG 461": {
        "nombre_largo": "NCG 461 de la CMF (Chile) - memoria anual integrada",
        "para_quien": "La Comision para el Mercado Financiero y quienes leen la memoria anual.",
        "cuando_usarlo": "Si la empresa es sociedad anonima abierta, banco, aseguradora, administradora de "
                         "fondos, bolsa u otro emisor inscrito que debe presentar memoria anual.",
        "mira": "Sostenibilidad y gobierno corporativo dentro de la memoria anual, organizados por areas.",
        "obligatorio_en": "Chile, para las entidades fiscalizadas por la CMF que presentan memoria anual, con "
                          "gradualidad por tamano desde el ejercicio 2022.",
        "ojo_con": "La NCG 519 no reemplaza a la NCG 461: la modifica. La memoria sigue la estructura de la "
                   "NCG 30 con el contenido de sostenibilidad de la NCG 461.",
    },
    "NCG 519": {
        "nombre_largo": "NCG 519 de la CMF (Chile) - adopcion de NIIF S1 y S2",
        "para_quien": "La Comision para el Mercado Financiero.",
        "cuando_usarlo": "Junto con la NCG 461, si la empresa esta supervisada por la CMF. Marca cuando y como "
                         "hay que reportar bajo NIIF S1 y S2.",
        "mira": "Que se incorpore la informacion de NIIF S1 y S2 a la memoria, mas exigencias de gobierno.",
        "obligatorio_en": "Chile. La NCG 572, de julio de 2026, movio la vigencia al 31-dic-2027: primer reporte "
                          "obligatorio sobre el ejercicio 2027, publicado en 2028.",
        "ojo_con": "Se puede adoptar antes de forma voluntaria, declarandolo de manera expresa. Las entidades "
                   "con activos consolidados promedio de hasta 1.000.000 de unidades de fomento tienen "
                   "exigencias reducidas.",
    },
    "ESRS": {
        "nombre_largo": "ESRS - normas europeas de informacion de sostenibilidad",
        "para_quien": "Autoridades europeas, inversionistas y clientes grandes de la Union Europea.",
        "cuando_usarlo": "Si la empresa esta dentro del ambito de la CSRD en la UE, o si una matriz europea le "
                         "pide datos para su propio reporte.",
        "mira": "Doble materialidad: el efecto de la empresa sobre el entorno y el efecto del entorno sobre "
                "la empresa. Basta que una de las dos vias sea material.",
        "obligatorio_en": "Union Europea. Con la Directiva (UE) 2026/470 el umbral subio a mas de 1.000 "
                          "empleados y mas de 450 millones de euros de facturacion, aplicable a ejercicios "
                          "iniciados desde el 1-ene-2027.",
        "ojo_con": "Una pyme de Chile o Peru casi nunca esta obligada: lo que si le llega son cuestionarios de "
                   "su cliente europeo. Para eso conviene el VSME.",
    },
    "VSME": {
        "nombre_largo": "VSME - norma voluntaria europea para pymes",
        "para_quien": "Bancos y clientes grandes que mandan cuestionarios de sostenibilidad.",
        "cuando_usarlo": "Es el mejor punto de partida para una pyme que exporta o que le vende a una empresa "
                         "grande: responde con una sola estructura reconocida en Europa.",
        "mira": "Un modulo basico (B1 a B11) y uno comprehensivo (C1 a C9) con lo minimo que suelen preguntar.",
        "obligatorio_en": "Nadie lo exige: es una recomendacion de la Comision Europea, no una norma "
                          "obligatoria.",
        "ojo_con": "No pide verificacion de un tercero: basta la autodeclaracion de la pyme. Reportar el modulo "
                   "basico es requisito para reportar el comprehensivo.",
    },
}


def _clave(texto):
    """Normaliza un nombre de marco para poder compararlo: 'NIIF S2' == 'niif-s2'."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", texto)


def _lista(texto):
    return [parte.strip() for parte in str(texto or "").split(";") if parte.strip()]


def cargar_contenidos(ruta=None):
    """Lee el catalogo de contenidos por marco."""
    ruta = ruta or ARCHIVO_MARCOS
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro el catalogo de marcos de reporte (%s)." % os.path.basename(ruta),
            "Sin ese archivo no puedo decirte que pide cada marco. Avisa para reinstalar los datos del motor.",
        )
    contenidos = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for numero, fila in enumerate(csv.DictReader(archivo), start=2):
            marco = (fila.get("marco") or "").strip()
            codigo = (fila.get("codigo") or "").strip()
            if not marco or not codigo:
                continue
            contenidos.append({
                "marco": marco,
                "marco_clave": _clave(marco),
                "codigo": codigo,
                "titulo": (fila.get("titulo") or "").strip(),
                "dimension": (fila.get("dimension") or "general").strip().lower(),
                "obligatorio": (fila.get("obligatorio") or "").strip().lower(),
                "dato_fuente": _lista(fila.get("dato_fuente")),
                "descripcion": (fila.get("descripcion") or "").strip(),
                "fuente": (fila.get("fuente") or "").strip(),
                "url": (fila.get("url") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
                "linea": numero,
            })
    if not contenidos:
        raise Problema(
            "El catalogo de marcos de reporte esta vacio.",
            "Avisa para reinstalar los datos del motor: sin contenidos no puedo armar ningun reporte.",
        )
    return contenidos


def nombres_de_marcos(ruta=None):
    """Nombres de los marcos del catalogo, en el orden en que aparecen."""
    nombres = []
    for contenido in cargar_contenidos(ruta):
        if contenido["marco"] not in nombres:
            nombres.append(contenido["marco"])
    return nombres


def resolver_marco(marco, ruta=None):
    """Devuelve el nombre exacto del marco aceptando mayusculas, guiones y espacios."""
    nombres = nombres_de_marcos(ruta)
    buscado = _clave(marco)
    if not buscado:
        raise Problema(
            "No me dijiste con que marco de reporte quieres trabajar.",
            "Elige uno de estos: %s. Por ejemplo: --marco GRI." % ", ".join(nombres),
        )
    for nombre in nombres:
        if _clave(nombre) == buscado:
            return nombre
    raise Problema(
        "No conozco el marco de reporte «%s»." % marco,
        "Trabajo con estos: %s. Si necesitas otro, dimelo y lo revisamos antes de agregarlo." % ", ".join(nombres),
    )


def marcos_disponibles(ruta=None):
    """Lista los marcos con lo que exige cada uno y para quien sirve."""
    contenidos = cargar_contenidos(ruta)
    resumen = []
    for nombre in nombres_de_marcos(ruta):
        propios = [c for c in contenidos if c["marco"] == nombre]
        por_dimension = {}
        for contenido in propios:
            etiqueta = DIMENSIONES.get(contenido["dimension"], contenido["dimension"])
            por_dimension[etiqueta] = por_dimension.get(etiqueta, 0) + 1
        guia = GUIA_MARCOS.get(nombre, {})
        con_dato = [c for c in propios if c["dato_fuente"]]
        resumen.append({
            "marco": nombre,
            "nombre_largo": guia.get("nombre_largo", nombre),
            "para_quien": guia.get("para_quien", ""),
            "cuando_usarlo": guia.get("cuando_usarlo", ""),
            "que_mira": guia.get("mira", ""),
            "obligatorio_en": guia.get("obligatorio_en", ""),
            "ojo_con": guia.get("ojo_con", ""),
            "contenidos": len(propios),
            "se_reportan_siempre": len([c for c in propios if c["obligatorio"] == "si"]),
            "salen_de_tus_datos": len(con_dato),
            "los_redacta_la_empresa": len(propios) - len(con_dato),
            "por_dimension": por_dimension,
            "verificado_el": propios[0]["verificado_el"] if propios else "",
        })
    return resumen


def contenidos_de(marco, ruta=None):
    """Contenidos que pide un marco, en el orden del catalogo."""
    nombre = resolver_marco(marco, ruta)
    return [c for c in cargar_contenidos(ruta) if c["marco"] == nombre]


def dato_sin_marca(dato):
    """Un dato terminado en «?» es opcional: se muestra si existe, pero no hace falta para cubrir."""
    return dato[:-1] if dato.endswith("?") else dato


def _ficha(contenido, disponibles):
    todas = contenido["dato_fuente"]
    fuentes = [f for f in todas if not f.endswith("?")]
    opcionales = [dato_sin_marca(f) for f in todas if f.endswith("?")]
    encontrados = [f for f in fuentes if f in disponibles] + [f for f in opcionales if f in disponibles]
    faltan = [f for f in fuentes if f not in disponibles]
    if not fuentes:
        estado = "pendiente"
        motivo = "Lo escribe la empresa: no hay ningun dato que lo pueda responder solo."
    elif not faltan:
        estado = "cubierto"
        motivo = "Ya tienes el dato en la carpeta; falta redactarlo y darle contexto."
    elif encontrados:
        estado = "parcial"
        motivo = "Tienes una parte del dato. Falta: %s." % ", ".join(
            DATOS_CONOCIDOS.get(f, f) for f in faltan)
    else:
        estado = "pendiente"
        motivo = "Falta el dato. Necesitas: %s." % ", ".join(DATOS_CONOCIDOS.get(f, f) for f in faltan)
    ficha = dict(contenido)
    ficha["estado"] = estado
    ficha["motivo"] = motivo
    ficha["encontrados"] = encontrados
    ficha["faltan"] = faltan
    ficha["se_redacta"] = not fuentes
    return ficha


def porcentaje_cubierto(fichas):
    """Porcentaje de cobertura de un grupo de contenidos: cubierto suma 1, parcial 0,5."""
    if not fichas:
        return 0.0
    listos = len([f for f in fichas if f["estado"] == "cubierto"])
    medios = len([f for f in fichas if f["estado"] == "parcial"])
    return round((listos + medios * 0.5) / float(len(fichas)) * 100, 1)


def evaluar_cobertura(marco, datos_disponibles, ruta=None):
    """Revisa que contenidos del marco se pueden llenar con los datos que ya existen.

    datos_disponibles: nombres de datos presentes en la carpeta de la empresa
    (las claves de DATOS_CONOCIDOS). Devuelve los contenidos cubiertos, los
    parciales, los pendientes y el porcentaje de cobertura.
    """
    nombre = resolver_marco(marco, ruta)
    disponibles = set()
    for dato in (datos_disponibles or []):
        texto = str(dato).strip()
        if texto:
            disponibles.add(texto)

    fichas = [_ficha(c, disponibles) for c in contenidos_de(nombre, ruta)]
    cubiertos = [f for f in fichas if f["estado"] == "cubierto"]
    parciales = [f for f in fichas if f["estado"] == "parcial"]
    pendientes = [f for f in fichas if f["estado"] == "pendiente"]
    total = len(fichas)

    faltantes = {}
    for ficha in fichas:
        for dato in ficha["faltan"]:
            faltantes[dato] = faltantes.get(dato, 0) + 1
    ganancia = sorted(
        ({"dato": dato, "nombre": DATOS_CONOCIDOS.get(dato, dato), "contenidos_que_desbloquea": veces}
         for dato, veces in faltantes.items()),
        key=lambda x: (-x["contenidos_que_desbloquea"], x["dato"]))

    siempre = [f for f in fichas if f["obligatorio"] == "si"]
    return {
        "marco": nombre,
        "total": total,
        "contenidos": fichas,
        "cubiertos": cubiertos,
        "parciales": parciales,
        "pendientes": pendientes,
        "porcentaje_cobertura": porcentaje_cubierto(fichas),
        "porcentaje_de_lo_que_se_reporta_siempre": porcentaje_cubierto(siempre),
        "por_redactar": len([f for f in pendientes if f["se_redacta"]]),
        "por_falta_de_datos": len([f for f in pendientes if not f["se_redacta"]]),
        "datos_usados": sorted(d for d in disponibles if any(d in f["encontrados"] for f in fichas)),
        "datos_que_mas_suman": ganancia[:8],
    }


def agrupar_por_dimension(fichas):
    """Ordena los contenidos por dimension, para armar las secciones de un reporte."""
    grupos = []
    vistas = [d for d in ORDEN_DIMENSIONES if any(f["dimension"] == d for f in fichas)]
    for dimension in vistas:
        grupos.append({
            "dimension": dimension,
            "titulo": DIMENSIONES.get(dimension, dimension),
            "contenidos": [f for f in fichas if f["dimension"] == dimension],
        })
    otras = [f for f in fichas if f["dimension"] not in ORDEN_DIMENSIONES]
    if otras:
        grupos.append({"dimension": "otros", "titulo": "Otros contenidos", "contenidos": otras})
    return grupos
