# -*- coding: utf-8 -*-
"""Reportes de sostenibilidad: que pide cada marco, que puede reportar la empresa hoy y el borrador."""

import datetime
import json
import os

from calculos import reportes as catalogo
from calculos import social
from nucleo import espacio, excel, informe, word
from nucleo.salida import Problema, Respuesta

AYUDA = ("Compara los marcos de reporte, revisa que puede reportar la empresa con los datos que ya tiene y "
         "arma el borrador del reporte y su indice de contenidos.")

AVISO = ("El borrador no es un reporte final ni una verificacion: es un punto de partida armado con los datos de "
         "esta carpeta. Hay que completarlo, revisarlo con quien corresponda y respaldar cada cifra antes de "
         "publicarlo.")

AVISO_GREENWASHING = [
    "No uses palabras generales como «ecologico», «verde» o «sostenible» sin una medicion detras. En la Union "
    "Europea esas alegaciones genericas estan prohibidas desde el 27 de septiembre de 2026 si no hay un "
    "desempeno ambiental excelente y reconocido que las respalde.",
    "No digas que la empresa o el producto es neutro en carbono cuando la neutralidad descansa solo en comprar "
    "compensaciones: esa afirmacion esta prohibida en la Union Europea.",
    "No apliques a toda la empresa un logro que solo alcanza a un producto, una planta o un periodo.",
    "Si prometes algo a futuro, necesitas un plan detallado y publico, con hitos y con verificacion periodica de "
    "un tercero independiente. Sin eso, la promesa es el problema.",
    "Si comparas con otro producto, publica el metodo de comparacion, que productos comparaste y como mantienes "
    "esa informacion al dia.",
    "No presentes como merito algo que la ley ya te obliga a hacer.",
    "En Chile la Ley 19.496 sanciona la publicidad falsa o enganosa con hasta 1.500 UTM, y hasta 2.250 UTM "
    "cuando incide sobre la salud, la seguridad o el medio ambiente.",
]

COMO_ELEGIR = ("GRI para clientes y publico general; NIIF S1 y S2 para inversionistas, bancos y reguladores; "
               "NCG 461 y NCG 519 si la empresa esta supervisada por la CMF en Chile; ESRS o VSME si quien "
               "pregunta es un cliente europeo. Se puede reportar con mas de un marco: comparten datos.")


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _texto(opciones, clave):
    valor = opciones.get(clave)
    if valor is None or valor is True:
        return None
    texto = str(valor).strip()
    return texto or None


def _contexto(opciones):
    raiz = _texto(opciones, "raiz")
    identificador = _texto(opciones, "empresa")
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _numero(valor):
    """Convierte a numero lo que escribio la persona: acepta 1.234,5 y 1234.5."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def _suma(filas, columna):
    total = 0.0
    hubo = False
    for fila in filas:
        valor = _numero(fila.get(columna))
        if valor is not None:
            total += valor
            hubo = True
    return total if hubo else None


def _cifra(valor, unidad=""):
    texto = informe.formatear_numero(valor)
    return ("%s %s" % (texto, unidad)).strip()


def _marco_pedido(opciones, perfil=None):
    """Toma el marco de la opcion --marco o, si no viene, del perfil de la empresa."""
    pedido = _texto(opciones, "marco")
    if pedido:
        return catalogo.resolver_marco(pedido)
    for candidato in (perfil or {}).get("marcos") or []:
        try:
            return catalogo.resolver_marco(candidato)
        except Problema:
            continue
    raise Problema(
        "No me dijiste con que marco de reporte quieres trabajar.",
        "Elige uno de estos y vuelve a intentarlo: %s. Por ejemplo: --marco GRI."
        % ", ".join(catalogo.nombres_de_marcos()),
    )


# --------------------------------------------------------------------------
# Que datos tiene la empresa hoy
# --------------------------------------------------------------------------

def _leer_json(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def _elegir_huella(ruta_empresa, periodo=None):
    """Devuelve la ruta del calculo de huella mas util, o None si todavia no hay."""
    carpeta = espacio.ruta_de(ruta_empresa, "resultados")
    candidatos = [os.path.join(carpeta, nombre) for nombre in sorted(os.listdir(carpeta))
                  if nombre.startswith("huella_") and nombre.endswith(".json")]
    if not candidatos:
        return None
    if periodo:
        preferido = os.path.join(carpeta, "huella_%s.json" % periodo)
        if preferido in candidatos:
            return preferido
    return max(candidatos, key=lambda ruta: os.path.getmtime(ruta))


def _datos_de_huella(ruta_empresa, periodo, claves, detalle, avisos):
    ruta = _elegir_huella(ruta_empresa, periodo)
    if not ruta:
        avisos.append("Todavia no hay una huella de carbono calculada: por eso quedan pendientes los contenidos "
                      "de emisiones. Se resuelve con: huella calcular.")
        return None
    try:
        resumen = _leer_json(ruta)
    except ValueError:
        avisos.append("El archivo %s esta dañado y no lo pude leer. Vuelve a ejecutar: huella calcular."
                      % os.path.basename(ruta))
        return None

    periodo_huella = resumen.get("periodo") or "el periodo calculado"
    por_alcance = resumen.get("por_alcance") or {}
    for clave, etiqueta in (("alcance_1", "Alcance 1 (lo que la empresa quema o fuga)"),
                            ("alcance_2", "Alcance 2 (energia comprada)"),
                            ("alcance_3", "Alcance 3 (cadena de valor)")):
        dato = por_alcance.get(clave) or {}
        if dato.get("kg_co2e") is not None:
            nombre = "huella.por_alcance.%s" % clave
            claves.add(nombre)
            detalle[nombre] = "%s: %s (periodo %s)." % (
                etiqueta, _cifra(dato["kg_co2e"] / 1000.0, "tCO2e"), periodo_huella)

    if resumen.get("total_t_co2e") is not None:
        claves.add("huella.total_t_co2e")
        detalle["huella.total_t_co2e"] = "Huella total: %s del periodo %s." % (
            _cifra(resumen["total_t_co2e"], "tCO2e"), periodo_huella)

    categorias = resumen.get("por_categoria_alcance3") or {}
    if categorias:
        claves.add("huella.por_categoria_alcance3")
        detalle["huella.por_categoria_alcance3"] = (
            "Alcance 3 calculado en %d categorias del GHG Protocol: %s." %
            (len(categorias), ", ".join(sorted(categorias, key=lambda c: str(c)))))

    sitios = resumen.get("por_sitio") or {}
    if sitios:
        claves.add("huella.por_sitio")
        detalle["huella.por_sitio"] = "Emisiones repartidas en %d sitios: %s." % (
            len(sitios), ", ".join(sorted(sitios)))

    periodos = [p for p in (resumen.get("por_periodo") or {}) if p and p != "sin periodo"]
    if len(periodos) > 1:
        claves.add("huella.por_periodo")
        detalle["huella.por_periodo"] = "Hay emisiones de %d periodos (%s), asi que se pueden comparar." % (
            len(periodos), ", ".join(sorted(periodos)))

    calidad = (resumen.get("calidad_datos") or {}).get("porcentaje") or {}
    if calidad:
        claves.add("huella.calidad_datos")
        detalle["huella.calidad_datos"] = "Calidad de los datos: %s%% verificado, %s%% reportado, %s%% estimado." % (
            informe.formatear_numero(calidad.get("verificado", 0)),
            informe.formatear_numero(calidad.get("reportado", 0)),
            informe.formatear_numero(calidad.get("estimado", 0)))

    if resumen.get("set_pcg"):
        claves.add("huella.set_pcg")
        detalle["huella.set_pcg"] = (
            "Metodologia: GHG Protocol Corporate Standard, con potenciales de calentamiento global %s. "
            "Alcance 2 calculado por ubicacion." % resumen["set_pcg"])
    return ruta


def _resumen_personas(ruta_archivo, periodo=None):
    tabla = excel.leer_tabla(ruta_archivo)
    filas = tabla["filas"]
    if periodo:
        del_periodo = [f for f in filas if str(f.get("periodo") or "").startswith(str(periodo))]
        filas = del_periodo or filas
    por_genero = {}
    for fila in filas:
        genero = str(fila.get("genero") or "sin declarar").strip().lower() or "sin declarar"
        cantidad = _numero(fila.get("numero_de_personas")) or 0
        por_genero[genero] = por_genero.get(genero, 0) + cantidad
    resumen = {
        "filas": len(filas),
        "personas": _suma(filas, "numero_de_personas"),
        "por_genero": por_genero,
        "contrataciones": _suma(filas, "contrataciones"),
        "desvinculaciones": _suma(filas, "desvinculaciones"),
        "horas_capacitacion": _suma(filas, "horas_de_capacitacion"),
        "accidentes": _suma(filas, "accidentes_con_tiempo_perdido"),
        "dias_perdidos": _suma(filas, "dias_perdidos"),
        "horas_trabajadas": _suma(filas, "horas_trabajadas"),
        "personas_con_discapacidad": _suma(filas, "personas_con_discapacidad"),
    }
    try:
        resumen["indicadores"] = social.calcular(filas, periodo)
    except Problema:
        resumen["indicadores"] = {}
    return resumen


def _plural(cantidad, singular, plural):
    """«1 accidente» y no «1 accidentes»: el reporte lo lee un cliente."""
    return "%s %s" % (informe.formatear_numero(cantidad), singular if cantidad == 1 else plural)


def _vinetas_de_personas(resumen):
    """Una viñeta por tema, para que cada seccion del reporte reciba lo suyo.

    Sin esto, la seccion de remuneraciones y la de accidentes reciben el mismo
    parrafo y el reporte parece armado sin leerlo.
    """
    indicadores = resumen.get("indicadores") or {}
    vinetas = {}

    if resumen["personas"]:
        reparto = ", ".join("%s %s" % (genero, informe.formatear_numero(valor))
                            for genero, valor in sorted(resumen["por_genero"].items()) if valor)
        vinetas["personas.dotacion"] = (
            "Dotacion: %s%s." % (_plural(resumen["personas"], "persona", "personas"),
                                 " (%s)" % reparto if reparto else ""))

    if resumen["contrataciones"] or resumen["desvinculaciones"]:
        texto = "Movimiento de personal: %s y %s" % (
            _plural(resumen["contrataciones"], "contratacion", "contrataciones"),
            _plural(resumen["desvinculaciones"], "desvinculacion", "desvinculaciones"))
        if indicadores.get("tasa_rotacion_pct") is not None:
            texto += " (rotacion %s%%)" % informe.formatear_numero(indicadores["tasa_rotacion_pct"])
        vinetas["personas.rotacion"] = texto + "."

    if resumen["accidentes"] or resumen["dias_perdidos"]:
        texto = "Seguridad y salud: %s y %s" % (
            _plural(resumen["accidentes"], "accidente con tiempo perdido",
                    "accidentes con tiempo perdido"),
            _plural(resumen["dias_perdidos"], "dia perdido", "dias perdidos"))
        if indicadores.get("tasa_accidentes_registrables") is not None:
            texto += " (%s accidentes por cada 200.000 horas trabajadas, GRI 403-9)" % \
                     informe.formatear_numero(indicadores["tasa_accidentes_registrables"])
        elif indicadores.get("tasa_accidentabilidad_pct") is not None:
            texto += " (accidentabilidad %s%% sobre la dotacion; faltan las horas trabajadas para la " \
                     "tasa por 200.000 horas que pide GRI 403-9)" % \
                     informe.formatear_numero(indicadores["tasa_accidentabilidad_pct"])
        vinetas["personas.seguridad"] = texto + "."

    brechas = indicadores.get("brecha_salarial_por_categoria") or {}
    if brechas:
        partes = ["%s: las mujeres ganan %s%% menos que los hombres (razon mujer/hombre %s)"
                  % (categoria, informe.formatear_numero(datos["brecha_pct"]),
                     informe.formatear_numero(datos["razon_mujer_hombre"]))
                  for categoria, datos in sorted(brechas.items())]
        vinetas["personas.remuneracion"] = "Brecha salarial por categoria: %s." % "; ".join(partes)
    else:
        vinetas["personas.remuneracion"] = (
            "Brecha salarial: no se puede calcular todavia. Falta la columna «Remuneracion promedio» "
            "en la planilla de personas, con hombres y mujeres de la misma categoria.")

    if resumen["horas_capacitacion"]:
        texto = "Capacitacion: %s de formacion" % _plural(resumen["horas_capacitacion"], "hora", "horas")
        if indicadores.get("horas_capacitacion_por_persona"):
            texto += " (%s por persona)" % informe.formatear_numero(
                indicadores["horas_capacitacion_por_persona"])
        vinetas["personas.formacion"] = texto + "."

    if resumen["personas_con_discapacidad"] or indicadores.get("mujeres_pct") is not None:
        partes = []
        if indicadores.get("mujeres_pct") is not None:
            partes.append("%s%% de mujeres en la dotacion" % informe.formatear_numero(indicadores["mujeres_pct"]))
        if indicadores.get("mujeres_en_direccion_pct") is not None:
            partes.append("%s%% de mujeres en cargos de direccion"
                          % informe.formatear_numero(indicadores["mujeres_en_direccion_pct"]))
        if resumen["personas_con_discapacidad"]:
            partes.append("%s con discapacidad"
                          % _plural(resumen["personas_con_discapacidad"], "persona", "personas"))
        if partes:
            vinetas["personas.diversidad"] = "Diversidad: %s." % "; ".join(partes)
    return vinetas


# Palabras del contenido del marco -> que viñeta de personas le corresponde.
# El orden es el orden en que aparecen en el documento.
TEMAS_DE_PERSONAS = (
    (("plantilla", "dotacion", "trabajador", "empleado", "tipo de contrato", "personal",
      "cuanta gente", "numero de personas"),
     "personas.dotacion"),
    (("accidente", "seguridad", "salud ocupacional", "salud y seguridad", "lesion", "siniestr",
      "fatalidad"),
     "personas.seguridad"),
    (("remunerac", "salari", "sueldo", "brecha", "negociacion colectiva", "sindic"),
     "personas.remuneracion"),
    (("formacion", "capacitacion", "desarrollo de competencias", "entrenamiento"),
     "personas.formacion"),
    (("rotacion", "contratacion", "nuevas contrataciones", "desvinculac", "movimiento"),
     "personas.rotacion"),
    (("diversidad", "inclusion", "discapacidad", "igualdad de oportunidades",
      "distribucion por genero", "por genero"),
     "personas.diversidad"),
)


def _vineta_para(clave, ficha, detalle):
    """Elige la viñeta que de verdad responde lo que pide esa seccion del marco."""
    if clave != "personas.xlsx":
        return detalle.get(clave, clave)
    texto = _clave_busqueda(ficha)
    elegidas = [nombre for palabras, nombre in TEMAS_DE_PERSONAS
                if any(palabra in texto for palabra in palabras) and nombre in detalle]
    if elegidas:
        return " ".join(detalle[nombre] for nombre in elegidas)
    return detalle.get("personas.dotacion") or detalle.get(clave, clave)


def _clave_busqueda(ficha):
    return ("%s %s" % (ficha.get("titulo", ""), ficha.get("descripcion", ""))).lower()


def _filas_del_periodo(filas, periodo):
    """Solo las filas del periodo del reporte, para no contar de mas."""
    if not periodo:
        return filas, 0
    del_periodo = [f for f in filas if str(f.get("periodo") or "").startswith(str(periodo))]
    if not del_periodo:
        return filas, 0
    return del_periodo, len(filas) - len(del_periodo)


def _datos_de_planillas(ruta_empresa, periodo, claves, detalle, avisos):
    descripciones = {
        "sitios.xlsx": ("Planilla de sitios: %s.", "lugar registrado", "lugares registrados", False),
        "consumos.xlsx": ("Planilla de consumos: %s de energia y combustibles.",
                          "fila", "filas", True),
        "alcance3.xlsx": ("Planilla de cadena de valor: %s de compras, fletes, viajes o residuos.",
                          "fila", "filas", True),
    }
    for nombre, (plantilla, singular, plural, por_periodo) in descripciones.items():
        ruta = espacio.ruta_de(ruta_empresa, "datos", nombre)
        if not os.path.isfile(ruta):
            continue
        try:
            tabla = excel.leer_tabla(ruta)
        except Problema as problema:
            avisos.append("No pude leer %s: %s" % (nombre, problema.mensaje))
            continue
        claves.add(nombre)
        filas = tabla["filas"]
        fuera = 0
        if por_periodo:
            filas, fuera = _filas_del_periodo(filas, periodo)
        texto = plantilla % _plural(len(filas), singular, plural)
        if fuera:
            texto = texto[:-1] + " del periodo %s (la planilla tiene %s mas de otros periodos)." % (
                periodo, informe.formatear_numero(fuera))
        detalle[nombre] = texto

    ruta_personas = espacio.ruta_de(ruta_empresa, "datos", "personas.xlsx")
    if os.path.isfile(ruta_personas):
        try:
            resumen = _resumen_personas(ruta_personas, periodo)
        except Problema as problema:
            avisos.append("No pude leer personas.xlsx: %s" % problema.mensaje)
            return
        claves.add("personas.xlsx")
        vinetas = _vinetas_de_personas(resumen)
        detalle.update(vinetas)
        detalle["personas.xlsx"] = vinetas.get("personas.dotacion") or (
            "Planilla de personas: %s cargada%s." % (_plural(resumen["filas"], "fila", "filas"),
                                                     "" if resumen["filas"] == 1 else "s"))


def datos_disponibles(perfil, ruta_empresa, periodo=None):
    """Revisa la carpeta de la empresa y devuelve (claves, detalle, avisos, huella_usada)."""
    claves = set()
    detalle = {}
    avisos = []

    claves.add("empresa.json")
    detalle["empresa.json"] = "Ficha de la empresa: %s, sector %s, pais %s, periodo %s." % (
        perfil.get("nombre", ""), perfil.get("sector") or "sin indicar",
        espacio.PAISES.get(perfil.get("pais", ""), perfil.get("pais", "")),
        perfil.get("periodo_actual", ""))

    huella = _datos_de_huella(ruta_empresa, periodo, claves, detalle, avisos)
    _datos_de_planillas(ruta_empresa, periodo, claves, detalle, avisos)

    ruta_diagnostico = espacio.ruta_de(ruta_empresa, "seguimiento", "diagnostico.json")
    if os.path.isfile(ruta_diagnostico):
        try:
            guardado = _leer_json(ruta_diagnostico)
        except ValueError:
            guardado = {}
            avisos.append("El archivo de seguimiento del diagnostico esta dañado; lo ignore para este reporte.")
        evaluacion = guardado.get("ultima_evaluacion") or {}
        if evaluacion:
            claves.add("diagnostico")
            puntajes = evaluacion.get("puntajes") or {}
            brechas = len(evaluacion.get("brechas") or [])
            detalle["diagnostico"] = (
                "Diagnostico ESG: puntaje general %s de 100 (ambiental %s, social %s, gobernanza %s), "
                "con %d %s identificada%s." % (
                    informe.formatear_numero(evaluacion.get("puntaje_general")),
                    informe.formatear_numero(puntajes.get("ambiental")),
                    informe.formatear_numero(puntajes.get("social")),
                    informe.formatear_numero(puntajes.get("gobernanza")),
                    brechas, "brecha" if brechas == 1 else "brechas", "" if brechas == 1 else "s"))
        else:
            avisos.append("Hay un diagnostico iniciado pero sin evaluacion guardada. Ejecuta: diagnostico evaluar.")

    ruta_metas = espacio.ruta_de(ruta_empresa, "seguimiento", "metas.json")
    if os.path.isfile(ruta_metas):
        claves.add("metas")
        detalle["metas"] = "Hay metas registradas en seguimiento/metas.json."

    return claves, detalle, avisos, huella


# --------------------------------------------------------------------------
# Acciones
# --------------------------------------------------------------------------

def marcos(opciones):
    """Lista los marcos de reporte y que exige cada uno."""
    pedido = _texto(opciones, "marco")
    if pedido:
        nombre = catalogo.resolver_marco(pedido)
        contenidos = catalogo.contenidos_de(nombre)
        guia = catalogo.GUIA_MARCOS.get(nombre, {})
        return {
            "marco": nombre,
            "nombre_largo": guia.get("nombre_largo", nombre),
            "para_quien": guia.get("para_quien", ""),
            "cuando_usarlo": guia.get("cuando_usarlo", ""),
            "que_mira": guia.get("mira", ""),
            "obligatorio_en": guia.get("obligatorio_en", ""),
            "ojo_con": guia.get("ojo_con", ""),
            "total_contenidos": len(contenidos),
            "contenidos": [{
                "codigo": c["codigo"],
                "titulo": c["titulo"],
                "dimension": catalogo.DIMENSIONES.get(c["dimension"], c["dimension"]),
                "cuando_se_reporta": catalogo.OBLIGATORIEDAD.get(c["obligatorio"], c["obligatorio"]),
                "que_pide": c["descripcion"],
                "de_donde_sale": [catalogo.DATOS_CONOCIDOS.get(d, d) for d in c["dato_fuente"]]
                                 or ["Lo escribe la empresa"],
                "notas": c["notas"],
                "fuente": c["fuente"],
                "url": c["url"],
                "verificado_el": c["verificado_el"],
            } for c in contenidos],
            "mensaje": "Para ver que puede reportar la empresa hoy: reporte cobertura --marco %s." % nombre,
        }

    disponibles = catalogo.marcos_disponibles()
    return {
        "marcos": disponibles,
        "como_elegir": COMO_ELEGIR,
        "mensaje": "Pide el detalle de uno con: reporte marcos --marco GRI. "
                   "Para ver que puede reportar la empresa: reporte cobertura --marco GRI.",
        "recordatorio": AVISO,
    }


def cobertura(opciones):
    """Revisa que contenidos del marco puede reportar la empresa hoy y cuales faltan."""
    perfil, ruta_empresa = _contexto(opciones)
    marco = _marco_pedido(opciones, perfil)
    periodo = _texto(opciones, "periodo")
    claves, detalle, avisos, huella = datos_disponibles(perfil, ruta_empresa, periodo)
    resultado = catalogo.evaluar_cobertura(marco, claves)

    def resumir(fichas, limite=12):
        return [{"codigo": f["codigo"], "titulo": f["titulo"], "que_hacer": f["motivo"]}
                for f in fichas[:limite]]

    liviano = {
        "empresa": perfil.get("nombre"),
        "marco": resultado["marco"],
        "periodo": periodo or perfil.get("periodo_actual"),
        "porcentaje_cobertura": resultado["porcentaje_cobertura"],
        "porcentaje_de_lo_que_se_reporta_siempre": resultado["porcentaje_de_lo_que_se_reporta_siempre"],
        "total_contenidos": resultado["total"],
        "cubiertos": len(resultado["cubiertos"]),
        "parciales": len(resultado["parciales"]),
        "pendientes": len(resultado["pendientes"]),
        "pendientes_por_falta_de_datos": resultado["por_falta_de_datos"],
        "pendientes_por_redactar": resultado["por_redactar"],
        "ya_puedes_reportar": resumir(resultado["cubiertos"]),
        "te_falta": resumir(resultado["parciales"] + [f for f in resultado["pendientes"] if not f["se_redacta"]]),
        "datos_que_mas_suman": resultado["datos_que_mas_suman"],
        "datos_encontrados": sorted(detalle.values()),
        "huella_usada": os.path.basename(huella) if huella else None,
        "siguiente_paso": "Genera el borrador con: reporte borrador --marco %s. El indice de contenidos sale "
                          "con: reporte indice --marco %s." % (resultado["marco"], resultado["marco"]),
    }
    return Respuesta(liviano, advertencias=[AVISO] + avisos)


def _seleccionar(resultado, opciones):
    """Filtra los contenidos del marco con --temas y --solo-obligatorios."""
    fichas = resultado["contenidos"]
    temas = _texto(opciones, "temas")
    if temas:
        prefijos = [t.strip().lower() for t in temas.replace(";", ",").split(",") if t.strip()]
        elegidas = [f for f in fichas if any(f["codigo"].lower().startswith(p) for p in prefijos)]
        if not elegidas:
            raise Problema(
                "Ningun contenido de %s empieza por %s." % (resultado["marco"], ", ".join(prefijos)),
                "Mira los codigos disponibles con: reporte marcos --marco %s." % resultado["marco"],
            )
        fichas = elegidas
    if opciones.get("solo_obligatorios"):
        elegidas = [f for f in fichas if f["obligatorio"] == "si"]
        if not elegidas:
            raise Problema(
                "En %s no hay contenidos marcados como «se reportan siempre» con ese filtro." % resultado["marco"],
                "Quita --solo-obligatorios para ver todos los contenidos del marco.",
            )
        fichas = elegidas
    return fichas


def _faltantes(ficha):
    return ", ".join(catalogo.DATOS_CONOCIDOS.get(dato, dato) for dato in ficha["faltan"])


def _instruccion(ficha):
    """Que tiene que hacer la persona en esta seccion del borrador."""
    if ficha["estado"] == "cubierto":
        return "[Revisa la cifra, explica de donde sale y agrega el contexto del periodo.]"
    if ficha["estado"] == "parcial":
        return "[Escribe el texto con lo que ya tienes y completa lo que falta: %s]" % _faltantes(ficha)
    if ficha["se_redacta"]:
        return "[Escribe aqui la respuesta de la empresa. Si el tema no aplica, dilo y explica por que.]"
    return "[Todavia no tienes este dato. Para llenarlo necesitas: %s]" % _faltantes(ficha)


def _datos_que_mas_suman(fichas):
    """Que dato conviene conseguir primero: el que desbloquea mas contenidos."""
    faltantes = {}
    for ficha in fichas:
        for dato in ficha["faltan"]:
            faltantes[dato] = faltantes.get(dato, 0) + 1
    return sorted(
        ({"dato": dato, "nombre": catalogo.DATOS_CONOCIDOS.get(dato, dato),
          "contenidos_que_desbloquea": veces} for dato, veces in faltantes.items()),
        key=lambda x: (-x["contenidos_que_desbloquea"], x["dato"]))[:8]


def _bloques_borrador(perfil, marco, periodo, fichas, detalle):
    hoy = datetime.date.today().strftime("%d-%m-%Y")
    bloques = [
        {"tipo": "titulo", "texto": "Borrador de reporte de sostenibilidad", "nivel": 0},
        {"tipo": "texto", "texto": "%s\nMarco: %s\nPeriodo: %s\nBorrador generado el %s" % (
            perfil.get("nombre", ""), marco, periodo, hoy), "negrita": True},
        {"tipo": "nota", "texto": AVISO},
    ]
    bloques.extend(word.desde_markdown(
        "## Como usar este borrador\n"
        "- Lo que aparece entre corchetes lo tiene que escribir la empresa: son los textos que ningun calculo "
        "puede inventar.\n"
        "- Las cifras que ya estan vienen de los datos de esta carpeta. Revisalas y explica de donde salen.\n"
        "- Borra las secciones que no correspondan a la empresa, pero deja dicho por que no corresponden.\n"
        "- Cuando termines, guarda el documento y respalda cada cifra con su evidencia.\n"
    ))
    bloques.append({"tipo": "salto_pagina"})

    for grupo in catalogo.agrupar_por_dimension(fichas):
        bloques.append({"tipo": "titulo", "texto": grupo["titulo"], "nivel": 1})
        for ficha in grupo["contenidos"]:
            bloques.append({"tipo": "titulo", "texto": "%s - %s" % (ficha["codigo"], ficha["titulo"]),
                            "nivel": 2})
            bloques.append({"tipo": "texto", "texto": "Que pide: %s" % ficha["descripcion"]})
            if ficha["encontrados"]:
                bloques.append({"tipo": "texto", "texto": "Con los datos de tu carpeta:", "negrita": True})
                bloques.append({"tipo": "lista",
                                "items": [_vineta_para(clave, ficha, detalle)
                                          for clave in ficha["encontrados"]]})
            bloques.append({"tipo": "texto", "texto": _instruccion(ficha)})
            if ficha["notas"]:
                bloques.append({"tipo": "nota", "texto": ficha["notas"]})

    bloques.append({"tipo": "salto_pagina"})
    faltan = [f for f in fichas if f["estado"] != "cubierto"]
    bloques.append({"tipo": "titulo", "texto": "Que falta para cerrar este borrador", "nivel": 1})
    if faltan:
        bloques.append({"tipo": "tabla", "columnas": ["Contenido", "Estado", "Que hacer"],
                        "filas": [["%s - %s" % (f["codigo"], f["titulo"]), f["estado"].capitalize(), f["motivo"]]
                                  for f in faltan]})
    else:
        bloques.append({"tipo": "texto",
                        "texto": "Todos los contenidos incluidos tienen su dato disponible. Falta redactarlos y "
                                 "revisarlos."})

    bloques.append({"tipo": "titulo", "texto": "Antes de publicar: revisa que no haya greenwashing", "nivel": 1})
    bloques.append({"tipo": "texto",
                    "texto": "Decir de mas es hoy un riesgo legal, no solo de reputacion. Revisa estos puntos "
                             "antes de que el texto salga de la empresa:"})
    bloques.append({"tipo": "lista", "items": AVISO_GREENWASHING})

    bloques.append({"tipo": "titulo", "texto": "De donde viene cada exigencia", "nivel": 1})
    fuentes = []
    for ficha in fichas:
        clave = (ficha["fuente"], ficha["url"], ficha["verificado_el"])
        if ficha["fuente"] and clave not in fuentes:
            fuentes.append(clave)
    bloques.append({"tipo": "tabla", "columnas": ["Fuente oficial", "Enlace", "Revisado el"],
                    "filas": [[nombre, url, fecha] for nombre, url, fecha in fuentes]})
    bloques.append({"tipo": "nota",
                    "texto": "Cobertura con los datos actuales: %s%% de los %d contenidos de %s incluidos en "
                             "este borrador. %s"
                             % (informe.formatear_numero(catalogo.porcentaje_cubierto(fichas)),
                                len(fichas), marco, AVISO)})
    return bloques


def borrador(opciones):
    """Genera en Word un borrador del reporte con las secciones del marco elegido."""
    perfil, ruta_empresa = _contexto(opciones)
    marco = _marco_pedido(opciones, perfil)
    periodo = _texto(opciones, "periodo") or str(perfil.get("periodo_actual") or "")
    claves, detalle, avisos, huella = datos_disponibles(perfil, ruta_empresa, periodo)
    resultado = catalogo.evaluar_cobertura(marco, claves)
    fichas = _seleccionar(resultado, opciones)

    destino = espacio.ruta_de(ruta_empresa, "reportes", "borrador-%s-%s.docx" % (
        espacio.texto_a_slug(marco), espacio.texto_a_slug(periodo or "sin-periodo")))
    word.escribir_docx(destino,
                       _bloques_borrador(perfil, marco, periodo or "sin indicar", fichas, detalle),
                       titulo="Borrador de reporte %s - %s" % (marco, perfil.get("nombre", "")))

    if len(fichas) > 40:
        avisos.append("El borrador quedo largo (%d secciones). Si quieres uno mas corto, pide solo los temas "
                      "materiales con --temas 302,305,403 o solo lo obligatorio con --solo-obligatorios."
                      % len(fichas))
    return Respuesta({
        "mensaje": "Borrador listo: abrelo en Word, completa lo que esta entre corchetes y revisalo antes de "
                   "compartirlo.",
        "archivo": destino,
        "empresa": perfil.get("nombre"),
        "marco": marco,
        "periodo": periodo or "sin indicar",
        "secciones_incluidas": len(fichas),
        "con_dato_listo": len([f for f in fichas if f["estado"] == "cubierto"]),
        "a_medias": len([f for f in fichas if f["estado"] == "parcial"]),
        "por_completar": len([f for f in fichas if f["estado"] == "pendiente"]),
        "porcentaje_cobertura": catalogo.porcentaje_cubierto(fichas),
        "porcentaje_del_marco_completo": resultado["porcentaje_cobertura"],
        "huella_usada": os.path.basename(huella) if huella else None,
    }, advertencias=[AVISO] + avisos)


_COLORES_ESTADO = {"cubierto": "verde", "parcial": "amarillo", "pendiente": "rojo"}
_PALABRA_ESTADO = {"cubierto": "Cubierto", "parcial": "Parcial", "pendiente": "Pendiente"}


def _bloques_indice(perfil, marco, fichas, detalle):
    conteo = {estado: len([f for f in fichas if f["estado"] == estado]) for estado in catalogo.ESTADOS}
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Cobertura", "valor": catalogo.porcentaje_cubierto(fichas), "unidad": "%",
             "detalle": "Con los datos que hay hoy en la carpeta", "color": "verde"},
            {"etiqueta": "Cubiertos", "valor": conteo["cubierto"], "detalle": "El dato ya existe"},
            {"etiqueta": "Parciales", "valor": conteo["parcial"], "detalle": "Falta una parte del dato"},
            {"etiqueta": "Pendientes", "valor": conteo["pendiente"], "detalle": "Falta el dato o falta escribirlo"},
        ]},
        {"tipo": "texto",
         "texto": "Este es el indice de contenidos de %s para %s. «Cubierto» significa que el dato ya esta en la "
                  "carpeta y solo falta redactarlo; «parcial», que falta una parte; «pendiente», que falta el dato "
                  "o que es un texto que debe escribir la empresa." % (marco, perfil.get("nombre", ""))},
        {"tipo": "dona", "titulo": "Estado de los contenidos", "unidad": "contenidos",
         "datos": [{"etiqueta": _PALABRA_ESTADO[estado], "valor": conteo[estado]} for estado in catalogo.ESTADOS]},
    ]
    for grupo in catalogo.agrupar_por_dimension(fichas):
        bloques.append({"tipo": "titulo", "texto": grupo["titulo"], "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Codigo", "Contenido", "Estado", "De donde sale o que falta"],
                        "filas": [[f["codigo"], f["titulo"], _PALABRA_ESTADO[f["estado"]],
                                   "; ".join(_vineta_para(c, f, detalle) for c in f["encontrados"])
                                   or f["motivo"]]
                                  for f in grupo["contenidos"]]})
    faltan = _datos_que_mas_suman(fichas)
    if faltan:
        bloques.append({"tipo": "titulo", "texto": "Que conviene cargar primero", "nivel": 2})
        bloques.append({"tipo": "barras", "titulo": "", "unidad": "contenidos que se desbloquean",
                        "datos": [{"etiqueta": dato["nombre"], "valor": dato["contenidos_que_desbloquea"]}
                                  for dato in faltan]})
    bloques.append({"tipo": "nota", "estilo": "aviso", "texto": AVISO})
    return bloques


def indice(opciones):
    """Genera en HTML el indice de contenidos del marco, con el estado de cada contenido."""
    perfil, ruta_empresa = _contexto(opciones)
    marco = _marco_pedido(opciones, perfil)
    periodo = _texto(opciones, "periodo")
    claves, detalle, avisos, _huella = datos_disponibles(perfil, ruta_empresa, periodo)
    resultado = catalogo.evaluar_cobertura(marco, claves)
    fichas = _seleccionar(resultado, opciones)

    destino = espacio.ruta_de(ruta_empresa, "reportes",
                              "indice-%s.html" % espacio.texto_a_slug(marco))
    informe.escribir_html(
        destino,
        "Indice de contenidos %s" % marco,
        _bloques_indice(perfil, marco, fichas, detalle),
        marca=perfil.get("marca") or {},
        subtitulo="%s - %s de %d contenidos con dato disponible" % (
            perfil.get("nombre", ""), len([f for f in fichas if f["estado"] == "cubierto"]), len(fichas)))
    return Respuesta({
        "mensaje": "Indice listo: abrelo con doble clic y, si lo necesitas en PDF, imprimelo desde el navegador.",
        "archivo": destino,
        "marco": marco,
        "contenidos": len(fichas),
        "cubiertos": len([f for f in fichas if f["estado"] == "cubierto"]),
        "parciales": len([f for f in fichas if f["estado"] == "parcial"]),
        "pendientes": len([f for f in fichas if f["estado"] == "pendiente"]),
        "porcentaje_cobertura": catalogo.porcentaje_cubierto(fichas),
        "porcentaje_del_marco_completo": resultado["porcentaje_cobertura"],
        "que_conviene_cargar_primero": _datos_que_mas_suman(fichas),
    }, advertencias=[AVISO] + avisos)


ACCIONES = {"marcos": marcos, "cobertura": cobertura, "borrador": borrador, "indice": indice}
