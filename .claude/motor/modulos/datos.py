# -*- coding: utf-8 -*-
"""Lectura y revision de los datos cargados por la empresa."""

import datetime
import os

from nucleo import espacio, excel
from nucleo.salida import Problema, Respuesta

AYUDA = "Lee las planillas cargadas, resume que hay y detecta datos raros o meses faltantes."

MESES = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _resolver_archivo(ruta_empresa, nombre):
    if os.path.isabs(nombre) and os.path.isfile(nombre):
        return nombre
    for candidato in (os.path.join(ruta_empresa, nombre),
                      os.path.join(ruta_empresa, "datos", nombre),
                      os.path.join(ruta_empresa, "datos", nombre + ".xlsx"),
                      nombre):
        if os.path.isfile(candidato):
            return candidato
    raise Problema(
        "No encontre el archivo «%s» en la carpeta de la empresa." % nombre,
        "Revisa el nombre. Puedes ver lo que hay cargado con: datos resumen.",
    )


def resumen(opciones):
    perfil, ruta = _contexto(opciones)
    carpeta = espacio.ruta_de(ruta, "datos")
    archivos = []
    for nombre in sorted(os.listdir(carpeta)):
        completa = os.path.join(carpeta, nombre)
        if not os.path.isfile(completa):
            continue
        ficha = {
            "archivo": nombre,
            "tamano_kb": round(os.path.getsize(completa) / 1024.0, 1),
            "actualizado": datetime.datetime.fromtimestamp(os.path.getmtime(completa)).strftime("%d-%m-%Y %H:%M"),
        }
        if nombre.lower().endswith(".xlsx"):
            try:
                libro = excel.leer_xlsx(completa)
                ficha["hojas"] = {hoja: max(len(filas) - 1, 0) for hoja, filas in libro.items()}
            except Problema as problema:
                ficha["problema"] = problema.mensaje
        archivos.append(ficha)
    resultados = sorted(os.listdir(espacio.ruta_de(ruta, "resultados")))
    reportes = sorted(os.listdir(espacio.ruta_de(ruta, "reportes")))
    return {
        "empresa": perfil.get("nombre"),
        "datos_cargados": archivos,
        "resultados_guardados": resultados,
        "reportes_generados": reportes,
        "mensaje": "Sin datos cargados todavia." if not archivos else
                   "Hay %d archivo(s) de datos cargados." % len(archivos),
    }


def leer(opciones):
    perfil, ruta = _contexto(opciones)
    nombre = opciones.get("archivo")
    if not nombre or nombre is True:
        raise Problema("Falta decir que archivo leer.",
                       "Por ejemplo: datos leer --archivo consumos.xlsx")
    completa = _resolver_archivo(ruta, nombre)
    hoja = opciones.get("hoja") if opciones.get("hoja") is not True else None
    limite = opciones.get("limite")
    limite = int(limite) if limite and limite is not True else 300
    tabla = excel.leer_tabla(completa, hoja=hoja)
    filas = tabla["filas"]
    return {
        "archivo": completa,
        "hoja": tabla["hoja"],
        "columnas": tabla["encabezados"],
        "total_filas": len(filas),
        "filas": filas[:limite],
        "truncado": len(filas) > limite,
    }


def _numero(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None


def anomalias(opciones):
    """Busca saltos raros y meses faltantes en los consumos cargados."""
    perfil, ruta = _contexto(opciones)
    completa = _resolver_archivo(ruta, opciones.get("archivo")
                                 if opciones.get("archivo") not in (None, True) else "consumos.xlsx")
    umbral = _numero(opciones.get("umbral")) or 50.0
    tabla = excel.leer_tabla(completa)

    series = {}
    for fila in tabla["filas"]:
        periodo = str(fila.get("periodo") or "").strip()
        cantidad = _numero(fila.get("cantidad"))
        if len(periodo) != 7 or cantidad is None:
            continue
        clave = (str(fila.get("sitio") or "sin sitio"), str(fila.get("recurso") or "sin recurso"),
                 str(fila.get("unidad") or ""))
        series.setdefault(clave, {})[periodo] = series.setdefault(clave, {}).get(periodo, 0.0) + cantidad

    hallazgos = []
    for (sitio, recurso, unidad), valores in sorted(series.items()):
        if len(valores) < 3:
            continue
        ordenados = sorted(valores.items())
        numeros = sorted(v for _, v in ordenados)
        mediana = numeros[len(numeros) // 2] if len(numeros) % 2 else \
            (numeros[len(numeros) // 2 - 1] + numeros[len(numeros) // 2]) / 2.0
        if mediana <= 0:
            continue
        for periodo, valor in ordenados:
            desvio = (valor - mediana) / mediana * 100.0
            if abs(desvio) >= umbral:
                hallazgos.append({
                    "tipo": "salto",
                    "sitio": sitio, "recurso": recurso, "periodo": periodo,
                    "valor": valor, "unidad": unidad, "mediana": round(mediana, 2),
                    "desvio_pct": round(desvio, 1),
                    "detalle": "%s en %s: %s %s, %s%% respecto a su mes tipico (%s %s)."
                               % (recurso, periodo, round(valor, 1), unidad,
                                  ("+%.0f" % desvio) if desvio > 0 else "%.0f" % desvio,
                                  round(mediana, 1), unidad),
                })
        anios = {p[:4] for p in valores}
        for anio in sorted(anios):
            faltantes = [m for m in MESES if "%s-%s" % (anio, m) not in valores]
            if faltantes and len(faltantes) < 12:
                hallazgos.append({
                    "tipo": "meses_faltantes", "sitio": sitio, "recurso": recurso, "anio": anio,
                    "meses": faltantes,
                    "detalle": "Falta %s de %s en %s (%s): el total del año queda incompleto."
                               % ("el mes" if len(faltantes) == 1 else "los meses",
                                  ", ".join(faltantes), anio, "%s / %s" % (sitio, recurso)),
                })

    hallazgos.sort(key=lambda h: (h["tipo"] != "meses_faltantes", -abs(h.get("desvio_pct", 0))))
    return Respuesta(
        {
            "empresa": perfil.get("nombre"),
            "archivo": completa,
            "series_revisadas": len(series),
            "umbral_pct": umbral,
            "hallazgos": hallazgos,
            "mensaje": "No encontre datos raros." if not hallazgos else
                       "Encontre %d cosa(s) que conviene revisar." % len(hallazgos),
        },
        advertencias=["Un salto no siempre es un error: puede ser estacionalidad o una parada de planta. "
                      "Preguntale a la persona antes de corregir nada."] if hallazgos else [],
    )


ACCIONES = {"resumen": resumen, "leer": leer, "anomalias": anomalias}
