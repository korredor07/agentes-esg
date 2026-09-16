# -*- coding: utf-8 -*-
"""Lectura y revision de los datos cargados por la empresa."""

import datetime
import json
import os

from nucleo import espacio, excel
from plantillas import definiciones
from nucleo.salida import Problema, Respuesta

AYUDA = "Lee las planillas cargadas, resume que hay y detecta datos raros o meses faltantes."

MESES = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _resolver_archivo(ruta_empresa, nombre):
    if os.path.isabs(nombre) and os.path.isfile(nombre):
        return nombre
    for candidato in (os.path.join(ruta_empresa, nombre),
                      os.path.join(ruta_empresa, "datos", nombre),
                      os.path.join(ruta_empresa, "datos", nombre + ".xlsx"),
                      nombre):
        if os.path.isfile(candidato):
            return candidato
    raise Problema(
        "No encontre el archivo «%s» en la carpeta de la empresa." % nombre,
        "Revisa el nombre. Puedes ver lo que hay cargado con: datos resumen.",
    )


def resumen(opciones):
    """Resume que hay cargado en la carpeta de la empresa."""
    perfil, ruta = _contexto(opciones)
    carpeta = espacio.ruta_de(ruta, "datos")
    archivos = []
    for nombre in sorted(os.listdir(carpeta)):
        completa = os.path.join(carpeta, nombre)
        if not os.path.isfile(completa):
            continue
        ficha = {
            "archivo": nombre,
            "tamano_kb": round(os.path.getsize(completa) / 1024.0, 1),
            "actualizado": datetime.datetime.fromtimestamp(os.path.getmtime(completa)).strftime("%d-%m-%Y %H:%M"),
        }
        if nombre.lower().endswith(".xlsx"):
            try:
                libro = excel.leer_xlsx(completa)
                ficha["hojas"] = {hoja: max(len(filas) - 1, 0) for hoja, filas in libro.items()}
            except Problema as problema:
                ficha["problema"] = problema.mensaje
        archivos.append(ficha)
    resultados = sorted(os.listdir(espacio.ruta_de(ruta, "resultados")))
    reportes = sorted(os.listdir(espacio.ruta_de(ruta, "reportes")))
    return {
        "empresa": perfil.get("nombre"),
        "datos_cargados": archivos,
        "resultados_guardados": resultados,
        "reportes_generados": reportes,
        "mensaje": "Sin datos cargados todavia." if not archivos else
                   "Hay %d archivo(s) de datos cargados." % len(archivos),
    }


def leer(opciones):
    """Muestra el contenido de una planilla cargada."""
    perfil, ruta = _contexto(opciones)
    nombre = opciones.get("archivo")
    if not nombre or nombre is True:
        raise Problema("Falta decir que archivo leer.",
                       "Por ejemplo: datos leer --archivo consumos.xlsx")
    completa = _resolver_archivo(ruta, nombre)
    hoja = opciones.get("hoja") if opciones.get("hoja") is not True else None
    limite = opciones.get("limite")
    limite = int(limite) if limite and limite is not True else 300
    tabla = excel.leer_tabla(completa, hoja=hoja)
    filas = tabla["filas"]
    resultado = {
        "archivo": completa,
        "hoja": tabla["hoja"],
        "columnas": tabla["encabezados"],
        "total_filas": len(filas),
        "filas": filas[:limite],
        "truncado": len(filas) > limite,
    }
    # Aqui se muestra la planilla tal cual, pero se dice si quedan ejemplos: los calculos no los usan.
    _, definicion = definiciones.obtener(os.path.splitext(os.path.basename(completa))[0])
    if definicion and not definiciones.es_empresa_de_ejemplo(completa):
        ejemplos = len([f for f in filas if definiciones.es_fila_de_ejemplo(definicion, f)])
        resultado["filas_de_ejemplo"] = ejemplos
        if ejemplos:
            resultado["aviso"] = ("La planilla todavia tiene %d fila(s) de ejemplo de la plantilla. Los calculos "
                                  "las dejan fuera, pero conviene borrarlas." % ejemplos)
    return resultado


def _numero(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None


def anomalias(opciones):
    """Busca saltos raros y meses faltantes en todas las planillas cargadas."""
    perfil, ruta = _contexto(opciones)
    pedido = opciones.get("archivo") if opciones.get("archivo") not in (None, True) else None
    umbral = _numero(opciones.get("umbral")) or 50.0

    if pedido:
        archivos = [_resolver_archivo(ruta, pedido)]
    else:
        archivos = []
        for nombre in ("consumos.xlsx", "alcance3.xlsx", "personas.xlsx", "agua.xlsx", "residuos.xlsx"):
            candidato = espacio.ruta_de(ruta, "datos", nombre)
            if os.path.isfile(candidato):
                archivos.append(candidato)
        if not archivos:
            raise Problema(
                "No hay ninguna planilla cargada para revisar.",
                "Crea la primera con: plantilla crear --tipo consumos.",
            )

    hallazgos = []
    revisadas = []
    avisos = []
    for completa in archivos:
        try:
            del_archivo, series, aviso = _anomalias_de(completa, umbral)
        except Problema as problema:
            avisos.append("No pude revisar %s: %s" % (os.path.basename(completa), problema.mensaje))
            continue
        if aviso:
            avisos.append(aviso)
        revisadas.append({"archivo": os.path.basename(completa), "series": series,
                          "hallazgos": len(del_archivo)})
        hallazgos.extend(del_archivo)

    hallazgos.sort(key=lambda h: (h["tipo"] != "meses_faltantes", -abs(h.get("desvio_pct", 0))))
    return Respuesta(
        {
            "empresa": perfil.get("nombre"),
            "planillas_revisadas": revisadas,
            "umbral_pct": umbral,
            "hallazgos": hallazgos,
            "mensaje": ("No encontre datos raros en %s."
                        % (", ".join(r["archivo"] for r in revisadas) or "ninguna planilla")
                        if not hallazgos else
                        "Encontre %d cosa(s) que conviene revisar en %d planilla(s)."
                        % (len(hallazgos), len([r for r in revisadas if r["hallazgos"]]))),
        },
        advertencias=avisos + (
            ["Un salto no siempre es un error: puede ser estacionalidad o una parada de planta. "
             "Preguntale a la persona antes de corregir nada."] if hallazgos else []),
    )


# Cada planilla llama distinto a lo mismo: aqui se dice donde esta la cantidad
# y que la identifica, para poder revisarlas todas con el mismo criterio.
COLUMNAS_POR_PLANILLA = {
    "consumos.xlsx": {"cantidad": ["cantidad"], "que_es": ["recurso"]},
    "alcance3.xlsx": {"cantidad": ["cantidad"], "que_es": ["actividad", "categoria"]},
    "residuos.xlsx": {"cantidad": ["cantidad"], "que_es": ["tipo_de_residuo"]},
    "agua.xlsx": {"cantidad": ["extraccion_m3", "extraccion"], "que_es": ["origen"]},
    "personas.xlsx": {"cantidad": ["numero_de_personas"], "que_es": ["categoria"]},
}
COLUMNAS_POR_DEFECTO = {"cantidad": ["cantidad"], "que_es": ["recurso", "actividad", "categoria"]}


def _primer_valor(fila, columnas):
    for columna in columnas:
        valor = fila.get(columna)
        if valor not in (None, ""):
            return valor
    return None


def _anomalias_de(completa, umbral):
    """Revisa una planilla y devuelve (hallazgos, series revisadas)."""
    tabla, aviso = definiciones.leer_sin_ejemplos(completa)
    archivo = os.path.basename(completa)
    columnas = COLUMNAS_POR_PLANILLA.get(archivo.lower(), COLUMNAS_POR_DEFECTO)

    series = {}
    for fila in tabla["filas"]:
        periodo = str(fila.get("periodo") or "").strip()
        cantidad = _numero(_primer_valor(fila, columnas["cantidad"]))
        # 2025 (anual) o 2025-03 (mensual): cualquier otra cosa no es un periodo.
        if len(periodo) not in (4, 7) or cantidad is None:
            continue
        clave = (str(fila.get("sitio") or "sin sitio"),
                 str(_primer_valor(fila, columnas["que_es"]) or "sin recurso"),
                 str(fila.get("unidad") or ""))
        series.setdefault(clave, {})[periodo] = series.setdefault(clave, {}).get(periodo, 0.0) + cantidad

    hallazgos = []
    for (sitio, recurso, unidad), valores in sorted(series.items()):
        if len(valores) < 3:
            continue
        ordenados = sorted(valores.items())
        numeros = sorted(v for _, v in ordenados)
        mediana = numeros[len(numeros) // 2] if len(numeros) % 2 else \
            (numeros[len(numeros) // 2 - 1] + numeros[len(numeros) // 2]) / 2.0
        if mediana <= 0:
            continue
        for periodo, valor in ordenados:
            desvio = (valor - mediana) / mediana * 100.0
            if abs(desvio) >= umbral:
                hallazgos.append({
                    "tipo": "salto", "archivo": archivo,
                    "sitio": sitio, "recurso": recurso, "periodo": periodo,
                    "valor": valor, "unidad": unidad, "mediana": round(mediana, 2),
                    "desvio_pct": round(desvio, 1),
                    "detalle": "%s, %s en %s: %s %s, %s%% respecto a su mes tipico (%s %s)."
                               % (archivo, recurso, periodo, round(valor, 1), unidad,
                                  ("+%.0f" % desvio) if desvio > 0 else "%.0f" % desvio,
                                  round(mediana, 1), unidad),
                })
        mensuales = {p for p in valores if len(p) == 7}
        anios = {p[:4] for p in mensuales}
        for anio in sorted(anios):
            faltantes = [m for m in MESES if "%s-%s" % (anio, m) not in mensuales]
            if faltantes and len(faltantes) < 12:
                hallazgos.append({
                    "tipo": "meses_faltantes", "archivo": archivo, "sitio": sitio, "recurso": recurso, "anio": anio,
                    "meses": faltantes,
                    "detalle": "%s: falta %s de %s en %s (%s), el total del año queda incompleto."
                               % (archivo, "el mes" if len(faltantes) == 1 else "los meses",
                                  ", ".join(faltantes), anio, "%s / %s" % (sitio, recurso)),
                })

    return hallazgos, len(series), aviso


def escribir(opciones):
    """Escribe filas en una planilla de la empresa, creandola desde la plantilla si hace falta.

    Sirve para que el asistente llene la planilla por la persona despues de leer
    sus boletas o de que ella le dicte los datos.
    """
    perfil, ruta = _contexto(opciones)
    tipo = opciones.get("tipo")
    if not tipo or tipo is True:
        raise Problema(
            "Falta decir en que planilla escribir.",
            "Por ejemplo: --tipo consumos. Las disponibles salen con: plantilla listar.",
        )
    clave, definicion = definiciones.obtener(tipo)
    if not definicion:
        raise Problema(
            "No tengo una planilla llamada «%s»." % tipo,
            "Disponibles: %s." % ", ".join(d["tipo"] for d in definiciones.listar()),
        )

    crudo = opciones.get("filas")
    if not crudo or crudo is True:
        raise Problema(
            "Faltan las filas que quieres escribir.",
            'Pasalas como JSON con --filas, por ejemplo: --filas "[[\"2025-01\", \"Planta\", '
            '\"electricidad\", \"electricidad\", 4200, \"kWh\", \"reportado\", \"\", \"\"]]". '
            "Cada fila debe traer los valores en el orden de las columnas de la planilla.",
        )
    if os.path.isfile(str(crudo)):
        with open(crudo, encoding="utf-8") as archivo:
            filas = json.load(archivo)
    else:
        try:
            filas = json.loads(crudo)
        except ValueError as error:
            raise Problema(
                "No pude leer las filas: %s." % error,
                "Revisa que el JSON este bien formado, o guardalo en un archivo y pasa su ruta.",
            )
    if isinstance(filas, dict):
        filas = [filas]
    if not isinstance(filas, list) or not filas:
        raise Problema("Las filas deben venir como una lista.", "Ejemplo: [[valor1, valor2, ...], [...]]")

    columnas = [c["titulo"] for c in definicion["columnas"]]
    normalizadas = []
    for numero, fila in enumerate(filas, start=1):
        if isinstance(fila, dict):
            fila = [fila.get(c) if c in fila else fila.get(excel.normalizar_encabezado(c)) for c in columnas]
        if len(fila) > len(columnas):
            raise Problema(
                "La fila %d trae %d valores y la planilla tiene %d columnas."
                % (numero, len(fila), len(columnas)),
                "Columnas de «%s»: %s." % (clave, ", ".join(columnas)),
            )
        normalizadas.append(list(fila) + [""] * (len(columnas) - len(fila)))

    destino = espacio.ruta_de(ruta, "datos", "%s.xlsx" % clave)
    existentes = []
    ejemplos_quitados = 0
    if os.path.isfile(destino) and not opciones.get("reemplazar"):
        tabla = excel.leer_tabla(destino)
        for fila in tabla["filas"]:
            # Una planilla recien creada trae filas de ejemplo de una empresa inventada:
            # si se agregan datos reales debajo, esas filas entrarian al calculo.
            if definiciones.es_fila_de_ejemplo(definicion, fila) and not definiciones.es_empresa_de_ejemplo(destino):
                ejemplos_quitados += 1
                continue
            existentes.append([fila.get(excel.normalizar_encabezado(c)) for c in columnas])

    hojas = definiciones.hojas_de(definicion, con_ejemplo=False)
    hojas[1]["filas"] = existentes + normalizadas
    excel.escribir_xlsx(destino, hojas)
    advertencias = ["Muestrale a la persona lo que escribiste; puede ser en la misma respuesta en que "
                    "le entregas el calculo."]
    if ejemplos_quitados:
        advertencias.insert(0, "Quite %d fila(s) de ejemplo que traia la plantilla, para que no se mezclen con "
                               "los datos reales." % ejemplos_quitados)
    return Respuesta(
        {
            "mensaje": "%s %d fila(s) en la planilla de %s."
                       % ("Reemplace con" if opciones.get("reemplazar") else "Agregue",
                          len(normalizadas), definicion["titulo"].lower()),
            "archivo": destino, "columnas": columnas,
            "filas_en_la_planilla": len(existentes) + len(normalizadas),
            "filas_de_ejemplo_quitadas": ejemplos_quitados,
        },
        advertencias=advertencias)


ACCIONES = {"resumen": resumen, "leer": leer, "escribir": escribir, "anomalias": anomalias}
