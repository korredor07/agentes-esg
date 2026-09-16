# -*- coding: utf-8 -*-
"""Cadena de frio: temperatura cinetica media, excursiones y limites legales."""

import json
import os

from calculos import frio as motor
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta

AYUDA = ("Revisa los registros de temperatura de la cadena de frio: temperatura cinetica media, "
         "excursiones fuera de rango y que exige la norma chilena para cada producto.")

ARCHIVO_DATOS = "temperaturas.xlsx"

COLUMNAS = ["Registro", "Fecha y hora", "Temperatura (C)", "Punto de medicion", "Producto", "Notas"]


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _valor(opciones, clave, por_defecto=None):
    valor = opciones.get(clave)
    if valor is None or valor is True:
        return por_defecto
    return valor


def _numero(opciones, clave, por_defecto=None):
    valor = _valor(opciones, clave)
    if valor is None:
        return por_defecto
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        raise Problema("«%s» no es un numero valido para --%s." % (valor, clave.replace("_", "-")),
                       "Escribe solo el numero, con punto o coma decimal.")


def _serie(opciones, ruta_empresa=None):
    """La serie de temperaturas: escrita en el comando o leida de la planilla."""
    crudo = _valor(opciones, "temperaturas")
    if crudo:
        if os.path.isfile(str(crudo)):
            with open(crudo, encoding="utf-8") as archivo:
                datos = json.load(archivo)
            return [float(t) for t in datos], "archivo %s" % crudo
        texto = str(crudo).replace(";", " ").replace(",", " ") if "." in str(crudo) \
            else str(crudo).replace(";", " ").replace(",", ".")
        piezas = [p for p in texto.replace("[", " ").replace("]", " ").split() if p]
        try:
            return [float(p) for p in piezas], "las lecturas que me diste"
        except ValueError:
            raise Problema(
                "No pude leer la serie de temperaturas.",
                'Escribelas separadas por espacios: --temperaturas "4.0 4.5 5.0 12.0". '
                "O cargalas en la planilla con: frio plantilla.",
            )
    if ruta_empresa is None:
        raise Problema("Faltan las temperaturas.",
                       'Pasalas con --temperaturas "4.0 4.5 5.0" o cargalas en la planilla.')

    ruta = espacio.ruta_de(ruta_empresa, "datos", ARCHIVO_DATOS)
    if not os.path.isfile(ruta):
        raise Problema(
            "No hay registros de temperatura cargados.",
            'Crea la planilla con: frio plantilla. O pasa las lecturas directo: '
            '--temperaturas "4.0 4.5 5.0".',
        )
    registro = _valor(opciones, "registro")
    tabla = excel.leer_tabla(ruta)
    serie = []
    for fila in tabla["filas"]:
        if registro and motor._clave(fila.get("registro")) != motor._clave(registro):
            continue
        valor = motor._numero(fila.get("temperatura_c"))
        if valor is not None:
            serie.append(valor)
    if not serie:
        disponibles = sorted({str(f.get("registro") or "") for f in tabla["filas"]} - {""})
        raise Problema(
            "No encontre lecturas%s en la planilla." % (" del registro «%s»" % registro if registro else ""),
            "Revisa la columna Registro. Los cargados son: %s." % (", ".join(disponibles) or "ninguno"),
        )
    return serie, "la planilla %s" % ARCHIVO_DATOS


def plantilla(opciones):
    """Crea la planilla donde se pegan las lecturas del registrador de temperatura."""
    perfil, ruta_empresa = _contexto(opciones)
    destino = espacio.ruta_de(ruta_empresa, "datos", ARCHIVO_DATOS)
    if os.path.isfile(destino) and not opciones.get("sobrescribir"):
        raise Problema(
            "Ya existe la planilla %s y no la voy a sobrescribir." % ARCHIVO_DATOS,
            "Puedo leerla tal como esta con: frio revisar. Si quieres empezar de cero, "
            "agrega --sobrescribir.",
        )
    hojas = [
        {"nombre": "Instrucciones", "filas": [
            ["Como llenar esta planilla"],
            [""],
            ["Una fila por lectura del registrador. La mayoria de los registradores exporta un CSV "
             "que se puede pegar tal cual en la hoja Lecturas."],
            [""],
            ["Registro: un nombre para cada serie (por ejemplo «Camara 1 enero» o «Envio 4521»). "
             "Asi conviven varias en la misma planilla."],
            ["Temperatura (C): en grados Celsius, con punto o coma decimal."],
            ["Punto de medicion: donde estaba el sensor. La temperatura del aire y la del centro del "
             "producto no son lo mismo y la norma a veces exige la del centro."],
            [""],
            ["Importante: las lecturas tienen que estar tomadas a intervalos regulares. Si el "
             "registrador midio cada 15 minutos, todas deben ser cada 15 minutos."],
        ]},
        {"nombre": "Lecturas", "filas": [COLUMNAS] + [
            ["Camara 1 enero", "2026-01-05 08:00", 4.0, "Aire de la camara", "Vacunas", ""],
            ["Camara 1 enero", "2026-01-05 09:00", 4.5, "Aire de la camara", "Vacunas", ""],
            ["Camara 1 enero", "2026-01-05 10:00", 12.0, "Aire de la camara", "Vacunas",
             "Se abrio la puerta para inventario"],
        ]},
    ]
    excel.escribir_xlsx(destino, hojas)
    return Respuesta(
        {"mensaje": "Planilla de temperaturas creada. Las tres filas son un ejemplo: reemplazalas.",
         "archivo": destino, "columnas": COLUMNAS},
        advertencias=["Borra las filas de ejemplo antes de calcular nada con esta planilla."])


def mkt(opciones):
    """Calcula la temperatura cinetica media de una serie de lecturas."""
    raiz = opciones.get("raiz")
    try:
        perfil, ruta_empresa = _contexto(opciones)
    except Problema:
        perfil, ruta_empresa = {}, None
    serie, origen = _serie(opciones, ruta_empresa)
    entalpia = _numero(opciones, "entalpia")
    resultado = motor.temperatura_cinetica_media(serie, entalpia=entalpia)
    resultado["origen_de_los_datos"] = origen
    resultado["mensaje"] = (
        "La temperatura cinetica media es %s C, %s C por encima del promedio simple (%s C). "
        "Es esa la que se compara con el limite, no el promedio."
        % (round(resultado["mkt_c"], 2), round(resultado["diferencia_con_el_promedio"], 2),
           round(resultado["promedio_c"], 2)))
    return Respuesta(resultado, advertencias=resultado["advertencias"],
                     fuentes=["USP General Chapter <1079.2> Mean Kinetic Temperature"])


def limites(opciones):
    """Dice que temperatura exige la norma para un producto."""
    tabla = motor.cargar_limites()
    producto = _valor(opciones, "producto")
    if not producto:
        return {
            "total": len(tabla),
            "productos": [{"producto": l["producto"], "situacion": l["situacion"],
                           "minimo_c": l["minimo_c"], "maximo_c": l["maximo_c"],
                           "tolerancia_c": l["tolerancia_c"], "articulo": l["articulo"],
                           "fuente": l["fuente"], "notas": l["notas"]} for l in tabla],
            "mensaje": "El Reglamento Sanitario de los Alimentos fija temperaturas por tipo de "
                       "producto y situacion, no una sola para todo. Pide la tuya con: "
                       "frio limites --producto <producto>.",
        }
    encontrado = motor.buscar_limite(producto, _valor(opciones, "situacion"), tabla)
    return Respuesta(encontrado, advertencias=[encontrado["aviso"]] if "aviso" in encontrado else [],
                     fuentes=[encontrado.get("fuente")] if encontrado.get("fuente") else [])


def revisar(opciones):
    """Revisa una serie contra el rango exigido: excursiones y temperatura cinetica media."""
    try:
        perfil, ruta_empresa = _contexto(opciones)
    except Problema:
        perfil, ruta_empresa = {}, None
    serie, origen = _serie(opciones, ruta_empresa)

    minimo = _numero(opciones, "minimo")
    maximo = _numero(opciones, "maximo")
    fuente_del_rango = "El rango lo indicaste tu"
    producto = _valor(opciones, "producto")
    if minimo is None and maximo is None and producto:
        limite = motor.buscar_limite(producto, _valor(opciones, "situacion"))
        if "varias_opciones" in limite:
            raise Problema(
                limite["aviso"],
                "Repite el comando agregando --situacion, por ejemplo: --situacion transporte local.",
            )
        minimo, maximo = limite["minimo_c"], limite["maximo_c"]
        fuente_del_rango = "%s, articulo %s" % (limite["fuente"], limite["articulo"])
    if minimo is None and maximo is None:
        raise Problema(
            "No se contra que rango revisar.",
            "Dame el producto (--producto «alimento congelado») para usar el limite legal, o el "
            "rango directo (--minimo 2 --maximo 8).",
        )

    resultado = motor.evaluar_excursiones(serie, minimo, maximo,
                                          _numero(opciones, "minutos_por_lectura"))
    resultado["origen_de_los_datos"] = origen
    resultado["origen_del_rango"] = fuente_del_rango
    resultado["mensaje"] = resultado["resumen"]

    if ruta_empresa:
        destino = espacio.ruta_de(ruta_empresa, "resultados", "frio_%s.json"
                                  % espacio.texto_a_slug(_valor(opciones, "registro") or "revision"))
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump(resultado, archivo, ensure_ascii=False, indent=2, default=str)
        resultado["resultado_guardado_en"] = destino

    return Respuesta(resultado, advertencias=resultado["advertencias"] + [resultado["quien_decide"]],
                     fuentes=[fuente_del_rango,
                              "USP General Chapter <1079.2> Mean Kinetic Temperature"])


def vida_util(opciones):
    """Estima la vida util a otra temperatura con la regla Q10 del producto."""
    resultado = motor.vida_util_por_q10(
        _numero(opciones, "vida_referencia"), _numero(opciones, "temperatura_referencia"),
        _numero(opciones, "temperatura"), _numero(opciones, "q10"))
    resultado["mensaje"] = resultado["interpretacion"]
    return Respuesta(resultado, advertencias=resultado["advertencias"])


def informe_html(opciones):
    """Arma el informe HTML de la revision de cadena de frio."""
    perfil, ruta_empresa = _contexto(opciones)
    respuesta = revisar(opciones)
    datos = respuesta.resultado

    estado = "verde" if datos["sin_excursiones"] and datos["mkt_dentro_del_rango"] else "rojo"
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Temperatura cinetica media", "valor": datos["mkt_c"], "unidad": "C",
             "detalle": "Es la que se compara con el limite", "color": estado},
            {"etiqueta": "Promedio simple", "valor": datos["promedio_c"], "unidad": "C",
             "detalle": "No sirve para decidir: se muestra para comparar"},
            {"etiqueta": "Excursiones", "valor": datos["total_excursiones"], "unidad": "",
             "detalle": "Veces que se salio del rango",
             "color": "verde" if datos["sin_excursiones"] else "rojo"},
            {"etiqueta": "Lecturas fuera de rango", "valor": datos["porcentaje_fuera_de_rango"],
             "unidad": "%", "detalle": "%d de %d lecturas"
                                       % (datos["lecturas_fuera_de_rango"], datos["lecturas"])},
        ]},
        {"tipo": "nota", "estilo": "aviso" if estado == "verde" else "riesgo",
         "texto": datos["resumen"]},
        {"tipo": "titulo", "texto": "Que exigia la norma", "nivel": 2},
        {"tipo": "lista", "items": [
            "Rango exigido: %s" % _texto_rango(datos["rango_exigido"]),
            "De donde sale: %s" % datos["origen_del_rango"],
            "Temperatura minima registrada: %s C" % datos["minima_registrada_c"],
            "Temperatura maxima registrada: %s C" % datos["maxima_registrada_c"],
        ]},
    ]
    if datos["excursiones"]:
        bloques.append({"tipo": "titulo", "texto": "Excursiones, una por una", "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Desde la lectura", "Hasta la lectura", "Lecturas",
                                     "Minima (C)", "Maxima (C)", "Horas"],
                        "numericas": [0, 1, 2, 3, 4, 5],
                        "filas": [[e["desde_lectura"], e["hasta_lectura"], e["lecturas"],
                                   e["minima_c"], e["maxima_c"], e.get("horas", "")]
                                  for e in datos["excursiones"]]})
    bloques.append({"tipo": "titulo", "texto": "Como se calculo", "nivel": 2})
    bloques.append({"tipo": "lista", "items": [
        "Temperatura cinetica media segun USP <1079.2>, con entalpia de activacion de 83,144 kJ/mol.",
        "La temperatura cinetica media es siempre mayor o igual que el promedio: el dano termico "
        "crece exponencialmente con la temperatura, no en linea recta.",
    ] + datos["advertencias"]})
    bloques.append({"tipo": "nota", "estilo": "riesgo", "texto": datos["quien_decide"]})

    destino = espacio.ruta_de(ruta_empresa, "reportes", "cadena-de-frio-%s.html"
                              % espacio.texto_a_slug(_valor(opciones, "registro") or "revision"))
    informe.escribir_html(destino, "Revision de cadena de frio", bloques,
                          marca=perfil.get("marca") or {}, subtitulo=perfil.get("nombre", ""))
    return Respuesta({"mensaje": "Informe de cadena de frio listo.", "archivo": destino,
                      "mkt_c": datos["mkt_c"], "excursiones": datos["total_excursiones"]},
                     advertencias=respuesta.advertencias, fuentes=respuesta.fuentes)


def _texto_rango(rango):
    minimo, maximo = rango["minimo_c"], rango["maximo_c"]
    if minimo is not None and maximo is not None:
        return "entre %s C y %s C" % (minimo, maximo)
    if maximo is not None:
        return "no mas de %s C" % maximo
    return "al menos %s C" % minimo


ACCIONES = {"plantilla": plantilla, "mkt": mkt, "limites": limites, "revisar": revisar,
            "vida-util": vida_util, "informe": informe_html}
