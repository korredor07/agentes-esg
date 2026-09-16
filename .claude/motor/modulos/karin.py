# -*- coding: utf-8 -*-
"""Ley Karin: casos, plazos legales y documentos base."""

import datetime
import json
import os

from calculos import karin as motor_karin
from nucleo import espacio, fechas, word
from nucleo.salida import Problema, Respuesta

AYUDA = "Gestiona denuncias de acoso y violencia laboral (Ley 21.643): plazos, seguimiento y documentos."

CARPETA = "karin"
ARCHIVO = "casos.json"
AVISO_PRIVACIDAD = ("Este caso contiene datos sensibles de personas. Se guarda solo en este computador, "
                    "nunca se publica y conviene usar iniciales o un codigo en vez de nombres completos.")
AVISO_LEGAL = ("Orientacion de apoyo, no asesoria legal. Los plazos de la Ley Karin son perentorios: "
               "ante una denuncia real, involucra a la asesoria juridica y al organismo administrador "
               "de la Ley 16.744.")


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    carpeta = espacio.ruta_de(ruta, "seguimiento", CARPETA)
    if not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    return perfil, ruta, os.path.join(carpeta, ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"casos": []}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema("El archivo de casos Ley Karin esta dañado.",
                           "No lo edites a mano. Puedo ayudarte a reconstruirlo con los datos que tengas.")
    for caso in datos.get("casos") or []:
        _migrar(caso)
    datos.setdefault("casos", [])
    return datos


def _migrar(caso):
    """Pone al dia lo que guardo la version anterior, sin inventar: lo que no se entiende queda como error visible."""
    avisos = []
    caso.setdefault("eventos", {})
    caso.setdefault("bitacora", [])
    via = caso.get("via")
    if via not in (None, "", "interna", "derivada"):
        interpretada = motor_karin.interpretar_via_guardada(via)
        if interpretada:
            avisos.append("La via guardada «%s» se leyo como «%s». Si no es asi, corrigela con: karin actualizar "
                          "--caso %s --via interna|derivada." % (via, interpretada, caso.get("id")))
            caso["via"] = interpretada
    for clave in ("fecha_denuncia",):
        if caso.get(clave):
            try:
                caso[clave] = fechas.parsear_fecha(caso[clave]).isoformat()
            except Problema:
                pass  # _calcular lo informa con el nombre del campo
    for clave, valor in list(caso["eventos"].items()):
        if valor:
            try:
                caso["eventos"][clave] = fechas.parsear_fecha(valor).isoformat()
            except Problema:
                pass  # _calcular lo informa con el nombre del hito
    if avisos:
        caso["_avisos_de_lectura"] = avisos


def _guardar(ruta_json, datos):
    limpios = {"casos": [{clave: valor for clave, valor in caso.items() if not clave.startswith("_avisos")}
                         for caso in datos.get("casos") or []]}
    limpios.update({clave: valor for clave, valor in datos.items() if clave != "casos"})
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(limpios, archivo, ensure_ascii=False, indent=2)


def _buscar(datos, identificador):
    for caso in datos["casos"]:
        if caso["id"].lower() == str(identificador or "").lower():
            return caso
    raise Problema(
        "No encontre el caso «%s»." % identificador,
        "Casos registrados: %s." % (", ".join(c["id"] for c in datos["casos"]) or "ninguno todavia"),
    )


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


SI = ("si", "s", "yes", "true", "1")
NO = ("no", "n", "false", "0")
NO_SE = ("no se", "nose", "no lo se", "no sabe", "desconocido", "sin informacion", "?")


def _si_no(opciones, clave):
    """Respuesta si, no o no se.

    Una opcion sin valor (--contra-representante) es «si», como en todo el motor. Un texto
    que no se entiende no se adivina: de esta respuesta depende si la empresa puede investigar.
    """
    valor = opciones.get(clave)
    if valor is None:
        return None
    if valor is True:
        return True
    texto = motor_karin.sin_tildes(str(valor).strip().lower())
    if texto in SI:
        return True
    if texto in NO:
        return False
    if not texto or texto in NO_SE:
        return None
    raise Problema(
        "No entiendo la respuesta «%s» de --%s." % (valor, clave.replace("_", "-")),
        "Responde si, no o no se. De esa respuesta depende si la empresa puede investigar o tiene que derivar "
        "la denuncia a la Direccion del Trabajo.",
    )


def _calcular(caso, hoy=None):
    identificador = caso.get("id", "sin identificador")
    if not caso.get("fecha_denuncia"):
        raise Problema("El caso %s no tiene la fecha de la denuncia." % identificador,
                       "Es el dato del que salen todos los plazos: hay que reconstruir el caso con esa fecha.")
    try:
        fechas.parsear_fecha(caso["fecha_denuncia"])
    except Problema:
        raise Problema("En el caso %s, la fecha de la denuncia guardada no se entiende: «%s»."
                       % (identificador, caso["fecha_denuncia"]),
                       "Es el dato del que salen todos los plazos: hay que corregirla antes de seguir.")
    for clave, valor in (caso.get("eventos") or {}).items():
        if not valor:
            continue
        try:
            fechas.parsear_fecha(valor)
        except Problema:
            raise Problema("En el caso %s, la fecha guardada de %s no se entiende: «%s»."
                           % (identificador, motor_karin.titulo_de(clave), valor),
                           "Corrigela con: karin evento --caso %s --hito %s --fecha <fecha>." % (identificador, clave))
    try:
        motor_karin.normalizar_via(caso.get("via"))
    except Problema:
        raise Problema("En el caso %s, la via guardada «%s» no se entiende." % (identificador, caso.get("via")),
                       "Corrigela con: karin actualizar --caso %s --via interna|derivada." % identificador)
    return motor_karin.plazos(caso["fecha_denuncia"], caso.get("eventos") or {}, caso.get("region") or None, hoy=hoy,
                              via=caso.get("via"), reglamento_actualizado=caso.get("reglamento_actualizado"),
                              contra_representante=caso.get("contra_representante"))


URGENTES = ("pendiente: debe hacerse de inmediato", "vencido", "por vencer", "en plazo")


def _proximos(calculo, cantidad=3):
    """Lo que sigue. Derivar, o confirmar si hay que derivar, va primero: decide todo lo demas."""
    pendientes = [h for h in calculo["hitos"]
                  if h.get("aplica", True) and not h["cumplido_el"]
                  and (h["estado"] in URGENTES or h["estado"].startswith("pendiente"))]
    pendientes.sort(key=lambda h: 0 if h["id"] in ("derivar_dt", "confirmar_derivacion") else 1)
    return pendientes[:cantidad]


def _derivada(caso):
    return motor_karin.normalizar_via(caso.get("via")) == "derivada" or bool((caso.get("eventos") or {}).get("derivacion_dt"))


def _avisos_de_derivacion(caso, calculo):
    """El aviso de derivar no sale una sola vez: acompaña al caso hasta que se registra."""
    if calculo["camino"] == "derivada" and not _derivada(caso):
        return ["IMPORTANTE: %s No corresponde investigar internamente. Cuando la envies, registralo con: "
                "karin evento --caso %s --hito derivacion_dt --fecha <fecha>. Cuando llegue el certificado de "
                "recepcion de la DT, con --hito recepcion_dt." % (calculo["motivo_derivacion"], caso["id"])]
    if calculo["camino"] == "interna" and calculo["derivacion_obligatoria"] is None:
        return ["Antes de investigar internamente: %s Registra las respuestas con: karin actualizar --caso %s "
                "--reglamento-actualizado si|no --contra-representante si|no."
                % (calculo["motivo_derivacion"], caso["id"])]
    return []


def crear(opciones):
    """Abre un caso nuevo y calcula todos sus plazos legales."""
    perfil, ruta, ruta_json = _contexto(opciones)
    fecha = _valor(opciones, "fecha_denuncia")
    if not fecha:
        raise Problema(
            "Falta la fecha en que se recibio la denuncia.",
            "Es la fecha clave: de ahi salen todos los plazos. Usa --fecha-denuncia 15-09-2026.",
        )
    fecha = fechas.parsear_fecha(fecha).isoformat()
    datos = _leer(ruta_json)
    anio = fecha[:4]
    correlativo = len([c for c in datos["casos"] if c["id"].startswith("KARIN-%s" % anio)]) + 1
    caso = {
        "id": "KARIN-%s-%03d" % (anio, correlativo),
        "fecha_denuncia": fecha,
        "tipo": _valor(opciones, "tipo", "acoso laboral"),
        "via": motor_karin.normalizar_via(_valor(opciones, "via", "interna")),
        "anonima": bool(opciones.get("anonima")),
        "sitio": _valor(opciones, "sitio"),
        "region": _valor(opciones, "region"),
        "denunciante": _valor(opciones, "denunciante"),
        "denunciado": _valor(opciones, "denunciado"),
        "investigador": _valor(opciones, "investigador"),
        "resumen": _valor(opciones, "resumen"),
        "reglamento_actualizado": _si_no(opciones, "reglamento_actualizado"),
        "contra_representante": _si_no(opciones, "contra_representante"),
        "estado": "en investigacion",
        "eventos": {},
        "bitacora": [{"fecha": datetime.date.today().isoformat(), "nota": "Caso registrado en el sistema."}],
        "creado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
    # Se calcula antes de guardar: si un dato esta mal, no queda un caso a medias que rompa a los demas.
    calculo = _calcular(caso)
    caso["derivacion_obligatoria"] = calculo["derivacion_obligatoria"]
    datos["casos"].append(caso)
    _guardar(ruta_json, datos)
    return Respuesta(
        {"mensaje": "Caso %s registrado." % caso["id"], "caso": caso["id"], "camino": calculo["camino"],
         "derivacion_obligatoria": calculo["derivacion_obligatoria"],
         "motivo_derivacion": calculo["motivo_derivacion"],
         "proximos_pasos": _proximos(calculo),
         "plazos": calculo["hitos"], "supuesto": calculo["supuesto"]},
        advertencias=_avisos_de_derivacion(caso, calculo) + [AVISO_PRIVACIDAD, AVISO_LEGAL])


def actualizar(opciones):
    """Registra o corrige las respuestas que deciden si la denuncia se deriva a la Direccion del Trabajo."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    caso = _buscar(datos, _valor(opciones, "caso"))
    cambios = {clave: _si_no(opciones, clave) for clave in ("reglamento_actualizado", "contra_representante")
               if clave in opciones}
    if "via" in opciones:
        via = motor_karin.normalizar_via(_valor(opciones, "via"))
        if via == "interna" and (caso.get("eventos") or {}).get("derivacion_dt"):
            raise Problema("El caso %s tiene registrada la derivacion a la Direccion del Trabajo." % caso["id"],
                           "Si fue un error, la fecha de derivacion hay que corregirla; no se puede volver a "
                           "investigacion interna con una derivacion registrada.")
        cambios["via"] = via
    if not cambios:
        raise Problema("No me dijiste que actualizar.",
                       "Usa --reglamento-actualizado si|no|no se, --contra-representante si|no|no se o "
                       "--via interna|derivada.")
    calculo = _calcular(dict(caso, **cambios))
    caso.update(cambios)
    caso["derivacion_obligatoria"] = calculo["derivacion_obligatoria"]
    caso["bitacora"].append({
        "fecha": datetime.date.today().isoformat(),
        "nota": "Respuestas actualizadas: %s." % ", ".join(
            "%s = %s" % (clave.replace("_", " "),
                         valor if clave == "via" else {True: "si", False: "no", None: "no se"}[valor])
            for clave, valor in sorted(cambios.items()))})
    _guardar(ruta_json, datos)
    return Respuesta(
        {"mensaje": "Caso %s actualizado." % caso["id"], "caso": caso["id"], "camino": calculo["camino"],
         "derivacion_obligatoria": calculo["derivacion_obligatoria"],
         "motivo_derivacion": calculo["motivo_derivacion"],
         "proximos_pasos": _proximos(calculo), "plazos": calculo["hitos"]},
        advertencias=list(caso.get("_avisos_de_lectura") or []) + _avisos_de_derivacion(caso, calculo)
        + [AVISO_LEGAL])


def evento(opciones):
    """Registra un hito del caso (derivacion, notificacion, informe, resolucion) y recalcula los plazos."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    caso = _buscar(datos, _valor(opciones, "caso"))
    hito = motor_karin.validar_evento(_valor(opciones, "hito"))
    avisos_fecha = []
    if opciones.get("fecha") is True:
        raise Problema("Falta la fecha en que ocurrio el hito.", "Escribela asi: --fecha 17-09-2026.")
    if opciones.get("fecha") in (None, ""):
        avisos_fecha.append("No indicaste --fecha: registre la de hoy. Si ocurrio otro dia, vuelve a registrarlo "
                            "con la fecha correcta.")
    fecha = fechas.parsear_fecha(_valor(opciones, "fecha") or datetime.date.today().isoformat()).isoformat()
    # La fecha que se registra reemplaza a la guardada: asi se corrige una fecha que no se entendia.
    correccion = hito["id"] in (caso.get("eventos") or {})
    antes = _calcular(dict(caso, eventos={clave: valor for clave, valor in (caso.get("eventos") or {}).items()
                                          if clave != hito["id"]}))
    if not correccion and hito["id"] in motor_karin.SOLO_DERIVADA and not _derivada(caso):
        raise Problema(
            "«%s» solo existe si la denuncia se derivo a la Direccion del Trabajo, y el caso %s no figura derivado."
            % (hito["titulo"], caso["id"]),
            "Si la derivaste, registra primero: karin evento --caso %s --hito derivacion_dt --fecha <fecha en que "
            "la enviaste>. Si es el certificado de recepcion del informe de tu investigacion interna, registralo "
            "con --hito remision_informe." % caso["id"])
    if not correccion and hito["id"] in motor_karin.SOLO_INTERNA and antes["camino"] == "derivada":
        raise Problema(
            "«%s» no corresponde: la denuncia del caso %s %s." % (
                hito["titulo"], caso["id"],
                "se derivo a la Direccion del Trabajo, que es quien investiga" if _derivada(caso)
                else "debe derivarse a la Direccion del Trabajo"),
            "En una denuncia derivada se registran: derivacion_dt, recepcion_dt, conclusiones_dt y aplicar_medidas.")
    prueba = dict(caso, eventos=dict(caso.get("eventos") or {}, **{hito["id"]: fecha}))
    if hito["id"] == "derivacion_dt":
        prueba["via"] = "derivada"
    # Se calcula antes de guardar: una fecha que no se entiende no puede quedar grabada.
    calculo = _calcular(prueba)
    caso.update(prueba)
    nota = _valor(opciones, "nota")
    caso["bitacora"].append({"fecha": datetime.date.today().isoformat(),
                             "nota": "%s: %s.%s" % (hito["titulo"], fecha, " " + nota if nota else "")})
    if hito["id"] == "aplicar_medidas":
        caso["estado"] = "cerrado"
    _guardar(ruta_json, datos)
    pendientes = [h for h in calculo["hitos"] if h.get("aplica", True) and not h["cumplido_el"]]
    return Respuesta(
        {"mensaje": "Registrado: %s el %s." % (hito["titulo"], fecha),
         "caso": caso["id"], "estado_caso": caso["estado"], "camino": calculo["camino"],
         "siguiente": pendientes[0] if pendientes else None,
         "plazos": calculo["hitos"]},
        advertencias=list(caso.get("_avisos_de_lectura") or []) + avisos_fecha + _avisos_de_derivacion(caso, calculo)
        + [AVISO_LEGAL])


def ver(opciones):
    """Muestra un caso con sus plazos, que sigue y cuanto queda."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    caso = _buscar(datos, _valor(opciones, "caso"))
    calculo = _calcular(caso, hoy=_valor(opciones, "hoy") or None)
    visible = {clave: valor for clave, valor in caso.items() if not clave.startswith("_avisos")}
    visible["derivacion_obligatoria"] = calculo["derivacion_obligatoria"]
    return Respuesta(
        {"caso": visible, "camino": calculo["camino"], "derivacion_obligatoria": calculo["derivacion_obligatoria"],
         "motivo_derivacion": calculo["motivo_derivacion"], "plazos": calculo["hitos"],
         "vencidos": calculo["vencidos"], "por_vencer": calculo["por_vencer"], "supuesto": calculo["supuesto"],
         "nota_feriados": calculo["nota_feriados"]},
        advertencias=list(caso.get("_avisos_de_lectura") or []) + _avisos_de_derivacion(caso, calculo)
        + [AVISO_PRIVACIDAD, AVISO_LEGAL])


def listar(opciones):
    """Lista los casos abiertos y cual tiene el plazo mas urgente."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    resumen = []
    for caso in datos["casos"]:
        try:
            calculo = _calcular(caso)
        except Problema as error:
            # Un caso con un dato dañado no esconde a los demas, y tampoco se esconde el.
            resumen.append({"id": caso.get("id"), "fecha_denuncia": caso.get("fecha_denuncia"),
                            "tipo": caso.get("tipo"), "estado": caso.get("estado"),
                            "error": "%s %s" % (error.mensaje, error.sugerencia)})
            continue
        cerrado = caso.get("estado") == "cerrado"
        resumen.append({
            "id": caso["id"], "fecha_denuncia": caso["fecha_denuncia"], "tipo": caso.get("tipo"),
            "estado": caso.get("estado"), "camino": calculo["camino"],
            # Un caso cerrado no tiene plazos que vencer, aunque se hayan saltado hitos al registrarlo.
            "vencidos": 0 if cerrado else len(calculo["vencidos"]),
            "por_vencer": 0 if cerrado else len(calculo["por_vencer"]),
            "siguiente": next((h["titulo"] for h in calculo["hitos"]
                               if h.get("aplica", True) and not h["cumplido_el"]), None),
        })
    con_error = len([c for c in resumen if c.get("error")])
    mensaje = "Sin casos registrados." if not resumen else "%d caso(s) registrados." % len(resumen)
    if con_error:
        mensaje += " %d con datos que hay que revisar." % con_error
    return {"total": len(resumen), "con_error": con_error, "casos": resumen, "mensaje": mensaje}


def alertas(opciones):
    """Deja en seguimiento/alertas.json los plazos que vencen, para el tablero."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    pendientes = []
    hoy = datetime.date.today().isoformat()
    for caso in datos["casos"]:
        if caso.get("estado") == "cerrado":
            continue
        try:
            calculo = _calcular(caso)
        except Problema as error:
            pendientes.append({
                "origen": "Ley Karin", "caso": caso.get("id"),
                "titulo": "Revisar los datos del caso %s" % caso.get("id"),
                "vence": datetime.date.today().isoformat(), "estado": "error", "por_vencer": False,
                "detalle": "No se pudieron calcular sus plazos: %s %s" % (error.mensaje, error.sugerencia),
                "articulo": "",
            })
            continue
        # Si no se sabe si hay que derivar, los plazos de la investigacion interna son condicionales.
        condicional = calculo["camino"] == "interna" and calculo["derivacion_obligatoria"] is None
        for hito in calculo["hitos"]:
            if not hito.get("aplica", True) or hito["cumplido_el"] or hito["proyectado"]:
                continue
            if not hito["vence"]:
                if hito["estado"].startswith("pendiente"):
                    # Por ejemplo, una denuncia derivada que espera el certificado de la DT: no puede quedar invisible.
                    pendientes.append({
                        "origen": "Ley Karin", "caso": caso["id"], "titulo": "%s (%s)" % (hito["titulo"], caso["id"]),
                        "vence": hoy, "estado": "pendiente", "por_vencer": True,
                        "detalle": hito["que_hacer"], "articulo": hito["articulo"],
                    })
                continue
            if hito["estado"] in ("vencido", "por vencer", "pendiente: debe hacerse de inmediato"):
                prefijo = ("Solo si no corresponde derivar: " if condicional
                           and hito["id"] not in ("medidas_resguardo", "confirmar_derivacion") else "")
                pendientes.append({
                    "origen": "Ley Karin", "caso": caso["id"],
                    "titulo": "%s%s (%s)" % (prefijo, hito["titulo"], caso["id"]),
                    "vence": hito["vence"], "estado": hito["estado"],
                    "por_vencer": hito["estado"] == "por vencer",
                    "detalle": hito["que_hacer"], "articulo": hito["articulo"],
                })
    archivo = espacio.ruta_de(ruta, "seguimiento", "alertas.json")
    otras = []
    avisos = [AVISO_LEGAL] if pendientes else []
    if os.path.isfile(archivo):
        try:
            with open(archivo, encoding="utf-8") as origen:
                otras = [a for a in json.load(origen) if a.get("origen") != "Ley Karin"]
        except ValueError:
            otras = []
            avisos.append("El archivo de alertas estaba dañado y se rehizo solo con los plazos de Ley Karin. "
                          "Las demas alertas vuelven con: calendario proximas.")
    with open(archivo, "w", encoding="utf-8") as destino:
        json.dump(otras + pendientes, destino, ensure_ascii=False, indent=2)
    return Respuesta(
        {"total": len(pendientes), "alertas": pendientes, "archivo": archivo,
         "mensaje": "Sin plazos criticos de Ley Karin." if not pendientes else
                    "Hay %d plazo(s) de Ley Karin que requieren atencion." % len(pendientes)},
        advertencias=avisos)


def _bloques_protocolo(perfil):
    nombre = perfil.get("nombre", "la empresa")
    return [
        {"tipo": "titulo", "texto": "Protocolo de prevencion del acoso sexual, laboral y la violencia en el trabajo",
         "nivel": 0},
        {"tipo": "texto", "texto": "%s — Version 1 — Fecha: ____________" % nombre},
        {"tipo": "nota", "texto": "Borrador base para completar con el organismo administrador de la Ley 16.744 "
                                  "al que esta afiliada la empresa. Los textos entre corchetes deben reemplazarse."},
        {"tipo": "titulo", "texto": "1. Objetivo y alcance", "nivel": 1},
        {"tipo": "texto", "texto": "Este protocolo establece las medidas que %s adopta para prevenir, investigar y "
                                   "sancionar el acoso sexual, el acoso laboral y la violencia en el trabajo, "
                                   "incluida la ejercida por terceros ajenos a la relacion laboral. Aplica a todas "
                                   "las personas trabajadoras, en todos los lugares y modalidades de trabajo." % nombre},
        {"tipo": "titulo", "texto": "2. Definiciones", "nivel": 1},
        {"tipo": "lista", "items": [
            "Acoso laboral: agresion u hostigamiento, ejercido por el empleador o por una o mas personas "
            "trabajadoras, por cualquier medio, que produzca menoscabo, maltrato o humillacion, o amenace o "
            "perjudique la situacion laboral u oportunidades de empleo. Basta un solo acto.",
            "Acoso sexual: requerimientos de caracter sexual no consentidos que amenacen o perjudiquen la "
            "situacion laboral u oportunidades de empleo.",
            "Violencia en el trabajo: conductas ejercidas por terceros ajenos a la relacion laboral, como "
            "clientes, proveedores o usuarios.",
        ]},
        {"tipo": "titulo", "texto": "3. Identificacion de peligros y evaluacion de riesgos psicosociales", "nivel": 1},
        {"tipo": "texto", "texto": "[Describir como se identifican los peligros y se evaluan los riesgos "
                                   "psicosociales, con perspectiva de genero, incluyendo la aplicacion del "
                                   "instrumento que indique el organismo administrador y la periodicidad.]"},
        {"tipo": "titulo", "texto": "4. Medidas de prevencion y control con objetivos medibles", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Riesgo identificado", "Medida", "Objetivo medible", "Responsable", "Plazo"],
         "filas": [["[Riesgo]", "[Medida]", "[Indicador y meta]", "[Cargo]", "[Fecha]"],
                   ["", "", "", "", ""], ["", "", "", "", ""]]},
        {"tipo": "titulo", "texto": "5. Informacion y capacitacion", "nivel": 1},
        {"tipo": "texto", "texto": "[Detallar como se informa y capacita sobre los riesgos, las medidas de "
                                   "prevencion y proteccion, y los derechos y responsabilidades. Incluir "
                                   "frecuencia, medios y registro de asistencia.]"},
        {"tipo": "titulo", "texto": "6. Canales de denuncia", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar los canales internos: persona o cargo responsable, correo, formulario "
                                   "y forma de presentar la denuncia verbal o escrita. Indicar tambien que se puede "
                                   "denunciar ante la Inspeccion del Trabajo.] La empresa informara estos canales "
                                   "al menos cada seis meses."},
        {"tipo": "titulo", "texto": "7. Procedimiento de investigacion y sancion", "nivel": 1},
        {"tipo": "lista", "ordenada": True, "items": [
            "Recibida la denuncia, la empresa adopta de inmediato medidas de resguardo.",
            "Dentro de 3 dias habiles informa a la Direccion del Trabajo el inicio de la investigacion interna, "
            "o le remite la denuncia con sus antecedentes.",
            "Designa a la persona investigadora, preferentemente con formacion en acoso, genero o derechos "
            "fundamentales, y lo informa por escrito a quien denuncia.",
            "La investigacion concluye dentro de 30 dias habiles, por escrito y en reserva, oyendo a ambas partes.",
            "Dentro de 2 dias habiles se remite el informe a la Direccion del Trabajo.",
            "Con el pronunciamiento de la Direccion del Trabajo, o vencido su plazo de 30 dias habiles, la empresa "
            "aplica las medidas o sanciones dentro de 15 dias corridos e informa a ambas partes.",
        ]},
        {"tipo": "titulo", "texto": "8. Resguardo de la privacidad y la honra", "nivel": 1},
        {"tipo": "texto", "texto": "Todas las actuaciones se realizan en estricta reserva. Se protege la privacidad "
                                   "y la honra de todas las personas involucradas, cualquiera sea el resultado de "
                                   "la investigacion. Se prohiben las represalias contra quien denuncia o declara. "
                                   "[Describir las medidas ante denuncias inconsistentes.]"},
        {"tipo": "titulo", "texto": "9. Difusion y vigencia", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar como se pone a disposicion: incorporacion al Reglamento Interno para "
                                   "empresas con 10 o mas personas trabajadoras, o entrega por escrito al firmar el "
                                   "contrato e incorporacion al reglamento del art. 67 de la Ley 16.744 en empresas "
                                   "mas pequeñas. Recordar la remision de copia del reglamento interno al Ministerio "
                                   "de Salud y a la Direccion del Trabajo dentro de los 5 dias siguientes a su "
                                   "vigencia.]"},
    ]


def _bloques_informe_investigacion(perfil):
    return [
        {"tipo": "titulo", "texto": "Informe de investigacion — Ley 21.643", "nivel": 0},
        {"tipo": "nota", "texto": "Estructura minima exigida por el art. 16 del DS N° 21 de 2024. "
                                  "Documento reservado."},
        {"tipo": "titulo", "texto": "1. Antecedentes de la empresa", "nivel": 1},
        {"tipo": "texto", "texto": "Razon social: %s. RUT: [____]. Domicilio: [____]. Actividad: %s."
                                   % (perfil.get("razon_social") or perfil.get("nombre", "[____]"),
                                      perfil.get("sector") or "[____]")},
        {"tipo": "titulo", "texto": "2. Individualizacion de las partes y de la persona investigadora", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Rol", "Identificacion", "Cargo", "Fecha de ingreso"],
         "filas": [["Denunciante", "[____]", "[____]", "[____]"],
                   ["Denunciada", "[____]", "[____]", "[____]"],
                   ["Investigador(a)", "[____]", "[____]", "[____]"]]},
        {"tipo": "titulo", "texto": "3. Medidas de resguardo adoptadas y su notificacion", "nivel": 1},
        {"tipo": "texto", "texto": "[Describir cada medida, su fecha y como se notifico a las partes.]"},
        {"tipo": "titulo", "texto": "4. Antecedentes recopilados y entrevistas", "nivel": 1},
        {"tipo": "texto", "texto": "[Listar declaraciones, documentos, registros de asistencia, contratos, "
                                   "resultados de la evaluacion de riesgos psicosociales y demas antecedentes. "
                                   "Las declaraciones deben constar en papel y firmadas en todas sus hojas.]"},
        {"tipo": "titulo", "texto": "5. Relacion de los hechos y alegaciones de las partes", "nivel": 1},
        {"tipo": "texto", "texto": "[Relato ordenado y fechado de los hechos investigados y de lo alegado por "
                                   "cada parte.]"},
        {"tipo": "titulo", "texto": "6. Razonamiento e indicios que fundan las conclusiones", "nivel": 1},
        {"tipo": "texto", "texto": "[Explicar de forma coherente y congruente como los antecedentes llevan a las "
                                   "conclusiones. Aplicar perspectiva de genero.]"},
        {"tipo": "titulo", "texto": "7. Conclusiones", "nivel": 1},
        {"tipo": "texto", "texto": "[Indicar si los hechos denunciados se acreditan o no, y su calificacion.]"},
        {"tipo": "titulo", "texto": "8. Medidas correctivas propuestas", "nivel": 1},
        {"tipo": "texto", "texto": "[Medidas sobre la causa que genero la denuncia, especialmente en casos de "
                                   "violencia ejercida por terceros.]"},
        {"tipo": "titulo", "texto": "9. Sanciones propuestas", "nivel": 1},
        {"tipo": "texto", "texto": "[Sanciones conforme al Reglamento Interno y a la legislacion vigente.]"},
        {"tipo": "texto", "texto": "Fecha: ____________    Firma de la persona investigadora: ____________"},
    ]


DOCUMENTOS = {
    "protocolo": ("protocolo-prevencion-ley-karin.docx", _bloques_protocolo,
                  "Protocolo de prevencion (Ley 21.643)"),
    "informe": ("informe-investigacion-ley-karin.docx", _bloques_informe_investigacion,
                "Informe de investigacion (Ley 21.643)"),
}


def documento(opciones):
    """Redacta un documento del procedimiento (protocolo, acta, resolucion)."""
    perfil, ruta, _ = _contexto(opciones)
    tipo = _valor(opciones, "tipo", "protocolo").lower()
    if tipo not in DOCUMENTOS:
        raise Problema("No tengo un documento «%s»." % tipo,
                       "Disponibles: %s." % ", ".join(DOCUMENTOS))
    nombre, constructor, titulo = DOCUMENTOS[tipo]
    destino = espacio.ruta_de(ruta, "reportes", nombre)
    word.escribir_docx(destino, constructor(perfil), titulo)
    return Respuesta(
        {"mensaje": "Borrador creado: %s." % titulo, "archivo": destino,
         "siguiente_paso": ("Revisalo con el organismo administrador de la Ley 16.744 y con la asesoria "
                            "juridica antes de publicarlo o firmarlo.")},
        advertencias=["Es un borrador base con la estructura minima exigida: hay que completarlo con la "
                      "realidad de la empresa. No reemplaza la asistencia tecnica del organismo administrador."])


ACCIONES = {"crear": crear, "actualizar": actualizar, "evento": evento, "ver": ver, "listar": listar,
            "alertas": alertas, "documento": documento}
