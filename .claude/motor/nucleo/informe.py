# -*- coding: utf-8 -*-
"""Informes y tableros en HTML autocontenido.

El HTML no carga nada de internet: se abre con doble clic en cualquier
computador y se imprime a PDF desde el navegador (Ctrl+P). Los graficos son
SVG dibujados aqui mismo, sin librerias.

Bloques disponibles (lista de diccionarios con la clave "tipo"):
    titulo    {"texto": "...", "nivel": 2}
    texto     {"texto": "parrafo"}
    kpi       {"items": [{"etiqueta", "valor", "unidad", "detalle", "color"}]}
    tabla     {"columnas": [...], "filas": [[...]], "nota": "...", "numericas": [1,2]}
    lista     {"items": [...], "ordenada": False}
    barras    {"titulo": "...", "datos": [{"etiqueta", "valor"}], "unidad": "tCO2e"}
    lineas    {"titulo": "...", "series": [{"nombre", "puntos": [(x, y)]}], "unidad": ""}
    dona      {"titulo": "...", "datos": [{"etiqueta", "valor"}], "unidad": ""}
    semaforo  {"items": [{"etiqueta", "estado": "verde|amarillo|rojo|gris", "detalle"}]}
    nota      {"texto": "...", "estilo": "info|aviso|riesgo|exito"}
    separador {}
"""

import datetime
import os

COLORES_SERIE = ["#2D6A4F", "#40916C", "#74C69D", "#B7E4C7", "#D9A441", "#C1666B", "#6C757D", "#457B9D"]
ESTADOS = {
    "verde": ("#2D6A4F", "#D8F3DC", "Cumple"),
    "amarillo": ("#946200", "#FFF3CD", "Atencion"),
    "rojo": ("#A4161A", "#FBE3E4", "Critico"),
    "gris": ("#495057", "#E9ECEF", "Sin datos"),
}


def escapar(texto):
    return (str("" if texto is None else texto)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def formatear_numero(valor, decimales=None):
    """Formato chileno: miles con punto y decimales con coma."""
    if valor is None or valor == "":
        return "—"
    if isinstance(valor, str):
        return escapar(valor)
    if decimales is None:
        numero = float(valor)
        magnitud = abs(numero)
        if numero == int(numero) and magnitud < 1e12:
            decimales = 0
        elif magnitud >= 1:
            decimales = 1
        else:
            decimales = 3
    texto = ("{:,.%df}" % decimales).format(float(valor))
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


# --------------------------------------------------------------------------
# Graficos SVG
# --------------------------------------------------------------------------

def _barras(bloque):
    datos = [d for d in bloque.get("datos", []) if d.get("valor") is not None]
    if not datos:
        return '<p class="vacio">Sin datos para graficar.</p>'
    unidad = bloque.get("unidad", "")
    maximo = max([abs(float(d["valor"])) for d in datos]) or 1.0
    alto_fila = 34
    alto = alto_fila * len(datos) + 10
    ancho = 720
    ancho_etiqueta = 190
    ancho_barra = ancho - ancho_etiqueta - 120
    partes = ['<svg viewBox="0 0 %d %d" class="grafico" role="img" xmlns="http://www.w3.org/2000/svg">' % (ancho, alto)]
    for indice, dato in enumerate(datos):
        y = indice * alto_fila + 6
        valor = float(dato["valor"])
        largo = max(2.0, abs(valor) / maximo * ancho_barra)
        color = dato.get("color") or COLORES_SERIE[indice % len(COLORES_SERIE)]
        partes.append('<text x="0" y="%d" class="eje">%s</text>' % (y + 15, escapar(dato.get("etiqueta", ""))))
        partes.append('<rect x="%d" y="%d" width="%.1f" height="20" rx="4" fill="%s"/>'
                      % (ancho_etiqueta, y, largo, color))
        partes.append('<text x="%.1f" y="%d" class="valor">%s %s</text>'
                      % (ancho_etiqueta + largo + 8, y + 15, formatear_numero(valor), escapar(unidad)))
    partes.append("</svg>")
    return "".join(partes)


def _lineas(bloque):
    series = bloque.get("series", [])
    if not series:
        return '<p class="vacio">Sin datos para graficar.</p>'
    etiquetas = [str(p[0]) for p in series[0].get("puntos", [])]
    valores = [float(p[1]) for serie in series for p in serie.get("puntos", []) if p[1] is not None]
    if not valores:
        return '<p class="vacio">Sin datos para graficar.</p>'
    maximo = max(valores)
    minimo = min(min(valores), 0)
    rango = (maximo - minimo) or 1.0
    ancho, alto = 720, 300
    margen_x, margen_y = 60, 30
    util_x = ancho - margen_x - 20
    util_y = alto - margen_y - 40

    def coordenada(indice, total, valor):
        x = margen_x + (util_x * (indice / float(max(total - 1, 1))))
        y = margen_y + util_y - ((float(valor) - minimo) / rango * util_y)
        return x, y

    partes = ['<svg viewBox="0 0 %d %d" class="grafico" role="img" xmlns="http://www.w3.org/2000/svg">' % (ancho, alto)]
    for paso in range(5):
        y = margen_y + util_y * paso / 4.0
        valor = maximo - (rango * paso / 4.0)
        partes.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#E3E6E3"/>' % (margen_x, y, ancho - 20, y))
        partes.append('<text x="0" y="%.1f" class="eje">%s</text>' % (y + 4, formatear_numero(valor)))
    for indice_serie, serie in enumerate(series):
        puntos = serie.get("puntos", [])
        color = serie.get("color") or COLORES_SERIE[indice_serie % len(COLORES_SERIE)]
        camino = []
        for indice, punto in enumerate(puntos):
            if punto[1] is None:
                continue
            x, y = coordenada(indice, len(puntos), punto[1])
            camino.append("%s%.1f,%.1f" % ("M" if not camino else "L", x, y))
            partes.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>' % (x, y, color))
        if camino:
            estilo = ' stroke-dasharray="6 4"' if serie.get("punteada") else ""
            partes.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"%s/>'
                          % (" ".join(camino), color, estilo))
    for indice, etiqueta in enumerate(etiquetas):
        x, _ = coordenada(indice, len(etiquetas), minimo)
        if len(etiquetas) <= 14 or indice % max(1, len(etiquetas) // 12) == 0:
            partes.append('<text x="%.1f" y="%d" class="eje" text-anchor="middle">%s</text>'
                          % (x, alto - 12, escapar(etiqueta)))
    partes.append("</svg>")
    leyenda = []
    for indice, serie in enumerate(series):
        color = serie.get("color") or COLORES_SERIE[indice % len(COLORES_SERIE)]
        leyenda.append('<span class="leyenda"><i style="background:%s"></i>%s</span>'
                       % (color, escapar(serie.get("nombre", ""))))
    return "".join(partes) + '<div class="leyendas">%s</div>' % "".join(leyenda)


def _dona(bloque):
    datos = [d for d in bloque.get("datos", []) if d.get("valor")]
    total = sum(float(d["valor"]) for d in datos)
    if not datos or total <= 0:
        return '<p class="vacio">Sin datos para graficar.</p>'
    radio, grosor, centro = 80, 34, 100
    partes = ['<svg viewBox="0 0 460 210" class="grafico" role="img" xmlns="http://www.w3.org/2000/svg">']
    circunferencia = 2 * 3.141592653589793 * radio
    desplazamiento = 0.0
    leyenda = []
    for indice, dato in enumerate(datos):
        porcion = float(dato["valor"]) / total
        color = dato.get("color") or COLORES_SERIE[indice % len(COLORES_SERIE)]
        partes.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="%d" '
                      'stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f" transform="rotate(-90 %d %d)"/>'
                      % (centro, centro + 5, radio, color, grosor,
                         circunferencia * porcion, circunferencia, -circunferencia * desplazamiento,
                         centro, centro + 5))
        desplazamiento += porcion
        leyenda.append('<span class="leyenda"><i style="background:%s"></i>%s — %s %s (%s%%)</span>'
                       % (color, escapar(dato.get("etiqueta", "")), formatear_numero(dato["valor"]),
                          escapar(bloque.get("unidad", "")), formatear_numero(porcion * 100, 1)))
    partes.append('<text x="%d" y="%d" text-anchor="middle" class="dona-total">%s</text>'
                  % (centro, centro + 8, formatear_numero(total)))
    partes.append('<text x="%d" y="%d" text-anchor="middle" class="eje">%s</text>'
                  % (centro, centro + 28, escapar(bloque.get("unidad", ""))))
    partes.append("</svg>")
    return "".join(partes) + '<div class="leyendas">%s</div>' % "".join(leyenda)


# --------------------------------------------------------------------------
# Bloques
# --------------------------------------------------------------------------

def _kpi(bloque):
    tarjetas = []
    for item in bloque.get("items", []):
        color = ESTADOS.get(item.get("color", ""), (None, None, None))[0] or "#1B4332"
        valor = item.get("valor")
        valor_texto = valor if isinstance(valor, str) else formatear_numero(valor)
        tarjetas.append(
            '<div class="tarjeta"><div class="tarjeta-etiqueta">%s</div>'
            '<div class="tarjeta-valor" style="color:%s">%s <span>%s</span></div>'
            '<div class="tarjeta-detalle">%s</div></div>'
            % (escapar(item.get("etiqueta", "")), color, valor_texto,
               escapar(item.get("unidad", "")), escapar(item.get("detalle", ""))))
    return '<div class="tarjetas">%s</div>' % "".join(tarjetas)


def _tabla(bloque):
    columnas = bloque.get("columnas", [])
    numericas = set(bloque.get("numericas", []))
    encabezado = "".join('<th%s>%s</th>' % (' class="num"' if i in numericas else "", escapar(c))
                         for i, c in enumerate(columnas))
    filas = []
    for fila in bloque.get("filas", []):
        celdas = []
        for indice, celda in enumerate(fila):
            if indice in numericas and not isinstance(celda, str):
                celdas.append('<td class="num">%s</td>' % formatear_numero(celda))
            else:
                celdas.append("<td>%s</td>" % escapar(celda))
        filas.append("<tr>%s</tr>" % "".join(celdas))
    nota = '<p class="nota-tabla">%s</p>' % escapar(bloque["nota"]) if bloque.get("nota") else ""
    if not filas:
        filas = ['<tr><td colspan="%d" class="vacio">Sin datos todavia.</td></tr>' % max(len(columnas), 1)]
    return ('<div class="tabla-envoltura"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>%s</div>'
            % (encabezado, "".join(filas), nota))


def _semaforo(bloque):
    filas = []
    for item in bloque.get("items", []):
        color, fondo, etiqueta = ESTADOS.get(item.get("estado", "gris"), ESTADOS["gris"])
        filas.append('<div class="semaforo-fila"><span class="pastilla" style="color:%s;background:%s">%s</span>'
                     '<div><strong>%s</strong><div class="tarjeta-detalle">%s</div></div></div>'
                     % (color, fondo, escapar(item.get("estado_texto", etiqueta)),
                        escapar(item.get("etiqueta", "")), escapar(item.get("detalle", ""))))
    return '<div class="semaforo">%s</div>' % "".join(filas)


def _bloque_html(bloque):
    tipo = bloque.get("tipo", "texto")
    if tipo == "titulo":
        nivel = int(bloque.get("nivel", 2))
        return "<h%d>%s</h%d>" % (nivel, escapar(bloque.get("texto", "")), nivel)
    if tipo == "texto":
        return "<p>%s</p>" % escapar(bloque.get("texto", ""))
    if tipo == "kpi":
        return _kpi(bloque)
    if tipo == "tabla":
        return _tabla(bloque)
    if tipo == "lista":
        etiqueta = "ol" if bloque.get("ordenada") else "ul"
        elementos = "".join("<li>%s</li>" % escapar(i) for i in bloque.get("items", []))
        return "<%s>%s</%s>" % (etiqueta, elementos, etiqueta)
    if tipo in ("barras", "lineas", "dona"):
        dibujo = {"barras": _barras, "lineas": _lineas, "dona": _dona}[tipo](bloque)
        titulo = '<h3>%s</h3>' % escapar(bloque["titulo"]) if bloque.get("titulo") else ""
        return '<div class="panel">%s%s</div>' % (titulo, dibujo)
    if tipo == "semaforo":
        return _semaforo(bloque)
    if tipo == "nota":
        estilo = bloque.get("estilo", "info")
        return '<div class="aviso %s">%s</div>' % (escapar(estilo), escapar(bloque.get("texto", "")))
    if tipo == "separador":
        return "<hr/>"
    return "<p>%s</p>" % escapar(bloque.get("texto", ""))


_PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>%(titulo)s</title>
<style>
:root { --primario: %(primario)s; --secundario: %(secundario)s; --texto: #1B2A22; --suave: #5A6B62; --borde: #E3E6E3; --fondo: #F7F9F7; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--fondo); color: var(--texto);
       font-family: "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif; line-height: 1.55; }
.hoja { max-width: 960px; margin: 0 auto; padding: 32px 28px 64px; background: #FFFFFF; min-height: 100vh; }
header.principal { border-bottom: 4px solid var(--primario); padding-bottom: 16px; margin-bottom: 28px; }
.marca { font-size: 13px; letter-spacing: .12em; text-transform: uppercase; color: var(--primario); font-weight: 700; }
h1 { font-size: 30px; margin: 6px 0 4px; }
h2 { font-size: 21px; margin: 32px 0 10px; color: var(--primario); }
h3 { font-size: 16px; margin: 20px 0 8px; color: var(--suave); text-transform: uppercase; letter-spacing: .06em; }
p { margin: 10px 0; }
.subtitulo { color: var(--suave); margin: 0; }
.tarjetas { display: flex; flex-wrap: wrap; gap: 14px; margin: 18px 0; }
.tarjeta { flex: 1 1 190px; border: 1px solid var(--borde); border-radius: 12px; padding: 14px 16px; background: #FCFDFC; }
.tarjeta-etiqueta { font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--suave); }
.tarjeta-valor { font-size: 27px; font-weight: 700; margin-top: 4px; }
.tarjeta-valor span { font-size: 14px; font-weight: 500; color: var(--suave); }
.tarjeta-detalle { font-size: 13px; color: var(--suave); }
.tabla-envoltura { overflow-x: auto; margin: 14px 0; }
table { border-collapse: collapse; width: 100%%; font-size: 14px; }
th, td { border-bottom: 1px solid var(--borde); padding: 9px 10px; text-align: left; vertical-align: top; }
th { background: var(--secundario); color: var(--primario); font-size: 12.5px; text-transform: uppercase; letter-spacing: .05em; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:last-child td { border-bottom: none; }
.nota-tabla, .vacio { font-size: 13px; color: var(--suave); font-style: italic; }
.panel { border: 1px solid var(--borde); border-radius: 12px; padding: 16px; margin: 16px 0; background: #FCFDFC; }
.grafico { width: 100%%; height: auto; }
.grafico .eje { font-size: 12px; fill: var(--suave); }
.grafico .valor { font-size: 12px; fill: var(--texto); font-weight: 600; }
.dona-total { font-size: 22px; font-weight: 700; fill: var(--texto); }
.leyendas { display: flex; flex-wrap: wrap; gap: 12px; font-size: 13px; color: var(--suave); margin-top: 8px; }
.leyenda i { display: inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: 6px; }
.semaforo-fila { display: flex; gap: 12px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--borde); }
.pastilla { font-size: 12px; font-weight: 700; border-radius: 999px; padding: 3px 11px; white-space: nowrap; }
.aviso { border-left: 4px solid var(--primario); background: #F1F6F2; padding: 11px 14px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
.aviso.aviso-riesgo, .aviso.riesgo { border-color: #A4161A; background: #FBE3E4; }
.aviso.aviso, .aviso.advertencia { border-color: #D9A441; background: #FFF6E0; }
.aviso.exito { border-color: #2D6A4F; background: #D8F3DC; }
footer { margin-top: 42px; border-top: 1px solid var(--borde); padding-top: 14px; font-size: 12.5px; color: var(--suave); }
hr { border: none; border-top: 1px solid var(--borde); margin: 26px 0; }
@media print {
  body { background: #FFFFFF; }
  .hoja { max-width: none; padding: 0; }
  .panel, .tarjeta { break-inside: avoid; }
  h2 { break-after: avoid; }
}
</style>
</head>
<body>
<div class="hoja">
<header class="principal">
<div class="marca">%(marca)s</div>
<h1>%(titulo)s</h1>
<p class="subtitulo">%(subtitulo)s</p>
</header>
%(cuerpo)s
<footer>%(pie)s</footer>
</div>
</body>
</html>
"""


def render(titulo, bloques, marca=None, subtitulo="", pie=""):
    """Devuelve el HTML completo del informe."""
    marca = marca or {}
    cuerpo = "\n".join(_bloque_html(bloque) for bloque in bloques)
    momento = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    pie_texto = pie or (
        "Generado por Agentes ESG el %s. Documento de apoyo: revisa los datos antes de "
        "usarlo con fines regulatorios o publicos." % momento)
    return _PLANTILLA % {
        "titulo": escapar(titulo),
        "subtitulo": escapar(subtitulo),
        "marca": escapar(marca.get("nombre", "Agentes ESG")),
        "primario": escapar(marca.get("color_primario", "#1B4332")),
        "secundario": escapar(marca.get("color_secundario", "#D8F3DC")),
        "cuerpo": cuerpo,
        "pie": escapar(pie_texto),
    }


def escribir_html(ruta, titulo, bloques, marca=None, subtitulo="", pie=""):
    carpeta = os.path.dirname(os.path.abspath(ruta))
    if carpeta and not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(render(titulo, bloques, marca, subtitulo, pie))
    return os.path.abspath(ruta)
