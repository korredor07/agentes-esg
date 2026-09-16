# -*- coding: utf-8 -*-
"""Ley Karin: casos, plazos legales y documentos base."""

import datetime
import json
import os

from calculos import karin as motor_karin
from nucleo import espacio, word
from nucleo.salida import Problema, Respuesta

AYUDA = "Gestiona denuncias de acoso y violencia laboral (Ley 21.643): plazos, seguimiento y documentos."

CARPETA = "karin"
ARCHIVO = "casos.json"
AVISO_PRIVACIDAD = ("Este caso contiene datos sensibles de personas. Se guarda solo en este computador, "
                    "nunca se publica y conviene usar iniciales o un codigo en vez de nombres completos.")
AVISO_LEGAL = ("Orientacion de apoyo, no asesoria legal. Los plazos de la Ley Karin son perentorios: "
               "ante una denuncia real, involucra a la asesoria juridica y al organismo administrador "
               "de la Ley 16.744.")


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    carpeta = espacio.ruta_de(ruta, "seguimiento", CARPETA)
    if not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    return perfil, ruta, os.path.join(carpeta, ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"casos": []}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            return json.load(archivo)
        except ValueError:
            raise Problema("El archivo de casos Ley Karin esta dañado.",
                           "No lo edites a mano. Puedo ayudarte a reconstruirlo con los datos que tengas.")


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _buscar(datos, identificador):
    for caso in datos["casos"]:
        if caso["id"].lower() == str(identificador or "").lower():
            return caso
    raise Problema(
        "No encontre el caso «%s»." % identificador,
        "Casos registrados: %s." % (", ".join(c["id"] for c in datos["casos"]) or "ninguno todavia"),
    )


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def crear(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    fecha = _valor(opciones, "fecha_denuncia")
    if not fecha:
        raise Problema(
            "Falta la fecha en que se recibio la denuncia.",
            "Es la fecha clave: de ahi salen todos los plazos. Usa --fecha-denuncia 15-09-2026.",
        )
    datos = _leer(ruta_json)
    anio = str(fecha)[:4] if str(fecha)[:4].isdigit() else str(datetime.date.today().year)
    correlativo = len([c for c in datos["casos"] if c["id"].startswith("KARIN-%s" % anio)]) + 1
    caso = {
        "id": "KARIN-%s-%03d" % (anio, correlativo),
        "fecha_denuncia": fecha,
        "tipo": _valor(opciones, "tipo", "acoso laboral"),
        "via": _valor(opciones, "via", "interna"),
        "anonima": bool(opciones.get("anonima")),
        "sitio": _valor(opciones, "sitio"),
        "region": _valor(opciones, "region"),
        "denunciante": _valor(opciones, "denunciante"),
        "denunciado": _valor(opciones, "denunciado"),
        "investigador": _valor(opciones, "investigador"),
        "resumen": _valor(opciones, "resumen"),
        "estado": "en investigacion",
        "eventos": {},
        "bitacora": [{"fecha": datetime.date.today().isoformat(), "nota": "Caso registrado en el sistema."}],
        "creado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
    datos["casos"].append(caso)
    _guardar(ruta_json, datos)
    calculo = motor_karin.plazos(caso["fecha_denuncia"], caso["eventos"], caso["region"] or None)
    return Respuesta(
        {"mensaje": "Caso %s registrado." % caso["id"], "caso": caso["id"],
         "proximos_pasos": [h for h in calculo["hitos"] if h["estado"] in ("por vencer", "en plazo", "vencido")][:3],
         "plazos": calculo["hitos"], "supuesto": calculo["supuesto"]},
        advertencias=[AVISO_PRIVACIDAD, AVISO_LEGAL])


def evento(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    caso = _buscar(datos, _valor(opciones, "caso"))
    hito = motor_karin.validar_evento(_valor(opciones, "hito"))
    fecha = _valor(opciones, "fecha") or datetime.date.today().isoformat()
    caso["eventos"][hito["id"]] = fecha
    nota = _valor(opciones, "nota")
    caso["bitacora"].append({"fecha": datetime.date.today().isoformat(),
                             "nota": "%s: %s.%s" % (hito["titulo"], fecha, " " + nota if nota else "")})
    if hito["id"] == "aplicar_medidas":
        caso["estado"] = "cerrado"
    _guardar(ruta_json, datos)
    calculo = motor_karin.plazos(caso["fecha_denuncia"], caso["eventos"], caso["region"] or None)
    pendientes = [h for h in calculo["hitos"] if not h["cumplido_el"]]
    return Respuesta(
        {"mensaje": "Registrado: %s el %s." % (hito["titulo"], fecha),
         "caso": caso["id"], "estado_caso": caso["estado"],
         "siguiente": pendientes[0] if pendientes else None,
         "plazos": calculo["hitos"]},
        advertencias=[AVISO_LEGAL])


def ver(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    caso = _buscar(datos, _valor(opciones, "caso"))
    calculo = motor_karin.plazos(caso["fecha_denuncia"], caso["eventos"], caso["region"] or None,
                                 hoy=_valor(opciones, "hoy") or None)
    return Respuesta(
        {"caso": caso, "plazos": calculo["hitos"], "vencidos": calculo["vencidos"],
         "por_vencer": calculo["por_vencer"], "supuesto": calculo["supuesto"],
         "nota_feriados": calculo["nota_feriados"]},
        advertencias=[AVISO_PRIVACIDAD, AVISO_LEGAL])


def listar(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    resumen = []
    for caso in datos["casos"]:
        calculo = motor_karin.plazos(caso["fecha_denuncia"], caso["eventos"], caso["region"] or None)
        resumen.append({
            "id": caso["id"], "fecha_denuncia": caso["fecha_denuncia"], "tipo": caso["tipo"],
            "estado": caso["estado"], "vencidos": len(calculo["vencidos"]),
            "por_vencer": len(calculo["por_vencer"]),
            "siguiente": next((h["titulo"] for h in calculo["hitos"] if not h["cumplido_el"]), None),
        })
    return {"total": len(resumen), "casos": resumen,
            "mensaje": "Sin casos registrados." if not resumen else "%d caso(s) registrados." % len(resumen)}


def alertas(opciones):
    """Deja en seguimiento/alertas.json los plazos que vencen, para el tablero."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    pendientes = []
    for caso in datos["casos"]:
        if caso["estado"] == "cerrado":
            continue
        calculo = motor_karin.plazos(caso["fecha_denuncia"], caso["eventos"], caso["region"] or None)
        for hito in calculo["hitos"]:
            if hito["cumplido_el"] or hito["proyectado"]:
                continue
            if hito["estado"] in ("vencido", "por vencer", "pendiente: debe hacerse de inmediato"):
                pendientes.append({
                    "origen": "Ley Karin", "caso": caso["id"], "titulo": "%s (%s)" % (hito["titulo"], caso["id"]),
                    "vence": hito["vence"], "estado": hito["estado"],
                    "por_vencer": hito["estado"] == "por vencer",
                    "detalle": hito["que_hacer"], "articulo": hito["articulo"],
                })
    archivo = espacio.ruta_de(ruta, "seguimiento", "alertas.json")
    otras = []
    if os.path.isfile(archivo):
        try:
            with open(archivo, encoding="utf-8") as origen:
                otras = [a for a in json.load(origen) if a.get("origen") != "Ley Karin"]
        except ValueError:
            otras = []
    with open(archivo, "w", encoding="utf-8") as destino:
        json.dump(otras + pendientes, destino, ensure_ascii=False, indent=2)
    return Respuesta(
        {"total": len(pendientes), "alertas": pendientes, "archivo": archivo,
         "mensaje": "Sin plazos criticos de Ley Karin." if not pendientes else
                    "Hay %d plazo(s) de Ley Karin que requieren atencion." % len(pendientes)},
        advertencias=[AVISO_LEGAL] if pendientes else [])


def _bloques_protocolo(perfil):
    nombre = perfil.get("nombre", "la empresa")
    return [
        {"tipo": "titulo", "texto": "Protocolo de prevencion del acoso sexual, laboral y la violencia en el trabajo",
         "nivel": 0},
        {"tipo": "texto", "texto": "%s — Version 1 — Fecha: ____________" % nombre},
        {"tipo": "nota", "texto": "Borrador base para completar con el organismo administrador de la Ley 16.744 "
                                  "al que esta afiliada la empresa. Los textos entre corchetes deben reemplazarse."},
        {"tipo": "titulo", "texto": "1. Objetivo y alcance", "nivel": 1},
        {"tipo": "texto", "texto": "Este protocolo establece las medidas que %s adopta para prevenir, investigar y "
                                   "sancionar el acoso sexual, el acoso laboral y la violencia en el trabajo, "
                                   "incluida la ejercida por terceros ajenos a la relacion laboral. Aplica a todas "
                                   "las personas trabajadoras, en todos los lugares y modalidades de trabajo." % nombre},
        {"tipo": "titulo", "texto": "2. Definiciones", "nivel": 1},
        {"tipo": "lista", "items": [
            "Acoso laboral: agresion u hostigamiento, ejercido por el empleador o por una o mas personas "
            "trabajadoras, por cualquier medio, que produzca menoscabo, maltrato o humillacion, o amenace o "
            "perjudique la situacion laboral u oportunidades de empleo. Basta un solo acto.",
            "Acoso sexual: requerimientos de caracter sexual no consentidos que amenacen o perjudiquen la "
            "situacion laboral u oportunidades de empleo.",
            "Violencia en el trabajo: conductas ejercidas por terceros ajenos a la relacion laboral, como "
            "clientes, proveedores o usuarios.",
        ]},
        {"tipo": "titulo", "texto": "3. Identificacion de peligros y evaluacion de riesgos psicosociales", "nivel": 1},
        {"tipo": "texto", "texto": "[Describir como se identifican los peligros y se evaluan los riesgos "
                                   "psicosociales, con perspectiva de genero, incluyendo la aplicacion del "
                                   "instrumento que indique el organismo administrador y la periodicidad.]"},
        {"tipo": "titulo", "texto": "4. Medidas de prevencion y control con objetivos medibles", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Riesgo identificado", "Medida", "Objetivo medible", "Responsable", "Plazo"],
         "filas": [["[Riesgo]", "[Medida]", "[Indicador y meta]", "[Cargo]", "[Fecha]"],
                   ["", "", "", "", ""], ["", "", "", "", ""]]},
        {"tipo": "titulo", "texto": "5. Informacion y capacitacion", "nivel": 1},
        {"tipo": "texto", "texto": "[Detallar como se informa y capacita sobre los riesgos, las medidas de "
                                   "prevencion y proteccion, y los derechos y responsabilidades. Incluir "
                                   "frecuencia, medios y registro de asistencia.]"},
        {"tipo": "titulo", "texto": "6. Canales de denuncia", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar los canales internos: persona o cargo responsable, correo, formulario "
                                   "y forma de presentar la denuncia verbal o escrita. Indicar tambien que se puede "
                                   "denunciar ante la Inspeccion del Trabajo.] La empresa informara estos canales "
                                   "al menos cada seis meses."},
        {"tipo": "titulo", "texto": "7. Procedimiento de investigacion y sancion", "nivel": 1},
        {"tipo": "lista", "ordenada": True, "items": [
            "Recibida la denuncia, la empresa adopta de inmediato medidas de resguardo.",
            "Dentro de 3 dias habiles informa a la Direccion del Trabajo el inicio de la investigacion interna, "
            "o le remite la denuncia con sus antecedentes.",
            "Designa a la persona investigadora, preferentemente con formacion en acoso, genero o derechos "
            "fundamentales, y lo informa por escrito a quien denuncia.",
            "La investigacion concluye dentro de 30 dias habiles, por escrito y en reserva, oyendo a ambas partes.",
            "Dentro de 2 dias habiles se remite el informe a la Direccion del Trabajo.",
            "Con el pronunciamiento de la Direccion del Trabajo, o vencido su plazo de 30 dias habiles, la empresa "
            "aplica las medidas o sanciones dentro de 15 dias corridos e informa a ambas partes.",
        ]},
        {"tipo": "titulo", "texto": "8. Resguardo de la privacidad y la honra", "nivel": 1},
        {"tipo": "texto", "texto": "Todas las actuaciones se realizan en estricta reserva. Se protege la privacidad "
                                   "y la honra de todas las personas involucradas, cualquiera sea el resultado de "
                                   "la investigacion. Se prohiben las represalias contra quien denuncia o declara. "
                                   "[Describir las medidas ante denuncias inconsistentes.]"},
        {"tipo": "titulo", "texto": "9. Difusion y vigencia", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar como se pone a disposicion: incorporacion al Reglamento Interno para "
                                   "empresas con 10 o mas personas trabajadoras, o entrega por escrito al firmar el "
                                   "contrato e incorporacion al reglamento del art. 67 de la Ley 16.744 en empresas "
                                   "mas pequeñas. Recordar la remision de copia del reglamento interno al Ministerio "
                                   "de Salud y a la Direccion del Trabajo dentro de los 5 dias siguientes a su "
                                   "vigencia.]"},
    ]


def _bloques_informe_investigacion(perfil):
    return [
        {"tipo": "titulo", "texto": "Informe de investigacion — Ley 21.643", "nivel": 0},
        {"tipo": "nota", "texto": "Estructura minima exigida por el art. 16 del DS N° 21 de 2024. "
                                  "Documento reservado."},
        {"tipo": "titulo", "texto": "1. Antecedentes de la empresa", "nivel": 1},
        {"tipo": "texto", "texto": "Razon social: %s. RUT: [____]. Domicilio: [____]. Actividad: %s."
                                   % (perfil.get("razon_social") or perfil.get("nombre", "[____]"),
                                      perfil.get("sector") or "[____]")},
        {"tipo": "titulo", "texto": "2. Individualizacion de las partes y de la persona investigadora", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Rol", "Identificacion", "Cargo", "Fecha de ingreso"],
         "filas": [["Denunciante", "[____]", "[____]", "[____]"],
                   ["Denunciada", "[____]", "[____]", "[____]"],
                   ["Investigador(a)", "[____]", "[____]", "[____]"]]},
        {"tipo": "titulo", "texto": "3. Medidas de resguardo adoptadas y su notificacion", "nivel": 1},
        {"tipo": "texto", "texto": "[Describir cada medida, su fecha y como se notifico a las partes.]"},
        {"tipo": "titulo", "texto": "4. Antecedentes recopilados y entrevistas", "nivel": 1},
        {"tipo": "texto", "texto": "[Listar declaraciones, documentos, registros de asistencia, contratos, "
                                   "resultados de la evaluacion de riesgos psicosociales y demas antecedentes. "
                                   "Las declaraciones deben constar en papel y firmadas en todas sus hojas.]"},
        {"tipo": "titulo", "texto": "5. Relacion de los hechos y alegaciones de las partes", "nivel": 1},
        {"tipo": "texto", "texto": "[Relato ordenado y fechado de los hechos investigados y de lo alegado por "
                                   "cada parte.]"},
        {"tipo": "titulo", "texto": "6. Razonamiento e indicios que fundan las conclusiones", "nivel": 1},
        {"tipo": "texto", "texto": "[Explicar de forma coherente y congruente como los antecedentes llevan a las "
                                   "conclusiones. Aplicar perspectiva de genero.]"},
        {"tipo": "titulo", "texto": "7. Conclusiones", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar si los hechos denunciados se acreditan o no, y su calificacion.]"},
        {"tipo": "titulo", "texto": "8. Medidas correctivas propuestas", "nivel": 1},
        {"tipo": "texto", "texto": "[Medidas sobre la causa que genero la denuncia, especialmente en casos de "
                                   "violencia ejercida por terceros.]"},
        {"tipo": "titulo", "texto": "9. Sanciones propuestas", "nivel": 1},
        {"tipo": "texto", "texto": "[Sanciones conforme al Reglamento Interno y a la legislacion vigente.]"},
        {"tipo": "texto", "texto": "Fecha: ____________    Firma de la persona investigadora: ____________"},
    ]


DOCUMENTOS = {
    "protocolo": ("protocolo-prevencion-ley-karin.docx", _bloques_protocolo,
                  "Protocolo de prevencion (Ley 21.643)"),
    "informe": ("informe-investigacion-ley-karin.docx", _bloques_informe_investigacion,
                "Informe de investigacion (Ley 21.643)"),
}


def documento(opciones):
    perfil, ruta, _ = _contexto(opciones)
    tipo = _valor(opciones, "tipo", "protocolo").lower()
    if tipo not in DOCUMENTOS:
        raise Problema("No tengo un documento «%s»." % tipo,
                       "Disponibles: %s." % ", ".join(DOCUMENTOS))
    nombre, constructor, titulo = DOCUMENTOS[tipo]
    destino = espacio.ruta_de(ruta, "reportes", nombre)
    word.escribir_docx(destino, constructor(perfil), titulo)
    return Respuesta(
        {"mensaje": "Borrador creado: %s." % titulo, "archivo": destino,
         "siguiente_paso": ("Revisalo con el organismo administrador de la Ley 16.744 y con la asesoria "
                            "juridica antes de publicarlo o firmarlo.")},
        advertencias=["Es un borrador base con la estructura minima exigida: hay que completarlo con la "
                      "realidad de la empresa. No reemplaza la asistencia tecnica del organismo administrador."])


ACCIONES = {"crear": crear, "evento": evento, "ver": ver, "listar": listar,
            "alertas": alertas, "documento": documento}
