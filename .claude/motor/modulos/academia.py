# -*- coding: utf-8 -*-
"""Academia interna: rutas de aprendizaje ESG, avance de cada persona y certificado."""

import csv
import datetime
import json
import os
import re
import unicodedata

from nucleo import espacio, informe, word
from nucleo.salida import Problema, Respuesta

AYUDA = "Formacion interna ESG: cursos con lecciones, registro de avance por persona y certificado."

ARCHIVO = "academia.json"
CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_CURSOS = os.path.join(CARPETA_DATOS, "academia_cursos.csv")

AVISO_CERTIFICADO = ("El certificado es un registro interno de capacitacion de la propia empresa. No es una "
                     "certificacion oficial ni una acreditacion de ningun organismo competente, y no "
                     "reemplaza las capacitaciones que exija la normativa del rubro.")
AVISO_RANKING = ("Este listado sirve para reconocer avances y ver donde hace falta apoyo. No lo publiques "
                 "como una tabla de mejores y peores: conversa en privado con quien va mas atras y "
                 "pregunta que le falta para avanzar, que muchas veces es tiempo, no interes.")


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _clave(texto):
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor not in (None, "", True) else por_defecto


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"avances": []}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo de avance de la academia esta dañado y no se puede leer.",
                "No lo edites a mano. Se puede volver a registrar el avance leccion por leccion.",
            )
    datos.setdefault("avances", [])
    return datos


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


LETRAS = "abcdefgh"


def cargar_lecciones(ruta=None):
    """Lee el catalogo de cursos y devuelve la lista de lecciones en orden."""
    ruta = ruta or ARCHIVO_CURSOS
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro el contenido de los cursos (%s)." % os.path.basename(ruta),
            "Sin ese archivo no hay lecciones que mostrar. Avisa para reinstalar los datos del motor.",
        )
    lecciones = []
    contador = {}
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for numero_fila, fila in enumerate(csv.DictReader(archivo), start=2):
            curso = (fila.get("curso") or "").strip()
            titulo = (fila.get("leccion") or "").strip()
            if not curso or not titulo:
                continue
            curso_id = _clave(curso)
            contador[curso_id] = contador.get(curso_id, 0) + 1
            opciones = [o.strip() for o in (fila.get("opciones") or "").split("|") if o.strip()]
            correcta = (fila.get("respuesta_correcta") or "").strip().lower()
            try:
                minutos = int(float((fila.get("minutos") or "0").strip() or 0))
            except ValueError:
                minutos = 0
            lecciones.append({
                "curso": curso,
                "curso_id": curso_id,
                "nivel": (fila.get("nivel") or "").strip(),
                "numero": contador[curso_id],
                "leccion": titulo,
                "leccion_id": _clave(titulo),
                "minutos": minutos,
                "objetivo": (fila.get("objetivo") or "").strip(),
                "contenido_clave": (fila.get("contenido_clave") or "").strip(),
                "pregunta": (fila.get("pregunta") or "").strip(),
                "opciones": dict(zip(LETRAS, opciones)),
                "respuesta_correcta": correcta,
                "explicacion": (fila.get("explicacion") or "").strip(),
                "linea": numero_fila,
            })
    if not lecciones:
        raise Problema(
            "El catalogo de cursos esta vacio.",
            "Revisa el archivo academia_cursos.csv del motor: deberia tener una fila por leccion.",
        )
    return lecciones


def _cursos_agrupados(lecciones):
    cursos = []
    indice = {}
    for leccion in lecciones:
        if leccion["curso_id"] not in indice:
            indice[leccion["curso_id"]] = {
                "curso": leccion["curso"], "curso_id": leccion["curso_id"],
                "nivel": leccion["nivel"], "lecciones": [], "minutos_total": 0,
            }
            cursos.append(indice[leccion["curso_id"]])
        ficha = indice[leccion["curso_id"]]
        ficha["lecciones"].append(leccion)
        ficha["minutos_total"] += leccion["minutos"]
    return cursos


def _buscar_curso(lecciones, texto):
    buscado = _clave(texto)
    cursos = _cursos_agrupados(lecciones)
    for ficha in cursos:
        if ficha["curso_id"] == buscado or buscado in ficha["curso_id"]:
            return ficha
    raise Problema(
        "No encontre el curso «%s»." % texto,
        "Cursos disponibles: %s." % ", ".join(f["curso"] for f in cursos),
    )


def _buscar_leccion(ficha_curso, texto):
    buscado = str(texto or "").strip()
    if buscado.isdigit():
        for leccion in ficha_curso["lecciones"]:
            if leccion["numero"] == int(buscado):
                return leccion
    clave = _clave(buscado)
    if clave:
        for leccion in ficha_curso["lecciones"]:
            if leccion["leccion_id"] == clave or clave in leccion["leccion_id"]:
                return leccion
    raise Problema(
        "No encontre la leccion «%s» dentro del curso %s." % (texto, ficha_curso["curso"]),
        "Lecciones del curso: %s." % ", ".join("%d. %s" % (lec["numero"], lec["leccion"])
                                               for lec in ficha_curso["lecciones"]),
    )


def _resumen_leccion(leccion, completa=False):
    ficha = {"numero": leccion["numero"], "leccion": leccion["leccion"],
             "leccion_id": leccion["leccion_id"], "minutos": leccion["minutos"],
             "objetivo": leccion["objetivo"]}
    if completa:
        ficha.update({
            "contenido_clave": leccion["contenido_clave"],
            "pregunta": leccion["pregunta"],
            "opciones": leccion["opciones"],
            "respuesta_correcta": leccion["respuesta_correcta"],
            "explicacion": leccion["explicacion"],
        })
    return ficha


# --------------------------------------------------------------------------
# Acciones
# --------------------------------------------------------------------------

def cursos(opciones):
    """Lista las rutas de aprendizaje. Con --curso entrega el contenido completo."""
    lecciones = cargar_lecciones()
    nombre_curso = _valor(opciones, "curso")
    if not nombre_curso:
        fichas = _cursos_agrupados(lecciones)
        return {
            "total_cursos": len(fichas),
            "total_lecciones": len(lecciones),
            "cursos": [{
                "curso": f["curso"], "curso_id": f["curso_id"], "nivel": f["nivel"],
                "lecciones": len(f["lecciones"]), "minutos_total": f["minutos_total"],
                "detalle_lecciones": [_resumen_leccion(lec) for lec in f["lecciones"]],
            } for f in fichas],
            "mensaje": ("Para ver el contenido de un curso: academia cursos --curso \"Fundamentos ESG\". "
                        "Para una leccion sola, agrega --leccion 2."),
        }
    ficha = _buscar_curso(lecciones, nombre_curso)
    numero_leccion = _valor(opciones, "leccion")
    if numero_leccion:
        leccion = _buscar_leccion(ficha, numero_leccion)
        return {
            "curso": ficha["curso"], "nivel": ficha["nivel"],
            "leccion": _resumen_leccion(leccion, completa=True),
            "total_lecciones": len(ficha["lecciones"]),
            "mensaje": ("Explica el contenido con tus palabras, despues haz la pregunta y registra el "
                        "resultado con: academia avance."),
        }
    return {
        "curso": ficha["curso"], "curso_id": ficha["curso_id"], "nivel": ficha["nivel"],
        "minutos_total": ficha["minutos_total"],
        "lecciones": [_resumen_leccion(lec, completa=True) for lec in ficha["lecciones"]],
        "mensaje": "Una leccion por conversacion: explicar, preguntar, corregir con amabilidad y registrar.",
    }


def avance(opciones):
    """Registra que persona completo que leccion y como le fue en la pregunta."""
    perfil, ruta, ruta_json = _contexto(opciones)
    persona = _valor(opciones, "persona")
    if not persona:
        raise Problema(
            "Falta el nombre de la persona que hizo la leccion.",
            "Indicalo asi: academia avance --persona \"Ana Perez\" --curso \"Fundamentos ESG\" --leccion 1.",
        )
    nombre_curso = _valor(opciones, "curso")
    if not nombre_curso:
        raise Problema(
            "Falta indicar de que curso es la leccion.",
            "Mira los cursos disponibles con: academia cursos.",
        )
    referencia = _valor(opciones, "leccion")
    if not referencia:
        raise Problema(
            "Falta indicar que leccion completo.",
            "Puedes usar el numero (--leccion 2) o parte del titulo.",
        )

    lecciones = cargar_lecciones()
    ficha = _buscar_curso(lecciones, nombre_curso)
    leccion = _buscar_leccion(ficha, referencia)

    respuesta = str(_valor(opciones, "respuesta")).strip().lower()
    resultado = "sin responder"
    correcta = None
    if respuesta:
        if respuesta not in leccion["opciones"]:
            # tambien se acepta el texto de la alternativa
            equivalencias = {_clave(v): k for k, v in leccion["opciones"].items()}
            respuesta = equivalencias.get(_clave(respuesta), respuesta)
        if respuesta not in leccion["opciones"]:
            raise Problema(
                "No reconozco la respuesta «%s»." % _valor(opciones, "respuesta"),
                "Las alternativas de esta leccion son: %s."
                % ", ".join("%s) %s" % (k, v) for k, v in sorted(leccion["opciones"].items())),
            )
        correcta = respuesta == leccion["respuesta_correcta"]
        resultado = "correcto" if correcta else "incorrecto"

    datos = _leer(ruta_json)
    persona_id = _clave(persona)
    registro = {
        "persona": persona,
        "persona_id": persona_id,
        "area": _valor(opciones, "area"),
        "curso": ficha["curso"],
        "curso_id": ficha["curso_id"],
        "leccion": leccion["leccion"],
        "leccion_id": leccion["leccion_id"],
        "numero": leccion["numero"],
        "minutos": leccion["minutos"],
        "respuesta": respuesta or "",
        "resultado": resultado,
        "fecha": _valor(opciones, "fecha", datetime.date.today().isoformat()),
        "registrado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
    previos = [a for a in datos["avances"]
               if not (a.get("persona_id") == persona_id and a.get("curso_id") == ficha["curso_id"]
                       and a.get("leccion_id") == leccion["leccion_id"])]
    repetida = len(previos) != len(datos["avances"])
    if not registro["area"]:
        anterior = next((a for a in datos["avances"] if a.get("persona_id") == persona_id and a.get("area")), None)
        registro["area"] = anterior["area"] if anterior else ""
    datos["avances"] = previos + [registro]
    _guardar(ruta_json, datos)

    hechas = {a["leccion_id"] for a in datos["avances"]
              if a.get("persona_id") == persona_id and a.get("curso_id") == ficha["curso_id"]}
    pendientes = [lec["leccion"] for lec in ficha["lecciones"] if lec["leccion_id"] not in hechas]
    advertencias = []
    if resultado == "incorrecto":
        advertencias.append("La respuesta no era la correcta. Explicaselo sin dramatismo y vuelve a "
                            "preguntar mas adelante: la idea es que aprenda, no que apruebe.")
    if resultado == "sin responder":
        advertencias.append("Quedo registrada la leccion sin resultado de cuestionario. Si le hiciste la "
                            "pregunta, registra la respuesta con --respuesta a|b|c.")

    return Respuesta(
        {"mensaje": "%s: %s completo la leccion «%s» (%s)."
                    % ("Avance actualizado" if repetida else "Avance registrado",
                       persona, leccion["leccion"], resultado),
         "avance": registro,
         "explicacion": leccion["explicacion"] if respuesta else "",
         "curso": ficha["curso"],
         "completadas": len(hechas),
         "total_lecciones": len(ficha["lecciones"]),
         "pendientes": pendientes,
         "curso_completo": not pendientes,
         "archivo": ruta_json},
        advertencias=advertencias)


def _avance_de_curso(datos, ficha, persona_id):
    registros = [a for a in datos["avances"]
                 if a.get("persona_id") == persona_id and a.get("curso_id") == ficha["curso_id"]]
    hechas = {a["leccion_id"]: a for a in registros}
    pendientes = [lec["leccion"] for lec in ficha["lecciones"] if lec["leccion_id"] not in hechas]
    correctas = len([a for a in registros if a.get("resultado") == "correcto"])
    return registros, hechas, pendientes, correctas


def _bloques_certificado_word(perfil, persona, ficha, fecha, correctas, respondidas, minutos):
    return [
        {"tipo": "titulo", "texto": "Certificado de capacitacion interna", "nivel": 0},
        {"tipo": "texto", "texto": "%s deja constancia de que" % perfil.get("nombre", "La empresa")},
        {"tipo": "titulo", "texto": persona, "nivel": 1},
        {"tipo": "texto", "texto": "completo la ruta de aprendizaje"},
        {"tipo": "titulo", "texto": ficha["curso"], "nivel": 2},
        {"tipo": "tabla", "columnas": ["Dato", "Detalle"], "filas": [
            ["Nivel", ficha["nivel"] or "—"],
            ["Lecciones completadas", "%d de %d" % (len(ficha["lecciones"]), len(ficha["lecciones"]))],
            ["Duracion estimada", "%d minutos" % minutos],
            ["Respuestas correctas en los cuestionarios",
             "%d de %d" % (correctas, respondidas) if respondidas else "sin cuestionario registrado"],
            ["Fecha de emision", fecha],
        ]},
        {"tipo": "texto", "texto": "Contenidos cubiertos:"},
        {"tipo": "lista", "items": ["%d. %s — %s" % (lec["numero"], lec["leccion"], lec["objetivo"])
                                    for lec in ficha["lecciones"]]},
        {"tipo": "texto", "texto": "\n\n____________________\nFirma de la jefatura o de quien coordina "
                                   "la capacitacion"},
        {"tipo": "nota", "texto": AVISO_CERTIFICADO},
    ]


def certificado(opciones):
    """Emite el certificado interno de una persona que completo un curso."""
    perfil, ruta, ruta_json = _contexto(opciones)
    persona = _valor(opciones, "persona")
    nombre_curso = _valor(opciones, "curso")
    if not persona or not nombre_curso:
        raise Problema(
            "Para emitir el certificado necesito el nombre de la persona y el curso.",
            "Por ejemplo: academia certificado --persona \"Ana Perez\" --curso \"Fundamentos ESG\".",
        )
    formato = str(_valor(opciones, "formato", "html")).lower()
    if formato in ("docx", "doc"):
        formato = "word"
    if formato not in ("html", "word"):
        raise Problema(
            "No se generar el certificado en formato «%s»." % _valor(opciones, "formato"),
            "Puedo hacerlo en html (se abre en el navegador y se imprime a PDF) o en word (editable).",
        )

    lecciones = cargar_lecciones()
    ficha = _buscar_curso(lecciones, nombre_curso)
    datos = _leer(ruta_json)
    persona_id = _clave(persona)
    registros, hechas, pendientes, correctas = _avance_de_curso(datos, ficha, persona_id)
    if not registros:
        raise Problema(
            "No hay ninguna leccion registrada de %s en el curso %s." % (persona, ficha["curso"]),
            "Registra el avance leccion por leccion con: academia avance --persona \"%s\" --curso \"%s\" "
            "--leccion 1." % (persona, ficha["curso"]),
        )
    if pendientes:
        raise Problema(
            "%s todavia no termina el curso %s: le faltan %d leccion(es)."
            % (persona, ficha["curso"], len(pendientes)),
            "Faltan: %s. Cuando las complete, vuelvo a emitir el certificado." % ", ".join(pendientes),
        )

    nombre_real = registros[0].get("persona") or persona
    respondidas = len([a for a in registros if a.get("resultado") in ("correcto", "incorrecto")])
    minutos = sum(lec["minutos"] for lec in ficha["lecciones"])
    fecha = _valor(opciones, "fecha", datetime.date.today().isoformat())
    base = "certificado-%s-%s" % (ficha["curso_id"], persona_id)

    if formato == "word":
        destino = espacio.ruta_de(ruta, "reportes", base + ".docx")
        word.escribir_docx(destino,
                           _bloques_certificado_word(perfil, nombre_real, ficha, fecha, correctas,
                                                     respondidas, minutos),
                           "Certificado de capacitacion interna")
    else:
        bloques = [
            {"tipo": "texto", "texto": "%s deja constancia de que" % perfil.get("nombre", "La empresa")},
            {"tipo": "titulo", "texto": nombre_real, "nivel": 2},
            {"tipo": "texto", "texto": "completo la ruta de aprendizaje «%s»." % ficha["curso"]},
            {"tipo": "kpi", "items": [
                {"etiqueta": "Lecciones completadas", "valor": len(ficha["lecciones"]),
                 "unidad": "de %d" % len(ficha["lecciones"]), "color": "verde"},
                {"etiqueta": "Duracion estimada", "valor": minutos, "unidad": "minutos"},
                {"etiqueta": "Respuestas correctas", "valor": correctas,
                 "unidad": "de %d" % respondidas if respondidas else "",
                 "detalle": "En los cuestionarios de cada leccion" if respondidas
                            else "Sin cuestionario registrado"},
                {"etiqueta": "Fecha de emision", "valor": fecha, "unidad": ""},
            ]},
            {"tipo": "titulo", "texto": "Contenidos cubiertos", "nivel": 2},
            {"tipo": "tabla", "columnas": ["N.", "Leccion", "Objetivo"], "numericas": [0],
             "filas": [[lec["numero"], lec["leccion"], lec["objetivo"]] for lec in ficha["lecciones"]]},
            {"tipo": "texto", "texto": "Firma de la jefatura o de quien coordina la capacitacion: "
                                       "____________________"},
            {"tipo": "nota", "estilo": "aviso", "texto": AVISO_CERTIFICADO},
        ]
        destino = espacio.ruta_de(ruta, "reportes", base + ".html")
        informe.escribir_html(destino, "Certificado de capacitacion interna", bloques,
                              marca=perfil.get("marca") or {},
                              subtitulo="%s — %s" % (nombre_real, ficha["curso"]),
                              pie=AVISO_CERTIFICADO)

    return Respuesta(
        {"mensaje": "Certificado emitido para %s." % nombre_real,
         "archivo": destino,
         "formato": formato,
         "persona": nombre_real,
         "curso": ficha["curso"],
         "fecha": fecha,
         "lecciones": len(ficha["lecciones"]),
         "correctas": correctas,
         "respondidas": respondidas},
        advertencias=[AVISO_CERTIFICADO])


def ranking(opciones):
    """Avance por persona o por area, para animar sin exponer a nadie."""
    perfil, ruta, ruta_json = _contexto(opciones)
    por = str(_valor(opciones, "por", "persona")).lower()
    if por in ("areas", "area", "equipo"):
        por = "area"
    elif por in ("persona", "personas", "gente"):
        por = "persona"
    else:
        raise Problema(
            "No se agrupar el avance por «%s»." % _valor(opciones, "por"),
            "Puedo agruparlo por persona o por area.",
        )

    lecciones = cargar_lecciones()
    total_disponible = len(lecciones)
    fichas = _cursos_agrupados(lecciones)
    por_curso = {f["curso_id"]: len(f["lecciones"]) for f in fichas}
    datos = _leer(ruta_json)
    if not datos["avances"]:
        return Respuesta(
            {"agrupado_por": por, "total": 0, "filas": [],
             "total_lecciones_disponibles": total_disponible,
             "mensaje": "Todavia nadie ha registrado lecciones. Empieza por una persona y una leccion."},
            advertencias=[])

    grupos = {}
    for registro in datos["avances"]:
        if por == "area":
            etiqueta = registro.get("area") or "Sin area indicada"
        else:
            etiqueta = registro.get("persona") or "Sin nombre"
        grupo = grupos.setdefault(_clave(etiqueta), {
            "nombre": etiqueta, "lecciones": 0, "correctas": 0, "respondidas": 0,
            "minutos": 0, "por_persona": {}, "ultima_fecha": "",
        })
        grupo["lecciones"] += 1
        grupo["minutos"] += int(registro.get("minutos") or 0)
        if registro.get("resultado") == "correcto":
            grupo["correctas"] += 1
        if registro.get("resultado") in ("correcto", "incorrecto"):
            grupo["respondidas"] += 1
        persona_id = registro.get("persona_id") or _clave(registro.get("persona"))
        cursos_persona = grupo["por_persona"].setdefault(persona_id, {})
        cursos_persona.setdefault(registro.get("curso_id"), set()).add(registro.get("leccion_id"))
        if str(registro.get("fecha") or "") > grupo["ultima_fecha"]:
            grupo["ultima_fecha"] = str(registro.get("fecha") or "")

    filas = []
    for grupo in grupos.values():
        personas = max(len(grupo["por_persona"]), 1)
        completos = 0
        for cursos_persona in grupo["por_persona"].values():
            for curso_id, hechas in cursos_persona.items():
                if por_curso.get(curso_id) and len(hechas) >= por_curso[curso_id]:
                    completos += 1
        posible = total_disponible * personas
        filas.append({
            "nombre": grupo["nombre"],
            "personas": personas,
            "lecciones_completadas": grupo["lecciones"],
            "lecciones_posibles": posible,
            "avance_pct": round(grupo["lecciones"] * 100.0 / posible, 1) if posible else 0.0,
            "cursos_completos": completos,
            "respuestas_correctas": grupo["correctas"],
            "preguntas_respondidas": grupo["respondidas"],
            "acierto_pct": (round(grupo["correctas"] * 100.0 / grupo["respondidas"], 1)
                            if grupo["respondidas"] else None),
            "minutos": grupo["minutos"],
            "ultima_actividad": grupo["ultima_fecha"],
        })
    filas.sort(key=lambda f: (-f["avance_pct"], f["nombre"]))

    return Respuesta(
        {"agrupado_por": por,
         "total": len(filas),
         "total_lecciones_disponibles": total_disponible,
         "cursos": [{"curso": f["curso"], "lecciones": len(f["lecciones"])} for f in fichas],
         "filas": filas,
         "mensaje": ("Avance por %s. Comparte el promedio del grupo y celebra a quien avanzo, sin nombrar "
                     "a quien va atras delante de los demas." % por)},
        advertencias=[AVISO_RANKING])


ACCIONES = {"cursos": cursos, "avance": avance, "certificado": certificado, "ranking": ranking}
