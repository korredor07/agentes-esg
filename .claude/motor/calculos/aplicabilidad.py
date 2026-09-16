# -*- coding: utf-8 -*-
"""Que normativa le aplica a una empresa, segun su perfil y unas pocas respuestas.

Cada regla dice: a quien aplica, que exige, que plazos tiene, que arriesga quien
no cumple y con que skill se trabaja. Las reglas salen de la investigacion
normativa del repositorio (docs/investigacion) y llevan su fuente.

Resultado por regla:
    aplica    -> le corresponde con la informacion disponible
    revisar   -> depende de un dato que la empresa aun no entrego
    no aplica -> queda fuera por pais, giro o tamaño

Esto es orientacion, no asesoria legal: la decision final es de la empresa y su
abogado. El motor nunca afirma que algo "no aplica" cuando le falta el dato:
en ese caso pregunta.
"""

FUENTE_KARIN = "docs/investigacion/03-ley-karin.md"
FUENTE_REP = "docs/investigacion/04-ley-rep-retc.md"
FUENTE_UE = "docs/investigacion/07-union-europea.md"
FUENTE_MARCOS = "docs/investigacion/06-marcos-reporte-metas-greenwashing.md"


def _si(valor):
    """Interpreta si/no/no se. Devuelve True, False o None (no se sabe)."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().lower()
    if texto in ("si", "sí", "true", "1", "y", "yes"):
        return True
    if texto in ("no", "false", "0", "n"):
        return False
    return None


def _trabajadores(perfil):
    try:
        return int(perfil.get("trabajadores") or 0)
    except (TypeError, ValueError):
        return 0


def _exporta_a_ue(perfil, r):
    """True, False o None: lo que diga la persona gana sobre el perfil; si nadie lo dijo, no se sabe."""
    respuesta = _si(r.get("exporta_a_ue"))
    if respuesta is not None:
        return respuesta
    perfil_dice = perfil.get("exporta_a_ue")
    return perfil_dice if isinstance(perfil_dice, bool) else None


# --------------------------------------------------------------------------
# Reglas
# --------------------------------------------------------------------------

def _karin(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una ley chilena."
    if _trabajadores(perfil) == 0 and _si(r.get("tiene_trabajadores")) is False:
        return "no aplica", "Sin personas contratadas no hay relacion laboral que regular."
    return "aplica", "Aplica a todo empleador en Chile, sin importar su tamaño."


def _rep(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una ley chilena."
    respuesta = _si(r.get("pone_productos_prioritarios"))
    if respuesta is True:
        return "aplica", ("La empresa introduce en el mercado chileno envases, neumaticos, aceites, "
                          "aparatos electricos, pilas o baterias, sea fabricandolos o importandolos.")
    if respuesta is False:
        return "no aplica", "No introduce productos prioritarios en el mercado chileno."
    return "revisar", ("Hay que confirmar si vende productos envasados, importa articulos o comercializa "
                       "neumaticos, aceites, aparatos electricos, pilas o baterias.")


def _retc(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una obligacion chilena."
    señales = [_si(r.get("genera_residuos_industriales")), _si(r.get("tiene_calderas")),
               _si(r.get("descarga_riles"))]
    if True in señales:
        return "aplica", "Tiene establecimientos con obligaciones sectoriales que se declaran en el RETC."
    if all(s is False for s in señales):
        return "no aplica", "No declara emisiones, residuos industriales ni descargas."
    return "revisar", ("Hay que confirmar si genera residuos industriales o peligrosos, si tiene calderas o "
                       "generadores, o si descarga riles.")


def _impuesto_verde(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es un impuesto chileno."
    if _si(r.get("fuente_fija_grande")) is True:
        return "aplica", "Sus fuentes fijas superan los umbrales de material particulado o de CO2."
    if _si(r.get("tiene_calderas")) is False:
        return "no aplica", "No tiene fuentes fijas de combustion."
    return "revisar", ("Aplica a establecimientos cuyas fuentes fijas emiten 100 o mas toneladas de material "
                       "particulado o 25.000 o mas toneladas de CO2 al año.")


def _datos_personales_cl(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una ley chilena."
    return "aplica", ("Toda empresa que trate datos de trabajadores, clientes o proveedores queda sujeta a "
                      "la nueva ley de proteccion de datos personales.")


def _inclusion(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una ley chilena."
    personas = _trabajadores(perfil)
    if personas >= 100:
        return "aplica", "Tiene %d personas: la cuota de inclusion laboral aplica desde 100." % personas
    if personas == 0:
        respuesta = _si(r.get("cien_o_mas_trabajadores"))
        if respuesta is True:
            return "aplica", "Tiene 100 o mas personas: la cuota de inclusion laboral aplica."
        if respuesta is False:
            return "no aplica", "Tiene menos de 100 personas; la obligacion parte en 100."
        return "revisar", "Falta saber cuantas personas trabajan en la empresa."
    return "no aplica", "Tiene %d personas; la obligacion parte en 100." % personas


def _delitos_economicos(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una ley chilena."
    return "aplica", ("Las personas juridicas responden penalmente por delitos economicos y ambientales; "
                      "el modelo de prevencion es la principal defensa.")


def _cmf(perfil, r):
    if (perfil.get("pais") or "").upper() != "CL":
        return "no aplica", "Es una norma chilena."
    if _si(r.get("supervisada_cmf")) is True:
        return "aplica", "Es una entidad supervisada por la CMF: debe reportar sostenibilidad en su memoria anual."
    if _si(r.get("supervisada_cmf")) is False:
        return "no aplica", "No es una sociedad supervisada por la CMF."
    return "revisar", "Hay que confirmar si es sociedad anonima abierta o entidad supervisada por la CMF."


def _cbam(perfil, r):
    exporta = _exporta_a_ue(perfil, r)
    if exporta is False:
        return "no aplica", "No exporta a la Union Europea."
    if exporta is None:
        return "revisar", "Falta confirmar si venden a la Union Europea, directo o por intermediario."
    if _si(r.get("exporta_bienes_cbam")) is True:
        return "aplica", ("Exporta bienes cubiertos por el mecanismo de ajuste en frontera (hierro y acero, "
                          "aluminio, cemento, fertilizantes, hidrogeno o electricidad): el importador europeo "
                          "le pedira las emisiones incorporadas.")
    if _si(r.get("exporta_bienes_cbam")) is False:
        return "no aplica", "Sus productos no estan en la lista de bienes cubiertos."
    return "revisar", ("Hay que confirmar si exporta hierro o acero, aluminio, cemento, fertilizantes, "
                       "hidrogeno o electricidad a la Union Europea.")


def _eudr(perfil, r):
    exporta = _exporta_a_ue(perfil, r)
    if exporta is False:
        return "no aplica", "No exporta a la Union Europea."
    if exporta is None:
        return "revisar", "Falta confirmar si venden a la Union Europea, directo o por intermediario."
    if _si(r.get("exporta_commodities_eudr")) is True:
        return "aplica", ("Exporta productos cubiertos por el reglamento de deforestacion (ganado, cacao, cafe, "
                          "palma, caucho, soya o madera y sus derivados).")
    if _si(r.get("exporta_commodities_eudr")) is False:
        return "no aplica", "Sus productos no estan entre las materias primas cubiertas."
    return "revisar", ("Hay que confirmar si exporta ganado, cacao, cafe, aceite de palma, caucho, soya o "
                       "madera y productos derivados.")


def _cadena_valor_ue(perfil, r):
    exporta = _exporta_a_ue(perfil, r)
    if exporta is False:
        return "no aplica", "No vende a clientes de la Union Europea."
    if exporta is None:
        return "revisar", "Falta confirmar si venden a la Union Europea, directo o por intermediario."
    return "aplica", ("Los clientes europeos sujetos a la directiva de reporte de sostenibilidad piden datos a "
                      "sus proveedores. Para pymes fuera de la UE el tope de lo exigible es el estandar "
                      "voluntario VSME.")


def _sostenibilidad_peru(perfil, r):
    if (perfil.get("pais") or "").upper() != "PE":
        return "no aplica", "Es una obligacion peruana."
    if _si(r.get("emisor_valores")) is True:
        return "aplica", "Como emisor de valores debe presentar su reporte de sostenibilidad corporativa a la SMV."
    if _si(r.get("emisor_valores")) is False:
        return "no aplica", "No es emisor de valores inscrito en el registro publico del mercado de valores."
    return "revisar", "Hay que confirmar si la empresa tiene valores inscritos en el mercado peruano."


def _hostigamiento_peru(perfil, r):
    if (perfil.get("pais") or "").upper() != "PE":
        return "no aplica", "Es una obligacion peruana."
    return "aplica", "Todo empleador en Peru debe tener procedimiento de prevencion y sancion del hostigamiento sexual."


REGLAS = [
    {"id": "cl-karin", "pais": "CL", "norma": "Ley 21.643 (Ley Karin)", "dimension": "social",
     "evaluar": _karin, "skill": "ley-karin", "riesgo": "alto", "fuente": FUENTE_KARIN,
     "que_exige": ["Protocolo de prevencion del acoso sexual, laboral y la violencia en el trabajo",
                   "Procedimiento de investigacion con plazos perentorios",
                   "Informar los canales de denuncia cada seis meses",
                   "Gestion de riesgos psicosociales con el organismo administrador de la Ley 16.744"],
     "plazos": "Ante una denuncia: medidas inmediatas, 3 dias habiles para informar a la DT, 30 dias habiles de investigacion.",
     "sancion": "Multa administrativa de la Direccion del Trabajo, que varia segun el tamaño de la empresa."},
    {"id": "cl-rep", "pais": "CL", "norma": "Ley 20.920 (Ley REP)", "dimension": "ambiental",
     "evaluar": _rep, "skill": "ley-rep", "riesgo": "alto", "fuente": FUENTE_REP,
     "que_exige": ["Inscribirse en el registro de productores",
                   "Integrarse a un sistema de gestion y financiar la recoleccion y valorizacion",
                   "Declarar anualmente las toneladas puestas en el mercado",
                   "Cumplir las metas del decreto de su producto prioritario"],
     "plazos": "Declaracion anual en la Ventanilla Unica del RETC.",
     "sancion": "Sanciones de la Superintendencia del Medio Ambiente, de hasta 10.000 unidades tributarias anuales."},
    {"id": "cl-retc", "pais": "CL", "norma": "RETC (DS 1/2013)", "dimension": "ambiental",
     "evaluar": _retc, "skill": "retc", "riesgo": "alto", "fuente": FUENTE_REP,
     "que_exige": ["Declarar emisiones, residuos y transferencias en la Ventanilla Unica",
                   "Mantener los registros y mediciones que respaldan la declaracion"],
     "plazos": "Declaracion jurada anual del RETC entre el 1 y el 31 de octubre; el registro de emisiones de fuentes fijas entre el 1 de enero y el 30 de abril.",
     "sancion": "Sanciones de la Superintendencia del Medio Ambiente y de la autoridad sanitaria."},
    {"id": "cl-impuesto-verde", "pais": "CL", "norma": "Impuesto verde a fuentes fijas", "dimension": "ambiental",
     "evaluar": _impuesto_verde, "skill": "retc", "riesgo": "medio", "fuente": FUENTE_REP,
     "que_exige": ["Medir y reportar las emisiones de las fuentes fijas",
                   "Pagar el impuesto por tonelada de CO2 y de contaminantes locales"],
     "plazos": "Declaracion anual asociada al RETC.",
     "sancion": "Cobro del impuesto con intereses y multas tributarias."},
    {"id": "cl-datos", "pais": "CL", "norma": "Ley 21.719 (proteccion de datos personales)",
     "dimension": "gobernanza", "evaluar": _datos_personales_cl, "skill": "proteccion-datos",
     "riesgo": "alto", "fuente": "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md",
     "que_exige": ["Tener base legal para tratar cada dato personal",
                   "Informar a las personas y atender sus derechos",
                   "Proteger los datos y notificar las vulneraciones",
                   "Evaluar el impacto cuando el tratamiento es de alto riesgo"],
     "plazos": "La ley entra en plena vigencia el 1 de diciembre de 2026.",
     "sancion": "Multas que escalan segun la gravedad, con topes en unidades tributarias y en porcentaje de ingresos."},
    {"id": "cl-inclusion", "pais": "CL", "norma": "Ley 21.015 (inclusion laboral)", "dimension": "social",
     "evaluar": _inclusion, "skill": "social-personas", "riesgo": "medio",
     "fuente": "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md",
     "que_exige": ["Contratar al menos un 1% de personas con discapacidad o pension de invalidez",
                   "Comunicar anualmente el cumplimiento a la Direccion del Trabajo"],
     "plazos": "Comunicacion anual en enero.",
     "sancion": "Multa administrativa de la Direccion del Trabajo."},
    {"id": "cl-delitos", "pais": "CL", "norma": "Ley 21.595 y Ley 20.393 (modelo de prevencion de delitos)",
     "dimension": "gobernanza", "evaluar": _delitos_economicos, "skill": "gobernanza", "riesgo": "alto",
     "fuente": "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md",
     "que_exige": ["Identificar los riesgos de delito del giro",
                   "Implementar un modelo de prevencion con encargado y canal de denuncias",
                   "Capacitar y supervisar su funcionamiento"],
     "plazos": "Permanente.",
     "sancion": "Responsabilidad penal de la empresa: multas, prohibiciones y, en casos graves, disolucion."},
    {"id": "cl-cmf", "pais": "CL", "norma": "Reporte de sostenibilidad de la CMF (NCG 461 y siguientes)",
     "dimension": "gobernanza", "evaluar": _cmf, "skill": "reportes", "riesgo": "alto", "fuente": FUENTE_MARCOS,
     "que_exige": ["Incluir informacion de sostenibilidad y gobierno corporativo en la memoria anual",
                   "Reportar indicadores ambientales, sociales y de gobernanza con trazabilidad"],
     "plazos": "Junto con la memoria anual.",
     "sancion": "Sanciones de la Comision para el Mercado Financiero."},
    {"id": "ue-cbam", "pais": "*", "norma": "CBAM (mecanismo de ajuste en frontera de la UE)",
     "dimension": "ambiental", "evaluar": _cbam, "skill": "cbam", "riesgo": "alto", "fuente": FUENTE_UE,
     "que_exige": ["Calcular las emisiones incorporadas de los bienes exportados",
                   "Entregar esa informacion al importador europeo, que declara y compra certificados"],
     "plazos": "Periodo definitivo desde 2026; la primera declaracion anual del importador es en septiembre de 2027.",
     "sancion": "El costo se traslada al precio: quien no entrega datos pierde competitividad frente al valor por defecto."},
    {"id": "ue-eudr", "pais": "*", "norma": "EUDR (reglamento de deforestacion de la UE)",
     "dimension": "ambiental", "evaluar": _eudr, "skill": "eudr", "riesgo": "alto", "fuente": FUENTE_UE,
     "que_exige": ["Demostrar que el producto no proviene de tierras deforestadas despues del 31-12-2020",
                   "Entregar la geolocalizacion de los predios de origen",
                   "Sostener un sistema de diligencia debida y trazabilidad"],
     "plazos": "Segun el calendario vigente del reglamento y el tamaño del operador europeo.",
     "sancion": "Para el operador europeo, multas de al menos el 4% de su facturacion en la UE y retiro del producto."},
    {"id": "ue-cadena", "pais": "*", "norma": "Exigencias de clientes europeos (CSRD y VSME)",
     "dimension": "gobernanza", "evaluar": _cadena_valor_ue, "skill": "union-europea", "riesgo": "medio",
     "fuente": FUENTE_UE,
     "que_exige": ["Responder cuestionarios de sostenibilidad de clientes europeos",
                   "Tener huella de carbono y datos sociales basicos con respaldo"],
     "plazos": "Cuando el cliente lo solicite, normalmente en su ciclo anual de reporte.",
     "sancion": "No es una multa: es perder al cliente o quedar fuera de su lista de proveedores."},
    {"id": "pe-smv", "pais": "PE", "norma": "Reporte de Sostenibilidad Corporativa (SMV)",
     "dimension": "gobernanza", "evaluar": _sostenibilidad_peru, "skill": "reportes", "riesgo": "medio",
     "fuente": "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md",
     "que_exige": ["Presentar el reporte de sostenibilidad corporativa junto con la memoria anual"],
     "plazos": "Anual, junto con la informacion financiera.",
     "sancion": "Sanciones de la Superintendencia del Mercado de Valores."},
    {"id": "pe-hostigamiento", "pais": "PE", "norma": "Ley 27942 (hostigamiento sexual laboral)",
     "dimension": "social", "evaluar": _hostigamiento_peru, "skill": "social-personas", "riesgo": "alto",
     "fuente": "docs/investigacion/05-chile-peru-gobernanza-clima-datos.md",
     "que_exige": ["Tener politica y procedimiento de prevencion y sancion del hostigamiento sexual",
                   "Capacitar al personal y atender las quejas en los plazos del reglamento"],
     "plazos": "Plazos breves desde la queja: medidas de proteccion y resolucion del procedimiento.",
     "sancion": "Multas de la SUNAFIL."},
]

PREGUNTAS = [
    {"clave": "tiene_trabajadores", "pregunta": "¿La empresa tiene personas contratadas?",
     "para_que": "Define casi todas las obligaciones laborales."},
    {"clave": "pone_productos_prioritarios", "paises": ["CL"],
     "pregunta": "¿Venden productos envasados, importan articulos, o comercializan neumaticos, aceites, "
                 "aparatos electricos, pilas o baterias?",
     "para_que": "Define si le aplica la Ley REP."},
    {"clave": "cien_o_mas_trabajadores", "paises": ["CL"],
     "pregunta": "¿La empresa tiene 100 o mas trabajadores?",
     "para_que": "Define si aplica la cuota de inclusion laboral (Ley 21.015). Se deduce solo si el perfil ya dice cuantas personas trabajan."},
    {"clave": "tiene_calderas", "paises": ["CL"], "pregunta": "¿Tienen calderas, hornos, grupos electrogenos u otras fuentes fijas?",
     "para_que": "Define obligaciones de declaracion de emisiones e impuesto verde."},
    {"clave": "genera_residuos_industriales", "paises": ["CL"],
     "pregunta": "¿Generan residuos industriales o peligrosos (aceites, solventes, lodos, chatarra)?",
     "para_que": "Define obligaciones de declaracion de residuos."},
    {"clave": "descarga_riles", "paises": ["CL"], "pregunta": "¿Descargan aguas del proceso a un rio, al mar o al alcantarillado?",
     "para_que": "Define obligaciones sobre residuos liquidos."},
    {"clave": "fuente_fija_grande", "paises": ["CL"],
     "pregunta": "¿Alguna instalacion emite mas de 100 toneladas de material particulado o mas de 25.000 "
                 "toneladas de CO2 al año?",
     "para_que": "Define si paga impuesto verde."},
    {"clave": "supervisada_cmf", "paises": ["CL"], "pregunta": "¿Es sociedad anonima abierta o esta supervisada por la CMF?",
     "para_que": "Define si debe reportar sostenibilidad en su memoria anual."},
    {"clave": "exporta_a_ue", "pregunta": "¿Venden a la Union Europea, directo o a traves de otra empresa?",
     "para_que": "Define las exigencias europeas."},
    {"clave": "exporta_bienes_cbam",
     "pregunta": "¿Exportan hierro o acero, aluminio, cemento, fertilizantes, hidrogeno o electricidad a la UE?",
     "para_que": "Define si le aplica el CBAM."},
    {"clave": "exporta_commodities_eudr",
     "pregunta": "¿Exportan a la UE ganado, cacao, cafe, aceite de palma, caucho, soya o madera?",
     "para_que": "Define si le aplica el reglamento de deforestacion."},
    {"clave": "emisor_valores", "paises": ["PE"], "pregunta": "¿La empresa tiene valores inscritos en el mercado de valores?",
     "para_que": "Define obligaciones de reporte en Peru."},
]


def respuestas_efectivas(perfil, respuestas=None):
    """Las respuestas guardadas, completadas con lo que ya se sabe por el perfil.

    Asi el calendario y la revision de normativa usan exactamente la misma base, y no
    se le pregunta a la persona algo que ya dijo al registrar la empresa.
    Una respuesta explicita de la persona siempre gana sobre lo deducido.
    """
    efectivas = dict(respuestas or {})
    personas = _trabajadores(perfil)
    if "tiene_trabajadores" not in efectivas and personas > 0:
        efectivas["tiene_trabajadores"] = "si"
    if "cien_o_mas_trabajadores" not in efectivas and personas > 0:
        efectivas["cien_o_mas_trabajadores"] = "si" if personas >= 100 else "no"
    exporta = perfil.get("exporta_a_ue")
    if "exporta_a_ue" not in efectivas and isinstance(exporta, bool):
        efectivas["exporta_a_ue"] = "si" if exporta else "no"
    if "fuente_fija_grande" not in efectivas and _si(efectivas.get("tiene_calderas")) is False:
        # Sin fuentes fijas de combustion no puede haber una fuente fija grande.
        efectivas["fuente_fija_grande"] = "no"
    return efectivas


# Preguntas que solo tienen sentido si otra se respondio que si. Primero se pregunta la
# de arriba: a quien no exporta a Europa no se le pregunta que exporta a Europa.
DEPENDENCIAS = {
    "exporta_bienes_cbam": "exporta_a_ue",
    "exporta_commodities_eudr": "exporta_a_ue",
    "fuente_fija_grande": "tiene_calderas",
}


def _vale_la_pena_preguntar(pregunta, respuestas):
    previa = DEPENDENCIAS.get(pregunta["clave"])
    return previa is None or _si(respuestas.get(previa)) is True


def preguntas_aplicables(perfil):
    """Solo las preguntas que tienen sentido para el pais de la empresa."""
    pais = (perfil.get("pais") or "").upper()
    return [p for p in PREGUNTAS if not p.get("paises") or pais in p["paises"]]


def evaluar(perfil, respuestas=None):
    """Evalua todas las reglas y agrupa el resultado."""
    respuestas = respuestas_efectivas(perfil, respuestas)
    pais = (perfil.get("pais") or "").upper()
    aplican, revisar, fuera = [], [], []
    for regla in REGLAS:
        estado, motivo = regla["evaluar"](perfil, respuestas)
        ficha = {clave: regla[clave] for clave in
                 ("id", "norma", "dimension", "skill", "riesgo", "que_exige", "plazos", "sancion", "fuente")}
        ficha["estado"] = estado
        ficha["motivo"] = motivo
        {"aplica": aplican, "revisar": revisar, "no aplica": fuera}[estado].append(ficha)

    orden = {"alto": 0, "medio": 1, "bajo": 2}
    aplican.sort(key=lambda f: orden.get(f["riesgo"], 3))
    pendientes = [p for p in preguntas_aplicables(perfil)
                  if p["clave"] not in respuestas and _vale_la_pena_preguntar(p, respuestas)]
    return {
        "pais": pais,
        "aplican": aplican,
        "por_revisar": revisar,
        "no_aplican": fuera,
        "preguntas_pendientes": pendientes,
        "resumen": ("Le aplican %d normas identificadas; %d quedan por confirmar."
                    % (len(aplican), len(revisar))),
        "aviso": ("Orientacion basada en el perfil declarado y en normativa publica. No es asesoria legal: "
                  "una revision con abogado es indispensable antes de tomar decisiones."),
    }
