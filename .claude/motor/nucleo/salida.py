# -*- coding: utf-8 -*-
"""Contrato de salida del motor: siempre JSON, siempre en español.

Todo lo que imprime el motor lo lee un agente de IA que se lo explicará a una
persona sin conocimientos técnicos. Por eso los mensajes de error describen qué
pasó y qué hacer, sin jerga.
"""

import json
import sys
import traceback


class Problema(Exception):
    """Error esperable (dato faltante, archivo mal formado, valor inválido)."""

    def __init__(self, mensaje, sugerencia="", detalle=None):
        super(Problema, self).__init__(mensaje)
        self.mensaje = mensaje
        self.sugerencia = sugerencia
        self.detalle = detalle or {}


class Respuesta(object):
    """Resultado de una acción, con advertencias y fuentes opcionales."""

    def __init__(self, resultado, advertencias=None, fuentes=None):
        self.resultado = resultado
        self.advertencias = list(advertencias or [])
        self.fuentes = list(fuentes or [])


def _preparar_consola():
    """Evita errores de acentos en la consola de Windows."""
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def _imprimir(dato):
    _preparar_consola()
    sys.stdout.write(json.dumps(dato, ensure_ascii=False, indent=2, default=str) + "\n")


def exito(resultado, advertencias=None, fuentes=None):
    _imprimir({
        "ok": True,
        "resultado": resultado,
        "advertencias": list(advertencias or []),
        "fuentes": list(fuentes or []),
    })
    return 0


def fallo(error, sugerencia="", detalle=None):
    _imprimir({
        "ok": False,
        "error": error,
        "sugerencia": sugerencia,
        "detalle": detalle or {},
    })
    return 1


def ejecutar(funcion, *args, **kwargs):
    """Ejecuta una acción y traduce cualquier error a la salida estándar."""
    try:
        salida = funcion(*args, **kwargs)
    except Problema as problema:
        return fallo(problema.mensaje, problema.sugerencia, problema.detalle)
    except FileNotFoundError as error:
        return fallo(
            "No encontré el archivo: %s" % (error.filename or error),
            "Revisa que la ruta esté bien escrita y que el archivo exista.",
        )
    except PermissionError as error:
        return fallo(
            "No pude usar el archivo %s: está abierto en otro programa o protegido." % (error.filename or error),
            "Ciérralo en Excel o Word y vuelve a intentarlo.",
        )
    except Exception as error:  # último recurso: nunca dejamos una traza cruda a la vista
        return fallo(
            "Ocurrió un error inesperado: %s" % error,
            "Cuéntale al asistente qué estabas haciendo; el detalle técnico está en 'detalle'.",
            {"tipo": type(error).__name__, "traza": traceback.format_exc(limit=4)},
        )

    if isinstance(salida, Respuesta):
        return exito(salida.resultado, salida.advertencias, salida.fuentes)
    return exito(salida)
