# -*- coding: utf-8 -*-
"""Proveedores: pedir datos ESG, registrar lo que responden y ordenar por donde partir."""

import datetime
import json
import os

from nucleo import espacio, informe, word
from nucleo.salida import Problema, Respuesta

AYUDA = "Pide datos ESG a los proveedores, registra sus respuestas y prioriza a quien perseguir primero."

ARCHIVO = "proveedores.json"
CALIDADES = ["estimado", "reportado", "verificado"]

AVISO_PRIVACIDAD = ("Los nombres, correos y telefonos de los contactos son datos de personas. Se guardan "
                    "solo en este computador, no se publican y se usan unicamente para el fin que se "
                    "explico en la solicitud.")
AVISO_DATO = ("La huella que declara un proveedor es su dato, no el tuyo: anota quien la entrego, de que "
              "año es y si la reviso un tercero independiente antes de usarla en un reporte.")


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


def _numero(valor):
    """Acepta 1.234,5 o 1234.5 y devuelve un numero; None si viene vacio."""
    if valor in (None, "", True):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace(" ", "")
    if texto.count(",") == 1 and (texto.count(".") > 1 or texto.rfind(",") > texto.rfind(".")):
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", "")
    try:
        return float(texto)
    except ValueError:
        raise Problema(
            "No entiendo el numero «%s»." % valor,
            "Escribelo solo con digitos, por ejemplo 12500 o 12500,5.",
        )


def _booleano(opciones, clave, por_defecto=False):
    valor = opciones.get(clave)
    if valor is None:
        return por_defecto
    if valor is True:
        return True
    texto = str(valor).strip().lower()
    if texto in ("si", "s", "true", "1", "verdadero"):
        return True
    if texto in ("no", "n", "false", "0", "falso"):
        return False
    raise Problema(
        "No entiendo la respuesta «%s» para --%s." % (valor, clave.replace("_", "-")),
        "Contesta si o no.",
    )


def _lista(valor):
    if not valor or valor is True:
        return []
    return [parte.strip() for parte in str(valor).replace(";", ",").split(",") if parte.strip()]


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"proveedores": []}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo de proveedores esta dañado y no se puede leer.",
                "No lo edites a mano. Puedo ayudarte a rehacerlo con las respuestas que tengas guardadas.",
            )
    datos.setdefault("proveedores", [])
    return datos


def _guardar(ruta_json, datos):
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def _hoy():
    return datetime.date.today().isoformat()


def _ahora():
    return datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")


# --------------------------------------------------------------------------
# Documentos para enviar al proveedor
# --------------------------------------------------------------------------

def _bloques_cuestionario(perfil, proveedor, periodo, plazo, responsable, correo):
    nombre_empresa = perfil.get("nombre", "la empresa")
    destinatario = proveedor or "[Nombre del proveedor]"
    return [
        {"tipo": "titulo", "texto": "Cuestionario ESG para proveedores", "nivel": 0},
        {"tipo": "texto", "texto": "Solicitado por: %s    |    Proveedor: %s    |    Periodo consultado: %s"
                                   % (nombre_empresa, destinatario, periodo)},
        {"tipo": "nota", "texto": "Son 20 minutos. Si no tiene un dato, escriba «no lo tengo» y siga: "
                                  "preferimos una respuesta incompleta y honesta a un numero inventado. "
                                  "Devuelva este archivo a %s (%s) antes del %s."
                                  % (responsable or "[nombre]", correo or "[correo]", plazo or "[fecha]")},

        {"tipo": "titulo", "texto": "1. Datos de la empresa", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Dato", "Respuesta"], "filas": [
            ["Razon social", ""],
            ["Identificador tributario (RUT / RUC / NIF)", ""],
            ["Pais y ciudad de la planta o bodega principal", ""],
            ["Numero aproximado de trabajadores", ""],
            ["Persona de contacto para temas ambientales", ""],
            ["Correo y telefono de esa persona", ""],
        ]},

        {"tipo": "titulo", "texto": "2. ¿Miden su huella de carbono?", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Pregunta", "Respuesta"], "filas": [
            ["¿Han calculado su huella de carbono alguna vez? (si / no)", ""],
            ["Si la respuesta es si: ¿de que año es el ultimo calculo?", ""],
            ["¿Que alcances incluye? (1, 2, 3 o los que sepa)", ""],
            ["¿La reviso un tercero independiente? (si / no / no se)", ""],
            ["¿Quien la calculo? (equipo interno, consultora, programa publico)", ""],
        ]},
        {"tipo": "texto", "texto": "Si nunca han medido, no hay problema: conteste «no» y salte a la "
                                   "seccion 3. Esa respuesta tambien nos sirve."},

        {"tipo": "titulo", "texto": "3. Energia y emisiones por producto", "nivel": 1},
        {"tipo": "texto", "texto": "Complete una fila por cada producto o servicio que nos vende. Si no "
                                   "conoce las emisiones, llene al menos la energia: con eso podemos "
                                   "estimarlas nosotros y se lo compartimos."},
        {"tipo": "tabla", "columnas": ["Producto o servicio", "Unidad de venta (kg, litro, unidad, hora)",
                                       "Electricidad por unidad (kWh)", "Combustible por unidad (litros o kg, indique cual)",
                                       "Huella declarada por unidad (kg CO2e), si la tiene"],
         "filas": [["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""], ["", "", "", "", ""]]},

        {"tipo": "titulo", "texto": "4. Practicas laborales", "nivel": 1},
        {"tipo": "tabla", "columnas": ["Pregunta", "Respuesta"], "filas": [
            ["¿Todo el personal tiene contrato escrito y cotizaciones al dia? (si / no)", ""],
            ["¿Tienen un canal para recibir denuncias de acoso o maltrato? (si / no)", ""],
            ["¿Tienen protocolo de prevencion de acoso y violencia en el trabajo? (si / no)", ""],
            ["¿Trabaja con subcontratistas o personal externo? (si / no)", ""],
            ["¿Accidentes con dias perdidos en el ultimo año? (numero o «no lo tengo»)", ""],
            ["¿Horas de capacitacion en seguridad en el ultimo año? (numero aproximado)", ""],
        ]},

        {"tipo": "titulo", "texto": "5. Certificaciones y permisos", "nivel": 1},
        {"tipo": "texto", "texto": "Marque las que tenga vigentes y adjunte el certificado si lo tiene a mano."},
        {"tipo": "tabla", "columnas": ["Certificacion o permiso", "¿Vigente? (si / no)", "Hasta cuando"],
         "filas": [
            ["ISO 14001 (gestion ambiental)", "", ""],
            ["ISO 45001 (seguridad y salud en el trabajo)", "", ""],
            ["ISO 9001 (calidad)", "", ""],
            ["Sello HuellaChile u otro programa de carbono", "", ""],
            ["Certificacion de producto (organico, comercio justo, forestal u otra)", "", ""],
            ["Resolucion sanitaria o permiso ambiental del rubro", "", ""],
            ["Otra (indique cual)", "", ""],
        ]},

        {"tipo": "titulo", "texto": "6. Comentarios", "nivel": 1},
        {"tipo": "texto", "texto": "¿Hay algo que quiera contarnos sobre lo que ya estan haciendo o sobre "
                                   "las dificultades para conseguir estos datos?"},
        {"tipo": "tabla", "columnas": ["Comentarios"], "filas": [[""], [""], [""]]},

        {"tipo": "titulo", "texto": "Como devolver el cuestionario", "nivel": 1},
        {"tipo": "lista", "ordenada": True, "items": [
            "Complete las casillas en este mismo archivo Word y guardelo.",
            "Envielo a %s (%s) antes del %s." % (responsable or "[nombre]", correo or "[correo]",
                                                 plazo or "[fecha]"),
            "Si algo no se entiende, escriba a ese mismo correo: preferimos aclarar antes que recibir "
            "un dato dudoso.",
            "Si tiene los datos en otro formato (una planilla, un informe propio), envielo tal cual: "
            "no hace falta rehacer el trabajo.",
        ]},
        {"tipo": "nota", "texto": "Uso de la informacion: %s usara estas respuestas para calcular su propia "
                                  "huella de carbono y responder requerimientos de clientes y autoridades. "
                                  "Los datos se guardan en los sistemas de %s, no se publican con el nombre "
                                  "del proveedor sin su acuerdo previo y no se comparten con la competencia."
                                  % (nombre_empresa, nombre_empresa)},
    ]


def _bloques_carta(perfil, proveedor, periodo, plazo, responsable, correo, motivo):
    nombre_empresa = perfil.get("nombre", "la empresa")
    return [
        {"tipo": "titulo", "texto": "Solicitud de datos ambientales y laborales a proveedores", "nivel": 0},
        {"tipo": "texto", "texto": "Fecha: %s" % _hoy()},
        {"tipo": "texto", "texto": "Para: %s" % (proveedor or "[Nombre del proveedor]")},
        {"tipo": "texto", "texto": "De: %s — %s" % (nombre_empresa, responsable or "[nombre y cargo]")},

        {"tipo": "titulo", "texto": "Estimados:", "nivel": 2},
        {"tipo": "texto", "texto": "Les escribimos porque %s esta midiendo el impacto ambiental de toda su "
                                   "cadena: no solo lo que ocurre dentro de nuestras instalaciones, sino "
                                   "tambien lo que ocurre antes de que el producto llegue a nosotros. Una "
                                   "parte importante de ese impacto esta en lo que compramos, y por eso les "
                                   "pedimos ayuda." % nombre_empresa},
        {"tipo": "texto", "texto": "El motivo concreto es este: %s" % (
            motivo or "nuestros clientes y las normas que nos aplican nos piden informar las emisiones de "
                      "nuestra cadena de suministro, y hoy las estamos estimando con promedios generales "
                      "que no reflejan lo que ustedes realmente hacen.")},

        {"tipo": "titulo", "texto": "Que les pedimos", "nivel": 1},
        {"tipo": "lista", "items": [
            "Responder el cuestionario adjunto para el periodo %s. Toma alrededor de 20 minutos." % periodo,
            "Si ya calcularon su huella de carbono, enviarnos ese informe: nos sirve tal como esta.",
            "Si no han medido nada todavia, responder igual: saber que no hay dato tambien es informacion "
            "util y no los deja fuera de nuestra lista de proveedores.",
        ]},

        {"tipo": "titulo", "texto": "Que haremos con el dato", "nivel": 1},
        {"tipo": "lista", "items": [
            "Lo usaremos para calcular nuestra huella de carbono con datos reales en vez de estimaciones, "
            "y para responder los requerimientos de nuestros clientes y de la autoridad.",
            "Los datos quedan en nuestros sistemas internos. No los publicamos identificando al proveedor "
            "sin acuerdo previo, ni los compartimos con otras empresas de su rubro.",
            "Los datos de contacto de las personas se usan solo para esta gestion y para las consultas que "
            "surjan de ella.",
            "Si el dato que nos entregan mejora nuestro calculo, se lo devolvemos: les diremos como quedo "
            "estimado su aporte y en que podrian mejorarlo.",
        ]},

        {"tipo": "titulo", "texto": "Que NO estamos pidiendo", "nivel": 1},
        {"tipo": "lista", "items": [
            "No pedimos informacion sobre sus costos, margenes ni sus otros clientes.",
            "No pedimos una certificacion ni una auditoria: no hace falta contratar a nadie para responder.",
            "No condicionamos la relacion comercial a que el resultado sea bueno; si condicionamos a que "
            "exista una respuesta, porque necesitamos saber con quien estamos trabajando.",
        ]},

        {"tipo": "titulo", "texto": "Plazo y contacto", "nivel": 1},
        {"tipo": "texto", "texto": "Agradeceremos recibir la respuesta antes del %s. Cualquier duda, escriban "
                                   "a %s (%s), que los puede acompañar a completar el cuestionario por "
                                   "telefono si les resulta mas comodo."
                                   % (plazo or "[fecha]", responsable or "[nombre]", correo or "[correo]")},
        {"tipo": "texto", "texto": "Gracias por el tiempo.\n\n\n____________________\n%s\n%s"
                                   % (responsable or "[Nombre y cargo]", nombre_empresa)},
        {"tipo": "nota", "texto": "Borrador para revisar y firmar. Ajusta el motivo y el plazo a la realidad "
                                  "de la empresa antes de enviarlo, y no prometas nada que no puedas cumplir."},
    ]


def cuestionario(opciones):
    perfil, ruta, _ = _contexto(opciones)
    proveedor = _valor(opciones, "proveedor")
    periodo = _valor(opciones, "periodo", str(perfil.get("periodo_actual") or datetime.date.today().year))
    plazo = _valor(opciones, "plazo")
    responsable = _valor(opciones, "responsable")
    correo = _valor(opciones, "correo")
    sufijo = espacio.texto_a_slug(proveedor) if proveedor else "general"
    destino = espacio.ruta_de(ruta, "reportes", "cuestionario-esg-%s.docx" % sufijo)
    word.escribir_docx(destino,
                       _bloques_cuestionario(perfil, proveedor, periodo, plazo, responsable, correo),
                       "Cuestionario ESG para proveedores")
    faltantes = [nombre for nombre, valor in
                 (("plazo", plazo), ("responsable", responsable), ("correo", correo)) if not valor]
    advertencias = [AVISO_PRIVACIDAD]
    if faltantes:
        advertencias.append("El documento quedo con espacios entre corchetes para: %s. Completalos antes "
                            "de enviarlo, o vuelve a generarlo con --plazo, --responsable y --correo."
                            % ", ".join(faltantes))
    return Respuesta(
        {"mensaje": "Cuestionario listo para enviar.",
         "archivo": destino,
         "proveedor": proveedor or "generico (sirve para cualquier proveedor)",
         "periodo": periodo,
         "siguiente_paso": ("Envialo junto con la carta de solicitud (proveedores carta) y, cuando "
                            "respondan, guarda la respuesta con: proveedores registrar.")},
        advertencias=advertencias)


def carta(opciones):
    perfil, ruta, _ = _contexto(opciones)
    proveedor = _valor(opciones, "proveedor")
    periodo = _valor(opciones, "periodo", str(perfil.get("periodo_actual") or datetime.date.today().year))
    plazo = _valor(opciones, "plazo")
    responsable = _valor(opciones, "responsable")
    correo = _valor(opciones, "correo")
    motivo = _valor(opciones, "motivo")
    sufijo = espacio.texto_a_slug(proveedor) if proveedor else "general"
    destino = espacio.ruta_de(ruta, "reportes", "carta-solicitud-proveedores-%s.docx" % sufijo)
    word.escribir_docx(destino,
                       _bloques_carta(perfil, proveedor, periodo, plazo, responsable, correo, motivo),
                       "Solicitud de datos a proveedores")
    return Respuesta(
        {"mensaje": "Carta de solicitud lista.",
         "archivo": destino,
         "proveedor": proveedor or "generica (sirve para cualquier proveedor)",
         "siguiente_paso": "Revisa el texto, firmalo y envialo con el cuestionario adjunto."},
        advertencias=[AVISO_PRIVACIDAD,
                      "Es un borrador: revisa que el motivo y el plazo sean los reales antes de enviarlo."])


# --------------------------------------------------------------------------
# Registro y prioridades
# --------------------------------------------------------------------------

def registrar(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    nombre = _valor(opciones, "nombre") or _valor(opciones, "proveedor")
    if not nombre:
        raise Problema(
            "Falta el nombre del proveedor.",
            "Indicalo asi: proveedores registrar --nombre \"Envases del Sur\".",
        )
    huella = _numero(opciones.get("huella_declarada") or opciones.get("huella"))
    entrego = _booleano(opciones, "entrego", huella is not None)
    calidad = str(_valor(opciones, "calidad", "estimado" if entrego else "")).lower()
    if calidad and calidad not in CALIDADES:
        raise Problema(
            "No reconozco la calidad de dato «%s»." % calidad,
            "Usa una de estas: %s. Estimado lo calculo alguien, reportado viene de una factura o medidor, "
            "verificado lo reviso un tercero independiente." % ", ".join(CALIDADES),
        )

    datos = _leer(ruta_json)
    identificador = espacio.texto_a_slug(nombre)
    registro = None
    for candidato in datos["proveedores"]:
        if candidato.get("id") == identificador:
            registro = candidato
            break
    nuevo = registro is None
    if nuevo:
        registro = {"id": identificador, "creado_el": _ahora(), "bitacora": []}
        datos["proveedores"].append(registro)

    registro["nombre"] = nombre
    for clave, opcion in (("contacto", "contacto"), ("correo", "correo"), ("telefono", "telefono"),
                          ("categoria_compra", "categoria"), ("pais", "pais"), ("notas", "notas"),
                          ("unidad_huella", "unidad"), ("periodo", "periodo")):
        valor = _valor(opciones, opcion)
        if valor or clave not in registro:
            registro[clave] = valor or registro.get(clave, "")
    gasto = _numero(opciones.get("gasto_anual") or opciones.get("gasto"))
    if gasto is not None or "gasto_anual" not in registro:
        registro["gasto_anual"] = gasto if gasto is not None else registro.get("gasto_anual")
    registro["moneda"] = (_valor(opciones, "moneda") or registro.get("moneda")
                          or perfil.get("moneda") or "CLP")
    emision = _numero(opciones.get("emision_estimada") or opciones.get("emision"))
    if emision is not None or "emision_estimada_tco2e" not in registro:
        registro["emision_estimada_tco2e"] = emision if emision is not None else registro.get("emision_estimada_tco2e")
    registro["entrego_datos"] = entrego
    if huella is not None or "huella_declarada" not in registro:
        registro["huella_declarada"] = huella if huella is not None else registro.get("huella_declarada")
    certificaciones = _lista(opciones.get("certificaciones"))
    if certificaciones or "certificaciones" not in registro:
        registro["certificaciones"] = certificaciones or registro.get("certificaciones", [])
    registro["calidad_dato"] = calidad
    registro["estado"] = "con datos" if entrego else "sin datos"
    registro["actualizado_el"] = _ahora()
    registro["bitacora"].append({
        "fecha": _hoy(),
        "nota": ("Respuesta registrada: %s." % ("entrego datos" if entrego else "todavia sin datos"))
                + (" Huella declarada: %s %s." % (huella, registro.get("unidad_huella") or "kg CO2e por unidad")
                   if huella is not None else ""),
    })
    _guardar(ruta_json, datos)

    advertencias = [AVISO_PRIVACIDAD]
    if entrego:
        advertencias.append(AVISO_DATO)
        if not registro.get("unidad_huella"):
            advertencias.append("No quedo anotada la unidad de la huella declarada. Sin unidad el numero no "
                                "se puede usar: pregunta si es por kilo, por litro o por unidad vendida.")
    else:
        advertencias.append("Quedo registrado como proveedor sin datos. Si es de los grandes, entra en la "
                            "lista de seguimiento: revisala con proveedores evaluar.")
    return Respuesta(
        {"mensaje": "%s el proveedor %s." % ("Registrado" if nuevo else "Actualizado", nombre),
         "proveedor": registro,
         "archivo": ruta_json,
         "total_proveedores": len(datos["proveedores"])},
        advertencias=advertencias)


def _impacto(proveedor, total_emision, total_gasto):
    """Peso relativo del proveedor: por emision si hay dato, si no por gasto."""
    emision = proveedor.get("emision_estimada_tco2e")
    gasto = proveedor.get("gasto_anual")
    if total_emision and emision:
        return float(emision) / total_emision, "emision estimada"
    if total_gasto and gasto:
        return float(gasto) / total_gasto, "gasto anual"
    return 0.0, "sin gasto ni emision registrados"


def _ordenar_por_prioridad(proveedores):
    total_emision = sum(float(p.get("emision_estimada_tco2e") or 0) for p in proveedores)
    total_gasto = sum(float(p.get("gasto_anual") or 0) for p in proveedores)
    filas = []
    for proveedor in proveedores:
        peso, base = _impacto(proveedor, total_emision, total_gasto)
        filas.append({
            "id": proveedor.get("id"),
            "nombre": proveedor.get("nombre"),
            "categoria_compra": proveedor.get("categoria_compra", ""),
            "contacto": proveedor.get("contacto", ""),
            "entrego_datos": bool(proveedor.get("entrego_datos")),
            "calidad_dato": proveedor.get("calidad_dato", ""),
            "gasto_anual": proveedor.get("gasto_anual"),
            "moneda": proveedor.get("moneda", ""),
            "emision_estimada_tco2e": proveedor.get("emision_estimada_tco2e"),
            "peso_pct": round(peso * 100, 1),
            "base_del_peso": base,
        })
    # el 80 % del impacto: se calcula sobre todos, entreguen o no datos
    filas.sort(key=lambda f: -f["peso_pct"])
    acumulado = 0.0
    for fila in filas:
        dentro = acumulado < 80.0
        acumulado += fila["peso_pct"]
        fila["explica_80_pct"] = bool(dentro and fila["peso_pct"] > 0)
        fila["acumulado_pct"] = round(min(acumulado, 100.0), 1)
    # prioridad de trabajo: primero los grandes que no entregan datos
    for fila in filas:
        if not fila["entrego_datos"] and fila["explica_80_pct"]:
            fila["prioridad"] = "alta"
            fila["accion_sugerida"] = ("Llamar por telefono y ofrecer completar el cuestionario juntos. "
                                       "Explica el 80/20: es de los pocos que mueven el resultado.")
        elif not fila["entrego_datos"]:
            fila["prioridad"] = "baja"
            fila["accion_sugerida"] = ("Reenviar el cuestionario una vez mas y, si no responde, seguir con "
                                       "la estimacion por gasto. No vale la pena insistir mas.")
        elif fila["explica_80_pct"] and fila["calidad_dato"] == "estimado":
            fila["prioridad"] = "media"
            fila["accion_sugerida"] = ("Entrego un dato estimado y pesa mucho. Pedirle el respaldo "
                                       "(factura, medicion o informe) para subirlo a reportado.")
        else:
            fila["prioridad"] = "seguimiento"
            fila["accion_sugerida"] = "Mantener el dato al dia: volver a pedirlo en el proximo periodo."
    orden = {"alta": 0, "media": 1, "baja": 2, "seguimiento": 3}
    filas.sort(key=lambda f: (orden[f["prioridad"]], -f["peso_pct"]))
    return filas, total_emision, total_gasto


def evaluar(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    proveedores = datos["proveedores"]
    if not proveedores:
        raise Problema(
            "Todavia no hay proveedores registrados.",
            "Registra el primero con: proveedores registrar --nombre \"Envases del Sur\" "
            "--categoria envases --gasto-anual 18000000.",
        )
    filas, total_emision, total_gasto = _ordenar_por_prioridad(proveedores)
    con_datos = [f for f in filas if f["entrego_datos"]]
    cubierto = sum(f["peso_pct"] for f in con_datos)
    criticos = [f for f in filas if f["prioridad"] == "alta"]
    advertencias = [AVISO_PRIVACIDAD]
    if not total_emision and not total_gasto:
        advertencias.append("Ningun proveedor tiene gasto anual ni emision estimada, asi que no se puede "
                            "priorizar por impacto. Agrega al menos el gasto anual de cada uno.")
    if criticos:
        advertencias.append("Hay %d proveedor(es) que pesan mucho y todavia no entregan datos: son los "
                            "unicos que vale la pena perseguir por telefono." % len(criticos))
    return Respuesta(
        {"total": len(filas),
         "con_datos": len(con_datos),
         "sin_datos": len(filas) - len(con_datos),
         "cobertura_del_impacto_pct": round(cubierto, 1),
         "explican_80_pct": len([f for f in filas if f["explica_80_pct"]]),
         "base_de_la_priorizacion": ("emision estimada" if total_emision else
                                     ("gasto anual" if total_gasto else "sin base: falta gasto o emision")),
         "foco_de_esta_semana": [f["nombre"] for f in criticos[:3]],
         "proveedores": filas,
         "mensaje": ("Estan ordenados por donde conviene partir: arriba los que pesan mucho y no "
                     "entregan datos.")},
        advertencias=advertencias)


def informe_html(opciones):
    perfil, ruta, ruta_json = _contexto(opciones)
    datos = _leer(ruta_json)
    proveedores = datos["proveedores"]
    if not proveedores:
        raise Problema(
            "No hay proveedores registrados, asi que no hay nada que mostrar en el informe.",
            "Registra al menos uno con: proveedores registrar --nombre \"Envases del Sur\".",
        )
    filas, total_emision, total_gasto = _ordenar_por_prioridad(proveedores)
    con_datos = [f for f in filas if f["entrego_datos"]]
    cubierto = round(sum(f["peso_pct"] for f in con_datos), 1)
    verificados = len([f for f in con_datos if f["calidad_dato"] == "verificado"])

    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Proveedores registrados", "valor": len(filas), "unidad": "",
             "detalle": "En la lista de seguimiento"},
            {"etiqueta": "Entregaron datos", "valor": len(con_datos), "unidad": "de %d" % len(filas),
             "detalle": "Respondieron el cuestionario",
             "color": "verde" if len(con_datos) * 2 >= len(filas) else "amarillo"},
            {"etiqueta": "Impacto cubierto", "valor": cubierto, "unidad": "%",
             "detalle": "Parte del gasto o de la emision con dato propio",
             "color": "verde" if cubierto >= 80 else ("amarillo" if cubierto >= 40 else "rojo")},
            {"etiqueta": "Datos verificados", "valor": verificados, "unidad": "",
             "detalle": "Revisados por un tercero"},
        ]},
        {"tipo": "texto", "texto": "Este informe muestra en que estado esta la peticion de datos a la "
                                   "cadena de suministro. El objetivo no es que respondan todos: es que "
                                   "respondan los que explican la mayor parte del impacto."},
    ]

    mayores = [f for f in sorted(filas, key=lambda x: -x["peso_pct"]) if f["peso_pct"] > 0][:8]
    if mayores:
        bloques.append({"tipo": "barras", "titulo": "Quienes pesan mas en la cadena", "unidad": "%",
                        "datos": [{"etiqueta": f["nombre"], "valor": f["peso_pct"],
                                   "color": "#2D6A4F" if f["entrego_datos"] else "#C1666B"}
                                  for f in mayores]})
        bloques.append({"tipo": "texto", "texto": "En verde los que ya entregaron datos; en rojo los que "
                                                  "todavia no. La prioridad son las barras rojas mas largas."})

    prioritarios = [f for f in filas if f["prioridad"] in ("alta", "media")][:10]
    if prioritarios:
        bloques.append({"tipo": "titulo", "texto": "Por donde partir", "nivel": 2})
        bloques.append({"tipo": "semaforo", "items": [
            {"etiqueta": f["nombre"],
             "estado": "rojo" if f["prioridad"] == "alta" else "amarillo",
             "estado_texto": "Prioridad alta" if f["prioridad"] == "alta" else "Mejorar dato",
             "detalle": f["accion_sugerida"]}
            for f in prioritarios]})

    bloques.append({"tipo": "titulo", "texto": "Todos los proveedores", "nivel": 2})
    bloques.append({"tipo": "tabla",
                    "columnas": ["Proveedor", "Categoria de compra", "Entrego datos", "Calidad del dato",
                                 "Peso (%)", "Prioridad"],
                    "numericas": [4],
                    "filas": [[f["nombre"], f["categoria_compra"] or "—",
                               "Si" if f["entrego_datos"] else "No",
                               f["calidad_dato"] or "—", f["peso_pct"], f["prioridad"]]
                              for f in filas],
                    "nota": "El peso se calcula con la %s." % (
                        "emision estimada" if total_emision else
                        ("participacion en el gasto anual" if total_gasto else
                         "informacion disponible, que hoy es insuficiente"))})
    bloques.append({"tipo": "nota", "estilo": "aviso", "texto": AVISO_DATO})
    bloques.append({"tipo": "nota", "estilo": "info", "texto": AVISO_PRIVACIDAD})

    destino = espacio.ruta_de(ruta, "reportes", "cadena-de-suministro.html")
    informe.escribir_html(destino, "Estado de la cadena de suministro", bloques,
                          marca=perfil.get("marca") or {},
                          subtitulo="%s — datos ESG solicitados a proveedores" % perfil.get("nombre", ""))
    return Respuesta(
        {"mensaje": "Informe listo: abrelo con doble clic y, si lo necesitas en PDF, imprimelo desde el navegador.",
         "archivo": destino,
         "total": len(filas),
         "cobertura_del_impacto_pct": cubierto},
        advertencias=[AVISO_PRIVACIDAD])


ACCIONES = {"cuestionario": cuestionario, "carta": carta, "registrar": registrar,
            "evaluar": evaluar, "informe": informe_html}
