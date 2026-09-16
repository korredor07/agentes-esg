# -*- coding: utf-8 -*-
"""E2E capa 1: ejecuta cada comando que las skills y los agentes le ensenan al asistente.

Una skill es una promesa: «para hacer X, corre este comando». Si el comando
documentado no funciona tal como esta escrito, el asistente falla aunque el
motor este bien. Este script los corre todos, en el orden en que aparecen, sobre
un clon limpio con la empresa de ejemplo.

Clasificacion de cada comando:
  ok          -> "ok": true
  controlado  -> "ok": false con error y sugerencia (falta un dato o el estado previo)
  omitido     -> tiene un marcador <...> que el asistente reemplaza con datos reales
  FALLA       -> no devuelve JSON, trae un Traceback, o el modulo/accion no existe
"""

import io
import json
import os
import re
import shlex
import subprocess
import sys

CLON = sys.argv[1]
SALIDA = sys.argv[2]


def bloques_bash(texto):
    return re.findall(r"```bash\n(.*?)```", texto, re.S)


def lineas_de_comando(bloque):
    for linea in bloque.splitlines():
        linea = linea.strip()
        if not linea.startswith("python .claude/motor/esg.py"):
            continue
        # Quita el comentario final, respetando las comillas.
        try:
            partes = shlex.split(linea, comments=True, posix=True)
        except ValueError:
            yield linea, None
            continue
        yield linea, partes


def documentos():
    for base, patron in ((".claude/skills", "SKILL.md"), (".claude/agents", None)):
        carpeta = os.path.join(CLON, base)
        for nombre in sorted(os.listdir(carpeta)):
            ruta = os.path.join(carpeta, nombre, patron) if patron else os.path.join(carpeta, nombre)
            if os.path.isfile(ruta) and ruta.endswith(".md"):
                yield os.path.relpath(ruta, CLON).replace("\\", "/"), io.open(ruta, encoding="utf-8").read()
    yield "CLAUDE.md", io.open(os.path.join(CLON, "CLAUDE.md"), encoding="utf-8").read()


resultados = []
for documento, texto in documentos():
    for bloque in bloques_bash(texto):
        for linea, partes in lineas_de_comando(bloque):
            ficha = {"documento": documento, "comando": linea}
            if partes is None:
                ficha.update(estado="FALLA", detalle="Comillas mal cerradas en la documentacion")
                resultados.append(ficha)
                continue
            if any("<" in p and ">" in p for p in partes):
                ficha.update(estado="omitido", detalle="Tiene un marcador que se reemplaza con datos reales")
                resultados.append(ficha)
                continue
            try:
                proceso = subprocess.run([sys.executable] + partes[1:], cwd=CLON, capture_output=True,
                                         text=True, encoding="utf-8", timeout=120)
            except subprocess.TimeoutExpired:
                ficha.update(estado="FALLA", detalle="Tardo mas de 120 segundos")
                resultados.append(ficha)
                continue
            if "Traceback" in (proceso.stderr or "") or "Traceback" in (proceso.stdout or ""):
                ficha.update(estado="FALLA", detalle=(proceso.stderr or proceso.stdout)[-400:])
                resultados.append(ficha)
                continue
            try:
                respuesta = json.loads(proceso.stdout)
            except ValueError:
                ficha.update(estado="FALLA", detalle="No devolvio JSON: " + (proceso.stdout or proceso.stderr)[:300])
                resultados.append(ficha)
                continue
            if respuesta.get("ok"):
                ficha.update(estado="ok")
            else:
                error = respuesta.get("error") or ""
                if "No conozco el modulo" in error or "no tiene la accion" in error \
                        or "No conozco el módulo" in error or "no tiene la acción" in error:
                    ficha.update(estado="FALLA", detalle=error)
                elif not respuesta.get("sugerencia"):
                    ficha.update(estado="FALLA", detalle="Error sin sugerencia: " + error)
                else:
                    ficha.update(estado="controlado", detalle=error, sugerencia=respuesta.get("sugerencia"))
            resultados.append(ficha)

conteo = {}
for ficha in resultados:
    conteo[ficha["estado"]] = conteo.get(ficha["estado"], 0) + 1
with io.open(SALIDA, "w", encoding="utf-8") as archivo:
    json.dump({"conteo": conteo, "resultados": resultados}, archivo, ensure_ascii=False, indent=2)

print("comandos documentados:", len(resultados), conteo)
for ficha in resultados:
    if ficha["estado"] in ("FALLA", "controlado"):
        print("%-10s %-42s %s" % (ficha["estado"], ficha["documento"][:42], ficha["comando"][27:110]))
        print("           -> %s" % str(ficha.get("detalle"))[:160])
