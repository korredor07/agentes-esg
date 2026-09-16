# -*- coding: utf-8 -*-
"""Escritura de documentos Word (.docx) sin dependencias externas.

Sirve para entregar reportes que la persona pueda editar y firmar: memorias de
sostenibilidad, protocolos, informes de investigacion, cartas a proveedores.

Bloques (lista de diccionarios con la clave "tipo"):
    titulo        {"texto": "...", "nivel": 0}   0 = portada, 1 y 2 = secciones
    texto         {"texto": "...", "negrita": False}
    lista         {"items": ["...", "..."], "ordenada": False}
    tabla         {"columnas": [...], "filas": [[...]]}
    nota          {"texto": "..."}
    salto_pagina  {}
"""

import os
import zipfile

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>"""

_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>"""

_RELS_DOC = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

_ESTILOS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:after="140" w:line="276" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="240"/></w:pPr><w:rPr><w:b/><w:color w:val="1B4332"/><w:sz w:val="52"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="320" w:after="120"/></w:pPr><w:rPr><w:b/><w:color w:val="1B4332"/><w:sz w:val="32"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:outlineLvl w:val="1"/><w:spacing w:before="240" w:after="100"/></w:pPr><w:rPr><w:b/><w:color w:val="2D6A4F"/><w:sz w:val="26"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:outlineLvl w:val="2"/><w:spacing w:before="200" w:after="80"/></w:pPr><w:rPr><w:b/><w:color w:val="40916C"/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Nota"><w:name w:val="Nota"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="284"/><w:pBdr><w:left w:val="single" w:sz="18" w:space="8" w:color="2D6A4F"/></w:pBdr></w:pPr><w:rPr><w:i/><w:color w:val="404040"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Vineta"><w:name w:val="Vineta"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="426" w:hanging="220"/><w:spacing w:after="60"/></w:pPr></w:style>
</w:styles>"""

_NUCLEO_PROPIEDADES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>%s</dc:title><dc:creator>Agentes ESG</dc:creator><cp:lastModifiedBy>Agentes ESG</cp:lastModifiedBy>
</cp:coreProperties>"""

ESTILOS_TITULO = {0: "Title", 1: "Heading1", 2: "Heading2", 3: "Heading3"}


def _escapar(texto):
    return (str("" if texto is None else texto)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def _corridas(texto, negrita=False, cursiva=False):
    """Convierte texto con saltos de linea en 'runs' de Word."""
    propiedades = ""
    if negrita or cursiva:
        propiedades = "<w:rPr>%s%s</w:rPr>" % ("<w:b/>" if negrita else "", "<w:i/>" if cursiva else "")
    partes = []
    for indice, linea in enumerate(str(texto or "").split("\n")):
        salto = "<w:br/>" if indice else ""
        partes.append('<w:r>%s%s<w:t xml:space="preserve">%s</w:t></w:r>'
                      % (propiedades, salto, _escapar(linea)))
    return "".join(partes)


def _parrafo(texto, estilo=None, negrita=False, cursiva=False):
    propiedades = '<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % estilo if estilo else ""
    return "<w:p>%s%s</w:p>" % (propiedades, _corridas(texto, negrita, cursiva))


def _tabla(bloque):
    columnas = bloque.get("columnas", [])
    filas = bloque.get("filas", [])
    total = max(len(columnas), 1)
    ancho = int(9000 / total)
    partes = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/>'
              '<w:tblBorders>'
              '<w:top w:val="single" w:sz="4" w:color="C9D3CC"/>'
              '<w:left w:val="none" w:sz="0" w:color="auto"/>'
              '<w:bottom w:val="single" w:sz="4" w:color="C9D3CC"/>'
              '<w:right w:val="none" w:sz="0" w:color="auto"/>'
              '<w:insideH w:val="single" w:sz="4" w:color="E3E6E3"/>'
              '<w:insideV w:val="none" w:sz="0" w:color="auto"/>'
              '</w:tblBorders></w:tblPr>']
    partes.append("<w:tblGrid>%s</w:tblGrid>" % "".join('<w:gridCol w:w="%d"/>' % ancho for _ in range(total)))
    if columnas:
        celdas = []
        for titulo in columnas:
            celdas.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/><w:shd w:val="clear" w:fill="D8F3DC"/></w:tcPr>'
                          '%s</w:tc>' % (ancho, _parrafo(titulo, negrita=True)))
        partes.append('<w:tr><w:trPr><w:tblHeader/></w:trPr>%s</w:tr>' % "".join(celdas))
    for fila in filas:
        celdas = []
        for indice in range(total):
            valor = fila[indice] if indice < len(fila) else ""
            celdas.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/></w:tcPr>%s</w:tc>'
                          % (ancho, _parrafo(valor)))
        partes.append("<w:tr>%s</w:tr>" % "".join(celdas))
    partes.append("</w:tbl>")
    partes.append("<w:p/>")
    return "".join(partes)


def _bloque_xml(bloque):
    tipo = bloque.get("tipo", "texto")
    if tipo == "titulo":
        estilo = ESTILOS_TITULO.get(int(bloque.get("nivel", 1)), "Heading2")
        return _parrafo(bloque.get("texto", ""), estilo)
    if tipo == "texto":
        return _parrafo(bloque.get("texto", ""), negrita=bloque.get("negrita", False))
    if tipo == "nota":
        return _parrafo(bloque.get("texto", ""), "Nota")
    if tipo == "lista":
        partes = []
        for indice, item in enumerate(bloque.get("items", [])):
            marca = "%d. " % (indice + 1) if bloque.get("ordenada") else "• "
            partes.append(_parrafo(marca + str(item), "Vineta"))
        return "".join(partes)
    if tipo == "tabla":
        return _tabla(bloque)
    if tipo == "salto_pagina":
        return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    return _parrafo(bloque.get("texto", ""))


def escribir_docx(ruta, bloques, titulo="Documento"):
    """Escribe un archivo Word y devuelve la ruta absoluta."""
    carpeta = os.path.dirname(os.path.abspath(ruta))
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    cuerpo = "".join(_bloque_xml(bloque) for bloque in bloques)
    documento = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                 '<w:body>%s<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
                 '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="709" w:footer="709"/>'
                 '</w:sectPr></w:body></w:document>' % cuerpo)
    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as zip_archivo:
        zip_archivo.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zip_archivo.writestr("_rels/.rels", _RELS)
        zip_archivo.writestr("docProps/core.xml", _NUCLEO_PROPIEDADES % _escapar(titulo))
        zip_archivo.writestr("word/document.xml", documento)
        zip_archivo.writestr("word/_rels/document.xml.rels", _RELS_DOC)
        zip_archivo.writestr("word/styles.xml", _ESTILOS)
    return os.path.abspath(ruta)


def desde_markdown(texto):
    """Convierte un Markdown sencillo (#, ##, ###, -, |) en bloques para Word."""
    bloques = []
    parrafo = []
    tabla = None

    def cerrar_parrafo():
        if parrafo:
            bloques.append({"tipo": "texto", "texto": " ".join(parrafo).strip()})
            del parrafo[:]

    def cerrar_tabla():
        if tabla and tabla["filas"]:
            bloques.append({"tipo": "tabla", "columnas": tabla["columnas"], "filas": tabla["filas"]})
        elif tabla:
            bloques.append({"tipo": "tabla", "columnas": tabla["columnas"], "filas": []})

    for linea in str(texto or "").splitlines():
        limpia = linea.rstrip()
        if limpia.startswith("|") and limpia.endswith("|"):
            celdas = [c.strip() for c in limpia.strip("|").split("|")]
            if set("".join(celdas)) <= set("-: "):
                continue
            if tabla is None:
                cerrar_parrafo()
                tabla = {"columnas": celdas, "filas": []}
            else:
                tabla["filas"].append(celdas)
            continue
        if tabla is not None:
            cerrar_tabla()
            tabla = None
        if not limpia.strip():
            cerrar_parrafo()
            continue
        if limpia.startswith("#"):
            cerrar_parrafo()
            nivel = len(limpia) - len(limpia.lstrip("#"))
            bloques.append({"tipo": "titulo", "texto": limpia.lstrip("# ").strip(), "nivel": min(nivel, 3)})
            continue
        if limpia.lstrip().startswith(("- ", "* ")):
            cerrar_parrafo()
            item = limpia.lstrip()[2:].strip()
            if bloques and bloques[-1]["tipo"] == "lista" and not bloques[-1].get("ordenada"):
                bloques[-1]["items"].append(item)
            else:
                bloques.append({"tipo": "lista", "items": [item]})
            continue
        parrafo.append(limpia.strip())
    if tabla is not None:
        cerrar_tabla()
    cerrar_parrafo()
    return bloques
