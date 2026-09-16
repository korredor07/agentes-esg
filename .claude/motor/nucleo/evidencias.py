# -*- coding: utf-8 -*-
"""Registro de evidencias con cadena de huellas SHA-256.

Cada respaldo (una boleta de luz, una planilla, un informe) queda anotado con
su huella digital y enlazado al anterior. Si alguien cambia un archivo o borra
una linea del registro, la verificacion lo detecta.

No reemplaza una firma electronica avanzada ni un sellado de tiempo acreditado:
prueba integridad y orden, no identidad legal. El agente debe decirlo asi.
"""

import datetime
import hashlib
import json
import os

from .salida import Problema

NOMBRE_REGISTRO = "registro.jsonl"
GENESIS = "0" * 64


def huella_archivo(ruta):
    """SHA-256 del contenido de un archivo."""
    if not os.path.isfile(ruta):
        raise Problema(
            "No encontre el archivo que quieres respaldar: %s" % ruta,
            "Revisa la ruta; si el archivo esta en la carpeta de la empresa, basta con su nombre.",
        )
    digestor = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(65536), b""):
            digestor.update(bloque)
    return digestor.hexdigest()


def _huella_registro(entrada):
    copia = {clave: entrada[clave] for clave in entrada if clave != "huella_registro"}
    texto = json.dumps(copia, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _ruta_registro(carpeta_evidencias):
    if not os.path.isdir(carpeta_evidencias):
        os.makedirs(carpeta_evidencias)
    return os.path.join(carpeta_evidencias, NOMBRE_REGISTRO)


def leer_registro(carpeta_evidencias):
    ruta = _ruta_registro(carpeta_evidencias)
    entradas = []
    if not os.path.isfile(ruta):
        return entradas
    with open(ruta, encoding="utf-8") as archivo:
        for numero, linea in enumerate(archivo, start=1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                entradas.append(json.loads(linea))
            except ValueError:
                raise Problema(
                    "La linea %d del registro de evidencias esta dañada." % numero,
                    "No edites registro.jsonl a mano. Puedo ayudarte a reconstruir el registro.",
                )
    return entradas


def registrar(carpeta_evidencias, archivo, descripcion="", tipo="documento", responsable="", base=None):
    """Anota un archivo en la cadena y devuelve la entrada creada."""
    ruta_archivo = os.path.abspath(archivo)
    huella = huella_archivo(ruta_archivo)
    entradas = leer_registro(carpeta_evidencias)
    anterior = entradas[-1]["huella_registro"] if entradas else GENESIS
    referencia = os.path.relpath(ruta_archivo, os.path.abspath(base)) if base else ruta_archivo
    entrada = {
        "n": len(entradas) + 1,
        "fecha": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "archivo": referencia.replace("\\", "/"),
        "nombre": os.path.basename(ruta_archivo),
        "bytes": os.path.getsize(ruta_archivo),
        "sha256": huella,
        "descripcion": descripcion,
        "tipo": tipo,
        "responsable": responsable,
        "huella_anterior": anterior,
    }
    entrada["huella_registro"] = _huella_registro(entrada)
    with open(_ruta_registro(carpeta_evidencias), "a", encoding="utf-8") as registro:
        registro.write(json.dumps(entrada, ensure_ascii=False) + "\n")
    return entrada


def verificar(carpeta_evidencias, base=None):
    """Revisa que la cadena este intacta y que los archivos no hayan cambiado."""
    entradas = leer_registro(carpeta_evidencias)
    problemas = []
    anterior = GENESIS
    archivos_ok = 0
    for entrada in entradas:
        numero = entrada.get("n")
        if _huella_registro(entrada) != entrada.get("huella_registro"):
            problemas.append({
                "n": numero, "archivo": entrada.get("nombre"), "tipo": "registro_alterado",
                "detalle": "La anotacion numero %s fue modificada despues de registrarse." % numero,
            })
        if entrada.get("huella_anterior") != anterior:
            problemas.append({
                "n": numero, "archivo": entrada.get("nombre"), "tipo": "cadena_rota",
                "detalle": "Falta una anotacion anterior o se cambio el orden en la anotacion %s." % numero,
            })
        anterior = entrada.get("huella_registro")

        referencia = entrada.get("archivo", "")
        ruta = referencia if os.path.isabs(referencia) else os.path.join(os.path.abspath(base or carpeta_evidencias), referencia)
        if not os.path.isfile(ruta):
            problemas.append({
                "n": numero, "archivo": entrada.get("nombre"), "tipo": "archivo_faltante",
                "detalle": "Ya no encuentro el archivo respaldado (%s)." % referencia,
            })
        elif huella_archivo(ruta) != entrada.get("sha256"):
            problemas.append({
                "n": numero, "archivo": entrada.get("nombre"), "tipo": "archivo_modificado",
                "detalle": "El archivo %s cambio despues de registrarse." % entrada.get("nombre"),
            })
        else:
            archivos_ok += 1
    return {
        "ok": not problemas,
        "total": len(entradas),
        "archivos_intactos": archivos_ok,
        "problemas": problemas,
        "resumen": ("La cadena de evidencias esta intacta: %d respaldo(s) verificados." % len(entradas))
        if not problemas else
        ("Se detectaron %d problema(s) en la cadena de evidencias." % len(problemas)),
    }


def listar(carpeta_evidencias):
    return [
        {clave: entrada.get(clave) for clave in ("n", "fecha", "nombre", "descripcion", "tipo", "sha256", "bytes")}
        for entrada in leer_registro(carpeta_evidencias)
    ]
