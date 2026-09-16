# -*- coding: utf-8 -*-
"""Carpeta de trabajo de cada empresa.

Todo lo de una empresa vive en una carpeta propia dentro de 'empresas/':

    empresas/mi-empresa/
        empresa.json      perfil (quien es, donde opera, que marcos usa)
        datos/            planillas Excel y documentos que carga la persona
        resultados/       resultados de calculos en JSON
        reportes/         entregables (Word, Excel, HTML)
        evidencias/       registro de respaldos con huella SHA-256
        seguimiento/      brechas, casos y metas en curso
"""

import datetime
import json
import os
import re
import unicodedata

from .salida import Problema

CARPETAS = ["datos", "resultados", "reportes", "evidencias", "seguimiento"]
VERSION_ESQUEMA = 1

PAISES = {
    "CL": "Chile", "PE": "Perú", "AR": "Argentina", "CO": "Colombia", "MX": "México",
    "BR": "Brasil", "ES": "España", "UY": "Uruguay", "EC": "Ecuador", "BO": "Bolivia",
    "PY": "Paraguay", "CR": "Costa Rica", "PA": "Panamá", "US": "Estados Unidos",
}
TAMANOS = ["micro", "pequena", "mediana", "grande"]
MARCOS = ["GRI", "NIIF S1/S2", "CSRD/ESRS", "VSME", "TCFD", "SASB", "NCG 519", "HuellaChile", "ISO 14064"]


def texto_a_slug(texto):
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto[:60] or "empresa"


def carpeta_empresas(raiz=None):
    return os.path.join(os.path.abspath(raiz or os.getcwd()), "empresas")


def _ahora():
    return datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _validar(datos):
    """Revisa el perfil y devuelve la lista de advertencias."""
    advertencias = []
    nombre = str(datos.get("nombre", "")).strip()
    if not nombre:
        raise Problema(
            "Falta el nombre de la empresa.",
            "Dime como se llama la empresa (por ejemplo: Alimentos del Sur SpA).",
        )
    pais = str(datos.get("pais", "")).strip().upper()
    if pais and pais not in PAISES:
        raise Problema(
            "No reconozco el pais «%s»." % datos.get("pais"),
            "Usa el codigo de dos letras: %s." % ", ".join(sorted(PAISES)),
        )
    if not pais:
        advertencias.append("No indicaste el pais: se asumio Chile (CL). Puedes cambiarlo cuando quieras.")
    tamano = str(datos.get("tamano", "")).strip().lower()
    if tamano and tamano not in TAMANOS:
        raise Problema(
            "El tamaño «%s» no es valido." % datos.get("tamano"),
            "Usa uno de estos: %s." % ", ".join(TAMANOS),
        )
    anio = datos.get("anio_base")
    if anio not in (None, ""):
        try:
            anio = int(anio)
        except (TypeError, ValueError):
            raise Problema("El año base «%s» no es un año valido." % datos.get("anio_base"),
                           "Escribe solo el año, por ejemplo 2025.")
        if anio < 1990 or anio > 2100:
            raise Problema("El año base %d esta fuera de rango." % anio,
                           "Usa un año entre 1990 y 2100.")
    return advertencias


def perfil_nuevo(datos):
    """Completa el perfil con valores por defecto sensatos."""
    advertencias = _validar(datos)
    pais = str(datos.get("pais", "CL")).strip().upper() or "CL"
    anio = datos.get("anio_base")
    perfil = {
        "version_esquema": VERSION_ESQUEMA,
        "nombre": str(datos.get("nombre", "")).strip(),
        "razon_social": str(datos.get("razon_social", "") or "").strip(),
        "identificador_tributario": str(datos.get("identificador_tributario", "") or "").strip(),
        "pais": pais,
        "sector": str(datos.get("sector", "") or "").strip(),
        "tamano": str(datos.get("tamano", "") or "").strip().lower(),
        "trabajadores": datos.get("trabajadores"),
        "ingresos_anuales": datos.get("ingresos_anuales"),
        "moneda": str(datos.get("moneda", "") or ("CLP" if pais == "CL" else "USD")).upper(),
        "anio_base": int(anio) if anio not in (None, "") else datetime.date.today().year - 1,
        "periodo_actual": str(datos.get("periodo_actual", "") or datetime.date.today().year),
        "marcos": list(datos.get("marcos") or []),
        "exporta_a_ue": bool(datos.get("exporta_a_ue", False)),
        "sitios": list(datos.get("sitios") or []),
        "entidades_legales": list(datos.get("entidades_legales") or []),
        "marca": {
            "nombre": str(datos.get("nombre", "")).strip(),
            "color_primario": "#1B4332",
            "color_secundario": "#D8F3DC",
        },
        "notas": str(datos.get("notas", "") or ""),
        "creado_el": _ahora(),
        "actualizado_el": _ahora(),
    }
    if isinstance(datos.get("marca"), dict):
        perfil["marca"].update(datos["marca"])
    return perfil, advertencias


def crear_empresa(datos, raiz=None):
    """Crea la carpeta de la empresa y su perfil. Devuelve (perfil, ruta, advertencias)."""
    perfil, advertencias = perfil_nuevo(datos)
    base = carpeta_empresas(raiz)
    slug = texto_a_slug(datos.get("carpeta") or perfil["nombre"])
    ruta = os.path.join(base, slug)
    if os.path.exists(os.path.join(ruta, "empresa.json")):
        raise Problema(
            "Ya existe una empresa registrada en «empresas/%s»." % slug,
            "Si quieres trabajar con ella, pideme que la abra. Si es otra empresa, usa un nombre distinto.",
        )
    for carpeta in [ruta] + [os.path.join(ruta, c) for c in CARPETAS]:
        if not os.path.isdir(carpeta):
            os.makedirs(carpeta)
    perfil["carpeta"] = slug
    guardar_empresa(perfil, ruta)
    return perfil, ruta, advertencias


def guardar_empresa(perfil, ruta):
    perfil["actualizado_el"] = _ahora()
    destino = os.path.join(ruta, "empresa.json")
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(perfil, archivo, ensure_ascii=False, indent=2)
    return destino


def listar_empresas(raiz=None):
    base = carpeta_empresas(raiz)
    empresas = []
    if not os.path.isdir(base):
        return empresas
    for nombre in sorted(os.listdir(base)):
        ruta = os.path.join(base, nombre)
        perfil_json = os.path.join(ruta, "empresa.json")
        if os.path.isfile(perfil_json):
            try:
                with open(perfil_json, encoding="utf-8") as archivo:
                    perfil = json.load(archivo)
            except ValueError:
                continue
            empresas.append({
                "carpeta": nombre,
                "nombre": perfil.get("nombre", nombre),
                "pais": perfil.get("pais", ""),
                "periodo_actual": perfil.get("periodo_actual", ""),
                "ruta": ruta,
            })
    return empresas


def resolver_ruta(identificador, raiz=None):
    """Acepta una ruta, el nombre de la carpeta o el nombre de la empresa."""
    if identificador:
        candidato = os.path.abspath(str(identificador))
        if os.path.isfile(os.path.join(candidato, "empresa.json")):
            return candidato
    empresas = listar_empresas(raiz)
    if identificador:
        buscado = texto_a_slug(identificador)
        for empresa in empresas:
            if empresa["carpeta"] == buscado or texto_a_slug(empresa["nombre"]) == buscado:
                return empresa["ruta"]
        raise Problema(
            "No encontre la empresa «%s»." % identificador,
            ("Empresas registradas: %s." % ", ".join(e["nombre"] for e in empresas)) if empresas
            else "Todavia no hay ninguna empresa registrada. Puedo crear una contigo en un minuto.",
        )
    if not empresas:
        raise Problema(
            "Todavia no hay ninguna empresa registrada.",
            "Dime el nombre de tu empresa y la registro en un minuto.",
        )
    # la empresa de demostracion no compite con la empresa real de la persona
    reales = [e for e in empresas if not e["carpeta"].startswith("ejemplo-")]
    candidatas = reales or empresas
    if len(candidatas) == 1:
        return candidatas[0]["ruta"]
    raise Problema(
        "Hay varias empresas registradas y no se cual usar.",
        "Agrega la opcion --empresa con el nombre de su carpeta. Por ejemplo: --empresa %s. "
        "Disponibles: %s." % (candidatas[0]["carpeta"],
                              ", ".join("%s (%s)" % (e["carpeta"], e["nombre"]) for e in candidatas)),
    )


def cargar_empresa(identificador=None, raiz=None):
    """Devuelve (perfil, ruta) de la empresa pedida."""
    ruta = resolver_ruta(identificador, raiz)
    with open(os.path.join(ruta, "empresa.json"), encoding="utf-8") as archivo:
        try:
            perfil = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo empresa.json de «%s» esta dañado." % os.path.basename(ruta),
                "Puedo volver a crearlo contigo; solo necesito los datos basicos de la empresa.",
            )
    perfil.setdefault("carpeta", os.path.basename(ruta))
    return perfil, ruta


def ruta_de(ruta_empresa, carpeta, *partes):
    """Devuelve una ruta dentro de la carpeta de la empresa, creandola si falta."""
    if carpeta not in CARPETAS:
        raise Problema(
            "No existe la carpeta «%s» dentro de una empresa." % carpeta,
            "Carpetas disponibles: %s." % ", ".join(CARPETAS),
        )
    destino = os.path.join(ruta_empresa, carpeta)
    if not os.path.isdir(destino):
        os.makedirs(destino)
    return os.path.join(destino, *partes) if partes else destino
