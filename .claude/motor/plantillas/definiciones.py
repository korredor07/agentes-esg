# -*- coding: utf-8 -*-
"""Catalogo de plantillas Excel que la persona llena con sus datos.

Cada plantilla trae una hoja de instrucciones, la hoja de datos con encabezados
y una fila de ejemplo que se borra al usarla. Las columnas se leen con
nucleo.excel.leer_tabla, que normaliza los titulos (por ejemplo
"Cantidad (kWh)" pasa a "cantidad_kwh").
"""

import json
import os
import re

PLANTILLAS = {
    "sitios": {
        "titulo": "Sitios e instalaciones",
        "para_que": "Registrar cada lugar donde opera la empresa: oficinas, plantas, bodegas, faenas o campos.",
        "hoja": "Sitios",
        "columnas": [
            {"titulo": "Nombre del sitio", "ancho": 26, "ayuda": "Como le dicen internamente. Ej: Planta Chillan."},
            {"titulo": "Tipo", "ancho": 20, "ayuda": "oficina, planta, bodega, tienda, faena, campo, centro de datos u otro."},
            {"titulo": "Direccion", "ancho": 32, "ayuda": "Calle y numero (opcional)."},
            {"titulo": "Comuna o distrito", "ancho": 20, "ayuda": "Comuna (Chile) o distrito (Peru)."},
            {"titulo": "Region", "ancho": 20, "ayuda": "Region o departamento."},
            {"titulo": "Pais", "ancho": 10, "ayuda": "Codigo de dos letras: CL, PE, ES..."},
            {"titulo": "Superficie (m2)", "ancho": 16, "ayuda": "Metros cuadrados construidos u operados. Opcional."},
            {"titulo": "Trabajadores", "ancho": 14, "ayuda": "Personas que trabajan habitualmente en el sitio."},
            {"titulo": "Control operacional", "ancho": 20, "ayuda": "si / no. Marca si la empresa decide como opera el sitio."},
            {"titulo": "Notas", "ancho": 30, "ayuda": "Cualquier detalle util."},
        ],
        "ejemplo": [
            ["Planta Chillan", "planta", "Camino a Coihueco 1200", "Chillan", "Ñuble", "CL", 4200, 85, "si", "Opera todo el año"],
            ["Oficina central", "oficina", "Av. Apoquindo 4500, piso 8", "Las Condes", "Metropolitana", "CL", 350, 22, "si", ""],
        ],
    },
    "personas": {
        "titulo": "Personas y condiciones laborales",
        "para_que": "Base para los indicadores sociales de los reportes (GRI 401, 403, 405) y para obligaciones laborales.",
        "hoja": "Personas",
        "columnas": [
            {"titulo": "Periodo", "ancho": 12, "ayuda": "Año o mes del dato. Ej: 2025 o 2025-06."},
            {"titulo": "Sitio", "ancho": 24, "ayuda": "Nombre del sitio, igual que en la plantilla de sitios."},
            {"titulo": "Categoria", "ancho": 22, "ayuda": "direccion, jefatura, profesional, tecnico, operario, administrativo."},
            {"titulo": "Genero", "ancho": 14, "ayuda": "mujer, hombre, otro, no declarado."},
            {"titulo": "Tipo de contrato", "ancho": 18, "ayuda": "indefinido, plazo fijo, por obra, honorarios."},
            {"titulo": "Jornada", "ancho": 14, "ayuda": "completa o parcial."},
            {"titulo": "Numero de personas", "ancho": 18, "ayuda": "Cuantas personas hay en esta combinacion."},
            {"titulo": "Contrataciones", "ancho": 16, "ayuda": "Personas que ingresaron en el periodo."},
            {"titulo": "Desvinculaciones", "ancho": 18, "ayuda": "Personas que salieron en el periodo."},
            {"titulo": "Remuneracion promedio", "ancho": 22, "ayuda": "Promedio bruto mensual en moneda local. Opcional pero necesario para brecha salarial."},
            {"titulo": "Horas de capacitacion", "ancho": 20, "ayuda": "Total de horas del periodo para este grupo."},
            {"titulo": "Accidentes con tiempo perdido", "ancho": 28, "ayuda": "Cantidad de accidentes con dias perdidos."},
            {"titulo": "Dias perdidos", "ancho": 14, "ayuda": "Dias de licencia por accidentes del trabajo."},
            {"titulo": "Horas trabajadas", "ancho": 18, "ayuda": "Total de horas trabajadas del grupo en el periodo."},
            {"titulo": "Personas con discapacidad", "ancho": 26, "ayuda": "Para la Ley 21.015 (Chile)."},
        ],
        "ejemplo": [
            ["2025", "Planta Chillan", "operario", "mujer", "indefinido", "completa", 34, 6, 3, 780000, 120, 1, 12, 61200, 1],
            ["2025", "Planta Chillan", "operario", "hombre", "indefinido", "completa", 51, 9, 7, 810000, 180, 2, 21, 91800, 0],
        ],
    },
    "consumos": {
        "titulo": "Consumos de energia y combustibles (alcances 1 y 2)",
        "para_que": "Es la planilla principal de la huella de carbono: la electricidad que compras y los combustibles que quemas o que se fugan.",
        "hoja": "Consumos",
        "columnas": [
            {"titulo": "Periodo", "ancho": 12, "ayuda": "Año (2025) o mes (2025-03). Mensual permite ver la evolucion."},
            {"titulo": "Sitio", "ancho": 22, "ayuda": "Nombre del lugar, igual que en la plantilla de sitios."},
            {"titulo": "Recurso", "ancho": 22, "ayuda": "electricidad, diesel, gasolina, gas natural, GLP, kerosene, carbon, R-410A, R-134a..."},
            {"titulo": "Uso", "ancho": 16, "ayuda": "estacionaria (calderas, generadores, calefaccion), movil (vehiculos, maquinaria), fugitiva (recarga de refrigerantes) o electricidad."},
            {"titulo": "Cantidad", "ancho": 14, "ayuda": "Solo el numero, sin unidad."},
            {"titulo": "Unidad", "ancho": 12, "ayuda": "kWh, MWh, litros, m3, kg, toneladas."},
            {"titulo": "Calidad del dato", "ancho": 18, "ayuda": "verificado (auditado), reportado (boleta o medidor) o estimado (calculo propio)."},
            {"titulo": "Evidencia", "ancho": 26, "ayuda": "Nombre del archivo de respaldo, por ejemplo boleta-enero.pdf."},
            {"titulo": "Notas", "ancho": 28, "ayuda": "Lo que quieras recordar de esa fila."},
        ],
        "ejemplo": [
            ["2025-01", "Planta Chillan", "electricidad", "electricidad", 42350, "kWh", "reportado", "boleta-enero.pdf", ""],
            ["2025-01", "Planta Chillan", "diesel", "estacionaria", 1800, "litros", "reportado", "factura-diesel-enero.pdf", "Caldera"],
            ["2025-01", "Flota", "diesel", "movil", 3400, "litros", "reportado", "", "Camiones de reparto"],
            ["2025", "Oficina central", "R-410A", "fugitiva", 3.5, "kg", "estimado", "", "Recarga anual del aire acondicionado"],
        ],
    },
    "alcance3": {
        "titulo": "Alcance 3 - cadena de valor",
        "para_que": "Las emisiones que ocurren fuera de la empresa pero que le pertenecen: compras, fletes, viajes, residuos y agua. Suele ser la mayor parte de la huella.",
        "hoja": "Alcance 3",
        "columnas": [
            {"titulo": "Periodo", "ancho": 12, "ayuda": "Año (2025) o mes (2025-03)."},
            {"titulo": "Categoria", "ancho": 12, "ayuda": "Numero del 1 al 15 del GHG Protocol. 1 compras, 4 fletes de entrada, 5 residuos, 6 viajes, 7 traslado de trabajadores, 9 fletes de salida."},
            {"titulo": "Actividad", "ancho": 26, "ayuda": "camion, barco contenedor, carga aerea, vuelo, hotel, bus, residuo mixto relleno, agua potable, gasto consultoria..."},
            {"titulo": "Cantidad", "ancho": 14, "ayuda": "Solo el numero. Si es un flete, puedes dejarlo vacio y llenar toneladas y kilometros."},
            {"titulo": "Unidad", "ancho": 14, "ayuda": "t.km (fletes), pasajero.km (viajes), km (auto), noche (hotel), t (residuos), m3 (agua), USD (gasto)."},
            {"titulo": "Toneladas (si aplica)", "ancho": 20, "ayuda": "Peso transportado, para calcular las toneladas por kilometro."},
            {"titulo": "Kilometros (si aplica)", "ancho": 22, "ayuda": "Distancia del viaje o del flete."},
            {"titulo": "Proveedor", "ancho": 22, "ayuda": "Quien presta el servicio o vende el producto. Opcional."},
            {"titulo": "Calidad del dato", "ancho": 18, "ayuda": "verificado, reportado o estimado."},
            {"titulo": "Evidencia", "ancho": 24, "ayuda": "Archivo de respaldo si lo tienes."},
            {"titulo": "Notas", "ancho": 26, "ayuda": "Supuestos usados, por ejemplo la distancia asumida."},
        ],
        "ejemplo": [
            ["2025", "4", "camion", "", "t.km", 45, 620, "Transportes del Sur", "estimado", "", "Traslado de fruta a puerto"],
            ["2025", "9", "barco contenedor", "", "t.km", 120, 11500, "Naviera", "estimado", "", "Exportacion a Rotterdam"],
            ["2025", "6", "vuelo", 18000, "pasajero.km", "", "", "", "reportado", "pasajes-2025.pdf", "Viajes comerciales"],
            ["2025", "6", "hotel", 40, "noche", "", "", "", "reportado", "", ""],
            ["2025", "5", "residuo mixto relleno", 12, "t", "", "", "Municipalidad", "estimado", "", ""],
            ["2025", "1", "gasto consultoria", 15000, "USD", "", "", "Varias", "reportado", "", "Servicios profesionales del año"],
        ],
    },
    "rep": {
        "titulo": "Ley REP - productos prioritarios",
        "para_que": "Declarar cuantas toneladas de cada producto prioritario puso la empresa en el mercado chileno "
                    "cada año, y cuantas se recolectaron y valorizaron. Con esto se calculan las metas de la "
                    "Ley 20.920 (Ley REP).",
        "hoja": "Ley REP",
        "columnas": [
            {"titulo": "Anio", "ancho": 10,
             "ayuda": "Año calendario del dato (2025). Una fila por año, producto, categoria y material. "
                      "Necesitas el año anterior para calcular la meta del año siguiente."},
            {"titulo": "Producto prioritario", "ancho": 26,
             "ayuda": "envases, neumaticos, aceites lubricantes, pilas, aee (aparatos electricos y "
                      "electronicos) o baterias. Son los seis del art. 10 de la Ley 20.920."},
            {"titulo": "Categoria", "ancho": 22,
             "ayuda": "Envases: domiciliario o no domiciliario. Neumaticos: A o B. AEE: ait (intercambio de "
                      "temperatura), pfv (paneles fotovoltaicos) u otros. Pilas, aceites y baterias: dejala vacia."},
            {"titulo": "Material", "ancho": 22,
             "ayuda": "Solo para envases: carton para liquidos, metal, papel y carton, plastico, vidrio u otros. "
                      "Si el envase es de varios materiales, va a la subcategoria que sea al menos el 85% de su "
                      "masa (art. 6 del DS 12/2020)."},
            {"titulo": "Toneladas puestas en el mercado", "ancho": 32,
             "ayuda": "Toneladas que la empresa vendio o importo por primera vez en Chile ese año. Los envases "
                      "reutilizables no cuentan aqui (art. 3 del DS 12/2020)."},
            {"titulo": "Toneladas recolectadas", "ancho": 24,
             "ayuda": "Toneladas de residuos recolectadas ese año a nombre de la empresa, segun el certificado "
                      "del sistema de gestion."},
            {"titulo": "Toneladas valorizadas", "ancho": 24,
             "ayuda": "Toneladas efectivamente valorizadas ese año. En envases solo cuenta el reciclaje material "
                      "(art. 28); en neumaticos tambien recauchaje, coprocesamiento y valorizacion energetica."},
            {"titulo": "Sistema de gestion", "ancho": 22,
             "ayuda": "individual o colectivo. Si es colectivo, escribe el nombre del sistema al que adhiere."},
            {"titulo": "Evidencia", "ancho": 24,
             "ayuda": "Archivo de respaldo: certificado del sistema de gestion, factura, declaracion de importacion."},
            {"titulo": "Notas", "ancho": 28, "ayuda": "Lo que quieras recordar de esa fila."},
        ],
        "ejemplo": [
            [2025, "envases", "domiciliario", "plastico", 500, 0, 0, "colectivo", "", "Año base de la meta 2026"],
            [2026, "envases", "domiciliario", "plastico", 520, 60, 60, "colectivo", "certificado-2026.pdf", ""],
            [2025, "envases", "domiciliario", "vidrio", 300, 0, 0, "colectivo", "", "Año base de la meta 2026"],
            [2026, "envases", "domiciliario", "vidrio", 310, 50, 50, "colectivo", "certificado-2026.pdf", ""],
            [2025, "neumaticos", "A", "", 1000, 0, 0, "colectivo", "", "Año base de la meta 2026"],
            [2026, "neumaticos", "A", "", 1050, 700, 520, "colectivo", "", ""],
        ],
    },
    "medidas": {
        "titulo": "Medidas de reduccion de emisiones",
        "para_que": "Comparar acciones posibles por lo que cuesta cada tonelada de CO2 evitada y decidir cuales hacer primero.",
        "hoja": "Medidas",
        "columnas": [
            {"titulo": "Medida", "ancho": 32, "ayuda": "Que se haria. Ej: cambiar la iluminacion a LED."},
            {"titulo": "Inversion (CAPEX)", "ancho": 20, "ayuda": "Cuanto cuesta implementarla, una sola vez."},
            {"titulo": "Costo anual (OPEX)", "ancho": 20, "ayuda": "Cuanto cuesta mantenerla cada año."},
            {"titulo": "Ahorro anual", "ancho": 18, "ayuda": "Cuanto ahorra al año en energia, combustible o insumos."},
            {"titulo": "Vida util (años)", "ancho": 16, "ayuda": "Cuantos años dura la medida."},
            {"titulo": "tCO2e evitadas al año", "ancho": 22, "ayuda": "Toneladas de CO2 equivalente que deja de emitir al año."},
            {"titulo": "Responsable", "ancho": 20, "ayuda": "Quien la impulsaria. Opcional."},
            {"titulo": "Notas", "ancho": 30, "ayuda": "Supuestos, cotizaciones o condiciones para hacerla."},
        ],
        "ejemplo": [
            ["Iluminacion LED en planta", 45000, 1200, 14000, 10, 38, "Mantencion", "Cotizacion de marzo"],
            ["Recuperador de calor en caldera", 210000, 8000, 22000, 15, 130, "Operaciones", ""],
        ],
    },
    "agua": {
        "titulo": "Agua: extraccion, consumo y descarga",
        "para_que": "Base para la huella hidrica, los indicadores de agua de los reportes y las obligaciones de descarga.",
        "hoja": "Agua",
        "columnas": [
            {"titulo": "Periodo", "ancho": 12, "ayuda": "Año (2025) o mes (2025-03)."},
            {"titulo": "Sitio", "ancho": 22, "ayuda": "Nombre del sitio, igual que en la plantilla de sitios."},
            {"titulo": "Origen", "ancho": 22, "ayuda": "red publica, pozo, rio, mar, agua de lluvia, agua reutilizada."},
            {"titulo": "Extraccion (m3)", "ancho": 18, "ayuda": "Cuanta agua entro al sitio en el periodo."},
            {"titulo": "Descarga (m3)", "ancho": 18, "ayuda": "Cuanta agua salio: alcantarillado, rio, mar o infiltracion."},
            {"titulo": "Destino de la descarga", "ancho": 24, "ayuda": "alcantarillado, rio, mar, infiltracion, riego."},
            {"titulo": "Zona de estres hidrico", "ancho": 22, "ayuda": "si / no / no se. Marca si el sitio esta en una zona con escasez."},
            {"titulo": "Calidad del dato", "ancho": 18, "ayuda": "verificado, reportado o estimado."},
            {"titulo": "Notas", "ancho": 28, "ayuda": "Medidor, boleta o supuesto usado."},
        ],
        "ejemplo": [
            ["2025", "Planta Chillan", "red publica", 28500, 24000, "alcantarillado", "si", "reportado", "Boletas de la sanitaria"],
            ["2025", "Planta Chillan", "pozo", 12000, 0, "riego", "si", "estimado", "Estimado por horas de bombeo"],
        ],
    },
    "residuos": {
        "titulo": "Residuos generados y su destino",
        "para_que": "Base para el alcance 3 de residuos, las declaraciones ambientales y los indicadores de economia circular.",
        "hoja": "Residuos",
        "columnas": [
            {"titulo": "Periodo", "ancho": 12, "ayuda": "Año (2025) o mes (2025-03)."},
            {"titulo": "Sitio", "ancho": 22, "ayuda": "Donde se genero el residuo."},
            {"titulo": "Tipo de residuo", "ancho": 26, "ayuda": "organico, papel y carton, plastico, vidrio, metal, madera, mixto, peligroso, otro."},
            {"titulo": "Peligroso", "ancho": 14, "ayuda": "si / no. Los peligrosos tienen obligaciones propias."},
            {"titulo": "Cantidad", "ancho": 14, "ayuda": "Solo el numero."},
            {"titulo": "Unidad", "ancho": 12, "ayuda": "t (toneladas) o kg."},
            {"titulo": "Destino", "ancho": 24, "ayuda": "relleno sanitario, reciclaje, compostaje, valorizacion energetica, tratamiento."},
            {"titulo": "Quien lo retira", "ancho": 24, "ayuda": "Empresa de retiro o municipalidad. Opcional."},
            {"titulo": "Calidad del dato", "ancho": 18, "ayuda": "verificado, reportado o estimado."},
            {"titulo": "Notas", "ancho": 26, "ayuda": "Numero de guia de retiro u observaciones."},
        ],
        "ejemplo": [
            ["2025", "Planta Chillan", "organico", "no", 320, "t", "compostaje", "Compostera regional", "reportado", "Descarte de fruta"],
            ["2025", "Planta Chillan", "mixto", "no", 145, "t", "relleno sanitario", "Municipalidad", "reportado", ""],
            ["2025", "Planta Chillan", "peligroso", "si", 1.2, "t", "tratamiento", "Gestor autorizado", "reportado", "Aceites usados"],
        ],
    },
}


def listar():
    return [
        {"tipo": clave, "titulo": definicion["titulo"], "para_que": definicion["para_que"],
         "columnas": [columna["titulo"] for columna in definicion["columnas"]]}
        for clave, definicion in sorted(PLANTILLAS.items())
    ]


def _comparable(valor):
    """Un valor escrito a mano y el mismo leido de Excel tienen que compararse igual."""
    if valor is None:
        return ""
    texto = str(valor).strip().lower()
    # Excel devuelve «2026-01-05 08:00:00» lo que en la plantilla se escribio «2026-01-05 08:00».
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:00$", texto):
        texto = texto[:-3]
    try:
        numero = float(texto.replace(",", "."))
        return ("%.6f" % numero).rstrip("0").rstrip(".")
    except ValueError:
        return texto


# Columnas de texto libre que la persona toca sin cambiar el dato: no deciden si una fila es de ejemplo.
COLUMNAS_QUE_NO_IDENTIFICAN = ("notas", "responsable", "evidencia", "calidad")


def es_fila_de_ejemplo(definicion, fila):
    """Si la fila es una de las filas de ejemplo que trae la plantilla nueva.

    Acepta la fila como lista (en el orden de las columnas) o como diccionario con
    los encabezados normalizados, que es como la devuelve nucleo.excel.leer_tabla.
    Cambiar solo la nota, el responsable, la evidencia o la calidad de una fila de
    ejemplo no la vuelve un dato de la empresa: sus cifras siguen siendo inventadas.
    """
    if not definicion or not fila:
        return False
    from nucleo import excel
    columnas = [excel.normalizar_encabezado(c["titulo"]) for c in definicion["columnas"]]
    valores = [fila.get(c) for c in columnas] if isinstance(fila, dict) else list(fila)
    cuentan = [i for i, c in enumerate(columnas) if not c.startswith(COLUMNAS_QUE_NO_IDENTIFICAN)]

    def clave(lista):
        lista = list(lista) + [""] * (len(columnas) - len(lista))
        return [_comparable(lista[i]) for i in cuentan]

    buscada = clave(valores)
    return any(clave(ejemplo) == buscada for ejemplo in definicion.get("ejemplo") or [])


def es_empresa_de_ejemplo(ruta_planilla):
    """La empresa de ejemplo del proyecto usa a proposito los mismos datos que las plantillas.

    Se reconoce por la marca empresa_de_ejemplo de su empresa.json. Si ese archivo no
    se puede leer, se trata como una empresa real: dejar fuera los ejemplos es lo seguro.
    """
    carpeta = os.path.dirname(os.path.dirname(os.path.abspath(ruta_planilla)))
    try:
        with open(os.path.join(carpeta, "empresa.json"), encoding="utf-8") as archivo:
            return json.load(archivo).get("empresa_de_ejemplo") is True
    except (OSError, ValueError, AttributeError):
        return False


def leer_sin_ejemplos(ruta, definicion=None, hoja=None):
    """Lee una planilla de datos dejando fuera las filas de ejemplo de la plantilla.

    Si la persona llena la planilla en Excel y no borra los ejemplos, esas filas son de
    una empresa inventada y entrarian al calculo sin que nadie lo note. Devuelve
    (tabla, aviso): el aviso dice cuantas se dejaron fuera, o es None si no habia.
    definicion: la de la plantilla; si no se da, se deduce del nombre del archivo.
    """
    from nucleo import excel
    tabla = excel.leer_tabla(ruta, hoja=hoja)
    if definicion is None:
        definicion = PLANTILLAS.get(os.path.splitext(os.path.basename(ruta))[0].lower())
    tabla["filas_de_ejemplo"] = 0
    if not definicion or es_empresa_de_ejemplo(ruta):
        return tabla, None
    reales = [fila for fila in tabla["filas"] if not es_fila_de_ejemplo(definicion, fila)]
    tabla["filas_de_ejemplo"] = len(tabla["filas"]) - len(reales)
    tabla["filas"] = reales
    if not tabla["filas_de_ejemplo"]:
        return tabla, None
    return tabla, ("Deje fuera %d fila(s) de ejemplo de %s: son de una empresa inventada y no entran al "
                   "calculo. Borralas de la planilla cuando puedas."
                   % (tabla["filas_de_ejemplo"], os.path.basename(ruta)))


def obtener(tipo):
    clave = str(tipo or "").strip().lower().replace(" ", "_")
    return clave, PLANTILLAS.get(clave)


def hojas_de(definicion, con_ejemplo=True):
    """Convierte una definicion en las hojas que espera nucleo.excel.escribir_xlsx."""
    instrucciones = [
        ["Para que sirve esta planilla"],
        [definicion["para_que"]],
        [""],
        ["Como llenarla"],
        ["1. Escribe una fila por cada dato. No cambies los titulos de las columnas."],
        ["2. Borra las filas de ejemplo cuando ya no las necesites."],
        ["3. Guarda el archivo y avisale al asistente: el se encarga del resto."],
        ["4. Si un dato no lo tienes, dejalo vacio y cuentaselo al asistente."],
        [""],
        ["Que significa cada columna"],
    ]
    for columna in definicion["columnas"]:
        instrucciones.append(["%s: %s" % (columna["titulo"], columna.get("ayuda", ""))])
    hoja_instrucciones = {
        "nombre": "Instrucciones",
        "columnas": [{"titulo": definicion["titulo"], "ancho": 110}],
        "filas": [{"valores": fila, "estilo": 2} for fila in instrucciones],
        "congelar": False,
    }
    hoja_datos = {
        "nombre": definicion["hoja"],
        "columnas": definicion["columnas"],
        "filas": list(definicion["ejemplo"]) if con_ejemplo else [],
    }
    return [hoja_instrucciones, hoja_datos]
