# -*- coding: utf-8 -*-
"""Revision del sistema: comprueba que todo lo necesario este en su lugar."""

import os
import platform
import sys

from nucleo.salida import Respuesta

AYUDA = "Comprueba que el motor, los datos y los permisos esten bien para trabajar."

RAIZ_MOTOR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATOS = os.path.join(RAIZ_MOTOR, "datos")

ARCHIVOS_ESPERADOS = {
    "factores_emision.csv": "factores de emision para la huella de carbono",
    "pcg.csv": "potenciales de calentamiento global",
    "feriados_chile.csv": "feriados de Chile para los plazos legales",
    "calendario_cl.csv": "calendario de obligaciones de Chile",
}


def _revisar_python():
    version = sys.version_info
    suficiente = version >= (3, 9)
    return {
        "punto": "Version de Python",
        "estado": "ok" if suficiente else "problema",
        "detalle": "Python %d.%d.%d%s" % (version.major, version.minor, version.micro,
                                          "" if suficiente else " (se necesita 3.9 o superior)"),
    }


def _revisar_datos():
    revisiones = []
    for nombre, descripcion in sorted(ARCHIVOS_ESPERADOS.items()):
        ruta = os.path.join(CARPETA_DATOS, nombre)
        existe = os.path.isfile(ruta)
        filas = 0
        if existe:
            with open(ruta, encoding="utf-8-sig") as archivo:
                filas = max(sum(1 for _ in archivo) - 1, 0)
        revisiones.append({
            "punto": "Datos: %s" % descripcion,
            "estado": "ok" if existe and filas else "problema",
            "detalle": ("%d registros cargados" % filas) if existe else
                       "Falta el archivo %s. Vuelve a descargar la carpeta del proyecto." % nombre,
        })
    return revisiones


def _revisar_calculo():
    try:
        from calculos import carbono
        factores = carbono.cargar_factores()
        pcg = carbono.cargar_pcg()
        prueba = carbono.calcular_registro(
            {"_fila": 1, "periodo": "2024", "recurso": "electricidad", "cantidad": 1000,
             "unidad": "kWh", "pais": "CL"}, factores, pcg, "AR5")
        correcto = abs(prueba["kg_co2e"] - 213.14) < 1.0
        return {
            "punto": "Calculo de prueba",
            "estado": "ok" if correcto else "problema",
            "detalle": ("1.000 kWh en Chile (2024) dan %.1f kg CO2e: el motor calcula bien."
                        % prueba["kg_co2e"]) if correcto else
                       "El calculo de prueba dio %.1f kg CO2e y deberia dar cerca de 213." % prueba["kg_co2e"],
        }
    except Exception as error:  # el motor debe seguir respondiendo aunque esto falle
        return {"punto": "Calculo de prueba", "estado": "problema",
                "detalle": "No se pudo completar: %s" % error}


def _revisar_escritura(carpeta):
    prueba = os.path.join(carpeta, ".permiso_de_escritura")
    try:
        with open(prueba, "w", encoding="utf-8") as archivo:
            archivo.write("ok")
        os.remove(prueba)
        return {"punto": "Permisos de escritura", "estado": "ok",
                "detalle": "Se pueden guardar archivos en %s" % carpeta}
    except OSError as error:
        return {"punto": "Permisos de escritura", "estado": "problema",
                "detalle": ("No puedo guardar archivos en %s (%s). Prueba copiando la carpeta a "
                            "Documentos o al Escritorio." % (carpeta, error))}


def sistema(opciones):
    """Revisa que el motor este completo y bien instalado en este computador."""
    carpeta = os.path.abspath(opciones.get("carpeta") if opciones.get("carpeta") not in (None, True)
                              else os.getcwd())
    revisiones = [_revisar_python()]
    revisiones.extend(_revisar_datos())
    revisiones.append(_revisar_calculo())
    revisiones.append(_revisar_escritura(carpeta))

    problemas = [r for r in revisiones if r["estado"] != "ok"]
    return Respuesta(
        {
            "sistema": "%s %s" % (platform.system(), platform.release()),
            "carpeta_de_trabajo": carpeta,
            "revisiones": revisiones,
            "todo_en_orden": not problemas,
            "mensaje": ("Todo en orden: el motor esta listo para trabajar." if not problemas else
                        "Hay %d cosa(s) por resolver antes de trabajar tranquilo." % len(problemas)),
        },
        advertencias=[r["detalle"] for r in problemas])


ACCIONES = {"sistema": sistema}
