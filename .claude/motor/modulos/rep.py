# -*- coding: utf-8 -*-
"""Ley REP (Ley 20.920): metas por producto prioritario, cumplimiento y obligaciones."""

import datetime
import json
import os

from calculos import rep as motor_rep
from nucleo import espacio, excel
from nucleo.salida import Problema, Respuesta

AYUDA = ("Ley REP (Ley 20.920 de Chile): consulta las metas de cada producto prioritario, calcula el "
         "cumplimiento con las toneladas de la empresa y lista que hay que declarar y cuando.")

PLANILLA = "rep.xlsx"

AVISO_LEGAL = ("Orientacion de apoyo, no asesoria legal. Las metas y los plazos salen de los decretos "
               "citados en cada resultado; antes de declarar ante el Ministerio del Medio Ambiente o la "
               "Superintendencia, confirmalo con tu sistema de gestion o tu asesoria.")

AVISO_SISTEMA = ("Las obligaciones de la REP se cumplen a traves de un sistema de gestion, individual o "
                 "colectivo (art. 19 de la Ley 20.920). Si la empresa esta en un sistema colectivo, casi "
                 "siempre es el sistema el que declara y acredita las toneladas: este calculo sirve para "
                 "revisar lo que el sistema informa, no para reemplazarlo.")

AVISO_ACEITES = ("La tabla de metas de aceites lubricantes (art. 21 del DS 47/2023) no esta verificada: en el "
                 "Diario Oficial se publico como imagen. Por eso el motor calcula el porcentaje logrado pero "
                 "NO dice si se cumple. Pide el porcentaje oficial al MMA o a tu sistema de gestion.")


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def _nombres_de_productos():
    return ", ".join(p["producto"] for p in motor_rep.productos_prioritarios())


def _leer_declaraciones(ruta_empresa):
    """Lee la planilla rep.xlsx de la empresa."""
    ruta = espacio.ruta_de(ruta_empresa, "datos", PLANILLA)
    if not os.path.isfile(ruta):
        raise Problema(
            "No encontre la planilla de la Ley REP (%s) en la carpeta de la empresa." % PLANILLA,
            "La creo vacia con: plantilla crear --tipo rep. Despues la llenas en Excel con las toneladas "
            "puestas en el mercado cada anio y me avisas.",
        )
    tabla = excel.leer_tabla(ruta)
    if not tabla["filas"]:
        raise Problema(
            "La planilla %s esta sin datos." % PLANILLA,
            "Abrela en Excel y escribe una fila por anio, producto, categoria y material, con las "
            "toneladas puestas en el mercado, recolectadas y valorizadas.",
        )
    return tabla["filas"], ruta


def _anio_pedido(opciones, perfil, advertencias):
    crudo = _valor(opciones, "anio")
    if crudo:
        return motor_rep.anio_valido(crudo)
    periodo = str(perfil.get("periodo_actual") or "").strip()
    if periodo[:4].isdigit():
        advertencias.append("No me dijiste el anio: use %s, que es el periodo actual de la empresa."
                            % periodo[:4])
        return int(periodo[:4])
    anio = datetime.date.today().year
    advertencias.append("No me dijiste el anio: use %d. Si querias otro, indicalo con --anio." % anio)
    return anio


def _resumir_meta(meta):
    partes = [p for p in (meta["categoria_nombre"] or meta["categoria"].replace("_", " "),
                          meta["material_nombre"] or meta["material"].replace("_", " ")) if p]
    etiqueta = " - ".join(partes) if partes else "meta unica del producto"
    if meta["sin_meta_este_anio"]:
        return "%s: sin meta este anio (%s)." % (etiqueta, meta["articulo"])
    if meta["meta_recoleccion_pct"] == meta["meta_valorizacion_pct"]:
        return "%s: %s%% de recoleccion y valorizacion (%s)." % (
            etiqueta, motor_rep.formatear_numero(meta["meta_valorizacion_pct"]), meta["articulo"])
    return "%s: %s%% de recoleccion y %s%% de valorizacion (%s)." % (
        etiqueta, motor_rep.formatear_numero(meta["meta_recoleccion_pct"]),
        motor_rep.formatear_numero(meta["meta_valorizacion_pct"]), meta["articulo"])


# --------------------------------------------------------------------------
# Accion: metas
# --------------------------------------------------------------------------

def metas(opciones):
    """Que porcentaje exige el decreto para un producto prioritario en un anio."""
    producto = _valor(opciones, "producto")
    if not producto:
        raise Problema(
            "Falta decirme de que producto prioritario quieres las metas.",
            "Productos de la Ley REP: %s. Por ejemplo: rep metas --producto envases --anio 2026."
            % _nombres_de_productos(),
        )
    anio = _valor(opciones, "anio") or datetime.date.today().year
    datos = motor_rep.metas_de(producto, anio,
                               material=_valor(opciones, "material") or None,
                               categoria=_valor(opciones, "categoria") or None)

    advertencias = [AVISO_LEGAL] + list(datos["advertencias"])
    if datos["producto"] == "aceites_lubricantes":
        advertencias.insert(1, AVISO_ACEITES)

    resultado = {
        "producto": datos["producto"],
        "nombre": datos["nombre"],
        "anio": datos["anio"],
        "decreto": datos["decreto"] or "sin decreto de metas publicado",
        "metas_vigentes_desde": datos["metas_vigentes_desde"] or "todavia no rigen metas",
        "hay_metas": datos["hay_metas"],
        "metas": datos["metas"],
        "en_palabras": [_resumir_meta(m) for m in datos["metas"]],
        "formula": datos["formula"],
        "articulo_de_la_formula": datos["articulo_formula"],
        "como_se_calcula_el_denominador": datos["como_se_calcula_el_denominador"],
        "anios_que_usa_el_denominador": datos["anios_base"],
    }
    if not datos["hay_metas"]:
        resultado["que_pasa"] = datos["motivo"]
        resultado["que_hacer"] = datos["que_hacer"]
        resultado["en_palabras"] = [datos["motivo"]] + ([datos["que_hacer"]] if datos["que_hacer"] else [])
    return Respuesta(resultado, advertencias=advertencias, fuentes=datos["fuentes"])


# --------------------------------------------------------------------------
# Accion: calcular
# --------------------------------------------------------------------------

def _productos_de_la_planilla(filas):
    """Productos prioritarios que aparecen en la planilla, sin repetir."""
    encontrados = []
    for fila in filas:
        registro = motor_rep.normalizar_declaracion(fila)
        if registro["producto"] not in encontrados:
            encontrados.append(registro["producto"])
    return encontrados


def calcular(opciones):
    """Compara las toneladas de la planilla con la meta que fija el decreto."""
    perfil, ruta_empresa = _contexto(opciones)
    advertencias = []
    filas, archivo = _leer_declaraciones(ruta_empresa)
    anio = _anio_pedido(opciones, perfil, advertencias)

    pedido = _valor(opciones, "producto")
    if pedido:
        productos = [motor_rep.normalizar_producto(pedido)]
    else:
        productos = _productos_de_la_planilla(filas)
        if not productos:
            raise Problema(
                "En la planilla %s no hay ningun producto prioritario reconocible." % PLANILLA,
                "Revisa la columna «Producto prioritario»: debe decir %s." % _nombres_de_productos(),
            )

    calculos = []
    for clave in productos:
        calculo = motor_rep.calcular_cumplimiento(
            filas, anio, clave,
            categoria=_valor(opciones, "categoria") or None,
            material=_valor(opciones, "material") or None)
        calculos.append(calculo)
        advertencias.extend(calculo["advertencias"])
        if clave == "aceites_lubricantes":
            advertencias.append(AVISO_ACEITES)

    total = {
        "metas_evaluadas": sum(c["resumen"]["metas_evaluadas"] for c in calculos),
        "cumple": sum(c["resumen"]["cumple"] for c in calculos),
        "no_cumple": sum(c["resumen"]["no_cumple"] for c in calculos),
        "sin_meta": sum(c["resumen"]["sin_meta"] for c in calculos),
        "sin_datos": sum(c["resumen"]["sin_datos"] for c in calculos),
        "brecha_total_t": round(sum(c["resumen"]["brecha_total_t"] for c in calculos), 4),
    }
    if total["no_cumple"]:
        mensaje = ("Con los datos cargados se cumplen %d de %d metas del anio %d. %s sin cumplir, con una "
                   "brecha de %s toneladas."
                   % (total["cumple"], total["metas_evaluadas"], anio,
                      "Queda 1 meta" if total["no_cumple"] == 1 else "Quedan %d metas" % total["no_cumple"],
                      motor_rep.formatear_numero(total["brecha_total_t"])))
    elif total["metas_evaluadas"]:
        mensaje = ("Con los datos cargados se cumplen las %d metas evaluadas del anio %d."
                   % (total["cumple"], anio)) if total["cumple"] else \
            ("No pude evaluar ninguna meta del anio %d: revisa los avisos." % anio)
    else:
        mensaje = ("No hay metas que evaluar para %s en %d. Revisa los avisos: puede que las metas todavia "
                   "no rijan o que falten toneladas por declarar."
                   % (", ".join(productos), anio))

    resumen = {
        "empresa": perfil.get("nombre"),
        "anio": anio,
        "planilla": archivo,
        "mensaje": mensaje,
        "total": total,
        "productos": [{
            "producto": c["producto"], "nombre": c["producto_nombre"], "decreto": c["decreto"],
            "metas_vigentes_desde": c["metas_vigentes_desde"], "formula": c["formula"],
            "resumen": c["resumen"], "items": c["items"],
            "metas_sin_declarar": c["metas_sin_declarar"],
            "que_pasa": c["motivo"], "que_hacer": c["que_hacer"],
        } for c in calculos],
        "calculado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }

    destino = espacio.ruta_de(ruta_empresa, "resultados", "rep_%d.json" % anio)
    with open(destino, "w", encoding="utf-8") as salida:
        json.dump(resumen, salida, ensure_ascii=False, indent=2, default=str)
    resumen["resultado_guardado_en"] = destino

    fuentes = sorted({f for c in calculos for f in c["fuentes"]})
    return Respuesta(resumen, advertencias=[AVISO_LEGAL, AVISO_SISTEMA] + sorted(set(advertencias)),
                     fuentes=fuentes)


# --------------------------------------------------------------------------
# Accion: obligaciones
# --------------------------------------------------------------------------

def _umbral_de_envases(filas, advertencias):
    """Revisa el umbral de 300 kilos al anio de los arts. 7 y 10 del DS 12/2020."""
    if filas is None:
        return None
    por_anio = {}
    for fila in filas:
        registro = motor_rep.normalizar_declaracion(fila)
        if registro["producto"] != "envases":
            continue
        por_anio[registro["anio"]] = por_anio.get(registro["anio"], 0.0) + registro["puestas"]
    con_toneladas = [a for a, valor in por_anio.items() if valor > 0]
    if not con_toneladas:
        return None
    anio = max(con_toneladas)
    toneladas = por_anio[anio]
    bajo_umbral = toneladas < 0.3
    if bajo_umbral:
        advertencias.append(
            "Segun la planilla, en %d la empresa puso %s toneladas de envases en el mercado, menos de los "
            "300 kilogramos del art. 7 del DS 12/2020: no queda obligada a cumplir metas, pero SI a "
            "informar cada anio (art. 10)." % (anio, motor_rep.formatear_numero(toneladas)))
    return {"anio": anio, "toneladas": round(toneladas, 4), "umbral_t": 0.3,
            "bajo_el_umbral": bajo_umbral,
            "articulo": "Arts. 7 y 10 del DS 12/2020"}


def obligaciones(opciones):
    """Que le aplica a esta empresa, que debe declarar y cuando."""
    perfil, ruta_empresa = _contexto(opciones)
    advertencias = [AVISO_LEGAL, AVISO_SISTEMA]

    pais = (perfil.get("pais") or "").upper()
    if pais and pais != "CL":
        advertencias.append(
            "La Ley REP que conozco es la chilena (Ley 20.920) y esta empresa esta registrada en %s. "
            "Lo de abajo le aplica solo si tambien introduce productos en el mercado chileno; para %s no "
            "tengo cargada la normativa equivalente." % (pais, pais))

    filas = None
    ruta_planilla = espacio.ruta_de(ruta_empresa, "datos", PLANILLA)
    if os.path.isfile(ruta_planilla):
        filas = excel.leer_tabla(ruta_planilla)["filas"]

    pedido = _valor(opciones, "producto")
    if pedido:
        claves = [motor_rep.normalizar_producto(p.strip()) for p in str(pedido).split(",") if p.strip()]
    elif filas:
        claves = _productos_de_la_planilla(filas)
    else:
        claves = [p["producto"] for p in motor_rep.productos_prioritarios()]
        advertencias.append(
            "No me dijiste que productos vende o importa la empresa y todavia no hay planilla cargada, "
            "asi que te muestro los seis productos prioritarios. Dime cual es el suyo con --producto y "
            "te dejo solo lo que le aplica.")

    hoy = datetime.date.today()
    catalogo = {p["producto"]: p for p in motor_rep.productos_prioritarios()}
    productos = []
    for clave in claves:
        ficha = catalogo[clave]
        info = motor_rep.PRODUCTOS[clave]
        if not info["tabla"]:
            estado = info["motivo_sin_tabla"]
            que_declarar = info["que_hacer_sin_tabla"]
        elif info["primer_anio_metas"] and hoy.year < info["primer_anio_metas"]:
            estado = ("Las metas del %s todavia no rigen: empiezan el %s."
                      % (info["decreto"], info["metas_desde"]))
            que_declarar = ("Mientras tanto hay que declarar cada anio las toneladas puestas en el mercado "
                            "(art. 2 transitorio de la Ley 20.920).")
        else:
            estado = ("Las metas del %s rigen desde el %s: este anio hay meta que cumplir."
                      % (info["decreto"], info["metas_desde"]))
            que_declarar = ("Hay que declarar las toneladas puestas en el mercado y acreditar las "
                            "recolectadas y valorizadas, directamente si el sistema es individual o a "
                            "traves del sistema colectivo (art. 11 de la Ley 20.920).")
        productos.append({
            "producto": clave,
            "nombre": ficha["nombre"],
            "letra_articulo_10": ficha["letra_articulo_10"],
            "decreto": ficha["decreto"],
            "metas_vigentes_desde": ficha["metas_vigentes_desde"],
            "estado_hoy": estado,
            "que_declarar": que_declarar,
            "exenciones": ficha["exenciones"],
            "como_se_valoriza": ficha["como_se_valoriza"],
        })

    if str(perfil.get("tamano", "")).lower() == "micro":
        advertencias.append(
            "El perfil dice que la empresa es micro. Si califica como microempresa segun la Ley 20.416 "
            "(ese es el criterio legal, no el tamano declarado aqui), queda fuera de la REP de envases "
            "(art. 7 del DS 12/2020) y fuera de las metas de pilas y AEE (art. 6 del DS 22/2025), aunque "
            "en pilas y AEE igual debe informar (art. 9). Conviene confirmarlo con la asesoria contable.")

    umbral = None
    if any(p["producto"] == "envases" for p in productos):
        umbral = _umbral_de_envases(filas, advertencias)
    if any(p["producto"] == "aceites_lubricantes" for p in productos):
        advertencias.append(
            "El umbral de aceites lubricantes esta en litros (66 litros al anio, art. 5 del DS 47/2023) y "
            "la planilla esta en toneladas. No puedo convertirlo sin la densidad del aceite, asi que ese "
            "umbral revisalo tu con las facturas.")

    sin_fecha_fija = [p for p in motor_rep.PLAZOS_ANUALES if not p.get("verificado")]
    for plazo in sin_fecha_fija:
        advertencias.append(plazo.get("nota", ""))

    resultado = {
        "empresa": perfil.get("nombre"),
        "pais": pais or "sin pais en el perfil",
        "ley": motor_rep.LEY,
        "quien_es_productor": motor_rep.DEFINICION_PRODUCTOR,
        "productos_que_le_aplican": productos,
        "obligaciones_del_productor": motor_rep.OBLIGACIONES_DEL_PRODUCTOR,
        "calendario_anual": motor_rep.PLAZOS_ANUALES,
        "donde_se_declara": motor_rep.VENTANILLA_UNICA,
        "sanciones": motor_rep.SANCIONES,
        "umbral_de_envases": umbral,
        "siguiente_paso": ("Si la empresa introduce alguno de estos productos en Chile y todavia no esta "
                           "inscrita en la Ventanilla Unica del RETC ni adherida a un sistema de gestion, "
                           "eso es lo primero: sin sistema de gestion no hay forma de cumplir las metas."),
    }
    return Respuesta(resultado, advertencias=[a for a in advertencias if a])


ACCIONES = {"metas": metas, "calcular": calcular, "obligaciones": obligaciones}
