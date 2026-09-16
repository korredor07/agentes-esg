# -*- coding: utf-8 -*-
"""Mineria: relaves, ventilacion, exposicion ocupacional, cierre de faenas y GISTM."""

import datetime
import os

from calculos import mineria as motor_mineria
from nucleo import espacio, informe
from nucleo.salida import Problema, Respuesta

AYUDA = ("Seguridad en faenas mineras de Chile: depositos de relaves (DS 248/2007), ventilacion "
         "subterranea (DS 132/2002), limites de exposicion (DS 594/1999), plan de cierre (Ley 20.551) "
         "y conformidad con el GISTM.")

AVISO_EXPERTO = ("Esto es apoyo para ordenar lo que exige la norma: NO reemplaza al experto en prevencion "
                 "de riesgos de la faena, al Ingeniero de Registro del deposito ni a la asistencia tecnica "
                 "del organismo administrador de la Ley 16.744 (ACHS, Mutual, IST o ISL).")

AVISO_MEDICIONES = ("Las mediciones deben hacerse con instrumentos calibrados y por personal competente. "
                    "Un numero mal medido aqui se convierte en una decision equivocada alla.")

AVISO_CRITICO = ("Hay al menos un valor fuera de rango con riesgo para las personas. La accion inmediata va "
                 "primero: ejecutala y despues documenta.")

FUENTES = [
    "DS 248/2007 del Ministerio de Mineria - Reglamento de depositos de relaves.",
    "DS 132/2002 del Ministerio de Mineria - Reglamento de Seguridad Minera (ultima version 09-04-2024).",
    "DS 594/1999 del Ministerio de Salud - condiciones sanitarias y ambientales basicas en los lugares de "
    "trabajo (texto vigente al 16-01-2026; tablas de limites segun Decreto 123/2015).",
    "Ley 20.551 y DS 41/2012 del Ministerio de Mineria - cierre de faenas e instalaciones mineras.",
    "GISTM - Estandar Global de Gestion de Relaves para la Industria Minera (agosto de 2020).",
]

ARCHIVO_INFORME = "mineria-seguridad.html"

_SI = ("si", "s", "true", "verdadero", "1", "x", "yes")


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def _bandera(opciones, clave):
    valor = opciones.get(clave)
    if valor is True:
        return True
    if valor is None or valor is False:
        return False
    return str(valor).strip().lower() in _SI


def _numero(opciones, clave, nombre):
    valor = opciones.get(clave)
    if valor is None or valor is True:
        return None
    return motor_mineria._numero(valor, nombre)


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _advertencias(resultado):
    avisos = [AVISO_EXPERTO]
    if resultado.get("nivel_riesgo") == "critico":
        avisos.insert(0, AVISO_CRITICO)
    for clave in ("advertencias", "no_calculado", "no_verificado"):
        avisos.extend(resultado.get(clave) or [])
    return avisos


# --------------------------------------------------------------------------
# Acciones
# --------------------------------------------------------------------------

def relaves(opciones):
    """Revisa revancha, factor de seguridad, metodo constructivo y muro de partida."""
    resultado = motor_mineria.evaluar_relave(
        revancha_m=_valor(opciones, "revancha") or None,
        factor_seguridad=_valor(opciones, "factor_seguridad") or None,
        fase=_valor(opciones, "fase", "i"),
        metodo=_valor(opciones, "metodo") or None,
        revancha_diseno_m=_valor(opciones, "revancha_diseno") or None,
        altura_muro_m=_valor(opciones, "altura_muro") or None,
        altura_final_muro_m=_valor(opciones, "altura_final_muro") or None,
        altura_muro_partida_m=_valor(opciones, "muro_partida") or None,
    )
    resultado["mensaje"] = _mensaje_nivel(resultado)
    return Respuesta(resultado, advertencias=_advertencias(resultado), fuentes=FUENTES[:1])


def ventilacion(opciones):
    """Caudal minimo, oxigeno y gases de una labor subterranea (DS 132/2002)."""
    resultado = motor_mineria.evaluar_ventilacion(
        personas=_valor(opciones, "personas") or None,
        hp_diesel=_valor(opciones, "hp_diesel") or None,
        caudal_m3min=_valor(opciones, "caudal") or None,
        oxigeno_pct=_valor(opciones, "oxigeno") or None,
        velocidad_m_min=_valor(opciones, "velocidad") or None,
        co_ppm=_valor(opciones, "co") or None,
        nox_ppm=_valor(opciones, "nox") or None,
        aldehido_ppm=_valor(opciones, "aldehido") or None,
        co_escape_ppm=_valor(opciones, "co_escape") or None,
        nox_escape_ppm=_valor(opciones, "nox_escape") or None,
        co2_ppm=_valor(opciones, "co2") or None,
        caudal_diesel_fabricante=_valor(opciones, "caudal_diesel_fabricante") or None,
        perdidas_pct=_valor(opciones, "perdidas") or None,
    )
    resultado["mensaje"] = _mensaje_nivel(resultado)
    return Respuesta(resultado, advertencias=_advertencias(resultado) + [AVISO_MEDICIONES],
                     fuentes=FUENTES[1:2])


def exposicion(opciones):
    """Compara una concentracion medida con el limite del DS 594 ya corregido."""
    if _bandera(opciones, "listar") or not _valor(opciones, "agente"):
        catalogo = motor_mineria.agentes_disponibles()
        if not _valor(opciones, "agente"):
            return Respuesta(
                {"mensaje": "Dime que agente quieres evaluar y la concentracion medida.",
                 "agentes": catalogo,
                 "ejemplo": ("mineria exposicion --agente \"Silice cristalizada - cuarzo\" "
                             "--concentracion 0.05 --unidad mg/m3 --horas 12 --altitud 3800 --presion 475"),
                 "nota": ("Solo tengo cargados los limites del art. 66 del DS 594 que la investigacion "
                          "verifico. Si necesitas otro agente, hay que verificarlo antes: no invento "
                          "limites.")},
                advertencias=[AVISO_EXPERTO])
        return Respuesta({"agentes": catalogo}, advertencias=[AVISO_EXPERTO])

    resultado = motor_mineria.evaluar_exposicion(
        agente=_valor(opciones, "agente"),
        concentracion=_valor(opciones, "concentracion") or None,
        unidad=_valor(opciones, "unidad") or None,
        tipo=_valor(opciones, "tipo", "ponderado"),
        horas_diarias=_valor(opciones, "horas") or None,
        horas_semanales=_valor(opciones, "horas_semana") or None,
        presion_mmhg=_valor(opciones, "presion") or None,
        altitud_m=_valor(opciones, "altitud") or None,
        estimar_presion=_bandera(opciones, "estimar_presion"),
    )
    resultado["mensaje"] = "%s: %s del limite corregido." % (
        resultado["agente"],
        ("%s %%" % motor_mineria._texto_numero(resultado["porcentaje_del_limite"]))
        if resultado["porcentaje_del_limite"] is not None else "no pude calcular el porcentaje")
    return Respuesta(resultado, advertencias=_advertencias(resultado) + [AVISO_MEDICIONES],
                     fuentes=FUENTES[2:3])


def cierre(opciones):
    """Lista de verificacion del plan de cierre y de su garantia (Ley 20.551)."""
    resultado = motor_mineria.plan_cierre(
        toneladas_mes=_valor(opciones, "toneladas_mes") or None,
        tiene_planta=_bandera(opciones, "planta"),
        tiene_relaves=_bandera(opciones, "deposito_relaves"),
        vida_util_anios=_valor(opciones, "vida_util") or None,
    )
    return Respuesta(resultado, advertencias=[AVISO_EXPERTO] + resultado["no_verificado"],
                     fuentes=FUENTES[3:4])


def gistm(opciones):
    """Conformidad con el GISTM sobre sus 77 requisitos auditables."""
    principios = _valor(opciones, "principios")
    lista = [p for p in str(principios).replace(";", ",").split(",") if p.strip()] if principios else []
    resultado = motor_mineria.evaluar_gistm(
        clasificacion=_valor(opciones, "clasificacion") or None,
        requisitos_conformes=_valor(opciones, "requisitos") or None,
        poblacion_en_riesgo=_valor(opciones, "poblacion") or None,
        miembro_icmm=_bandera(opciones, "miembro_icmm"),
        principios_cubiertos=lista,
    )
    return Respuesta(resultado, advertencias=[AVISO_EXPERTO] + resultado["advertencias"]
                     + resultado["no_verificado"], fuentes=FUENTES[4:5])


def _mensaje_nivel(resultado):
    nivel = resultado.get("nivel_riesgo")
    acciones = resultado.get("acciones_inmediatas") or []
    if acciones:
        return acciones[0]
    if nivel == "conforme":
        return "Todo lo que pude revisar cumple la norma."
    if nivel == "alerta":
        return "Cumple lo minimo legal, pero hay algo que conviene corregir antes de que se transforme en problema."
    return "Me faltan datos para decidir si cumple. Te digo cuales en «hallazgos»."


# --------------------------------------------------------------------------
# Informe HTML
# --------------------------------------------------------------------------

_COLOR_NIVEL = {"critico": "rojo", "alerta": "amarillo", "conforme": "verde", "sin_evaluar": "gris"}
_TEXTO_NIVEL = {"critico": "Critico", "alerta": "Atencion", "conforme": "Cumple", "sin_evaluar": "Sin datos"}


def _bloques_hallazgos(titulo, resultado):
    bloques = [{"tipo": "titulo", "texto": titulo, "nivel": 2}]
    for accion in resultado.get("acciones_inmediatas") or []:
        bloques.append({"tipo": "nota", "estilo": "riesgo", "texto": accion})
    bloques.append({"tipo": "semaforo", "items": [
        {"etiqueta": h["tema"],
         "estado": _COLOR_NIVEL.get(h["nivel"], "gris"),
         "estado_texto": _TEXTO_NIVEL.get(h["nivel"], "Sin datos"),
         "detalle": "Exigido: %s. Medido: %s. %s (%s)"
                    % (h["exigido"], h["medido"], h["explicacion"], h["articulo"])}
        for h in resultado.get("hallazgos", [])]})
    return bloques


def informe_html(opciones):
    """Arma un informe HTML con lo que se haya podido evaluar."""
    perfil, ruta = _contexto(opciones)
    bloques = [
        {"tipo": "texto", "texto": "Revision de cumplimiento en seguridad minera con las normas chilenas "
                                   "vigentes. Cada hallazgo indica el articulo del que sale la exigencia."},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_EXPERTO},
    ]
    secciones = []
    criticos = []

    if _valor(opciones, "personas"):
        resultado = ventilacion(opciones).resultado
        secciones.append(("Ventilacion subterranea (DS 132/2002)", resultado))
        caudal = resultado["caudal"]
        bloques.extend(_bloques_hallazgos("Ventilacion subterranea (DS 132/2002)", resultado))
        bloques.append({"tipo": "kpi", "items": [
            {"etiqueta": "Caudal exigido", "valor": round(caudal["caudal_exigido_m3min"], 1),
             "unidad": "m3/min", "detalle": "3 m3/min por persona + 2,83 m3/min por HP diesel"},
            {"etiqueta": "Caudal medido", "valor": caudal["caudal_medido_m3min"], "unidad": "m3/min",
             "detalle": "Arts. 132 y 138 del DS 132/2002",
             "color": "rojo" if (caudal["diferencia_m3min"] is not None
                                 and caudal["diferencia_m3min"] < 0) else "verde"},
            {"etiqueta": "Personas en el sector", "valor": caudal["personas"], "unidad": "",
             "detalle": "Art. 138 del DS 132/2002"},
        ]})

    if _valor(opciones, "revancha") or _valor(opciones, "factor_seguridad") or _valor(opciones, "metodo"):
        resultado = relaves(opciones).resultado
        secciones.append(("Deposito de relaves (DS 248/2007)", resultado))
        bloques.extend(_bloques_hallazgos("Deposito de relaves (DS 248/2007)", resultado))

    if _valor(opciones, "agente"):
        resultado = exposicion(opciones).resultado
        secciones.append(("Exposicion ocupacional (DS 594/1999)", resultado))
        bloques.append({"tipo": "titulo", "texto": "Exposicion ocupacional (DS 594/1999)", "nivel": 2})
        for accion in resultado["acciones_inmediatas"]:
            bloques.append({"tipo": "nota", "estilo": "riesgo", "texto": accion})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Agente", "Medido", "Limite de tabla", "Fj", "Fa",
                                     "Limite corregido", "% del limite", "Estado"],
                        "numericas": [1, 2, 3, 4, 5, 6],
                        "filas": [[resultado["agente"], resultado["concentracion"],
                                   resultado["limite_tabla"], resultado["factores"]["fj"],
                                   resultado["factores"]["fa"], resultado["limite_corregido"],
                                   resultado["porcentaje_del_limite"], resultado["estado"]]],
                        "nota": "Arts. 62, 63 y 64 del DS 594/1999. Unidad: %s." % resultado["unidad"]})

    if _valor(opciones, "toneladas_mes"):
        resultado = cierre(opciones).resultado
        secciones.append(("Plan de cierre (Ley 20.551)", resultado))
        bloques.append({"tipo": "titulo", "texto": "Plan de cierre (Ley 20.551)", "nivel": 2})
        bloques.append({"tipo": "texto", "texto": resultado["mensaje"]})
        bloques.append({"tipo": "tabla", "columnas": ["Letra", "Contenido minimo del plan", "Articulo"],
                        "filas": [[c["letra"], c["item"], c["articulo"]]
                                  for c in resultado["contenido_minimo"]],
                        "nota": resultado["nota_contenido"]})

    if _valor(opciones, "clasificacion") or _valor(opciones, "requisitos") or _valor(opciones, "poblacion"):
        resultado = gistm(opciones).resultado
        secciones.append(("GISTM", resultado))
        bloques.append({"tipo": "titulo", "texto": "GISTM - Estandar Global de Gestion de Relaves",
                        "nivel": 2})
        bloques.append({"tipo": "texto", "texto": resultado.get("mensaje", "")})
        if resultado.get("porcentaje_conformidad") is not None:
            bloques.append({"tipo": "kpi", "items": [
                {"etiqueta": "Conformidad", "valor": resultado["porcentaje_conformidad"], "unidad": "%",
                 "detalle": "%s de 77 requisitos auditables" % resultado["requisitos_conformes"]},
                {"etiqueta": "Requisitos pendientes", "valor": resultado["requisitos_pendientes"],
                 "unidad": "", "detalle": "Se cuentan con los Conformance Protocols de ICMM"},
            ]})
        if resultado.get("criterios_diseno"):
            criterios = resultado["criterios_diseno"]
            bloques.append({"tipo": "tabla",
                            "columnas": ["Clasificacion", "Crecidas operacion y cierre",
                                         "Crecidas poscierre", "Sismico operacion y cierre",
                                         "Sismico poscierre"],
                            "filas": [[criterios["clasificacion"],
                                       criterios["crecidas_operacion_y_cierre"],
                                       criterios["crecidas_poscierre"],
                                       criterios["sismico_operacion_y_cierre"],
                                       criterios["sismico_poscierre"]]],
                            "nota": "Probabilidad anual de excedencia para el diseno (Anexo 1 del GISTM)."})

    if not secciones:
        raise Problema(
            "No me diste ningun dato que evaluar, asi que no hay informe que armar.",
            "Agrega al menos uno: --personas para ventilacion, --revancha o --factor-seguridad para "
            "relaves, --agente y --concentracion para exposicion, --toneladas-mes para cierre, o "
            "--clasificacion para GISTM.",
        )

    for titulo, resultado in secciones:
        criticos.extend(resultado.get("acciones_inmediatas") or [])
        pendientes = list(resultado.get("no_verificado") or []) + list(resultado.get("no_calculado") or [])
        if pendientes:
            bloques.append({"tipo": "titulo", "texto": "Lo que NO calculo aqui: %s" % titulo, "nivel": 3})
            bloques.append({"tipo": "lista", "items": pendientes})

    bloques.insert(2, {"tipo": "nota", "estilo": "riesgo" if criticos else "exito",
                       "texto": (criticos[0] if criticos else
                                 "No detecte valores fuera de rango en lo que pude revisar.")})
    bloques.append({"tipo": "nota", "estilo": "info", "texto": motor_mineria.AVISO_SIN_TARP})
    bloques.append({"tipo": "nota", "estilo": "aviso", "texto": AVISO_MEDICIONES})

    destino = espacio.ruta_de(ruta, "reportes", ARCHIVO_INFORME)
    informe.escribir_html(
        destino, "Seguridad minera - revision de cumplimiento", bloques,
        marca=perfil.get("marca") or {},
        subtitulo="%s - %s" % (perfil.get("nombre", ""), datetime.date.today().strftime("%d-%m-%Y")))
    return Respuesta(
        {"mensaje": "Informe de seguridad minera listo.", "archivo": destino,
         "secciones": [titulo for titulo, _ in secciones],
         "acciones_inmediatas": criticos},
        advertencias=([AVISO_CRITICO] if criticos else []) + [AVISO_EXPERTO],
        fuentes=FUENTES)


ACCIONES = {
    "relaves": relaves,
    "ventilacion": ventilacion,
    "exposicion": exposicion,
    "cierre": cierre,
    "gistm": gistm,
    "informe": informe_html,
}
