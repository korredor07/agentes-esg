# -*- coding: utf-8 -*-
"""Metas de reduccion: trayectoria, probabilidad de cumplirlas y plan de medidas."""

import glob
import json
import os

from calculos import macc as motor_macc
from calculos import metas as motor_metas
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta
from plantillas import definiciones

AYUDA = "Define metas de reduccion, calcula su trayectoria, estima la probabilidad de cumplirlas y arma el plan."

ARCHIVO = "metas.json"
AVISO = ("Una meta publica sin plan detras es un riesgo legal y reputacional. Publica siempre los "
         "supuestos y el plan junto con la meta.")


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _valor(opciones, clave, por_defecto=None):
    valor = opciones.get(clave)
    return valor if valor not in (None, True) else por_defecto


def _leer_meta(ruta_json):
    if not os.path.isfile(ruta_json):
        return {}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            return json.load(archivo)
        except ValueError:
            raise Problema("El archivo de metas esta dañado.",
                           "Puedo volver a definir la meta contigo en un minuto.")


def _guardar_meta(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _ultima_huella(ruta_empresa):
    archivos = sorted(glob.glob(os.path.join(ruta_empresa, "resultados", "huella_*.json")))
    for ruta in reversed(archivos):
        try:
            with open(ruta, encoding="utf-8") as archivo:
                return json.load(archivo)
        except (ValueError, OSError):
            continue
    return None


def _emisiones_de_la_huella(huella):
    por_alcance = (huella or {}).get("por_alcance", {})
    return {
        "alcance_1": por_alcance.get("alcance_1", {}).get("kg_co2e", 0) / 1000.0,
        "alcance_2": por_alcance.get("alcance_2", {}).get("kg_co2e", 0) / 1000.0,
        "alcance_3": por_alcance.get("alcance_3", {}).get("kg_co2e", 0) / 1000.0,
        "total": (huella or {}).get("total_t_co2e", 0.0),
    }


def trayectoria(opciones):
    """Calcula la trayectoria de reduccion ano por ano hasta la meta."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardada = _leer_meta(ruta_json)
    huella = _ultima_huella(ruta)
    emisiones = _emisiones_de_la_huella(huella)

    base = _valor(opciones, "base") or guardada.get("emisiones_base")
    if base in (None, ""):
        base = (emisiones["alcance_1"] + emisiones["alcance_2"]) or None
    if not base:
        raise Problema(
            "No se cuantas toneladas emitio la empresa en el año base.",
            "Calcula primero la huella (huella calcular) o indicame el valor con --base.",
        )
    anio_base = int(_valor(opciones, "anio_base") or guardada.get("anio_base") or perfil.get("anio_base") or 0)
    anio_meta = int(_valor(opciones, "anio_meta") or guardada.get("anio_meta") or 0)
    if not anio_base or not anio_meta:
        raise Problema(
            "Falta el año base o el año de la meta.",
            "Por ejemplo: --anio-base 2025 --anio-meta 2030.",
        )
    tasa = float(_valor(opciones, "tasa") or guardada.get("tasa") or motor_metas.TASA_ALCANCE_1_2)
    resultado = motor_metas.trayectoria(base, anio_base, anio_meta, tasa)
    resultado["largo_plazo"] = motor_metas.meta_largo_plazo(base)
    resultado["emisiones_actuales"] = emisiones
    return Respuesta(resultado, advertencias=[AVISO])


def definir(opciones):
    """Define la meta de reduccion y la guarda en el seguimiento."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardada = _leer_meta(ruta_json)
    huella = _ultima_huella(ruta)
    emisiones = _emisiones_de_la_huella(huella)

    datos = dict(guardada)
    for clave in ("anio_base", "anio_meta"):
        valor = _valor(opciones, clave)
        if valor:
            datos[clave] = int(valor)
    base_indicada = _valor(opciones, "emisiones_base") or _valor(opciones, "base")
    if base_indicada not in (None, ""):
        datos["emisiones_base"] = float(str(base_indicada).replace(",", "."))
    for clave in ("tasa", "cobertura_alcance_3", "exclusiones_pct"):
        valor = _valor(opciones, clave)
        if valor not in (None, ""):
            datos[clave] = float(str(valor).replace(",", "."))
    reduccion = _valor(opciones, "reduccion")
    if reduccion not in (None, ""):
        # La gente dice «bajar 42 % al 2030», no «8,4 % lineal al año».
        porcentaje = float(str(reduccion).replace(",", ".").replace("%", ""))
        if porcentaje <= 0 or porcentaje > 100:
            raise Problema("La reduccion %s %% no tiene sentido." % reduccion,
                           "Escribela como porcentaje entre 1 y 100, por ejemplo --reduccion 42.")
        anio_base_reduccion = datos.get("anio_base") or perfil.get("anio_base")
        if not datos.get("anio_meta") or not anio_base_reduccion:
            raise Problema("Para convertir la reduccion en una trayectoria necesito el año base y el año meta.",
                           "Por ejemplo: --reduccion 42 --anio-base 2025 --anio-meta 2030.")
        datos["tasa"] = porcentaje / 100.0 / (int(datos["anio_meta"]) - int(anio_base_reduccion))
        datos["reduccion_pedida_pct"] = porcentaje
    if _valor(opciones, "alcances"):
        datos["alcances"] = _valor(opciones, "alcances")
    if opciones.get("meta_alcance_3"):
        datos["meta_alcance_3"] = True
    if _valor(opciones, "descripcion"):
        datos["descripcion"] = _valor(opciones, "descripcion")

    datos.setdefault("anio_base", perfil.get("anio_base"))
    datos.setdefault("alcances", "1 y 2")
    if "emisiones_base" not in datos and emisiones["total"]:
        datos["emisiones_base"] = round(emisiones["alcance_1"] + emisiones["alcance_2"], 2)
    datos["emisiones_por_alcance"] = emisiones
    if not datos.get("anio_meta"):
        raise Problema("Falta el año en que se quiere cumplir la meta.",
                       "Por ejemplo: --anio-meta 2030.")
    if not datos.get("emisiones_base"):
        raise Problema(
            "No se desde que nivel de emisiones parte la meta.",
            "Calcula primero la huella del año base (huella calcular) o indicalo con --base 12500.")
    if not datos.get("anio_base"):
        raise Problema("Falta el año base de la meta.",
                       "Es el año contra el que se compara la reduccion, por ejemplo --anio-base 2025.")

    resultado = motor_metas.trayectoria(datos["emisiones_base"], datos["anio_base"],
                                        datos["anio_meta"], datos.get("tasa", motor_metas.TASA_ALCANCE_1_2))
    datos["emisiones_meta"] = resultado["emisiones_meta"]
    _guardar_meta(ruta_json, datos)
    validacion = motor_metas.validar_meta({
        "anio_base": datos["anio_base"], "anio_meta": datos["anio_meta"],
        "alcance_1": emisiones["alcance_1"], "alcance_2": emisiones["alcance_2"],
        "alcance_3": emisiones["alcance_3"],
        "meta_alcance_3": datos.get("meta_alcance_3"),
        "cobertura_alcance_3": datos.get("cobertura_alcance_3"),
        "exclusiones_pct": datos.get("exclusiones_pct"),
        "usa_creditos": datos.get("usa_creditos"),
    })
    return Respuesta(
        {"mensaje": "Meta guardada: reducir de %s a %s tCO2e entre %s y %s."
                    % (datos["emisiones_base"], datos["emisiones_meta"], datos["anio_base"], datos["anio_meta"]),
         "meta": datos, "trayectoria": resultado["trayectoria"], "revision": validacion},
        advertencias=[AVISO] + [r["detalle"] for r in validacion["pendientes"]])


def validar(opciones):
    """Revisa si la meta cumple los criterios de un objetivo creible."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer_meta(ruta_json)
    if not datos:
        raise Problema("Todavia no hay una meta definida.",
                       "Definela con: meta definir --anio-meta 2030.")
    emisiones = datos.get("emisiones_por_alcance") or _emisiones_de_la_huella(_ultima_huella(ruta))
    validacion = motor_metas.validar_meta({
        "anio_base": datos.get("anio_base"), "anio_meta": datos.get("anio_meta"),
        "alcance_1": emisiones.get("alcance_1", 0), "alcance_2": emisiones.get("alcance_2", 0),
        "alcance_3": emisiones.get("alcance_3", 0),
        "meta_alcance_3": datos.get("meta_alcance_3"),
        "cobertura_alcance_3": datos.get("cobertura_alcance_3"),
        "exclusiones_pct": datos.get("exclusiones_pct"),
        "usa_creditos": datos.get("usa_creditos"),
    })
    return Respuesta(validacion, advertencias=[validacion["aviso"]])


def probabilidad(opciones):
    """Estima que tan probable es cumplir la meta, simulando muchos escenarios."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer_meta(ruta_json)
    if not datos.get("emisiones_meta"):
        raise Problema("Necesito una meta definida para estimar la probabilidad.",
                       "Definela con: meta definir --anio-meta 2030.")
    configuracion = dict(datos.get("simulacion") or {})
    configuracion.setdefault("emisiones_actuales", datos.get("emisiones_base"))
    configuracion.setdefault("anio_inicio", datos.get("anio_base"))
    configuracion.setdefault("anio_meta", datos.get("anio_meta"))
    configuracion["emisiones_meta"] = datos["emisiones_meta"]
    archivo_config = _valor(opciones, "supuestos")
    if archivo_config:
        if not os.path.isfile(archivo_config):
            raise Problema("No encontre el archivo de supuestos: %s" % archivo_config,
                           "Debe ser un archivo JSON con las distribuciones.")
        with open(archivo_config, encoding="utf-8") as archivo:
            configuracion.update(json.load(archivo))
    iteraciones = int(_valor(opciones, "iteraciones") or 20000)
    resultado = motor_metas.monte_carlo(configuracion, iteraciones=iteraciones)
    datos["simulacion"] = {clave: configuracion[clave] for clave in
                           ("crecimiento", "descarbonizacion_red", "eficiencia", "proyectos")
                           if clave in configuracion}
    datos["ultima_probabilidad"] = {"probabilidad_pct": resultado["probabilidad_pct"],
                                    "lectura": resultado["lectura"],
                                    "brecha_mediana": resultado["brecha_mediana"]}
    _guardar_meta(ruta_json, datos)
    return Respuesta(resultado, advertencias=[resultado["aviso"], AVISO])


# Opciones que definir y trayectoria leen recorriendo tuplas de claves: se declaran para la ayuda.
OPCIONES_DINAMICAS = {
    "definir": ["anio_base", "anio_meta", "tasa", "reduccion", "cobertura_alcance_3", "exclusiones_pct"],
}


def _leer_medidas(ruta_empresa):
    # El mismo nombre que crea «plantilla crear --tipo medidas». Antes se buscaba otro
    # (medidas_reduccion.xlsx) y el plan nunca encontraba la planilla: se sigue leyendo por si existe.
    ruta = espacio.ruta_de(ruta_empresa, "datos", "medidas.xlsx")
    anterior = espacio.ruta_de(ruta_empresa, "datos", "medidas_reduccion.xlsx")
    if not os.path.isfile(ruta) and os.path.isfile(anterior):
        ruta = anterior
    if not os.path.isfile(ruta):
        raise Problema(
            "No encontre la planilla de medidas de reduccion.",
            "Crea la planilla con: plantilla crear --tipo medidas, y anota que acciones evaluan.",
        )
    tabla = excel.leer_tabla(ruta)
    _, definicion = definiciones.obtener("medidas")
    medidas = []
    ejemplos = 0
    for fila in tabla["filas"]:
        # Las filas de ejemplo son de una empresa inventada: no pueden entrar al plan.
        if definiciones.es_fila_de_ejemplo(definicion, fila):
            ejemplos += 1
            continue
        medidas.append({
            "medida": fila.get("medida") or fila.get("accion") or fila.get("nombre"),
            "capex": fila.get("inversion_capex") or fila.get("inversion") or fila.get("capex"),
            "opex": fila.get("costo_anual_opex") or fila.get("costo_anual") or fila.get("opex"),
            "ahorros": fila.get("ahorro_anual") or fila.get("ahorros"),
            "vida_util": fila.get("vida_util_anos") or fila.get("vida_util") or 10,
            "tco2e_evitadas": fila.get("tco2e_evitadas_al_ano") or fila.get("tco2e_evitadas"),
            "notas": fila.get("notas") or "",
            "_fila": fila.get("_fila"),
        })
    if ejemplos and not medidas:
        raise Problema(
            "La planilla de medidas solo tiene las filas de ejemplo que trae la plantilla.",
            "Reemplazalas por las medidas que la empresa esta evaluando, con sus cotizaciones, y vuelve a intentarlo.",
            {"archivo": ruta},
        )
    return medidas, ruta, ejemplos


def plan(opciones):
    """Curva de costos de abatimiento con las medidas cargadas."""
    perfil, ruta, ruta_json = _contexto(opciones)
    medidas, archivo, ejemplos = _leer_medidas(ruta)
    datos = _leer_meta(ruta_json)
    brecha = _valor(opciones, "brecha") or (datos.get("ultima_probabilidad") or {}).get("brecha_mediana")
    tasa = float(_valor(opciones, "tasa_descuento") or 0.10)
    resultado = motor_macc.curva(medidas, tasa_descuento=tasa, brecha=brecha)
    resultado["archivo"] = archivo
    advertencias = [
        "Los costos dependen de las cotizaciones que cargaste: revisalas antes de decidir una inversion.",
        AVISO]
    if ejemplos:
        advertencias.insert(0, "Deje fuera %d fila(s) de ejemplo de la plantilla: no son medidas de la empresa. "
                               "Borralas de la planilla cuando puedas." % ejemplos)
    return Respuesta(resultado, advertencias=advertencias)


def informe_html(opciones):
    """Arma el informe HTML de la meta y su trayectoria."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer_meta(ruta_json)
    if not datos:
        raise Problema("Todavia no hay una meta definida.",
                       "Definela con: meta definir --anio-meta 2030 y vuelve a intentarlo.")
    calculo = motor_metas.trayectoria(datos["emisiones_base"], datos["anio_base"], datos["anio_meta"],
                                      datos.get("tasa", motor_metas.TASA_ALCANCE_1_2))
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Emisiones año base", "valor": calculo["emisiones_base"], "unidad": "tCO2e",
             "detalle": "Año %s" % datos["anio_base"]},
            {"etiqueta": "Meta", "valor": calculo["emisiones_meta"], "unidad": "tCO2e",
             "detalle": "Año %s" % datos["anio_meta"], "color": "verde"},
            {"etiqueta": "Reduccion", "valor": calculo["reduccion_total_pct"], "unidad": "%",
             "detalle": "%.1f%% anual lineal" % calculo["tasa_anual_lineal_pct"]},
        ]},
        {"tipo": "lineas", "titulo": "Trayectoria de la meta", "unidad": "tCO2e",
         "series": [{"nombre": "Maximo permitido",
                     "puntos": [(str(f["anio"]), f["emisiones_permitidas"]) for f in calculo["trayectoria"]]}]},
        {"tipo": "tabla", "columnas": ["Año", "Reduccion acumulada (%)", "Emisiones permitidas (tCO2e)"],
         "numericas": [1, 2],
         "filas": [[f["anio"], f["reduccion_acumulada_pct"], f["emisiones_permitidas"]]
                   for f in calculo["trayectoria"]]},
    ]
    probabilidad_guardada = datos.get("ultima_probabilidad")
    if probabilidad_guardada:
        bloques.append({"tipo": "titulo", "texto": "Probabilidad de cumplir", "nivel": 2})
        pct = probabilidad_guardada.get("probabilidad_pct")
        if pct is None:
            bloques.append({"tipo": "nota", "estilo": "aviso",
                            "texto": probabilidad_guardada.get("lectura") or
                            "Todavia no hay supuestos para estimar una probabilidad: faltan las medidas de "
                            "reduccion y cuanto se espera que crezca la empresa."})
        bloques.append({"tipo": "kpi", "items": [
            {"etiqueta": "Probabilidad estimada", "valor": pct if pct is not None else "sin estimar",
             "unidad": "%" if pct is not None else "",
             "color": "gris" if pct is None else ("verde" if pct >= 80 else "amarillo")},
            {"etiqueta": "Brecha mediana", "valor": probabilidad_guardada["brecha_mediana"], "unidad": "tCO2e",
             "detalle": "Lo que falta cubrir con medidas"},
        ]})
    bloques.append({"tipo": "nota", "estilo": "aviso", "texto": AVISO})
    destino = espacio.ruta_de(ruta, "reportes", "meta-reduccion.html")
    informe.escribir_html(destino, "Meta de reduccion de emisiones", bloques,
                          marca=perfil.get("marca") or {},
                          subtitulo="%s - meta %s" % (perfil.get("nombre", ""), datos["anio_meta"]))
    return {"mensaje": "Informe de la meta listo.", "archivo": destino}


ACCIONES = {"trayectoria": trayectoria, "definir": definir, "validar": validar,
            "probabilidad": probabilidad, "plan": plan, "informe": informe_html}
