# -*- coding: utf-8 -*-
"""Catalogo de plantillas Excel que la persona llena con sus datos.

Cada plantilla trae una hoja de instrucciones, la hoja de datos con encabezados
y una fila de ejemplo que se borra al usarla. Las columnas se leen con
nucleo.excel.leer_tabla, que normaliza los titulos (por ejemplo
"Cantidad (kWh)" pasa a "cantidad_kwh").
"""

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
}


def listar():
    return [
        {"tipo": clave, "titulo": definicion["titulo"], "para_que": definicion["para_que"]}
        for clave, definicion in sorted(PLANTILLAS.items())
    ]


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
