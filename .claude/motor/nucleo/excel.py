# -*- coding: utf-8 -*-
"""Lectura y escritura de archivos Excel (.xlsx) sin dependencias externas.

Un archivo .xlsx es un ZIP con archivos XML. Aqui se implementa lo justo para
que una persona pueda llenar plantillas en Excel y el motor las lea, y para
entregar resultados en Excel sin instalar nada.
"""

import datetime
import os
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

from .salida import Problema

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

# Formatos de numero integrados que representan fechas u horas.
FORMATOS_FECHA = set(list(range(14, 23)) + list(range(45, 48)) + [27, 30, 36, 50, 57])
BASE_1900 = datetime.datetime(1899, 12, 30)
BASE_1904 = datetime.datetime(1904, 1, 1)


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def _analizar_xml(datos):
    """Parsea XML rechazando DOCTYPE y entidades (evita XXE y 'billion laughs')."""
    cabeza = datos[:4096].lower() if isinstance(datos, bytes) else datos[:4096].encode().lower()
    if b"<!doctype" in cabeza or b"<!entity" in cabeza:
        raise Problema(
            "El archivo contiene instrucciones XML no permitidas y no se abrira por seguridad.",
            "Vuelve a guardarlo desde Excel como Libro de Excel (.xlsx) y reintenta.",
        )
    return ET.fromstring(datos)


def columna_a_indice(referencia):
    """Convierte 'B7' en 1 (indice de columna, base 0)."""
    letras = re.match(r"([A-Za-z]+)", referencia or "")
    if not letras:
        return 0
    total = 0
    for caracter in letras.group(1).upper():
        total = total * 26 + (ord(caracter) - 64)
    return total - 1


def indice_a_columna(indice):
    """Convierte 0 en 'A' y 26 en 'AA'."""
    nombre = ""
    indice += 1
    while indice > 0:
        indice, resto = divmod(indice - 1, 26)
        nombre = chr(65 + resto) + nombre
    return nombre


def normalizar_encabezado(texto):
    """Convierte 'Cantidad (kWh) ' en 'cantidad_kwh'."""
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def _escapar(texto):
    return (str(texto)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _serial_a_fecha(numero, base):
    try:
        momento = base + datetime.timedelta(days=float(numero))
    except (ValueError, OverflowError):
        return numero
    if momento.hour or momento.minute or momento.second:
        return momento.replace(microsecond=0).isoformat(sep=" ")
    return momento.date().isoformat()


# --------------------------------------------------------------------------
# Lectura
# --------------------------------------------------------------------------

def _cadenas_compartidas(zip_archivo):
    if "xl/sharedStrings.xml" not in zip_archivo.namelist():
        return []
    raiz = _analizar_xml(zip_archivo.read("xl/sharedStrings.xml"))
    cadenas = []
    for si in raiz.findall(NS + "si"):
        partes = [nodo.text or "" for nodo in si.iter(NS + "t")]
        cadenas.append("".join(partes))
    return cadenas


def _estilos_de_fecha(zip_archivo):
    """Indices de estilo que representan fechas."""
    if "xl/styles.xml" not in zip_archivo.namelist():
        return set()
    raiz = _analizar_xml(zip_archivo.read("xl/styles.xml"))
    personalizados = set()
    for numero in raiz.iter(NS + "numFmt"):
        codigo = numero.get("formatCode", "")
        sin_literales = re.sub(r"\[[^\]]*\]|\"[^\"]*\"", "", codigo)
        if re.search(r"[dmyhs]", sin_literales, re.IGNORECASE):
            personalizados.add(int(numero.get("numFmtId")))
    fechas = set()
    contenedor = raiz.find(NS + "cellXfs")
    if contenedor is None:
        return fechas
    for indice, xf in enumerate(contenedor.findall(NS + "xf")):
        formato = int(xf.get("numFmtId", "0"))
        if formato in FORMATOS_FECHA or formato in personalizados:
            fechas.add(indice)
    return fechas


def _hojas_del_libro(zip_archivo):
    """Lista de (nombre, ruta_del_xml) respetando el orden del libro."""
    libro = _analizar_xml(zip_archivo.read("xl/workbook.xml"))
    relaciones = {}
    if "xl/_rels/workbook.xml.rels" in zip_archivo.namelist():
        raiz_rel = _analizar_xml(zip_archivo.read("xl/_rels/workbook.xml.rels"))
        for relacion in raiz_rel:
            destino = relacion.get("Target", "")
            if destino.startswith("/"):
                destino = destino[1:]
            elif not destino.startswith("xl/"):
                destino = "xl/" + destino
            relaciones[relacion.get("Id")] = destino
    base_1904 = False
    propiedades = libro.find(NS + "workbookPr")
    if propiedades is not None and propiedades.get("date1904") in ("1", "true"):
        base_1904 = True
    hojas = []
    contenedor = libro.find(NS + "sheets")
    nodos = contenedor.findall(NS + "sheet") if contenedor is not None else []
    for indice, hoja in enumerate(nodos):
        ruta = relaciones.get(hoja.get(NS_REL + "id"))
        if not ruta:
            ruta = "xl/worksheets/sheet%d.xml" % (indice + 1)
        hojas.append((hoja.get("name", "Hoja%d" % (indice + 1)), ruta))
    return hojas, base_1904


def _valor_de_celda(celda, cadenas, estilos_fecha, base):
    tipo = celda.get("t")
    estilo = int(celda.get("s", "0") or 0)
    if tipo == "inlineStr":
        nodo = celda.find(NS + "is")
        if nodo is None:
            return None
        return "".join(t.text or "" for t in nodo.iter(NS + "t")) or None
    nodo_valor = celda.find(NS + "v")
    if nodo_valor is None or nodo_valor.text is None:
        return None
    bruto = nodo_valor.text
    if tipo == "s":
        indice = int(bruto)
        return cadenas[indice] if indice < len(cadenas) else None
    if tipo == "b":
        return bruto in ("1", "true", "TRUE")
    if tipo in ("str", "e"):
        return bruto
    try:
        numero = float(bruto)
    except ValueError:
        return bruto
    if estilo in estilos_fecha:
        return _serial_a_fecha(numero, base)
    if numero == int(numero) and abs(numero) < 1e15:
        return int(numero)
    return numero


def leer_xlsx(ruta):
    """Lee todas las hojas y devuelve {nombre_hoja: [[celda, ...], ...]}."""
    if not os.path.exists(ruta):
        raise Problema(
            "No encontre el archivo Excel: %s" % ruta,
            "Revisa el nombre y la carpeta. Si lo acabas de guardar, confirma que sea .xlsx y no .xls o .csv.",
        )
    try:
        with zipfile.ZipFile(ruta) as zip_archivo:
            cadenas = _cadenas_compartidas(zip_archivo)
            estilos_fecha = _estilos_de_fecha(zip_archivo)
            hojas, es_1904 = _hojas_del_libro(zip_archivo)
            base = BASE_1904 if es_1904 else BASE_1900
            libro = {}
            for nombre, ruta_hoja in hojas:
                if ruta_hoja not in zip_archivo.namelist():
                    libro[nombre] = []
                    continue
                raiz = _analizar_xml(zip_archivo.read(ruta_hoja))
                filas = []
                datos = raiz.find(NS + "sheetData")
                nodos = datos.findall(NS + "row") if datos is not None else []
                for fila in nodos:
                    valores = []
                    for celda in fila.findall(NS + "c"):
                        posicion = columna_a_indice(celda.get("r", ""))
                        while len(valores) < posicion:
                            valores.append(None)
                        valores.append(_valor_de_celda(celda, cadenas, estilos_fecha, base))
                    numero_fila = int(fila.get("r", len(filas) + 1))
                    while len(filas) < numero_fila - 1:
                        filas.append([])
                    filas.append(valores)
                libro[nombre] = filas
            return libro
    except zipfile.BadZipFile:
        raise Problema(
            "El archivo %s no es un Excel valido." % os.path.basename(ruta),
            "Abrelo en Excel y usa Guardar como, eligiendo Libro de Excel (.xlsx).",
        )


def leer_tabla(ruta, hoja=None):
    """Lee una hoja como lista de diccionarios.

    Usa la primera fila con contenido como encabezado. Cada diccionario incluye
    '_fila' con el numero de fila en Excel, para poder decir exactamente donde
    esta el problema cuando algo falta.
    """
    libro = leer_xlsx(ruta)
    if not libro:
        raise Problema(
            "El archivo %s no tiene hojas." % os.path.basename(ruta),
            "Revisa que sea la planilla correcta.",
        )
    if hoja is None:
        nombre = list(libro.keys())[0]
        for candidato in libro:
            if normalizar_encabezado(candidato) not in ("instrucciones", "ayuda", "ejemplo", "ejemplos"):
                nombre = candidato
                break
    else:
        coincidencias = [h for h in libro if normalizar_encabezado(h) == normalizar_encabezado(hoja)]
        if not coincidencias:
            raise Problema(
                "El archivo %s no tiene una hoja llamada %s." % (os.path.basename(ruta), hoja),
                "Hojas disponibles: %s." % ", ".join(libro.keys()),
            )
        nombre = coincidencias[0]

    filas = libro[nombre]
    encabezados = None
    inicio = 0
    for indice, fila in enumerate(filas):
        if any(celda not in (None, "") for celda in fila):
            encabezados = [normalizar_encabezado(celda) for celda in fila]
            inicio = indice + 1
            break
    if not encabezados:
        raise Problema(
            "La hoja %s esta vacia." % nombre,
            "Llena la plantilla con al menos una fila de datos y vuelve a intentarlo.",
        )

    registros = []
    for indice in range(inicio, len(filas)):
        fila = filas[indice]
        if not any(celda not in (None, "") for celda in fila):
            continue
        registro = {"_fila": indice + 1}
        for posicion, clave in enumerate(encabezados):
            if not clave:
                continue
            registro[clave] = fila[posicion] if posicion < len(fila) else None
        registros.append(registro)
    return {"hoja": nombre, "encabezados": [c for c in encabezados if c], "filas": registros}


# --------------------------------------------------------------------------
# Escritura
# --------------------------------------------------------------------------

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
%s
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

_ESTILOS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FF1B4332"/><name val="Calibri"/></font><font><i/><sz val="10"/><color rgb="FF555555"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFD8F3DC"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="4">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""

ESTILO_NORMAL = 0
ESTILO_ENCABEZADO = 1
ESTILO_TEXTO_LARGO = 2
ESTILO_NOTA = 3


def _celda_xml(referencia, valor, estilo):
    if valor is None or valor == "":
        return '<c r="%s" s="%d"/>' % (referencia, estilo)
    if isinstance(valor, bool):
        return '<c r="%s" s="%d" t="b"><v>%d</v></c>' % (referencia, estilo, 1 if valor else 0)
    if isinstance(valor, (int, float)):
        texto = repr(valor) if isinstance(valor, float) else str(valor)
        return '<c r="%s" s="%d"><v>%s</v></c>' % (referencia, estilo, texto)
    if isinstance(valor, (datetime.date, datetime.datetime)):
        valor = valor.isoformat()
    return ('<c r="%s" s="%d" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
            % (referencia, estilo, _escapar(valor)))


def _hoja_xml(hoja):
    columnas = hoja.get("columnas") or []
    filas = hoja.get("filas") or []
    partes = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
              '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    if hoja.get("congelar", True) and columnas:
        partes.append('<sheetViews><sheetView workbookViewId="0">'
                      '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
                      '</sheetView></sheetViews>')
    if columnas:
        anchos = []
        for indice, columna in enumerate(columnas):
            if isinstance(columna, dict):
                titulo = columna.get("titulo", "")
                ancho = columna.get("ancho")
            else:
                titulo = str(columna)
                ancho = None
            if not ancho:
                ancho = max(12, min(45, len(titulo) + 6))
            anchos.append('<col min="%d" max="%d" width="%.1f" customWidth="1"/>'
                          % (indice + 1, indice + 1, ancho))
        partes.append("<cols>%s</cols>" % "".join(anchos))
    partes.append("<sheetData>")
    numero = 1
    if columnas:
        celdas = []
        for indice, columna in enumerate(columnas):
            titulo = columna.get("titulo", "") if isinstance(columna, dict) else str(columna)
            celdas.append(_celda_xml("%s1" % indice_a_columna(indice), titulo, ESTILO_ENCABEZADO))
        partes.append('<row r="1">%s</row>' % "".join(celdas))
        numero = 2
    for fila in filas:
        if isinstance(fila, dict):
            valores = fila.get("valores", [])
            estilo_fila = fila.get("estilo", ESTILO_NORMAL)
        else:
            valores = fila
            estilo_fila = ESTILO_NORMAL
        celdas = []
        for indice, valor in enumerate(valores):
            celdas.append(_celda_xml("%s%d" % (indice_a_columna(indice), numero), valor, estilo_fila))
        partes.append('<row r="%d">%s</row>' % (numero, "".join(celdas)))
        numero += 1
    partes.append("</sheetData></worksheet>")
    return "".join(partes)


def escribir_xlsx(ruta, hojas):
    """Escribe un archivo Excel.

    hojas: lista de diccionarios con la forma
        {"nombre": "Datos",
         "columnas": [{"titulo": "Sitio", "ancho": 20}, ...],
         "filas": [[valor, ...], ...] o [{"valores": [...], "estilo": 2}, ...],
         "congelar": True}
    """
    if isinstance(hojas, dict):
        hojas = [{"nombre": nombre, "filas": filas} for nombre, filas in hojas.items()]
    if not hojas:
        raise Problema("No hay nada que escribir en el Excel.",
                       "Entrega al menos una hoja con datos.")

    carpeta = os.path.dirname(os.path.abspath(ruta))
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)

    overrides = []
    entradas_libro = []
    relaciones = []
    for indice, hoja in enumerate(hojas):
        numero = indice + 1
        overrides.append('<Override PartName="/xl/worksheets/sheet%d.xml" '
                         'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                         % numero)
        nombre = _escapar(hoja.get("nombre", "Hoja%d" % numero))[:31]
        entradas_libro.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (nombre, numero, numero))
        relaciones.append('<Relationship Id="rId%d" '
                          'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                          'Target="worksheets/sheet%d.xml"/>' % (numero, numero))

    libro_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                 '<sheets>%s</sheets></workbook>' % "".join(entradas_libro))
    rels_libro = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '%s<Relationship Id="rId%d" '
                  'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                  'Target="styles.xml"/></Relationships>'
                  % ("".join(relaciones), len(hojas) + 1))

    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as zip_archivo:
        zip_archivo.writestr("[Content_Types].xml", _CONTENT_TYPES % "\n".join(overrides))
        zip_archivo.writestr("_rels/.rels", _RELS)
        zip_archivo.writestr("xl/workbook.xml", libro_xml)
        zip_archivo.writestr("xl/_rels/workbook.xml.rels", rels_libro)
        zip_archivo.writestr("xl/styles.xml", _ESTILOS)
        for indice, hoja in enumerate(hojas):
            zip_archivo.writestr("xl/worksheets/sheet%d.xml" % (indice + 1), _hoja_xml(hoja))
    return os.path.abspath(ruta)
