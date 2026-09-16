# -*- coding: utf-8 -*-
"""Emisiones del transporte de carga, tramo por tramo, segun ISO 14083."""

import json
import os

from calculos import logistica as motor
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta
from plantillas import definiciones

AYUDA = ("Calcula las emisiones de una cadena de transporte tramo por tramo segun ISO 14083, "
         "compara modos y arma el informe para el cliente que lo pide.")

ARCHIVO_DATOS = "cadenas_transporte.xlsx"

COLUMNAS = ["Cadena", "Tramo", "Tipo", "Descripcion", "Modo", "Vehiculo", "Toneladas", "TEU",
            "Kilometros", "Tipo de distancia", "Intensidad propia", "Fuente", "Notas"]

# Filas de ejemplo de la planilla: se reconocen al leer para que no entren al calculo.
EJEMPLO_TRAMOS = [
    ["Fruta a Venlo", 1, "transporte", "Curico a Puerto San Antonio", "carretera",
     "camion refrigerado", 12, "", 220, "SFD", "", "", "Distancia de ruta"],
    ["Fruta a Venlo", 2, "hub", "Terminal de contenedores San Antonio", "", "", 12, "", "", "",
     "", "", "Falta la intensidad del terminal"],
    ["Fruta a Venlo", 3, "transporte", "San Antonio a Rotterdam", "maritimo", "barco", 12, "",
     12000, "SFD", "", "", ""],
    ["Fruta a Venlo", 4, "hub", "Terminal de contenedores Rotterdam", "", "", 12, "", "", "",
     "", "", ""],
    ["Fruta a Venlo", 5, "transporte", "Rotterdam a Venlo", "carretera", "camion refrigerado",
     12, "", 150, "SFD", "", "", ""],
]


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
                       "Escribe solo el numero.")


def factores(opciones):
    """Lista los vehiculos disponibles con su intensidad, fuente y licencia."""
    catalogo = motor.cargar_factores()
    modo = _valor(opciones, "modo")
    seleccion = [f for f in catalogo.values() if not modo or f["modo"] == motor._clave(modo)]
    seleccion.sort(key=lambda f: (f["modo"], f["total"]))
    return {
        "total": len(seleccion),
        "vehiculos": [{
            "id": f["id"], "modo": f["modo"], "que_es": f["detalle"],
            "kg_co2e_por_t_km": f["total"],
            "de_operacion": f["operacion"], "de_provision_de_energia": f["provision"],
            "anio": f["anio"], "fuente": f["fuente"], "licencia": f["licencia"],
            "notas": f["notas"],
        } for f in seleccion],
        "como_se_escribe": sorted(motor.ALIAS),
        "mensaje": "El total suma la operacion del vehiculo y la provision de su energia, como pide "
                   "ISO 14083. Si el transportista entrega su propio dato, es mejor que cualquiera "
                   "de estos promedios.",
    }


def tramo(opciones):
    """Calcula un solo tramo: util para responder rapido cuanto emite un flete."""
    catalogo = motor.cargar_factores()
    datos = {
        "tipo": _valor(opciones, "tipo", "transporte"),
        "modo": _valor(opciones, "modo"),
        "vehiculo": _valor(opciones, "vehiculo"),
        "toneladas": _numero(opciones, "toneladas"),
        "teu": _numero(opciones, "teu"),
        "carga": _valor(opciones, "carga"),
        "km": _numero(opciones, "km") or _numero(opciones, "kilometros"),
        "tipo_distancia": _valor(opciones, "tipo_distancia", "SFD"),
        "intensidad": _numero(opciones, "intensidad"),
        "descripcion": _valor(opciones, "descripcion"),
        "_fila": 1,
    }
    resultado = motor.calcular_tramo(datos, catalogo)
    if resultado.get("kg_co2e_total") is not None:
        resultado["mensaje"] = "Ese tramo emite %s kg CO2e (%s toneladas por %s km)." % (
            round(resultado["kg_co2e_total"], 1), resultado["toneladas"],
            round(resultado.get("distancia_de_actividad_km") or 0, 1))
    return Respuesta(resultado, advertencias=resultado.get("advertencias") or [],
                     fuentes=[resultado.get("fuente")] if resultado.get("fuente") else [])


def _tramos_del_comando(opciones):
    """Tramos pasados como JSON con --tramos: la persona dicto el viaje en la conversacion.

    Cada tramo: {"tipo", "descripcion", "modo", "vehiculo", "toneladas", "teu", "km",
    "tipo_distancia", "intensidad"}. Solo lo necesario: tipo, toneladas y km o intensidad.
    """
    crudo = _valor(opciones, "tramos")
    if not crudo:
        return None
    if os.path.isfile(str(crudo)):
        with open(crudo, encoding="utf-8") as archivo:
            tramos = json.load(archivo)
    else:
        try:
            tramos = json.loads(crudo)
        except ValueError as error:
            raise Problema("No pude leer los tramos: %s." % error,
                           'Pasalos como lista JSON, por ejemplo: --tramos "[{\\"vehiculo\\": \\"camion\\", '
                           '\\"toneladas\\": 12, \\"km\\": 220}]", o guardalos en un archivo y pasa su ruta.')
    if isinstance(tramos, dict):
        tramos = [tramos]
    if not isinstance(tramos, list) or not tramos:
        raise Problema("Los tramos deben venir como una lista.", "Un elemento por tramo del viaje.")
    salida = []
    for numero, tramo in enumerate(tramos, start=1):
        ficha = dict(tramo)
        ficha.setdefault("_fila", numero)
        salida.append(ficha)
    return salida


def _leer_tramos(ruta_empresa, cadena=None):
    ruta = espacio.ruta_de(ruta_empresa, "datos", ARCHIVO_DATOS)
    if not os.path.isfile(ruta):
        raise Problema(
            "No hay ninguna cadena de transporte cargada.",
            "Crea la planilla con: logistica plantilla, llenala con los tramos del envio y avisame.",
        )
    tabla, aviso = definiciones.leer_sin_ejemplos(
        ruta, definicion={"columnas": [{"titulo": c} for c in COLUMNAS], "ejemplo": EJEMPLO_TRAMOS})
    filas = []
    for numero, fila in enumerate(tabla["filas"], start=1):
        nombre = str(fila.get("cadena") or "").strip()
        if cadena and motor._clave(nombre) != motor._clave(cadena):
            continue
        filas.append({
            "cadena": nombre or "Cadena de transporte",
            "_fila": fila.get("tramo") or numero,
            "tipo": fila.get("tipo") or "transporte",
            "descripcion": fila.get("descripcion"),
            "modo": fila.get("modo"),
            "vehiculo": fila.get("vehiculo"),
            "toneladas": fila.get("toneladas"),
            "teu": fila.get("teu"),
            "km": fila.get("kilometros"),
            "tipo_distancia": fila.get("tipo_de_distancia"),
            "intensidad": fila.get("intensidad_propia"),
            "fuente": fila.get("fuente"),
        })
    if not filas:
        raise Problema(
            ("La planilla de transporte solo tiene las filas de ejemplo." if aviso and not tabla["filas"] else
             "No encontre tramos%s en la planilla." % (" de la cadena «%s»" % cadena if cadena else "")),
            ("Reemplazalas por los tramos del envio real, o dictalos con --tramos."
             if aviso and not tabla["filas"] else
             "Revisa la columna Cadena. Las cargadas son: %s."
             % ", ".join(sorted({str(f.get("cadena") or "") for f in tabla["filas"]}) or ["ninguna"])),
        )
    return filas, ruta, aviso


def plantilla(opciones):
    """Crea la planilla vacia donde se anotan los tramos de cada envio."""
    perfil, ruta_empresa = _contexto(opciones)
    destino = espacio.ruta_de(ruta_empresa, "datos", ARCHIVO_DATOS)
    if os.path.isfile(destino) and not opciones.get("sobrescribir"):
        raise Problema(
            "Ya existe la planilla %s y no la voy a sobrescribir." % ARCHIVO_DATOS,
            "Puedo leerla tal como esta con: logistica calcular. Si de verdad quieres empezar de "
            "cero, agrega --sobrescribir.",
        )
    ejemplo = [list(fila) for fila in EJEMPLO_TRAMOS]
    hojas = [
        {"nombre": "Instrucciones", "filas": [
            ["Como llenar esta planilla"],
            [""],
            ["Cada fila es un tramo del viaje. Se abre un tramo nuevo cada vez que cambia el "
             "vehiculo o la carga pasa por un puerto, un terminal o una bodega."],
            [""],
            ["Cadena: un nombre para el envio. Sirve para tener varios en la misma planilla."],
            ["Tipo: transporte (un vehiculo moviendo la carga) o hub (un puerto, terminal o bodega)."],
            ["Modo: carretera, ferrocarril, maritimo, fluvial o aereo."],
            ["Vehiculo: camion, camion refrigerado, furgon, tren, barco, granelero, avion..."],
            ["Toneladas: la mercancia con el embalaje del vendedor, SIN los palets ni el contenedor."],
            ["TEU: si no sabes el peso, cuantos contenedores. Se asumen 10 toneladas por contenedor."],
            ["Kilometros: del tramo. Si no la sabes, se puede estimar entre ciudades o puertos."],
            ["Tipo de distancia: SFD (la mas corta practicable, lo habitual), REAL (la del odometro) "
             "o GCD (en linea recta). No mezcles tipos dentro de una misma cadena."],
            ["Intensidad propia: si el transportista entrega su dato en kg CO2e por t.km, ponlo aqui "
             "y se usa en vez del promedio. Es el mejor dato posible."],
            [""],
            ["Los hubs sin intensidad no se pueden calcular y el total queda marcado como incompleto: "
             "es correcto que lo diga, porque ISO 14083 exige incluirlos."],
        ]},
        {"nombre": "Tramos", "filas": [COLUMNAS] + ejemplo},
    ]
    excel.escribir_xlsx(destino, hojas)
    return Respuesta(
        {"mensaje": "Planilla de cadenas de transporte creada. Trae un ejemplo: reemplazalo por los "
                    "tramos reales.", "archivo": destino, "columnas": COLUMNAS},
        advertencias=["Las filas de ejemplo son de mentira: borralas antes de calcular."])


def calcular(opciones):
    """Calcula las emisiones de una cadena completa y guarda el resultado."""
    perfil, ruta_empresa = _contexto(opciones)
    cadena = _valor(opciones, "cadena")
    dictados = _tramos_del_comando(opciones)
    if dictados:
        filas, archivo, nombre = dictados, "tramos indicados en el comando", cadena or "Cadena de transporte"
        aviso = None
    else:
        filas, archivo, aviso = _leer_tramos(ruta_empresa, cadena)
        nombre = filas[0].get("cadena") if cadena or len({f["cadena"] for f in filas}) == 1 else None

    resultado = motor.calcular_cadena(filas, nombre)
    if aviso:
        resultado["advertencias"] = [aviso] + list(resultado.get("advertencias", []))
    resultado["empresa"] = perfil.get("nombre")
    resultado["archivo"] = archivo

    destino = espacio.ruta_de(ruta_empresa, "resultados",
                              "logistica_%s.json" % espacio.texto_a_slug(resultado["cadena"]))
    with open(destino, "w", encoding="utf-8") as archivo_salida:
        json.dump(resultado, archivo_salida, ensure_ascii=False, indent=2, default=str)
    resultado["resultado_guardado_en"] = destino
    resultado["mensaje"] = (
        "La cadena «%s» emite %s kg CO2e (%s g CO2e por tonelada kilometro)."
        % (resultado["cadena"], round(resultado["total_kg_co2e"], 1),
           resultado["intensidad_g_co2e_por_t_km"])
        if resultado["completo"] else
        "%s Lo calculado hasta ahora suma %s kg CO2e."
        % (resultado["aviso_principal"], round(resultado["total_kg_co2e"], 1)))
    return Respuesta(resultado, advertencias=resultado["advertencias"], fuentes=resultado["fuentes"])


def comparar(opciones):
    """Muestra cuanto emitiria la misma carga en cada modo de transporte."""
    toneladas = _numero(opciones, "toneladas")
    km = _numero(opciones, "km") or _numero(opciones, "kilometros")
    if not toneladas or not km:
        raise Problema(
            "Para comparar necesito cuanta carga y cuantos kilometros.",
            "Por ejemplo: logistica comparar --toneladas 12 --km 500",
        )
    resultado = motor.comparar_modos(toneladas, km)
    mejor = resultado["opciones"][0] if resultado["opciones"] else None
    peor = resultado["opciones"][-1] if resultado["opciones"] else None
    if mejor and peor and mejor is not peor:
        resultado["mensaje"] = (
            "Mover %s toneladas %s km va de %s kg CO2e en %s a %s kg CO2e en %s: %s veces mas."
            % (toneladas, km, round(mejor["kg_co2e"], 1), mejor["detalle"].lower(),
               round(peor["kg_co2e"], 1), peor["detalle"].lower(), peor["veces_el_mas_limpio"]))
    return Respuesta(resultado, advertencias=[resultado["aviso"]])


def _bloques(resultado, perfil):
    tramos = resultado["tramos"]
    bloques = []
    if not resultado["completo"]:
        bloques.append({"tipo": "nota", "estilo": "riesgo",
                        "texto": "%s ISO 14083 exige incluir tambien las operaciones de puerto, "
                                 "terminal y bodega. Mientras falten, esta cifra es un piso."
                                 % resultado["aviso_principal"]})
    bloques.append({"tipo": "kpi", "items": [
        {"etiqueta": "Emisiones de la cadena", "valor": resultado["total_t_co2e"], "unidad": "tCO2e",
         "detalle": resultado["cadena"], "color": "verde" if resultado["completo"] else "amarillo"},
        {"etiqueta": "Actividad", "valor": resultado["actividad_t_km"], "unidad": "t.km",
         "detalle": "Toneladas por kilometro recorrido"},
        {"etiqueta": "Intensidad", "valor": resultado["intensidad_g_co2e_por_t_km"],
         "unidad": "g CO2e/t.km", "detalle": "Lo que emite mover una tonelada un kilometro"},
        {"etiqueta": "Provision de energia", "valor": resultado["porcentaje_de_provision"],
         "unidad": "%", "detalle": "Parte que no sale del tubo de escape"},
    ]})

    with_dato = [t for t in tramos if t["calculado"] and t.get("kg_co2e_total")]
    if with_dato:
        bloques.append({"tipo": "barras", "titulo": "De donde vienen las emisiones del viaje",
                        "unidad": "kg CO2e",
                        "datos": [{"etiqueta": t.get("descripcion") or "Tramo %s" % t["tramo"],
                                   "valor": t["kg_co2e_total"]} for t in with_dato]})

    bloques.append({"tipo": "titulo", "texto": "Tramo por tramo", "nivel": 2})
    bloques.append({"tipo": "tabla",
                    "columnas": ["Tramo", "Modo", "Toneladas", "Km de actividad", "t.km", "kg CO2e"],
                    "numericas": [2, 3, 4, 5],
                    "filas": [[t.get("descripcion") or "Tramo %s" % t["tramo"],
                               t.get("modo") or t["tipo"], t.get("toneladas"),
                               t.get("distancia_de_actividad_km"), t.get("t_km"),
                               t.get("kg_co2e_total")] for t in tramos]})

    if resultado["por_modo"]:
        bloques.append({"tipo": "titulo", "texto": "Donde esta la palanca de reduccion", "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Modo", "% de las emisiones", "% de las toneladas kilometro"],
                        "numericas": [1, 2],
                        "filas": [[modo, datos["porcentaje_de_las_emisiones"],
                                   datos["porcentaje_de_la_actividad"]]
                                  for modo, datos in sorted(
                                      resultado["por_modo"].items(),
                                      key=lambda x: -x[1]["porcentaje_de_las_emisiones"])]})
        bloques.append({"tipo": "texto",
                        "texto": "Cuando un modo aporta mucho mas porcentaje de emisiones que de "
                                 "toneladas kilometro, ahi esta lo que conviene cambiar primero."})

    bloques.append({"tipo": "titulo", "texto": "Como se calculo", "nivel": 2})
    ajustados = [t for t in tramos if t.get("tipo") == "transporte"
                 and (abs((t.get("ajuste_de_distancia") or 1.0) - 1.0) > 1e-9 or t.get("modo") == "aereo")]
    if ajustados:
        texto_distancias = ("Se ajusto la distancia de %d tramo(s) para dejarla del mismo tipo que la intensidad: "
                            "%s." % (len(ajustados), "; ".join(
                                "%s: %s km declarados, %s km usados"
                                % (t.get("descripcion") or "tramo %s" % t["tramo"],
                                   informe.formatear_numero(t["distancia_declarada_km"]),
                                   informe.formatear_numero(t["distancia_de_actividad_km"])) for t in ajustados)))
    else:
        texto_distancias = ("Las distancias se usaron tal como se declararon, porque ya eran la ruta mas corta "
                            "practicable: no hizo falta ajustarlas.")
    bloques.append({"tipo": "lista", "items": [
        resultado["metodo"],
        texto_distancias,
        "La masa es la mercancia con el embalaje del vendedor, sin palets ni contenedor.",
    ] + [f for f in resultado["fuentes"]]})
    if resultado["advertencias"]:
        bloques.append({"tipo": "titulo", "texto": "Supuestos y limitaciones", "nivel": 2})
        bloques.append({"tipo": "lista", "items": resultado["advertencias"]})
    return bloques


def informe_html(opciones):
    """Arma el informe HTML de la cadena de transporte."""
    perfil, ruta_empresa = _contexto(opciones)
    cadena = _valor(opciones, "cadena")
    dictados = _tramos_del_comando(opciones)
    if dictados:
        filas, nombre = dictados, cadena or "Cadena de transporte"
        aviso = None
    else:
        filas, _, aviso = _leer_tramos(ruta_empresa, cadena)
        nombre = filas[0].get("cadena") if cadena or len({f["cadena"] for f in filas}) == 1 else None
    resultado = motor.calcular_cadena(filas, nombre)
    if aviso:
        resultado["advertencias"] = [aviso] + list(resultado.get("advertencias", []))

    destino = espacio.ruta_de(ruta_empresa, "reportes",
                              "transporte-%s.html" % espacio.texto_a_slug(resultado["cadena"]))
    informe.escribir_html(destino, "Emisiones del transporte", _bloques(resultado, perfil),
                          marca=perfil.get("marca") or {},
                          subtitulo="%s - %s" % (perfil.get("nombre", ""), resultado["cadena"]))
    return Respuesta(
        {"mensaje": "Informe de transporte listo.", "archivo": destino,
         "total_t_co2e": resultado["total_t_co2e"], "completo": resultado["completo"]},
        advertencias=resultado["advertencias"], fuentes=resultado["fuentes"])


ACCIONES = {"factores": factores, "tramo": tramo, "plantilla": plantilla, "calcular": calcular,
            "comparar": comparar, "informe": informe_html}
