# -*- coding: utf-8 -*-
"""Resultados guardados en resultados/: cual usar y si todavia sirven.

Un resultado guardado por una version anterior del motor puede omitir advertencias o
venir de reglas que ya se corrigieron, y uno de otro periodo pone cifras de otro año en
un documento. Quien arma un informe usa estas dos funciones para no hacerlo en silencio.
"""

import glob
import os
import re

# Sube cuando cambia lo que guarda un calculo o como se calcula.
VERSIONES = {"huella": 2, "agua": 2, "social": 2}


def es_vigente(datos, tipo):
    """Si el resultado lo guardo la version actual del calculo."""
    return (datos or {}).get("version_calculo") == VERSIONES[tipo]


def elegir(ruta_empresa, prefijo, periodo=None):
    """Elige resultados/<prefijo>_<periodo>.json. Devuelve (ruta o None, aviso o None).

    Con periodo, solo sirve el de ese periodo. Sin periodo, el del periodo mas reciente;
    el acumulado («completa» o «completo») solo si no hay ninguno por periodo.
    """
    rutas = sorted(glob.glob(os.path.join(ruta_empresa, "resultados", "%s_*.json" % prefijo)))
    if not rutas:
        return None, None
    por_nombre = {os.path.basename(ruta)[len(prefijo) + 1:-len(".json")]: ruta for ruta in rutas}
    if periodo:
        if str(periodo) in por_nombre:
            return por_nombre[str(periodo)], None
        return None, ("No hay un calculo de %s del periodo %s (hay: %s). Para usarlo, calculalo con: %s calcular "
                      "--periodo %s." % (prefijo, periodo, ", ".join(sorted(por_nombre)), prefijo, periodo))
    con_periodo = sorted(nombre for nombre in por_nombre if re.match(r"^\d{4}(-\d{2})?$", nombre))
    if con_periodo:
        return por_nombre[con_periodo[-1]], None
    return rutas[-1], None


def periodo_del_nombre(ruta, prefijo):
    """El periodo que dice el nombre del archivo, o None si es el acumulado."""
    nombre = os.path.basename(ruta)[len(prefijo) + 1:-len(".json")]
    return nombre if re.match(r"^\d{4}(-\d{2})?$", nombre) else None
