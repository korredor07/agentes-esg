# -*- coding: utf-8 -*-
"""Indicadores sociales: personas, seguridad, capacitacion e inclusion."""

import json
import os

from calculos import social as motor_social
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Calcula los indicadores de personas: dotacion, rotacion, brecha salarial, accidentes e inclusion."


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _leer_personas(ruta_empresa):
    ruta = espacio.ruta_de(ruta_empresa, "datos", "personas.xlsx")
    if not os.path.isfile(ruta):
        raise Problema(
            "No encontre la planilla de personas.",
            "Creala con: plantilla crear --tipo personas, llenala con los datos del año y avisame.",
        )
    return excel.leer_tabla(ruta)["filas"], ruta


def calcular(opciones):
    perfil, ruta = _contexto(opciones)
    periodo = opciones.get("periodo") if opciones.get("periodo") is not True else None
    filas, archivo = _leer_personas(ruta)
    indicadores = motor_social.calcular(filas, periodo)
    indicadores["empresa"] = perfil.get("nombre")
    indicadores["inclusion"] = motor_social.revisar_inclusion(indicadores, perfil.get("pais"))

    destino = espacio.ruta_de(ruta, "resultados", "social_%s.json" % (periodo or "completo"))
    with open(destino, "w", encoding="utf-8") as archivo_salida:
        json.dump(indicadores, archivo_salida, ensure_ascii=False, indent=2)
    indicadores["archivo_datos"] = archivo
    indicadores["resultado_guardado_en"] = destino
    return Respuesta(indicadores, advertencias=indicadores.get("advertencias", []))


def _bloques(indicadores, perfil):
    inclusion = indicadores.get("inclusion") or {}
    tarjetas = [
        {"etiqueta": "Dotacion", "valor": indicadores["dotacion_total"], "unidad": "personas",
         "detalle": "Periodo: %s" % indicadores.get("periodo", "")},
        {"etiqueta": "Mujeres", "valor": indicadores["mujeres_pct"], "unidad": "%"},
        {"etiqueta": "Rotacion", "valor": indicadores["tasa_rotacion_pct"], "unidad": "%",
         "detalle": "%d desvinculaciones" % indicadores["desvinculaciones"]},
        {"etiqueta": "Accidentabilidad", "valor": indicadores["tasa_accidentabilidad_pct"], "unidad": "%",
         "detalle": "%d accidentes con tiempo perdido" % indicadores["accidentes_con_tiempo_perdido"],
         "color": "rojo" if indicadores["accidentes_con_tiempo_perdido"] else "verde"},
        {"etiqueta": "Capacitacion", "valor": indicadores["horas_capacitacion_por_persona"],
         "unidad": "h/persona"},
    ]
    bloques = [
        {"tipo": "kpi", "items": tarjetas},
        {"tipo": "titulo", "texto": "Composicion del equipo", "nivel": 2},
        {"tipo": "barras", "titulo": "Personas por categoria", "unidad": "personas",
         "datos": [{"etiqueta": clave, "valor": valor}
                   for clave, valor in sorted(indicadores["por_categoria"].items(), key=lambda x: -x[1])]},
        {"tipo": "tabla", "columnas": ["Genero", "Personas"], "numericas": [1],
         "filas": [[clave, valor] for clave, valor in sorted(indicadores["por_genero"].items(),
                                                             key=lambda x: -x[1])]},
    ]

    brechas = indicadores.get("brecha_salarial_por_categoria") or {}
    if brechas:
        bloques.append({"tipo": "titulo", "texto": "Brecha salarial por categoria", "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Categoria", "Promedio mujeres", "Promedio hombres",
                                     "Razon mujer/hombre", "Brecha (%)"],
                        "numericas": [1, 2, 3, 4],
                        "filas": [[categoria, datos["promedio_mujeres"], datos["promedio_hombres"],
                                   datos["razon_mujer_hombre"], datos["brecha_pct"]]
                                  for categoria, datos in sorted(brechas.items())],
                        "nota": "Una razon menor a 1 significa que las mujeres ganan menos en esa categoria."})

    if inclusion.get("aplica"):
        bloques.append({"tipo": "titulo", "texto": "Inclusion laboral", "nivel": 2})
        bloques.append({"tipo": "semaforo", "items": [{
            "etiqueta": "Cuota del 1 % (Ley 21.015)",
            "estado": "verde" if inclusion.get("cumple") else "rojo",
            "detalle": "Exige %s persona(s); hay %s contratada(s)."
                       % (inclusion.get("personas_exigidas"), inclusion.get("personas_contratadas"))}]})

    if indicadores.get("advertencias"):
        bloques.append({"tipo": "titulo", "texto": "Datos que faltan", "nivel": 2})
        bloques.append({"tipo": "lista", "items": indicadores["advertencias"]})

    bloques.append({"tipo": "nota", "estilo": "info", "texto": indicadores["nota_metodologica"]})
    bloques.append({"tipo": "nota", "estilo": "aviso",
                    "texto": "Los datos de personas son sensibles: este informe se queda en el computador "
                             "de la empresa y se comparte solo de forma agregada."})
    return bloques


def informe_html(opciones):
    perfil, ruta = _contexto(opciones)
    periodo = opciones.get("periodo") if opciones.get("periodo") is not True else None
    origen = espacio.ruta_de(ruta, "resultados", "social_%s.json" % (periodo or "completo"))
    if os.path.isfile(origen):
        with open(origen, encoding="utf-8") as archivo:
            indicadores = json.load(archivo)
    else:
        filas, _ = _leer_personas(ruta)
        indicadores = motor_social.calcular(filas, periodo)
        indicadores["inclusion"] = motor_social.revisar_inclusion(indicadores, perfil.get("pais"))

    destino = espacio.ruta_de(ruta, "reportes", "indicadores-sociales-%s.html" % (periodo or "completo"))
    informe.escribir_html(destino, "Indicadores sociales", _bloques(indicadores, perfil),
                          marca=perfil.get("marca") or {},
                          subtitulo="%s - %s" % (perfil.get("nombre", ""), indicadores.get("periodo", "")))
    return {"mensaje": "Informe de indicadores sociales listo.", "archivo": destino,
            "dotacion": indicadores["dotacion_total"]}


ACCIONES = {"calcular": calcular, "informe": informe_html}
