# -*- coding: utf-8 -*-
"""Activos fijos: vida util del SII, depreciacion y correccion monetaria (Chile).

Depreciar es repartir lo que costo un bien a lo largo de los anios en que se usa,
en vez de anotarlo todo como gasto el anio de la compra.

De donde sale cada regla (investigacion normativa en
docs/investigacion/09-finanzas-logistica-frio.md, seccion SII):

  VIDA UTIL
    Resolucion Exenta SII N 43 de 26.12.2002, vigente desde el 01.01.2003,
    con la modificacion de la Res. Ex. SII N 56 de 09.06.2021 (vehiculos
    electricos, hibridos enchufables y cero emisiones: 3 anios normal, 1
    acelerada). Instrucciones en la Circular SII N 6 de 14.01.2003.
    Ambito: bienes adquiridos nuevos, construidos o internados desde la
    publicacion de la Ley N 19.840 (23.11.2002).

  DEPRECIACION NORMAL - art. 31 N 5, inciso primero, de la Ley de la Renta

      cuota_anual = (valor - valor_residual) / vida_util_normal

    Se cuenta desde que el bien SE USA en la empresa, no desde la compra. En el
    primer ejercicio se computa por los meses efectivos de uso al 31 de diciembre:

      cuota_primer_ejercicio = cuota_anual x meses_de_uso / 12

    La base es el valor actualizado por correccion monetaria (art. 41), neto de
    depreciaciones acumuladas. No se deprecian los terrenos, los intangibles ni
    el activo realizable (mercaderias, materias primas, productos en proceso).

  DEPRECIACION ACELERADA - art. 31 N 5 de la Ley de la Renta

      vida_util_acelerada = max(1, parte entera de (vida_util_normal / 3))

    Solo para bienes nuevos adquiridos o importados (los importados pueden ser
    usados) y solo si la vida util normal es de 3 anios o mas. Para los registros
    empresariales del art. 14 solo se considera la depreciacion normal: la
    diferencia entre acelerada y normal se controla por separado.

  ART. 31 N 5 BIS - empresas medianas y pequenas (desde el 01.10.2014)
    Ingresos promedio del giro de los 3 ejercicios anteriores:
      hasta 25.000 UF            -> vida util 1 anio, bienes nuevos o usados
      sobre 25.000 y hasta 100.000 UF -> max(1, parte entera de normal/10),
                                         bienes nuevos o importados
    Es opcional: la empresa elige entre el N 5 y el N 5 bis.

  PRO PYME - art. 14 letra D) N 3 de la Ley de la Renta
    Depreciacion instantanea e integra (100 %) en el mismo ejercicio en que el
    bien se adquiere o fabrica, siempre que este efectivamente pagado (el
    regimen trabaja con flujos de caja). Estas empresas NO aplican correccion
    monetaria.

  CORRECCION MONETARIA - art. 41 de la Ley de la Renta
    Bienes que ya estaban al inicio del ejercicio: se actualizan con el mismo
    porcentaje del capital propio inicial (variacion del IPC desde el ultimo dia
    del segundo mes anterior al inicio del ejercicio hasta el ultimo dia del mes
    anterior al balance; en un ano calendario, 30.11 del ano anterior a 30.11 del
    ano del balance).
    Bienes comprados durante el ejercicio: variacion del IPC desde el ultimo dia
    del mes anterior a la compra hasta el ultimo dia del mes anterior al balance.
    Si el porcentaje resulta negativo, se iguala a cero.
    Primero se actualiza el valor neto del bien y sobre ese valor actualizado se
    calcula la cuota de depreciacion del ejercicio.

Lo que este modulo NO hace, porque la investigacion no lo dejo verificado, y que
avisa en vez de inventar:

  - Las nominas del SII por actividad distintas de la agricola (construccion,
    mineria, transporte, energia electrica, telecomunicaciones) quedaron con
    lectura parcial: no estan cargadas.
  - Algunos items de detalle de la nomina generica no se pudieron leer completos.
  - La vida util de los vinedos depende de la variedad (entre 11 y 23 anios): la
    tabla la trae sin numero y el motor pide confirmarla.
  - El valor residual de $1 esta verificado para el caso de la Ley 21.256; como
    regla general quedo como fuente secundaria. Se usa por defecto y se avisa.
  - El credito por activo fijo del art. 33 bis no se calcula aqui.
  - La vida util especial que puede autorizar el Director Regional quedo como
    fuente secundaria: no se aplica sola.
"""

import csv
import datetime
import os
import re
import unicodedata

from nucleo.salida import Problema

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datos")
ARCHIVO_VIDA_UTIL = os.path.join(CARPETA_DATOS, "vida_util_sii.csv")

# Valor al que queda el bien totalmente depreciado (un peso).
VALOR_RESIDUAL_TRIBUTARIO = 1.0
AVISO_VALOR_RESIDUAL = (
    "El bien totalmente depreciado queda en $1 hasta que se venda o se de de baja. La Ley 21.256 lo dijo "
    "expresamente para su propio regimen; como regla general es practica establecida pero no quedo "
    "verificada en la investigacion: confirmala con tu contador.")

# Tramos de ingresos del art. 31 N 5 bis, en UF.
TOPE_UF_VIDA_UTIL_UN_ANIO = 25000.0
TOPE_UF_CINCO_BIS = 100000.0

ARTICULO_NORMAL = "art. 31 N 5, inciso primero, de la Ley de la Renta"
ARTICULO_ACELERADA = "art. 31 N 5 de la Ley de la Renta"
ARTICULO_CINCO_BIS = "art. 31 N 5 bis de la Ley de la Renta"
ARTICULO_PROPYME = "art. 14 letra D) N 3 de la Ley de la Renta (Circular SII N 62 de 2020)"
ARTICULO_CORRECCION = "art. 41 de la Ley de la Renta"

FUENTE_VIDA_UTIL = ("Res. Ex. SII N 43 de 26.12.2002 (Circular SII N 6 de 14.01.2003), con la "
                    "modificacion de la Res. Ex. SII N 56 de 09.06.2021")
FUENTE_CORRECCION = "Circular SII N 5 de 21.01.2026 (arts. 41, 52 y 52 bis de la Ley de la Renta)"

# Reajuste del capital propio inicial, por ejercicio comercial (porcentaje).
# Se usa tambien para los bienes del activo inmovilizado existentes al inicio.
REAJUSTE_CAPITAL_PROPIO = {2025: 3.4}

# Factores de actualizacion directos para bienes adquiridos durante el ejercicio,
# por mes de adquisicion. Verificados para el ejercicio 2025.
FACTORES_MENSUALES = {
    2025: {1: 1.036, 2: 1.026, 3: 1.022, 4: 1.016, 5: 1.014, 6: 1.012,
           7: 1.017, 8: 1.008, 9: 1.007, 10: 1.003, 11: 1.003, 12: 1.000},
}

# Porcentajes de actualizacion para termino de giro, ano 2026 (el SII los publica
# mes a mes; de septiembre en adelante no estaban publicados al 16.09.2026).
PORCENTAJES_TERMINO_GIRO = {
    2026: {1: 0.4, 2: 0.0, 3: 1.0, 4: 1.3, 5: 0.2, 6: 0.0, 7: 0.1, 8: 0.6},
}

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

METODOS = ("normal", "acelerada", "5_bis", "propyme")

# Nominas del SII que existen pero que la investigacion dejo con lectura parcial.
NOMINAS_PENDIENTES = [
    "industria de la construccion", "mineria", "transporte maritimo", "transporte terrestre",
    "energia electrica", "telecomunicaciones",
]
AVISO_NOMINAS = (
    "La tabla del SII tiene ademas nominas por actividad (%s) y algunos items de detalle de la nomina "
    "generica que la investigacion no alcanzo a leer completos: no estan cargados. Si tu bien es de esos "
    "rubros, pidele el dato a tu contador o revisalo en la tabla publicada por el SII."
    % ", ".join(NOMINAS_PENDIENTES))

PALABRAS_VACIAS = {"de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o",
                   "para", "por", "con", "en", "mi", "su", "que", "al", "a", "the"}

# Como le dice la gente a cada bien -> codigos de la tabla del SII.
# Solo son atajos de busqueda: la respuesta siempre muestra el texto oficial del
# bien, su codigo y su fuente, para que la persona pueda revisarlo.
ALIAS = {
    "camioneta": ["sii-gen-10"],
    "pick up": ["sii-gen-10"],
    "pickup": ["sii-gen-10"],
    "jeep": ["sii-gen-10"],
    "suv": ["sii-gen-10"],
    "auto": ["sii-gen-11"],
    "vehiculo liviano": ["sii-gen-11"],
    "camion": ["sii-gen-09"],
    "furgon": ["sii-gen-12"],
    "van": ["sii-gen-12"],
    "minibus": ["sii-gen-12"],
    "moto": ["sii-gen-13"],
    "motocicleta": ["sii-gen-13"],
    "acoplado": ["sii-gen-14"],
    "computador": ["sii-gen-23"],
    "computadora": ["sii-gen-23"],
    "notebook": ["sii-gen-23"],
    "laptop": ["sii-gen-23"],
    "pc": ["sii-gen-23"],
    "servidor": ["sii-gen-23"],
    "impresora": ["sii-gen-23"],
    "galpon": ["sii-gen-05"],
    "bodega": ["sii-gen-05", "sii-gen-02", "sii-gen-03", "sii-gen-01"],
    "escritorio": ["sii-gen-22"],
    "silla": ["sii-gen-22"],
    "mueble": ["sii-gen-22"],
    "estanteria": ["sii-gen-22"],
    "aire acondicionado": ["sii-gen-17"],
    "camara de frio": ["sii-gen-17"],
    "camara frigorifica": ["sii-gen-17"],
    "climatizacion": ["sii-gen-17"],
    "refrigerador": ["sii-gen-16"],
    "congelador": ["sii-gen-16"],
    "freezer": ["sii-gen-16"],
    "vitrina": ["sii-gen-16"],
    "balanza": ["sii-gen-16"],
    "maquina": ["sii-gen-15"],
    "maquinaria": ["sii-gen-15"],
    "herramienta": ["sii-gen-18", "sii-gen-19"],
    "estanque": ["sii-gen-24"],
    "alarma": ["sii-gen-26"],
    "extintor": ["sii-gen-26"],
    "camara de seguridad": ["sii-gen-26"],
    "camara de vigilancia": ["sii-gen-26"],
    "envase": ["sii-gen-27"],
    "proyector": ["sii-gen-28"],
    "television": ["sii-gen-28"],
    "vehiculo electrico": ["sii-gen-30"],
    "auto electrico": ["sii-gen-30"],
    "camioneta electrica": ["sii-gen-30", "sii-gen-10"],
    "hibrido": ["sii-gen-30"],
    "cero emisiones": ["sii-gen-31"],
    "tractor": ["sii-agr-01"],
    "vina": ["sii-agr-13"],
    "vinedo": ["sii-agr-13"],
    "parronal": ["sii-agr-13"],
    "vaca": ["sii-agr-23"],
    "gallina": ["sii-agr-24"],
}

ALIAS_ACTIVIDAD = {
    "generico": "generico", "general": "generico", "generica": "generico",
    "agricola": "agricola", "agricultura": "agricola", "agro": "agricola",
    "agropecuario": "agricola", "campo": "agricola", "fundo": "agricola",
}

# Bienes que no se deprecian, con el motivo. Todo verificado en la investigacion.
NO_DEPRECIABLES = [
    {
        "palabras": ["terreno", "sitio eriazo"],
        "titulo": "Los terrenos no se deprecian",
        "detalle": ("Un terreno no se desgasta ni se agota con el uso, y ademas no puede comprarse nuevo: "
                    "por eso queda fuera de la depreciacion. Si compraste un inmueble, hay que separar "
                    "cuanto vale el terreno y cuanto la construccion; solo la construccion se deprecia."),
        "fuente": "%s (ejemplos de la Circular SII N 31 de 2020)" % ARTICULO_NORMAL,
    },
    {
        "palabras": ["software", "marca comercial", "derecho de llave", "intangible", "programa computacional"],
        "titulo": "Los bienes intangibles no se deprecian",
        "detalle": ("La depreciacion del art. 31 N 5 es solo para bienes fisicos. Un software, una marca o un "
                    "derecho de llave no son bienes fisicos, asi que siguen otro tratamiento: preguntale a tu "
                    "contador. El computador donde corre el software si se deprecia."),
        "fuente": ARTICULO_NORMAL,
    },
    {
        "palabras": ["mercaderia", "materia prima", "producto en proceso", "existencia", "insumo"],
        "titulo": "Las mercaderias y materias primas no se deprecian",
        "detalle": ("Son activo realizable, es decir, cosas que la empresa va a vender o transformar, no bienes "
                    "que use por anios. Se valorizan de otra manera."),
        "fuente": ARTICULO_NORMAL,
    },
]


# --------------------------------------------------------------------------
# Utilidades de texto y de numeros
# --------------------------------------------------------------------------

def _falta(valor):
    """True si el dato no viene.

    Ojo: en Python 1 == True, asi que la marca de opcion sin valor se compara por
    identidad; de lo contrario el mes 1 (enero) se leeria como dato faltante.
    """
    if valor is None or valor is True:
        return True
    return isinstance(valor, str) and not valor.strip()


def _clave(texto):
    """Deja el texto en minusculas, sin tildes y sin simbolos."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return texto.strip()


def _raiz(palabra):
    """Quita el plural mas comun para que 'camiones' y 'camion' se encuentren."""
    if len(palabra) >= 5 and palabra.endswith("es"):
        return palabra[:-2]
    if len(palabra) >= 4 and palabra.endswith("s"):
        return palabra[:-1]
    return palabra


def _firma(texto):
    """Texto normalizado, sin palabras vacias y con los plurales reducidos."""
    return " ".join(_raiz(p) for p in _clave(texto).split() if p not in PALABRAS_VACIAS)


_ALIAS_FIRMADO = {}
for _alias, _codigos in ALIAS.items():
    _ALIAS_FIRMADO.setdefault(_firma(_alias), []).extend(_codigos)


def _contiene(firma, buscada):
    """True si 'buscada' aparece como palabra (o grupo de palabras) dentro de 'firma'."""
    if not buscada:
        return False
    return (" %s " % buscada) in (" %s " % firma)


def numero(valor, nombre="el valor", detalle=""):
    """Lee un numero escrito como lo escribe la gente: 12.000.000 o 1.234,56."""
    if _falta(valor):
        raise Problema(
            "Falta %s." % nombre,
            "Escribe solo el numero, sin signo peso ni letras. Por ejemplo: 12000000.%s"
            % ((" " + detalle) if detalle else ""),
        )
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    texto = re.sub(r"[^0-9,.\-]", "", texto)
    if not texto or texto in ("-", ".", ","):
        raise Problema(
            "No entendi %s: «%s» no es un numero." % (nombre, valor),
            "Escribe solo el numero, sin signo peso ni letras. Por ejemplo: 12000000.",
        )
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    elif re.match(r"^-?\d{1,3}(\.\d{3})+$", texto):
        texto = texto.replace(".", "")
    try:
        return float(texto)
    except ValueError:
        raise Problema(
            "No entendi %s: «%s» no es un numero." % (nombre, valor),
            "Escribe solo el numero, sin signo peso ni letras. Por ejemplo: 12000000.",
        )


def entero(valor, nombre, sugerencia):
    convertido = numero(valor, nombre)
    if convertido != int(convertido):
        raise Problema("%s debe ser un numero entero y me llego %s." % (nombre.capitalize(), valor),
                       sugerencia)
    return int(convertido)


def _entero_o_nada(valor):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def _mes(valor, nombre="el mes"):
    """Acepta el numero del mes o su nombre."""
    if _falta(valor):
        return None
    if isinstance(valor, str):
        clave = _clave(valor)
        for indice, nombre_mes in enumerate(MESES, start=1):
            if clave == nombre_mes or (len(clave) >= 3 and nombre_mes.startswith(clave)):
                return indice
    convertido = entero(valor, nombre, "Usa el numero del mes (1 a 12) o su nombre, por ejemplo marzo.")
    if not 1 <= convertido <= 12:
        raise Problema("El mes %s no existe." % valor, "Usa un numero del 1 al 12 o el nombre del mes.")
    return convertido


def redondear(valor):
    return round(float(valor) + 0.0, 2)


# --------------------------------------------------------------------------
# Tabla de vida util del SII
# --------------------------------------------------------------------------

def cargar_tabla(ruta=None):
    """Lee la tabla de vida util de los bienes del activo inmovilizado."""
    ruta = ruta or ARCHIVO_VIDA_UTIL
    if not os.path.isfile(ruta):
        raise Problema(
            "No encuentro la tabla de vida util del SII (%s)." % os.path.basename(ruta),
            "Sin esa tabla no puedo decirte en cuantos anios se deprecia un bien. "
            "Avisale al asistente para reinstalar los datos del motor.",
        )
    bienes = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        for linea, fila in enumerate(csv.DictReader(archivo), start=2):
            texto_bien = (fila.get("bien") or "").strip()
            if not texto_bien:
                continue
            normal = _entero_o_nada(fila.get("vida_util_normal"))
            acelerada = _entero_o_nada(fila.get("vida_util_acelerada"))
            actividad = (fila.get("actividad") or "generico").strip().lower()
            bienes.append({
                "codigo": (fila.get("codigo") or "").strip(),
                "bien": texto_bien,
                "actividad": actividad,
                "vida_util_normal": normal,
                "vida_util_acelerada": acelerada,
                "resolucion": (fila.get("resolucion") or "").strip(),
                "fuente": (fila.get("fuente") or "").strip(),
                "verificado_el": (fila.get("verificado_el") or "").strip(),
                "notas": (fila.get("notas") or "").strip(),
                "requiere_confirmacion": normal is None,
                "_firma": _firma("%s %s" % (texto_bien, actividad)),
                "_linea": linea,
            })
    if not bienes:
        raise Problema(
            "La tabla de vida util del SII esta vacia.",
            "Avisale al asistente para reinstalar los datos del motor.",
        )
    return bienes


def _limpiar(bien):
    """Deja el bien listo para entregarlo en la respuesta, sin campos internos."""
    return {clave: valor for clave, valor in bien.items() if not clave.startswith("_")}


def normalizar_actividad(actividad):
    """Traduce como escribe la gente la actividad ('agro', 'campo') a la de la tabla."""
    if _falta(actividad):
        return None
    clave = _clave(actividad)
    if clave in ALIAS_ACTIVIDAD:
        return ALIAS_ACTIVIDAD[clave]
    raiz = _raiz(clave)
    for texto, destino in ALIAS_ACTIVIDAD.items():
        if _raiz(texto) == raiz:
            return destino
    raise Problema(
        "No tengo cargada la nomina de la actividad «%s»." % actividad,
        "Por ahora el motor trae la nomina generica y la agricola. %s" % AVISO_NOMINAS,
    )


def _revisar_no_depreciable(firma_consulta):
    for caso in NO_DEPRECIABLES:
        for palabra in caso["palabras"]:
            if _contiene(firma_consulta, _firma(palabra)):
                return {"titulo": caso["titulo"], "detalle": caso["detalle"], "fuente": caso["fuente"]}
    return None


def buscar_vida_util(descripcion, actividad=None, ruta=None, maximo=6):
    """Busca en la tabla del SII el bien descrito en lenguaje comun.

    Devuelve todas las opciones razonables para que la persona elija, con el
    codigo, los anios y la fuente de cada una. Si no encuentra ninguna, lo dice.
    """
    firma_consulta = _firma(descripcion)
    if not firma_consulta:
        raise Problema(
            "No me dijiste que bien quieres buscar.",
            "Escribelo como lo dirias normalmente: camioneta, computador, galpon, camara de frio.",
        )

    filtro = normalizar_actividad(actividad)
    no_depreciable = _revisar_no_depreciable(firma_consulta)
    if no_depreciable:
        return {
            "consulta": str(descripcion),
            "actividad": filtro,
            "encontrado": False,
            "se_deprecia": False,
            "no_se_deprecia": no_depreciable,
            "coincidencias": [],
            "eleccion_unica": None,
            "mensaje": "%s. %s" % (no_depreciable["titulo"], no_depreciable["detalle"]),
            "fuente": FUENTE_VIDA_UTIL,
            "advertencias": [],
        }

    tabla = cargar_tabla(ruta)
    codigos_alias = []
    for firma_alias, codigos in _ALIAS_FIRMADO.items():
        if _contiene(firma_consulta, firma_alias):
            codigos_alias.extend(codigos)

    palabras_consulta = [p for p in firma_consulta.split() if len(p) >= 3]
    resultados = []
    for bien in tabla:
        if filtro and bien["actividad"] != filtro:
            continue
        puntaje = 0
        if bien["codigo"] in codigos_alias:
            puntaje += 6
        palabras_bien = bien["_firma"].split()
        for palabra in palabras_consulta:
            if palabra in palabras_bien:
                puntaje += 3
            elif len(palabra) >= 4 and any(
                    p.startswith(palabra) or palabra.startswith(p)
                    for p in palabras_bien if len(p) >= 4):
                puntaje += 2
        if not puntaje:
            continue
        if not filtro and bien["actividad"] == "generico":
            puntaje += 1
        encontrado = _limpiar(bien)
        encontrado["puntaje"] = puntaje
        resultados.append(encontrado)

    resultados.sort(key=lambda b: (-b["puntaje"], b["codigo"]))
    coincidencias = resultados[:maximo]

    advertencias = []
    if any(c["requiere_confirmacion"] for c in coincidencias):
        advertencias.append(
            "Hay una opcion cuya vida util depende de la variedad o del caso: el motor no elige por ti. "
            "Confirma el numero exacto con tu contador.")
    if not filtro:
        advertencias.append(AVISO_NOMINAS)

    if not coincidencias:
        return {
            "consulta": str(descripcion),
            "actividad": filtro,
            "encontrado": False,
            "se_deprecia": None,
            "coincidencias": [],
            "eleccion_unica": None,
            "mensaje": ("No encontre «%s» en la tabla de vida util del SII que tengo cargada. No voy a "
                        "inventar un numero: dime con otras palabras de que bien se trata (por ejemplo "
                        "camioneta, computador, galpon, camara de frio) o preguntale a tu contador en que "
                        "item de la tabla del SII lo clasifica." % descripcion),
            "ejemplos": ["camioneta", "computador", "galpon", "camara de frio", "maquinaria", "tractor"],
            "fuente": FUENTE_VIDA_UTIL,
            "advertencias": advertencias,
        }

    unica = coincidencias[0] if len(coincidencias) == 1 else None
    if unica is None and len(coincidencias) > 1 and coincidencias[0]["puntaje"] > coincidencias[1]["puntaje"]:
        unica = coincidencias[0]

    if len(coincidencias) == 1:
        mensaje = "«%s» corresponde a: %s (%s anios de vida util normal)." % (
            descripcion, coincidencias[0]["bien"], coincidencias[0]["vida_util_normal"])
    else:
        mensaje = ("Para «%s» la tabla del SII tiene %d opciones. La mas parecida es «%s»; revisa la lista y "
                   "elige la que corresponde al bien de la empresa."
                   % (descripcion, len(coincidencias), coincidencias[0]["bien"]))

    return {
        "consulta": str(descripcion),
        "actividad": filtro,
        "encontrado": True,
        "se_deprecia": True,
        "coincidencias": coincidencias,
        "eleccion_unica": unica,
        "mensaje": mensaje,
        "fuente": FUENTE_VIDA_UTIL,
        "advertencias": advertencias,
    }


# --------------------------------------------------------------------------
# Vidas utiles tributarias
# --------------------------------------------------------------------------

def vida_util_acelerada(vida_util_normal):
    """Vida util acelerada del art. 31 N 5: max(1, parte entera de normal/3)."""
    normal = entero(vida_util_normal, "la vida util normal",
                     "Es el numero de anios que fija la tabla del SII, por ejemplo 7 para una camioneta.")
    if normal <= 0:
        raise Problema("La vida util normal debe ser de al menos un anio.",
                       "Revisa el numero de anios que trae la tabla del SII para ese bien.")
    if normal < 3:
        return {
            "aplica": False,
            "anios": None,
            "vida_util_normal": normal,
            "motivo": ("La depreciacion acelerada solo corre para bienes con vida util normal de 3 anios o "
                       "mas, y este tiene %d." % normal),
            "formula": "max(1, parte entera de %d / 3)" % normal,
            "articulo": ARTICULO_ACELERADA,
        }
    return {
        "aplica": True,
        "anios": max(1, normal // 3),
        "vida_util_normal": normal,
        "formula": "max(1, parte entera de %d / 3) = %d anios" % (normal, max(1, normal // 3)),
        "requisitos": [
            "El bien debe ser nuevo adquirido o importado (los importados pueden ser usados).",
            "La vida util normal debe ser de 3 anios o mas.",
            "Para los registros del art. 14 solo se considera la depreciacion normal: la diferencia entre "
            "acelerada y normal se controla aparte y queda afecta a los impuestos finales.",
        ],
        "articulo": ARTICULO_ACELERADA,
    }


def vida_util_5_bis(vida_util_normal, ingresos_uf):
    """Vida util del art. 31 N 5 bis segun el promedio de ingresos del giro, en UF."""
    normal = entero(vida_util_normal, "la vida util normal",
                     "Es el numero de anios que fija la tabla del SII para ese bien.")
    ingresos = numero(ingresos_uf, "el promedio de ingresos en UF",
                      "Es el promedio anual de ingresos del giro de los 3 ejercicios anteriores, en UF.")
    if ingresos <= TOPE_UF_VIDA_UTIL_UN_ANIO:
        return {
            "aplica": True, "anios": 1, "tramo": "hasta 25.000 UF",
            "vida_util_normal": normal, "ingresos_uf": ingresos,
            "bienes": "nuevos o usados",
            "formula": "vida util de 1 anio, cualquiera sea la vida util normal",
            "articulo": ARTICULO_CINCO_BIS,
        }
    if ingresos <= TOPE_UF_CINCO_BIS:
        return {
            "aplica": True, "anios": max(1, normal // 10), "tramo": "sobre 25.000 y hasta 100.000 UF",
            "vida_util_normal": normal, "ingresos_uf": ingresos,
            "bienes": "nuevos o importados",
            "formula": "max(1, parte entera de %d / 10) = %d anios" % (normal, max(1, normal // 10)),
            "articulo": ARTICULO_CINCO_BIS,
        }
    return {
        "aplica": False, "anios": None, "tramo": "sobre 100.000 UF",
        "vida_util_normal": normal, "ingresos_uf": ingresos,
        "motivo": ("El art. 31 N 5 bis es para empresas con ingresos promedio de hasta 100.000 UF; esta "
                   "declara %s UF." % ingresos),
        "articulo": ARTICULO_CINCO_BIS,
    }


def _resolver_vida_util(metodo, vida_util_normal, ingresos_uf, advertencias):
    """Devuelve (anios_a_usar, detalle_del_regimen) segun el metodo elegido."""
    if metodo == "propyme":
        return 1, {
            "regimen": "Pro Pyme: depreciacion instantanea e integra",
            "articulo": ARTICULO_PROPYME,
            "formula": "100 % del valor en el ejercicio de adquisicion o fabricacion",
        }
    normal = entero(vida_util_normal, "la vida util normal",
                     "Dime el bien con --bien para buscarlo en la tabla del SII, o los anios con --vida-util.")
    if normal <= 0:
        raise Problema("La vida util debe ser de al menos un anio.",
                       "Revisa los anios que fija la tabla del SII para ese bien.")
    if metodo == "normal":
        return normal, {
            "regimen": "Depreciacion normal (lineal)",
            "articulo": ARTICULO_NORMAL,
            "formula": "(valor - valor residual) / %d anios" % normal,
        }
    if metodo == "acelerada":
        acelerada = vida_util_acelerada(normal)
        if not acelerada["aplica"]:
            raise Problema(
                acelerada["motivo"],
                "Usa la depreciacion normal para este bien (--metodo normal).",
                {"vida_util_normal": normal, "articulo": ARTICULO_ACELERADA},
            )
        advertencias.append(
            "La depreciacion acelerada solo corre si el bien es nuevo adquirido o importado (los importados "
            "pueden ser usados). Si es usado comprado en Chile, corresponde la depreciacion normal.")
        return acelerada["anios"], {
            "regimen": "Depreciacion acelerada",
            "articulo": ARTICULO_ACELERADA,
            "formula": acelerada["formula"],
            "requisitos": acelerada["requisitos"],
        }
    cinco_bis = vida_util_5_bis(normal, ingresos_uf)
    if not cinco_bis["aplica"]:
        raise Problema(
            cinco_bis["motivo"],
            "Usa --metodo normal o --metodo acelerada.",
            {"articulo": ARTICULO_CINCO_BIS},
        )
    advertencias.append(
        "El art. 31 N 5 bis aplica a bienes %s. Es un regimen opcional: la empresa elige entre el N 5 y el "
        "N 5 bis, y esa decision la toma con su contador." % cinco_bis["bienes"])
    return cinco_bis["anios"], {
        "regimen": "Art. 31 N 5 bis (tramo %s)" % cinco_bis["tramo"],
        "articulo": ARTICULO_CINCO_BIS,
        "formula": cinco_bis["formula"],
    }


# --------------------------------------------------------------------------
# Depreciacion
# --------------------------------------------------------------------------

def depreciacion(valor, vida_util_normal=None, metodo="normal", anio_inicio=None, mes_inicio=1,
                 valor_residual=None, ingresos_uf=None, bien=None):
    """Tabla anual de depreciacion lineal, con el valor libro de cada anio.

        cuota_anual = (valor - valor_residual) / vida_util
        primer ejercicio = cuota_anual x meses de uso al 31 de diciembre / 12

    metodo: normal, acelerada, 5_bis o propyme.
    """
    metodo = _clave(metodo).replace(" ", "_") or "normal"
    if metodo in ("5bis", "cinco_bis", "n_5_bis"):
        metodo = "5_bis"
    if metodo == "pro_pyme":
        metodo = "propyme"
    if metodo not in METODOS:
        raise Problema(
            "No conozco el metodo de depreciacion «%s»." % metodo,
            "Los metodos disponibles son: normal, acelerada, 5_bis (empresas de hasta 100.000 UF) "
            "y propyme (depreciacion instantanea del regimen Pro Pyme).",
        )

    monto = numero(valor, "el valor del activo",
                   "Es lo que costo el bien, sin el IVA que la empresa recupera.")
    if monto <= 0:
        raise Problema("El valor del activo tiene que ser mayor que cero y me llego %s." % valor,
                       "Escribe cuanto costo el bien, por ejemplo 12000000.")

    advertencias = []
    residual = VALOR_RESIDUAL_TRIBUTARIO if metodo != "propyme" else 0.0
    if not _falta(valor_residual):
        residual = numero(valor_residual, "el valor residual")
    if residual < 0:
        raise Problema("El valor residual no puede ser negativo.",
                       "Dejalo en 1 peso, que es lo habitual, o en 0 si tu contador lo indica.")
    if residual >= monto:
        raise Problema(
            "El valor residual (%s) no puede ser igual o mayor que el valor del activo (%s)."
            % (residual, monto),
            "Revisa los dos numeros: el residual es lo que queda despues de depreciar todo.",
        )
    if metodo != "propyme":
        advertencias.append(AVISO_VALOR_RESIDUAL)

    anios, regimen = _resolver_vida_util(metodo, vida_util_normal, ingresos_uf, advertencias)

    mes = _mes(mes_inicio, "el mes en que se empezo a usar el bien") or 1
    anio = None
    if not _falta(anio_inicio):
        anio = entero(anio_inicio, "el anio en que se empezo a usar el bien",
                       "Escribe solo el anio, por ejemplo 2024.")

    base = monto - residual
    cuota = base / anios
    meses_primero = 13 - mes if metodo != "propyme" else 12

    tabla = []
    acumulada = 0.0
    numero_ejercicio = 1
    while acumulada < base - 0.005 and numero_ejercicio <= anios + 2:
        meses = meses_primero if numero_ejercicio == 1 else 12
        cuota_ejercicio = min(cuota * meses / 12.0, base - acumulada)
        acumulada += cuota_ejercicio
        tabla.append({
            "numero": numero_ejercicio,
            "anio": (anio + numero_ejercicio - 1) if anio else None,
            "meses": meses,
            "cuota": redondear(cuota_ejercicio),
            "depreciacion_acumulada": redondear(acumulada),
            "valor_libro": redondear(monto - acumulada),
        })
        numero_ejercicio += 1

    if metodo == "propyme":
        advertencias.append(
            "La depreciacion instantanea del regimen Pro Pyme exige que el bien este efectivamente pagado, "
            "porque ese regimen trabaja con flujos de caja. Si todavia lo estas pagando, no corresponde.")
        advertencias.append(
            "Las empresas del art. 14 letra D) N 3 no aplican correccion monetaria.")
    else:
        advertencias.append(
            "Esta tabla esta en pesos historicos. Para la declaracion, cada anio hay que actualizar el valor "
            "del bien por correccion monetaria y recien sobre ese valor calcular la cuota. El motor lo hace "
            "con los factores oficiales del SII que tiene verificados.")
    if mes != 1 and metodo != "propyme":
        advertencias.append(
            "El primer ejercicio se deprecia solo por los %d meses de uso (desde %s hasta diciembre), asi que "
            "la depreciacion termina de repartirse en %d ejercicios."
            % (meses_primero, MESES[mes - 1], len(tabla)))

    explicacion = (
        "El bien costo %s y se deprecia en %d anios, asi que cada anio completo se rebaja %s. "
        "La depreciacion empieza cuando el bien se usa en la empresa, no cuando se compra."
        % (redondear(monto), anios, redondear(cuota)))
    if metodo == "propyme":
        explicacion = ("En el regimen Pro Pyme el bien se deprecia entero en el mismo ejercicio en que se "
                       "compra o se fabrica, siempre que este pagado: %s de una sola vez." % redondear(monto))

    return {
        "bien": bien,
        "metodo": metodo,
        "regimen": regimen["regimen"],
        "articulo": regimen["articulo"],
        "formula": regimen["formula"],
        "valor": redondear(monto),
        "valor_residual": redondear(residual),
        "base_depreciable": redondear(base),
        "vida_util_normal": _entero_o_nada(vida_util_normal),
        "vida_util_aplicada": anios,
        "cuota_anual": redondear(cuota),
        "anio_inicio": anio,
        "mes_inicio": mes,
        "meses_primer_ejercicio": meses_primero,
        "ejercicios": len(tabla),
        "tabla": tabla,
        "total_depreciado": redondear(sum(f["cuota"] for f in tabla)),
        "explicacion": explicacion,
        "fuente": FUENTE_VIDA_UTIL,
        "advertencias": advertencias,
    }


# --------------------------------------------------------------------------
# Correccion monetaria
# --------------------------------------------------------------------------

def anios_con_correccion():
    """Ejercicios para los que el motor tiene factores oficiales verificados."""
    return sorted(set(list(REAJUSTE_CAPITAL_PROPIO.keys()) + list(FACTORES_MENSUALES.keys())))


def correccion_monetaria(valor, anio_ejercicio, mes_adquisicion=None, anio_adquisicion=None,
                         porcentaje=None):
    """Actualiza el valor de un bien por la variacion del IPC (art. 41 de la Ley de la Renta).

    Bien que ya estaba al inicio del ejercicio: se usa el mismo porcentaje del
    capital propio inicial. Bien comprado durante el ejercicio: se usa el factor
    del mes de la compra. Si el porcentaje resulta negativo, se iguala a cero.
    """
    monto = numero(valor, "el valor a actualizar")
    ejercicio = entero(anio_ejercicio, "el anio del ejercicio",
                        "Es el anio que estas cerrando, por ejemplo 2025.")
    mes = _mes(mes_adquisicion, "el mes de la compra")
    anio_compra = None
    if not _falta(anio_adquisicion):
        anio_compra = entero(anio_adquisicion, "el anio de la compra", "Escribe solo el anio, por ejemplo 2025.")

    advertencias = []
    comprado_en_el_ejercicio = anio_compra is not None and anio_compra == ejercicio
    if anio_compra is not None and anio_compra > ejercicio:
        raise Problema(
            "El bien se compro en %d, despues del ejercicio %d que estas cerrando." % (anio_compra, ejercicio),
            "Revisa la fecha de compra o el anio del ejercicio.",
        )

    if not _falta(porcentaje):
        pct = numero(porcentaje, "el porcentaje de correccion monetaria")
        regla = ("Porcentaje indicado por ti. Confirmalo con tu contador o con la tabla del SII antes de "
                 "usarlo en una declaracion.")
        origen = "indicado por el usuario"
        advertencias.append(regla)
    elif comprado_en_el_ejercicio:
        if mes is None:
            raise Problema(
                "Para un bien comprado durante el ejercicio necesito el mes de la compra.",
                "Indicalo con --mes-compra (por ejemplo 3 o marzo): el factor de actualizacion cambia mes a mes.",
            )
        tabla_mes = FACTORES_MENSUALES.get(ejercicio)
        if not tabla_mes:
            raise Problema(
                "No tengo los factores oficiales de correccion monetaria del ejercicio %d." % ejercicio,
                "El motor solo trae los que estan verificados (ejercicio %s, segun la %s). Pidele el "
                "porcentaje a tu contador o busca la tabla en el sitio del SII, y pasamelo con --porcentaje."
                % (", ".join(str(a) for a in anios_con_correccion()), FUENTE_CORRECCION),
            )
        pct = round((tabla_mes[mes] - 1.0) * 100, 4)
        regla = ("Bien comprado en %s de %d: se actualiza por la variacion del IPC desde el ultimo dia del mes "
                 "anterior a la compra hasta el ultimo dia del mes anterior al balance."
                 % (MESES[mes - 1], ejercicio))
        origen = "factor mensual oficial del SII"
    else:
        pct = REAJUSTE_CAPITAL_PROPIO.get(ejercicio)
        if pct is None:
            raise Problema(
                "No tengo el porcentaje oficial de correccion monetaria del ejercicio %d." % ejercicio,
                "El motor solo trae los que estan verificados (ejercicio %s, segun la %s). Pidele el "
                "porcentaje a tu contador o busca la tabla en el sitio del SII, y pasamelo con --porcentaje."
                % (", ".join(str(a) for a in anios_con_correccion()), FUENTE_CORRECCION),
            )
        regla = ("Bien que ya estaba en la empresa al comenzar el ejercicio %d: se actualiza con el mismo "
                 "porcentaje del capital propio inicial, es decir la variacion del IPC entre el 30 de "
                 "noviembre de %d y el 30 de noviembre de %d." % (ejercicio, ejercicio - 1, ejercicio))
        origen = "reajuste oficial del capital propio inicial"

    if pct < 0:
        advertencias.append(
            "El porcentaje daba negativo (%s %%). La norma dice que en ese caso se iguala a cero, asi que el "
            "valor del bien no cambia." % pct)
        pct = 0.0

    factor = 1 + pct / 100.0
    actualizado = monto * factor
    return {
        "valor_inicial": redondear(monto),
        "anio_ejercicio": ejercicio,
        "mes_adquisicion": mes,
        "anio_adquisicion": anio_compra,
        "comprado_en_el_ejercicio": comprado_en_el_ejercicio,
        "porcentaje": round(pct, 4),
        "factor": round(factor, 6),
        "valor_actualizado": redondear(actualizado),
        "mayor_valor": redondear(actualizado - monto),
        "origen_del_factor": origen,
        "regla": regla,
        "explicacion": ("%s x %s = %s. La diferencia de %s no es una ganancia: solo mantiene el valor del bien "
                        "al dia con la inflacion."
                        % (redondear(monto), round(factor, 6), redondear(actualizado),
                           redondear(actualizado - monto))),
        "articulo": ARTICULO_CORRECCION,
        "fuente": FUENTE_CORRECCION,
        "advertencias": advertencias,
    }


def depreciar_con_correccion(detalle, correccion):
    """Rehace la cuota del ejercicio corregido: primero se actualiza, despues se deprecia.

    Regla del art. 41 de la Ley de la Renta, verificada en la investigacion
    (docs/investigacion/09, seccion 8.3):

        valor bruto actualizado        = valor x factor
        depreciacion previa actualizada = depreciacion acumulada al cierre anterior x factor
        cuota del ejercicio            = (valor bruto actualizado - residual) / vida util x meses / 12

    Los ejercicios siguientes necesitan su propio factor, que se publica cada
    año: la tabla los deja en pesos del ejercicio corregido y lo advierte.
    """
    ejercicio = correccion["anio_ejercicio"]
    tabla = detalle.get("tabla") or []
    fila = next((f for f in tabla if f.get("anio") == ejercicio), None)
    if fila is None:
        return dict(detalle, advertencias=list(detalle.get("advertencias") or []) + [
            "El ejercicio %d no esta dentro de la tabla de este bien, asi que la correccion monetaria no cambia "
            "ninguna cuota." % ejercicio])

    factor = correccion["factor"]
    anios = detalle["vida_util_aplicada"]
    residual = detalle["valor_residual"]
    bruto = detalle["valor"] * factor
    base = bruto - residual
    cuota_completa = base / anios

    anteriores = [f for f in tabla if f.get("anio") is not None and f["anio"] < ejercicio]
    acumulada = (anteriores[-1]["depreciacion_acumulada"] if anteriores else 0.0) * factor

    nueva_tabla = [dict(f) for f in anteriores]
    for original in tabla:
        if original.get("anio") is None or original["anio"] < ejercicio:
            continue
        if acumulada >= base - 0.005:
            break
        cuota = min(cuota_completa * original["meses"] / 12.0, base - acumulada)
        acumulada += cuota
        nueva_tabla.append({
            "numero": original["numero"], "anio": original["anio"], "meses": original["meses"],
            "cuota": redondear(cuota),
            "depreciacion_acumulada": redondear(acumulada),
            "valor_libro": redondear(bruto - acumulada),
            "en_pesos_de": ejercicio,
        })

    fila_nueva = next(f for f in nueva_tabla if f["anio"] == ejercicio)
    advertencias = [a for a in (detalle.get("advertencias") or []) if not a.startswith("Esta tabla esta en pesos")]
    advertencias.append(
        "Primero se actualizo el valor (%s x %s = %s) y recien sobre ese valor se calculo la cuota de %d: %s. "
        "Los ejercicios siguientes quedan en pesos de %d: cada año hay que volver a actualizarlos con el factor "
        "que publique el SII." % (redondear(detalle["valor"]), factor, redondear(bruto), ejercicio,
                                   fila_nueva["cuota"], ejercicio))
    resultado = dict(detalle)
    resultado.update({
        "tabla": nueva_tabla,
        "valor_actualizado": redondear(bruto),
        "cuota_del_ejercicio_corregido": fila_nueva["cuota"],
        "valor_libro_al_cierre_corregido": fila_nueva["valor_libro"],
        "total_depreciado": redondear(sum(f["cuota"] for f in nueva_tabla)),
        "advertencias": advertencias,
    })
    return resultado


def porcentaje_termino_giro(anio, mes):
    """Porcentaje de actualizacion para termino de giro publicado por el SII."""
    ejercicio = entero(anio, "el anio", "Escribe solo el anio, por ejemplo 2026.")
    numero_mes = _mes(mes, "el mes")
    tabla = PORCENTAJES_TERMINO_GIRO.get(ejercicio) or {}
    if numero_mes not in tabla:
        raise Problema(
            "No tengo publicado el porcentaje de termino de giro de %s de %d."
            % (MESES[(numero_mes or 1) - 1], ejercicio),
            "El SII publica esta tabla mes a mes. Pidesela a tu contador o revisala en el sitio del SII.",
        )
    return {
        "anio": ejercicio, "mes": numero_mes, "porcentaje": tabla[numero_mes],
        "factor": round(1 + tabla[numero_mes] / 100.0, 6),
        "uso": "Termino de giro y otras situaciones de reajustabilidad dentro del anio.",
        "fuente": "SII - tabla de porcentajes de actualizacion por correccion monetaria (termino de giro)",
    }


# --------------------------------------------------------------------------
# Cartera de activos
# --------------------------------------------------------------------------

def anio_y_mes_de_uso(activo):
    """Saca el anio y el mes en que el bien empezo a usarse."""
    for clave in ("fecha_uso", "fecha_puesta_en_uso", "fecha_compra", "fecha"):
        crudo = activo.get(clave)
        if _falta(crudo):
            continue
        if isinstance(crudo, (datetime.date, datetime.datetime)):
            return crudo.year, crudo.month
        texto = str(crudo).strip()
        coincidencia = re.match(r"^(\d{4})[-/](\d{1,2})", texto)
        if coincidencia:
            return int(coincidencia.group(1)), int(coincidencia.group(2))
        coincidencia = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", texto)
        if coincidencia:
            return int(coincidencia.group(3)), int(coincidencia.group(2))
        if re.match(r"^\d{4}$", texto):
            return int(texto), 1
    if not _falta(activo.get("anio_inicio")):
        return entero(activo["anio_inicio"], "el anio de inicio de uso", "Escribe solo el anio."), \
            (_mes(activo.get("mes_inicio")) or 1)
    return None, 1


def vida_util_del_activo(activo, advertencias, ruta=None):
    """Resuelve la vida util: la que viene en la planilla o la de la tabla del SII."""
    indicada = activo.get("vida_util_normal") or activo.get("vida_util")
    if not _falta(indicada):
        return entero(indicada, "la vida util", "Escribe los anios, por ejemplo 7."), "indicada por ti", None
    descripcion = activo.get("bien") or activo.get("nombre")
    if not descripcion:
        return None, None, ("No me dijiste que bien es ni cuantos anios dura, asi que no puedo depreciarlo.")
    busqueda = buscar_vida_util(descripcion, activo.get("actividad"), ruta=ruta)
    if not busqueda["encontrado"]:
        return None, None, busqueda["mensaje"]
    elegido = busqueda["eleccion_unica"]
    if not elegido:
        opciones = "; ".join("%s (%s anios)" % (c["bien"], c["vida_util_normal"])
                             for c in busqueda["coincidencias"])
        return None, None, ("«%s» calza con varias filas de la tabla del SII y no voy a elegir por ti. "
                            "Opciones: %s. Escribe los anios que corresponden en la columna "
                            "«Vida util normal (anos)»." % (descripcion, opciones))
    if elegido["requiere_confirmacion"] or elegido["vida_util_normal"] is None:
        return None, None, ("La vida util de «%s» depende de la variedad o del caso y la tabla no fija un "
                            "numero unico. Confirmala con tu contador y escribela en la columna "
                            "«Vida util normal (anos)». %s" % (elegido["bien"], elegido["notas"]))
    if len(busqueda["coincidencias"]) > 1:
        otras = "; ".join("%s (%s anios)" % (c["bien"], c["vida_util_normal"])
                          for c in busqueda["coincidencias"][1:])
        advertencias.append(
            "Para «%s» use «%s» (%d anios). La tabla tiene otras opciones parecidas: %s. Si corresponde otra, "
            "escribe los anios en la planilla."
            % (descripcion, elegido["bien"], elegido["vida_util_normal"], otras))
    return elegido["vida_util_normal"], "%s (%s)" % (elegido["bien"], elegido["codigo"]), None


def resumen_cartera(activos, anio=None, ruta=None, anios_para_renovar=2):
    """Totales de la cartera de activos fijos para un ejercicio.

    Entrega, por activo y en total: cuanto se invirtio, cuanto se deprecia en el
    ejercicio y con que valor libro queda. Marca ademas los activos que ya
    cumplieron su vida util, que son los candidatos naturales a reemplazo.
    """
    if not activos:
        raise Problema(
            "No hay activos cargados.",
            "Llena la planilla de activos fijos con una fila por bien: que es, cuanto costo y desde cuando "
            "se usa.",
        )
    ejercicio = entero(anio, "el anio del ejercicio", "Escribe solo el anio, por ejemplo 2025.") \
        if not _falta(anio) else datetime.date.today().year

    advertencias = []
    calculados = []
    sin_vida_util = []
    inversion = 0.0
    del_ejercicio = 0.0
    acumulada_total = 0.0
    libro_total = 0.0

    for posicion, activo in enumerate(activos, start=1):
        nombre = (activo.get("nombre") or activo.get("bien") or "activo %d" % posicion)
        fila = activo.get("_fila")
        estado = _clave(activo.get("estado") or "")
        if estado in ("baja", "dado de baja", "vendido", "enajenado"):
            continue
        try:
            monto = numero(activo.get("valor") or activo.get("valor_de_compra"), "el valor del activo")
        except Problema as problema:
            sin_vida_util.append({"activo": nombre, "fila": fila, "motivo": problema.mensaje})
            continue
        anio_inicio, mes_inicio = anio_y_mes_de_uso(activo)
        if not anio_inicio:
            sin_vida_util.append({
                "activo": nombre, "fila": fila,
                "motivo": "No se desde cuando se usa este bien: sin esa fecha no puedo repartir la "
                          "depreciacion. Escribe la fecha de compra en la planilla.",
            })
            continue
        anios, origen, motivo = vida_util_del_activo(activo, advertencias, ruta=ruta)
        if motivo:
            sin_vida_util.append({"activo": nombre, "fila": fila, "motivo": motivo})
            continue

        metodo = _clave(activo.get("metodo") or "normal").replace(" ", "_") or "normal"
        try:
            detalle = depreciacion(monto, anios, metodo=metodo, anio_inicio=anio_inicio,
                                   mes_inicio=mes_inicio, bien=activo.get("bien"),
                                   ingresos_uf=activo.get("ingresos_uf"),
                                   valor_residual=activo.get("valor_residual"))
        except Problema as problema:
            sin_vida_util.append({"activo": nombre, "fila": fila, "motivo": problema.mensaje})
            continue

        fila_ejercicio = next((f for f in detalle["tabla"] if f["anio"] == ejercicio), None)
        cuota_ejercicio = fila_ejercicio["cuota"] if fila_ejercicio else 0.0
        anteriores = [f for f in detalle["tabla"] if f["anio"] is not None and f["anio"] <= ejercicio]
        if anteriores:
            acumulada = anteriores[-1]["depreciacion_acumulada"]
            valor_libro = anteriores[-1]["valor_libro"]
        else:
            acumulada, valor_libro = 0.0, detalle["valor"]

        ultimo_anio = detalle["tabla"][-1]["anio"]
        restantes = max(0, (ultimo_anio - ejercicio)) if ultimo_anio else None
        terminada = bool(ultimo_anio and ejercicio >= ultimo_anio)
        calculados.append({
            "activo": nombre,
            "fila": fila,
            "bien": activo.get("bien") or "",
            "vida_util_segun": origen,
            "categoria": (activo.get("categoria") or "sin categoria").strip() or "sin categoria",
            "sitio": activo.get("sitio") or "",
            "valor": detalle["valor"],
            "anio_inicio": anio_inicio,
            "mes_inicio": mes_inicio,
            "metodo": detalle["metodo"],
            "vida_util_aplicada": detalle["vida_util_aplicada"],
            "cuota_anual": detalle["cuota_anual"],
            "depreciacion_del_ejercicio": redondear(cuota_ejercicio),
            "depreciacion_acumulada": redondear(acumulada),
            "valor_libro": redondear(valor_libro),
            "porcentaje_depreciado": round(acumulada / detalle["valor"] * 100, 1) if detalle["valor"] else 0.0,
            "anios_de_uso": max(0, ejercicio - anio_inicio + 1),
            "anios_restantes": restantes,
            "vida_util_terminada": terminada,
            "en_uso_desde": "%s de %d" % (MESES[mes_inicio - 1], anio_inicio),
        })
        inversion += detalle["valor"]
        del_ejercicio += cuota_ejercicio
        acumulada_total += acumulada
        libro_total += valor_libro

    if not calculados:
        raise Problema(
            "No pude calcular ningun activo de la planilla.",
            "Revisa lo que falta en cada fila y vuelve a intentarlo.",
            {"activos_con_problema": sin_vida_util},
        )

    por_categoria = {}
    for activo in calculados:
        grupo = por_categoria.setdefault(activo["categoria"], {
            "categoria": activo["categoria"], "cantidad": 0, "inversion": 0.0,
            "depreciacion_del_ejercicio": 0.0, "valor_libro": 0.0})
        grupo["cantidad"] += 1
        grupo["inversion"] += activo["valor"]
        grupo["depreciacion_del_ejercicio"] += activo["depreciacion_del_ejercicio"]
        grupo["valor_libro"] += activo["valor_libro"]
    for grupo in por_categoria.values():
        for clave in ("inversion", "depreciacion_del_ejercicio", "valor_libro"):
            grupo[clave] = redondear(grupo[clave])

    renovacion = [
        {"activo": a["activo"], "bien": a["bien"], "categoria": a["categoria"],
         "anios_de_uso": a["anios_de_uso"], "anios_restantes": a["anios_restantes"],
         "valor_libro": a["valor_libro"], "vida_util_terminada": a["vida_util_terminada"]}
        for a in calculados
        if a["vida_util_terminada"] or (a["anios_restantes"] is not None
                                        and a["anios_restantes"] <= anios_para_renovar)
    ]
    renovacion.sort(key=lambda a: (not a["vida_util_terminada"], a["anios_restantes"] or 0))

    if sin_vida_util:
        advertencias.append(
            "Hay %d fila(s) que no pude calcular: estan en «activos_con_problema» con el motivo de cada una."
            % len(sin_vida_util))
    if renovacion:
        advertencias.append(
            "Hay %d activo(s) que ya cumplieron o estan por cumplir su vida util. Es el mejor momento para "
            "evaluar reemplazarlos por equipos mas eficientes: eso baja el consumo de energia y las emisiones."
            % len(renovacion))

    return {
        "ejercicio": ejercicio,
        "cantidad": len(calculados),
        "activos": calculados,
        "totales": {
            "inversion": redondear(inversion),
            "depreciacion_del_ejercicio": redondear(del_ejercicio),
            "depreciacion_acumulada": redondear(acumulada_total),
            "valor_libro": redondear(libro_total),
            "porcentaje_depreciado": round(acumulada_total / inversion * 100, 1) if inversion else 0.0,
        },
        "por_categoria": sorted(por_categoria.values(), key=lambda g: -g["inversion"]),
        "renovacion": renovacion,
        "activos_con_problema": sin_vida_util,
        "fuente": FUENTE_VIDA_UTIL,
        "advertencias": advertencias,
    }
