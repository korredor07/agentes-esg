# -*- coding: utf-8 -*-
"""Normativa europea que alcanza a un exportador de Chile o Peru.

Cubre cinco mecanismos, cada uno con su reglamento y su articulo citado:

    CBAM          Reglamento (UE) 2023/956, modificado por el Reglamento (UE) 2025/2083
    ETS maritimo  Directiva 2003/87/CE, modificada por la Directiva (UE) 2023/959
    FuelEU        Reglamento (UE) 2023/1805
    CSRD          Directiva 2013/34/UE, tras la Directiva (UE) 2026/470 ("Omnibus I")
    EUDR          Reglamento (UE) 2023/1115, tras el Reglamento (UE) 2025/2650

Fuente unica de los datos: docs/investigacion/07-union-europea.md, que transcribe
los textos del Diario Oficial y marca cada dato como VERIFICADO, SECUNDARIO o NO
VERIFICADO.

Regla de la casa: lo que la investigacion dejo como NO VERIFICADO no se inventa.
El motor pide el dato a la persona o dice que no esta confirmado. Los precios
(derecho del RCDE, certificado CBAM) son de mercado y cambian a diario: siempre
los entrega quien hace el calculo, nunca estan escritos en el codigo.
"""

import unicodedata

from nucleo.salida import Problema

FUENTE = "docs/investigacion/07-union-europea.md"

AVISO_LEGAL = ("Orientacion de apoyo, no asesoria legal ni aduanera. Los reglamentos europeos cambiaron "
               "en 2025 y 2026: antes de firmar un contrato o declarar ante una autoridad, confirmalo con "
               "tu cliente europeo, tu agente de aduana o tu asesoria.")

AVISO_PRECIOS = ("Los precios del derecho de emision europeo y del certificado CBAM son de mercado y "
                 "cambian todos los dias. El motor usa el precio que tu entregues y lo deja registrado "
                 "en el resultado para que el calculo sea auditable.")

# Lo que la investigacion normativa NO pudo confirmar contra fuente oficial.
# Cada entrada explica que falta y como resolverlo, en lenguaje de persona.
PENDIENTES_DE_VERIFICAR = {
    "cbam_valores_por_defecto": {
        "que_falta": ("La tabla de valores por defecto del periodo definitivo del CBAM (los que usa el "
                      "importador cuando el exportador no entrega datos): no se confirmo el numero ni la "
                      "fecha del acto de ejecucion que los publica."),
        "consecuencia": "El motor no puede estimar el escenario «sin datos del proveedor».",
        "como_resolverlo": ("Pidelos a tu cliente europeo o descarga el fichero «Default values definitive "
                            "period» de la Direccion General de Fiscalidad y Union Aduanera de la Comision."),
    },
    "cbam_deduccion_origen": {
        "que_falta": ("La mecanica exacta de la deduccion por el precio del carbono ya pagado en el pais de "
                      "origen (art. 9 del Reglamento (UE) 2023/956) se remite a un acto de ejecucion que no "
                      "se pudo leer."),
        "consecuencia": ("El descuento que calcula el motor es una estimacion abierta, no la formula oficial. "
                         "Si el impuesto verde chileno sera aceptado o no, tampoco esta confirmado."),
        "como_resolverlo": "Confirmarlo con el importador europeo antes de prometerle un descuento.",
    },
    "cbam_anexo_i_subpartidas": {
        "que_falta": "El detalle completo de subpartidas arancelarias de hierro, acero y aluminio del Anexo I.",
        "consecuencia": "El motor decide por sector, no por codigo arancelario exacto.",
        "como_resolverlo": "Que tu agente de aduana confirme el codigo arancelario de cada producto.",
    },
    "ets_exclusiones_mrv": {
        "que_falta": ("El contenido exacto de los apartados 1 bis y 1 ter del art. 2 del Reglamento (UE) "
                      "2015/757, que definen que actividades quedan fuera del ETS maritimo."),
        "consecuencia": "El motor asume que el viaje esta cubierto; puede haber exclusiones que no conoce.",
        "como_resolverlo": "Preguntarselo a la naviera.",
    },
    "gwp_fueleu": {
        "que_falta": ("Los valores de potencial de calentamiento global a 100 años (GWP) a los que remite "
                      "FuelEU: estan en el Anexo V de la Directiva (UE) 2018/2001 y no se leyeron directamente."),
        "consecuencia": "Sin ellos no se puede convertir el metano y el oxido nitroso a CO2 equivalente.",
        "como_resolverlo": "Entregar los valores que use la naviera o su verificador y dejarlos registrados.",
    },
    "eudr_fechas_articulado": {
        "que_falta": ("Las fechas de aplicacion del EUDR proceden de la pagina oficial de la Comision Europea "
                      "y no se confirmaron contra el articulo 38 del texto consolidado."),
        "consecuencia": "Sirven para planificar, no para discutir un plazo con una autoridad.",
        "como_resolverlo": "Confirmarlas con el operador europeo que presentara la declaracion.",
    },
    "eudr_geolocalizacion": {
        "que_falta": ("El formato exacto de la geolocalizacion (decimales, punto o poligono segun el tamaño "
                      "del predio) tras las modificaciones de 2024 y 2025."),
        "consecuencia": "El motor pide las coordenadas pero no fija el formato como obligatorio.",
        "como_resolverlo": "Pedir al cliente europeo el formato que exige su sistema de declaracion.",
    },
    "csrd_sucursal_ue": {
        "que_falta": ("Si el umbral de la sucursal en la UE del art. 40 bis sigue en 40 millones de euros "
                      "tras el Omnibus I."),
        "consecuencia": "Un grupo con sucursal europea no puede saber con certeza si entra en ambito.",
        "como_resolverlo": "Consultarlo con la asesoria del grupo en Europa.",
    },
    "csrd_tope_vsme_extraterritorial": {
        "que_falta": ("Si un proveedor que no esta domiciliado en la Union Europea puede invocar el derecho "
                      "a negarse a entregar informacion que excede el estandar VSME."),
        "consecuencia": "El tope VSME sirve para negociar, no como un derecho garantizado.",
        "como_resolverlo": "Revisar la ley aplicable al contrato con el cliente europeo.",
    },
    "csrd_espana": {
        "que_falta": ("Si España ya aprobo la norma que transpone la CSRD y que pasa con la Ley 11/2018 de "
                      "informacion no financiera."),
        "consecuencia": ("Un cliente español mediano puede seguir obligado por la Ley 11/2018 (desde 250 "
                         "trabajadores) aunque quede fuera de la CSRD, y ahi el tope VSME no lo ampara."),
        "como_resolverlo": "Preguntarle al cliente español bajo que norma te esta pidiendo los datos.",
    },
}


def pendientes(*temas):
    """Devuelve la ficha de los puntos que la investigacion no pudo verificar."""
    salida = []
    for tema in temas:
        ficha = PENDIENTES_DE_VERIFICAR.get(tema)
        if ficha:
            salida.append(dict(ficha, tema=tema))
    return salida


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _clave(texto):
    """Normaliza un nombre escrito por una persona: sin tildes, sin espacios."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    for signo in (" ", "-", ".", "/", "_"):
        texto = texto.replace(signo, "")
    return texto


def _numero(valor, nombre, obligatorio=True, minimo=None):
    """Convierte a numero un dato escrito por una persona."""
    if valor in (None, "", True, False):
        if obligatorio:
            raise Problema(
                "Falta %s." % nombre,
                "Es un dato que solo tienes tu: escribelo y repetimos el calculo.",
            )
        return None
    try:
        numero = float(str(valor).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        raise Problema(
            "«%s» no es un numero valido para %s." % (valor, nombre),
            "Escribe solo el numero, sin simbolos de moneda ni unidades. Por ejemplo: 1500.",
        )
    if minimo is not None and numero < minimo:
        raise Problema(
            "%s no puede ser menor que %s (recibi %s)." % (nombre.capitalize(), minimo, valor),
            "Revisa el dato y volvemos a calcular.",
        )
    return numero


def _anio(valor, nombre="el año"):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        raise Problema("«%s» no es un año valido para %s." % (valor, nombre),
                       "Escribe solo el año, por ejemplo 2026.")


# --------------------------------------------------------------------------
# CBAM — Reglamento (UE) 2023/956, modificado por el Reglamento (UE) 2025/2083
# --------------------------------------------------------------------------

# Anexo I del Reg. (UE) 2023/956 (sectores) y Anexo II (que emisiones se computan).
# "indirectas": True  -> se computan directas e indirectas (cemento y fertilizantes)
#               False -> solo emisiones directas (hierro y acero, aluminio, hidrogeno)
#               None  -> la investigacion no lo confirmo para ese sector
SECTORES_CBAM = {
    "cemento": {
        "nombre": "Cemento", "gases": ["CO2"], "indirectas": True, "de_minimis": True,
        "codigos_nc": "2507 00 80, 2523 10 00, 2523 21 00, 2523 29 00, 2523 30 00, 2523 90 00",
    },
    "electricidad": {
        "nombre": "Electricidad", "gases": ["CO2"], "indirectas": None, "de_minimis": False,
        "codigos_nc": "2716 00 00",
    },
    "fertilizantes": {
        "nombre": "Fertilizantes", "gases": ["CO2", "N2O"], "indirectas": True, "de_minimis": True,
        "codigos_nc": "2808 00 00, 2814, 2834 21 00, 3102, 3105 (excepto 3105 60 00)",
    },
    "hierro_acero": {
        "nombre": "Hierro y acero", "gases": ["CO2"], "indirectas": False, "de_minimis": True,
        "codigos_nc": "Capitulo 72 y determinadas partidas del capitulo 73",
    },
    "aluminio": {
        "nombre": "Aluminio", "gases": ["CO2", "PFC"], "indirectas": False, "de_minimis": True,
        "codigos_nc": "Capitulo 76 (7601, 7603 a 7608, 7609 00 00 y determinados productos)",
    },
    "hidrogeno": {
        "nombre": "Hidrogeno", "gases": ["CO2"], "indirectas": False, "de_minimis": False,
        "codigos_nc": "2804 10 00",
    },
}

ALIAS_SECTORES_CBAM = {
    "cemento": "cemento", "clinker": "cemento", "clinkeres": "cemento", "cementoyclinker": "cemento",
    "electricidad": "electricidad", "energiaelectrica": "electricidad",
    "fertilizantes": "fertilizantes", "fertilizante": "fertilizantes", "abonos": "fertilizantes",
    "urea": "fertilizantes", "amoniaco": "fertilizantes", "nitratos": "fertilizantes",
    "hierroacero": "hierro_acero", "hierroyacero": "hierro_acero", "acero": "hierro_acero",
    "hierro": "hierro_acero", "siderurgia": "hierro_acero", "aceroyhierro": "hierro_acero",
    "aluminio": "aluminio", "hidrogeno": "hidrogeno",
}

# Art. 10 bis, ap. 1 bis, de la Directiva 2003/87/CE (via art. 31 del Reg. (UE) 2023/956).
# Es la asignacion gratuita que todavia reciben las instalaciones europeas: cuanto mas
# baja, mas paga el importador.
FACTOR_CBAM = {
    2026: 0.975, 2027: 0.95, 2028: 0.90, 2029: 0.775, 2030: 0.515,
    2031: 0.39, 2032: 0.265, 2033: 0.14, 2034: 0.0,
}
PRIMER_ANIO_CBAM_DEFINITIVO = 2026
INICIO_PERIODO_TRANSITORIO_CBAM = 2023

# Art. 2 bis introducido por el Reglamento (UE) 2025/2083, con remision al Anexo VII, punto 1.
UMBRAL_MASA_CBAM_TONELADAS = 50.0

CALENDARIO_CBAM = {
    "periodo_transitorio": "1 de octubre de 2023 al 31 de diciembre de 2025: solo informacion, sin pagar.",
    "periodo_definitivo": "Desde el 1 de enero de 2026.",
    "primera_declaracion": "30 de septiembre de 2027, referida al año 2026 (art. 6, ap. 1).",
    "venta_de_certificados": "Desde el 1 de febrero de 2027 (art. 20, ap. 1).",
    "entrega_de_certificados": "Antes del 30 de septiembre de cada año (art. 22, ap. 1).",
    "precio_del_certificado": ("En 2026 es la media trimestral del precio de subasta del derecho del RCDE UE; "
                               "desde 2027, la media semanal."),
}


def sector_cbam(nombre):
    """Devuelve la ficha del sector CBAM, aceptando como lo escriba una persona."""
    clave = ALIAS_SECTORES_CBAM.get(_clave(nombre))
    if not clave:
        raise Problema(
            "«%s» no es uno de los sectores que cubre el CBAM." % (nombre if nombre else "(vacio)"),
            ("El CBAM solo cubre cemento, electricidad, fertilizantes, hierro y acero, aluminio e "
             "hidrogeno. La fruta, el vino, la harina de pescado, la celulosa y el cobre quedan fuera."),
            {"sectores": sorted(SECTORES_CBAM)},
        )
    return dict(SECTORES_CBAM[clave], clave=clave)


def factor_cbam(anio):
    """Factor CBAM del año (art. 10 bis, ap. 1 bis, de la Directiva 2003/87/CE).

    Devuelve (factor, porcentaje_exigible). El factor es la asignacion gratuita que
    subsiste; lo exigible al importador es 1 menos ese factor (art. 31 del Reg. 2023/956).
    """
    anio = _anio(anio)
    if anio < INICIO_PERIODO_TRANSITORIO_CBAM:
        raise Problema(
            "En %d el CBAM todavia no existia." % anio,
            "El mecanismo parte con el periodo transitorio en octubre de 2023 y cobra desde 2026.",
        )
    if anio < PRIMER_ANIO_CBAM_DEFINITIVO:
        return 1.0, 0.0
    if anio >= 2034:
        return 0.0, 1.0
    factor = FACTOR_CBAM[anio]
    return factor, round(1.0 - factor, 6)


def cbam_umbral_masa(masa_neta_anual_toneladas, sector=None):
    """Umbral de exencion por masa (art. 2 bis del Reg. (UE) 2023/956, Anexo VII, punto 1).

    Son 50 toneladas de masa neta acumuladas por IMPORTADOR y año natural, no por
    envio ni por exportador. Electricidad e hidrogeno no tienen umbral de minimis.
    """
    masa = _numero(masa_neta_anual_toneladas, "la masa neta importada en el año", minimo=0)
    ficha = sector_cbam(sector) if sector else None
    aplica_umbral = True if ficha is None else bool(ficha["de_minimis"])
    if not aplica_umbral:
        return {
            "exento": False,
            "umbral_toneladas": None,
            "masa_toneladas": masa,
            "motivo": ("La %s no tiene umbral de minimis: entra al CBAM desde el primer kilo."
                       % (ficha["nombre"].lower() if ficha else "mercancia")),
            "articulo": "Art. 2 bis del Reglamento (UE) 2023/956, introducido por el Reglamento (UE) 2025/2083",
        }
    exento = masa <= UMBRAL_MASA_CBAM_TONELADAS
    return {
        "exento": exento,
        "umbral_toneladas": UMBRAL_MASA_CBAM_TONELADAS,
        "masa_toneladas": masa,
        "motivo": (("El importador acumula %s t en el año, que no supera las 50 t: queda exento." % masa)
                   if exento else
                   ("El importador acumula %s t en el año y supera las 50 t: todas sus importaciones "
                    "entran al regimen." % masa)),
        "advertencia": ("El umbral es del importador europeo, no tuyo. Si el importa lo mismo de varios "
                        "proveedores, lo supera facil y entonces te pedira los datos igual."),
        "articulo": "Art. 2 bis del Reglamento (UE) 2023/956, introducido por el Reglamento (UE) 2025/2083",
    }


def cbam_emisiones_incorporadas(sector, cantidad_toneladas, see=None, emisiones_directas=None,
                                emisiones_indirectas=None, nivel_actividad=None, precursores=None):
    """Emisiones incorporadas de un envio (Anexo IV del Reglamento (UE) 2023/956).

    Mercancias simples (Anexo IV, punto 2):

        SEE_g    = AttrEm_g / AL_g
        AttrEm_g = DirEm + IndirEm

    Mercancias complejas (Anexo IV, punto 3):

        SEE_g       = (AttrEm_g + EE_InpMat) / AL_g
        EE_InpMat   = suma de (M_i x SEE_i) de cada precursor i

    Donde SEE_g son las emisiones especificas incorporadas (t CO2e por tonelada de
    mercancia), AL_g el nivel de actividad (toneladas producidas en el periodo) y
    M_i la masa de cada precursor.

    Que emisiones se computan lo define el Anexo II del mismo reglamento: hierro y
    acero, aluminio e hidrogeno solo computan emisiones DIRECTAS; cemento y
    fertilizantes computan DIRECTAS e INDIRECTAS (las de la electricidad consumida).

    Se puede entregar directamente el SEE verificado de la instalacion, o los datos
    brutos (emisiones del periodo y toneladas producidas) para que el motor lo calcule.

    Los valores por defecto del periodo definitivo NO estan verificados: si no hay
    datos de la instalacion, el motor no inventa un numero.
    """
    ficha = sector_cbam(sector)
    cantidad = _numero(cantidad_toneladas, "la cantidad de mercancia del envio, en toneladas", minimo=0)
    if cantidad <= 0:
        raise Problema("La cantidad del envio tiene que ser mayor que cero.",
                       "Dime cuantas toneladas de %s se exportan." % ficha["nombre"].lower())

    if ficha["indirectas"] is None:
        raise Problema(
            "Para la %s el calculo de emisiones incorporadas tiene reglas propias que no estan "
            "confirmadas en la investigacion del proyecto." % ficha["nombre"].lower(),
            "No voy a inventar el metodo. Pidele el calculo al importador europeo o a su verificador.",
            {"pendiente": PENDIENTES_DE_VERIFICAR["cbam_valores_por_defecto"]},
        )

    advertencias = []
    supuestos = []
    directas_por_t = None
    indirectas_por_t = None
    precursores_por_t = 0.0
    detalle_precursores = []

    if see not in (None, "", True, False):
        see_valor = _numero(see, "las emisiones especificas incorporadas (t CO2e por tonelada)", minimo=0)
        origen = "SEE entregado por la instalacion productora"
        supuestos.append("Se usa el SEE que entregaste tal cual: el motor no lo recalcula ni lo verifica.")
        if ficha["indirectas"]:
            supuestos.append("Para %s el SEE debe incluir las emisiones directas y las indirectas "
                             "(Anexo II del Reglamento (UE) 2023/956)." % ficha["nombre"].lower())
        else:
            supuestos.append("Para %s el SEE debe incluir solo las emisiones directas "
                             "(Anexo II del Reglamento (UE) 2023/956)." % ficha["nombre"].lower())
    else:
        nivel = _numero(nivel_actividad, "el nivel de actividad de la instalacion (toneladas producidas "
                                         "en el periodo de referencia)", minimo=0)
        if nivel <= 0:
            raise Problema(
                "El nivel de actividad de la instalacion tiene que ser mayor que cero.",
                "Es cuantas toneladas produjo la planta en el periodo con el que calculaste las emisiones.",
            )
        directas = _numero(emisiones_directas, "las emisiones directas del proceso, en t CO2e", minimo=0)
        if ficha["indirectas"]:
            if emisiones_indirectas in (None, "", True, False):
                raise Problema(
                    "Para %s hay que declarar tambien las emisiones indirectas y no me las diste."
                    % ficha["nombre"].lower(),
                    ("Son las emisiones de la electricidad que consume el proceso. No las puedo estimar: "
                     "los valores por defecto del periodo definitivo no estan confirmados. Pidelas a la "
                     "planta o calculalas con el consumo electrico y el factor de la red."),
                    {"pendiente": PENDIENTES_DE_VERIFICAR["cbam_valores_por_defecto"]},
                )
            indirectas = _numero(emisiones_indirectas, "las emisiones indirectas, en t CO2e", minimo=0)
        else:
            indirectas = 0.0
            if _numero(emisiones_indirectas, "las emisiones indirectas", obligatorio=False, minimo=0):
                advertencias.append(
                    "Para %s el Anexo II del Reglamento (UE) 2023/956 computa solo emisiones directas: "
                    "las indirectas que indicaste quedan fuera del calculo." % ficha["nombre"].lower())

        for entrada in (precursores or []):
            if isinstance(entrada, dict):
                masa = entrada.get("masa", entrada.get("toneladas"))
                see_i = entrada.get("see", entrada.get("emisiones"))
                nombre_i = entrada.get("nombre", "precursor")
            else:
                masa, see_i = entrada[0], entrada[1]
                nombre_i = entrada[2] if len(entrada) > 2 else "precursor"
            masa = _numero(masa, "la masa del precursor «%s», en toneladas" % nombre_i, minimo=0)
            see_i = _numero(see_i, "el SEE del precursor «%s», en t CO2e por tonelada" % nombre_i, minimo=0)
            detalle_precursores.append({"nombre": nombre_i, "masa_toneladas": masa,
                                        "see_t_co2e_por_t": see_i, "aporte_t_co2e": masa * see_i})

        atribuidas = directas + indirectas
        aporte_precursores = sum(p["aporte_t_co2e"] for p in detalle_precursores)
        see_valor = (atribuidas + aporte_precursores) / nivel
        directas_por_t = directas / nivel
        indirectas_por_t = indirectas / nivel
        precursores_por_t = aporte_precursores / nivel
        origen = ("Calculado con los datos de la instalacion (mercancia %s)"
                  % ("compleja" if detalle_precursores else "simple"))
        supuestos.append("AttrEm = emisiones directas + indirectas, dividido por el nivel de actividad "
                         "(Anexo IV, puntos 2 y 3 del Reglamento (UE) 2023/956).")

    return {
        "sector": ficha["clave"],
        "sector_nombre": ficha["nombre"],
        "gases_cubiertos": ficha["gases"],
        "codigos_nc": ficha["codigos_nc"],
        "computa_indirectas": bool(ficha["indirectas"]),
        "tipo_de_mercancia": "compleja" if detalle_precursores else "simple",
        "cantidad_toneladas": cantidad,
        "see_t_co2e_por_t": see_valor,
        "emisiones_incorporadas_t_co2e": cantidad * see_valor,
        "componentes_por_tonelada": {
            "directas": directas_por_t,
            "indirectas": indirectas_por_t,
            "precursores": precursores_por_t if detalle_precursores else None,
        },
        "precursores": detalle_precursores,
        "origen_del_dato": origen,
        "articulos": ["Anexo IV, puntos 1 a 3, del Reglamento (UE) 2023/956",
                      "Anexo II del Reglamento (UE) 2023/956 (emisiones directas e indirectas)"],
        "supuestos": supuestos,
        "advertencias": advertencias,
        "fuente": FUENTE,
    }


def cbam_costo_estimado(emisiones_incorporadas, anio, precio_certificado_eur,
                        deduccion_certificados=None, precio_carbono_origen_eur_t=None,
                        cantidad_toneladas=None, masa_neta_anual_importador=None, sector=None):
    """Certificados a entregar y costo del CBAM (arts. 9, 22 y 31 del Reg. (UE) 2023/956).

        Certificados = Emisiones_incorporadas x (1 - FactorCBAM_año) - Deduccion_origen
        Costo        = Certificados x Precio_del_certificado

    El termino (1 - FactorCBAM_año) traduce el art. 31: la obligacion se ajusta para
    reflejar la asignacion gratuita que todavia reciben las instalaciones europeas
    (art. 10 bis, ap. 1 bis, de la Directiva 2003/87/CE).

    La deduccion del art. 9 (precio del carbono ya pagado en el pais de origen) se
    remite a un acto de ejecucion que la investigacion NO pudo verificar. Por eso
    aqui es un parametro abierto: o entregas directamente cuantos certificados
    descuenta el importador, o entregas el precio pagado por tonelada y el motor
    hace una estimacion que queda marcada como no confirmada.

    El precio del certificado nunca esta en el codigo: es de mercado y lo entregas tu.
    """
    emisiones = _numero(emisiones_incorporadas, "las emisiones incorporadas del envio, en t CO2e", minimo=0)
    anio = _anio(anio)
    factor, exigible = factor_cbam(anio)
    precio = _numero(precio_certificado_eur, "el precio del certificado CBAM, en euros por tonelada",
                     minimo=0)

    advertencias = [AVISO_PRECIOS]
    supuestos = []
    exencion = None

    if masa_neta_anual_importador not in (None, "", True, False):
        exencion = cbam_umbral_masa(masa_neta_anual_importador, sector)
        if exencion["exento"]:
            advertencias.append(exencion["motivo"])

    if anio < PRIMER_ANIO_CBAM_DEFINITIVO:
        advertencias.append("En %d el CBAM estaba en periodo transitorio: solo habia que informar, no se "
                            "compraban certificados. Por eso el costo es cero." % anio)

    certificados_teoricos = emisiones * exigible
    deduccion = 0.0
    deduccion_estimada = False

    if deduccion_certificados not in (None, "", True, False):
        deduccion = _numero(deduccion_certificados, "la deduccion en certificados", minimo=0)
        supuestos.append("La deduccion por carbono pagado en origen la entregaste tu, en certificados.")
    elif precio_carbono_origen_eur_t not in (None, "", True, False):
        precio_origen = _numero(precio_carbono_origen_eur_t,
                                "el precio del carbono pagado en el pais de origen, en euros por tonelada",
                                minimo=0)
        if precio > 0:
            deduccion = (emisiones * precio_origen) / precio
            deduccion_estimada = True
            supuestos.append(
                "Estimacion del descuento del art. 9: el carbono pagado en origen (%s EUR/t sobre %s t CO2e) "
                "se convierte a certificados dividiendolo por el precio del certificado. NO es la formula "
                "oficial." % (precio_origen, emisiones))
            advertencias.append(PENDIENTES_DE_VERIFICAR["cbam_deduccion_origen"]["consecuencia"])

    if deduccion > certificados_teoricos:
        advertencias.append("El descuento por carbono pagado en origen supera la obligacion del año: se "
                            "topa en cero certificados, no genera saldo a favor.")
        deduccion = certificados_teoricos

    certificados = max(0.0, certificados_teoricos - deduccion)
    costo = certificados * precio
    if exencion and exencion["exento"]:
        certificados = 0.0
        costo = 0.0

    cantidad = _numero(cantidad_toneladas, "la cantidad del envio", obligatorio=False, minimo=0)
    return {
        "anio": anio,
        "factor_cbam": factor,
        "porcentaje_exigible": exigible,
        "emisiones_incorporadas_t_co2e": emisiones,
        "certificados_teoricos": certificados_teoricos,
        "deduccion_certificados": deduccion,
        "deduccion_es_estimacion": deduccion_estimada,
        "certificados_a_entregar": certificados,
        "precio_certificado_eur": precio,
        "costo_eur": costo,
        "costo_por_tonelada_eur": (costo / cantidad) if cantidad else None,
        "exencion_por_masa": exencion,
        "calendario": CALENDARIO_CBAM,
        "articulos": ["Art. 31 del Reglamento (UE) 2023/956 (ajuste por asignacion gratuita)",
                      "Art. 10 bis, ap. 1 bis, de la Directiva 2003/87/CE (factor CBAM por año)",
                      "Art. 9 del Reglamento (UE) 2023/956 (carbono pagado en el pais de origen)",
                      "Art. 22 del Reglamento (UE) 2023/956 (entrega de certificados)"],
        "supuestos": supuestos,
        "advertencias": advertencias,
        "no_verificado": pendientes("cbam_deduccion_origen", "cbam_valores_por_defecto"),
        "fuente": FUENTE,
    }


def cbam_curva(emisiones_incorporadas, precio_certificado_eur, cantidad_toneladas=None,
               desde=2026, hasta=2034):
    """El mismo envio año a año, para ver como crece el costo hasta 2034."""
    filas = []
    for anio in range(_anio(desde), _anio(hasta) + 1):
        calculo = cbam_costo_estimado(emisiones_incorporadas, anio, precio_certificado_eur,
                                      cantidad_toneladas=cantidad_toneladas)
        filas.append({
            "anio": anio,
            "factor_cbam": calculo["factor_cbam"],
            "porcentaje_exigible": calculo["porcentaje_exigible"],
            "certificados_a_entregar": calculo["certificados_a_entregar"],
            "costo_eur": calculo["costo_eur"],
            "costo_por_tonelada_eur": calculo["costo_por_tonelada_eur"],
        })
    return filas


# --------------------------------------------------------------------------
# FuelEU Maritime — Reglamento (UE) 2023/1805
# --------------------------------------------------------------------------

# Anexo II del Reglamento (UE) 2023/1805, transcrito del DO L 234 de 22-09-2023.
# lcv en MJ/g; wtt en gCO2e/MJ; cf_* en g del gas por g de combustible;
# c_slip en % de la masa de combustible que escapa sin quemar.
# None significa que la investigacion no transcribio ese valor: hay que pedirlo.
COMBUSTIBLES_FUELEU = {
    "HFO": {"nombre": "Fueloil pesado (HFO)", "via": "ISO 8217 grados RME a RMK",
            "lcv": 0.0405, "wtt": 13.5, "consumidor": "Todos los motores de combustion interna",
            "cf_co2": 3.114, "cf_ch4": 0.00005, "cf_n2o": 0.00018, "c_slip": 0.0},
    "LFO": {"nombre": "Fueloil ligero (LFO)", "via": "ISO 8217 grados RMA a RMD",
            "lcv": 0.041, "wtt": 13.2, "consumidor": "Todos los motores de combustion interna",
            "cf_co2": 3.151, "cf_ch4": 0.00005, "cf_n2o": 0.00018, "c_slip": 0.0},
    "MDO": {"nombre": "Diesel marino / gasoil marino (MDO/MGO)", "via": "ISO 8217 grados DMX a DMB",
            "lcv": 0.0427, "wtt": 14.4, "consumidor": "Todos los motores de combustion interna",
            "cf_co2": 3.206, "cf_ch4": 0.00005, "cf_n2o": 0.00018, "c_slip": 0.0},
    "GNL_OTTO_MEDIA": {"nombre": "Gas natural licuado (GNL)", "via": "-",
                       "lcv": 0.0491, "wtt": 18.5, "consumidor": "LNG Otto (dual fuel, media velocidad)",
                       "cf_co2": 2.750, "cf_ch4": 0.0, "cf_n2o": 0.00011, "c_slip": 3.1},
    "GNL_OTTO_BAJA": {"nombre": "Gas natural licuado (GNL)", "via": "-",
                      "lcv": 0.0491, "wtt": 18.5, "consumidor": "LNG Otto (dual fuel, baja velocidad)",
                      "cf_co2": 2.750, "cf_ch4": 0.0, "cf_n2o": 0.00011, "c_slip": 1.7},
    "GNL_DIESEL_BAJA": {"nombre": "Gas natural licuado (GNL)", "via": "-",
                        "lcv": 0.0491, "wtt": 18.5, "consumidor": "LNG Diesel (dual fuel, baja velocidad)",
                        "cf_co2": 2.750, "cf_ch4": 0.0, "cf_n2o": 0.00011, "c_slip": 0.2},
    "GNL_LBSI": {"nombre": "Gas natural licuado (GNL)", "via": "-",
                 "lcv": 0.0491, "wtt": 18.5, "consumidor": "LBSI",
                 "cf_co2": 2.750, "cf_ch4": 0.0, "cf_n2o": 0.00011, "c_slip": 2.6},
    "GLP_BUTANO": {"nombre": "Gas licuado de petroleo (butano)", "via": "-",
                   "lcv": 0.046, "wtt": 7.8, "consumidor": "Todos los motores de combustion interna",
                   "cf_co2": 3.030, "cf_ch4": None, "cf_n2o": None, "c_slip": 0.0},
    "GLP_PROPANO": {"nombre": "Gas licuado de petroleo (propano)", "via": "-",
                    "lcv": 0.046, "wtt": 7.8, "consumidor": "Todos los motores de combustion interna",
                    "cf_co2": 3.000, "cf_ch4": None, "cf_n2o": None, "c_slip": 0.0},
    "METANOL_GN": {"nombre": "Metanol de gas natural", "via": "Gas natural",
                   "lcv": 0.0199, "wtt": 31.3, "consumidor": "Todos los motores de combustion interna",
                   "cf_co2": 1.375, "cf_ch4": None, "cf_n2o": None, "c_slip": 0.0},
    "H2_GN": {"nombre": "Hidrogeno de gas natural", "via": "Gas natural",
              "lcv": 0.12, "wtt": 132.0, "consumidor": "-",
              "cf_co2": None, "cf_ch4": None, "cf_n2o": None, "c_slip": 0.0},
    "NH3_GN": {"nombre": "Amoniaco de gas natural", "via": "Gas natural",
               "lcv": 0.0186, "wtt": 121.0, "consumidor": "-",
               "cf_co2": None, "cf_ch4": None, "cf_n2o": None, "c_slip": 0.0},
}

ALIAS_COMBUSTIBLES = {
    "hfo": "HFO", "fueloil": "HFO", "fueloilpesado": "HFO", "ifo": "HFO", "hsfo": "HFO",
    "lfo": "LFO", "fueloilligero": "LFO",
    "mdo": "MDO", "mgo": "MDO", "mdomgo": "MDO", "dieselmarino": "MDO", "gasoilmarino": "MDO",
    "gnl": "GNL_OTTO_MEDIA", "lng": "GNL_OTTO_MEDIA",
    "gnlottomedia": "GNL_OTTO_MEDIA", "lngottomedia": "GNL_OTTO_MEDIA",
    "gnlottobaja": "GNL_OTTO_BAJA", "lngottobaja": "GNL_OTTO_BAJA",
    "gnldieselbaja": "GNL_DIESEL_BAJA", "lngdieselbaja": "GNL_DIESEL_BAJA",
    "gnllbsi": "GNL_LBSI", "lbsi": "GNL_LBSI",
    "glpbutano": "GLP_BUTANO", "butano": "GLP_BUTANO",
    "glppropano": "GLP_PROPANO", "propano": "GLP_PROPANO", "glp": "GLP_PROPANO",
    "metanol": "METANOL_GN", "metanolgn": "METANOL_GN", "metanoldegasnatural": "METANOL_GN",
    "h2": "H2_GN", "hidrogeno": "H2_GN", "h2gn": "H2_GN",
    "nh3": "NH3_GN", "amoniaco": "NH3_GN", "nh3gn": "NH3_GN",
}

# Art. 4, ap. 2, del Reglamento (UE) 2023/1805.
REFERENCIA_FUELEU = 91.16              # gCO2e/MJ, media de la flota en 2020
REDUCCIONES_FUELEU = {2025: 0.02, 2030: 0.06, 2035: 0.145, 2040: 0.31, 2045: 0.62, 2050: 0.80}
PRIMER_ANIO_FUELEU = 2025

# Anexo IV, parte B, del Reglamento (UE) 2023/1805.
MJ_POR_TONELADA_VLSFO = 41000.0        # "1 metric ton of VLSFO that is equivalent to 41 000 MJ"
EUR_POR_TONELADA_VLSFO = 2400.0        # "amount to be paid in EUR per equivalent metric ton of VLSFO"

# Art. 5 y ecuacion (1) del Anexo I: premio de 2 para combustibles de origen no biologico.
FACTOR_PREMIO_RFNBO = 2.0
RFNBO_DESDE, RFNBO_HASTA = 2025, 2033

# Art. 2 del Reglamento (UE) 2023/1805.
COBERTURA_ENERGIA_FUELEU = {
    "en_puerto": 1.00,
    "intra_ue": 1.00,
    "region_ultraperiferica": 0.50,
    "tercer_pais_ue": 0.50,
    "ue_tercer_pais": 0.50,
}


def combustible_fueleu(nombre):
    """Ficha del combustible en el Anexo II del Reglamento (UE) 2023/1805."""
    clave = ALIAS_COMBUSTIBLES.get(_clave(nombre))
    if not clave:
        raise Problema(
            "No tengo los factores del combustible «%s»." % (nombre if nombre else "(vacio)"),
            ("Combustibles con factores verificados del Anexo II: HFO, LFO, MDO/MGO, GNL (segun el tipo de "
             "motor), GLP butano, GLP propano, metanol y amoniaco de gas natural, e hidrogeno de gas natural. "
             "Si el buque usa otro, pide el factor a la naviera."),
            {"combustibles": sorted(COMBUSTIBLES_FUELEU)},
        )
    return dict(COMBUSTIBLES_FUELEU[clave], clave=clave)


def factor_co2e_ttw(combustible, gwp=None):
    """Factor CO2-equivalente del pozo al propulsor (ecuacion 2 del Anexo I, Reg. (UE) 2023/1805).

        CO2eq_TtW = Cf_CO2 x GWP_CO2 + Cf_CH4 x GWP_CH4 + Cf_N2O x GWP_N2O

    Los GWP a 100 años se remiten al Anexo V, parte C, punto 4, de la Directiva (UE)
    2018/2001. La investigacion NO leyo esa disposicion, asi que los valores hay que
    entregarlos; el motor no los supone.
    """
    ficha = combustible_fueleu(combustible)
    gwp = gwp or {}
    faltan = [gas for gas in ("ch4", "n2o") if _numero(gwp.get(gas), gas, obligatorio=False) is None]
    if faltan:
        raise Problema(
            "Para incluir el metano y el oxido nitroso necesito sus valores de potencial de calentamiento "
            "global (GWP) y no los tengo confirmados.",
            ("Los define el Anexo V de la Directiva (UE) 2018/2001 y la investigacion del proyecto no los "
             "pudo leer. Pidelos a la naviera o a su verificador y pasalos como dato; asi queda registrado "
             "que valor se uso."),
            {"faltan": faltan, "pendiente": PENDIENTES_DE_VERIFICAR["gwp_fueleu"]},
        )
    if ficha["cf_co2"] is None:
        raise Problema(
            "No tengo el factor de CO2 del combustible «%s» en la tabla verificada." % ficha["nombre"],
            "Pide a la naviera el factor del Anexo II para ese combustible y su tipo de motor.",
        )
    gwp_co2 = _numero(gwp.get("co2", 1.0), "el GWP del CO2", minimo=0)
    gwp_ch4 = _numero(gwp.get("ch4"), "el GWP del metano", minimo=0)
    gwp_n2o = _numero(gwp.get("n2o"), "el GWP del oxido nitroso", minimo=0)
    cf_ch4 = ficha["cf_ch4"] if ficha["cf_ch4"] is not None else 0.0
    cf_n2o = ficha["cf_n2o"] if ficha["cf_n2o"] is not None else 0.0
    return ficha["cf_co2"] * gwp_co2 + cf_ch4 * gwp_ch4 + cf_n2o * gwp_n2o


def fueleu_intensidad_objetivo(anio):
    """Limite de intensidad de GEI del año (art. 4, ap. 2, del Reg. (UE) 2023/1805).

        GHGIE_target = 91,16 gCO2e/MJ x (1 - reduccion del periodo)

    Reducciones: 2 % desde 2025, 6 % desde 2030, 14,5 % desde 2035, 31 % desde 2040,
    62 % desde 2045 y 80 % desde 2050.
    """
    anio = _anio(anio)
    if anio < PRIMER_ANIO_FUELEU:
        raise Problema(
            "FuelEU Maritime empieza a medir en 2025; %d queda fuera." % anio,
            "El primer periodo de referencia es el año natural 2025.",
        )
    periodo = max(a for a in REDUCCIONES_FUELEU if a <= anio)
    reduccion = REDUCCIONES_FUELEU[periodo]
    return {
        "anio": anio,
        "periodo_desde": periodo,
        "referencia_gco2e_mj": REFERENCIA_FUELEU,
        "reduccion": reduccion,
        "objetivo_gco2e_mj": REFERENCIA_FUELEU * (1.0 - reduccion),
        "articulo": "Art. 4, ap. 2, del Reglamento (UE) 2023/1805",
    }


def fueleu_intensidad_real(consumos, gwp=None, energia_ops_mj=0.0, co2eq_ops=None, f_wind=1.0, anio=None):
    """Intensidad de GEI real de la energia usada a bordo (Anexo I, ecuacion 1).

        GHGIE = f_wind x (WtT + TtW)

        WtT = suma(M_i x CO2eq_WtT,i x LCV_i) + suma(E_k x CO2eq_elec,k)
              --------------------------------------------------------
              suma(M_i x LCV_i x RWD_i) + suma(E_k)

        TtW = suma(M_i x [(1 - C_slip/100) x CO2eq_TtW,i + (C_slip/100) x GWP_CH4])
              -----------------------------------------------------------------
              suma(M_i x LCV_i x RWD_i) + suma(E_k)

    RWD_i vale 2 para combustibles de origen no biologico entre el 1-1-2025 y el
    31-12-2033 (art. 5), y 1 en los demas casos. Para el combustible que escapa sin
    quemar (methane slip) el Anexo I fija Csf_CO2 = 0, Csf_N2O = 0 y Csf_CH4 = 1.
    """
    if not consumos:
        raise Problema("No me dijiste que combustible consumio el buque.",
                       "Necesito al menos el tipo de combustible y las toneladas consumidas.")
    anio = _anio(anio) if anio not in (None, "", True, False) else None
    numerador_wtt = 0.0
    numerador_ttw = 0.0
    denominador = 0.0
    energia_total = 0.0
    detalle = []
    advertencias = []
    gwp = gwp or {}
    gwp_ch4 = _numero(gwp.get("ch4"), "el GWP del metano", obligatorio=False, minimo=0)

    for entrada in consumos:
        if not isinstance(entrada, dict):
            entrada = {"combustible": entrada[0], "toneladas": entrada[1]}
        ficha = combustible_fueleu(entrada.get("combustible"))
        toneladas = _numero(entrada.get("toneladas", entrada.get("masa_t")),
                            "las toneladas de %s consumidas" % ficha["nombre"], minimo=0)
        masa_g = toneladas * 1000000.0
        energia = masa_g * ficha["lcv"]
        rwd = 1.0
        if entrada.get("rfnbo"):
            if anio is None or RFNBO_DESDE <= anio <= RFNBO_HASTA:
                rwd = FACTOR_PREMIO_RFNBO
        co2eq_ttw = factor_co2e_ttw(ficha["clave"], gwp)
        deslizado = (ficha["c_slip"] or 0.0) / 100.0
        if deslizado and gwp_ch4 is None:
            raise Problema(
                "Ese motor de GNL pierde metano sin quemar y necesito el GWP del metano para contarlo.",
                "Pidele el valor a la naviera: sin el, el resultado subestimaria las emisiones.",
                {"pendiente": PENDIENTES_DE_VERIFICAR["gwp_fueleu"]},
            )
        if ficha["cf_ch4"] is None or ficha["cf_n2o"] is None:
            advertencias.append(
                "De %s la investigacion solo transcribio el factor de CO2: el metano y el oxido nitroso "
                "quedan en cero y el resultado puede estar por debajo del real. Pide los factores a la "
                "naviera." % ficha["nombre"])
        aporte_ttw = masa_g * ((1.0 - deslizado) * co2eq_ttw + deslizado * (gwp_ch4 or 0.0))
        numerador_wtt += masa_g * ficha["wtt"] * ficha["lcv"]
        numerador_ttw += aporte_ttw
        denominador += energia * rwd
        energia_total += energia
        detalle.append({
            "combustible": ficha["clave"], "nombre": ficha["nombre"], "consumidor": ficha["consumidor"],
            "toneladas": toneladas, "energia_mj": energia, "lcv_mj_g": ficha["lcv"],
            "wtt_gco2e_mj": ficha["wtt"], "co2eq_ttw_g_g": co2eq_ttw,
            "methane_slip_pct": ficha["c_slip"], "factor_premio": rwd,
        })

    ops = _numero(energia_ops_mj, "la energia electrica recibida en puerto (OPS), en MJ",
                  obligatorio=False, minimo=0) or 0.0
    if ops:
        factor_ops = _numero(co2eq_ops, "el factor de emision de la electricidad de puerto, en gCO2e/MJ",
                             minimo=0)
        numerador_wtt += ops * factor_ops
        denominador += ops
        energia_total += ops

    if denominador <= 0:
        raise Problema("El consumo declarado da energia cero.",
                       "Revisa las toneladas de combustible: no pueden ser todas cero.")

    viento = _numero(f_wind, "el factor de propulsion asistida por viento", obligatorio=False, minimo=0)
    viento = 1.0 if viento is None else viento
    wtt = numerador_wtt / denominador
    ttw = numerador_ttw / denominador
    return {
        "ghgie_gco2e_mj": viento * (wtt + ttw),
        "wtt_gco2e_mj": wtt,
        "ttw_gco2e_mj": ttw,
        "f_wind": viento,
        "energia_total_mj": energia_total,
        "energia_ops_mj": ops,
        "combustibles": detalle,
        "articulos": ["Anexo I, ecuaciones 1 y 2, del Reglamento (UE) 2023/1805",
                      "Anexo II del Reglamento (UE) 2023/1805 (factores por defecto)"],
        "advertencias": advertencias,
        "no_verificado": pendientes("gwp_fueleu"),
    }


def fueleu_balance(anio, consumos=None, ghgie_actual=None, energia_total_mj=None, energia_ops_mj=0.0,
                   co2eq_ops=None, f_wind=1.0, gwp=None, periodos_consecutivos=1):
    """Balance de cumplimiento y penalizacion FuelEU (Anexo IV del Reg. (UE) 2023/1805).

    Parte A — balance:

        Balance [gCO2eq] = (GHGIE_target - GHGIE_actual) x [ suma(M_i x LCV_i) + suma(E_k) ]

    Resultado positivo es superavit; negativo es deficit y genera penalizacion.

    Parte B — penalizacion:

        Penalizacion [EUR] = ( |Balance| / (GHGIE_actual x 41 000) ) x 2 400

    donde 41 000 MJ es el equivalente energetico de una tonelada de VLSFO y 2 400 EUR
    es el importe por tonelada equivalente de VLSFO, ambos definidos en el Anexo IV.

    Si el buque tiene deficit en periodos consecutivos, el importe se multiplica por
    1 + (n - 1)/10, donde n son los periodos consecutivos (art. 23, ap. 2).

    Puedes entregar la intensidad real ya calculada (ghgie_actual) o el consumo de
    combustible mas los valores de GWP para que el motor la calcule.
    """
    objetivo = fueleu_intensidad_objetivo(anio)
    advertencias = []
    detalle_intensidad = None

    if ghgie_actual not in (None, "", True, False):
        actual = _numero(ghgie_actual, "la intensidad real de gases de efecto invernadero (gCO2e/MJ)",
                         minimo=0)
        energia = _numero(energia_total_mj, "la energia total usada a bordo dentro del ambito, en MJ",
                          minimo=0)
        advertencias.append("Se usa la intensidad que entregaste; el motor no la recalcula.")
    else:
        detalle_intensidad = fueleu_intensidad_real(consumos, gwp=gwp, energia_ops_mj=energia_ops_mj,
                                                    co2eq_ops=co2eq_ops, f_wind=f_wind, anio=anio)
        actual = detalle_intensidad["ghgie_gco2e_mj"]
        energia = (_numero(energia_total_mj, "la energia total", obligatorio=False, minimo=0)
                   or detalle_intensidad["energia_total_mj"])
        advertencias.extend(detalle_intensidad["advertencias"])

    if actual <= 0:
        raise Problema("La intensidad de gases de efecto invernadero no puede ser cero o negativa.",
                       "Revisa el dato: se mide en gramos de CO2 equivalente por megajoule.")
    if energia <= 0:
        raise Problema("La energia usada a bordo no puede ser cero.",
                       "Necesito los megajoules o las toneladas de combustible del periodo.")

    balance = (objetivo["objetivo_gco2e_mj"] - actual) * energia
    equivalente_vlsfo = abs(balance) / (actual * MJ_POR_TONELADA_VLSFO)
    periodos = int(_numero(periodos_consecutivos, "los periodos consecutivos con deficit",
                           obligatorio=False, minimo=1) or 1)
    multiplicador = 1.0 + (periodos - 1) / 10.0

    if balance < 0:
        estado = "deficit"
        penalizacion = equivalente_vlsfo * EUR_POR_TONELADA_VLSFO * multiplicador
    else:
        estado = "superavit" if balance > 0 else "justo en el limite"
        penalizacion = 0.0
        multiplicador = 1.0
        if balance > 0:
            advertencias.append("Con superavit la compañia puede guardarlo para el periodo siguiente "
                                "(banking, art. 20, ap. 1) o agruparlo con otros buques (pooling, art. 21).")

    return {
        "anio": objetivo["anio"],
        "objetivo_gco2e_mj": objetivo["objetivo_gco2e_mj"],
        "reduccion_exigida": objetivo["reduccion"],
        "intensidad_real_gco2e_mj": actual,
        "energia_total_mj": energia,
        "balance_gco2e": balance,
        "balance_t_co2e": balance / 1000000.0,
        "estado": estado,
        "equivalente_vlsfo_t": equivalente_vlsfo,
        "periodos_consecutivos": periodos,
        "multiplicador_reincidencia": multiplicador,
        "penalizacion_eur": penalizacion,
        "detalle_intensidad": detalle_intensidad,
        "articulos": ["Anexo IV, parte A, del Reglamento (UE) 2023/1805 (balance)",
                      "Anexo IV, parte B, del Reglamento (UE) 2023/1805 (penalizacion)",
                      "Art. 23, ap. 2, del Reglamento (UE) 2023/1805 (reincidencia)",
                      objetivo["articulo"]],
        "calendario": {
            "primer_periodo": "Año natural 2025.",
            "registro_de_balances": "Antes del 1 de mayo del periodo de verificacion.",
            "pago_de_la_penalizacion": "30 de junio del periodo de verificacion.",
            "documento_de_cumplimiento": "30 de junio; vale 18 meses tras el fin del periodo.",
        },
        "advertencias": advertencias,
        "no_verificado": pendientes("gwp_fueleu"),
        "fuente": FUENTE,
    }


# --------------------------------------------------------------------------
# EU ETS maritimo — Directiva 2003/87/CE tras la Directiva (UE) 2023/959
# --------------------------------------------------------------------------

# Art. 3 octies bis (3ga) de la Directiva 2003/87/CE.
COBERTURA_VIAJE_ETS = {
    "ue_tercer_pais": {"cobertura": 0.50, "descripcion": "Sale de un puerto de la UE y llega a un tercer pais"},
    "tercer_pais_ue": {"cobertura": 0.50, "descripcion": "Sale de un tercer pais y llega a un puerto de la UE"},
    "intra_ue": {"cobertura": 1.00, "descripcion": "Entre dos puertos de la Union Europea"},
    "en_puerto": {"cobertura": 1.00, "descripcion": "Emisiones del buque atracado en un puerto de la UE"},
}

ALIAS_VIAJE_ETS = {
    "uetercerpais": "ue_tercer_pais", "salidadelaue": "ue_tercer_pais", "exportacionue": "ue_tercer_pais",
    "tercerpaisue": "tercer_pais_ue", "llegadaalaue": "tercer_pais_ue", "haciaeuropa": "tercer_pais_ue",
    "chileue": "tercer_pais_ue", "peruue": "tercer_pais_ue", "sudamericaeuropa": "tercer_pais_ue",
    "intraue": "intra_ue", "dentrodelaue": "intra_ue", "europaeuropa": "intra_ue",
    "enpuerto": "en_puerto", "atraque": "en_puerto", "puerto": "en_puerto",
}

# Art. 3 octies ter (3gb) de la Directiva 2003/87/CE.
ENTREGA_ETS_POR_ANIO = {2024: 0.40, 2025: 0.70}
PRIMER_ANIO_ETS_MARITIMO = 2024
ANIO_CH4_N2O_ETS = 2026
UMBRAL_GT_ETS = 5000

MILLAS_TRANSBORDO_ETS = 300
PORCENTAJE_TRANSBORDO_ETS = 0.65


def tipo_viaje_ets(nombre):
    """Cobertura del viaje segun el art. 3 octies bis de la Directiva 2003/87/CE."""
    pedido = _clave(nombre)
    for llave in COBERTURA_VIAJE_ETS:
        if _clave(llave) == pedido:
            return dict(COBERTURA_VIAJE_ETS[llave], clave=llave)
    clave = ALIAS_VIAJE_ETS.get(pedido)
    if clave:
        return dict(COBERTURA_VIAJE_ETS[clave], clave=clave)
    raise Problema(
        "No reconozco el tipo de viaje «%s»." % (nombre if nombre else "(vacio)"),
        ("Usa uno de estos: tercer_pais_ue (de Chile o Peru hacia Europa, se cubre el 50 %), "
         "ue_tercer_pais (50 %), intra_ue (100 %) o en_puerto (100 %)."),
        {"tipos": sorted(COBERTURA_VIAJE_ETS)},
    )


def porcentaje_entrega_ets(anio):
    """Porcentaje de emisiones verificadas que hay que cubrir con derechos (art. 3 octies ter)."""
    anio = _anio(anio)
    if anio < PRIMER_ANIO_ETS_MARITIMO:
        raise Problema(
            "El transporte maritimo entro al mercado de carbono europeo el 1 de enero de 2024; "
            "%d queda fuera." % anio,
            "Si te interesa comparar, el primer año con obligacion es 2024, al 40 %.",
        )
    return ENTREGA_ETS_POR_ANIO.get(anio, 1.0)


def ets_maritimo_obligacion(anio, tipo_viaje="tercer_pais_ue", emisiones_viaje_t=None,
                            consumo_toneladas=None, combustible="HFO", precio_eua_eur=None,
                            teu=None, incluir_ch4_n2o=False, gwp=None):
    """Derechos a entregar y recargo por contenedor del ETS maritimo.

        Emisiones_viaje    = consumo de combustible x factor de emision
        Emisiones_cubiertas = Emisiones_viaje x cobertura del viaje (50 % o 100 %)
        Derechos           = Emisiones_cubiertas x porcentaje del año (40 %, 70 % o 100 %)
        Costo              = Derechos x precio del derecho (EUA)
        Recargo por TEU    = Costo / contenedores transportados

    Cobertura del viaje: art. 3 octies bis de la Directiva 2003/87/CE (50 % en los
    viajes entre un tercer pais y la UE, 100 % dentro de la UE y en puerto).
    Porcentaje por año: art. 3 octies ter (40 % en 2024, 70 % en 2025, 100 % desde 2026).

    El factor de emision del combustible sale del Anexo II del Reglamento (UE)
    2023/1805. Desde 2026 el regimen cubre tambien metano y oxido nitroso: para
    incluirlos hacen falta los valores de GWP, que no estan verificados.

    El obligado es la compañia naviera, no el exportador: este calculo sirve para
    entender y negociar el recargo que aparece en el flete.
    """
    anio = _anio(anio)
    viaje = tipo_viaje_ets(tipo_viaje)
    entrega = porcentaje_entrega_ets(anio)
    advertencias = [AVISO_PRECIOS]
    supuestos = []
    factor_usado = None
    ficha = None

    if emisiones_viaje_t not in (None, "", True, False):
        emisiones = _numero(emisiones_viaje_t, "las emisiones del viaje, en t CO2e", minimo=0)
        supuestos.append("Se usan las emisiones del viaje que entregaste (normalmente las informa la naviera).")
    else:
        ficha = combustible_fueleu(combustible)
        consumo = _numero(consumo_toneladas, "el consumo de combustible del viaje, en toneladas", minimo=0)
        if incluir_ch4_n2o:
            factor_usado = factor_co2e_ttw(ficha["clave"], gwp)
            supuestos.append("Factor CO2 equivalente del %s: %.5f t CO2e por tonelada de combustible, "
                             "con los valores de GWP que entregaste." % (ficha["nombre"], factor_usado))
        else:
            if ficha["cf_co2"] is None:
                raise Problema(
                    "No tengo el factor de CO2 del combustible «%s»." % ficha["nombre"],
                    "Pidele a la naviera las emisiones del viaje ya calculadas.",
                )
            factor_usado = ficha["cf_co2"]
            supuestos.append("Factor de CO2 del %s: %s t CO2 por tonelada de combustible (Anexo II del "
                             "Reglamento (UE) 2023/1805)." % (ficha["nombre"], ficha["cf_co2"]))
        emisiones = consumo * factor_usado

    if anio >= ANIO_CH4_N2O_ETS and not incluir_ch4_n2o:
        advertencias.append(
            "Desde el 1 de enero de 2026 el mercado de carbono europeo cubre tambien metano y oxido "
            "nitroso. Este calculo solo incluye CO2, asi que queda algo por debajo del real (en fueloil "
            "la diferencia es pequeña; en buques a gas natural licuado es grande por el metano que se "
            "escapa sin quemar).")

    precio = _numero(precio_eua_eur, "el precio del derecho de emision europeo (EUA), en euros por tonelada",
                     minimo=0)
    cubiertas = emisiones * viaje["cobertura"]
    derechos = cubiertas * entrega
    costo = derechos * precio
    contenedores = _numero(teu, "los contenedores transportados (TEU)", obligatorio=False, minimo=0)

    return {
        "anio": anio,
        "tipo_viaje": viaje["clave"],
        "descripcion_viaje": viaje["descripcion"],
        "cobertura_viaje": viaje["cobertura"],
        "porcentaje_entrega": entrega,
        "combustible": ficha["clave"] if ficha else None,
        "factor_emision_t_por_t": factor_usado,
        "emisiones_viaje_t_co2e": emisiones,
        "emisiones_cubiertas_t_co2e": cubiertas,
        "derechos_a_entregar_t": derechos,
        "precio_eua_eur": precio,
        "costo_eur": costo,
        "teu": contenedores,
        "recargo_por_teu_eur": (costo / contenedores) if contenedores else None,
        "recargo_por_feu_eur": (costo / contenedores * 2) if contenedores else None,
        "obligado": ("La compañia naviera (armador, gestor naval o fletador a casco desnudo). El exportador "
                     "no declara ni entrega derechos: lo paga como recargo en el flete."),
        "articulos": ["Art. 3 octies bis de la Directiva 2003/87/CE (cobertura del viaje)",
                      "Art. 3 octies ter de la Directiva 2003/87/CE (40 % en 2024, 70 % en 2025, 100 % desde 2026)",
                      "Anexo I de la Directiva 2003/87/CE (CO2 desde 2024; CH4 y N2O desde 2026)",
                      "Anexo II del Reglamento (UE) 2023/1805 (factores de los combustibles)"],
        "que_pedirle_a_la_naviera": [
            "Que el recargo aplique el 50 % en las rutas Sudamerica-Europa, no el 100 %.",
            "El precio del derecho europeo usado como referencia y el periodo al que corresponde.",
            "El factor de emision por contenedor de esa ruta y ese servicio.",
            "El desglose separado del recargo del mercado de carbono y del de FuelEU: son dos cosas "
            "distintas y no se compensan entre si.",
        ],
        "supuestos": supuestos,
        "advertencias": advertencias,
        "no_verificado": pendientes("ets_exclusiones_mrv", "gwp_fueleu") if incluir_ch4_n2o
                         else pendientes("ets_exclusiones_mrv"),
        "fuente": FUENTE,
    }


# --------------------------------------------------------------------------
# CSRD — Directiva 2013/34/UE tras la Directiva (UE) 2026/470 ("Omnibus I")
# --------------------------------------------------------------------------

UMBRAL_CSRD_VOLUMEN_EUR = 450000000.0
UMBRAL_CSRD_EMPLEADOS = 1000
UMBRAL_CSRD_VOLUMEN_EN_UE_EUR = 450000000.0
UMBRAL_CSRD_FILIAL_UE_EUR = 200000000.0
UMBRAL_EMPRESA_PROTEGIDA_EMPLEADOS = 1000
PRIMER_EJERCICIO_CSRD_NUEVO = 2027
PRIMER_INFORME_CSRD_NUEVO = 2028

NORMAS_CSRD = {
    "base": "Directiva 2013/34/UE en su version consolidada tras la Directiva (UE) 2026/470",
    "stop_the_clock": "Directiva (UE) 2025/794, de 14 de abril de 2025 (aplazo el calendario)",
    "omnibus": "Directiva (UE) 2026/470, de 24 de febrero de 2026 (cambio los umbrales y el contenido)",
    "transposicion_csrd": "19 de marzo de 2027",
    "transposicion_csddd": "26 de julio de 2028",
}

UMBRALES_CSDDD = {
    "empleados": 5000,
    "volumen_negocios_eur": 1500000000.0,
    "aplicacion": "26 de julio de 2029 para todas las empresas en ambito",
    "sancion": "Tope uniforme del 3 % del volumen de negocios mundial neto (antes era el 5 %).",
    "norma": "Directiva (UE) 2024/1760, modificada por la Directiva (UE) 2026/470",
}


def csrd_aplica(empleados=None, volumen_negocios_eur=None, establecida_en_ue=False,
                volumen_negocios_en_ue_eur=None, filial_ue_volumen_eur=None,
                tiene_sucursal_ue=False, ya_reportaba=False, ejercicio=None):
    """Si a la empresa le aplica el informe de sostenibilidad europeo (CSRD).

    Regimen vigente tras la Directiva (UE) 2026/470:

    - Empresa o grupo de la Union Europea (arts. 19 bis y 29 bis de la Directiva
      2013/34/UE): volumen de negocios neto superior a 450 000 000 EUR **y** mas de
      1 000 empleados de media. Los dos criterios a la vez, no dos de tres.
      Primer ejercicio reportado: el que empiece desde el 1-1-2027; primer informe: 2028.

    - Matriz de fuera de la UE (art. 40 bis): volumen de negocios del grupo generado
      DENTRO de la UE superior a 450 000 000 EUR durante dos ejercicios consecutivos
      **y** una filial en la UE con mas de 200 000 000 EUR de volumen de negocios.
      El umbral de la sucursal quedo sin confirmar en la investigacion.

    - Empresa protegida (tope VSME): la que no supera una media de 1 000 empleados
      puede negarse a entregar a su cliente informacion que exceda los limites del
      estandar voluntario VSME. Es un techo frente a la obligacion regulatoria, no
      frente a lo que el cliente pacte por contrato.

    Devuelve "aplica", "no aplica" o "revisar". Nunca dice "no aplica" si le falta
    un dato: en ese caso pide el dato.
    """
    personas = _numero(empleados, "el numero de empleados", obligatorio=False, minimo=0)
    volumen = _numero(volumen_negocios_eur, "el volumen de negocios en euros", obligatorio=False, minimo=0)
    volumen_ue = _numero(volumen_negocios_en_ue_eur, "el volumen de negocios generado en la UE, en euros",
                         obligatorio=False, minimo=0)
    filial = _numero(filial_ue_volumen_eur, "el volumen de negocios de la filial europea, en euros",
                     obligatorio=False, minimo=0)

    protegida = None if personas is None else personas <= UMBRAL_EMPRESA_PROTEGIDA_EMPLEADOS
    faltan = []
    if establecida_en_ue:
        via = "Empresa o grupo establecido en la Union Europea (arts. 19 bis y 29 bis)"
        if personas is None:
            faltan.append("cuantas personas trabajan en promedio en el ejercicio")
        if volumen is None:
            faltan.append("el volumen de negocios neto anual en euros")
        if faltan:
            estado = "revisar"
            motivo = "Falta un dato para decidir: %s." % " y ".join(faltan)
        elif volumen > UMBRAL_CSRD_VOLUMEN_EUR and personas > UMBRAL_CSRD_EMPLEADOS:
            estado = "aplica"
            motivo = ("Supera los dos umbrales a la vez: mas de 450 millones de euros de volumen de "
                      "negocios y mas de 1.000 empleados.")
        else:
            estado = "no aplica"
            motivo = ("Para quedar obligada hay que superar los DOS umbrales: mas de 450 millones de euros "
                      "y mas de 1.000 empleados. La empresa no los supera.")
    else:
        via = "Matriz de un tercer pais con actividad en la Union Europea (art. 40 bis)"
        if volumen_ue is None:
            faltan.append("cuanto factura el grupo dentro de la Union Europea")
        if volumen_ue is not None and volumen_ue > UMBRAL_CSRD_VOLUMEN_EN_UE_EUR and filial is None:
            faltan.append("el volumen de negocios de la filial europea")
        if faltan:
            estado = "revisar"
            motivo = ("Falta un dato para decidir: %s. Casi ninguna empresa exportadora de Chile o Peru "
                      "llega a estos numeros, pero conviene confirmarlo." % " y ".join(faltan))
        elif volumen_ue > UMBRAL_CSRD_VOLUMEN_EN_UE_EUR and filial and filial > UMBRAL_CSRD_FILIAL_UE_EUR:
            estado = "aplica"
            motivo = ("El grupo factura mas de 450 millones de euros dentro de la Union Europea y tiene una "
                      "filial europea de mas de 200 millones: entra por la puerta de las matrices de "
                      "terceros paises.")
        elif volumen_ue > UMBRAL_CSRD_VOLUMEN_EN_UE_EUR and tiene_sucursal_ue and not filial:
            estado = "revisar"
            motivo = ("El grupo supera los 450 millones de euros en la Union Europea y opera con sucursal. "
                      "El umbral de la sucursal tras la reforma de 2026 no esta confirmado.")
        else:
            estado = "no aplica"
            motivo = ("No alcanza los umbrales del art. 40 bis: hacen falta mas de 450 millones de euros "
                      "facturados dentro de la Union Europea durante dos ejercicios seguidos y una filial "
                      "europea de mas de 200 millones.")

    oleada = None
    if ya_reportaba:
        oleada = ("Primera oleada: entidades de interes publico de mas de 500 empleados que ya reportaban. "
                  "Mantienen la obligacion solo para ejercicios que empiecen hasta el 31-12-2026.")

    return {
        "estado": estado,
        "via": via,
        "motivo": motivo,
        "faltan_datos": faltan,
        "primer_ejercicio": PRIMER_EJERCICIO_CSRD_NUEVO if estado == "aplica" else None,
        "primer_informe": PRIMER_INFORME_CSRD_NUEVO if estado == "aplica" else None,
        "oleada": oleada,
        "umbrales": {
            "volumen_negocios_eur": UMBRAL_CSRD_VOLUMEN_EUR,
            "empleados": UMBRAL_CSRD_EMPLEADOS,
            "volumen_en_ue_eur": UMBRAL_CSRD_VOLUMEN_EN_UE_EUR,
            "filial_ue_eur": UMBRAL_CSRD_FILIAL_UE_EUR,
            "logica": "Los dos criterios a la vez (acumulativos), no dos de tres.",
        },
        "empresa_protegida": protegida,
        "tope_vsme": {
            "aplica": protegida,
            "que_es": ("La empresa declarante sujeta a la CSRD no puede exigir a una empresa que no supera "
                       "los 1.000 empleados informacion que exceda los limites del estandar voluntario "
                       "VSME, y esa empresa puede negarse a entregarla."),
            "limite": "Estandar voluntario VSME para pymes no cotizadas.",
            "ojo": ("Es un techo frente a lo que el cliente puede EXIGIR por obligacion legal, no frente a "
                    "lo que puede PACTAR en el contrato. Y si el proveedor no esta domiciliado en la Union "
                    "Europea, que pueda invocarlo no esta confirmado."),
        },
        "aseguramiento": "Solo aseguramiento limitado; se elimino el paso a aseguramiento razonable.",
        "estandares_sectoriales": ("Se suprimieron los estandares sectoriales obligatorios. La Comision solo "
                                   "podra emitir orientaciones sectoriales no vinculantes."),
        "normas": NORMAS_CSRD,
        "csddd": UMBRALES_CSDDD,
        "articulos": ["Arts. 19 bis, 29 bis y 40 bis de la Directiva 2013/34/UE, en su version tras la "
                      "Directiva (UE) 2026/470",
                      "Directiva (UE) 2025/794 (aplazamiento del calendario)"],
        "no_verificado": pendientes("csrd_sucursal_ue", "csrd_tope_vsme_extraterritorial", "csrd_espana"),
        "aviso": AVISO_LEGAL,
        "fuente": FUENTE,
    }


# --------------------------------------------------------------------------
# EUDR — Reglamento (UE) 2023/1115 tras el Reglamento (UE) 2025/2650
# --------------------------------------------------------------------------

FECHA_CORTE_EUDR = "31 de diciembre de 2020"

MATERIAS_EUDR = {
    "ganado_bovino": {"nombre": "Ganado bovino", "derivados": ["carne de bovino", "cuero"]},
    "cacao": {"nombre": "Cacao", "derivados": ["pasta de cacao", "manteca de cacao", "chocolate"]},
    "cafe": {"nombre": "Cafe", "derivados": ["cafe tostado", "cafe soluble"]},
    "palma_aceitera": {"nombre": "Palma aceitera", "derivados": ["aceite de palma", "derivados oleoquimicos"]},
    "caucho": {"nombre": "Caucho", "derivados": ["neumaticos", "manufacturas de caucho"]},
    "soja": {"nombre": "Soja", "derivados": ["harina de soja", "aceite de soja"]},
    "madera": {"nombre": "Madera", "derivados": ["muebles", "tableros", "pasta y papel"]},
}

ALIAS_MATERIAS_EUDR = {
    "ganadobovino": "ganado_bovino", "ganado": "ganado_bovino", "bovino": "ganado_bovino",
    "carnedevacuno": "ganado_bovino", "vacuno": "ganado_bovino", "cuero": "ganado_bovino",
    "cacao": "cacao", "chocolate": "cacao",
    "cafe": "cafe",
    "palma": "palma_aceitera", "palmaaceitera": "palma_aceitera", "aceitedepalma": "palma_aceitera",
    "caucho": "caucho", "neumaticos": "caucho", "hule": "caucho",
    "soja": "soja", "soya": "soja",
    "madera": "madera", "muebles": "madera", "celulosa": "madera", "tableros": "madera",
    "papel": "madera", "pastadecelulosa": "madera",
}

# Reglamento de Ejecucion (UE) 2025/1093, de 22 de mayo de 2025.
# Los paises que no figuran en la lista de riesgo alto ni en la de riesgo bajo
# mantienen riesgo estandar (art. 1, ap. 2).
RIESGO_PAIS_EUDR = {
    "CL": "bajo",
    "PE": "estandar", "BR": "estandar", "CO": "estandar",
    "BY": "alto", "KP": "alto", "MM": "alto", "RU": "alto",
}
RIESGO_EUDR_POR_DEFECTO = "estandar"

# Fechas de la pagina oficial de la Comision Europea; no confirmadas contra el art. 38.
FECHAS_EUDR = {
    "grande": "30 de diciembre de 2026",
    "mediana": "30 de diciembre de 2026",
    "pequena": "30 de junio de 2027",
    "micro": "30 de junio de 2027",
}
FECHA_EUDR_EUTR = "30 de diciembre de 2026"

INFORMACION_EUDR = [
    {"id": "descripcion", "que": "Descripcion del producto y lista de materias primas que contiene",
     "por": "lote", "articulo": "Art. 9 del Reglamento (UE) 2023/1115"},
    {"id": "cantidad", "que": "Cantidad del envio, en kilogramos",
     "por": "lote", "articulo": "Art. 9 del Reglamento (UE) 2023/1115"},
    {"id": "pais_produccion", "que": "Pais donde se produjo la materia prima",
     "por": "lote", "articulo": "Art. 9 del Reglamento (UE) 2023/1115"},
    {"id": "geolocalizacion",
     "que": "Coordenadas de latitud y longitud de todas las parcelas donde se produjo",
     "por": "predio", "articulo": "Art. 9 del Reglamento (UE) 2023/1115"},
    {"id": "proveedor", "que": "Nombre, direccion y correo del proveedor de cada lote",
     "por": "lote", "articulo": "Art. 9 del Reglamento (UE) 2023/1115"},
    {"id": "comprador", "que": "Nombre, direccion y correo de a quien se le vendio",
     "por": "lote", "articulo": "Art. 9 del Reglamento (UE) 2023/1115"},
    {"id": "libre_deforestacion",
     "que": "Prueba de que la tierra no fue deforestada despues del 31 de diciembre de 2020 "
            "(imagenes satelitales, titulos, estudios, certificaciones)",
     "por": "predio", "articulo": "Arts. 2 y 9 del Reglamento (UE) 2023/1115"},
    {"id": "legalidad",
     "que": "Prueba de que la produccion cumple la legislacion del pais: uso del suelo, ambiental, "
            "laboral, derechos de terceros y tributaria",
     "por": "predio", "articulo": "Art. 3, letra b), del Reglamento (UE) 2023/1115"},
]

PASOS_DILIGENCIA_EUDR = [
    {"paso": 1, "titulo": "Recopilar la informacion", "articulo": "Art. 9",
     "obligatorio_en_riesgo_bajo": True,
     "detalle": "Reunir y conservar durante cinco años todos los datos de cada lote y cada predio."},
    {"paso": 2, "titulo": "Evaluar el riesgo", "articulo": "Art. 10",
     "obligatorio_en_riesgo_bajo": False,
     "detalle": ("Considerar la clasificacion de riesgo del pais, la presencia de bosques, los derechos de "
                 "los pueblos indigenas, la complejidad de la cadena y las denuncias recibidas.")},
    {"paso": 3, "titulo": "Mitigar el riesgo", "articulo": "Art. 11",
     "obligatorio_en_riesgo_bajo": False,
     "detalle": ("Tomar medidas hasta dejar el riesgo en nulo o insignificante: documentacion adicional, "
                 "auditorias independientes, apoyo al proveedor para que levante su informacion.")},
    {"paso": 4, "titulo": "Presentar la declaracion de diligencia debida", "articulo": "Arts. 4 y 33",
     "obligatorio_en_riesgo_bajo": True,
     "detalle": ("La presenta el operador europeo por el sistema de informacion (TRACES) antes de poner el "
                 "producto en el mercado. Genera un numero de referencia que acompaña al producto.")},
]

SANCIONES_EUDR = [
    "Multa de al menos el 4 % del volumen de negocios anual del operador en toda la Union Europea.",
    "Decomiso de los productos y de los ingresos obtenidos.",
    "Exclusion de la contratacion publica y del acceso a financiacion publica.",
    "Prohibicion temporal de comercializar, en infracciones graves o reiteradas.",
]


def materia_eudr(nombre):
    """Materia prima del Anexo I del Reglamento (UE) 2023/1115, como la escriba una persona."""
    clave = ALIAS_MATERIAS_EUDR.get(_clave(nombre))
    if not clave:
        raise Problema(
            "«%s» no esta entre las materias primas del reglamento de deforestacion."
            % (nombre if nombre else "(vacio)"),
            ("Solo cubre siete: ganado bovino, cacao, cafe, palma aceitera, caucho, soja y madera, mas sus "
             "derivados (cuero, chocolate, neumaticos, muebles y otros). La fruta, la uva, la pesca y el "
             "cobre quedan fuera."),
            {"materias": sorted(MATERIAS_EUDR)},
        )
    return dict(MATERIAS_EUDR[clave], clave=clave)


def riesgo_pais_eudr(pais):
    """Categoria de riesgo del pais (Reglamento de Ejecucion (UE) 2025/1093)."""
    codigo = str(pais or "").strip().upper()
    if codigo in RIESGO_PAIS_EUDR:
        return RIESGO_PAIS_EUDR[codigo], True
    return RIESGO_EUDR_POR_DEFECTO, False


def eudr_aplica(producto=None, pais=None, tamano_operador=None, cubierto_por_eutr=False):
    """Si al producto le aplica el reglamento europeo de deforestacion, y con que exigencia.

    Los tres requisitos del art. 3 del Reglamento (UE) 2023/1115 son acumulativos:
    el producto tiene que estar libre de deforestacion (fecha de corte: 31 de
    diciembre de 2020), haberse producido conforme a la legislacion del pais y estar
    amparado por una declaracion de diligencia debida.

    La diligencia debida es simplificada cuando el pais de produccion esta clasificado
    como de riesgo bajo por el Reglamento de Ejecucion (UE) 2025/1093: basta con
    recopilar la informacion del art. 9, sin completar la evaluacion (art. 10) ni la
    mitigacion del riesgo (art. 11). Chile es de riesgo bajo; Peru, Brasil y Colombia
    son de riesgo estandar y necesitan la diligencia completa.

    Las fechas de aplicacion proceden de la pagina oficial de la Comision y no se
    confirmaron contra el articulo 38: sirven para planificar, no para discutir plazos.
    """
    if producto in (None, "", True, False):
        return {
            "estado": "revisar",
            "motivo": ("Falta saber que se exporta. El reglamento cubre ganado bovino, cacao, cafe, palma "
                       "aceitera, caucho, soja y madera, y los productos hechos con ellos."),
            "materias_cubiertas": [MATERIAS_EUDR[m]["nombre"] for m in sorted(MATERIAS_EUDR)],
            "fecha_de_corte": FECHA_CORTE_EUDR,
            "articulos": ["Anexo I del Reglamento (UE) 2023/1115"],
            "no_verificado": pendientes("eudr_fechas_articulado"),
            "fuente": FUENTE,
        }

    ficha = materia_eudr(producto)
    riesgo, listado = riesgo_pais_eudr(pais)
    tamano = _clave(tamano_operador) if tamano_operador not in (None, True, False) else ""
    tamano = {"grande": "grande", "mediana": "mediana", "median": "mediana", "pequena": "pequena",
              "pequeña": "pequena", "micro": "micro", "microempresa": "micro"}.get(tamano, "")

    if cubierto_por_eutr and tamano in ("micro", "pequena"):
        fecha = FECHA_EUDR_EUTR
        nota_fecha = ("Como microempresa o empresa pequeña ya cubierta por el reglamento anterior de la "
                      "madera, la fecha es la misma de las grandes.")
    elif tamano:
        fecha = FECHAS_EUDR[tamano]
        nota_fecha = ""
    else:
        fecha = None
        nota_fecha = ("Falta saber el tamaño del operador europeo que importa: grandes y medianas desde el "
                      "30 de diciembre de 2026; micro y pequeñas desde el 30 de junio de 2027.")

    simplificada = riesgo == "bajo"
    pasos = [dict(p, exigible=(p["obligatorio_en_riesgo_bajo"] or not simplificada))
             for p in PASOS_DILIGENCIA_EUDR]

    return {
        "estado": "aplica",
        "materia_prima": ficha["clave"],
        "materia_prima_nombre": ficha["nombre"],
        "derivados": ficha["derivados"],
        "pais": str(pais or "").strip().upper() or None,
        "riesgo_pais": riesgo,
        "riesgo_confirmado_en_lista": listado,
        "nota_riesgo": (("%s figura en la lista de riesgo %s del Reglamento de Ejecucion (UE) 2025/1093."
                         % (str(pais).strip().upper(), riesgo)) if listado else
                        ("Ese pais no figura en la lista de riesgo alto ni en la de riesgo bajo, asi que "
                         "queda en riesgo estandar (art. 1, ap. 2, del Reglamento de Ejecucion (UE) 2025/1093).")),
        "diligencia": "simplificada" if simplificada else "completa",
        "explicacion_diligencia": (
            "Riesgo bajo: basta con recopilar y conservar la informacion del art. 9. No hay que completar "
            "la evaluacion ni la mitigacion del riesgo. Es una ventaja competitiva concreta."
            if simplificada else
            "Riesgo estandar o alto: hay que hacer la diligencia debida completa, con recopilacion de "
            "informacion (art. 9), evaluacion del riesgo (art. 10) y mitigacion hasta dejarlo en nulo o "
            "insignificante (art. 11)."),
        "fecha_de_aplicacion": fecha,
        "nota_fecha": nota_fecha,
        "fecha_de_corte": FECHA_CORTE_EUDR,
        "requisitos_articulo_3": [
            "Estar libre de deforestacion: la tierra no puede haber sido deforestada despues del "
            "31 de diciembre de 2020.",
            "Haberse producido conforme a la legislacion del pais de produccion.",
            "Estar amparado por una declaracion de diligencia debida del operador europeo.",
        ],
        "pasos_de_diligencia": pasos,
        "informacion_requerida": INFORMACION_EUDR,
        "sanciones": SANCIONES_EUDR,
        "quien_declara": ("El operador europeo que pone el producto en el mercado presenta la declaracion "
                          "por el sistema TRACES. El exportador no declara: entrega la informacion y las "
                          "pruebas."),
        "articulos": ["Art. 2 del Reglamento (UE) 2023/1115 (definicion y fecha de corte)",
                      "Art. 3 del Reglamento (UE) 2023/1115 (los tres requisitos)",
                      "Arts. 9, 10 y 11 del Reglamento (UE) 2023/1115 (diligencia debida)",
                      "Arts. 4 y 33 del Reglamento (UE) 2023/1115 (declaracion y sistema de informacion)",
                      "Art. 25 del Reglamento (UE) 2023/1115 (sanciones)",
                      "Reglamento de Ejecucion (UE) 2025/1093 (riesgo por pais)"],
        "no_verificado": pendientes("eudr_fechas_articulado", "eudr_geolocalizacion"),
        "aviso": AVISO_LEGAL,
        "fuente": FUENTE,
    }
