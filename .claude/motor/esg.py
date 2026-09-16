# -*- coding: utf-8 -*-
"""Motor de cálculo de Agentes ESG.

Uso:
    python esg.py <módulo> <acción> [--opción valor ...]
    python esg.py --ayuda

Siempre imprime JSON:
    éxito -> {"ok": true, "resultado": ..., "advertencias": [...], "fuentes": [...]}
    error -> {"ok": false, "error": "...", "sugerencia": "...", "detalle": {...}}
"""

import importlib
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from nucleo.salida import Problema, ejecutar, exito  # noqa: E402

CARPETA_MODULOS = os.path.join(RAIZ, "modulos")


def modulos_disponibles():
    """Nombres de módulos instalados, en orden alfabético."""
    nombres = []
    for archivo in sorted(os.listdir(CARPETA_MODULOS)):
        if archivo.endswith(".py") and not archivo.startswith("_"):
            nombres.append(archivo[:-3])
    return nombres


def cargar_modulo(nombre):
    if nombre not in modulos_disponibles():
        raise Problema(
            "No conozco el módulo «%s»." % nombre,
            "Módulos disponibles: %s." % ", ".join(modulos_disponibles()),
        )
    return importlib.import_module("modulos.%s" % nombre)


def parsear(argumentos):
    """Convierte la línea de comandos en (módulo, acción, opciones)."""
    posicionales = []
    opciones = {}
    i = 0
    while i < len(argumentos):
        pieza = argumentos[i]
        if pieza.startswith("--"):
            clave = pieza[2:].replace("-", "_")
            if i + 1 < len(argumentos) and not argumentos[i + 1].startswith("--"):
                opciones[clave] = argumentos[i + 1]
                i += 2
            else:
                opciones[clave] = True
                i += 1
        else:
            posicionales.append(pieza)
            i += 1
    modulo = posicionales[0] if posicionales else None
    accion = posicionales[1] if len(posicionales) > 1 else None
    opciones["_extra"] = posicionales[2:]
    return modulo, accion, opciones


def ayuda_general():
    catalogo = {}
    for nombre in modulos_disponibles():
        modulo = importlib.import_module("modulos.%s" % nombre)
        catalogo[nombre] = {
            "descripcion": getattr(modulo, "AYUDA", "").strip(),
            "acciones": sorted(getattr(modulo, "ACCIONES", {}).keys()),
        }
    return {
        "uso": "python esg.py <módulo> <acción> [--opción valor ...]",
        "modulos": catalogo,
    }


def despachar(argumentos):
    modulo_nombre, accion_nombre, opciones = parsear(argumentos)

    if not modulo_nombre or modulo_nombre in ("--ayuda", "ayuda", "-h", "--help"):
        return ayuda_general()

    modulo = cargar_modulo(modulo_nombre)
    acciones = getattr(modulo, "ACCIONES", {})

    if not accion_nombre:
        raise Problema(
            "Falta indicar qué acción quieres del módulo «%s»." % modulo_nombre,
            "Acciones disponibles: %s." % ", ".join(sorted(acciones)),
        )
    if accion_nombre not in acciones:
        raise Problema(
            "El módulo «%s» no tiene la acción «%s»." % (modulo_nombre, accion_nombre),
            "Acciones disponibles: %s." % ", ".join(sorted(acciones)),
        )
    return acciones[accion_nombre](opciones)


def principal(argumentos=None):
    if argumentos is None:
        argumentos = sys.argv[1:]
    if argumentos and argumentos[0] in ("--ayuda", "-h", "--help"):
        return exito(ayuda_general())
    return ejecutar(despachar, argumentos)


if __name__ == "__main__":
    sys.exit(principal())
