# -*- coding: utf-8 -*-
"""Alta y consulta del perfil de una empresa."""

import json
import os

from nucleo import espacio
from nucleo.salida import Problema, Respuesta

AYUDA = "Registra una empresa, muestra su perfil o lista las empresas de esta carpeta."

CAMPOS_SIMPLES = [
    "nombre", "razon_social", "identificador_tributario", "pais", "sector", "tamano",
    "trabajadores", "ingresos_anuales", "moneda", "anio_base", "periodo_actual", "notas", "carpeta",
]


def _datos_de(opciones):
    """Junta lo que viene por --datos archivo.json con las opciones sueltas."""
    datos = {}
    archivo = opciones.get("datos")
    if archivo and archivo is not True:
        if not os.path.isfile(archivo):
            raise Problema(
                "No encontre el archivo con los datos de la empresa: %s" % archivo,
                "Revisa la ruta o entrega los datos con opciones sueltas (--nombre, --pais, ...).",
            )
        with open(archivo, encoding="utf-8") as origen:
            try:
                datos = json.load(origen)
            except ValueError as error:
                raise Problema(
                    "El archivo %s no tiene un JSON valido (%s)." % (os.path.basename(archivo), error),
                    "Revisa comas y comillas, o entrega los datos con opciones sueltas.",
                )
    for campo in CAMPOS_SIMPLES:
        if campo in opciones and opciones[campo] is not True:
            datos[campo] = opciones[campo]
    for campo in ("trabajadores", "anio_base"):
        if isinstance(datos.get(campo), str) and datos[campo].strip().isdigit():
            datos[campo] = int(datos[campo])
    if isinstance(datos.get("marcos"), str):
        datos["marcos"] = [m.strip() for m in datos["marcos"].split(",") if m.strip()]
    if isinstance(datos.get("exporta_a_ue"), str):
        datos["exporta_a_ue"] = datos["exporta_a_ue"].strip().lower() in ("si", "sí", "true", "1", "y")
    return datos


def crear(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    perfil, ruta, advertencias = espacio.crear_empresa(_datos_de(opciones), raiz=raiz)
    siguientes = [
        "Revisar el perfil y agregar los sitios o instalaciones.",
        "Crear las plantillas de datos (motor: plantilla crear).",
        "Revisar que normas le aplican a la empresa.",
    ]
    return Respuesta(
        {
            "mensaje": "Empresa «%s» registrada en empresas/%s." % (perfil["nombre"], perfil["carpeta"]),
            "carpeta": perfil["carpeta"],
            "ruta": ruta,
            "perfil": perfil,
            "siguientes_pasos": siguientes,
        },
        advertencias=advertencias,
    )


def ver(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    conteos = {}
    for carpeta in espacio.CARPETAS:
        destino = os.path.join(ruta, carpeta)
        conteos[carpeta] = len(os.listdir(destino)) if os.path.isdir(destino) else 0
    return {"perfil": perfil, "ruta": ruta, "archivos_por_carpeta": conteos}


def listar(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    empresas = espacio.listar_empresas(raiz=raiz)
    return {
        "total": len(empresas),
        "empresas": empresas,
        "mensaje": "No hay empresas registradas todavia." if not empresas
        else "Hay %d empresa(s) registrada(s)." % len(empresas),
    }


def actualizar(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    cambios = _datos_de(opciones)
    cambios.pop("carpeta", None)
    if not cambios:
        raise Problema(
            "No indicaste que cambiar del perfil.",
            "Por ejemplo: --sector Agroindustria --trabajadores 45 --anio-base 2025.",
        )
    perfil.update(cambios)
    espacio._validar(perfil)
    if cambios.get("nombre"):
        perfil.setdefault("marca", {})["nombre"] = cambios["nombre"]
    espacio.guardar_empresa(perfil, ruta)
    return {
        "mensaje": "Perfil actualizado: %s." % ", ".join(sorted(cambios)),
        "perfil": perfil,
        "ruta": ruta,
    }


ACCIONES = {"crear": crear, "ver": ver, "listar": listar, "actualizar": actualizar}
