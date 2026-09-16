# -*- coding: utf-8 -*-
"""Union Europea: que le exige Europa a un exportador y cuanto le cuesta."""

import datetime
import json
import os

from calculos import union_europea as ue
from nucleo import espacio, informe
from nucleo.salida import Problema, Respuesta

AYUDA = ("Normativa europea para quien exporta a Europa: CBAM (arancel de carbono), mercado de carbono "
         "maritimo y FuelEU en el flete, EUDR (deforestacion) y lo que piden los clientes europeos.")

ARCHIVO = "europa.json"
ARCHIVO_CUMPLIMIENTO = "cumplimiento.json"

AVISO_LEGAL = ue.AVISO_LEGAL
AVISO_INTERMEDIARIO = ("Aunque vendas a un intermediario y no directo a Europa, la exigencia llega igual: "
                       "el importador europeo se la traslada a quien le vende.")

# Estados miembros de la Union Europea, por codigo de dos letras.
PAISES_UE = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
             "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}

PREGUNTAS = [
    {"clave": "exporta_a_ue", "pregunta": "¿Venden a la Union Europea, directo o a traves de otra empresa?",
     "para_que": "Es la puerta de entrada: sin ventas a Europa no aplica casi nada de esto."},
    {"clave": "exporta_bienes_cbam",
     "pregunta": "¿Exportan hierro o acero, aluminio, cemento, fertilizantes, hidrogeno o electricidad?",
     "para_que": "Define si el importador europeo les va a pedir las emisiones incorporadas (CBAM)."},
    {"clave": "exporta_commodities_eudr",
     "pregunta": "¿Exportan ganado, cuero, cacao, cafe, aceite de palma, caucho, soya o madera?",
     "para_que": "Define si aplica el reglamento de deforestacion (EUDR)."},
    {"clave": "envia_por_mar", "pregunta": "¿La carga viaja a Europa por barco?",
     "para_que": "Define si el flete carga el recargo del mercado de carbono europeo y de FuelEU."},
    {"clave": "tiene_filial_ue", "pregunta": "¿Tienen una filial o sucursal propia en Europa?",
     "para_que": "Es lo unico que puede hacer que la empresa quede obligada directamente a reportar."},
]

CLAVES_VALIDAS = {p["clave"] for p in PREGUNTAS}

# La accion aplica lee sus respuestas recorriendo PREGUNTAS: se declaran para que la ayuda las muestre.
OPCIONES_DINAMICAS = {"aplica": sorted(CLAVES_VALIDAS)}


# --------------------------------------------------------------------------
# Contexto y almacenamiento
# --------------------------------------------------------------------------

def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    perfil, ruta = espacio.cargar_empresa(identificador, raiz=raiz)
    return perfil, ruta, espacio.ruta_de(ruta, "seguimiento", ARCHIVO)


def _leer(ruta_json):
    if not os.path.isfile(ruta_json):
        return {"respuestas": {}}
    with open(ruta_json, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except ValueError:
            raise Problema(
                "El archivo con los datos europeos de la empresa esta dañado.",
                "No lo edites a mano. Puedo rehacerlo: solo hay que repetir los calculos.",
            )
    datos.setdefault("respuestas", {})
    return datos


def _guardar(ruta_json, datos):
    datos["actualizado_el"] = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
    with open(ruta_json, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2, default=str)


def _respuestas_de_cumplimiento(ruta_empresa):
    """Reutiliza lo que la persona ya contesto en el diagnostico de normativa."""
    archivo = os.path.join(ruta_empresa, "seguimiento", ARCHIVO_CUMPLIMIENTO)
    if not os.path.isfile(archivo):
        return {}
    try:
        with open(archivo, encoding="utf-8") as origen:
            guardado = json.load(origen)
    except (ValueError, OSError):
        return {}
    respuestas = guardado.get("respuestas") or {}
    return {clave: valor for clave, valor in respuestas.items() if clave in CLAVES_VALIDAS}


def _valor(opciones, clave, por_defecto=""):
    valor = opciones.get(clave)
    return valor if valor and valor is not True else por_defecto


def _bandera(opciones, clave):
    valor = opciones.get(clave)
    if valor is True:
        return True
    return _si(valor) is True


def _si(valor):
    """Interpreta si / no / no se. Devuelve True, False o None."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().lower()
    if texto in ("si", "sí", "true", "1", "y", "yes", "claro"):
        return True
    if texto in ("no", "false", "0", "n", "ninguno"):
        return False
    return None


def _recoger_respuestas(opciones, guardado, perfil, ruta_empresa):
    """Junta lo guardado antes, lo del diagnostico y lo que venga en esta llamada."""
    respuestas = dict(_respuestas_de_cumplimiento(ruta_empresa))
    respuestas.update(guardado.get("respuestas") or {})
    nuevas = {}
    for pregunta in PREGUNTAS:
        valor = opciones.get(pregunta["clave"])
        if valor not in (None, ""):
            nuevas[pregunta["clave"]] = True if valor is True else valor
    respuestas.update(nuevas)
    if perfil.get("exporta_a_ue") and "exporta_a_ue" not in respuestas:
        respuestas["exporta_a_ue"] = "si"
    return respuestas, nuevas


def _trabajadores(perfil):
    try:
        return int(perfil.get("trabajadores") or 0) or None
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# Accion: aplica
# --------------------------------------------------------------------------

def _mecanismo(identificador, norma, estado, motivo, que_hacer, skill, riesgo="medio", detalle=None):
    # Lo que no aplica no deja tareas: una accion al lado de «no aplica» confunde.
    if estado == "no aplica" and not str(que_hacer).startswith("Nada"):
        que_hacer = "Nada por ahora."
    return {"id": identificador, "norma": norma, "estado": estado, "motivo": motivo,
            "que_hacer": que_hacer, "skill": skill, "riesgo": riesgo, "detalle": detalle or {}}


def _evaluar(perfil, respuestas):
    pais = (perfil.get("pais") or "").upper()
    en_la_ue = pais in PAISES_UE
    exporta = _si(respuestas.get("exporta_a_ue"))
    if exporta is None and perfil.get("exporta_a_ue"):
        exporta = True
    mecanismos = []

    # 1. Informe de sostenibilidad europeo (CSRD) sobre la propia empresa.
    csrd = ue.csrd_aplica(
        empleados=_trabajadores(perfil),
        volumen_negocios_eur=perfil.get("ingresos_anuales") if en_la_ue else None,
        establecida_en_ue=en_la_ue,
        volumen_negocios_en_ue_eur=respuestas.get("volumen_negocios_en_ue_eur"),
        filial_ue_volumen_eur=respuestas.get("filial_ue_volumen_eur"),
        tiene_filial_ue=_si(respuestas.get("tiene_filial_ue")),
    )
    mecanismos.append(_mecanismo(
        "csrd", "CSRD — informe de sostenibilidad europeo (Directiva 2013/34/UE tras la Directiva (UE) 2026/470)",
        csrd["estado"], csrd["motivo"],
        ("Nada por ahora: la obligacion es de la empresa europea, no tuya."
         if csrd["estado"] == "no aplica" else
         "Revisar con la asesoria del grupo en Europa cuanto se factura dentro de la Union Europea."),
        "union-europea", "medio" if csrd["estado"] != "aplica" else "alto",
        {"umbrales": csrd["umbrales"], "empresa_protegida": csrd["empresa_protegida"],
         "primer_informe": csrd["primer_informe"]}))

    # 2. Lo que piden los clientes europeos, con el tope VSME.
    if exporta is False:
        estado, motivo = "no aplica", "No venden a clientes de la Union Europea."
    elif exporta is None:
        estado, motivo = "revisar", "Falta confirmar si venden a la Union Europea, directo o por intermediario."
    else:
        estado = "aplica"
        motivo = ("Los clientes europeos obligados a reportar piden datos a sus proveedores. Si la empresa "
                  "no supera las 1.000 personas, el techo de lo exigible es el estandar voluntario VSME.")
    mecanismos.append(_mecanismo(
        "cadena_valor", "Exigencias del cliente europeo y tope VSME", estado, motivo,
        ("Preparar el paquete VSME: huella de carbono de alcance 1 y 2, datos basicos de personas y "
         "gobernanza, con respaldo. Sirve para todos los clientes a la vez."),
        "union-europea", "medio",
        {"tope_vsme": csrd["tope_vsme"]}))

    # 3. CBAM.
    bienes = _si(respuestas.get("exporta_bienes_cbam"))
    if exporta is False:
        estado_cbam, motivo_cbam = "no aplica", "No venden a la Union Europea."
    elif bienes is False:
        estado_cbam = "no aplica"
        motivo_cbam = ("Sus productos no estan en la lista del CBAM. Solo cubre cemento, electricidad, "
                       "fertilizantes, hierro y acero, aluminio e hidrogeno.")
    elif bienes is True and exporta is None:
        estado_cbam = "revisar"
        motivo_cbam = ("Exporta bienes que el CBAM cubre, pero falta confirmar si los vende a la Union Europea.")
    elif bienes is True:
        estado_cbam = "aplica"
        motivo_cbam = ("Exporta bienes cubiertos: el importador europeo declara y paga, pero necesita que la "
                       "empresa le entregue las emisiones incorporadas de cada envio.")
    else:
        estado_cbam = "revisar"
        motivo_cbam = ("Falta confirmar si exportan hierro o acero, aluminio, cemento, fertilizantes, "
                       "hidrogeno o electricidad.")
    mecanismos.append(_mecanismo(
        "cbam", "CBAM — Reglamento (UE) 2023/956, modificado por el Reglamento (UE) 2025/2083",
        estado_cbam, motivo_cbam,
        "Calcular las emisiones incorporadas por tonelada de producto y entregarselas al importador.",
        "cbam", "alto",
        {"periodo_definitivo": "Desde el 1 de enero de 2026.",
         "primera_declaracion": ue.CALENDARIO_CBAM["primera_declaracion"],
         "umbral_del_importador_t": ue.UMBRAL_MASA_CBAM_TONELADAS}))

    # 4. Flete maritimo: mercado de carbono europeo y FuelEU.
    por_mar = _si(respuestas.get("envia_por_mar"))
    if exporta is False:
        estado_mar, motivo_mar = "no aplica", "No envian carga a Europa."
    elif por_mar is False:
        estado_mar, motivo_mar = "no aplica", "La carga no viaja por barco a Europa."
    elif exporta is None:
        estado_mar, motivo_mar = "revisar", "Falta confirmar si venden a Europa y si la carga viaja por barco."
    elif por_mar is None:
        # Sin saber si la carga va en barco no se puede decir que llega el recargo (hallazgo E2E).
        estado_mar, motivo_mar = "revisar", "Falta confirmar si la carga viaja a Europa por barco."
    else:
        estado_mar = "aplica"
        motivo_mar = ("Desde 2026 la naviera entrega derechos por el 100 % de sus emisiones verificadas y en "
                      "las rutas Sudamerica-Europa se cubre el 50 % del viaje. Ese costo llega como recargo "
                      "en el flete, aunque la empresa no tenga ninguna obligacion propia.")
    mecanismos.append(_mecanismo(
        "maritimo", "Mercado de carbono maritimo (Directiva (UE) 2023/959) y FuelEU (Reglamento (UE) 2023/1805)",
        estado_mar, motivo_mar,
        ("Pedirle a la naviera el desglose del recargo: que aplique el 50 % en rutas Sudamerica-Europa, con "
         "que precio del derecho europeo y separando el recargo de FuelEU."),
        "maritimo-ets", "medio",
        {"cobertura_del_viaje": "50 % entre un tercer pais y la Union Europea",
         "entrega_2026": "100 % de las emisiones verificadas",
         "gases_desde_2026": "CO2, metano y oxido nitroso"}))

    # 5. EUDR.
    commodities = _si(respuestas.get("exporta_commodities_eudr"))
    if exporta is False:
        estado_eudr = "no aplica"
        motivo_eudr = "No venden a la Union Europea."
    elif commodities is False:
        estado_eudr = "no aplica"
        motivo_eudr = ("Sus productos no estan entre las siete materias primas cubiertas (ganado, cacao, "
                       "cafe, palma, caucho, soya y madera).")
    elif commodities is True and exporta is None:
        estado_eudr = "revisar"
        motivo_eudr = ("Exporta materias primas que el EUDR cubre, pero falta confirmar si las vende a la Union "
                       "Europea.")
    elif commodities is True:
        estado_eudr = "aplica"
        riesgo, listado = ue.riesgo_pais_eudr(pais)
        motivo_eudr = ("Exporta materias primas cubiertas. %s queda en riesgo %s, asi que la diligencia "
                       "debida del operador europeo es %s."
                       % (espacio.PAISES.get(pais, pais or "El pais"), riesgo,
                          "simplificada" if riesgo == "bajo" else "completa"))
    else:
        estado_eudr = "revisar"
        motivo_eudr = "Falta confirmar si exportan ganado, cuero, cacao, cafe, palma, caucho, soya o madera."
    mecanismos.append(_mecanismo(
        "eudr", "EUDR — Reglamento (UE) 2023/1115, tras el Reglamento (UE) 2025/2650",
        estado_eudr, motivo_eudr,
        ("Reunir la geolocalizacion de cada predio y las pruebas de que no hubo deforestacion despues del "
         "31 de diciembre de 2020."),
        "eudr", "alto",
        {"fecha_de_corte": ue.FECHA_CORTE_EUDR,
         "grandes_y_medianas": ue.FECHAS_EUDR["grande"],
         "micro_y_pequenas": ue.FECHAS_EUDR["micro"]}))

    # 6. Diligencia debida del cliente (CSDDD).
    # La directiva obliga al cliente europeo grande, no a su proveedor: decir «aplica»
    # a un exportador de 85 personas seria un falso positivo. Lo que le llega a el son
    # clausulas de contrato, y eso se marca como «por el cliente».
    empleados = _trabajadores(perfil)
    grande = (empleados is not None and empleados > ue.UMBRALES_CSDDD["empleados"])
    if en_la_ue and grande:
        estado_csddd = "revisar"
        motivo_csddd = ("La empresa esta en la Union Europea y supera los %s empleados: falta confirmar si su "
                        "volumen de negocios pasa los 1.500 millones de euros. Si los pasa, le aplica desde el "
                        "26 de julio de 2029." % ue.UMBRALES_CSDDD["empleados"])
    elif exporta is False:
        estado_csddd = "no aplica"
        motivo_csddd = "No vende a clientes de la Union Europea."
    elif exporta is None:
        estado_csddd = "revisar"
        motivo_csddd = "Falta confirmar si venden a la Union Europea, directo o por intermediario."
    else:
        estado_csddd = "por el cliente"
        motivo_csddd = ("No es una obligacion de la empresa: tras la reforma de 2026 solo obliga a empresas de "
                        "mas de 5.000 empleados y 1.500 millones de euros, desde el 26 de julio de 2029. Lo que "
                        "si llega son las clausulas de derechos humanos y ambiente que los grandes compradores "
                        "ya ponen en sus contratos.")
    mecanismos.append(_mecanismo(
        "csddd", "CSDDD — diligencia debida del cliente europeo (Directiva (UE) 2024/1760 tras la 2026/470)",
        estado_csddd, motivo_csddd,
        "Mantener al dia las politicas laborales, ambientales y de proveedores que piden esos contratos.",
        "union-europea", "medio", {"umbrales": ue.UMBRALES_CSDDD}))

    return mecanismos


def aplica(opciones):
    """Que normativa europea le afecta a la empresa, segun su perfil y sus respuestas."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    respuestas, nuevas = _recoger_respuestas(opciones, guardado, perfil, ruta)
    mecanismos = _evaluar(perfil, respuestas)

    guardado["respuestas"] = respuestas
    guardado["aplica"] = {"mecanismos": mecanismos,
                          "evaluado_el": datetime.date.today().isoformat()}
    _guardar(ruta_json, guardado)

    aplican = [m for m in mecanismos if m["estado"] == "aplica"]
    revisar = [m for m in mecanismos if m["estado"] == "revisar"]
    por_el_cliente = [m for m in mecanismos if m["estado"] == "por el cliente"]
    pendientes = [p for p in PREGUNTAS if _si(respuestas.get(p["clave"])) is None]

    advertencias = [AVISO_LEGAL]
    if revisar:
        advertencias.append("Hay %d punto(s) que no puedo decidir sin un dato mas: preguntalos de a uno."
                            % len(revisar))
    if _si(respuestas.get("exporta_a_ue")) is None:
        advertencias.append(AVISO_INTERMEDIARIO)

    return Respuesta({
        "empresa": perfil.get("nombre"),
        "pais": (perfil.get("pais") or "").upper(),
        "exporta_a_ue": _si(respuestas.get("exporta_a_ue")),
        "resumen": ("Le aplican %d mecanismos europeos; %d quedan por confirmar y %d le llegan solo por "
                    "contrato con el cliente." % (len(aplican), len(revisar), len(por_el_cliente))),
        "mecanismos": mecanismos,
        "aplican": [m["norma"] for m in aplican],
        "por_revisar": [{"norma": m["norma"], "motivo": m["motivo"]} for m in revisar],
        "no_aplican": [m["norma"] for m in mecanismos if m["estado"] == "no aplica"],
        "le_llegan_por_el_cliente": [{"norma": m["norma"], "motivo": m["motivo"]} for m in por_el_cliente],
        "preguntas_pendientes": pendientes,
        "respuestas_guardadas": nuevas or {},
        "siguiente_paso": ("Responde lo que falte con, por ejemplo: europa aplica --exporta-bienes-cbam si. "
                           "Despues: europa cbam, europa maritimo o europa eudr."),
        "fuente": ue.FUENTE,
    }, advertencias=advertencias)


# --------------------------------------------------------------------------
# Accion: cbam
# --------------------------------------------------------------------------

def _precursores(texto):
    """Lee «120:1,8; 30:0,9» como lista de precursores masa:SEE."""
    if not texto or texto is True:
        return []
    salida = []
    for pieza in str(texto).replace(";", ",").split(","):
        pieza = pieza.strip()
        if not pieza:
            continue
        partes = pieza.split(":")
        if len(partes) < 2:
            raise Problema(
                "No entendi el precursor «%s»." % pieza,
                "Escribelos como masa:emisiones, separados por coma. Por ejemplo: 120:1.8, 30:0.9.",
            )
        salida.append({"masa": partes[0], "see": partes[1],
                       "nombre": partes[2].strip() if len(partes) > 2 else "precursor"})
    return salida


def cbam(opciones):
    """Emisiones incorporadas y costo CBAM del envio, con los datos de la empresa."""
    perfil, ruta, ruta_json = _contexto(opciones)
    sector = _valor(opciones, "sector")
    if not sector:
        raise Problema(
            "Falta decirme que producto se exporta.",
            ("El CBAM solo cubre seis sectores: cemento, electricidad, fertilizantes, hierro y acero, "
             "aluminio e hidrogeno. Usa --sector acero (o el que corresponda)."),
        )
    anio = int(_valor(opciones, "anio", datetime.date.today().year))

    # Sin datos de la planta no hay emisiones que calcular, pero si se puede decir si el
    # producto esta cubierto y si el importador queda bajo el umbral de 50 t. Eso es lo
    # primero que necesita saber la persona, y no depende de las emisiones.
    tiene_datos_planta = any(_valor(opciones, clave, None) not in (None, "")
                             for clave in ("see", "emisiones_directas"))
    if not tiene_datos_planta:
        ficha = ue.sector_cbam(sector)
        # En acero y aluminio el Anexo I cubre solo algunas partidas de las manufacturas, y el
        # detalle por subpartida no quedo verificado: hay que confirmar el codigo del producto.
        cobertura_parcial = "determinad" in ficha["codigos_nc"]
        salvedad = (" Ojo: en %s el CBAM cubre solo algunas partidas de las manufacturas; confirma que el codigo "
                    "arancelario exacto del producto este en el Anexo I del Reglamento (UE) 2023/956."
                    % ficha["nombre"].lower()) if cobertura_parcial else ""
        masa = _valor(opciones, "masa_anual_importador", None)
        umbral = ue.cbam_umbral_masa(masa, ficha["clave"]) if masa not in (None, "") else None
        if umbral and umbral["exento"]:
            conclusion = ("El producto esta cubierto por el CBAM, pero con %s t al año el importador queda bajo el "
                          "umbral de 50 t y no tiene que declarar ni comprar certificados por estas compras."
                          % umbral["masa_toneladas"])
        elif umbral:
            conclusion = ("El producto esta cubierto por el CBAM y el importador supera las 50 t al año: va a "
                          "necesitar las emisiones incorporadas de cada envio.")
        elif ficha["de_minimis"]:
            conclusion = ("El producto esta cubierto por el CBAM. Si el importador europeo trae menos de 50 t al "
                          "año sumando TODOS sus proveedores de estos productos, queda exento; si no, te va a pedir "
                          "las emisiones incorporadas.")
        else:
            conclusion = ("El producto esta cubierto por el CBAM y este sector no tiene umbral de 50 t: entra "
                          "desde el primer kilo.")
        return Respuesta({
            "empresa": perfil.get("nombre"),
            "producto": ficha["nombre"],
            "cubierto_por_el_cbam": "confirmar codigo arancelario" if cobertura_parcial else True,
            "codigos_arancelarios": ficha["codigos_nc"],
            "umbral_del_importador": umbral or {
                "umbral_toneladas": ue.UMBRAL_MASA_CBAM_TONELADAS if ficha["de_minimis"] else None,
                "como_saberlo": "Preguntale al importador cuantas toneladas de estos productos trae al año en total "
                                "(--masa-anual-importador)."},
            "en_una_frase": conclusion + salvedad,
            "emisiones": None,
            "que_pedirle_a_la_planta": [
                "Emisiones especificas incorporadas por tonelada del producto (SEE), con su metodo y periodo.",
                "O bien: emisiones directas de la instalacion y su nivel de actividad del periodo.",
                "Si hay precursores (por ejemplo, el acero con que se fabrican los pernos), sus emisiones.",
                "Si pagaron un precio del carbono en el pais de origen, el comprobante.",
            ],
            "siguiente_paso": ("Con esos datos: europa cbam --sector %s --cantidad <toneladas> --see <t CO2e por t> "
                               "--precio-certificado <euros>." % ficha["clave"]),
            "fuente": ue.FUENTE,
        }, advertencias=[AVISO_LEGAL,
                         "No calcule emisiones ni costo porque no hay datos de la planta. El motor no usa valores "
                         "por defecto del CBAM definitivo porque no estan verificados."])

    emisiones = ue.cbam_emisiones_incorporadas(
        sector,
        _valor(opciones, "cantidad"),
        see=_valor(opciones, "see", None),
        emisiones_directas=_valor(opciones, "emisiones_directas", None),
        emisiones_indirectas=_valor(opciones, "emisiones_indirectas", None),
        nivel_actividad=_valor(opciones, "nivel_actividad", None),
        precursores=_precursores(opciones.get("precursores")),
    )
    costo = ue.cbam_costo_estimado(
        emisiones["emisiones_incorporadas_t_co2e"], anio,
        _valor(opciones, "precio_certificado", None),
        deduccion_certificados=_valor(opciones, "deduccion_certificados", None),
        precio_carbono_origen_eur_t=_valor(opciones, "precio_carbono_origen", None),
        cantidad_toneladas=emisiones["cantidad_toneladas"],
        masa_neta_anual_importador=_valor(opciones, "masa_anual_importador", None),
        sector=emisiones["sector"],
    )
    curva = ue.cbam_curva(emisiones["emisiones_incorporadas_t_co2e"], costo["precio_certificado_eur"],
                          emisiones["cantidad_toneladas"])

    guardado = _leer(ruta_json)
    guardado.setdefault("cbam", []).append({"anio": anio, "sector": emisiones["sector"],
                                            "emisiones": emisiones, "costo": costo,
                                            "calculado_el": datetime.date.today().isoformat()})
    guardado["cbam"] = guardado["cbam"][-20:]
    _guardar(ruta_json, guardado)

    destino = espacio.ruta_de(ruta, "resultados", "cbam_%s_%d.json" % (emisiones["sector"], anio))
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump({"emisiones": emisiones, "costo": costo, "curva": curva},
                  archivo, ensure_ascii=False, indent=2, default=str)

    advertencias = [AVISO_LEGAL] + emisiones["advertencias"] + costo["advertencias"]
    return Respuesta({
        "empresa": perfil.get("nombre"),
        "producto": emisiones["sector_nombre"],
        "codigos_arancelarios": emisiones["codigos_nc"],
        "emisiones": emisiones,
        "costo": costo,
        "curva_hasta_2034": curva,
        "que_entregarle_al_importador": [
            "Identificacion de la instalacion donde se produjo la mercancia.",
            "Emisiones especificas incorporadas por tonelada (%s t CO2e/t en este calculo)."
            % emisiones["see_t_co2e_por_t"],
            "Periodo de referencia y metodo con que se calcularon.",
            "Si corresponde, el precio del carbono pagado en el pais de origen, con documentacion de pago.",
            "Verificacion de un tercero: sube la credibilidad y evita que usen valores por defecto.",
        ],
        "archivo": destino,
        "fuente": ue.FUENTE,
    }, advertencias=advertencias, fuentes=costo["articulos"] + emisiones["articulos"])


# --------------------------------------------------------------------------
# Accion: maritimo
# --------------------------------------------------------------------------

def _gwp(opciones):
    ch4 = _valor(opciones, "gwp_ch4", None)
    n2o = _valor(opciones, "gwp_n2o", None)
    if ch4 is None and n2o is None:
        return None
    return {"ch4": ch4, "n2o": n2o, "co2": _valor(opciones, "gwp_co2", 1.0)}


def maritimo(opciones):
    """Recargo del mercado de carbono europeo (ETS) y penalizacion FuelEU del flete."""
    perfil, ruta, ruta_json = _contexto(opciones)
    anio = int(_valor(opciones, "anio", datetime.date.today().year))
    gwp = _gwp(opciones)
    incluir = _bandera(opciones, "incluir_ch4_n2o") or (gwp is not None and _valor(opciones, "gwp_ch4", None))

    teu = _valor(opciones, "teu", None)
    if teu is None and _valor(opciones, "capacidad_teu", None):
        capacidad = float(str(_valor(opciones, "capacidad_teu")).replace(",", "."))
        ocupacion = float(str(_valor(opciones, "ocupacion", 1.0)).replace(",", "."))
        if ocupacion > 1:
            ocupacion = ocupacion / 100.0
        teu = capacidad * ocupacion

    # El ETS se mide por viaje y FuelEU por buque y año: quien pregunta solo por
    # uno de los dos no tiene por que traer los datos del otro.
    hay_viaje = _valor(opciones, "consumo", None) or _valor(opciones, "emisiones_viaje", None)
    hay_buque = _valor(opciones, "consumo_anual", None) or _valor(opciones, "ghgie_actual", None)
    ets = None
    if hay_viaje or not hay_buque:
        ets = ue.ets_maritimo_obligacion(
            anio,
            tipo_viaje=_valor(opciones, "tipo_viaje", "tercer_pais_ue"),
            emisiones_viaje_t=_valor(opciones, "emisiones_viaje", None),
            consumo_toneladas=_valor(opciones, "consumo", None),
            combustible=_valor(opciones, "combustible", "HFO"),
            precio_eua_eur=_valor(opciones, "precio_eua", None),
            teu=teu,
            incluir_ch4_n2o=bool(incluir),
            gwp=gwp,
        )

    # FuelEU se mide por buque y por año completo, no por viaje.
    fueleu = None
    consumo_anual = _valor(opciones, "consumo_anual", None)
    ghgie = _valor(opciones, "ghgie_actual", None)
    if consumo_anual or ghgie:
        consumos = ([{"combustible": _valor(opciones, "combustible", "HFO"), "toneladas": consumo_anual}]
                    if consumo_anual else None)
        try:
            fueleu = ue.fueleu_balance(
                anio, consumos=consumos, ghgie_actual=ghgie,
                energia_total_mj=_valor(opciones, "energia_total", None),
                energia_ops_mj=_valor(opciones, "energia_ops", 0),
                co2eq_ops=_valor(opciones, "co2eq_ops", None),
                gwp=gwp,
                periodos_consecutivos=_valor(opciones, "periodos_consecutivos", 1),
            )
        except Problema as problema:
            fueleu = {"no_se_pudo_calcular": problema.mensaje, "que_necesito": problema.sugerencia}
    else:
        fueleu = {"no_se_pudo_calcular": "No me diste el consumo anual del buque ni su intensidad verificada.",
                  "que_necesito": ("FuelEU se mide por buque y por año completo, no por viaje. Pidele a la "
                                   "naviera el consumo del periodo dentro del ambito europeo (--consumo-anual) "
                                   "o el balance que ya le verificaron (--ghgie-actual y --energia-total).")}

    guardado = _leer(ruta_json)
    guardado["maritimo"] = {"anio": anio, "ets": ets, "fueleu": fueleu,
                            "calculado_el": datetime.date.today().isoformat()}
    _guardar(ruta_json, guardado)

    advertencias = [AVISO_LEGAL] + (ets["advertencias"] if ets else [])
    if ets is None:
        advertencias.append("ETS: no lo calcule porque no me diste un viaje. Para el recargo del mercado de "
                            "carbono necesito el consumo del viaje en toneladas (--consumo) o sus emisiones "
                            "(--emisiones-viaje).")
    if isinstance(fueleu, dict) and fueleu.get("no_se_pudo_calcular"):
        advertencias.append("FuelEU: %s %s" % (fueleu["no_se_pudo_calcular"], fueleu["que_necesito"]))
    elif fueleu:
        advertencias.extend(fueleu.get("advertencias") or [])

    if ets:
        frase = ("El viaje paga %s derechos de emision. Con el precio que indicaste son %s euros%s."
                 % (round(ets["derechos_a_entregar_t"], 1), round(ets["costo_eur"], 2),
                    (", o %s euros por contenedor de 20 pies"
                     % round(ets["recargo_por_teu_eur"], 2)) if ets["recargo_por_teu_eur"] else ""))
    elif isinstance(fueleu, dict) and fueleu.get("penalizacion_eur") is not None:
        frase = "La penalizacion FuelEU del buque en %s es de %s euros." % (anio, round(fueleu["penalizacion_eur"], 2))
    else:
        frase = "Con estos datos no pude calcular ni el ETS ni FuelEU: revisa las advertencias."

    return Respuesta({
        "empresa": perfil.get("nombre"),
        "anio": anio,
        "ets": ets,
        "fueleu": fueleu,
        "en_una_frase": frase,
        "son_dos_cosas_distintas": ("El mercado de carbono cobra por las toneladas emitidas y FuelEU castiga "
                                    "la intensidad del combustible. Se pagan los dos y no se compensan entre "
                                    "si: un recargo que los junte sin desglosar hay que cuestionarlo."),
        "fuente": ue.FUENTE,
    }, advertencias=advertencias, fuentes=ets["articulos"] if ets else [])


# --------------------------------------------------------------------------
# Accion: eudr
# --------------------------------------------------------------------------

def eudr(opciones):
    """Lista de verificacion de diligencia debida del reglamento de deforestacion."""
    perfil, ruta, ruta_json = _contexto(opciones)
    pais = _valor(opciones, "pais") or (perfil.get("pais") or "")
    resultado = ue.eudr_aplica(
        producto=_valor(opciones, "producto") or _valor(opciones, "materia_prima"),
        pais=pais,
        tamano_operador=_valor(opciones, "tamano_operador"),
        cubierto_por_eutr=_bandera(opciones, "cubierto_por_eutr"),
    )

    por_lote = [i for i in ue.INFORMACION_EUDR if i["por"] == "lote"]
    por_predio = [i for i in ue.INFORMACION_EUDR if i["por"] == "predio"]
    verificacion = []
    if resultado["estado"] == "aplica":
        for paso in resultado["pasos_de_diligencia"]:
            verificacion.append({
                "paso": paso["paso"], "titulo": paso["titulo"], "articulo": paso["articulo"],
                "exigible": paso["exigible"], "detalle": paso["detalle"],
                "estado": "por hacer" if paso["exigible"] else "no exigible con riesgo bajo",
            })

    guardado = _leer(ruta_json)
    guardado["eudr"] = dict(resultado, revisado_el=datetime.date.today().isoformat())
    _guardar(ruta_json, guardado)

    advertencias = [AVISO_LEGAL]
    if resultado["estado"] == "aplica" and not resultado.get("fecha_de_aplicacion"):
        advertencias.append(resultado["nota_fecha"])
    if resultado["estado"] == "aplica":
        advertencias.append(
            "El formato exacto de la geolocalizacion tras las reformas de 2024 y 2025 no esta confirmado: "
            "pidele a tu cliente europeo el formato que exige su sistema antes de levantar los datos en terreno.")

    return Respuesta({
        "empresa": perfil.get("nombre"),
        "evaluacion": resultado,
        "que_reunir_por_lote": por_lote,
        "que_reunir_por_predio": por_predio,
        "lista_de_verificacion": verificacion,
        "como_organizarlo": [
            "Una planilla por predio: codigo del predio, productor, superficie, coordenadas y evidencia "
            "de que no hubo deforestacion despues del 31 de diciembre de 2020.",
            "Una planilla por lote de exportacion: kilos, predios de origen, proveedor, comprador y "
            "numero de referencia de la declaracion del operador europeo.",
            "Guardar todo cinco años: es el plazo de conservacion del art. 9.",
            "Si compras a terceros, el contrato tiene que obligar al proveedor a entregar coordenadas y "
            "pruebas; sin eso el lote no se puede declarar.",
        ],
        "fuente": ue.FUENTE,
    }, advertencias=advertencias, fuentes=resultado.get("articulos") or [])


# --------------------------------------------------------------------------
# Accion: informe
# --------------------------------------------------------------------------

_COLOR_ESTADO = {"aplica": "rojo", "revisar": "amarillo", "no aplica": "verde", "por el cliente": "gris"}


def _bloques_cbam(guardado):
    calculos = guardado.get("cbam") or []
    if not calculos:
        return []
    ultimo = calculos[-1]
    emisiones, costo = ultimo["emisiones"], ultimo["costo"]
    bloques = [
        {"tipo": "titulo", "texto": "CBAM — arancel de carbono en frontera", "nivel": 2},
        {"tipo": "kpi", "items": [
            {"etiqueta": "Producto", "valor": emisiones["sector_nombre"], "unidad": "",
             "detalle": "%s toneladas del envio" % emisiones["cantidad_toneladas"]},
            {"etiqueta": "Emisiones incorporadas", "valor": emisiones["emisiones_incorporadas_t_co2e"],
             "unidad": "t CO2e", "detalle": "%s t CO2e por tonelada" % emisiones["see_t_co2e_por_t"]},
            {"etiqueta": "Costo %d" % costo["anio"], "valor": costo["costo_eur"], "unidad": "EUR",
             "detalle": "Exigible el %s %% de la obligacion" % round(costo["porcentaje_exigible"] * 100, 1),
             "color": "amarillo"},
        ]},
        {"tipo": "texto", "texto": ("Se calcula asi: emisiones incorporadas por el porcentaje exigible del "
                                    "año, menos el carbono ya pagado en el pais de origen, por el precio del "
                                    "certificado. El precio usado fue de %s euros por tonelada."
                                    % costo["precio_certificado_eur"])},
    ]
    curva = []
    for anio in range(2026, 2035):
        fila = ue.cbam_costo_estimado(emisiones["emisiones_incorporadas_t_co2e"], anio,
                                      costo["precio_certificado_eur"],
                                      cantidad_toneladas=emisiones["cantidad_toneladas"])
        curva.append({"etiqueta": str(anio), "valor": round(fila["costo_eur"], 2)})
    bloques.append({"tipo": "barras", "titulo": "Costo del mismo envio, año a año (EUR)",
                    "datos": curva, "unidad": "EUR"})
    bloques.append({"tipo": "nota", "estilo": "aviso",
                    "texto": ("El costo se multiplica por cuarenta entre 2026 y 2034, cuando desaparece la "
                              "asignacion gratuita. Quien hoy mire el CBAM y diga «son tres euros por "
                              "tonelada» esta leyendo mal la curva.")})
    return bloques


def _bloques_maritimo(guardado):
    datos = guardado.get("maritimo")
    if not datos:
        return []
    ets = datos.get("ets")
    bloques = [{"tipo": "titulo", "texto": "Flete maritimo: mercado de carbono europeo y FuelEU", "nivel": 2}]
    if ets:
        bloques.extend([
            {"tipo": "kpi", "items": [
                {"etiqueta": "Emisiones cubiertas", "valor": ets["emisiones_cubiertas_t_co2e"], "unidad": "t CO2e",
                 "detalle": "%s %% del viaje" % round(ets["cobertura_viaje"] * 100)},
                {"etiqueta": "Costo del viaje", "valor": ets["costo_eur"], "unidad": "EUR",
                 "detalle": "Entrega del %s %% en %d" % (round(ets["porcentaje_entrega"] * 100), ets["anio"])},
                {"etiqueta": "Recargo por contenedor", "valor": ets["recargo_por_teu_eur"], "unidad": "EUR/TEU",
                 "detalle": "Referencia para negociar el flete", "color": "amarillo"},
            ]},
            {"tipo": "titulo", "texto": "Que pedirle a la naviera", "nivel": 3},
            {"tipo": "lista", "items": ets["que_pedirle_a_la_naviera"]},
        ])
    else:
        # Se calculo solo FuelEU, que va por buque y año: no hay un viaje del que sacar el recargo.
        bloques.append({"tipo": "nota", "estilo": "aviso",
                        "texto": "No se calculo el recargo del mercado de carbono porque no se indico un viaje. "
                                 "Para calcularlo hace falta el consumo del viaje o sus emisiones."})
    fueleu = datos.get("fueleu") or {}
    if fueleu.get("penalizacion_eur") is not None:
        bloques.append({"tipo": "texto", "texto": (
            "FuelEU %d: el limite de intensidad es %s gramos de CO2 equivalente por megajoule y el buque "
            "declara %s. El balance es de %s toneladas de CO2 equivalente y la penalizacion estimada, %s euros."
            % (fueleu["anio"], round(fueleu["objetivo_gco2e_mj"], 4),
               round(fueleu["intensidad_real_gco2e_mj"], 4), round(fueleu["balance_t_co2e"], 1),
               round(fueleu["penalizacion_eur"], 2)))})
    elif fueleu.get("no_se_pudo_calcular"):
        bloques.append({"tipo": "nota", "estilo": "aviso",
                        "texto": "FuelEU: %s %s" % (fueleu["no_se_pudo_calcular"], fueleu["que_necesito"])})
    return bloques


def _bloques_eudr(guardado):
    datos = guardado.get("eudr")
    if not datos or datos.get("estado") != "aplica":
        return []
    return [
        {"tipo": "titulo", "texto": "EUDR — productos libres de deforestacion", "nivel": 2},
        {"tipo": "kpi", "items": [
            {"etiqueta": "Materia prima", "valor": datos["materia_prima_nombre"], "unidad": ""},
            {"etiqueta": "Riesgo del pais", "valor": datos["riesgo_pais"], "unidad": "",
             "color": "verde" if datos["riesgo_pais"] == "bajo" else "amarillo"},
            {"etiqueta": "Diligencia debida", "valor": datos["diligencia"], "unidad": "",
             "detalle": datos.get("fecha_de_aplicacion") or "Fecha segun el tamaño del importador"},
        ]},
        {"tipo": "texto", "texto": datos["explicacion_diligencia"]},
        {"tipo": "titulo", "texto": "Informacion que hay que reunir", "nivel": 3},
        {"tipo": "tabla", "columnas": ["Dato", "Por", "Articulo"],
         "filas": [[i["que"], i["por"], i["articulo"]] for i in datos["informacion_requerida"]]},
        {"tipo": "nota", "estilo": "riesgo",
         "texto": ("Fecha de corte: %s. Si el predio fue deforestado despues de esa fecha, el producto no "
                   "puede entrar a Europa, aunque la deforestacion haya sido legal en el pais."
                   % datos["fecha_de_corte"])},
    ]


def informe_html(opciones):
    """Informe HTML con todo lo europeo de la empresa."""
    perfil, ruta, ruta_json = _contexto(opciones)
    guardado = _leer(ruta_json)
    respuestas = guardado.get("respuestas") or _respuestas_de_cumplimiento(ruta)
    # Siempre desde las respuestas: un veredicto guardado por una version anterior del motor puede estar mal.
    mecanismos = _evaluar(perfil, respuestas)

    aplican = [m for m in mecanismos if m["estado"] == "aplica"]
    revisar = [m for m in mecanismos if m["estado"] == "revisar"]

    bloques = [
        {"tipo": "texto", "texto": ("Resumen de lo que Europa le exige a %s y por que via le llega. Ninguna "
                                    "de estas normas obliga directamente a una empresa de fuera de la Union "
                                    "Europea: llegan por contrato con el cliente, por el importador o por el "
                                    "flete." % perfil.get("nombre", "la empresa"))},
        {"tipo": "kpi", "items": [
            {"etiqueta": "Mecanismos que le afectan", "valor": len(aplican), "unidad": "", "color": "rojo"},
            {"etiqueta": "Por confirmar", "valor": len(revisar), "unidad": "", "color": "amarillo",
             "detalle": "Falta un dato para decidir"},
            {"etiqueta": "Solo por contrato", "valor": len([m for m in mecanismos if m["estado"] == "por el cliente"]),
             "unidad": "", "color": "gris", "detalle": "Obligacion del cliente europeo, no de la empresa"},
            {"etiqueta": "Fuera de alcance", "valor": len([m for m in mecanismos if m["estado"] == "no aplica"]),
             "unidad": "", "color": "verde"},
        ]},
        {"tipo": "titulo", "texto": "Mapa de exigencias europeas", "nivel": 2},
        {"tipo": "semaforo", "items": [
            {"etiqueta": m["norma"],
             "estado": _COLOR_ESTADO.get(m["estado"], "gris"),
             "estado_texto": m["estado"].capitalize(),
             "detalle": "%s %s" % (m["motivo"], m["que_hacer"] if m["estado"] != "no aplica" else "")}
            for m in mecanismos]},
    ]
    # Un calculo guardado no se muestra si hoy el mecanismo no le aplica: el informe se contradeciria.
    estados = {m["id"]: m["estado"] for m in mecanismos}
    for clave, armar in (("cbam", _bloques_cbam), ("maritimo", _bloques_maritimo), ("eudr", _bloques_eudr)):
        secciones = armar(guardado)
        if not secciones:
            continue
        if estados.get(clave) in ("aplica", "revisar"):
            bloques.extend(secciones)
        else:
            bloques.append({"tipo": "nota", "estilo": "info",
                            "texto": "Hay un calculo guardado de %s, pero con las respuestas actuales no le aplica a "
                                     "la empresa: no se muestra." % clave.upper()})

    sin_verificar = ue.pendientes(*sorted(ue.PENDIENTES_DE_VERIFICAR))
    bloques.extend([
        {"tipo": "titulo", "texto": "Lo que todavia no esta confirmado", "nivel": 2},
        {"tipo": "texto", "texto": ("Estos puntos no se pudieron verificar contra el texto oficial. El motor "
                                    "no los inventa: cuando hacen falta, pide el dato.")},
        {"tipo": "tabla", "columnas": ["Que falta", "Que significa", "Como resolverlo"],
         "filas": [[p["que_falta"], p["consecuencia"], p["como_resolverlo"]] for p in sin_verificar]},
        {"tipo": "nota", "estilo": "aviso", "texto": AVISO_LEGAL},
    ])

    destino = espacio.ruta_de(ruta, "reportes", "normativa-europea.html")
    informe.escribir_html(destino, "Normativa europea aplicable", bloques,
                          marca=perfil.get("marca") or {}, subtitulo=perfil.get("nombre", ""))
    return Respuesta({"mensaje": "Informe de normativa europea listo.", "archivo": destino,
                      "mecanismos_que_aplican": len(aplican), "por_revisar": len(revisar)},
                     advertencias=[AVISO_LEGAL])


ACCIONES = {"aplica": aplica, "cbam": cbam, "maritimo": maritimo, "eudr": eudr, "informe": informe_html}
