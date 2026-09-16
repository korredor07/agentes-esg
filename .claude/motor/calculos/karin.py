# -*- coding: utf-8 -*-
"""Ley Karin (Ley 21.643 de Chile): plazos del procedimiento de denuncia.

Regla de conteo (art. 1 inc. 2 del DS N° 21 de 2024 del Ministerio del Trabajo):
los plazos son de dias habiles y son inhabiles los sabados, domingos y festivos.
Confirmado por los dictamenes de la Direccion del Trabajo ORD. N° 386/10 de
03-06-2025 y ORD. N° 57/04 de 26-01-2026.

Unica excepcion: la aplicacion de medidas y sanciones es de quince dias
CORRIDOS (art. 19 DS 21). Muchas guias comerciales dicen "habiles" y es un error.

El dia inicial se cuenta desde el dia siguiente al hecho (regla supletoria del
art. 25 de la Ley 19.880 para plazos habiles administrativos). El DS 21 no lo
dice expresamente: el motor lo declara como supuesto en cada resultado.

Los plazos NO se suspenden por feriado legal ni licencia medica de las personas
involucradas (ORD. N° 386/10, conclusion 1).
"""

import datetime
import os

from nucleo import fechas
from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_FERIADOS = os.path.join(CARPETA_DATOS, "feriados_chile.csv")

SUPUESTO_DIA_INICIAL = ("Los plazos se cuentan desde el dia siguiente al hecho, aplicando la regla "
                        "supletoria del art. 25 de la Ley 19.880. El DS 21 no lo dice expresamente.")

# Hitos del procedimiento. "desde" apunta al evento que dispara el plazo.
HITOS = [
    {
        "id": "medidas_resguardo", "titulo": "Adoptar medidas de resguardo",
        "dias": 0, "tipo": "inmediato", "desde": "denuncia",
        "articulo": "Art. 211-B bis inc. 2 del Codigo del Trabajo; art. 13 DS 21",
        "que_hacer": ("Separar espacios fisicos, redistribuir la jornada u ofrecer atencion psicologica "
                      "temprana a traves del organismo administrador de la Ley 16.744. No pueden ser "
                      "gravosas ni perjudiciales para quien denuncia."),
    },
    {
        "id": "informar_dt", "titulo": "Informar a la Direccion del Trabajo el inicio de la investigacion (o derivar la denuncia)",
        "dias": 3, "tipo": "habiles", "desde": "denuncia",
        "articulo": "Art. 211-C inc. 1 del Codigo del Trabajo; art. 12 inc. 4 DS 21",
        "que_hacer": ("Informar por escrito a la DT que se inicia la investigacion interna y cuales son "
                      "las medidas de resguardo, o remitir la denuncia con sus antecedentes. En ambos "
                      "casos hay que informar por escrito a la persona denunciante."),
    },
    {
        "id": "designar_investigador", "titulo": "Designar a la persona investigadora e informarlo por escrito",
        "dias": 3, "tipo": "habiles", "desde": "denuncia",
        "articulo": "Art. 211-C inc. final del Codigo del Trabajo; art. 14 DS 21",
        "que_hacer": ("Designar preferentemente a alguien con formacion en acoso, genero o derechos "
                      "fundamentales, e informar la designacion por escrito a la persona denunciante."),
    },
    {
        "id": "conclusion_investigacion", "titulo": "Concluir la investigacion",
        "dias": 30, "tipo": "habiles", "desde": "denuncia",
        "articulo": "Art. 211-C inc. 2 del Codigo del Trabajo; art. 17 DS 21",
        "que_hacer": ("La investigacion debe constar por escrito, en reserva, oyendo a ambas partes. "
                      "El informe tiene contenido minimo obligatorio (art. 16 DS 21). Si la denuncia "
                      "fue derivada a la DT, los 30 dias corren desde el certificado de recepcion."),
    },
    {
        "id": "remision_informe", "titulo": "Remitir el informe y las conclusiones a la Direccion del Trabajo",
        "dias": 2, "tipo": "habiles", "desde": "conclusion_investigacion",
        "articulo": "Art. 18 inc. 1 DS 21",
        "que_hacer": "Enviarlo por via electronica a la DT.",
    },
    {
        "id": "pronunciamiento_dt", "titulo": "Pronunciamiento de la Direccion del Trabajo",
        "dias": 30, "tipo": "habiles", "desde": "remision_informe",
        "articulo": "Art. 211-C inc. 3 del Codigo del Trabajo; art. 18 inc. 2 DS 21",
        "que_hacer": ("Lo hace la DT, no la empresa. Si no se pronuncia dentro del plazo, las "
                      "conclusiones del informe se consideran validas."),
        "responsable": "Direccion del Trabajo",
    },
    {
        "id": "aplicar_medidas", "titulo": "Aplicar las medidas y sanciones e informarlas a las partes",
        "dias": 15, "tipo": "corridos", "desde": "pronunciamiento_dt",
        "articulo": "Art. 211-E del Codigo del Trabajo; art. 19 DS 21",
        "que_hacer": ("Aplicar lo resuelto e informar por escrito a la persona denunciante y a la "
                      "denunciada. Este es el unico plazo en dias corridos del procedimiento."),
    },
]

HITOS_POR_ID = {h["id"]: h for h in HITOS}


def cargar_feriados(region=None):
    ambitos = ["nacional"] + ([region] if region else [])
    return fechas.cargar_feriados(ARCHIVO_FERIADOS, ambitos=ambitos)


# Eventos que no son un plazo en si, pero desde los que corre un plazo.
EVENTOS_EXTRA = {
    "recepcion_dt": {
        "id": "recepcion_dt",
        "titulo": "Certificado de recepcion de la derivacion emitido por la Direccion del Trabajo",
        "articulo": "Art. 17 DS 21",
    },
}


def derivacion_obligatoria(reglamento_actualizado=None, contra_representante=None):
    """Si la ley obliga a derivar la denuncia a la Direccion del Trabajo. Devuelve (obligatoria, motivo)."""
    if contra_representante is True:
        return True, ("La denuncia es contra una de las personas del art. 4 inc. 1 del Codigo del Trabajo "
                      "(gerente, administrador o quien representa al empleador): siempre se deriva a la "
                      "Direccion del Trabajo (art. 12 inc. 5 DS 21).")
    if reglamento_actualizado is False:
        return True, ("El reglamento interno todavia no esta actualizado con el procedimiento de la Ley Karin: "
                      "mientras no lo este, la denuncia se deriva a la Direccion del Trabajo de inmediato (DS 21, "
                      "art. primero transitorio inc. 3).")
    return False, ""


def plazos(fecha_denuncia, eventos=None, region=None, hoy=None, via=None):
    """Calcula el estado de cada plazo del procedimiento.

    eventos: fechas reales ya ocurridas, por id de hito. Cuando un hito previo
    ya ocurrio, el siguiente plazo se cuenta desde esa fecha real; si no, se
    proyecta desde el vencimiento estimado y se marca como proyectado.
    """
    eventos = {clave: valor for clave, valor in (eventos or {}).items() if valor}
    feriados = cargar_feriados(region)
    referencia = fechas.parsear_fecha(hoy) if hoy else datetime.date.today()
    inicio = fechas.parsear_fecha(fecha_denuncia)

    calculados = {"denuncia": {"fecha": inicio, "real": True}}
    derivada = str(via or "").strip().lower() in ("derivada", "dt", "direccion del trabajo")
    if eventos.get("recepcion_dt"):
        calculados["recepcion_dt"] = {"fecha": fechas.parsear_fecha(eventos["recepcion_dt"]), "real": True}
    salida = []
    for hito in HITOS:
        desde = hito["desde"]
        if derivada and hito["id"] == "conclusion_investigacion":
            # Art. 17 DS 21: si se derivo, los 30 dias corren desde la recepcion en la DT.
            desde = "recepcion_dt"
            if "recepcion_dt" not in calculados:
                salida.append({
                    "id": hito["id"], "titulo": hito["titulo"], "articulo": "Art. 17 DS 21",
                    "que_hacer": ("La denuncia fue derivada: los 30 dias habiles corren desde la fecha del "
                                  "certificado de recepcion que emite la Direccion del Trabajo. Registralo con "
                                  "karin evento --hito recepcion_dt --fecha <fecha>."),
                    "responsable": "Direccion del Trabajo", "dias": hito["dias"], "tipo_de_dias": hito["tipo"],
                    "cuenta_desde": "recepcion_dt", "vence": None, "cumplido_el": None, "dias_restantes": None,
                    "estado": "pendiente: falta el certificado de recepcion de la DT", "proyectado": False,
                })
                continue
        base = calculados.get(desde)
        if base is None:
            continue
        proyectado = not base["real"]

        if hito["tipo"] == "inmediato":
            vence = base["fecha"]
            detalle = {"inicio": base["fecha"].isoformat(), "vence": vence.isoformat(),
                       "dias": 0, "tipo": "inmediato", "dias_restantes": None,
                       "estado": "inmediato", "referencia": referencia.isoformat()}
        else:
            detalle = fechas.plazo(base["fecha"], hito["dias"], hito["tipo"], feriados, hoy=referencia)
            vence = fechas.parsear_fecha(detalle["vence"])

        real = eventos.get(hito["id"])
        cumplido = None
        if real:
            cumplido = fechas.parsear_fecha(real)
            estado = "cumplido a tiempo" if cumplido <= vence else "cumplido fuera de plazo"
            calculados[hito["id"]] = {"fecha": cumplido, "real": True}
        else:
            estado = {"vencido": "vencido", "por_vencer": "por vencer", "vigente": "en plazo",
                      "inmediato": "pendiente: debe hacerse de inmediato"}[detalle["estado"]]
            calculados[hito["id"]] = {"fecha": vence, "real": False}

        salida.append({
            "id": hito["id"], "titulo": hito["titulo"], "articulo": hito["articulo"],
            "que_hacer": hito["que_hacer"], "responsable": hito.get("responsable", "La empresa"),
            "dias": hito["dias"], "tipo_de_dias": hito["tipo"],
            "cuenta_desde": desde,
            "vence": vence.isoformat(),
            "cumplido_el": cumplido.isoformat() if cumplido else None,
            "dias_restantes": detalle["dias_restantes"] if not cumplido else None,
            "estado": estado,
            "proyectado": proyectado and not cumplido,
        })
    return {
        "fecha_denuncia": inicio.isoformat(),
        "region": region or "nacional",
        "hoy": referencia.isoformat(),
        "hitos": salida,
        "vencidos": [h for h in salida if h["estado"] == "vencido"],
        "por_vencer": [h for h in salida if h["estado"] in ("por vencer", "pendiente: debe hacerse de inmediato")],
        "supuesto": SUPUESTO_DIA_INICIAL,
        "nota_feriados": ("Se usan los feriados nacionales de Chile 2025-2027%s. "
                          "Los plazos no se suspenden por feriado legal ni licencia medica."
                          % (" mas los de %s" % region if region else "")),
    }


def validar_evento(identificador):
    if identificador in EVENTOS_EXTRA:
        return EVENTOS_EXTRA[identificador]
    if identificador not in HITOS_POR_ID:
        raise Problema(
            "No conozco el hito «%s» del procedimiento." % identificador,
            "Hitos validos: %s." % ", ".join(list(HITOS_POR_ID) + list(EVENTOS_EXTRA)),
        )
    return HITOS_POR_ID[identificador]
