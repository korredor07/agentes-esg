# -*- coding: utf-8 -*-
"""CRM de servicios ESG: prospectos, embudo, bitacora y proxima accion."""

import datetime
import json
import os

from nucleo import espacio, fechas, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Seguimiento comercial de servicios ESG: prospectos, estados del embudo y que hacer con cada uno."

ARCHIVO = "crm.json"

# Orden del embudo. Los dos ultimos son estados de cierre.
ESTADOS = ["nuevo", "contactado", "reunion", "propuesta", "negociacion", "ganado", "perdido"]
CERRADOS = ["ganado", "perdido"]

DESCRIPCION_ESTADO = {
    "nuevo": "Llego el contacto y todavia no se le habla.",
    "contactado": "Ya se le escribio o llamo, sin reunion agendada.",
    "reunion": "Hay reunion hecha o agendada para entender su necesidad.",
    "propuesta": "Se envio una propuesta con alcance y precio.",
    "negociacion": "Estan revisando condiciones, plazos o precio.",
    "ganado": "Aceptaron y el trabajo esta contratado.",
    "perdido": "No siguio: se cerro sin contrato.",
}

# Dias sin movimiento a partir de los cuales conviene actuar, por estado.
DIAS_SIN_MOVIMIENTO = {
    "nuevo": 2, "contactado": 5, "reunion": 7, "propuesta": 7, "negociacion": 5,
}

ACCION_POR_ESTADO = {
    "nuevo": "Llamar o escribir por primera vez. Una sola pregunta: que los llevo a buscar esto ahora.",
    "contactado": "Proponer una reunion corta con dos horarios concretos, no preguntar si les interesa.",
    "reunion": "Enviar el resumen de lo conversado y la propuesta, o la fecha en que la enviaras.",
    "propuesta": "Llamar para revisar la propuesta juntos y resolver dudas antes de que se enfrie.",
    "negociacion": "Cerrar el punto pendiente concreto y acordar una fecha de decision.",
    "ganado": "Sin accion comercial: coordinar el inicio del trabajo.",
    "perdido": "Sin accion inmediata. Anota por que se perdio y vuelve a contactar mas adelante.",
}

AVISO_PRIVACIDAD = ("Aqui se guardan datos de personas: nombres, correos y telefonos. Se quedan en este "
                    "computador, no se publican ni se comparten. Guarda solo lo necesario para el "
                    "seguimiento comercial, no anotes datos sensibles y borra el registro cuando la "
                    "persona lo pida o cuando ya no haga falta.")


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor not in (None, "", True) else por_defecto


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"prospectos": []}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo del CRM esta dañado y no se puede leer.",
                "No lo edites a mano. Puedo ayudarte a rehacerlo con lo que tengas anotado.",
            )
    datos.setdefault("prospectos", [])
    return datos


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _hoy(opciones=None):
    indicado = _valor(opciones or {}, "hoy")
    return fechas.parsear_fecha(indicado) if indicado else datetime.date.today()


def _normalizar_estado(texto, por_defecto=None):
    estado = str(texto or "").strip().lower()
    if not estado:
        if por_defecto:
            return por_defecto
        raise Problema(
            "Falta indicar el estado del prospecto.",
            "Estados del embudo: %s." % ", ".join(ESTADOS),
        )
    estado = espacio.texto_a_slug(estado).replace("-", " ")
    equivalencias = {"cerrado": "ganado", "ganada": "ganado", "descartado": "perdido",
                     "prospecto": "nuevo", "reunion agendada": "reunion"}
    estado = equivalencias.get(estado, estado)
    if estado not in ESTADOS:
        raise Problema(
            "No reconozco el estado «%s»." % texto,
            "Usa uno de estos, en orden del embudo: %s." % ", ".join(ESTADOS),
        )
    return estado


def _nombre_prospecto(opciones):
    return (_valor(opciones, "prospecto") or _valor(opciones, "nombre")
            or _valor(opciones, "empresa_prospecto") or _valor(opciones, "cliente"))


def _buscar(datos, referencia):
    buscado = str(referencia or "").strip().lower()
    if not buscado:
        raise Problema(
            "Falta decir de que prospecto se trata.",
            "Usa --prospecto con el nombre de la empresa o con su codigo (por ejemplo CRM-0001).",
        )
    clave = espacio.texto_a_slug(buscado)
    for prospecto in datos["prospectos"]:
        if prospecto.get("id", "").lower() == buscado or prospecto.get("prospecto_id") == clave:
            return prospecto
    registrados = ["%s (%s)" % (p.get("empresa"), p.get("id")) for p in datos["prospectos"]]
    raise Problema(
        "No encontre el prospecto «%s»." % referencia,
        ("Prospectos registrados: %s." % ", ".join(registrados)) if registrados
        else "Todavia no hay prospectos registrados. Registra el primero con: crm registrar.",
    )


def _ultima_fecha(prospecto):
    """Fecha de la ultima anotacion en la bitacora: es lo que cuenta como movimiento."""
    for entrada in reversed(prospecto.get("bitacora", [])):
        fecha = str(entrada.get("fecha") or "")[:10]
        if fecha:
            return fecha
    return str(prospecto.get("creado_el", ""))[:10]


def _dias_sin_movimiento(prospecto, hoy):
    ultima = _ultima_fecha(prospecto)
    if not ultima:
        return None
    try:
        return (hoy - fechas.parsear_fecha(ultima)).days
    except Problema:
        return None


def _ficha(prospecto, hoy):
    dias = _dias_sin_movimiento(prospecto, hoy)
    return {
        "id": prospecto.get("id"),
        "empresa": prospecto.get("empresa"),
        "contacto": prospecto.get("contacto", ""),
        "cargo": prospecto.get("cargo", ""),
        "sector": prospecto.get("sector", ""),
        "tamano": prospecto.get("tamano", ""),
        "origen": prospecto.get("origen", ""),
        "necesidad": prospecto.get("necesidad", ""),
        "estado": prospecto.get("estado"),
        "valor_estimado": prospecto.get("valor_estimado"),
        "moneda": prospecto.get("moneda", ""),
        "ultimo_movimiento": _ultima_fecha(prospecto),
        "dias_sin_movimiento": dias,
    }


# --------------------------------------------------------------------------
# Acciones
# --------------------------------------------------------------------------

def registrar(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    nombre = _nombre_prospecto(opciones)
    if not nombre:
        raise Problema(
            "Falta el nombre de la empresa del prospecto.",
            "Indicalo con --prospecto, por ejemplo: crm registrar --prospecto \"Vina Los Robles\" "
            "--contacto \"Marta Diaz\" --origen \"recomendacion\". "
            "(--empresa se usa para elegir tu propia empresa en el espacio de trabajo.)",
        )
    estado = _normalizar_estado(_valor(opciones, "estado"), por_defecto="nuevo")
    valor_texto = _valor(opciones, "valor_estimado") or _valor(opciones, "valor")
    valor_estimado = None
    if valor_texto:
        try:
            valor_estimado = float(str(valor_texto).replace(".", "").replace(",", "."))
        except ValueError:
            raise Problema(
                "No entiendo el valor estimado «%s»." % valor_texto,
                "Escribe solo el numero, por ejemplo 3500000.",
            )

    datos = _leer(ruta_json)
    clave = espacio.texto_a_slug(nombre)
    for existente in datos["prospectos"]:
        if existente.get("prospecto_id") == clave:
            raise Problema(
                "Ya hay un prospecto registrado para «%s» (%s)." % (existente.get("empresa"),
                                                                    existente.get("id")),
                "Para cambiarle el estado usa: crm mover --prospecto %s --estado contactado. "
                "Para verlo: crm listar." % existente.get("id"),
            )

    hoy = _hoy(opciones)
    prospecto = {
        "id": "CRM-%04d" % (len(datos["prospectos"]) + 1),
        "prospecto_id": clave,
        "empresa": nombre,
        "contacto": _valor(opciones, "contacto"),
        "cargo": _valor(opciones, "cargo"),
        "correo": _valor(opciones, "correo"),
        "telefono": _valor(opciones, "telefono"),
        "sector": _valor(opciones, "sector"),
        "tamano": _valor(opciones, "tamano"),
        "origen": _valor(opciones, "origen"),
        "necesidad": _valor(opciones, "necesidad"),
        "estado": estado,
        "valor_estimado": valor_estimado,
        "moneda": _valor(opciones, "moneda", perfil.get("moneda") or "CLP"),
        "notas": _valor(opciones, "notas"),
        "bitacora": [{"fecha": hoy.isoformat(), "de": "", "a": estado,
                      "nota": "Prospecto registrado."}],
        "creado_el": datetime.datetime.now().replace(microsecond=0).isoformat(sep=" "),
    }
    datos["prospectos"].append(prospecto)
    _guardar(ruta_json, datos)

    advertencias = [AVISO_PRIVACIDAD]
    if not prospecto["necesidad"]:
        advertencias.append("No quedo anotada la necesidad detectada. En la primera conversacion pregunta "
                            "que los llevo a buscar esto ahora y anotalo: es lo que despues permite "
                            "proponer algo util y no un catalogo de servicios.")
    return Respuesta(
        {"mensaje": "Prospecto %s registrado como «%s»." % (prospecto["id"], estado),
         "prospecto": prospecto,
         "total": len(datos["prospectos"]),
         "archivo": ruta_json,
         "siguiente_paso": ACCION_POR_ESTADO[estado]},
        advertencias=advertencias)


def listar(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    hoy = _hoy(opciones)
    filtro_estado = _valor(opciones, "estado")
    if filtro_estado:
        filtro_estado = _normalizar_estado(filtro_estado)
    filtro_sector = espacio.texto_a_slug(_valor(opciones, "sector")) if _valor(opciones, "sector") else ""

    fichas = []
    for prospecto in datos["prospectos"]:
        if filtro_estado and prospecto.get("estado") != filtro_estado:
            continue
        if filtro_sector and espacio.texto_a_slug(prospecto.get("sector", "")) != filtro_sector:
            continue
        fichas.append(_ficha(prospecto, hoy))
    orden = {estado: indice for indice, estado in enumerate(ESTADOS)}
    fichas.sort(key=lambda f: (orden.get(f["estado"], 99), -(f["dias_sin_movimiento"] or 0)))

    por_estado = {}
    for prospecto in datos["prospectos"]:
        estado = prospecto.get("estado", "nuevo")
        por_estado[estado] = por_estado.get(estado, 0) + 1
    activos = [p for p in datos["prospectos"] if p.get("estado") not in CERRADOS]

    if not datos["prospectos"]:
        mensaje = ("Todavia no hay prospectos registrados. Registra el primero con: "
                   "crm registrar --prospecto \"Nombre de la empresa\".")
    elif not fichas:
        mensaje = "Hay %d prospecto(s), pero ninguno coincide con ese filtro." % len(datos["prospectos"])
    else:
        mensaje = "%d prospecto(s) en la lista, %d activos." % (len(fichas), len(activos))

    return {
        "total": len(fichas),
        "total_registrados": len(datos["prospectos"]),
        "activos": len(activos),
        "por_estado": {estado: por_estado.get(estado, 0) for estado in ESTADOS},
        "estados_del_embudo": [{"estado": e, "significa": DESCRIPCION_ESTADO[e]} for e in ESTADOS],
        "prospectos": fichas,
        "mensaje": mensaje,
    }


def mover(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    prospecto = _buscar(datos, _nombre_prospecto(opciones))
    nuevo = _normalizar_estado(_valor(opciones, "estado"))
    anterior = prospecto.get("estado", "nuevo")
    nota = _valor(opciones, "nota")
    hoy = _hoy(opciones)

    if nuevo == anterior and not nota:
        raise Problema(
            "%s ya estaba en «%s», asi que no hay nada que mover." % (prospecto.get("empresa"), anterior),
            "Si igual quieres dejar constancia de algo, agrega --nota \"lo que paso\".",
        )
    if nuevo == "perdido" and not nota:
        raise Problema(
            "Para cerrar un prospecto como perdido necesito saber por que.",
            "Agrega --nota \"precio\", --nota \"lo hara internamente\" o lo que corresponda. Sin esa "
            "razon no se aprende nada de la oportunidad perdida.",
        )

    prospecto["estado"] = nuevo
    prospecto["bitacora"].append({
        "fecha": hoy.isoformat(),
        "de": anterior,
        "a": nuevo,
        "nota": nota or ("Paso de %s a %s." % (anterior, nuevo)),
    })
    _guardar(ruta_json, datos)

    avance = ESTADOS.index(nuevo) - ESTADOS.index(anterior)
    advertencias = []
    if nuevo in CERRADOS:
        advertencias.append("El prospecto queda cerrado: deja de aparecer en las acciones pendientes.")
    if avance < 0 and nuevo not in CERRADOS:
        advertencias.append("El prospecto retrocedio en el embudo. Anota en la bitacora que lo hizo "
                            "retroceder: suele repetirse con otros clientes.")
    return Respuesta(
        {"mensaje": "%s paso de «%s» a «%s»." % (prospecto.get("empresa"), anterior, nuevo),
         "prospecto": prospecto.get("id"),
         "empresa": prospecto.get("empresa"),
         "estado_anterior": anterior,
         "estado": nuevo,
         "significa": DESCRIPCION_ESTADO[nuevo],
         "siguiente_paso": ACCION_POR_ESTADO[nuevo],
         "bitacora": prospecto["bitacora"][-3:]},
        advertencias=advertencias)


def siguiente(opciones):
    """Propone la proxima accion de cada prospecto segun cuanto lleva sin moverse."""
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    hoy = _hoy(opciones)
    if not datos["prospectos"]:
        raise Problema(
            "Todavia no hay prospectos registrados.",
            "Registra el primero con: crm registrar --prospecto \"Nombre de la empresa\".",
        )

    pendientes = []
    cerrados = 0
    for prospecto in datos["prospectos"]:
        estado = prospecto.get("estado", "nuevo")
        if estado in CERRADOS:
            cerrados += 1
            continue
        dias = _dias_sin_movimiento(prospecto, hoy)
        limite = DIAS_SIN_MOVIMIENTO.get(estado, 7)
        if dias is None:
            urgencia, atraso = "sin fecha", 0
        elif dias > limite * 3:
            urgencia, atraso = "detenido", dias - limite
        elif dias > limite:
            urgencia, atraso = "atrasado", dias - limite
        else:
            urgencia, atraso = "al dia", 0
        accion = ACCION_POR_ESTADO[estado]
        if urgencia == "detenido":
            accion = ("Lleva %d dias sin movimiento. Llama una ultima vez y, si no responde, pregunta "
                      "derecho si esto sigue en pie o lo cerramos. %s" % (dias, accion))
        pendientes.append({
            "id": prospecto.get("id"),
            "empresa": prospecto.get("empresa"),
            "contacto": prospecto.get("contacto", ""),
            "estado": estado,
            "necesidad": prospecto.get("necesidad", ""),
            "ultimo_movimiento": _ultima_fecha(prospecto),
            "dias_sin_movimiento": dias,
            "limite_sugerido_dias": limite,
            "urgencia": urgencia,
            "accion_sugerida": accion,
        })

    orden = {"detenido": 0, "atrasado": 1, "sin fecha": 2, "al dia": 3}
    pendientes.sort(key=lambda p: (orden[p["urgencia"]], -(p["dias_sin_movimiento"] or 0)))
    para_hoy = [p for p in pendientes if p["urgencia"] in ("detenido", "atrasado")]

    advertencias = []
    if len(para_hoy) > 5:
        advertencias.append("Hay %d prospectos atrasados. No intentes todos hoy: toma los tres primeros "
                            "de la lista, que son los que llevan mas tiempo detenidos." % len(para_hoy))
    return Respuesta(
        {"total_activos": len(pendientes),
         "cerrados": cerrados,
         "para_hoy": len(para_hoy),
         "hoy": hoy.isoformat(),
         "acciones": pendientes,
         "mensaje": ("Nada urgente: todos los prospectos activos estan dentro de su plazo."
                     if not para_hoy else
                     "%d prospecto(s) necesitan una accion hoy." % len(para_hoy))},
        advertencias=advertencias)


def informe_html(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    hoy = _hoy(opciones)
    if not datos["prospectos"]:
        raise Problema(
            "No hay prospectos registrados, asi que el embudo estaria vacio.",
            "Registra al menos uno con: crm registrar --prospecto \"Nombre de la empresa\".",
        )

    por_estado = {estado: [] for estado in ESTADOS}
    for prospecto in datos["prospectos"]:
        por_estado.setdefault(prospecto.get("estado", "nuevo"), []).append(prospecto)
    activos = [p for p in datos["prospectos"] if p.get("estado") not in CERRADOS]
    ganados = len(por_estado.get("ganado", []))
    perdidos = len(por_estado.get("perdido", []))
    cerrados = ganados + perdidos
    conversion = round(ganados * 100.0 / cerrados, 1) if cerrados else None
    valor_activo = sum(float(p.get("valor_estimado") or 0) for p in activos)

    detenidos = []
    for prospecto in activos:
        dias = _dias_sin_movimiento(prospecto, hoy)
        limite = DIAS_SIN_MOVIMIENTO.get(prospecto.get("estado", "nuevo"), 7)
        if dias is not None and dias > limite:
            detenidos.append((prospecto, dias, limite))
    detenidos.sort(key=lambda x: -x[1])

    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Prospectos activos", "valor": len(activos), "unidad": "",
             "detalle": "Sin cerrar todavia"},
            {"etiqueta": "Ganados", "valor": ganados, "unidad": "", "color": "verde",
             "detalle": "Trabajos contratados"},
            {"etiqueta": "Conversion", "valor": conversion if conversion is not None else "—",
             "unidad": "%" if conversion is not None else "",
             "detalle": "De los cerrados (%d)" % cerrados if cerrados else "Aun no hay cierres"},
            {"etiqueta": "Valor en juego", "valor": valor_activo,
             "unidad": (activos[0].get("moneda", "") if activos else ""),
             "detalle": "Suma estimada de los activos"},
        ]},
        {"tipo": "barras", "titulo": "Embudo por estado", "unidad": "prospectos",
         "datos": [{"etiqueta": "%s — %s" % (estado, DESCRIPCION_ESTADO[estado].split(".")[0].lower()),
                    "valor": len(por_estado.get(estado, []))} for estado in ESTADOS]},
        {"tipo": "texto", "texto": "Un embudo sano se angosta de arriba hacia abajo. Si se acumulan "
                                   "muchos en un mismo escalon, ahi esta el problema: revisa que pasa "
                                   "en ese paso antes de buscar mas prospectos nuevos."},
    ]

    if detenidos:
        bloques.append({"tipo": "titulo", "texto": "Prospectos detenidos", "nivel": 2})
        bloques.append({"tipo": "semaforo", "items": [
            {"etiqueta": "%s (%s)" % (p.get("empresa"), p.get("id")),
             "estado": "rojo" if dias > limite * 3 else "amarillo",
             "estado_texto": "%d dias" % dias,
             "detalle": "En «%s». %s" % (p.get("estado"), ACCION_POR_ESTADO[p.get("estado", "nuevo")])}
            for p, dias, limite in detenidos[:10]]})

    bloques.append({"tipo": "titulo", "texto": "Todos los prospectos", "nivel": 2})
    bloques.append({"tipo": "tabla",
                    "columnas": ["Codigo", "Empresa", "Sector", "Necesidad detectada", "Estado",
                                 "Dias sin movimiento"],
                    "numericas": [5],
                    "filas": [[p.get("id"), p.get("empresa"), p.get("sector") or "—",
                               p.get("necesidad") or "—", p.get("estado"),
                               _dias_sin_movimiento(p, hoy)]
                              for p in sorted(datos["prospectos"],
                                              key=lambda x: ESTADOS.index(x.get("estado", "nuevo")))],
                    "nota": "Los dias sin movimiento se cuentan desde la ultima anotacion en la bitacora."})

    if perdidos:
        razones = []
        for prospecto in por_estado.get("perdido", []):
            ultima = [b for b in prospecto.get("bitacora", []) if b.get("a") == "perdido"]
            razones.append([prospecto.get("empresa"),
                            ultima[-1].get("nota") if ultima else "sin razon anotada"])
        bloques.append({"tipo": "titulo", "texto": "Por que se perdieron", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Empresa", "Razon anotada"], "filas": razones,
                        "nota": "Revisa si se repite una misma razon: eso se puede corregir."})

    bloques.append({"tipo": "nota", "estilo": "info", "texto": AVISO_PRIVACIDAD})

    destino = espacio.ruta_de(ruta, "reportes", "embudo-comercial.html")
    informe.escribir_html(destino, "Embudo comercial de servicios ESG", bloques,
                          marca=perfil.get("marca") or {},
                          subtitulo="%s — estado al %s" % (perfil.get("nombre", ""), hoy.isoformat()))
    return Respuesta(
        {"mensaje": "Informe del embudo listo: abrelo con doble clic.",
         "archivo": destino,
         "activos": len(activos),
         "ganados": ganados,
         "perdidos": perdidos,
         "conversion_pct": conversion},
        advertencias=[AVISO_PRIVACIDAD])


ACCIONES = {"registrar": registrar, "listar": listar, "mover": mover,
            "siguiente": siguiente, "informe": informe_html}
