# -*- coding: utf-8 -*-
"""Tablero: una sola pagina con el estado ESG de la empresa."""

import datetime
import glob
import json
import os

from calculos import puntaje as motor_puntaje
from nucleo import espacio, evidencias, informe
from nucleo.salida import Respuesta

AYUDA = "Arma un tablero HTML con la huella, el diagnostico, las alertas y el estado de los datos."


def _leer_json(ruta):
    if not os.path.isfile(ruta):
        return None
    try:
        with open(ruta, encoding="utf-8") as archivo:
            return json.load(archivo)
    except (ValueError, OSError):
        return None


def _ultima_huella(ruta_empresa):
    archivos = sorted(glob.glob(os.path.join(ruta_empresa, "resultados", "huella_*.json")))
    return _leer_json(archivos[-1]) if archivos else None


def _estado_archivos(ruta_empresa):
    filas = []
    carpeta = os.path.join(ruta_empresa, "datos")
    esperados = {
        "consumos.xlsx": "Energia y combustibles (alcances 1 y 2)",
        "alcance3.xlsx": "Cadena de valor (alcance 3)",
        "sitios.xlsx": "Sitios e instalaciones",
        "personas.xlsx": "Personas y condiciones laborales",
    }
    for nombre, descripcion in esperados.items():
        ruta = os.path.join(carpeta, nombre)
        if os.path.isfile(ruta):
            fecha = datetime.datetime.fromtimestamp(os.path.getmtime(ruta)).strftime("%d-%m-%Y")
            filas.append({"etiqueta": descripcion, "estado": "verde", "detalle": "Actualizado el %s" % fecha})
        else:
            filas.append({"etiqueta": descripcion, "estado": "gris", "detalle": "Todavia sin cargar",
                          "estado_texto": "Pendiente"})
    return filas


def _alertas(ruta_empresa):
    """Alertas de plazos que dejan otros modulos en seguimiento/alertas.json."""
    datos = _leer_json(os.path.join(ruta_empresa, "seguimiento", "alertas.json")) or []
    hoy = datetime.date.today().isoformat()
    vigentes = []
    for alerta in datos:
        if alerta.get("vence") and alerta.get("estado") != "resuelta":
            vigentes.append({
                "etiqueta": alerta.get("titulo", "Plazo"),
                "estado": "rojo" if alerta["vence"] <= hoy else ("amarillo" if alerta.get("por_vencer") else "verde"),
                "detalle": "Vence el %s. %s" % (alerta["vence"], alerta.get("detalle", "")),
            })
    return vigentes


def generar(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)

    huella = _ultima_huella(ruta)
    seguimiento = _leer_json(os.path.join(ruta, "seguimiento", "diagnostico.json")) or {}
    diagnostico = seguimiento.get("ultima_evaluacion")
    if not diagnostico:
        diagnostico = motor_puntaje.evaluar(perfil, ruta, seguimiento.get("respuestas"))
    verificacion = evidencias.verificar(espacio.ruta_de(ruta, "evidencias"), base=ruta)

    palabra, color = motor_puntaje.nivel(diagnostico["puntaje_general"])
    tarjetas = [
        {"etiqueta": "Puntaje ESG", "valor": diagnostico["puntaje_general"], "unidad": "/100",
         "detalle": "Nivel: %s" % palabra, "color": color},
        {"etiqueta": "Huella de carbono", "valor": (huella or {}).get("total_t_co2e", 0), "unidad": "tCO2e",
         "detalle": ("Periodo: %s" % (huella or {}).get("periodo", "sin calcular")) if (huella or {}).get("completo", True)
                    else "INCOMPLETA: faltan %d fila(s)" % (huella or {}).get("registros_con_problema", 0),
         "color": None if (huella or {}).get("completo", True) else "rojo"},
        {"etiqueta": "Brechas por cerrar", "valor": len([b for b in diagnostico["brechas"]
                                                         if b["seguimiento"] != "resuelta"]),
         "unidad": "", "detalle": "%d de alto riesgo" % len(diagnostico["brechas_criticas"]),
         "color": "rojo" if diagnostico["brechas_criticas"] else "verde"},
        {"etiqueta": "Listo para auditoria", "valor": diagnostico["listo_para_auditoria_pct"], "unidad": "%",
         "detalle": "Indicadores con dato respaldado"},
        {"etiqueta": "Evidencias", "valor": verificacion["total"], "unidad": "respaldos",
         "detalle": "Cadena intacta" if verificacion["ok"] else "Revisar: hay problemas",
         "color": "verde" if verificacion["ok"] else "rojo"},
    ]
    bloques = []
    if huella and not huella.get("completo", True):
        bloques.append({"tipo": "nota", "estilo": "riesgo",
                        "texto": "%s Mientras tanto, la huella que aparece aqui abajo esta subestimada."
                                 % huella.get("aviso_principal", "El ultimo calculo de huella esta incompleto.")})
    bloques.append({"tipo": "kpi", "items": tarjetas})

    alertas = _alertas(ruta)
    if alertas:
        bloques.append({"tipo": "titulo", "texto": "Plazos que vencen", "nivel": 2})
        bloques.append({"tipo": "semaforo", "items": alertas})

    if huella:
        por_alcance = huella.get("por_alcance", {})
        if por_alcance:
            bloques.append({"tipo": "dona", "titulo": "Huella por alcance", "unidad": "tCO2e",
                            "datos": [{"etiqueta": clave.replace("_", " ").title(), "valor": v["kg_co2e"] / 1000.0}
                                      for clave, v in sorted(por_alcance.items())]})
        periodos = sorted(k for k in huella.get("por_periodo", {}) if k != "sin periodo")
        mensuales = [p for p in periodos if len(p) == 7]
        serie = mensuales if len(mensuales) > 1 else periodos
        if len(serie) > 1:
            bloques.append({"tipo": "lineas",
                            "titulo": "Emisiones mes a mes" if serie is mensuales else "Emisiones por periodo",
                            "unidad": "tCO2e",
                            "series": [{"nombre": "Emisiones",
                                        "puntos": [(p, huella["por_periodo"][p]["kg_co2e"] / 1000.0)
                                                   for p in serie]}]})
            if serie is mensuales and len(mensuales) < len(periodos):
                bloques.append({"tipo": "texto",
                                "texto": "La curva muestra solo lo cargado mes a mes; los datos anuales "
                                         "(como la cadena de valor) estan en el total pero no en la curva."})
    else:
        bloques.append({"tipo": "nota", "estilo": "aviso",
                        "texto": "Todavia no hay huella calculada. Es el mejor primer paso: con las boletas "
                                 "de luz y el combustible del año ya se puede."})

    proximas = [b for b in diagnostico["brechas"] if b["seguimiento"] != "resuelta"][:5]
    if proximas:
        bloques.append({"tipo": "titulo", "texto": "Proximas cinco cosas por hacer", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Prioridad", "Que falta", "Que hacer"], "numericas": [0],
                        "filas": [[b["prioridad"], b["titulo"], b["que_hacer"]] for b in proximas]})

    bloques.append({"tipo": "titulo", "texto": "Estado de los datos", "nivel": 2})
    estado_archivos = _estado_archivos(ruta)
    if huella and not huella.get("completo", True):
        for fila in estado_archivos:
            if fila["etiqueta"].startswith("Energia y combustibles"):
                fila["estado"] = "rojo"
                fila["estado_texto"] = "Con errores"
                fila["detalle"] = ("%s, pero %d fila(s) no se pudieron calcular."
                                   % (fila["detalle"], huella.get("registros_con_problema", 0)))
    bloques.append({"tipo": "semaforo", "items": estado_archivos})
    bloques.append({"tipo": "nota", "estilo": "info",
                    "texto": "Tablero generado con los datos de esta carpeta. Es apoyo de gestion: "
                             "no reemplaza asesoria legal ni una auditoria."})

    destino = espacio.ruta_de(ruta, "reportes", "tablero.html")
    informe.escribir_html(destino, "Tablero ESG", bloques, marca=perfil.get("marca") or {},
                          subtitulo="%s - %s" % (perfil.get("nombre", ""),
                                                 datetime.date.today().strftime("%d-%m-%Y")))
    return Respuesta(
        {"mensaje": "Tablero listo.", "archivo": destino,
         "puntaje_general": diagnostico["puntaje_general"],
         "huella_t_co2e": (huella or {}).get("total_t_co2e"),
         "brechas_abiertas": len([b for b in diagnostico["brechas"] if b["seguimiento"] != "resuelta"]),
         "evidencias_ok": verificacion["ok"]},
        advertencias=[] if verificacion["ok"] else ["Hay problemas en la cadena de evidencias: revisalos."])


ACCIONES = {"generar": generar}
