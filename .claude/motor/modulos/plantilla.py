# -*- coding: utf-8 -*-
"""Creacion de las plantillas Excel que la persona llena con sus datos."""

import os

from nucleo import espacio, excel
from nucleo.salida import Problema
from plantillas import definiciones

AYUDA = "Crea en Excel las plantillas de datos (sitios, personas, ...) y lista las disponibles."


def listar(opciones):
    disponibles = definiciones.listar()
    return {
        "total": len(disponibles),
        "plantillas": disponibles,
        "mensaje": "Puedes crear cualquiera de estas plantillas con: plantilla crear --tipo <tipo>.",
    }


def crear(opciones):
    tipo = opciones.get("tipo")
    if not tipo or tipo is True:
        raise Problema(
            "Falta indicar que plantilla crear.",
            "Tipos disponibles: %s." % ", ".join(d["tipo"] for d in definiciones.listar()),
        )
    clave, definicion = definiciones.obtener(tipo)
    if not definicion:
        raise Problema(
            "No tengo una plantilla llamada «%s»." % tipo,
            "Tipos disponibles: %s." % ", ".join(d["tipo"] for d in definiciones.listar()),
        )

    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    destino = opciones.get("salida") if opciones.get("salida") is not True else None
    if destino:
        ruta = os.path.abspath(destino)
        nombre_empresa = None
    else:
        perfil, ruta_empresa = espacio.cargar_empresa(identificador, raiz=raiz)
        nombre_empresa = perfil.get("nombre")
        ruta = espacio.ruta_de(ruta_empresa, "datos", "%s.xlsx" % clave)

    if os.path.exists(ruta) and not opciones.get("sobrescribir"):
        raise Problema(
            "Ya existe la planilla %s y no la voy a sobrescribir." % os.path.basename(ruta),
            "Si quieres empezar de cero, dime que la reemplace; si ya tiene datos, la puedo leer tal como esta.",
            {"ruta": ruta},
        )

    con_ejemplo = not opciones.get("sin_ejemplo")
    excel.escribir_xlsx(ruta, definiciones.hojas_de(definicion, con_ejemplo=con_ejemplo))
    return {
        "mensaje": "Planilla «%s» creada." % definicion["titulo"],
        "tipo": clave,
        "archivo": ruta,
        "empresa": nombre_empresa,
        "columnas": [c["titulo"] for c in definicion["columnas"]],
        "instrucciones": "Abrela en Excel, reemplaza las filas de ejemplo por tus datos y guarda el archivo.",
    }


ACCIONES = {"listar": listar, "crear": crear}
