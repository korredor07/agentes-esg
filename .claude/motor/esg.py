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
import inspect
import os
import re
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
        "mensaje": "Para ver qué opciones acepta cada acción: python esg.py <módulo> --ayuda.",
    }


# Opciones que aceptan todos los módulos que trabajan sobre una empresa.
OPCIONES_COMUNES = {
    "empresa": "Qué empresa usar, cuando hay más de una registrada (el nombre o la carpeta).",
    "raiz": "Dónde está la carpeta 'empresas/'. Solo hace falta si no es la del proyecto.",
}


def _leer_opciones(fuente):
    """Las dos formas en que los modulos leen una opcion."""
    encontradas = set(re.findall(r"opciones(?:\.get\(|\[)[\"']([a-z_0-9]+)[\"']", fuente))
    encontradas |= set(re.findall(r"\(\s*opciones\s*,\s*[\"']([a-z_0-9]+)[\"']", fuente))
    return encontradas


def _opciones_de(funcion, modulo=None):
    """Lee del propio código qué opciones usa una acción.

    Se lee el código en vez de mantener una lista aparte: así la ayuda no puede
    quedar desactualizada respecto de lo que la acción realmente acepta. Sigue
    también a los ayudantes a los que la acción le pasa las opciones (como
    _contexto), porque ahí viven --empresa y --raiz.
    """
    encontradas = set()
    pendientes = [funcion]
    vistas = set()
    while pendientes:
        actual = pendientes.pop()
        if actual in vistas:
            continue
        vistas.add(actual)
        try:
            fuente = inspect.getsource(actual)
        except (OSError, TypeError):
            continue
        encontradas |= _leer_opciones(fuente)
        # Cualquier funcion del mismo modulo que reciba las opciones, en cualquier posicion:
        # _contexto(opciones), _correccion_para(resultado, opciones, ...) o relaves(opciones).
        for llamada in set(re.findall(r"\b([a-z_][a-z_0-9]*)\((?:[^()]|\([^()]*\))*?\bopciones\b", fuente)):
            destino = getattr(modulo, llamada, None)
            if (inspect.isfunction(destino) and destino.__module__ == getattr(modulo, "__name__", None)
                    and destino not in vistas):
                pendientes.append(destino)
    encontradas.discard("_extra")
    # Opciones que el modulo lee recorriendo una lista (por ejemplo, las preguntas de europa aplica).
    dinamicas = getattr(modulo, "OPCIONES_DINAMICAS", {}) or {}
    for accion, funcion_accion in (getattr(modulo, "ACCIONES", {}) or {}).items():
        if funcion_accion is funcion:
            encontradas |= set(dinamicas.get(accion, []))
    return sorted(encontradas)


def ayuda_de_modulo(nombre):
    """Qué hace cada acción de un módulo y qué opciones acepta."""
    modulo = cargar_modulo(nombre)
    acciones = {}
    for accion, funcion in sorted(getattr(modulo, "ACCIONES", {}).items()):
        opciones = _opciones_de(funcion, modulo)
        acciones[accion] = {
            "que_hace": (inspect.getdoc(funcion) or "").split("\n\n")[0].strip(),
            "opciones": ["--%s" % o.replace("_", "-") for o in opciones],
            "explicacion": {"--%s" % o.replace("_", "-"): OPCIONES_COMUNES[o]
                            for o in opciones if o in OPCIONES_COMUNES},
        }
    return {
        "modulo": nombre,
        "para_que_sirve": getattr(modulo, "AYUDA", "").strip(),
        "uso": "python esg.py %s <acción> [--opción valor ...]" % nombre,
        "acciones": acciones,
        "nota": "Las opciones salen del código de cada acción. Una opción sin valor se entiende como sí "
                "(por ejemplo --corregir). Los valores con espacios van entre comillas.",
    }


def despachar(argumentos):
    modulo_nombre, accion_nombre, opciones = parsear(argumentos)

    if not modulo_nombre or modulo_nombre in ("--ayuda", "ayuda", "-h", "--help"):
        return ayuda_general()

    if opciones.get("ayuda") or accion_nombre in ("ayuda", "--ayuda"):
        return ayuda_de_modulo(modulo_nombre)

    modulo = cargar_modulo(modulo_nombre)
    acciones = getattr(modulo, "ACCIONES", {})

    if not accion_nombre:
        raise Problema(
            "Falta indicar qué acción quieres del módulo «%s»." % modulo_nombre,
            "Acciones disponibles: %s. Para ver qué opciones acepta cada una: "
            "python esg.py %s --ayuda." % (", ".join(sorted(acciones)), modulo_nombre),
        )
    if accion_nombre not in acciones:
        raise Problema(
            "El módulo «%s» no tiene la acción «%s»." % (modulo_nombre, accion_nombre),
            "Acciones disponibles: %s. Para ver qué opciones acepta cada una: "
            "python esg.py %s --ayuda." % (", ".join(sorted(acciones)), modulo_nombre),
        )
    sobrante = opciones.get("_extra") or []
    if sobrante:
        # --contra-representante no se, sin comillas, se leia como «no» y «se» se perdia sin aviso.
        raise Problema(
            "No entendi «%s»: sobra en el comando." % " ".join(str(p) for p in sobrante),
            "Los valores con espacios van entre comillas, por ejemplo: --contra-representante \"no se\".",
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
