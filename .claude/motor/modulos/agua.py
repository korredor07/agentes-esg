# -*- coding: utf-8 -*-
"""Huella hidrica y gestion del agua: contabilidad GRI 303, escasez AWARE y MEE de la DGA."""

import datetime
import json
import os

from calculos import agua as motor_agua
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta
from plantillas import definiciones

AYUDA = ("Calcula cuanta agua entra, sale y se consume en cada sitio (GRI 303), pondera el consumo por "
         "la escasez del lugar (metodo AWARE) y revisa la obligacion chilena de monitorear las "
         "extracciones ante la DGA.")

PLANILLA = "agua.xlsx"

AVISO_CONTEXTO = ("Con el agua no basta el total: importa donde y cuando se usa. El mismo metro cubico "
                  "pesa muy distinto en una cuenca con estres hidrico que en una con agua de sobra.")

AVISO_APOYO = ("Esto es un apoyo de gestion, no una verificacion ni asesoria legal. Antes de publicar "
               "estas cifras o presentarlas a una autoridad, un cliente o una auditoria, revisa los "
               "datos de origen y sus respaldos.")


# --------------------------------------------------------------------------
# Utilidades del modulo
# --------------------------------------------------------------------------

def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def _bandera(opciones, clave):
    valor = opciones.get(clave)
    if valor is True:
        return True
    return str(valor or "").strip().lower() in ("si", "s", "sí", "true", "1", "ok")


def _nombre_resultado(periodo):
    return "agua_%s.json" % str(periodo or "completa").replace("/", "-")


def _leer_planilla(ruta_empresa):
    """Lee datos/agua.xlsx. Si no esta, explica como crearla."""
    ruta = espacio.ruta_de(ruta_empresa, "datos", PLANILLA)
    if not os.path.isfile(ruta):
        raise Problema(
            "No encontre la planilla de agua (%s) en la carpeta de datos de la empresa." % PLANILLA,
            "La creo vacia con: plantilla crear --tipo agua. Despues la llenas en Excel con una fila "
            "por periodo, sitio y origen del agua (cuanta entro, cuanta salio y a donde) y me avisas.",
            {"archivo_esperado": ruta},
        )
    tabla, aviso = definiciones.leer_sin_ejemplos(ruta)
    if not tabla["filas"]:
        raise Problema(
            "La planilla de agua (%s) %s." % (PLANILLA, "solo tiene las filas de ejemplo de la plantilla"
                                              if aviso else "esta sin datos"),
            "Abrela en Excel y escribe al menos una fila: periodo, sitio, origen del agua, metros "
            "cubicos extraidos y metros cubicos descargados.",
            {"archivo": ruta},
        )
    return tabla["filas"], ruta, aviso


def _resumen_del_periodo(ruta_empresa, periodo):
    """Calcula la contabilidad de agua del periodo desde la planilla."""
    filas, ruta, aviso = _leer_planilla(ruta_empresa)
    resumen = motor_agua.calcular(filas, periodo)
    resumen["planilla"] = ruta
    if aviso:
        resumen["advertencias"] = [aviso] + list(resumen.get("advertencias", []))
    return resumen


def _mes_del_periodo(periodo):
    """De '2025-03' saca 3. De '2025' no saca nada."""
    texto = str(periodo or "").strip()
    if len(texto) >= 7 and texto[4] in "-/" and texto[5:7].isdigit():
        mes = int(texto[5:7])
        return mes if 1 <= mes <= 12 else None
    return None


# --------------------------------------------------------------------------
# Accion: calcular
# --------------------------------------------------------------------------

def calcular(opciones):
    """Cuanta agua entro, salio y se consumio, con el desglose que pide GRI 303."""
    perfil, ruta_empresa = _contexto(opciones)
    periodo = _valor(opciones, "periodo") or None

    resumen = _resumen_del_periodo(ruta_empresa, periodo)
    resumen["empresa"] = perfil.get("nombre")
    resumen["pais"] = perfil.get("pais", "")
    resumen["indicadores_gri303"] = motor_agua.indicadores_gri303(resumen)

    destino = espacio.ruta_de(ruta_empresa, "resultados", _nombre_resultado(periodo))
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2, default=str)

    zonas = resumen["zonas_estres_hidrico"]
    liviano = {
        "empresa": resumen["empresa"],
        "periodo": resumen["periodo"],
        "planilla": resumen["planilla"],
        "extraccion_m3": round(resumen["extraccion_m3"], 3),
        "descarga_m3": round(resumen["descarga_m3"], 3),
        "consumo_m3": round(resumen["consumo_m3"], 3),
        "extraccion_megalitros": round(resumen["extraccion_megalitros"], 4),
        "descarga_megalitros": round(resumen["descarga_megalitros"], 4),
        "consumo_megalitros": round(resumen["consumo_megalitros"], 4),
        "formula_del_consumo": motor_agua.FORMULAS["consumo"]["formula"],
        "registros_calculados": resumen["registros_calculados"],
        "registros_con_problema": resumen["registros_con_problema"],
        "por_sitio": resumen["por_sitio"],
        "por_origen": resumen["por_origen"],
        "por_destino": resumen["por_destino"],
        "por_periodo": resumen["por_periodo"],
        "consumo_en_zonas_de_estres_m3": round(zonas["metros_cubicos"]["consumo_m3"]["si"], 3),
        "porcentaje_extraccion_en_zonas_de_estres": round(zonas["porcentaje"]["extraccion"]["si"], 2),
        "porcentaje_consumo_en_zonas_de_estres": round(zonas["porcentaje"]["consumo"]["si"], 2),
        "sitios_en_zona_de_estres": zonas["sitios_en_estres"],
        "sitios_sin_definir_estres": zonas["sitios_sin_definir"],
        "calidad_datos": resumen["calidad_datos"],
        "desglose_agua_dulce_y_otras": resumen["desglose_agua_dulce_y_otras"],
        "indicadores_gri303": resumen["indicadores_gri303"],
        "problemas": resumen["problemas"],
        "resultado_guardado_en": destino,
        "siguiente_paso": ("Para saber cuanto pesa ese consumo segun la escasez del lugar: "
                           "agua escasez. Para el informe en HTML: agua informe."),
    }
    return Respuesta(liviano,
                     advertencias=[AVISO_CONTEXTO] + list(resumen["advertencias"]) + [AVISO_APOYO],
                     fuentes=resumen["fuentes"])


# --------------------------------------------------------------------------
# Accion: escasez
# --------------------------------------------------------------------------

def _factor_mundial(agregacion, catalogo):
    """Factor de la region GLO para poder comparar. Si no esta, no se compara."""
    for factor in catalogo:
        if factor["iso3"] == "GLO" and factor["agregacion"] == agregacion and factor["periodo"] == "anual":
            return factor
    return None


def escasez(opciones):
    """Huella de escasez hidrica: consumo x factor AWARE del lugar.

    Solo calcula cuando la persona entrega el factor (--factor) o confirma el
    que propone el catalogo (--confirmar). El factor de pais es un promedio y
    AWARE se define por cuenca: por eso no se aplica a ciegas.
    """
    perfil, ruta_empresa = _contexto(opciones)
    periodo = _valor(opciones, "periodo") or None
    advertencias = [AVISO_CONTEXTO]

    consumo_pedido = _valor(opciones, "consumo")
    resumen = None
    if consumo_pedido:
        consumo = consumo_pedido
        origen_del_consumo = "el valor que me entregaste con --consumo"
    else:
        resumen = _resumen_del_periodo(ruta_empresa, periodo)
        consumo = resumen["consumo_m3"]
        origen_del_consumo = "la planilla %s (extraccion menos descarga, GRI 303-5)" % PLANILLA
        advertencias.extend(resumen["advertencias"])
        if resumen["registros_con_problema"]:
            advertencias.append(
                "Ojo: %d fila(s) de la planilla quedaron fuera del consumo por tener datos que revisar. "
                "Corrigelas y vuelve a calcular para que la huella sea completa."
                % resumen["registros_con_problema"])

    agregacion = motor_agua.normalizar_agregacion(_valor(opciones, "agregacion") or "no_agricola")
    mes = _valor(opciones, "mes") or _mes_del_periodo(periodo)
    if mes:
        try:
            mes = int(str(mes).strip())
        except ValueError:
            raise Problema(
                "El mes «%s» no lo entiendo." % mes,
                "Escribe el numero del mes: 1 para enero, 12 para diciembre.",
            )
        if not 1 <= mes <= 12:
            raise Problema(
                "El mes %s no existe." % mes,
                "Escribe un numero del 1 al 12.",
            )

    catalogo = motor_agua.cargar_factores_aware()
    factor_pedido = _valor(opciones, "factor")
    pais = (_valor(opciones, "pais") or perfil.get("pais") or "").upper()

    ficha = None
    if factor_pedido:
        factor = factor_pedido
        de_donde = "el factor que me entregaste con --factor"
    else:
        ficha, avisos = motor_agua.buscar_factor_aware(pais, agregacion, mes, catalogo)
        advertencias.extend(avisos)
        factor = ficha["factor"]
        de_donde = "el catalogo de factores %s por pais que trae el motor" % ficha["version"]
        if not _bandera(opciones, "confirmar"):
            return Respuesta({
                "huella_calculada": False,
                "empresa": perfil.get("nombre"),
                "periodo": periodo or "todos los periodos cargados",
                "consumo_m3": round(float(consumo), 3),
                "de_donde_sale_el_consumo": origen_del_consumo,
                "factor_propuesto": {
                    "factor_aware": ficha["factor"],
                    "pais": ficha["nombre"],
                    "agregacion": ficha["agregacion"],
                    "que_significa_la_agregacion": motor_agua.AGREGACIONES_AWARE[ficha["agregacion"]],
                    "periodo_del_factor": "anual" if ficha["periodo"] == "anual"
                                          else motor_agua.MESES.get(int(ficha["periodo"]), ficha["periodo"]),
                    "version": ficha["version"],
                    "fuente": ficha["fuente"],
                    "url": ficha["url"],
                    "licencia": ficha["licencia"],
                    "advertencia": ficha["notas"],
                },
                "por_que_te_lo_pregunto": (
                    "El factor de pais es un promedio y AWARE se define por cuenca y por mes: en un "
                    "pais largo como Chile, dos faenas pueden tener factores muy distintos. Antes de "
                    "usar este numero conviene que lo confirmes o que busques el de la cuenca del sitio."),
                "como_confirmar": (
                    "Si te sirve el promedio del pais: agua escasez --confirmar. "
                    "Si tienes el factor de la cuenca: agua escasez --factor %s (reemplaza el numero)."
                    % ficha["factor"]),
                "donde_conseguir_el_de_la_cuenca": motor_agua.DONDE_CONSEGUIR_AWARE,
                "formula_que_voy_a_usar": motor_agua.FORMULAS["huella_de_escasez"]["formula"],
            }, advertencias=advertencias + [AVISO_APOYO],
                fuentes=[motor_agua.FUENTE_ISO14046, motor_agua.ATRIBUCION_AWARE])

    comparacion = _factor_mundial(agregacion, catalogo)
    resultado = motor_agua.huella_de_escasez(
        consumo, factor, comparacion["factor"] if comparacion else None)
    resultado["empresa"] = perfil.get("nombre")
    resultado["periodo"] = periodo or "todos los periodos cargados"
    resultado["huella_calculada"] = True
    resultado["de_donde_sale_el_consumo"] = origen_del_consumo
    resultado["de_donde_sale_el_factor"] = de_donde
    resultado["agregacion"] = agregacion
    resultado["que_significa_la_agregacion"] = motor_agua.AGREGACIONES_AWARE[agregacion]
    if mes:
        resultado["mes_del_factor"] = motor_agua.MESES[mes]
    if ficha:
        resultado["pais_del_factor"] = ficha["nombre"]
        resultado["version_de_los_factores"] = ficha["version"]
        resultado["advertencia_del_factor"] = ficha["notas"]
    else:
        advertencias.append(
            "Use el factor %s que me entregaste. Deja anotado en el reporte de donde lo sacaste "
            "(cuenca, mes y version de AWARE): sin eso la cifra no se puede revisar." % factor)

    if resumen is not None:
        zonas = resumen["zonas_estres_hidrico"]["metros_cubicos"]["consumo_m3"]
        resultado["consumo_en_zonas_de_estres_m3"] = round(zonas["si"], 3)
        resultado["sitios_en_zona_de_estres"] = resumen["zonas_estres_hidrico"]["sitios_en_estres"]

    fuentes = [motor_agua.FUENTE_ISO14046, motor_agua.FUENTE_AWARE_METODO]
    if ficha:
        fuentes.append(motor_agua.ATRIBUCION_AWARE)
    return Respuesta(resultado, advertencias=advertencias + [AVISO_APOYO], fuentes=fuentes)


# --------------------------------------------------------------------------
# Accion: dga (monitoreo de extracciones efectivas, Chile)
# --------------------------------------------------------------------------

ESTANDARES_MEE = {
    "mayor": {
        "estandar": "Mayor",
        "sistema_de_medicion": "General",
        "plazo_medicion_y_registro": "4 meses",
        "plazo_transmision": "5 meses",
        "frecuencia_de_medicion": "1 medicion por hora",
        "via_de_transmision": "Online (API REST desde un Centro de Control)",
        "desfase_maximo": "7 dias",
    },
    "medio": {
        "estandar": "Medio",
        "sistema_de_medicion": "General o Basico",
        "plazo_medicion_y_registro": "10 meses",
        "plazo_transmision": "12 meses",
        "frecuencia_de_medicion": "1 medicion por dia",
        "via_de_transmision": "Archivo (planilla Excel con el formato oficial)",
        "desfase_maximo": "15 dias",
    },
    "menor": {
        "estandar": "Menor",
        "sistema_de_medicion": "Basico",
        "plazo_medicion_y_registro": "60 meses",
        "plazo_transmision": "72 meses",
        "frecuencia_de_medicion": "1 medicion por mes",
        "via_de_transmision": "Formulario en el software MEE",
        "desfase_maximo": "1 mes",
    },
    "muy_pequenos": {
        "estandar": "Caudales Muy Pequenos",
        "sistema_de_medicion": "Solo flujometro",
        "plazo_medicion_y_registro": "60 meses",
        "plazo_transmision": "72 meses",
        "frecuencia_de_medicion": "2 mediciones por año",
        "via_de_transmision": "Formulario en el software MEE",
        "desfase_maximo": "1 mes",
    },
}

ALIAS_ESTANDAR = {
    "mayor": "mayor", "grande": "mayor",
    "medio": "medio", "mediano": "medio",
    "menor": "menor", "pequeno": "menor",
    "muy pequenos": "muy_pequenos", "muy pequeno": "muy_pequenos",
    "caudales muy pequenos": "muy_pequenos",
}

SISTEMAS_DE_MEDICION = {
    "General": ("Flujometro que mide volumen y caudal, mas un sensor de nivel freatico y un data logger "
                "instalados en la obra."),
    "Basico": ("El mismo flujometro del sistema General, mas un equipo para medir el nivel freatico que "
               "puede ser portatil (no queda fijo en la obra)."),
    "Solo flujometro": ("Solo el flujometro. No se exige sensor de nivel freatico ni data logger. Es el "
                        "sistema del estandar de caudales muy pequeños."),
}

SISTEMAS_DE_TRANSMISION = {
    "Online": "Un Centro de Control envia los datos al software de la DGA de forma automatica.",
    "Archivo": "Se sube una planilla Excel con el formato oficial de la DGA.",
    "Formulario": "Se escriben a mano en el software MEE los caudales, volumenes y niveles freaticos.",
}

NORMAS_MEE = [
    {"norma": "Codigo de Aguas, arts. 67, 68 y 173",
     "que_dice": ("El art. 68 permite a la DGA exigir que se instalen y mantengan sistemas de medicion "
                  "de caudales, de volumenes extraidos y de niveles freaticos, mas un sistema para "
                  "transmitirle esa informacion."),
     "verificado": True},
    {"norma": "Ley 21.064 (D.O. 27-01-2018)",
     "que_dice": ("Modifico el Codigo de Aguas y reforzo la fiscalizacion y el monitoreo de la DGA. Es la "
                  "base sobre la que se implementa el MEE."),
     "verificado": True},
    {"norma": "Resolucion DGA (Exenta) N 1238, de 21-06-2019 (D.O. 01-07-2019)",
     "que_dice": ("Norma matriz nacional para obras de captacion de aguas SUBTERRANEAS: fija las "
                  "condiciones tecnicas y los plazos, con 4 estandares, 3 sistemas de medicion y 3 "
                  "sistemas de transmision."),
     "verificado": True},
    {"norma": "Resolucion DGA (Exenta) N 564, de 13-04-2020",
     "que_dice": "Rectifica la Resolucion 1238 en los estandares y en el respaldo del Centro de Control.",
     "verificado": True},
    {"norma": "Resolucion DGA (Exenta) N 1608, de 2023",
     "que_dice": ("Amplia los plazos de instalacion de los estandares Menor y Caudales Muy Pequeños. "
                  "Dato de fuente secundaria: confirma su vigencia con la DGA regional."),
     "verificado": False},
    {"norma": "Resolucion DGA N 2170, de junio de 2025 (vigente desde el 01-08-2025)",
     "que_dice": ("Manual Tecnico N 1 de transmision online: endpoints REST, formato JSON y controles de "
                  "ciberseguridad para los Centros de Control. Dato de fuente secundaria."),
     "verificado": False},
    {"norma": "Resoluciones DGA regionales",
     "que_dice": ("Son las que realmente activan la obligacion en cada zona y las que fijan los rangos de "
                  "caudal (litros por segundo) que asignan cada estandar. Los plazos se cuentan desde que "
                  "la resolucion regional se publica en el Diario Oficial."),
     "verificado": True},
    {"norma": "Resolucion DGA N 2129, de 2016",
     "que_dice": ("Titulares que ya tenian una orden de control de extracciones: mantienen su sistema y "
                  "deben registrarse en el software MEE, transmitiendo mensualmente por formulario el "
                  "totalizador, el caudal y el nivel freatico."),
     "verificado": True},
    {"norma": "Decreto MOP N 53, de 2020 (D.O. 15-10-2020)",
     "que_dice": ("Reglamento de monitoreo de extracciones efectivas de aguas SUPERFICIALES: obliga a "
                  "instalar y mantener dispositivos de control y aforo mas transmision instantanea, con "
                  "cuatro niveles de exigencia y rangos de caudal fijados en las resoluciones regionales."),
     "verificado": True},
    {"norma": "Ley 21.740 (D.O. 23-04-2025)",
     "que_dice": ("Cambia el procedimiento de fiscalizacion y vigilancia de la DGA: colaboracion de "
                  "municipios y otros organos del Estado, procedimiento sancionatorio simplificado, "
                  "paralizacion inmediata de extracciones no autorizadas y notificacion electronica."),
     "verificado": True},
    {"norma": "Ley 21.435 (D.O. 06-04-2022), reforma del Codigo de Aguas",
     "que_dice": ("Los derechos nuevos duran 30 años y se extinguen por no usarlos: 5 años en los "
                  "consuntivos y 10 en los no consuntivos (art. 6 bis). El uso para consumo humano, uso "
                  "domestico de subsistencia y saneamiento siempre tiene prioridad (art. 5 bis)."),
     "verificado": True},
]

PASOS_MEE = [
    {"paso": 1,
     "que_hacer": ("Revisa si tu obra de captacion esta en una zona ya cubierta por una resolucion "
                   "regional de MEE, o si recibiste una orden de control de la DGA. Eso es lo que "
                   "activa la obligacion."),
     "donde": "dga.mop.gob.cl, seccion Monitoreo de Extracciones Efectivas, resoluciones por region"},
    {"paso": 2,
     "que_hacer": ("Suma el caudal de TODOS los derechos de aprovechamiento que se ejercen en esa misma "
                   "obra de captacion, en litros por segundo. El estandar se asigna por el caudal total "
                   "de la obra, no por cada derecho por separado."),
     "donde": "Las resoluciones que constituyeron tus derechos y el Catastro Publico de Aguas"},
    {"paso": 3,
     "que_hacer": ("Busca en la resolucion regional en que rango de caudal cae ese total: ahi dice si te "
                   "toca el estandar Mayor, Medio, Menor o de Caudales Muy Pequeños."),
     "donde": "La resolucion regional publicada en el Diario Oficial"},
    {"paso": 4,
     "que_hacer": ("Designa a un informante. Puede ser un tercero, pero la responsabilidad sigue siendo "
                   "del titular. Necesita ClaveUnica."),
     "donde": "Software MEE de la DGA"},
    {"paso": 5,
     "que_hacer": ("Registra la obra en el software MEE con los titulares, los derechos y las "
                   "caracteristicas del sistema de medicion. Te entregan un codigo de obra y un codigo "
                   "QR que hay que exhibir en un lugar visible de la obra."),
     "donde": "Software MEE de la DGA"},
    {"paso": 6,
     "que_hacer": ("Instala el sistema de medicion que corresponde a tu estandar (General, Basico o solo "
                   "flujometro) dentro del plazo. La DGA no acredita proveedores ni certifica "
                   "instaladores: la responsabilidad de que el equipo cumpla es tuya."),
     "donde": "En la obra de captacion"},
    {"paso": 7,
     "que_hacer": ("Instala el sistema de transmision y empieza a transmitir dentro del plazo, por la via "
                   "que corresponda: online, archivo Excel o formulario."),
     "donde": "Software MEE de la DGA"},
    {"paso": 8,
     "que_hacer": ("Guarda los registros y manten el sistema funcionando. Dejar de transmitir no es solo "
                   "un incumplimiento administrativo: alimenta la evidencia de que el derecho no se esta "
                   "usando, y el no uso extingue el derecho (Ley 21.435)."),
     "donde": "Registro interno de la empresa y software MEE"},
]

LO_QUE_EL_MOTOR_NO_PUEDE_DETERMINAR = [
    ("Los rangos de caudal en litros por segundo de cada estandar NO existen a nivel nacional: los fija "
     "cada resolucion regional. Por eso el motor no puede decirte que estandar te toca solo con el "
     "caudal; hace falta la resolucion regional de tu zona."),
    ("Las frecuencias de medicion y los desfases maximos de transmision que muestro provienen de fuentes "
     "secundarias, no del texto de la resolucion. Confirmalos en la Resolucion DGA 1238/2019 y en la "
     "1608/2023 antes de comprometer una frecuencia."),
    ("El estado de los plazos por region cambia y proviene de fuentes secundarias. Confirmalo con la DGA "
     "regional que corresponda."),
]


def dga(opciones):
    """Lista de verificacion de la obligacion chilena de monitorear extracciones (MEE)."""
    perfil, _ruta_empresa = _contexto(opciones)
    advertencias = [AVISO_APOYO]

    pais = (perfil.get("pais") or "").upper()
    if pais and pais != "CL":
        advertencias.append(
            "Esta obligacion es chilena y la empresa figura en %s. Lo de abajo le aplica solo si tambien "
            "extrae agua en Chile con derechos de aprovechamiento; para %s no tengo cargada la normativa "
            "equivalente." % (pais, pais))

    pedido = _valor(opciones, "estandar")
    estandar = None
    if pedido:
        clave = excel.normalizar_encabezado(pedido).replace("_", " ")
        elegido = ALIAS_ESTANDAR.get(clave)
        if not elegido:
            raise Problema(
                "No conozco el estandar de monitoreo «%s»." % pedido,
                "Los cuatro estandares de la Resolucion DGA 1238/2019 son: mayor, medio, menor y "
                "caudales muy pequeños.",
            )
        estandar = ESTANDARES_MEE[elegido]

    caudal = _valor(opciones, "caudal")
    if caudal:
        advertencias.append(
            "Me diste un caudal de %s l/s, pero con eso solo no puedo decirte que estandar te toca: los "
            "rangos de caudal los fija la resolucion regional de tu zona, no una tabla nacional. Busca "
            "esa resolucion en dga.mop.gob.cl y ahi vas a ver en que rango cae." % caudal)

    region = _valor(opciones, "region")
    if not region:
        advertencias.append(
            "No me dijiste la region de la obra de captacion. Los plazos se cuentan desde que se publica "
            "la resolucion regional en el Diario Oficial, asi que sin la region no puedo decirte si ya "
            "estas fuera de plazo.")

    resultado = {
        "empresa": perfil.get("nombre"),
        "pais": pais or "sin pais en el perfil",
        "obligacion": ("Monitoreo de Extracciones Efectivas (MEE): quien tiene derechos de "
                       "aprovechamiento de agua en Chile debe medir cuanta agua saca realmente y "
                       "transmitirle esa informacion a la Direccion General de Aguas (DGA)."),
        "por_que_importa": (
            "No es solo un tramite. Con la reforma del Codigo de Aguas (Ley 21.435) los derechos se "
            "extinguen si no se usan: 5 años en los derechos consuntivos y 10 en los no consuntivos. "
            "El monitoreo es justamente la prueba del uso efectivo, asi que no transmitir puede terminar "
            "costando el derecho de agua, no solo una multa."),
        "a_quien_le_aplica": [
            ("A quien tenga derechos de aprovechamiento cuya obra de captacion este en una zona cubierta "
             "por una resolucion regional de MEE."),
            ("A quien haya recibido una orden de control de extracciones de la DGA: por la Resolucion "
             "2129/2016, al constituirse el derecho, al cambiar el punto de captacion, en derechos "
             "provisionales o dentro de un proceso de fiscalizacion."),
            ("Hay dos reglamentos distintos: la Resolucion DGA 1238/2019 para aguas subterraneas (pozos, "
             "norias, sondajes) y el Decreto MOP 53/2020 para aguas superficiales (rios, canales, "
             "esteros). Si sacas agua de las dos formas, te aplican los dos."),
        ],
        "como_se_determina_el_estandar": {
            "regla": ("Por el caudal total sumado de todos los derechos que se ejercen en la MISMA obra "
                      "de captacion, no por cada derecho por separado."),
            "donde_estan_los_rangos": ("En la resolucion regional de tu zona. No hay rangos nacionales: "
                                       "el motor no puede asignarte el estandar sin ese documento."),
            "que_hacer_si_no_la_tienes": ("Buscala en dga.mop.gob.cl, seccion Monitoreo de Extracciones "
                                          "Efectivas, o preguntale a la DGA regional."),
        },
        "estandares_y_plazos": list(ESTANDARES_MEE.values()),
        "nota_sobre_los_plazos": ("Los plazos de instalacion y de inicio de transmision se cuentan desde "
                                  "la publicacion de la resolucion regional en el Diario Oficial."),
        "nota_sobre_las_frecuencias": ("Las frecuencias de medicion y los desfases maximos vienen de "
                                       "fuentes secundarias: confirmalos antes de comprometerlos."),
        "sistemas_de_medicion": SISTEMAS_DE_MEDICION,
        "sistemas_de_transmision": SISTEMAS_DE_TRANSMISION,
        "nota_sobre_el_flujometro": ("El flujometro no esta obligado a medir el caudal directamente: el "
                                     "caudal se puede deducir del volumen medido en un tiempo. Y la DGA "
                                     "no acredita proveedores ni certifica instaladores."),
        "lista_de_verificacion": PASOS_MEE,
        "sanciones": ("Multas en UTM, suspension del ejercicio del derecho y reduccion del caudal "
                      "autorizado. Ademas, desde la Ley 21.740 la DGA puede ordenar la paralizacion "
                      "inmediata de extracciones no autorizadas. Los montos exactos dependen del caso: "
                      "esto es orientacion, no una tasacion."),
        "donde_se_hace": "dga.mop.gob.cl, seccion Monitoreo de Extracciones Efectivas (software MEE)",
        "normas_aplicables": NORMAS_MEE,
        "lo_que_no_puedo_determinar": LO_QUE_EL_MOTOR_NO_PUEDE_DETERMINAR,
        "siguiente_paso": ("Confirma la resolucion regional de tu zona y el caudal total de la obra. Con "
                           "esos dos datos sabras que estandar te toca y desde cuando corren tus plazos."),
    }
    if estandar:
        resultado["estandar_consultado"] = dict(estandar)
        resultado["estandar_consultado"]["que_equipos_necesitas"] = SISTEMAS_DE_MEDICION.get(
            estandar["sistema_de_medicion"],
            "General o Basico: cualquiera de los dos sirve para el estandar Medio.")
    if caudal:
        resultado["caudal_declarado_l_s"] = caudal
    if region:
        resultado["region_declarada"] = region

    return Respuesta(resultado, advertencias=advertencias)


# --------------------------------------------------------------------------
# Accion: informe
# --------------------------------------------------------------------------

def _bloques_informe(resumen):
    zonas = resumen.get("zonas_estres_hidrico") or {}
    porcentajes = zonas.get("porcentaje") or {}
    pct_consumo = (porcentajes.get("consumo") or {}).get("si", 0)
    indicadores = resumen.get("indicadores_gri303") or {}

    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Extraccion", "valor": resumen.get("extraccion_megalitros", 0), "unidad": "ML",
             "detalle": "Toda el agua que entro (GRI 303-3)", "color": "verde"},
            {"etiqueta": "Descarga", "valor": resumen.get("descarga_megalitros", 0), "unidad": "ML",
             "detalle": "Agua devuelta (GRI 303-4)"},
            {"etiqueta": "Consumo", "valor": resumen.get("consumo_megalitros", 0), "unidad": "ML",
             "detalle": "Extraccion menos descarga (GRI 303-5)"},
            {"etiqueta": "Consumo en zonas de estres", "valor": pct_consumo, "unidad": "%",
             "detalle": "Es la parte que mas pesa",
             "color": "rojo" if pct_consumo >= 40 else "amarillo" if pct_consumo > 0 else "gris"},
        ]},
        {"tipo": "texto",
         "texto": ("Con el agua no basta el total: importa donde se usa. Un metro cubico consumido en una "
                   "cuenca con poca agua disponible pesa mucho mas que el mismo metro cubico en una "
                   "cuenca con agua de sobra. Por eso este informe separa siempre lo que ocurre en zonas "
                   "con estres hidrico.")},
        {"tipo": "texto",
         "texto": "Periodo: %s. Metodo de calculo del consumo: %s."
                  % (resumen.get("periodo", ""), resumen.get("formulas", {}).get(
                      "consumo", {}).get("formula", "extraccion menos descarga"))},
    ]

    por_origen = resumen.get("por_origen") or {}
    datos_origen = [{"etiqueta": datos.get("nombre", clave), "valor": datos.get("extraccion_m3", 0) / 1000.0}
                    for clave, datos in sorted(por_origen.items()) if datos.get("extraccion_m3")]
    if datos_origen:
        bloques.append({"tipo": "dona", "titulo": "De donde sale el agua (GRI 303-3)", "unidad": "ML",
                        "datos": datos_origen})

    por_sitio = resumen.get("por_sitio") or {}
    if por_sitio:
        ordenados = sorted(por_sitio.items(), key=lambda x: -x[1].get("consumo_m3", 0))
        bloques.append({"tipo": "barras", "titulo": "Consumo por sitio", "unidad": "ML",
                        "datos": [{"etiqueta": sitio, "valor": datos.get("consumo_m3", 0) / 1000.0}
                                  for sitio, datos in ordenados[:10]]})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Sitio", "Extraccion (ML)", "Descarga (ML)", "Consumo (ML)",
                                     "Zona de estres hidrico"],
                        "numericas": [1, 2, 3],
                        "filas": [[sitio,
                                   datos.get("extraccion_m3", 0) / 1000.0,
                                   datos.get("descarga_m3", 0) / 1000.0,
                                   datos.get("consumo_m3", 0) / 1000.0,
                                   datos.get("zona_estres_hidrico", "sin definir")]
                                  for sitio, datos in ordenados],
                        "nota": "Los volumenes van en megalitros: 1 ML = 1.000 m3."})

    por_destino = resumen.get("por_destino") or {}
    if por_destino:
        bloques.append({"tipo": "tabla", "columnas": ["A donde va el agua devuelta", "Descarga (ML)"],
                        "numericas": [1],
                        "filas": [[datos.get("nombre", clave), datos.get("descarga_m3", 0) / 1000.0]
                                  for clave, datos in sorted(por_destino.items())
                                  if datos.get("descarga_m3")],
                        "nota": "Divulgacion 303-4: el estandar pide decir a donde se devuelve el agua."})

    if indicadores:
        bloques.append({"tipo": "titulo", "texto": "Lo que pide el estandar de reporte (GRI 303)",
                        "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Divulgacion", "Total (ML)", "En zonas de estres (ML)", "Sin definir (ML)"],
                        "numericas": [1, 2, 3],
                        "filas": [[indicadores[clave]["titulo"],
                                   indicadores[clave]["total_megalitros"],
                                   indicadores[clave]["en_zonas_con_estres_hidrico_megalitros"],
                                   indicadores[clave]["sin_definir_megalitros"]]
                                  for clave in ("303-3", "303-4", "303-5") if clave in indicadores]})
        faltantes = []
        for clave in ("303-3", "303-4", "303-5"):
            for falta in (indicadores.get(clave) or {}).get("lo_que_falta", []):
                faltantes.append("%s: %s" % (clave, falta))
        if faltantes:
            bloques.append({"tipo": "titulo", "texto": "Lo que todavia falta para reportar completo",
                            "nivel": 3})
            bloques.append({"tipo": "lista", "items": faltantes})

    calidad = (resumen.get("calidad_datos") or {}).get("porcentaje") or {}
    bloques.extend([
        {"tipo": "titulo", "texto": "Calidad de los datos", "nivel": 2},
        {"tipo": "texto", "texto": ("Cuanto del agua extraida viene de un medidor o una boleta y cuanto de "
                                    "una estimacion. Para una auditoria conviene subir la parte medida.")},
        {"tipo": "barras", "titulo": "", "unidad": "%", "datos": [
            {"etiqueta": "Verificado", "valor": calidad.get("verificado", 0)},
            {"etiqueta": "Reportado", "valor": calidad.get("reportado", 0)},
            {"etiqueta": "Estimado", "valor": calidad.get("estimado", 0)},
        ]},
    ])

    if resumen.get("problemas"):
        bloques.append({"tipo": "titulo", "texto": "Filas que no se pudieron calcular", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Fila", "Que pasa", "Que hacer"],
                        "filas": [[p.get("fila"), p.get("error"), p.get("sugerencia")]
                                  for p in resumen["problemas"]]})

    dulce = resumen.get("desglose_agua_dulce_y_otras") or {}
    bloques.extend([
        {"tipo": "titulo", "texto": "Metodologia y fuentes", "nivel": 2},
        {"tipo": "lista", "items": [
            "Definiciones y desgloses: GRI 303: Agua y efluentes 2018 (divulgaciones 303-3, 303-4 y 303-5).",
            "Consumo: %s" % resumen.get("formulas", {}).get("consumo", {}).get(
                "formula", "extraccion menos descarga"),
            "Volumenes en megalitros: 1 ML = 1.000 m3.",
            ("Zonas con estres hidrico: las marca la empresa en la planilla. GRI 303 reconoce el WRI "
             "Aqueduct Water Risk Atlas y el WWF Water Risk Filter, y considera zona con estres la que "
             "tiene estres hidrico de referencia alto (40-80%) o extremadamente alto (mas de 80%)."),
            ("Huella de escasez (si se calculo aparte): metodo AWARE de WULCA, dentro del marco de "
             "ISO 14046:2014."),
        ]},
        {"tipo": "nota", "estilo": "aviso",
         "texto": "%s %s" % (dulce.get("que_pide_el_estandar", ""), dulce.get("que_hacer", ""))},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_APOYO},
    ])
    return bloques


def informe_html(opciones):
    """Arma el informe de agua en HTML a partir del ultimo calculo guardado."""
    perfil, ruta_empresa = _contexto(opciones)
    periodo = _valor(opciones, "periodo") or None
    origen = espacio.ruta_de(ruta_empresa, "resultados", _nombre_resultado(periodo))
    if not os.path.isfile(origen):
        raise Problema(
            "Todavia no hay un calculo de agua guardado%s." % (" para %s" % periodo if periodo else ""),
            "Primero ejecuta: agua calcular%s. Con ese resultado armo el informe."
            % (" --periodo %s" % periodo if periodo else ""),
        )
    with open(origen, encoding="utf-8") as archivo:
        resumen = json.load(archivo)

    destino = espacio.ruta_de(ruta_empresa, "reportes",
                              "huella-hidrica-%s.html" % (periodo or "completa"))
    informe.escribir_html(
        destino,
        "Huella hidrica y gestion del agua %s" % (periodo or ""),
        _bloques_informe(resumen),
        marca=perfil.get("marca") or {},
        subtitulo="%s - %s" % (perfil.get("nombre", ""),
                               perfil.get("sector", "") or "Agua, efluentes y escasez hidrica"),
    )
    return Respuesta({
        "mensaje": ("Informe listo: abrelo con doble clic y, si lo necesitas en PDF, imprimelo desde el "
                    "navegador con Ctrl+P."),
        "archivo": destino,
        "empresa": perfil.get("nombre"),
        "periodo": resumen.get("periodo"),
        "extraccion_megalitros": resumen.get("extraccion_megalitros"),
        "consumo_megalitros": resumen.get("consumo_megalitros"),
        "generado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }, advertencias=[AVISO_APOYO], fuentes=[motor_agua.FUENTE_GRI303])


ACCIONES = {"calcular": calcular, "escasez": escasez, "dga": dga, "informe": informe_html}
