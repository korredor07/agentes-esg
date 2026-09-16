# -*- coding: utf-8 -*-
"""Módulo de diagnóstico: confirma que el motor funciona."""

import platform
import sys

AYUDA = "Comprueba que el motor de cálculo funciona y muestra su versión."
VERSION = "0.1.0"


def mostrar(opciones):
    """Muestra la version del motor y datos del computador, para soporte."""
    return {
        "motor": "Agentes ESG",
        "version": VERSION,
        "python": sys.version.split()[0],
        "sistema": platform.system(),
        "mensaje": "El motor de cálculo está funcionando correctamente.",
    }


ACCIONES = {"mostrar": mostrar}
