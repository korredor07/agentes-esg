# -*- coding: utf-8 -*-
"""Boveda de evidencias: respaldos con huella SHA-256 encadenada."""

import os

from nucleo import espacio, evidencias
from nucleo.salida import Problema, Respuesta

AYUDA = "Registra respaldos (boletas, planillas, informes) y verifica que no hayan cambiado."

AVISO = ("La cadena de huellas prueba integridad y orden, no identidad legal: "
         "no reemplaza una firma electronica avanzada ni un sellado de tiempo acreditado.")


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "evidencias")


def registrar(opciones):
    perfil, ruta_empresa, carpeta = _contexto(opciones)
    archivo = opciones.get("archivo")
    if not archivo or archivo is True:
        raise Problema(
            "Falta el archivo que quieres respaldar.",
            "Indica su ruta, por ejemplo: --archivo empresas/mi-empresa/datos/consumos.xlsx",
        )
    if not os.path.isabs(archivo) and not os.path.isfile(archivo):
        candidato = os.path.join(ruta_empresa, archivo)
        if os.path.isfile(candidato):
            archivo = candidato
    entrada = evidencias.registrar(
        carpeta, archivo,
        descripcion=opciones.get("descripcion") if opciones.get("descripcion") is not True else "",
        tipo=opciones.get("tipo") if opciones.get("tipo") is not True else "documento",
        responsable=opciones.get("responsable") if opciones.get("responsable") is not True else "",
        base=ruta_empresa,
    )
    return Respuesta(
        {
            "mensaje": "Respaldo registrado con el numero %d." % entrada["n"],
            "entrada": entrada,
            "empresa": perfil.get("nombre"),
        },
        advertencias=[AVISO],
    )


def verificar(opciones):
    perfil, ruta_empresa, carpeta = _contexto(opciones)
    resultado = evidencias.verificar(carpeta, base=ruta_empresa)
    return Respuesta(
        dict(resultado, empresa=perfil.get("nombre")),
        advertencias=[] if resultado["ok"] else ["Revisa los problemas antes de usar estas evidencias en una auditoria."],
    )


def listar(opciones):
    perfil, _, carpeta = _contexto(opciones)
    listado = evidencias.listar(carpeta)
    return {
        "empresa": perfil.get("nombre"),
        "total": len(listado),
        "evidencias": listado,
        "mensaje": "Sin respaldos registrados todavia." if not listado
        else "Hay %d respaldo(s) registrados." % len(listado),
    }


ACCIONES = {"registrar": registrar, "verificar": verificar, "listar": listar}
