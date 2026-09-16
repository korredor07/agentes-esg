# -*- coding: utf-8 -*-
"""Activos fijos: vida util del SII, depreciacion, correccion monetaria y cartera."""

import json
import os

from calculos import activos as motor_activos
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta

AYUDA = ("Activos fijos en Chile: busca la vida util que fija el SII, calcula la depreciacion normal o "
         "acelerada, aplica la correccion monetaria y resume la cartera (inversion, depreciacion del "
         "ejercicio y valor libro).")

PLANILLA = "activos_fijos.xlsx"
HOJA = "Activos"

AVISO_LEGAL = ("Esto es apoyo de gestion, no asesoria tributaria ni contable. La vida util y las formulas "
               "salen de la tabla y de los articulos citados en cada resultado, pero la decision de que "
               "regimen usar y como declarar la toma la empresa con su contador.")

AVISO_ESG = ("Saber la antiguedad de cada equipo permite planificar su reemplazo: cuando un activo llega al "
             "final de su vida util es el momento natural para cambiarlo por uno mas eficiente, y ese "
             "recambio es la base del plan de reduccion de emisiones.")

# Columnas de la planilla datos/activos_fijos.xlsx. El titulo es lo que ve la
# persona en Excel; el motor lo lee normalizado (nucleo.excel.leer_tabla).
COLUMNAS = [
    {"titulo": "Nombre del activo", "ancho": 30,
     "ayuda": "Como le dicen en la empresa. Ej: Camioneta Hilux PPU ABCD-12."},
    {"titulo": "Bien segun la tabla del SII", "ancho": 30,
     "ayuda": "En palabras simples: camioneta, computador, galpon, camara de frio, maquinaria, tractor. "
              "Con esto busco la vida util en la tabla del SII."},
    {"titulo": "Actividad", "ancho": 14,
     "ayuda": "generico (por defecto) o agricola, si el bien esta en la nomina agricola del SII."},
    {"titulo": "Categoria", "ancho": 18,
     "ayuda": "Agrupacion tuya para los totales: flota, edificios, equipos, oficina."},
    {"titulo": "Sitio", "ancho": 20,
     "ayuda": "Donde esta el activo. Usa el mismo nombre que en la planilla de sitios."},
    {"titulo": "Fecha de compra", "ancho": 16, "ayuda": "AAAA-MM-DD. Ej: 2023-05-10."},
    {"titulo": "Fecha de puesta en uso", "ancho": 20,
     "ayuda": "Cuando el bien empezo a usarse en la empresa. Si se uso desde la compra, dejala vacia. "
              "La depreciacion parte desde el uso, no desde la compra."},
    {"titulo": "Valor de compra", "ancho": 18,
     "ayuda": "En pesos, sin el IVA que la empresa recupera. Solo el numero."},
    {"titulo": "Condicion", "ancho": 14,
     "ayuda": "nuevo, usado o importado. La depreciacion acelerada solo corre para bienes nuevos o importados."},
    {"titulo": "Metodo", "ancho": 14,
     "ayuda": "normal (por defecto), acelerada, 5_bis o propyme. Consultalo con tu contador."},
    {"titulo": "Vida util normal (anos)", "ancho": 20,
     "ayuda": "Dejala vacia y la busco en la tabla del SII. Llenala solo si tu contador indica otra."},
    {"titulo": "Estado", "ancho": 14,
     "ayuda": "en uso (por defecto), vendido o dado de baja. Los vendidos y dados de baja no se suman."},
    {"titulo": "Notas", "ancho": 28, "ayuda": "Lo que quieras recordar de ese activo."},
]

EJEMPLO = [
    ["Camioneta Hilux PPU ABCD-12", "camioneta", "generico", "flota", "Planta Chillan",
     "2023-05-10", "", 18500000, "nuevo", "normal", "", "en uso", ""],
    ["Camara de frio bodega 2", "camara de frio", "generico", "equipos", "Planta Chillan",
     "2021-03-01", "", 24000000, "nuevo", "acelerada", "", "en uso", "Refrigeracion de producto terminado"],
    ["Notebooks administracion (5)", "computador", "generico", "oficina", "Oficina central",
     "2024-08-20", "", 3750000, "nuevo", "normal", "", "en uso", ""],
]


# --------------------------------------------------------------------------
# Apoyo
# --------------------------------------------------------------------------

def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _valor(opciones, clave, por_defecto=None):
    """Valor de una opcion. La marca True es una opcion escrita sin valor."""
    valor = opciones.get(clave)
    if valor is None or valor is True or (isinstance(valor, str) and not valor.strip()):
        return por_defecto
    return valor


def _crear_planilla(ruta):
    """Escribe la planilla vacia de activos fijos, con sus instrucciones."""
    instrucciones = [
        ["Para que sirve esta planilla"],
        ["Anotar cada bien que la empresa usa por anios (vehiculos, maquinas, equipos, construcciones) "
         "para calcular su depreciacion y saber con que valor queda en los libros."],
        [""],
        ["Como llenarla"],
        ["1. Una fila por activo. No cambies los titulos de las columnas."],
        ["2. Borra las filas de ejemplo cuando ya no las necesites."],
        ["3. Si no sabes la vida util, dejala vacia: la busco en la tabla del SII."],
        ["4. Los terrenos no se deprecian: si compraste un inmueble, anota solo el valor de la construccion."],
        ["5. Guarda el archivo y avisale al asistente."],
        [""],
        ["Que significa cada columna"],
    ]
    for columna in COLUMNAS:
        instrucciones.append(["%s: %s" % (columna["titulo"], columna.get("ayuda", ""))])
    hojas = [
        {"nombre": "Instrucciones",
         "columnas": [{"titulo": "Activos fijos y depreciacion", "ancho": 110}],
         "filas": [{"valores": fila, "estilo": excel.ESTILO_TEXTO_LARGO} for fila in instrucciones],
         "congelar": False},
        {"nombre": HOJA, "columnas": COLUMNAS, "filas": [list(fila) for fila in EJEMPLO]},
    ]
    return excel.escribir_xlsx(ruta, hojas)


def _ruta_planilla(ruta_empresa):
    return espacio.ruta_de(ruta_empresa, "datos", PLANILLA)


def _leer_planilla(ruta_empresa):
    """Devuelve las filas de la planilla. Si no existe, la crea vacia y lo explica."""
    ruta = _ruta_planilla(ruta_empresa)
    if not os.path.isfile(ruta):
        _crear_planilla(ruta)
        raise Problema(
            "Todavia no tenias la planilla de activos fijos, asi que la acabo de crear en %s." % ruta,
            "Abrela en Excel, reemplaza las filas de ejemplo por los activos de la empresa (que es, cuanto "
            "costo y desde cuando se usa), guardala y avisame para calcular.",
            {"archivo": ruta, "columnas": [c["titulo"] for c in COLUMNAS]},
        )
    tabla = excel.leer_tabla(ruta, hoja=HOJA)
    if not tabla["filas"]:
        raise Problema(
            "La planilla de activos fijos esta sin datos.",
            "Abrela en Excel y escribe una fila por cada bien: nombre, que es, cuanto costo y desde cuando "
            "se usa.",
            {"archivo": ruta},
        )
    return tabla["filas"], ruta


def _activo_desde_fila(fila):
    """Traduce una fila de la planilla a lo que espera el motor de calculo."""
    return {
        "nombre": fila.get("nombre_del_activo") or fila.get("nombre"),
        "bien": fila.get("bien_segun_la_tabla_del_sii") or fila.get("bien"),
        "actividad": fila.get("actividad"),
        "categoria": fila.get("categoria"),
        "sitio": fila.get("sitio"),
        "fecha_compra": fila.get("fecha_de_compra"),
        "fecha_uso": fila.get("fecha_de_puesta_en_uso"),
        "valor": fila.get("valor_de_compra") or fila.get("valor"),
        "condicion": fila.get("condicion"),
        "metodo": fila.get("metodo") or "normal",
        "vida_util_normal": fila.get("vida_util_normal_anos") or fila.get("vida_util_normal"),
        "estado": fila.get("estado"),
        "notas": fila.get("notas"),
        "_fila": fila.get("_fila"),
    }


def _vida_util_pedida(opciones):
    """Resuelve cuantos anios usar: los que indicaron o los de la tabla del SII."""
    indicada = _valor(opciones, "vida_util") or _valor(opciones, "vida_util_normal")
    if indicada not in (None, ""):
        return motor_activos.entero(indicada, "la vida util", "Escribe los anios, por ejemplo 7."), None
    bien = _valor(opciones, "bien")
    if not bien:
        raise Problema(
            "No se en cuantos anios se deprecia este bien.",
            "Dime que es con --bien (por ejemplo --bien camioneta) y lo busco en la tabla del SII, o "
            "indicame los anios con --vida-util 7.",
        )
    busqueda = motor_activos.buscar_vida_util(bien, _valor(opciones, "actividad"))
    if not busqueda["encontrado"]:
        raise Problema(busqueda["mensaje"],
                       "Tambien puedes indicarme los anios directamente con --vida-util.",
                       {"consulta": bien})
    elegido = busqueda["eleccion_unica"]
    if not elegido or elegido["vida_util_normal"] is None:
        opciones_texto = "; ".join("%s (%s anios)" % (c["bien"], c["vida_util_normal"])
                                   for c in busqueda["coincidencias"])
        raise Problema(
            "«%s» calza con mas de una fila de la tabla del SII y no voy a elegir por ti." % bien,
            "Opciones: %s. Vuelve a pedirmelo con --vida-util y los anios que correspondan."
            % opciones_texto,
            {"coincidencias": busqueda["coincidencias"]},
        )
    return elegido["vida_util_normal"], elegido


# --------------------------------------------------------------------------
# Accion: vida-util
# --------------------------------------------------------------------------

def vida_util(opciones):
    """En cuantos anios se deprecia un bien, segun la tabla del SII."""
    bien = _valor(opciones, "bien") or _valor(opciones, "descripcion")
    if not bien:
        raise Problema(
            "Falta decirme que bien quieres consultar.",
            "Escribelo como lo dirias normalmente. Por ejemplo: activos vida-util --bien camioneta.",
        )
    resultado = motor_activos.buscar_vida_util(bien, _valor(opciones, "actividad"))
    advertencias = list(resultado.pop("advertencias", []))
    advertencias.append(AVISO_LEGAL)
    return Respuesta(resultado, advertencias=advertencias,
                     fuentes=[motor_activos.FUENTE_VIDA_UTIL])


# --------------------------------------------------------------------------
# Accion: depreciar
# --------------------------------------------------------------------------

def _correccion_para(resultado, opciones, valor, anio_inicio, mes_inicio):
    """Actualiza el valor del bien por correccion monetaria, si lo piden."""
    pedido = opciones.get("correccion", opciones.get("corregir"))
    if pedido in (None, False, ""):
        return None
    anio = pedido if pedido is not True else None
    ejercicio = anio or (resultado.get("anio_inicio") or None)
    if not ejercicio:
        raise Problema(
            "Para la correccion monetaria necesito saber que ejercicio estas cerrando.",
            "Indicalo asi: --correccion 2025.",
        )
    return motor_activos.correccion_monetaria(
        valor, ejercicio,
        mes_adquisicion=mes_inicio, anio_adquisicion=anio_inicio,
        porcentaje=_valor(opciones, "porcentaje"))


def _depreciar_uno(opciones):
    valor = _valor(opciones, "valor")
    anios, elegido = _vida_util_pedida(opciones)
    anio_inicio = _valor(opciones, "anio_inicio") or _valor(opciones, "anio")
    mes_inicio = _valor(opciones, "mes_inicio") or _valor(opciones, "mes") or 1
    resultado = motor_activos.depreciacion(
        valor, anios,
        metodo=_valor(opciones, "metodo") or "normal",
        anio_inicio=anio_inicio,
        mes_inicio=mes_inicio,
        valor_residual=_valor(opciones, "valor_residual"),
        ingresos_uf=_valor(opciones, "ingresos_uf"),
        bien=_valor(opciones, "bien"))
    if elegido:
        resultado["vida_util_segun"] = "%s (%s), %s" % (elegido["bien"], elegido["codigo"],
                                                        elegido["resolucion"])
        resultado["codigo_sii"] = elegido["codigo"]
    else:
        resultado["vida_util_segun"] = "anios indicados por ti"

    advertencias = list(resultado.pop("advertencias", []))
    correccion = _correccion_para(resultado, opciones, resultado["valor"],
                                  resultado.get("anio_inicio"), resultado.get("mes_inicio"))
    if correccion:
        advertencias.extend(correccion.pop("advertencias", []))
        advertencias.append(
            "La correccion monetaria se aplico al valor de compra. En la declaracion se actualiza cada anio "
            "el valor neto del bien (valor menos depreciacion acumulada) y sobre ese valor se calcula la cuota.")
        resultado["correccion_monetaria"] = correccion
    advertencias.append(AVISO_LEGAL)
    return Respuesta(resultado, advertencias=advertencias,
                     fuentes=[motor_activos.FUENTE_VIDA_UTIL, motor_activos.FUENTE_CORRECCION])


def _depreciar_planilla(opciones):
    perfil, ruta_empresa = _contexto(opciones)
    filas, archivo = _leer_planilla(ruta_empresa)
    advertencias = []
    calculados = []
    con_problema = []
    for fila in filas:
        activo = _activo_desde_fila(fila)
        nombre = activo.get("nombre") or activo.get("bien") or "fila %s" % activo.get("_fila")
        anios, origen, motivo = motor_activos.vida_util_del_activo(activo, advertencias)
        if motivo:
            con_problema.append({"activo": nombre, "fila": activo.get("_fila"), "motivo": motivo})
            continue
        anio_inicio, mes_inicio = motor_activos.anio_y_mes_de_uso(activo)
        try:
            detalle = motor_activos.depreciacion(
                activo.get("valor"), anios, metodo=activo.get("metodo") or "normal",
                anio_inicio=anio_inicio, mes_inicio=mes_inicio, bien=activo.get("bien"))
        except Problema as problema:
            con_problema.append({"activo": nombre, "fila": activo.get("_fila"),
                                 "motivo": problema.mensaje})
            continue
        detalle["activo"] = nombre
        detalle["fila"] = activo.get("_fila")
        detalle["vida_util_segun"] = origen
        advertencias.extend(a for a in detalle.pop("advertencias", []) if a not in advertencias)
        calculados.append(detalle)

    if not calculados:
        raise Problema(
            "No pude depreciar ninguna fila de la planilla.",
            "Revisa el motivo de cada fila y completa lo que falta.",
            {"activos_con_problema": con_problema, "archivo": archivo},
        )
    if con_problema:
        advertencias.append("Hay %d fila(s) que no pude calcular: revisa «activos_con_problema»."
                            % len(con_problema))
    advertencias.append(AVISO_LEGAL)
    return Respuesta({
        "empresa": perfil.get("nombre"),
        "archivo": archivo,
        "cantidad": len(calculados),
        "activos": calculados,
        "activos_con_problema": con_problema,
    }, advertencias=advertencias, fuentes=[motor_activos.FUENTE_VIDA_UTIL])


def depreciar(opciones):
    """Tabla de depreciacion de un activo o de todos los de la planilla."""
    if _valor(opciones, "valor") is not None:
        return _depreciar_uno(opciones)
    return _depreciar_planilla(opciones)


# --------------------------------------------------------------------------
# Accion: cartera
# --------------------------------------------------------------------------

def _resumen(opciones):
    perfil, ruta_empresa = _contexto(opciones)
    filas, archivo = _leer_planilla(ruta_empresa)
    anio = _valor(opciones, "anio") or _valor(opciones, "ejercicio") or perfil.get("periodo_actual")
    if anio and str(anio)[:4].isdigit():
        anio = int(str(anio)[:4])
    else:
        anio = None
    resultado = motor_activos.resumen_cartera([_activo_desde_fila(f) for f in filas], anio=anio)
    resultado["empresa"] = perfil.get("nombre")
    resultado["archivo"] = archivo

    if opciones.get("corregir") or opciones.get("correccion"):
        _agregar_correccion(resultado, _valor(opciones, "porcentaje"))
    return perfil, ruta_empresa, resultado


def _agregar_correccion(resultado, porcentaje=None):
    """Actualiza el valor de compra de cada activo por correccion monetaria."""
    ejercicio = resultado["ejercicio"]
    total = 0.0
    aviso = None
    for activo in resultado["activos"]:
        try:
            correccion = motor_activos.correccion_monetaria(
                activo["valor"], ejercicio,
                mes_adquisicion=activo["mes_inicio"], anio_adquisicion=activo["anio_inicio"],
                porcentaje=porcentaje)
        except Problema as problema:
            aviso = "%s %s" % (problema.mensaje, problema.sugerencia)
            break
        activo["valor_actualizado"] = correccion["valor_actualizado"]
        activo["factor_correccion"] = correccion["factor"]
        total += correccion["valor_actualizado"]
    if aviso:
        resultado["advertencias"].append(aviso)
    else:
        resultado["totales"]["inversion_actualizada"] = motor_activos.redondear(total)
        if porcentaje not in (None, ""):
            resultado["advertencias"].append(
                "Use el %s %% de correccion monetaria que me indicaste para todos los activos. Confirmalo "
                "con tu contador o con la tabla del SII antes de usarlo en una declaracion." % porcentaje)
        resultado["advertencias"].append(
            "El valor de compra de cada activo quedo actualizado al 31 de diciembre de %d (%s). En la "
            "declaracion se actualiza el valor neto y sobre ese valor se calcula la cuota del ejercicio."
            % (ejercicio, motor_activos.FUENTE_CORRECCION))


def cartera(opciones):
    """Resumen de la cartera: inversion, depreciacion del ejercicio y valor libro."""
    perfil, ruta_empresa, resultado = _resumen(opciones)
    destino = espacio.ruta_de(ruta_empresa, "resultados", "activos_%s.json" % resultado["ejercicio"])
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=2)
    resultado["resultado_guardado_en"] = destino
    advertencias = list(resultado.pop("advertencias", []))
    advertencias.append(AVISO_ESG)
    advertencias.append(AVISO_LEGAL)
    return Respuesta(resultado, advertencias=advertencias,
                     fuentes=[motor_activos.FUENTE_VIDA_UTIL])


# --------------------------------------------------------------------------
# Accion: informe
# --------------------------------------------------------------------------

def _bloques(resultado):
    totales = resultado["totales"]
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Inversion total", "valor": totales["inversion"], "unidad": "$",
             "detalle": "%d activos en uso" % resultado["cantidad"]},
            {"etiqueta": "Depreciacion del ejercicio", "valor": totales["depreciacion_del_ejercicio"],
             "unidad": "$", "detalle": "Ano %s" % resultado["ejercicio"]},
            {"etiqueta": "Valor libro", "valor": totales["valor_libro"], "unidad": "$",
             "detalle": "Lo que queda por depreciar", "color": "verde"},
            {"etiqueta": "Depreciado", "valor": totales["porcentaje_depreciado"], "unidad": "%",
             "detalle": "Del valor de compra",
             "color": "amarillo" if totales["porcentaje_depreciado"] >= 70 else "verde"},
        ]},
        {"tipo": "titulo", "texto": "Inversion por categoria", "nivel": 2},
        {"tipo": "barras", "titulo": "Valor de compra por categoria", "unidad": "$",
         "datos": [{"etiqueta": grupo["categoria"], "valor": grupo["inversion"]}
                   for grupo in resultado["por_categoria"]]},
        {"tipo": "titulo", "texto": "Detalle de los activos", "nivel": 2},
        {"tipo": "tabla",
         "columnas": ["Activo", "Categoria", "En uso desde", "Metodo", "Vida util (anos)",
                      "Valor de compra", "Depreciacion del ejercicio", "Valor libro"],
         "numericas": [4, 5, 6, 7],
         "filas": [[a["activo"], a["categoria"], a["en_uso_desde"], a["metodo"], a["vida_util_aplicada"],
                    a["valor"], a["depreciacion_del_ejercicio"], a["valor_libro"]]
                   for a in resultado["activos"]],
         "nota": "La vida util sale de la tabla del SII (%s), salvo las filas donde indicaste otra."
                 % motor_activos.FUENTE_VIDA_UTIL},
    ]

    if resultado["renovacion"]:
        bloques.append({"tipo": "titulo", "texto": "Equipos a evaluar para reemplazo", "nivel": 2})
        bloques.append({"tipo": "semaforo", "items": [
            {"etiqueta": activo["activo"],
             "estado": "rojo" if activo["vida_util_terminada"] else "amarillo",
             "estado_texto": "Vida util cumplida" if activo["vida_util_terminada"] else "Por cumplir",
             "detalle": "%d anos de uso; quedan %s anos de vida util. Valor libro: %s."
                        % (activo["anios_de_uso"],
                           activo["anios_restantes"] if activo["anios_restantes"] is not None else "?",
                           informe.formatear_numero(activo["valor_libro"]))}
            for activo in resultado["renovacion"]]})
        bloques.append({"tipo": "nota", "estilo": "info", "texto": AVISO_ESG})

    if resultado.get("activos_con_problema"):
        bloques.append({"tipo": "titulo", "texto": "Filas que no pude calcular", "nivel": 2})
        bloques.append({"tipo": "lista", "items": [
            "%s: %s" % (problema["activo"], problema["motivo"])
            for problema in resultado["activos_con_problema"]]})

    bloques.append({"tipo": "nota", "estilo": "aviso", "texto": AVISO_LEGAL})
    return bloques


def informe_html(opciones):
    """Informe HTML de la cartera de activos fijos."""
    perfil, ruta_empresa, resultado = _resumen(opciones)
    destino = espacio.ruta_de(ruta_empresa, "reportes", "activos-fijos-%s.html" % resultado["ejercicio"])
    informe.escribir_html(
        destino, "Activos fijos y depreciacion", _bloques(resultado),
        marca=perfil.get("marca") or {},
        subtitulo="%s - ejercicio %s" % (perfil.get("nombre", ""), resultado["ejercicio"]))
    return Respuesta({
        "mensaje": "Informe de activos fijos listo. Se abre con doble clic y se imprime a PDF con Ctrl+P.",
        "archivo": destino,
        "ejercicio": resultado["ejercicio"],
        "activos": resultado["cantidad"],
        "totales": resultado["totales"],
    }, advertencias=[AVISO_ESG, AVISO_LEGAL], fuentes=[motor_activos.FUENTE_VIDA_UTIL])


ACCIONES = {
    "vida-util": vida_util,
    "depreciar": depreciar,
    "cartera": cartera,
    "informe": informe_html,
}
