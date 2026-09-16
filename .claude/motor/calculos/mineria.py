# -*- coding: utf-8 -*-
"""Mineria en Chile: relaves, ventilacion subterranea, exposicion ocupacional, cierre y GISTM.

Este modulo puede generar alertas de seguridad para personas. Regla de la casa:
ningun valor se inventa. Si la investigacion normativa no verifico un numero, la
funcion lo dice y NO calcula. Ante duda se falla hacia el lado protector.

Normas implementadas y de donde sale cada formula:

DS 248/2007 (Min. Mineria) - depositos de relaves
    Art. 14 letra o)  Factor de seguridad minimo 1,2 para las fases I y II del
                      analisis de estabilidad (simulaciones estaticas o
                      pseudo-estaticas). "El factor de Seguridad resultante del
                      calculo de las fases anteriores, no debe ser menor de uno
                      coma dos (1,2)."
                      Los depositos pequenos (muro menor de 15 m) que cumplen
                      esa condicion no necesitan la fase III.
    Art. 14 letra h)  Prohibicion absoluta del metodo aguas arriba.
    Art. 14 letra p)  Sismo de diseno desde estadisticas de zonas sismogenicas.
                      El reglamento NO fija un coeficiente sismico numerico.
    Art. 49           Revancha minima de 1 metro (piso absoluto, no un objetivo).
    Art. 54           Muro de partida: max(0,10 x altura final, 2 m).
    Art. 30           Informe trimestral a SERNAGEOMIN.
    Art. 34 y 35      Manual de Emergencias y notificacion inmediata al Servicio.

DS 132/2002 (Min. Mineria) - Reglamento de Seguridad Minera
    Art. 138          3 m3/min de aire fresco por persona; velocidad media del
                      aire entre 15 y 150 m/min.
    Art. 132          2,83 m3/min por HP efectivo al freno de equipo diesel
                      cuando el fabricante no especifica el caudal. Inciso 2: el
                      caudal de los diesel SIEMPRE se SUMA al de las personas.
    Art. 144          Oxigeno minimo 19,5 % en peso y retiro obligatorio del
                      trabajador mientras no se normalicen las condiciones, lo
                      que debe certificar personal calificado y autorizado.
    Art. 135 a)       Detencion del equipo diesel: CO 40 ppm, NOx 20 ppm y
                      aldehido formico 1,6 ppm en el ambiente. El resto de los
                      contaminantes se rige por el DS 594.
    Art. 135 b)       Detencion por gases en el escape: CO sobre 2.000 ppm y
                      NOx sobre 1.000 ppm.
    Art. 139          Perdidas de ventilacion toleradas hasta 15 %; aforo
                      trimestral de entradas y salidas; control general semestral.

DS 594/1999 (MINSAL) - limites permisibles (texto vigente al 16-01-2026)
    Art. 60           El promedio ponderado no puede superar el LPP. Las
                      excedencias momentaneas NUNCA pueden superar 5 veces su
                      valor, no mas de 4 veces en la jornada ni mas de 1 vez por
                      hora.
    Art. 62           Correccion por jornada DIARIA (texto segun Decreto
                      123/2015): Fj = (8 / h) x ((24 - h) / 16), solo si h > 8.
                      Caso especial: jornada de 8 h diarias con semana mayor a
                      45 h y hasta 48 h, Fj = 0,90.
                      La antigua formula semanal (48/h)x((168-h)/120) esta
                      DEROGADA desde 2015: usarla subestima el riesgo.
    Art. 63           Correccion por altitud: Fa = P / 760, con P = presion
                      atmosferica local MEDIDA en mmHg, solo sobre 1.000 m
                      s.n.m. y solo sobre valores en mg/m3 y fibras/cc.
    Art. 64           LPP corregido = LPP x Fj x Fa. Los limites temporales y
                      absolutos se corrigen SOLO por Fa, nunca por Fj.
    Redondeo          Fj y Fa se expresan con dos decimales; el segundo decimal
                      se eleva si el tercero es igual o mayor que 5. No se
                      admiten aproximaciones parciales (Arts. 62 y 63).

GISTM (Estandar Global de Gestion de Relaves, agosto de 2020)
    77 requisitos auditables agrupados en 15 principios y 6 temas. Anexo 1 con
    los criterios de diseno por clasificacion y Anexo 2 con la matriz de
    clasificacion por consecuencias.

Ley 20.551 y DS 41/2012 - cierre de faenas mineras
    Arts. 10 y 16     Umbrales de regimen: general sobre 10.000 t brutas
                      mensuales; simplificado hasta 10.000 t; declaracion
                      simplificada hasta 5.000 t sin planta ni relaves.
    Art. 13           Contenido minimo del plan de cierre.
    Arts. 50 a 52     Garantia financiera, tasa BCU-10 e instrumentos A.1.
    Art. 51           3 dias habiles para informar contingencias de la garantia;
                      30 dias para que el Servicio resuelva.
    Art. 18           Auditoria cada 5 anios, a costa de la empresa.
    Art. 23           90 dias para presentar la actualizacion del plan; 60 dias
                      para que el Servicio resuelva.

Lo que este modulo NO calcula, porque la investigacion no lo verifico:

- Un factor de seguridad estatico distinto de 1,2 (1,4 o 1,5 de la practica
  internacional CDA/ANCOLD). El DS 248 solo fija 1,2 y no se verifico otro.
- El factor de seguridad de la fase III (analisis dinamicos) ni el de la fase IV
  (condicion de cierre): el DS 248 no les fija un valor numerico propio.
- Un coeficiente sismico numerico para el diseno (Art. 14 letra p).
- Los limites permisibles absolutos del Art. 61: esa tabla no esta digitalizada.
- La progresion de las parcialidades de la garantia de cierre: la guia de
  SERNAGEOMIN se leyo con OCR degradado.
- La presion atmosferica a partir de la altitud: el DS 594 exige presion MEDIDA
  y no entrega formula. Hay una estimacion opcional, marcada como tal.

Aviso sobre niveles de alerta escalonados: ni el DS 248 ni el DS 132 contienen
niveles tipo TARP (verde / amarillo / naranja / rojo). Se verifico por ausencia
sobre el texto completo de ambos reglamentos. Lo que existe es un esquema
binario: detener el equipo (Art. 135 DS 132) y retirar al trabajador (Art. 144
DS 132). El TARP es buena practica del GISTM, no exigencia chilena.
"""

import csv
import os
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_LIMITES = os.path.join(CARPETA_DATOS, "limites_exposicion_cl.csv")

# --------------------------------------------------------------------------
# Constantes normativas (cada una con su articulo)
# --------------------------------------------------------------------------

# DS 248/2007 - depositos de relaves
FS_MINIMO = 1.2                       # Art. 14 letra o)
REVANCHA_MINIMA_M = 1.0               # Art. 49
ALTURA_DEPOSITO_PEQUENO_M = 15.0      # Art. 14 letra o)
MURO_PARTIDA_FRACCION = 0.10          # Art. 54
MURO_PARTIDA_MINIMO_M = 2.0           # Art. 54

# DS 132/2002 - ventilacion en mineria subterranea
CAUDAL_POR_PERSONA_M3MIN = 3.0        # Art. 138
CAUDAL_POR_HP_DIESEL_M3MIN = 2.83     # Art. 132
VELOCIDAD_MINIMA_M_MIN = 15.0         # Art. 138
VELOCIDAD_MAXIMA_M_MIN = 150.0        # Art. 138
OXIGENO_MINIMO_PCT = 19.5             # Art. 144
PERDIDAS_MAXIMAS_PCT = 15.0           # Art. 139

# Art. 135 letra a): concentraciones ambientales que obligan a detener el equipo
# diesel. El reglamento las enuncia como "valor maximo": el motor aplica el
# criterio conservador de detener cuando la medicion alcanza el valor.
GASES_DETENCION_AMBIENTE_PPM = {
    "co": {"valor": 40.0, "nombre": "monoxido de carbono (CO)"},
    "nox": {"valor": 20.0, "nombre": "oxidos de nitrogeno (NOx)"},
    "aldehido": {"valor": 1.6, "nombre": "aldehido formico (formaldehido)"},
}
# Art. 135 letra b): medicion en el tubo de escape, enunciada con "mas de".
GASES_DETENCION_ESCAPE_PPM = {
    "co": {"valor": 2000.0, "nombre": "monoxido de carbono (CO) en el escape"},
    "nox": {"valor": 1000.0, "nombre": "oxidos de nitrogeno (NOx) en el escape"},
}

# DS 594/1999 - correcciones
JORNADA_ORDINARIA_H = 8.0             # Art. 62
FJ_JORNADA_8H_SEMANA_LARGA = 0.90     # Art. 62 inciso 2
PRESION_NIVEL_MAR_MMHG = 760.0        # Art. 63
ALTITUD_CORRECCION_M = 1000.0         # Art. 63
FACTOR_TECHO_ART_60 = 5.0             # Art. 60
MAX_EXCURSIONES_JORNADA = 4           # Art. 60
MAX_EXCURSIONES_HORA = 1              # Art. 60

TIPOS_LIMITE = {
    "ponderado": "LPP - promedio ponderado de la jornada (art. 59)",
    "temporal": "LPT - promedio de 15 minutos continuos (art. 59)",
    "absoluto": "LPA - concentracion medida en cualquier momento (art. 59)",
}

# GISTM
GISTM_TOTAL_REQUISITOS = 77           # total oficial ICMM / Global Tailings Review
GISTM_TOTAL_PRINCIPIOS = 15
GISTM_TOTAL_TEMAS = 6
GISTM_CRITERIOS_PROTOCOLO_ICMM = 219

# Ley 20.551 - cierre
UMBRAL_REGIMEN_GENERAL_T_MES = 10000.0     # Art. 10
UMBRAL_DECLARACION_SIMPLE_T_MES = 5000.0   # Art. 16
VIDA_UTIL_CORTE_ANIOS = 20.0               # guia de garantias de SERNAGEOMIN
PLAZO_GARANTIA_VIDA_LARGA_ANIOS = 15.0

NORMA_RELAVES = "DS 248/2007 del Ministerio de Mineria (Reglamento de depositos de relaves)"
NORMA_VENTILACION = "DS 132/2002 del Ministerio de Mineria (Reglamento de Seguridad Minera)"
NORMA_EXPOSICION = "DS 594/1999 del Ministerio de Salud, texto vigente al 16-01-2026"
NORMA_CIERRE = "Ley 20.551 y su reglamento DS 41/2012 del Ministerio de Mineria"
NORMA_GISTM = "GISTM - Estandar Global de Gestion de Relaves para la Industria Minera (agosto de 2020)"

AVISO_SIN_TARP = ("Ni el DS 248 ni el DS 132 tienen niveles de alerta escalonados tipo TARP. Lo que existe "
                  "es un esquema binario: detener el equipo (art. 135 DS 132) y retirar al trabajador "
                  "(art. 144 DS 132). Un TARP con umbrales verde, amarillo y rojo es buena practica del "
                  "GISTM, no una exigencia chilena.")

_ORDEN_NIVELES = {"conforme": 0, "sin_evaluar": 1, "alerta": 2, "critico": 3}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _clave(texto):
    """Convierte 'Silice cristalizada - cuarzo' en 'silice_cristalizada_cuarzo'."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def _numero(valor, nombre, minimo=None, maximo=None, sugerencia=""):
    """Lee un numero escrito como 1250, 1250.5 o 1250,5. None si viene vacio."""
    if valor is None or valor is True or (isinstance(valor, str) and not valor.strip()):
        return None
    texto = str(valor).strip()
    if re.match(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$", texto):   # 1.250,5 al estilo chileno
        texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    try:
        numero = float(texto)
    except ValueError:
        raise Problema(
            "El valor de %s («%s») no es un numero." % (nombre, valor),
            sugerencia or "Escribe solo el numero, sin la unidad ni texto.",
        )
    if minimo is not None and numero < minimo:
        raise Problema(
            "%s no puede ser menor que %s (recibi %s)." % (nombre.capitalize(), _texto_numero(minimo), texto),
            sugerencia or "Revisa el dato: de este calculo depende la seguridad de personas.",
        )
    if maximo is not None and numero > maximo:
        raise Problema(
            "%s no puede ser mayor que %s (recibi %s)." % (nombre.capitalize(), _texto_numero(maximo), texto),
            sugerencia or "Revisa el dato y la unidad de medida.",
        )
    return numero


def _texto_numero(valor):
    if valor is None:
        return "sin dato"
    if float(valor) == int(float(valor)):
        return str(int(float(valor)))
    return ("%.4f" % float(valor)).rstrip("0").rstrip(".")


def _dos_decimales(valor):
    """Redondeo del DS 594: dos decimales, el segundo sube si el tercero es >= 5."""
    return float(Decimal(repr(float(valor))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _peor(niveles):
    peor = "conforme"
    for nivel in niveles:
        if _ORDEN_NIVELES.get(nivel, 0) > _ORDEN_NIVELES[peor]:
            peor = nivel
    return peor


def _hallazgo(tema, nivel, exigido, medido, articulo, explicacion, accion=""):
    return {"tema": tema, "nivel": nivel, "exigido": exigido, "medido": medido,
            "articulo": articulo, "explicacion": explicacion, "accion": accion}


# --------------------------------------------------------------------------
# Tabla de limites permisibles del DS 594
# --------------------------------------------------------------------------

def _unidad_normalizada(unidad):
    clave = _clave(unidad)
    if clave in ("ppm",):
        return "ppm"
    if clave in ("mg_m3", "mgm3", "mg_m", "mg_metro_cubico", "mg_m3_", "mg"):
        return "mg/m3"
    if clave in ("fibras_cc", "fibrascc", "f_cc"):
        return "fibras/cc"
    return _clave(unidad) or ""


def cargar_limites(ruta=None):
    """Lee la tabla de limites permisibles del DS 594 (art. 66)."""
    ruta = ruta or ARCHIVO_LIMITES
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro la tabla de limites permisibles (%s)." % os.path.basename(ruta),
            "Sin esa tabla no puedo decirte cual es el limite legal, y no voy a inventar uno. "
            "Avisa para reinstalar los datos del motor.",
        )
    filas = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for linea, fila in enumerate(csv.DictReader(archivo), start=2):
            agente = (fila.get("agente") or "").strip()
            if not agente:
                continue
            filas.append({
                "agente": agente,
                "clave": _clave(agente),
                "lpp": _numero(fila.get("lpp"), "el LPP de %s" % agente, minimo=0),
                "lpt": _numero(fila.get("lpt"), "el LPT de %s" % agente, minimo=0),
                "unidad": (fila.get("unidad") or "").strip(),
                "carcinogeno": (fila.get("carcinogeno") or "").strip(),
                "articulo": (fila.get("articulo") or "").strip(),
                "fuente": (fila.get("fuente") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
                "linea": linea,
            })
    if not filas:
        raise Problema(
            "La tabla de limites permisibles esta vacia.",
            "No voy a comparar contra un limite inventado. Avisa para reinstalar los datos del motor.",
        )
    return filas


def agentes_disponibles(limites=None):
    """Lista de agentes cargados, con las unidades en que esta cada uno."""
    limites = limites or cargar_limites()
    catalogo = {}
    for fila in limites:
        catalogo.setdefault(fila["agente"], []).append(fila["unidad"])
    return [{"agente": nombre, "unidades": unidades} for nombre, unidades in sorted(catalogo.items())]


def buscar_limite(agente, unidad=None, limites=None):
    """Busca un agente en la tabla del art. 66. Nunca adivina entre dos candidatos."""
    limites = limites or cargar_limites()
    buscado = _clave(agente)
    if not buscado:
        raise Problema(
            "No me dijiste que agente quieres evaluar.",
            "Agentes cargados: %s." % ", ".join(a["agente"] for a in agentes_disponibles(limites)),
        )
    candidatos = [f for f in limites if f["clave"] == buscado]
    if not candidatos:
        candidatos = [f for f in limites if buscado in f["clave"] or f["clave"] in buscado]
    if not candidatos:
        palabras = [p for p in buscado.split("_") if len(p) > 3]
        candidatos = [f for f in limites if palabras and all(p in f["clave"] for p in palabras)]
    if not candidatos:
        raise Problema(
            "No tengo cargado el limite permisible de «%s»." % agente,
            "No voy a inventar un limite: de esto depende la salud de personas. Agentes cargados: %s. "
            "Si necesitas otro, hay que verificarlo en la tabla del art. 66 del DS 594 antes de usarlo."
            % ", ".join(a["agente"] for a in agentes_disponibles(limites)),
        )
    if unidad:
        pedida = _unidad_normalizada(unidad)
        filtrados = [f for f in candidatos if _unidad_normalizada(f["unidad"]) == pedida]
        if not filtrados:
            raise Problema(
                "Tengo el limite de «%s» pero no en %s." % (candidatos[0]["agente"], unidad),
                "Lo tengo en: %s. Mide en esa unidad o convierte el resultado con tu laboratorio; "
                "yo no convierto entre ppm y mg/m3 porque el DS 594 publica cada valor por separado."
                % ", ".join(sorted({f["unidad"] for f in candidatos})),
            )
        candidatos = filtrados
    if len(candidatos) > 1:
        raise Problema(
            "«%s» corresponde a mas de una fila de la tabla y no quiero elegir por ti." % agente,
            "Indica cual: %s." % "; ".join("%s en %s" % (f["agente"], f["unidad"]) for f in candidatos),
        )
    return candidatos[0]


def _texto_carcinogeno(codigo):
    codigo = (codigo or "").strip()
    if not codigo or codigo.lower() in ("no", "-", "n/a"):
        return ""
    if codigo.upper() == "A.1":
        return ("El DS 594 lo clasifica A.1: cancerigeno comprobado para el ser humano (art. 68). "
                "Cumplir el limite no vuelve segura la exposicion: hay que reducirla al minimo posible "
                "y acordar la vigilancia de la salud con el organismo administrador de la Ley 16.744.")
    return ("El DS 594 lo clasifica %s en la escala de evidencia cancerigena del art. 68 (A.1 es la "
            "categoria mas fuerte y A.4 la mas debil). Conviene mantener la exposicion lo mas baja "
            "posible y conversarlo con el organismo administrador de la Ley 16.744." % codigo.upper())


# --------------------------------------------------------------------------
# 1. Depositos de relaves - DS 248/2007
# --------------------------------------------------------------------------

FASES_ESTABILIDAD = {
    "i": {
        "nombre": "Fase I - estabilidad estatica (analisis pseudo-estaticos) asumiendo licuefaccion "
                  "total de los relaves de la cubeta",
        "fs_minimo": FS_MINIMO,
        "articulo": "Art. 14 letra o) del DS 248/2007",
    },
    "ii": {
        "nombre": "Fase II - estabilidad estatica (analisis pseudo-estaticos) con determinacion "
                  "simplificada de las presiones de poros",
        "fs_minimo": FS_MINIMO,
        "articulo": "Art. 14 letra o) del DS 248/2007",
    },
    "iii": {
        "nombre": "Fase III - analisis dinamicos basados en ensayos de propiedades dinamicas de los suelos",
        "fs_minimo": None,
        "articulo": "Art. 14 letra o) del DS 248/2007",
    },
    "iv": {
        "nombre": "Fase IV - analisis para la condicion de cierre, con los eventos solicitantes maximos",
        "fs_minimo": None,
        "articulo": "Art. 14 letra o) del DS 248/2007",
    },
}

_ALIAS_FASES = {
    "1": "i", "2": "ii", "3": "iii", "4": "iv",
    "fase_i": "i", "fase_ii": "ii", "fase_iii": "iii", "fase_iv": "iv",
    "estatico": "ii", "estatica": "ii", "pseudoestatico": "i", "pseudo_estatico": "i",
    "licuefaccion": "i", "sismico": "iii", "sismica": "iii", "dinamico": "iii", "dinamica": "iii",
    "cierre": "iv",
}

METODOS_CONSTRUCTIVOS = {
    "aguas_arriba": {
        "nombre": "aguas arriba (upstream)",
        "permitido": False,
        "articulo": "Art. 14 letra h) del DS 248/2007",
        "detalle": ("El DS 248 dice: «Se prohibe la utilizacion del metodo aguas arriba». Es la unica "
                    "mencion del metodo en todo el reglamento, o sea que la prohibicion no tiene "
                    "excepciones escritas."),
    },
    "aguas_abajo": {
        "nombre": "aguas abajo (downstream)",
        "permitido": True,
        "articulo": "DS 248/2007 (no lo prohibe)",
        "detalle": "El DS 248 no lo prohibe. Igual debe cumplir el factor de seguridad y la revancha.",
    },
    "eje_central": {
        "nombre": "eje central (centerline)",
        "permitido": True,
        "articulo": "DS 248/2007 (no lo prohibe)",
        "detalle": "El DS 248 no lo prohibe. Igual debe cumplir el factor de seguridad y la revancha.",
    },
}

_ALIAS_METODOS = {
    "upstream": "aguas_arriba", "arriba": "aguas_arriba", "aguas_arriba": "aguas_arriba",
    "downstream": "aguas_abajo", "abajo": "aguas_abajo", "aguas_abajo": "aguas_abajo",
    "centerline": "eje_central", "eje_central": "eje_central", "central": "eje_central",
    "linea_central": "eje_central",
}

NO_VERIFICADO_RELAVES = [
    "No esta verificado que el DS 248 exija un factor de seguridad estatico distinto de 1,2 (la practica "
    "internacional CDA y ANCOLD usa 1,4 o 1,5). No lo trates como exigencia chilena mientras no lo "
    "confirmes en el texto del art. 14 o con SERNAGEOMIN.",
    "El DS 248 no fija un factor de seguridad numerico para la fase III (analisis dinamicos) ni para la "
    "fase IV (condicion de cierre): el criterio lo define el proyecto aprobado y su revisor.",
    "El art. 14 letra p) exige obtener el sismo de diseno de las estadisticas de zonas sismogenicas, pero "
    "no fija un coeficiente sismico numerico. No uses un valor de referencia como si fuera la norma.",
    "Desde 2024 hay en tramite un reglamento que reemplazaria al DS 248 (consulta publica de la Res. Ex. "
    "1706/2024). No se verifico su publicacion: mientras tanto rige el DS 248/2007 original.",
]


def _fase_valida(fase):
    clave = _clave(fase) or "i"
    clave = _ALIAS_FASES.get(clave, clave)
    if clave not in FASES_ESTABILIDAD:
        raise Problema(
            "No reconozco la fase de analisis «%s»." % fase,
            "Usa i, ii, iii o iv (tambien acepto: estatico, pseudoestatico, sismico, dinamico o cierre). "
            "Son las cuatro fases del art. 14 letra o) del DS 248.",
        )
    return clave


def _metodo_valido(metodo):
    if metodo is None or metodo is True or not str(metodo).strip():
        return None
    clave = _clave(metodo)
    clave = _ALIAS_METODOS.get(clave, clave)
    if clave not in METODOS_CONSTRUCTIVOS:
        raise Problema(
            "No reconozco el metodo constructivo «%s»." % metodo,
            "Usa aguas_arriba, aguas_abajo o eje_central.",
        )
    return clave


def evaluar_relave(revancha_m=None, factor_seguridad=None, fase="i", metodo=None,
                   revancha_diseno_m=None, altura_muro_m=None, altura_final_muro_m=None,
                   altura_muro_partida_m=None):
    """Revisa un deposito de relaves contra el DS 248/2007.

    Revisa la revancha (art. 49), el factor de seguridad de la fase que se este
    analizando (art. 14 letra o), el metodo constructivo (art. 14 letra h) y el
    muro de partida (art. 54). Devuelve un nivel de riesgo con su explicacion.
    """
    clave_fase = _fase_valida(fase)
    datos_fase = FASES_ESTABILIDAD[clave_fase]
    clave_metodo = _metodo_valido(metodo)

    revancha_m = _numero(revancha_m, "la revancha", minimo=0,
                         sugerencia="La revancha es la altura libre entre el nivel de aguas y la "
                                    "coronacion del muro, en metros.")
    revancha_diseno_m = _numero(revancha_diseno_m, "la revancha de diseno", minimo=0)
    factor_seguridad = _numero(factor_seguridad, "el factor de seguridad", minimo=0)
    altura_muro_m = _numero(altura_muro_m, "la altura del muro", minimo=0)
    altura_final_muro_m = _numero(altura_final_muro_m, "la altura final del muro", minimo=0)
    altura_muro_partida_m = _numero(altura_muro_partida_m, "la altura del muro de partida", minimo=0)

    hallazgos = []
    acciones = []

    # Metodo constructivo - art. 14 letra h)
    if clave_metodo is None:
        hallazgos.append(_hallazgo(
            "Metodo constructivo", "sin_evaluar", "no puede ser aguas arriba", "sin dato",
            "Art. 14 letra h) del DS 248/2007",
            "No me dijiste con que metodo se levanta el muro. Es lo primero que hay que saber: el metodo "
            "aguas arriba esta prohibido en Chile.",
            "Pregunta al area de geotecnia o al Ingeniero de Registro cual es el metodo del deposito."))
    else:
        datos_metodo = METODOS_CONSTRUCTIVOS[clave_metodo]
        if not datos_metodo["permitido"]:
            accion = ("ACCION INMEDIATA: detener el peralte del muro y avisar hoy mismo a la "
                      "administracion de la faena y a SERNAGEOMIN. El metodo aguas arriba esta PROHIBIDO "
                      "por el art. 14 letra h) del DS 248/2007. Esto no se corrige con un informe: se "
                      "corrige cambiando el metodo constructivo con un proyecto aprobado.")
            acciones.append(accion)
            hallazgos.append(_hallazgo(
                "Metodo constructivo", "critico", "prohibido el metodo aguas arriba",
                datos_metodo["nombre"], datos_metodo["articulo"], datos_metodo["detalle"], accion))
        else:
            hallazgos.append(_hallazgo(
                "Metodo constructivo", "conforme", "no puede ser aguas arriba", datos_metodo["nombre"],
                datos_metodo["articulo"], datos_metodo["detalle"], ""))

    # Revancha - art. 49
    if revancha_m is None:
        hallazgos.append(_hallazgo(
            "Revancha", "sin_evaluar", "%s m como minimo" % _texto_numero(REVANCHA_MINIMA_M), "sin dato",
            "Art. 49 del DS 248/2007",
            "Sin la revancha medida no puedo decirte si el deposito esta dentro de la norma.",
            "Mide la altura libre entre el nivel de aguas claras y la coronacion del muro."))
    elif revancha_m < REVANCHA_MINIMA_M:
        accion = ("ACCION INMEDIATA: recupera la revancha antes de seguir depositando. Suspende el "
                  "deposito de relaves en la cubeta, evacua el agua clara y avisa a la administracion de "
                  "la faena. Si hay riesgo de rebalse, el art. 35 del DS 248 obliga a notificar de "
                  "inmediato a SERNAGEOMIN.")
        acciones.append(accion)
        hallazgos.append(_hallazgo(
            "Revancha", "critico", "%s m como minimo" % _texto_numero(REVANCHA_MINIMA_M),
            "%s m" % _texto_numero(revancha_m), "Art. 49 del DS 248/2007",
            "La revancha esta bajo el minimo legal de 1 metro. El art. 49 no admite excepciones: es un "
            "piso absoluto, y el propio articulo advierte que los fenomenos climaticos pueden exigir mas.",
            accion))
    elif revancha_diseno_m is not None and revancha_m < revancha_diseno_m:
        accion = ("Revisa el balance de aguas y recupera la revancha de diseno antes de la proxima "
                  "temporada de lluvias o deshielo.")
        hallazgos.append(_hallazgo(
            "Revancha", "alerta", "%s m de diseno (minimo legal 1 m)" % _texto_numero(revancha_diseno_m),
            "%s m" % _texto_numero(revancha_m), "Art. 49 del DS 248/2007",
            "Cumple el minimo legal de 1 metro pero esta bajo la revancha de diseno del proyecto. El "
            "metro del art. 49 es un piso absoluto, no un objetivo de operacion.", accion))
    else:
        hallazgos.append(_hallazgo(
            "Revancha", "conforme", "%s m como minimo" % _texto_numero(REVANCHA_MINIMA_M),
            "%s m" % _texto_numero(revancha_m), "Art. 49 del DS 248/2007",
            "Cumple el minimo del art. 49. Recuerda que 1 metro es el piso absoluto: el proyecto puede "
            "exigir mas por lluvias o deshielo.", ""))

    # Factor de seguridad - art. 14 letra o)
    fs_exigido = datos_fase["fs_minimo"]
    if factor_seguridad is None:
        hallazgos.append(_hallazgo(
            "Factor de seguridad (%s)" % clave_fase.upper(), "sin_evaluar",
            _texto_numero(fs_exigido) if fs_exigido else "sin valor verificado en el DS 248",
            "sin dato", datos_fase["articulo"],
            "No me diste el factor de seguridad calculado. %s" % datos_fase["nombre"],
            "Pidelo al Ingeniero de Registro o a la consultora geotecnica que hizo el analisis."))
    elif fs_exigido is None:
        hallazgos.append(_hallazgo(
            "Factor de seguridad (%s)" % clave_fase.upper(), "sin_evaluar",
            "sin valor verificado en el DS 248", _texto_numero(factor_seguridad), datos_fase["articulo"],
            "No voy a decirte si %s cumple: el DS 248 fija el minimo de 1,2 solo para las fases I y II. "
            "Para la %s el reglamento no tiene un numero propio verificado, asi que el criterio lo define "
            "el proyecto aprobado y su revisor. No invento un valor."
            % (_texto_numero(factor_seguridad), datos_fase["nombre"].split(" - ")[0]),
            "Compara este valor con el criterio del proyecto aprobado por SERNAGEOMIN."))
    elif factor_seguridad < fs_exigido:
        accion = ("ACCION INMEDIATA: avisa hoy a la administracion de la faena y al Ingeniero de Registro, "
                  "y detiene el crecimiento del muro hasta tener un analisis nuevo. Un factor de seguridad "
                  "bajo 1,2 no cumple el art. 14 letra o) del DS 248/2007.")
        acciones.append(accion)
        hallazgos.append(_hallazgo(
            "Factor de seguridad (%s)" % clave_fase.upper(), "critico",
            "no menor que %s" % _texto_numero(fs_exigido), _texto_numero(factor_seguridad),
            datos_fase["articulo"],
            "El DS 248 exige que el factor de seguridad de las fases I y II no sea menor que 1,2. "
            "Aqui esta por debajo. %s" % datos_fase["nombre"], accion))
    else:
        hallazgos.append(_hallazgo(
            "Factor de seguridad (%s)" % clave_fase.upper(), "conforme",
            "no menor que %s" % _texto_numero(fs_exigido), _texto_numero(factor_seguridad),
            datos_fase["articulo"],
            "Cumple el minimo de 1,2 del art. 14 letra o). %s" % datos_fase["nombre"], ""))

    # Exigencia de la fase III - art. 14 letra o)
    exige_fase_iii = None
    if altura_muro_m is not None or factor_seguridad is not None:
        exige_fase_iii = bool(
            (altura_muro_m is not None and altura_muro_m >= ALTURA_DEPOSITO_PEQUENO_M)
            or (factor_seguridad is not None and fs_exigido is not None and factor_seguridad < fs_exigido))
        if exige_fase_iii:
            hallazgos.append(_hallazgo(
                "Fase III (analisis dinamicos)", "alerta", "obligatoria",
                "muro de %s m" % _texto_numero(altura_muro_m) if altura_muro_m is not None else "sin dato",
                "Art. 14 letra o) del DS 248/2007",
                "La fase III solo se puede omitir en depositos pequenos, con muros de menos de 15 metros, "
                "que ademas cumplen el factor de seguridad de 1,2. Este deposito no esta en ese caso.",
                "Confirma con el Ingeniero de Registro que la fase III (analisis dinamicos con ensayos de "
                "propiedades dinamicas de los suelos) este hecha y vigente."))
        else:
            hallazgos.append(_hallazgo(
                "Fase III (analisis dinamicos)", "conforme", "se puede omitir",
                "muro de %s m" % _texto_numero(altura_muro_m) if altura_muro_m is not None else "sin dato",
                "Art. 14 letra o) del DS 248/2007",
                "Es un deposito pequeno (muro bajo 15 m) que cumple el factor de seguridad de 1,2, asi que "
                "el DS 248 permite no cumplir la fase III.", ""))

    # Muro de partida - art. 54
    if altura_final_muro_m is not None:
        minimo_partida = max(MURO_PARTIDA_FRACCION * altura_final_muro_m, MURO_PARTIDA_MINIMO_M)
        if altura_muro_partida_m is None:
            hallazgos.append(_hallazgo(
                "Muro de partida", "sin_evaluar", "%s m" % _texto_numero(minimo_partida), "sin dato",
                "Art. 54 del DS 248/2007",
                "Para una altura final de %s m, el muro de partida debe tener al menos %s m: un decimo de "
                "la altura final, con un piso de 2 metros."
                % (_texto_numero(altura_final_muro_m), _texto_numero(minimo_partida)),
                "Pide la altura del muro de partida al proyecto aprobado."))
        elif altura_muro_partida_m < minimo_partida:
            accion = ("Revisa el proyecto con geotecnia: el muro de partida esta bajo el minimo del "
                      "art. 54 del DS 248.")
            acciones.append(accion)
            hallazgos.append(_hallazgo(
                "Muro de partida", "critico", "%s m" % _texto_numero(minimo_partida),
                "%s m" % _texto_numero(altura_muro_partida_m), "Art. 54 del DS 248/2007",
                "El muro de partida debe tener como minimo un decimo de la altura final proyectada, y "
                "nunca menos de 2 metros.", accion))
        else:
            hallazgos.append(_hallazgo(
                "Muro de partida", "conforme", "%s m" % _texto_numero(minimo_partida),
                "%s m" % _texto_numero(altura_muro_partida_m), "Art. 54 del DS 248/2007",
                "Cumple el minimo del art. 54: un decimo de la altura final, con piso de 2 metros.", ""))

    nivel = _peor(h["nivel"] for h in hallazgos)
    return {
        "norma": NORMA_RELAVES,
        "fase_analizada": {"clave": clave_fase, "nombre": datos_fase["nombre"],
                           "fs_minimo": fs_exigido, "articulo": datos_fase["articulo"]},
        "metodo_constructivo": METODOS_CONSTRUCTIVOS[clave_metodo]["nombre"] if clave_metodo else None,
        "nivel_riesgo": nivel,
        "acciones_inmediatas": acciones,
        "hallazgos": hallazgos,
        "exige_fase_iii": exige_fase_iii,
        "obligaciones_permanentes": [
            "Informe trimestral a SERNAGEOMIN sobre la operacion y mantencion del deposito (art. 30).",
            "Manual de Emergencias del deposito elaborado y actualizado (art. 34).",
            "Notificacion inmediata al Servicio ante cualquier emergencia (art. 35).",
            "Instrumentacion para medir presiones de poros, niveles freaticos, desplazamientos y "
            "aceleraciones sismicas (art. 14 letra n).",
        ],
        "advertencias": [AVISO_SIN_TARP],
        "no_verificado": list(NO_VERIFICADO_RELAVES),
    }


# --------------------------------------------------------------------------
# 2. Ventilacion subterranea - DS 132/2002
# --------------------------------------------------------------------------

def evaluar_ventilacion(personas=None, hp_diesel=None, caudal_m3min=None, oxigeno_pct=None,
                        velocidad_m_min=None, co_ppm=None, nox_ppm=None, aldehido_ppm=None,
                        co_escape_ppm=None, nox_escape_ppm=None, co2_ppm=None,
                        caudal_diesel_fabricante=None, perdidas_pct=None, limites=None):
    """Caudal minimo, oxigeno y gases de una labor subterranea, segun el DS 132/2002.

    Caudal exigido (arts. 132 y 138):
        Q_personas = 3,0 m3/min x numero de personas
        Q_diesel   = 2,83 m3/min x HP efectivo al freno (si el fabricante no especifica)
        Q_minimo   = Q_personas + Q_diesel        <- siempre se suman, no es un maximo
    """
    personas = _numero(personas, "el numero de personas", minimo=0,
                       sugerencia="Cuenta a todas las personas que pueden estar en el sector a la vez.")
    hp_diesel = _numero(hp_diesel, "la potencia diesel", minimo=0,
                        sugerencia="Suma los HP efectivos al freno (BHP) de todos los equipos diesel del sector.")
    caudal_m3min = _numero(caudal_m3min, "el caudal medido", minimo=0)
    caudal_diesel_fabricante = _numero(caudal_diesel_fabricante, "el caudal que indica el fabricante", minimo=0)
    oxigeno_pct = _numero(oxigeno_pct, "el oxigeno", minimo=0, maximo=100,
                          sugerencia="El oxigeno se mide en porcentaje, entre 0 y 100.")
    velocidad_m_min = _numero(velocidad_m_min, "la velocidad del aire", minimo=0)
    perdidas_pct = _numero(perdidas_pct, "las perdidas de ventilacion", minimo=0, maximo=100)

    if personas is None:
        raise Problema(
            "Necesito saber cuantas personas pueden estar en el sector.",
            "El caudal minimo del art. 138 del DS 132 se calcula por persona (3 m3/min cada una). "
            "Dime el numero de personas y, si hay equipos diesel, su potencia total en HP.",
        )

    hallazgos = []
    acciones = []

    # --- Oxigeno (art. 144): lo primero, porque es lo que mata primero ---
    oxigeno = oxigeno_pct
    if oxigeno is None:
        hallazgos.append(_hallazgo(
            "Oxigeno", "sin_evaluar", "%s %% como minimo" % _texto_numero(OXIGENO_MINIMO_PCT), "sin dato",
            "Art. 144 del DS 132/2002",
            "No me diste la medicion de oxigeno. Es el dato mas importante de una labor subterranea.",
            "Mide el oxigeno antes de que entre alguien."))
    elif oxigeno < OXIGENO_MINIMO_PCT:
        accion = ("EVACUAR AHORA. Saca a todas las personas de la labor antes de cualquier otra cosa: el "
                  "oxigeno esta bajo el minimo de 19,5 %% (medido: %s %%). El art. 144 del DS 132 obliga a "
                  "retirar al trabajador del area mientras las condiciones no vuelvan a la normalidad, y "
                  "el reingreso lo tiene que certificar personal calificado y autorizado. No entres a "
                  "medir de nuevo sin equipo autonomo de respiracion."
                  % _texto_numero(oxigeno))
        acciones.append(accion)
        hallazgos.append(_hallazgo(
            "Oxigeno", "critico", "%s %% como minimo" % _texto_numero(OXIGENO_MINIMO_PCT),
            "%s %%" % _texto_numero(oxigeno), "Art. 144 del DS 132/2002",
            "Bajo 19,5 % de oxigeno no se puede trabajar. Es una emergencia, no un hallazgo de informe.",
            accion))
    else:
        hallazgos.append(_hallazgo(
            "Oxigeno", "conforme", "%s %% como minimo" % _texto_numero(OXIGENO_MINIMO_PCT),
            "%s %%" % _texto_numero(oxigeno), "Art. 144 del DS 132/2002",
            "Cumple el minimo del art. 144. El reglamento lo expresa en porcentaje en peso: confirma en "
            "que unidad entrega el dato tu instrumento.", ""))

    # --- Gases que obligan a detener el equipo diesel (art. 135) ---
    medidos_ambiente = {"co": co_ppm, "nox": nox_ppm, "aldehido": aldehido_ppm}
    for clave, dato in GASES_DETENCION_AMBIENTE_PPM.items():
        medido = _numero(medidos_ambiente.get(clave), "la concentracion de %s" % dato["nombre"], minimo=0)
        if medido is None:
            continue
        if medido >= dato["valor"]:
            accion = ("DETENER EL EQUIPO DIESEL AHORA y ventilar la labor: %s esta en %s ppm y el art. 135 "
                      "letra a) del DS 132 fija %s ppm como maximo. Si ademas hay personas con sintomas, "
                      "evacua el sector."
                      % (dato["nombre"], _texto_numero(medido), _texto_numero(dato["valor"])))
            acciones.append(accion)
            hallazgos.append(_hallazgo(
                "Gas ambiental: %s" % dato["nombre"], "critico",
                "%s ppm" % _texto_numero(dato["valor"]), "%s ppm" % _texto_numero(medido),
                "Art. 135 letra a) del DS 132/2002",
                "Alcanzado ese valor el reglamento obliga a detener el equipo diesel. El motor aplica el "
                "criterio conservador: al llegar al valor ya corresponde detener, no solo al superarlo.",
                accion))
        else:
            hallazgos.append(_hallazgo(
                "Gas ambiental: %s" % dato["nombre"], "conforme",
                "%s ppm" % _texto_numero(dato["valor"]), "%s ppm" % _texto_numero(medido),
                "Art. 135 letra a) del DS 132/2002",
                "Bajo el valor que obliga a detener el equipo diesel.", ""))

    medidos_escape = {"co": co_escape_ppm, "nox": nox_escape_ppm}
    for clave, dato in GASES_DETENCION_ESCAPE_PPM.items():
        medido = _numero(medidos_escape.get(clave), "la concentracion de %s" % dato["nombre"], minimo=0)
        if medido is None:
            continue
        if medido > dato["valor"]:
            accion = ("DETENER Y SACAR DE SERVICIO EL EQUIPO: %s marca %s ppm y el art. 135 letra b) del "
                      "DS 132 obliga a detenerlo sobre %s ppm. No vuelve a operar hasta que mantencion lo "
                      "corrija y se mida de nuevo."
                      % (dato["nombre"], _texto_numero(medido), _texto_numero(dato["valor"])))
            acciones.append(accion)
            hallazgos.append(_hallazgo(
                "Gas en el escape: %s" % dato["nombre"], "critico",
                "no mas de %s ppm" % _texto_numero(dato["valor"]), "%s ppm" % _texto_numero(medido),
                "Art. 135 letra b) del DS 132/2002",
                "La medicion en el tubo de escape supera el maximo del reglamento.", accion))
        else:
            hallazgos.append(_hallazgo(
                "Gas en el escape: %s" % dato["nombre"], "conforme",
                "no mas de %s ppm" % _texto_numero(dato["valor"]), "%s ppm" % _texto_numero(medido),
                "Art. 135 letra b) del DS 132/2002",
                "Dentro del maximo del reglamento. La medicion en el escape se repite a intervalos no "
                "superiores a un mes (art. 133 letra b).", ""))

    # --- CO2: el DS 132 no tiene limite propio, se aplica el DS 594 ---
    co2 = _numero(co2_ppm, "la concentracion de CO2", minimo=0)
    if co2 is not None:
        fila_co2 = buscar_limite("Anhidrido carbonico", "ppm", limites)
        if co2 > fila_co2["lpt"]:
            accion = ("EVACUAR Y VENTILAR: el CO2 esta en %s ppm y supera el limite temporal de %s ppm del "
                      "art. 66 del DS 594." % (_texto_numero(co2), _texto_numero(fila_co2["lpt"])))
            acciones.append(accion)
            nivel_co2, explicacion = "critico", ("Sobre el limite permisible temporal. El DS 132 no fija "
                                                 "limite propio de CO2: se aplica el DS 594 por remision "
                                                 "expresa del art. 135.")
        elif co2 > fila_co2["lpp"]:
            accion = "Ventila el sector y busca la fuente del CO2 antes de seguir trabajando."
            nivel_co2, explicacion = "alerta", ("Sobre el limite permisible ponderado del art. 66 del "
                                                "DS 594, bajo el temporal. El DS 132 no fija limite propio "
                                                "de CO2: se aplica el DS 594 por remision del art. 135.")
        else:
            accion, nivel_co2 = "", "conforme"
            explicacion = ("Dentro del limite ponderado del art. 66 del DS 594, que es el que aplica porque "
                           "el DS 132 no fija uno propio para el CO2.")
        hallazgos.append(_hallazgo(
            "Anhidrido carbonico (CO2)", nivel_co2,
            "LPP %s ppm / LPT %s ppm" % (_texto_numero(fila_co2["lpp"]), _texto_numero(fila_co2["lpt"])),
            "%s ppm" % _texto_numero(co2), "Art. 66 del DS 594/1999 (por remision del art. 135 del DS 132)",
            explicacion, accion))

    # --- Caudal exigido (arts. 132 y 138) ---
    caudal_personas = CAUDAL_POR_PERSONA_M3MIN * personas
    if caudal_diesel_fabricante is not None:
        caudal_diesel = caudal_diesel_fabricante
        origen_diesel = "caudal indicado por el fabricante de los equipos"
    elif hp_diesel:
        caudal_diesel = CAUDAL_POR_HP_DIESEL_M3MIN * hp_diesel
        origen_diesel = ("2,83 m3/min por HP efectivo al freno, porque el fabricante no especifica "
                         "(art. 132)")
    else:
        caudal_diesel = 0.0
        origen_diesel = "sin equipos diesel declarados"
    caudal_exigido = caudal_personas + caudal_diesel

    if caudal_m3min is None:
        hallazgos.append(_hallazgo(
            "Caudal de aire", "sin_evaluar", "%s m3/min" % _texto_numero(caudal_exigido), "sin dato",
            "Arts. 132 y 138 del DS 132/2002",
            "Calcule el caudal exigido pero no me diste el caudal que realmente entra a la labor.",
            "Afora la entrada de aire. El art. 139 exige aforos al menos trimestrales en entradas y "
            "salidas principales."))
    elif caudal_m3min < caudal_exigido:
        falta = caudal_exigido - caudal_m3min
        accion = ("AUMENTA LA VENTILACION ANTES DE SEGUIR TRABAJANDO: faltan %s m3/min. La labor tiene %s "
                  "m3/min y el DS 132 exige %s m3/min (%s m3/min por las %s personas mas %s m3/min por los "
                  "equipos diesel). Mientras no se corrija, saca los equipos diesel o reduce la dotacion "
                  "del sector."
                  % (_texto_numero(falta), _texto_numero(caudal_m3min), _texto_numero(caudal_exigido),
                     _texto_numero(caudal_personas), _texto_numero(personas), _texto_numero(caudal_diesel)))
        acciones.append(accion)
        hallazgos.append(_hallazgo(
            "Caudal de aire", "critico", "%s m3/min" % _texto_numero(caudal_exigido),
            "%s m3/min" % _texto_numero(caudal_m3min), "Arts. 132 y 138 del DS 132/2002",
            "El art. 138 exige 3 m3/min por persona y el art. 132 agrega el aire de los equipos diesel. El "
            "inciso 2 del art. 132 es claro: los dos caudales SE SUMAN, no se elige el mayor.", accion))
    else:
        hallazgos.append(_hallazgo(
            "Caudal de aire", "conforme", "%s m3/min" % _texto_numero(caudal_exigido),
            "%s m3/min" % _texto_numero(caudal_m3min), "Arts. 132 y 138 del DS 132/2002",
            "Cumple la suma del art. 132: aire por personas mas aire por equipos diesel.", ""))

    # --- Velocidad media del aire (art. 138) ---
    if velocidad_m_min is not None:
        if velocidad_m_min < VELOCIDAD_MINIMA_M_MIN:
            accion = ("Corrige la ventilacion: con menos de 15 m/min el aire no barre los gases, aunque el "
                      "caudal total parezca suficiente.")
            hallazgos.append(_hallazgo(
                "Velocidad media del aire", "alerta",
                "entre %s y %s m/min" % (_texto_numero(VELOCIDAD_MINIMA_M_MIN),
                                         _texto_numero(VELOCIDAD_MAXIMA_M_MIN)),
                "%s m/min" % _texto_numero(velocidad_m_min), "Art. 138 del DS 132/2002",
                "Esta bajo la velocidad media minima que exige el reglamento.", accion))
        elif velocidad_m_min > VELOCIDAD_MAXIMA_M_MIN:
            accion = "Baja la velocidad del aire: sobre 150 m/min levanta polvo y molesta la operacion."
            hallazgos.append(_hallazgo(
                "Velocidad media del aire", "alerta",
                "entre %s y %s m/min" % (_texto_numero(VELOCIDAD_MINIMA_M_MIN),
                                         _texto_numero(VELOCIDAD_MAXIMA_M_MIN)),
                "%s m/min" % _texto_numero(velocidad_m_min), "Art. 138 del DS 132/2002",
                "Supera la velocidad media maxima que permite el reglamento.", accion))
        else:
            hallazgos.append(_hallazgo(
                "Velocidad media del aire", "conforme",
                "entre %s y %s m/min" % (_texto_numero(VELOCIDAD_MINIMA_M_MIN),
                                         _texto_numero(VELOCIDAD_MAXIMA_M_MIN)),
                "%s m/min" % _texto_numero(velocidad_m_min), "Art. 138 del DS 132/2002",
                "Dentro del rango del art. 138.", ""))

    # --- Perdidas de ventilacion (art. 139) ---
    if perdidas_pct is not None:
        if perdidas_pct > PERDIDAS_MAXIMAS_PCT:
            hallazgos.append(_hallazgo(
                "Perdidas de ventilacion", "alerta",
                "hasta %s %%" % _texto_numero(PERDIDAS_MAXIMAS_PCT),
                "%s %%" % _texto_numero(perdidas_pct), "Art. 139 del DS 132/2002",
                "Las perdidas superan el 15 % que tolera el reglamento: hay aire que se pierde antes de "
                "llegar a las labores.",
                "Revisa puertas, tapados y cortinas del circuito de ventilacion."))
        else:
            hallazgos.append(_hallazgo(
                "Perdidas de ventilacion", "conforme",
                "hasta %s %%" % _texto_numero(PERDIDAS_MAXIMAS_PCT),
                "%s %%" % _texto_numero(perdidas_pct), "Art. 139 del DS 132/2002",
                "Dentro del 15 % que tolera el reglamento.", ""))

    nivel = _peor(h["nivel"] for h in hallazgos)
    return {
        "norma": NORMA_VENTILACION,
        "nivel_riesgo": nivel,
        "cumple": nivel == "conforme",
        "acciones_inmediatas": acciones,
        "caudal": {
            "personas": personas,
            "hp_diesel": hp_diesel or 0.0,
            "caudal_por_personas_m3min": caudal_personas,
            "caudal_por_diesel_m3min": caudal_diesel,
            "origen_caudal_diesel": origen_diesel,
            "caudal_exigido_m3min": caudal_exigido,
            "caudal_medido_m3min": caudal_m3min,
            "diferencia_m3min": None if caudal_m3min is None else caudal_m3min - caudal_exigido,
            "formula": "Q_minimo = 3,0 x personas + 2,83 x HP diesel (arts. 138 y 132 del DS 132/2002)",
        },
        "cumple_por_tema": {h["tema"]: h["nivel"] for h in hallazgos},
        "hallazgos": hallazgos,
        "no_cumple": [h for h in hallazgos if h["nivel"] in ("critico", "alerta")],
        "sin_datos": [h["tema"] for h in hallazgos if h["nivel"] == "sin_evaluar"],
        "obligaciones_permanentes": [
            "Proyecto de ventilacion aprobado por SERNAGEOMIN antes de aplicarlo (art. 136).",
            "Aforo de entradas y salidas principales al menos trimestral y control general semestral "
            "(art. 139).",
            "En minas con equipos diesel: medir y registrar CO, oxidos de nitrogeno y aldehidos, al menos "
            "una vez por semana, y en el escape a intervalos no superiores a un mes (art. 133).",
            "Sensores y alarmas en las areas o labores criticas (art. 133).",
            "Refugios que garanticen la sobrevivencia por al menos 48 horas (art. 100) y procedimiento de "
            "evacuacion actualizado con simulacros (art. 99).",
        ],
        "advertencias": [AVISO_SIN_TARP],
        "no_verificado": [
            "El regimen especial de pequena mineria del Decreto 1/2024 (arts. 615-616, 626 y 628, para "
            "faenas de hasta 5.000 t/mes) se leyo de forma indirecta y no esta verificado articulo por "
            "articulo. Este calculo aplica el regimen general de los arts. 132 a 153.",
        ],
    }


# --------------------------------------------------------------------------
# 3. Correccion de limites permisibles - DS 594/1999
# --------------------------------------------------------------------------

def presion_estimada_mmhg(altitud_m):
    """Estimacion de la presion atmosferica a partir de la altitud.

    ATENCION: esta formula NO esta en el DS 594. El reglamento exige presion
    atmosferica local MEDIDA. Es la atmosfera estandar internacional y sirve solo
    como referencia para ordenar una medicion, nunca para decidir cumplimiento.
    """
    altitud = _numero(altitud_m, "la altitud", minimo=-500, maximo=9000)
    if altitud is None:
        return None
    return PRESION_NIVEL_MAR_MMHG * (1.0 - 2.25577e-5 * altitud) ** 5.25588


def corregir_limite(limite, unidad, tipo="ponderado", horas_diarias=None, horas_semanales=None,
                    presion_mmhg=None, altitud_m=None, estimar_presion=False):
    """Corrige un limite permisible por jornada y altitud (arts. 62, 63 y 64 del DS 594).

        Fj = (8 / h) x ((24 - h) / 16)     solo si la jornada diaria supera 8 horas (art. 62)
        Fj = 0,90                          jornada de 8 h diarias con semana > 45 h y hasta 48 h
        Fa = P / 760                       P = presion local MEDIDA en mmHg, solo sobre 1.000 m (art. 63)

        LPP corregido = LPP x Fj x Fa      (art. 64)
        LPT y LPA corregidos = valor x Fa  (art. 64: nunca se les aplica Fj)

    Fa solo corrige valores en mg/m3 y fibras/cc. Los valores en ppm no se
    corrigen por altitud.
    """
    tipo = _clave(tipo) or "ponderado"
    if tipo in ("lpp",):
        tipo = "ponderado"
    if tipo in ("lpt", "corto_plazo"):
        tipo = "temporal"
    if tipo in ("lpa", "instantaneo", "techo"):
        tipo = "absoluto"
    if tipo not in TIPOS_LIMITE:
        raise Problema(
            "No reconozco el tipo de limite «%s»." % tipo,
            "Usa ponderado (LPP, promedio de la jornada), temporal (LPT, 15 minutos) o absoluto (LPA).",
        )

    limite = _numero(limite, "el limite permisible", minimo=0)
    if limite is None:
        raise Problema(
            "No tengo un limite permisible que corregir.",
            "Dime el agente para buscarlo en la tabla del art. 66, o entrega el valor del limite.",
        )
    unidad_norm = _unidad_normalizada(unidad)
    horas_diarias = _numero(horas_diarias, "la jornada diaria", minimo=0.5,
                            sugerencia="Escribe las horas que dura el turno, por ejemplo 12.")
    horas_semanales = _numero(horas_semanales, "la jornada semanal", minimo=0, maximo=168)
    presion_mmhg = _numero(presion_mmhg, "la presion atmosferica", minimo=1, maximo=800,
                           sugerencia="La presion va en milimetros de mercurio (mmHg). Si tu instrumento "
                                      "entrega hPa o mbar, conviertelo antes: 1.013 hPa son 760 mmHg.")
    altitud_m = _numero(altitud_m, "la altitud", minimo=-500, maximo=9000)

    if horas_diarias is not None and horas_diarias >= 24:
        raise Problema(
            "Una jornada diaria de %s horas no es posible." % _texto_numero(horas_diarias),
            "La formula del art. 62 usa las horas trabajadas en un dia. Revisa el dato.",
        )

    advertencias = []
    no_calculado = []
    formulas = []
    articulos = ["Art. 62 del DS 594/1999 (texto segun Decreto 123/2015)",
                 "Art. 63 del DS 594/1999", "Art. 64 del DS 594/1999"]

    # --- Fj, factor de jornada (art. 62). Solo corrige el LPP (art. 64) ---
    if tipo != "ponderado":
        fj = 1.0
        formulas.append("Fj no se aplica: el art. 64 corrige los limites temporales y absolutos solo por Fa.")
    elif horas_diarias is None:
        fj = 1.0
        advertencias.append(
            "No me dijiste cuantas horas dura el turno, asi que no apliqué la correccion por jornada del "
            "art. 62. Si el turno pasa de 8 horas diarias, el limite real es MAS BAJO que el que ves aqui.")
        formulas.append("Fj = 1,00 (sin dato de jornada)")
    elif horas_diarias > JORNADA_ORDINARIA_H:
        bruto = (JORNADA_ORDINARIA_H / horas_diarias) * ((24.0 - horas_diarias) / 16.0)
        fj = _dos_decimales(bruto)
        formulas.append("Fj = (8 / %s) x ((24 - %s) / 16) = %s"
                        % (_texto_numero(horas_diarias), _texto_numero(horas_diarias), _texto_numero(fj)))
        if horas_diarias > 12:
            advertencias.append(
                "Una jornada de %s horas diarias es excepcional: confirma con tu asesoria que el sistema "
                "de turnos este autorizado." % _texto_numero(horas_diarias))
    elif (abs(horas_diarias - JORNADA_ORDINARIA_H) < 1e-9 and horas_semanales is not None
          and 45 < horas_semanales <= 48):
        fj = FJ_JORNADA_8H_SEMANA_LARGA
        formulas.append("Fj = 0,90 (jornada de 8 horas diarias con semana de mas de 45 y hasta 48 horas, "
                        "art. 62 inciso 2)")
    else:
        fj = 1.0
        formulas.append("Fj = 1,00 (jornada de 8 horas diarias o menos: el art. 62 no corrige)")
        if horas_semanales is not None and horas_semanales > 48:
            advertencias.append(
                "Declaraste una semana de %s horas con turnos de %s horas diarias. Desde el Decreto "
                "123/2015 el art. 62 corrige por jornada DIARIA y solo tiene el caso especial de hasta 48 "
                "horas semanales: para esta combinacion no hay factor verificado y no voy a inventar uno. "
                "Consultalo con el organismo administrador de la Ley 16.744."
                % (_texto_numero(horas_semanales), _texto_numero(horas_diarias)))

    # --- Fa, factor de altitud (art. 63). Solo sobre mg/m3 y fibras/cc ---
    presion_es_estimada = False
    if unidad_norm == "ppm":
        fa = 1.0
        formulas.append("Fa no se aplica: el art. 63 solo corrige valores en mg/m3 y fibras/cc, no en ppm.")
    elif altitud_m is not None and altitud_m <= ALTITUD_CORRECCION_M:
        fa = 1.0
        formulas.append("Fa = 1,00 (la faena esta a %s m, y el art. 63 corrige solo sobre 1.000 m)"
                        % _texto_numero(altitud_m))
    elif presion_mmhg is not None:
        fa = _dos_decimales(presion_mmhg / PRESION_NIVEL_MAR_MMHG)
        formulas.append("Fa = %s / 760 = %s" % (_texto_numero(presion_mmhg), _texto_numero(fa)))
        if altitud_m is None:
            advertencias.append(
                "Use la presion que me diste. Recuerda que el art. 63 corrige solo cuando la faena esta "
                "sobre 1.000 m s.n.m.")
    elif altitud_m is not None and altitud_m > ALTITUD_CORRECCION_M and estimar_presion:
        presion_mmhg = presion_estimada_mmhg(altitud_m)
        presion_es_estimada = True
        fa = _dos_decimales(presion_mmhg / PRESION_NIVEL_MAR_MMHG)
        formulas.append("Fa = %s / 760 = %s (presion ESTIMADA desde la altitud, no medida)"
                        % (_texto_numero(presion_mmhg), _texto_numero(fa)))
        advertencias.append(
            "La presion de %s mmHg es una ESTIMACION con la atmosfera estandar internacional, una formula "
            "que NO esta en el DS 594. El reglamento exige presion local medida. Sirve para dimensionar el "
            "problema, no para decidir si la empresa cumple: manda a medir la presion real."
            % _texto_numero(presion_mmhg))
    elif altitud_m is not None and altitud_m > ALTITUD_CORRECCION_M:
        fa = None
        no_calculado.append(
            "No puedo corregir por altitud: la faena esta a %s m (sobre los 1.000 m del art. 63) y no me "
            "diste la presion atmosferica local en mmHg. El DS 594 exige presion MEDIDA y no entrega una "
            "formula para deducirla de la altitud, asi que no la voy a inventar. Sin esa correccion el "
            "limite quedaria mas permisivo de lo que exige la norma." % _texto_numero(altitud_m))
    else:
        fa = 1.0
        formulas.append("Fa = 1,00 (sin dato de altitud)")
        advertencias.append(
            "No me dijiste a que altitud esta la faena, asi que no apliqué la correccion del art. 63. Si "
            "esta sobre 1.000 m, el limite real es MAS BAJO que el que ves aqui.")

    corregido = None if fa is None else limite * fj * fa
    return {
        "limite_tabla": limite,
        "unidad": unidad,
        "tipo": tipo,
        "descripcion_tipo": TIPOS_LIMITE[tipo],
        "fj": fj,
        "fa": fa,
        "presion_mmhg": presion_mmhg,
        "presion_estimada": presion_es_estimada,
        "altitud_m": altitud_m,
        "horas_diarias": horas_diarias,
        "horas_semanales": horas_semanales,
        "limite_corregido": corregido,
        "formulas": formulas,
        "articulos": articulos,
        "redondeo": ("Fj y Fa se expresan con dos decimales: el segundo decimal sube si el tercero es 5 o "
                     "mas. No se hacen aproximaciones parciales (arts. 62 y 63)."),
        "advertencias": advertencias,
        "no_calculado": no_calculado,
    }


# --------------------------------------------------------------------------
# 4. Exposicion medida contra el limite corregido
# --------------------------------------------------------------------------

UMBRAL_VIGILANCIA_PCT = 50.0   # criterio de gestion del motor, NO una exigencia del DS 594


def evaluar_exposicion(agente, concentracion, unidad=None, tipo="ponderado", horas_diarias=None,
                       horas_semanales=None, presion_mmhg=None, altitud_m=None,
                       estimar_presion=False, limites=None):
    """Compara una concentracion medida contra el limite del DS 594 ya corregido.

    Devuelve el porcentaje del limite y la accion sugerida. Si falta un dato que
    haria el limite mas estricto (por ejemplo la presion en altura), no declara
    cumplimiento: lo dice y pide el dato.
    """
    fila = buscar_limite(agente, unidad, limites)
    concentracion = _numero(concentracion, "la concentracion medida", minimo=0,
                            sugerencia="Escribe la concentracion medida en %s." % fila["unidad"])
    if concentracion is None:
        raise Problema(
            "No me diste la concentracion medida de %s." % fila["agente"],
            "Necesito el resultado del muestreo en %s para compararlo con el limite." % fila["unidad"],
        )

    tipo_norm = _clave(tipo) or "ponderado"
    if tipo_norm in ("lpp",):
        tipo_norm = "ponderado"
    if tipo_norm in ("lpt", "corto_plazo"):
        tipo_norm = "temporal"
    if tipo_norm in ("lpa", "instantaneo", "techo"):
        tipo_norm = "absoluto"

    advertencias = []
    base_tipo = tipo_norm
    valor_base = None
    referencia = ""

    if tipo_norm == "ponderado":
        valor_base = fila["lpp"]
        referencia = "LPP del art. 66"
        if valor_base is None:
            raise Problema(
                "La tabla no trae LPP para %s en %s." % (fila["agente"], fila["unidad"]),
                "Sin limite verificado no comparo nada. Revisa la tabla del art. 66 del DS 594.",
            )
    elif tipo_norm == "temporal":
        if fila["lpt"] is not None:
            valor_base = fila["lpt"]
            referencia = "LPT del art. 66"
        else:
            base_tipo = "ponderado"
            valor_base = fila["lpp"]
            referencia = "techo del art. 60 (5 veces el LPP)"
            advertencias.append(
                "%s no tiene limite temporal (LPT) en la tabla del art. 66. Para las excursiones cortas "
                "rige el techo del art. 60: nunca superar 5 veces el limite ponderado." % fila["agente"])
    elif tipo_norm == "absoluto":
        base_tipo = "ponderado"
        valor_base = fila["lpp"]
        referencia = "techo del art. 60 (5 veces el LPP)"
        advertencias.append(
            "No tengo cargada la tabla de limites permisibles absolutos del art. 61 del DS 594 y no voy a "
            "inventar un valor. Comparo contra el techo del art. 60, que prohibe superar 5 veces el limite "
            "ponderado en cualquier momento de la jornada.")
    else:
        raise Problema(
            "No reconozco el tipo de medicion «%s»." % tipo,
            "Usa ponderado (promedio de la jornada), temporal (15 minutos) o absoluto (en cualquier momento).",
        )

    correccion = corregir_limite(valor_base, fila["unidad"], base_tipo, horas_diarias, horas_semanales,
                                 presion_mmhg, altitud_m, estimar_presion)
    advertencias.extend(correccion["advertencias"])

    limite_corregido = correccion["limite_corregido"]
    # Techo del art. 60: 5 veces el limite ponderado corregido.
    correccion_lpp = correccion if base_tipo == "ponderado" else corregir_limite(
        fila["lpp"], fila["unidad"], "ponderado", horas_diarias, horas_semanales,
        presion_mmhg, altitud_m, estimar_presion) if fila["lpp"] is not None else None
    techo = None
    if correccion_lpp is not None and correccion_lpp["limite_corregido"] is not None:
        techo = FACTOR_TECHO_ART_60 * correccion_lpp["limite_corregido"]

    if tipo_norm in ("temporal", "absoluto") and referencia.startswith("techo"):
        limite_corregido = techo

    porcentaje = None
    if limite_corregido:
        porcentaje = concentracion / limite_corregido * 100.0

    acciones = []
    if porcentaje is None:
        estado, nivel = "sin_evaluar", "sin_evaluar"
        explicacion = ("No puedo decidir si cumple: falta un dato que hace el limite mas estricto. "
                       "Si comparara sin esa correccion, el resultado quedaria mas permisivo que la norma.")
        acciones.append("Consigue el dato que falta (lo detallo en «no_calculado») y vuelve a preguntarme.")
        porcentaje_referencial = concentracion / (valor_base or 1) * 100.0
    else:
        porcentaje_referencial = porcentaje
        if techo is not None and concentracion > techo:
            estado, nivel = "critico", "critico"
            accion = ("SACA A LA GENTE DEL AREA AHORA y no la dejes volver hasta ventilar y volver a medir. "
                      "La concentracion de %s (%s %s) supera 5 veces el limite ponderado corregido (%s %s), "
                      "y el art. 60 del DS 594 prohibe eso en cualquier momento de la jornada."
                      % (fila["agente"], _texto_numero(concentracion), fila["unidad"],
                         _texto_numero(techo), fila["unidad"]))
            acciones.append(accion)
            explicacion = ("El art. 60 permite excedencias momentaneas del limite ponderado, pero nunca "
                           "sobre 5 veces su valor. Este resultado pasa ese techo.")
        elif porcentaje > 100.0:
            estado, nivel = "no cumple", "critico"
            accion = ("REDUCE LA EXPOSICION ANTES DEL PROXIMO TURNO: la concentracion esta en %s %% del "
                      "limite legal corregido. Controla la fuente (ventilacion, humectacion, encierro o "
                      "cambio de proceso); la proteccion respiratoria es una medida transitoria, no la "
                      "solucion. Avisa al organismo administrador de la Ley 16.744 para la evaluacion y la "
                      "vigilancia de la salud de las personas expuestas." % _texto_numero(round(porcentaje, 1)))
            acciones.append(accion)
            explicacion = ("El promedio no puede superar el limite permisible (art. 60). Aqui lo supera, "
                           "asi que hay sobreexposicion.")
        elif porcentaje >= UMBRAL_VIGILANCIA_PCT:
            estado, nivel = "cumple - en vigilancia", "alerta"
            acciones.append(
                "Cumple, pero sin holgura: refuerza los controles y repite la medicion. Que la exposicion "
                "quede sobre la mitad del limite es un criterio de gestion del motor para anticiparse, NO "
                "una exigencia del DS 594.")
            explicacion = ("Esta bajo el limite legal, pero por encima de la mitad: cualquier cambio en el "
                           "proceso o una falla de ventilacion puede pasarlo.")
        else:
            estado, nivel = "cumple", "conforme"
            explicacion = "La concentracion medida esta bajo el limite permisible corregido."

    if correccion["presion_estimada"] and estado in ("cumple", "cumple - en vigilancia"):
        estado = "referencial - falta la presion medida"
        nivel = "sin_evaluar"
        acciones.append(
            "No tomes esto como prueba de cumplimiento: el limite se corrigio con una presion ESTIMADA. "
            "Manda a medir la presion atmosferica local antes de concluir nada.")

    texto_carcinogeno = _texto_carcinogeno(fila["carcinogeno"])
    if texto_carcinogeno:
        advertencias.append(texto_carcinogeno)

    return {
        "norma": NORMA_EXPOSICION,
        "agente": fila["agente"],
        "unidad": fila["unidad"],
        "tipo_medicion": tipo_norm,
        "referencia": referencia,
        "concentracion": concentracion,
        "limite_tabla": valor_base,
        "limite_corregido": limite_corregido,
        "porcentaje_del_limite": None if porcentaje is None else round(porcentaje, 1),
        "porcentaje_referencial": round(porcentaje_referencial, 1),
        "techo_art_60": techo,
        "factores": {"fj": correccion["fj"], "fa": correccion["fa"],
                     "presion_estimada": correccion["presion_estimada"]},
        "formulas": correccion["formulas"],
        "estado": estado,
        "nivel_riesgo": nivel,
        "acciones_inmediatas": acciones,
        "explicacion": explicacion,
        "carcinogeno": fila["carcinogeno"],
        "articulo_limite": fila["articulo"],
        "fuente": fila["fuente"],
        "verificado_el": fila["verificado_el"],
        "notas_del_agente": fila["notas"],
        "regla_excursiones": ("El art. 60 permite excedencias momentaneas pero nunca sobre 5 veces el "
                              "limite, y no mas de %d veces en la jornada ni mas de %d vez por hora."
                              % (MAX_EXCURSIONES_JORNADA, MAX_EXCURSIONES_HORA)),
        "advertencias": advertencias,
        "no_calculado": correccion["no_calculado"],
    }


# --------------------------------------------------------------------------
# 5. GISTM
# --------------------------------------------------------------------------

GISTM_CLASIFICACIONES = ["baja", "significativa", "alta", "muy alta", "extrema"]

GISTM_CRITERIOS_DISENO = {
    "baja": {"crecidas_operacion": "1/200", "crecidas_poscierre": "1/10.000",
             "sismico_operacion": "1/200", "sismico_poscierre": "1/10.000"},
    "significativa": {"crecidas_operacion": "1/1.000", "crecidas_poscierre": "1/10.000",
                      "sismico_operacion": "1/1.000", "sismico_poscierre": "1/10.000"},
    "alta": {"crecidas_operacion": "1/2.475", "crecidas_poscierre": "1/10.000",
             "sismico_operacion": "1/2.475", "sismico_poscierre": "1/10.000"},
    "muy alta": {"crecidas_operacion": "1/5.000", "crecidas_poscierre": "1/10.000",
                 "sismico_operacion": "1/5.000", "sismico_poscierre": "1/10.000"},
    "extrema": {"crecidas_operacion": "1/10.000", "crecidas_poscierre": "1/10.000",
                "sismico_operacion": "1/10.000", "sismico_poscierre": "1/10.000"},
}

GISTM_PLAZO_CONFORMIDAD = {
    "extrema": "2023-08-05", "muy alta": "2023-08-05",
    "alta": "2025-08-05", "significativa": "2025-08-05", "baja": "2025-08-05",
}

GISTM_PRINCIPIOS = [
    (1, "I. Comunidades afectadas", "Respetar los derechos de las personas afectadas por el proyecto y "
        "asegurar su participacion significativa durante todo el ciclo de vida, incluido el cierre"),
    (2, "II. Base de conocimientos integrada", "Construir y mantener una base de conocimientos "
        "interdisciplinaria: social, ambiental, economica y tecnica"),
    (3, "II. Base de conocimientos integrada", "Usar esa base de conocimientos para fundamentar las "
        "decisiones a lo largo de todo el ciclo de vida"),
    (4, "III. Diseno, construccion, operacion y monitoreo", "Desarrollar planes y criterios de diseno que "
        "minimicen el riesgo en todas las fases, incluidos cierre y poscierre"),
    (5, "III. Diseno, construccion, operacion y monitoreo", "Desarrollar un diseno solido que minimice el "
        "riesgo de falla para las personas y el ambiente (criterio ALARP)"),
    (6, "III. Diseno, construccion, operacion y monitoreo", "Planificar, construir y operar la instalacion "
        "gestionando el riesgo en todas las fases"),
    (7, "III. Diseno, construccion, operacion y monitoreo", "Disenar, implementar y operar sistemas de "
        "monitoreo para gestionar el riesgo"),
    (8, "IV. Gestion y gobernanza", "Establecer politicas, sistemas y rendicion de cuentas que respalden la "
        "seguridad e integridad de la instalacion"),
    (9, "IV. Gestion y gobernanza", "Nombrar y dar facultades a un Ingeniero de Registro (IDR)"),
    (10, "IV. Gestion y gobernanza", "Establecer niveles de revision independiente del riesgo y la calidad"),
    (11, "IV. Gestion y gobernanza", "Desarrollar una cultura organizacional de aprendizaje, comunicacion y "
         "deteccion temprana de problemas"),
    (12, "IV. Gestion y gobernanza", "Tener un canal para reportar inquietudes, con proteccion a quien "
         "denuncia"),
    (13, "V. Respuesta ante emergencias y recuperacion", "Estar preparado para la respuesta ante "
         "emergencias en caso de falla de la instalacion"),
    (14, "V. Respuesta ante emergencias y recuperacion", "Prepararse para la recuperacion a largo plazo "
         "ante una falla catastrofica"),
    (15, "VI. Divulgacion publica y acceso a la informacion", "Hacer publica y accesible la informacion "
         "sobre las instalaciones de relaves"),
]


def clasificar_por_poblacion(personas_en_riesgo):
    """Sugiere una clasificacion de consecuencias por poblacion potencial en riesgo.

    Es SOLO una sugerencia sobre la dimension A del Anexo 2. La clasificacion
    final es el maximo de las cinco dimensiones (poblacion, perdida de vidas,
    medio ambiente, salud y aspectos sociales, infraestructura y economia).
    """
    personas = _numero(personas_en_riesgo, "la poblacion potencial en riesgo", minimo=0)
    if personas is None:
        return None, ""
    if personas == 0:
        return "baja", "Ninguna persona en riesgo (dimension A del Anexo 2)."
    if personas < 10:
        return "significativa", "Entre 1 y 10 personas en riesgo (dimension A del Anexo 2)."
    if personas <= 100:
        # Las bandas 1-10 y 10-100 se tocan en 10, y 10-100 con 100-1.000 en 100:
        # en el borde se toma la clase mas alta, que es la mas protectora.
        return "alta", "Entre 10 y 100 personas en riesgo (dimension A del Anexo 2)."
    if personas <= 1000:
        return "muy alta", "Entre 100 y 1.000 personas en riesgo (dimension A del Anexo 2)."
    return "extrema", "Mas de 1.000 personas en riesgo (dimension A del Anexo 2)."


def evaluar_gistm(clasificacion=None, requisitos_conformes=None, poblacion_en_riesgo=None,
                  miembro_icmm=False, principios_cubiertos=None):
    """Porcentaje de conformidad sobre los 77 requisitos del GISTM y que falta.

    El porcentaje se calcula siempre sobre los 77 requisitos auditables, que es
    el total oficial de ICMM y la Global Tailings Review. La distribucion de
    requisitos por principio NO se usa como criterio: el conteo automatico del
    PDF arroja 78 etiquetas y esa diferencia no esta resuelta.
    """
    sugerida, motivo_sugerencia = clasificar_por_poblacion(poblacion_en_riesgo)
    clase = _clave(clasificacion).replace("_", " ") if clasificacion and clasificacion is not True else ""
    if clase and clase not in GISTM_CLASIFICACIONES:
        raise Problema(
            "No reconozco la clasificacion de consecuencias «%s»." % clasificacion,
            "El Anexo 2 del GISTM tiene cinco: %s." % ", ".join(GISTM_CLASIFICACIONES),
        )
    if not clase:
        clase = sugerida

    advertencias = [
        "El GISTM es un estandar voluntario de industria. NO es ley en Chile: obliga por contrato a los "
        "miembros de ICMM y a quienes firmen con el GTMI. Lo obligatorio en Chile es el DS 248/2007.",
        "A la fecha de la investigacion no existe un esquema de certificacion GISTM de terceros: el GTMI "
        "todavia no abre la convocatoria de auditores. Si alguien ofrece una «certificacion GISTM», es una "
        "autodeclaracion o un aseguramiento privado.",
        "El porcentaje se calcula sobre los 77 requisitos oficiales. No uso la distribucion de requisitos "
        "por principio como criterio de conformidad: el conteo del PDF oficial arroja 78 etiquetas y la "
        "diferencia no esta resuelta.",
    ]

    conformes = _numero(requisitos_conformes, "el numero de requisitos conformes", minimo=0,
                        maximo=GISTM_TOTAL_REQUISITOS,
                        sugerencia="Es un numero entre 0 y 77: los requisitos auditables del GISTM que la "
                                   "instalacion ya cumple, segun la evaluacion que hayan hecho.")
    porcentaje = None
    pendientes = None
    if conformes is not None:
        if abs(conformes - round(conformes)) > 1e-9:
            raise Problema(
                "Los requisitos del GISTM se cuentan enteros y me diste %s." % _texto_numero(conformes),
                "Escribe cuantos de los 77 requisitos cumple la instalacion, como numero entero.",
            )
        conformes = int(round(conformes))
        porcentaje = round(conformes / float(GISTM_TOTAL_REQUISITOS) * 100.0, 1)
        pendientes = GISTM_TOTAL_REQUISITOS - conformes

    cubiertos = set()
    for pieza in (principios_cubiertos or []):
        try:
            cubiertos.add(int(str(pieza).strip()))
        except (TypeError, ValueError):
            raise Problema(
                "No entiendo el principio «%s»." % pieza,
                "Los principios del GISTM se numeran del 1 al 15.",
            )
    fuera = sorted(p for p in cubiertos if p < 1 or p > GISTM_TOTAL_PRINCIPIOS)
    if fuera:
        raise Problema(
            "El GISTM tiene 15 principios y me nombraste el %s." % ", ".join(str(p) for p in fuera),
            "Usa numeros del 1 al 15.",
        )
    faltantes = [{"principio": numero, "tema": tema, "titulo": titulo}
                 for numero, tema, titulo in GISTM_PRINCIPIOS if numero not in cubiertos]
    if cubiertos:
        advertencias.append(
            "La cobertura por principios (%d de 15) sirve para ordenar el trabajo, pero NO es el porcentaje "
            "de conformidad: ese se mide sobre los 77 requisitos." % len(cubiertos))

    resultado = {
        "norma": NORMA_GISTM,
        "clasificacion": clase,
        "clasificacion_sugerida": sugerida,
        "motivo_sugerencia": motivo_sugerencia,
        "total_requisitos": GISTM_TOTAL_REQUISITOS,
        "requisitos_conformes": conformes,
        "requisitos_pendientes": pendientes,
        "porcentaje_conformidad": porcentaje,
        "principios_cubiertos": sorted(cubiertos),
        "principios_faltantes": faltantes,
        "estructura": "6 temas, 15 principios y 77 requisitos auditables (agosto de 2020).",
        "protocolos_icmm": ("Los Conformance Protocols de ICMM traducen los 77 requisitos en %d criterios "
                            "de evaluacion." % GISTM_CRITERIOS_PROTOCOLO_ICMM),
        "advertencias": advertencias,
        "no_verificado": [
            "El total de requisitos: ICMM y la Global Tailings Review declaran 77, pero el conteo "
            "automatico del PDF en espanol arroja 78 etiquetas. Se usa 77, que es el numero oficial.",
        ],
    }

    if not clase:
        resultado["que_falta"] = [
            "Falta la clasificacion de consecuencias de la instalacion. Es lo primero: de ella dependen los "
            "criterios de diseno y el plazo de conformidad.",
        ]
        resultado["mensaje"] = ("Sin la clasificacion de consecuencias no puedo decirte que criterios de "
                                "diseno te exige el GISTM.")
        return resultado

    criterios = GISTM_CRITERIOS_DISENO[clase]
    resultado["criterios_diseno"] = {
        "clasificacion": clase,
        "crecidas_operacion_y_cierre": criterios["crecidas_operacion"],
        "crecidas_poscierre": criterios["crecidas_poscierre"],
        "sismico_operacion_y_cierre": criterios["sismico_operacion"],
        "sismico_poscierre": criterios["sismico_poscierre"],
        "unidad": "probabilidad anual de excedencia para el diseno (Anexo 1, tablas 2 y 3)",
    }
    resultado["plazo_conformidad_icmm"] = GISTM_PLAZO_CONFORMIDAD[clase]
    resultado["revision_independiente"] = (
        "Las instalaciones de clasificacion alta, muy alta y extrema requieren una Comision Independiente "
        "de Revision de Relaves (CIRR) y revisiones reforzadas."
        if clase in ("alta", "muy alta", "extrema") else
        "En clasificacion baja o significativa el GISTM igual exige niveles de revision independiente "
        "(principio 10), proporcionales al riesgo.")

    que_falta = []
    if conformes is None:
        que_falta.append(
            "Falta saber cuantos de los 77 requisitos cumple hoy la instalacion. Se cuentan con los "
            "Conformance Protocols de ICMM (219 criterios), no a ojo.")
    elif pendientes:
        que_falta.append("Quedan %d de los 77 requisitos por cumplir (%s %% de conformidad)."
                         % (pendientes, _texto_numero(porcentaje)))
    if faltantes and cubiertos:
        que_falta.append("Principios sin cobertura declarada: %s."
                         % ", ".join("P%d" % f["principio"] for f in faltantes))
    if miembro_icmm:
        que_falta.append("Como miembro de ICMM, el plazo de conformidad para esta clasificacion vencio el "
                         "%s." % GISTM_PLAZO_CONFORMIDAD[clase])
    resultado["que_falta"] = que_falta
    resultado["mensaje"] = (
        "Clasificacion %s: %s de conformidad sobre los 77 requisitos."
        % (clase, ("%s %%" % _texto_numero(porcentaje)) if porcentaje is not None else "sin evaluar")
    )
    return resultado


# --------------------------------------------------------------------------
# 6. Cierre de faenas - Ley 20.551 y DS 41/2012
# --------------------------------------------------------------------------

REGIMENES_CIERRE = {
    "general": {
        "nombre": "Procedimiento de aplicacion general",
        "umbral": "capacidad de extraccion superior a 10.000 toneladas brutas mensuales por faena",
        "articulo": "Art. 10 de la Ley 20.551 (y art. 12 del DS 41/2012)",
        "exige_garantia": True,
    },
    "simplificado": {
        "nombre": "Procedimiento simplificado",
        "umbral": "hasta 10.000 toneladas brutas mensuales por faena, y exploracion o prospeccion",
        "articulo": "Arts. 10 y 16 de la Ley 20.551 (y art. 28 del DS 41/2012)",
        "exige_garantia": False,
    },
    "declaracion_simplificada": {
        "nombre": "Declaracion simplificada",
        "umbral": "hasta 5.000 toneladas mensuales, sin plantas de produccion ni depositos de relaves",
        "articulo": "Art. 16 de la Ley 20.551",
        "exige_garantia": False,
    },
}

CONTENIDO_PLAN_CIERRE = [
    ("a", "Identificacion de la empresa minera", True),
    ("b", "Descripcion de la faena minera y de sus instalaciones", True),
    ("c", "Resolucion de Calificacion Ambiental (RCA) que corresponda", False),
    ("d", "Informe tecnico sobre la vida util de la faena", False),
    ("e", "Medidas de cierre propuestas, para la estabilidad fisica y quimica", True),
    ("f", "Estimacion de los costos de las medidas de cierre", False),
    ("g", "Programa de post cierre", False),
    ("h", "Garantia de cumplimiento", False),
    ("i", "Documentos que fundamentan el plan", False),
    ("j", "Programa de difusion a la comunidad", False),
]


def regimen_cierre(toneladas_mes, tiene_planta=False, tiene_relaves=False):
    """Regimen de cierre segun la capacidad de extraccion (arts. 10 y 16 Ley 20.551)."""
    toneladas = _numero(toneladas_mes, "la capacidad de extraccion mensual", minimo=0,
                        sugerencia="Son las toneladas brutas mensuales de la faena.")
    if toneladas is None:
        raise Problema(
            "Necesito la capacidad de extraccion de la faena, en toneladas brutas al mes.",
            "De ese numero depende todo: sobre 10.000 t/mes el plan de cierre es del procedimiento general "
            "y exige garantia financiera.",
        )
    if toneladas > UMBRAL_REGIMEN_GENERAL_T_MES:
        return "general", toneladas
    if (toneladas <= UMBRAL_DECLARACION_SIMPLE_T_MES and not tiene_planta and not tiene_relaves):
        return "declaracion_simplificada", toneladas
    return "simplificado", toneladas


def plan_cierre(toneladas_mes=None, tiene_planta=False, tiene_relaves=False, vida_util_anios=None):
    """Lista de verificacion del plan de cierre y de su garantia (Ley 20.551)."""
    clave, toneladas = regimen_cierre(toneladas_mes, tiene_planta, tiene_relaves)
    datos = REGIMENES_CIERRE[clave]
    vida_util = _numero(vida_util_anios, "la vida util de la faena", minimo=0, maximo=200)

    if clave == "simplificado":
        contenido = [{"letra": letra, "item": item, "articulo": "Art. 13 de la Ley 20.551"}
                     for letra, item, en_simplificado in CONTENIDO_PLAN_CIERRE if en_simplificado]
        nota_contenido = ("En el procedimiento simplificado el plan lleva solo los antecedentes de las "
                          "letras a), b) y e) del art. 13, segun las guias metodologicas de SERNAGEOMIN "
                          "(art. 16). La resolucion que se pronuncia se rige por el art. 17.")
    else:
        contenido = [{"letra": letra, "item": item, "articulo": "Art. 13 de la Ley 20.551"}
                     for letra, item, _ in CONTENIDO_PLAN_CIERRE]
        nota_contenido = ("Contenido minimo del art. 13 de la Ley 20.551. El plan ademas lleva un capitulo "
                          "de garantias (art. 14 letra l del DS 41/2012) y los costos se expresan en UF.")

    garantia = {"exige": datos["exige_garantia"]}
    if datos["exige_garantia"]:
        garantia.update({
            "monto": ("Valor presente de los costos de todas las medidas de cierre hasta el termino de la "
                      "vida util, mas las medidas de post cierre, incluidos los costos administrativos "
                      "(art. 50 de la Ley 20.551)."),
            "tasa_descuento": ("Tasa de los Bonos del Banco Central en Unidades de Fomento a un plazo "
                               "minimo de 10 anios (BCU-10), art. 50."),
            "instrumentos": ("Categoria A.1 del art. 52: certificados de deposito a la vista, boletas "
                             "bancarias de garantia a la vista, certificados de deposito a menos de 360 "
                             "dias, cartas de credito stand by de emisores con clasificacion minima A y "
                             "polizas de garantia a primer requerimiento de aseguradoras nacionales con "
                             "clasificacion BBB o superior, pagaderas a SERNAGEOMIN a su solo "
                             "requerimiento (Ley 21.169 de 2019)."),
            "custodia": "Deposito Central de Valores o institucion financiera autorizada (art. 52).",
            "integridad": ("La empresa debe velar por la integridad, suficiencia y estabilidad de la "
                           "garantia durante toda la vida util. Tiene 3 dias habiles para informar una "
                           "contingencia y el Servicio tiene 30 dias para resolver (art. 51)."),
            "descuentos": ("Se pueden descontar proporcionalmente las garantias ya constituidas conforme al "
                           "art. 297 del Codigo de Aguas (art. 50)."),
        })
        if vida_util is not None:
            if vida_util < VIDA_UTIL_CORTE_ANIOS:
                plazo = round(vida_util * 2.0 / 3.0, 2)
                regla = "dos tercios de la vida util, porque la faena dura menos de 20 anios"
            else:
                plazo = PLAZO_GARANTIA_VIDA_LARGA_ANIOS
                regla = "15 anios, porque la vida util es de 20 anios o mas"
            garantia["plazo_constitucion_anios"] = plazo
            garantia["regla_plazo"] = ("La garantia se constituye por parcialidades en %s (guia "
                                       "metodologica de SERNAGEOMIN)." % regla)
        else:
            garantia["plazo_constitucion_anios"] = None
            garantia["regla_plazo"] = ("Dime la vida util de la faena y te digo en cuantos anios hay que "
                                       "constituir la garantia: dos tercios de la vida util si dura menos "
                                       "de 20 anios, o 15 anios si dura 20 o mas.")
        garantia["no_calcula"] = (
            "No calculo el monto de cada parcialidad. La progresion del 20 % al 100 % del valor presente "
            "total se extrajo de la guia de SERNAGEOMIN con un OCR degradado y no esta verificada: usarla "
            "para un calculo financiero seria irresponsable. El plazo total si esta verificado.")
    else:
        garantia["motivo"] = ("La garantia financiera del Titulo V de la Ley 20.551 se exige a las empresas "
                              "del procedimiento de aplicacion general, es decir sobre 10.000 t/mes.")

    obligaciones = [
        {"obligacion": "Presentar el plan de cierre para aprobacion de SERNAGEOMIN, elaborado conforme a "
                       "la RCA", "plazo": "antes de iniciar las operaciones", "articulo": "Art. 6 de la Ley 20.551"},
        {"obligacion": "Implementar las medidas de cierre de forma progresiva durante toda la vida util",
         "plazo": "permanente", "articulo": "Art. 2 de la Ley 20.551"},
    ]
    if clave == "general":
        obligaciones.extend([
            {"obligacion": "Auditoria del plan de cierre, a costa de la empresa", "plazo": "cada 5 anios",
             "articulo": "Art. 18 de la Ley 20.551 (y art. 44 del DS 41/2012)"},
            {"obligacion": "Presentar el proyecto de actualizacion del plan despues de la auditoria",
             "plazo": "90 dias desde la notificacion; el Servicio resuelve en 60 dias",
             "articulo": "Art. 23 de la Ley 20.551"},
            {"obligacion": "Informar cualquier contingencia que afecte la garantia",
             "plazo": "3 dias habiles; el Servicio resuelve en 30 dias", "articulo": "Art. 51 de la Ley 20.551"},
            {"obligacion": "Aportar al Fondo para la Gestion de Faenas Mineras Cerradas",
             "plazo": "antes de obtener el certificado de cierre", "articulo": "Arts. 55 a 57 de la Ley 20.551"},
        ])

    no_verificado = [
        "El DS 15/2026, que crearia la declaracion jurada por el sistema SUPER para faenas de hasta 5.000 "
        "t/mes con vigencia de 60 meses, estaba en toma de razon en abril de 2026. NO esta verificada su "
        "publicacion en el Diario Oficial: confirmala antes de usar esa via.",
        "La Ley 21.770 (Ley Marco de Autorizaciones Sectoriales, D.O. 29-09-2025) modifica la Ley 20.551 en "
        "su art. 97, con vigencia diferida a los reglamentos que deben dictarse. No se pudo leer el "
        "articulado completo.",
        "La progresion de las parcialidades de la garantia no esta verificada (OCR degradado de la guia de "
        "SERNAGEOMIN). El plazo total de constitucion si lo esta.",
    ]

    mensaje = "Faena de %s t/mes: %s." % (_texto_numero(toneladas), datos["nombre"])
    if clave == "declaracion_simplificada":
        mensaje += (" Ojo: si la faena llega a tener planta de produccion o deposito de relaves, pasa al "
                    "procedimiento simplificado.")

    return {
        "norma": NORMA_CIERRE,
        "regimen": clave,
        "nombre_regimen": datos["nombre"],
        "umbral": datos["umbral"],
        "articulo_regimen": datos["articulo"],
        "toneladas_mes": toneladas,
        "tiene_planta": bool(tiene_planta),
        "tiene_relaves": bool(tiene_relaves),
        "vida_util_anios": vida_util,
        "contenido_minimo": contenido,
        "nota_contenido": nota_contenido,
        "garantia": garantia,
        "obligaciones": obligaciones,
        "mensaje": mensaje,
        "no_verificado": no_verificado,
    }
