# -*- coding: utf-8 -*-
"""Diagnostico ESG: puntaje de madurez y brechas priorizadas.

Que es y que no es:

- ES una autoevaluacion de madurez y cumplimiento, calculada con los datos que
  hay en la carpeta de la empresa y con respuestas que da la propia persona.
- NO es una calificacion ESG de mercado (tipo agencia de rating) ni una
  certificacion. El agente debe decirlo asi cada vez que entregue el puntaje.

Como se calcula:

    puntaje de una dimension = puntos obtenidos / puntos posibles x 100
    puntos de un indicador   = peso x factor del estado
        cumple = 1.0 | parcial = 0.5 | no_cumple = 0 | sin_datos = 0
    los indicadores "no aplica" salen del denominador.
    puntaje general = promedio simple de las tres dimensiones evaluables.

Cada indicador no cumplido genera una brecha con prioridad:

    prioridad = peso x riesgo   (riesgo: legal 3, reputacional 2, gestion 1)
"""

import datetime
import glob
import json
import os

RIESGOS = {"legal": 3, "reputacional": 2, "gestion": 1}
FACTOR_ESTADO = {"cumple": 1.0, "parcial": 0.5, "no_cumple": 0.0, "sin_datos": 0.0}
DIMENSIONES = {"ambiental": "Ambiental", "social": "Social", "gobernanza": "Gobernanza"}
ESTADOS_BRECHA = ["abierta", "reconocida", "pospuesta", "resuelta"]

# Catalogo de indicadores. "automatico" indica que el motor lo evalua solo;
# el resto lo responde la persona a traves del agente.
INDICADORES = [
    # ---------------------------------------------------------------- Ambiental
    {"id": "amb-perfil", "dimension": "ambiental", "peso": 1, "riesgo": "gestion",
     "titulo": "Perfil de la empresa completo",
     "porque": "Sin saber donde opera y a que se dedica no se puede saber que normas le aplican.",
     "como_cerrarlo": "Completar sector, tamano, pais, año base y sitios.", "automatico": "perfil_completo"},
    {"id": "amb-huella", "dimension": "ambiental", "peso": 3, "riesgo": "reputacional",
     "titulo": "Huella de carbono del ultimo año calculada",
     "porque": "Es el dato que piden clientes, bancos y licitaciones.",
     "como_cerrarlo": "Cargar consumos de energia y combustibles y calcular la huella.",
     "automatico": "huella_calculada"},
    {"id": "amb-alcance1", "dimension": "ambiental", "peso": 2, "riesgo": "gestion",
     "titulo": "Alcance 1 medido (combustibles y fugas propias)",
     "porque": "Es lo que la empresa controla directamente y puede reducir primero.",
     "como_cerrarlo": "Registrar litros de combustible, gas y recargas de refrigerante.",
     "automatico": "alcance_1"},
    {"id": "amb-alcance2", "dimension": "ambiental", "peso": 2, "riesgo": "gestion",
     "titulo": "Alcance 2 medido (electricidad comprada)",
     "porque": "Suele ser la fuente mas facil de medir y de reducir.",
     "como_cerrarlo": "Cargar los kWh de las boletas del año.", "automatico": "alcance_2"},
    {"id": "amb-alcance3", "dimension": "ambiental", "peso": 2, "riesgo": "reputacional",
     "titulo": "Alcance 3 estimado (cadena de valor)",
     "porque": "Suele ser la mayor parte de la huella y es lo que piden los clientes europeos.",
     "como_cerrarlo": "Estimar al menos compras, fletes, viajes y residuos.", "automatico": "alcance_3"},
    {"id": "amb-calidad", "dimension": "ambiental", "peso": 2, "riesgo": "reputacional",
     "titulo": "Datos respaldados en boletas o mediciones",
     "porque": "Un numero estimado no resiste una auditoria ni una exigencia de cliente.",
     "como_cerrarlo": "Reemplazar estimaciones por boletas, facturas o lecturas de medidor.",
     "automatico": "calidad_datos"},
    {"id": "amb-metas", "dimension": "ambiental", "peso": 2, "riesgo": "reputacional",
     "titulo": "Meta de reduccion definida",
     "porque": "Medir sin meta no reduce nada, y las metas se piden en todos los reportes.",
     "como_cerrarlo": "Definir año base, meta y plazo.", "automatico": "metas_definidas"},
    {"id": "amb-residuos", "dimension": "ambiental", "peso": 2, "riesgo": "legal",
     "titulo": "Gestion de residuos con destino conocido",
     "porque": "Saber cuanto se genera y a donde va es la base de casi toda la normativa de residuos.",
     "como_cerrarlo": "Registrar toneladas por tipo y su destino (relleno, reciclaje, compostaje)."},
    {"id": "amb-agua", "dimension": "ambiental", "peso": 1, "riesgo": "gestion",
     "titulo": "Consumo de agua medido",
     "porque": "Es un indicador exigido en la mayoria de los reportes y clave en zonas con escasez.",
     "como_cerrarlo": "Registrar los metros cubicos de las boletas o del medidor."},
    {"id": "amb-permisos", "dimension": "ambiental", "peso": 3, "riesgo": "legal",
     "titulo": "Permisos y declaraciones ambientales al dia",
     "porque": "Las declaraciones fuera de plazo son la causa mas comun de multas ambientales.",
     "como_cerrarlo": "Revisar que declaraciones le aplican y sus fechas."},
    # ------------------------------------------------------------------- Social
    {"id": "soc-personas", "dimension": "social", "peso": 2, "riesgo": "gestion",
     "titulo": "Datos de personas registrados",
     "porque": "Dotacion, rotacion y accidentes son la base de los indicadores sociales.",
     "como_cerrarlo": "Llenar la planilla de personas.", "automatico": "personas_datos"},
    {"id": "soc-contratos", "dimension": "social", "peso": 3, "riesgo": "legal",
     "titulo": "Contratos y obligaciones laborales al dia",
     "porque": "Es lo primero que revisa una fiscalizacion laboral.",
     "como_cerrarlo": "Verificar contratos, jornada, cotizaciones y reglamento interno."},
    {"id": "soc-riesgos", "dimension": "social", "peso": 3, "riesgo": "legal",
     "titulo": "Prevencion de riesgos laborales activa",
     "porque": "Obligatorio y ademas es lo que evita accidentes graves.",
     "como_cerrarlo": "Matriz de riesgos, elementos de proteccion y capacitacion vigente."},
    {"id": "soc-karin", "dimension": "social", "peso": 3, "riesgo": "legal", "paises": ["CL"],
     "titulo": "Protocolo de prevencion de acoso y violencia laboral (Ley Karin)",
     "porque": "Es obligatorio para todo empleador en Chile y su ausencia se multa.",
     "como_cerrarlo": "Elaborar el protocolo, incorporarlo al reglamento interno y difundirlo."},
    {"id": "soc-canal", "dimension": "social", "peso": 2, "riesgo": "legal",
     "titulo": "Canal para recibir denuncias",
     "porque": "Sin canal, los problemas llegan directo a la autoridad o a la prensa.",
     "como_cerrarlo": "Definir un canal conocido, con responsable y plazos."},
    {"id": "soc-capacitacion", "dimension": "social", "peso": 1, "riesgo": "gestion",
     "titulo": "Plan de capacitacion",
     "porque": "Es un indicador estandar de los reportes y mejora la retencion.",
     "como_cerrarlo": "Registrar horas de capacitacion por año y area."},
    {"id": "soc-inclusion", "dimension": "social", "peso": 2, "riesgo": "legal", "paises": ["CL"],
     "titulo": "Cumplimiento de inclusion laboral",
     "porque": "Las empresas de 100 o mas trabajadores deben cumplir la cuota de la Ley 21.015.",
     "como_cerrarlo": "Revisar la dotacion, las contrataciones y la comunicacion anual."},
    {"id": "soc-brecha", "dimension": "social", "peso": 1, "riesgo": "reputacional",
     "titulo": "Brecha salarial medida",
     "porque": "Se pide en los reportes y es un riesgo reputacional si no se conoce.",
     "como_cerrarlo": "Comparar remuneraciones promedio por cargo equivalente."},
    # --------------------------------------------------------------- Gobernanza
    {"id": "gob-responsable", "dimension": "gobernanza", "peso": 2, "riesgo": "gestion",
     "titulo": "Responsable de sostenibilidad designado",
     "porque": "Sin un responsable con nombre, nada de esto se sostiene en el tiempo.",
     "como_cerrarlo": "Designar a una persona y dejarlo por escrito."},
    {"id": "gob-etica", "dimension": "gobernanza", "peso": 2, "riesgo": "reputacional",
     "titulo": "Codigo de etica o conducta vigente",
     "porque": "Es la base de cualquier programa de cumplimiento y lo piden los clientes grandes.",
     "como_cerrarlo": "Redactarlo, aprobarlo y difundirlo con acuse de recibo."},
    {"id": "gob-delitos", "dimension": "gobernanza", "peso": 3, "riesgo": "legal", "paises": ["CL"],
     "titulo": "Modelo de prevencion de delitos",
     "porque": "La Ley 21.595 amplio la responsabilidad penal de las empresas.",
     "como_cerrarlo": "Identificar riesgos, definir controles y designar un encargado."},
    {"id": "gob-datos", "dimension": "gobernanza", "peso": 3, "riesgo": "legal",
     "titulo": "Proteccion de datos personales",
     "porque": "Se manejan datos de trabajadores y clientes; el incumplimiento tiene multas altas.",
     "como_cerrarlo": "Inventariar que datos se tratan, para que, y como se protegen."},
    {"id": "gob-evidencias", "dimension": "gobernanza", "peso": 2, "riesgo": "reputacional",
     "titulo": "Evidencias respaldadas y verificables",
     "porque": "Un dato sin respaldo no sirve ante un auditor, un cliente ni un tribunal.",
     "como_cerrarlo": "Registrar los archivos de respaldo en la boveda de evidencias.",
     "automatico": "evidencias"},
    {"id": "gob-reporte", "dimension": "gobernanza", "peso": 1, "riesgo": "reputacional",
     "titulo": "Reporte o comunicacion de sostenibilidad",
     "porque": "Es la forma de mostrar el trabajo hecho a clientes, bancos y trabajadores.",
     "como_cerrarlo": "Publicar al menos un resumen anual con datos respaldados."},
    {"id": "gob-proveedores", "dimension": "gobernanza", "peso": 1, "riesgo": "gestion",
     "titulo": "Criterios ESG en la compra a proveedores",
     "porque": "La mayor parte del impacto esta en la cadena de suministro.",
     "como_cerrarlo": "Incluir preguntas ambientales y laborales en la evaluacion de proveedores."},
]


# --------------------------------------------------------------------------
# Evaluadores automaticos
# --------------------------------------------------------------------------

def _ultimo_resultado_huella(ruta_empresa):
    archivos = sorted(glob.glob(os.path.join(ruta_empresa, "resultados", "huella_*.json")))
    for ruta in reversed(archivos):
        try:
            with open(ruta, encoding="utf-8") as archivo:
                return json.load(archivo)
        except (ValueError, OSError):
            continue
    return None


def _estado_automatico(clave, contexto):
    perfil = contexto["perfil"]
    ruta = contexto["ruta"]
    huella = contexto.get("huella")

    if clave == "perfil_completo":
        faltan = [c for c in ("nombre", "pais", "sector", "tamano", "anio_base") if not perfil.get(c)]
        if not faltan and perfil.get("sitios"):
            return "cumple", "Perfil completo."
        if faltan:
            return ("parcial" if len(faltan) <= 2 else "no_cumple"), "Falta: %s." % ", ".join(faltan)
        return "parcial", "Falta registrar los sitios donde opera."

    if clave == "huella_calculada":
        if not huella:
            return "no_cumple", "Todavia no hay ningun calculo de huella guardado."
        anio_dato = str(huella.get("periodo", ""))[:4]
        anio_actual = datetime.date.today().year
        if anio_dato.isdigit() and anio_actual - int(anio_dato) > 2:
            return "parcial", "El ultimo calculo es de %s: conviene actualizarlo." % anio_dato
        return "cumple", "Huella calculada (%s tCO2e)." % round(huella.get("total_t_co2e", 0), 1)

    if clave in ("alcance_1", "alcance_2", "alcance_3"):
        if not huella:
            return "sin_datos", "Falta calcular la huella."
        dato = (huella.get("por_alcance") or {}).get(clave, {})
        if dato.get("kg_co2e"):
            return "cumple", "%s tCO2e registradas." % round(dato["kg_co2e"] / 1000.0, 1)
        return "no_cumple", "No hay datos cargados de este alcance."

    if clave == "calidad_datos":
        if not huella:
            return "sin_datos", "Falta calcular la huella."
        porcentaje = (huella.get("calidad_datos", {}).get("porcentaje", {}))
        respaldado = porcentaje.get("verificado", 0) + porcentaje.get("reportado", 0)
        if respaldado >= 70:
            return "cumple", "%d%% de la huella viene de datos respaldados." % round(respaldado)
        if respaldado >= 40:
            return "parcial", "Solo el %d%% viene de datos respaldados." % round(respaldado)
        return "no_cumple", "Casi todo son estimaciones (%d%% respaldado)." % round(respaldado)

    if clave == "personas_datos":
        return ("cumple", "Planilla de personas cargada.") if os.path.isfile(
            os.path.join(ruta, "datos", "personas.xlsx")) else ("no_cumple", "Falta la planilla de personas.")

    if clave == "metas_definidas":
        return ("cumple", "Meta registrada.") if os.path.isfile(
            os.path.join(ruta, "seguimiento", "metas.json")) else ("no_cumple", "Sin meta de reduccion definida.")

    if clave == "evidencias":
        registro = os.path.join(ruta, "evidencias", "registro.jsonl")
        if not os.path.isfile(registro) or os.path.getsize(registro) == 0:
            return "no_cumple", "No hay respaldos registrados."
        return "cumple", "Hay respaldos registrados en la boveda de evidencias."

    return "sin_datos", ""


# --------------------------------------------------------------------------
# Evaluacion completa
# --------------------------------------------------------------------------

def indicadores_aplicables(perfil):
    pais = (perfil.get("pais") or "").upper()
    aplicables = []
    for indicador in INDICADORES:
        paises = indicador.get("paises")
        if paises and pais not in paises:
            continue
        aplicables.append(indicador)
    return aplicables


def evaluar(perfil, ruta_empresa, respuestas=None):
    """Calcula puntajes y brechas. `respuestas` son las respuestas manuales guardadas."""
    respuestas = respuestas or {}
    contexto = {"perfil": perfil, "ruta": ruta_empresa, "huella": _ultimo_resultado_huella(ruta_empresa)}

    detalle, brechas = [], []
    acumulado = {clave: {"obtenidos": 0.0, "posibles": 0.0} for clave in DIMENSIONES}

    for indicador in indicadores_aplicables(perfil):
        guardada = respuestas.get(indicador["id"], {})
        if indicador.get("automatico"):
            estado, nota = _estado_automatico(indicador["automatico"], contexto)
        else:
            estado = guardada.get("estado", "sin_datos")
            nota = guardada.get("nota", "")
        if estado not in FACTOR_ESTADO and estado != "no_aplica":
            estado = "sin_datos"

        fila = {
            "id": indicador["id"], "dimension": indicador["dimension"], "titulo": indicador["titulo"],
            "peso": indicador["peso"], "riesgo": indicador["riesgo"], "estado": estado, "nota": nota,
            "porque": indicador["porque"], "como_cerrarlo": indicador["como_cerrarlo"],
            "automatico": bool(indicador.get("automatico")),
        }
        detalle.append(fila)

        if estado == "no_aplica":
            continue
        casilla = acumulado[indicador["dimension"]]
        casilla["posibles"] += indicador["peso"]
        casilla["obtenidos"] += indicador["peso"] * FACTOR_ESTADO[estado]

        if estado in ("no_cumple", "parcial", "sin_datos"):
            brechas.append({
                "id": indicador["id"], "titulo": indicador["titulo"], "dimension": indicador["dimension"],
                "estado_indicador": estado,
                "prioridad": indicador["peso"] * RIESGOS.get(indicador["riesgo"], 1),
                "riesgo": indicador["riesgo"], "porque": indicador["porque"],
                "que_hacer": indicador["como_cerrarlo"], "nota": nota,
                "seguimiento": guardada.get("seguimiento", "abierta"),
                "responsable": guardada.get("responsable", ""),
                "fecha_compromiso": guardada.get("fecha_compromiso", ""),
            })

    puntajes = {}
    for clave, valores in acumulado.items():
        puntajes[clave] = round(valores["obtenidos"] / valores["posibles"] * 100.0, 1) if valores["posibles"] else None
    evaluables = [v for v in puntajes.values() if v is not None]
    general = round(sum(evaluables) / len(evaluables), 1) if evaluables else 0.0

    con_datos = [f for f in detalle if f["automatico"]]
    respaldados = [f for f in con_datos if f["estado"] == "cumple"]
    listo_auditoria = round(len(respaldados) / len(con_datos) * 100.0, 1) if con_datos else 0.0

    brechas.sort(key=lambda b: (-b["prioridad"], b["dimension"]))
    sin_responder = [f["id"] for f in detalle if not f["automatico"] and f["estado"] == "sin_datos"]

    return {
        "empresa": perfil.get("nombre"),
        "evaluado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "puntaje_general": general,
        "puntajes": {clave: puntajes[clave] for clave in DIMENSIONES},
        "listo_para_auditoria_pct": listo_auditoria,
        "indicadores": detalle,
        "brechas": brechas,
        "brechas_criticas": [b for b in brechas if b["prioridad"] >= 6 and b["seguimiento"] != "resuelta"],
        "preguntas_pendientes": sin_responder,
        "total_indicadores": len(detalle),
        "metodologia": ("Autoevaluacion de madurez y cumplimiento con los datos de la carpeta y las "
                        "respuestas de la empresa. No es una calificacion ESG de mercado ni una certificacion."),
    }


def nivel(puntaje):
    """Traduce el puntaje a una palabra que la persona entienda."""
    if puntaje is None:
        return "sin evaluar", "gris"
    if puntaje >= 80:
        return "avanzado", "verde"
    if puntaje >= 60:
        return "en marcha", "verde"
    if puntaje >= 40:
        return "inicial", "amarillo"
    return "sin gestion", "rojo"
