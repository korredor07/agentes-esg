# -*- coding: utf-8 -*-
"""Huella de carbono: calcula alcances 1, 2 y 3 desde las planillas de la empresa."""

import json
import os

from calculos import carbono
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta

AYUDA = "Calcula la huella de carbono desde las planillas, guarda el resultado y arma el informe."

NOMBRES_ALCANCE = {
    "alcance_1": "Alcance 1 - lo que quema o fuga la empresa",
    "alcance_2": "Alcance 2 - electricidad y energia comprada",
    "alcance_3": "Alcance 3 - cadena de valor",
}

CATEGORIAS_ALCANCE3 = {
    "1": "Bienes y servicios comprados", "2": "Bienes de capital",
    "3": "Combustibles y energia no incluidos en alcance 1 y 2", "4": "Transporte y distribucion aguas arriba",
    "5": "Residuos generados en la operacion", "6": "Viajes de negocios",
    "7": "Desplazamiento de trabajadores", "8": "Activos arrendados aguas arriba",
    "9": "Transporte y distribucion aguas abajo", "10": "Procesamiento de productos vendidos",
    "11": "Uso de productos vendidos", "12": "Fin de vida de productos vendidos",
    "13": "Activos arrendados aguas abajo", "14": "Franquicias", "15": "Inversiones",
}


def _contexto(opciones):
    raiz = opciones.get("raiz") if opciones.get("raiz") is not True else None
    identificador = opciones.get("empresa") if opciones.get("empresa") is not True else None
    return espacio.cargar_empresa(identificador, raiz=raiz)


def _preparar_filas(tabla, alcance_por_defecto=None):
    """Normaliza las filas de una planilla al formato que espera el calculo."""
    registros = []
    for fila in tabla["filas"]:
        registro = dict(fila)
        registro["recurso"] = fila.get("recurso") or fila.get("actividad") or fila.get("actividad_o_recurso")
        registro["cantidad"] = fila.get("cantidad")
        registro["unidad"] = fila.get("unidad")
        # comodidad: si la persona puso toneladas y kilometros, calculamos las t.km
        toneladas = fila.get("toneladas_si_aplica") or fila.get("toneladas")
        kilometros = fila.get("kilometros_si_aplica") or fila.get("kilometros")
        if registro["cantidad"] in (None, "") and toneladas and kilometros:
            try:
                registro["cantidad"] = float(str(toneladas).replace(",", ".")) * float(str(kilometros).replace(",", "."))
                registro["unidad"] = "t.km"
            except ValueError:
                pass
        if alcance_por_defecto and not registro.get("alcance"):
            registro["alcance"] = alcance_por_defecto
        registros.append(registro)
    return registros


def _leer_planilla(ruta_empresa, nombre, alcance=None):
    ruta = espacio.ruta_de(ruta_empresa, "datos", nombre)
    if not os.path.isfile(ruta):
        return [], None
    tabla = excel.leer_tabla(ruta)
    return _preparar_filas(tabla, alcance), ruta


def calcular(opciones):
    perfil, ruta_empresa = _contexto(opciones)
    periodo = opciones.get("periodo") if opciones.get("periodo") is not True else None
    conjunto = (opciones.get("pcg") if opciones.get("pcg") is not True else None) or "AR5"

    registros, archivo_consumos = _leer_planilla(ruta_empresa, "consumos.xlsx")
    registros_a3, archivo_a3 = _leer_planilla(ruta_empresa, "alcance3.xlsx", alcance=3)
    registros = registros + registros_a3
    if not registros:
        raise Problema(
            "No encontre datos para calcular la huella de %s." % perfil.get("nombre"),
            "Crea la planilla con: plantilla crear --tipo consumos, llenala y avisame.",
        )
    if periodo:
        registros = [r for r in registros if str(r.get("periodo", "")).startswith(str(periodo))]
        if not registros:
            raise Problema(
                "No hay filas del periodo %s en las planillas." % periodo,
                "Revisa la columna Periodo: debe decir el año (2025) o el mes (2025-03).",
            )

    resumen = carbono.calcular(registros, conjunto=conjunto.upper(), pais=perfil.get("pais"))
    resumen["empresa"] = perfil.get("nombre")
    resumen["periodo"] = periodo or "todos los periodos cargados"
    resumen["archivos"] = [a for a in (archivo_consumos, archivo_a3) if a]

    destino = espacio.ruta_de(ruta_empresa, "resultados",
                              "huella_%s.json" % (periodo or "completa").replace("/", "-"))
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2, default=str)

    liviano = {clave: resumen[clave] for clave in
               ("total_kg_co2e", "total_t_co2e", "registros_calculados", "registros_con_problema",
                "por_alcance", "por_sitio", "por_recurso", "por_periodo", "por_categoria_alcance3",
                "calidad_datos", "set_pcg", "problemas", "fuentes", "empresa", "periodo")}
    liviano["resultado_guardado_en"] = destino
    liviano["mayores_fuentes"] = sorted(
        ({"recurso": k, "t_co2e": v["kg_co2e"] / 1000.0} for k, v in resumen["por_recurso"].items()),
        key=lambda x: -x["t_co2e"])[:5]
    return Respuesta(liviano, advertencias=resumen["advertencias"], fuentes=resumen["fuentes"])


def _bloques_informe(resumen, perfil):
    total_t = resumen["total_t_co2e"]
    por_alcance = resumen["por_alcance"]
    bloques = [
        {"tipo": "kpi", "items": [
            {"etiqueta": "Huella total", "valor": total_t, "unidad": "tCO2e",
             "detalle": "Periodo: %s" % resumen.get("periodo", ""), "color": "verde"},
            {"etiqueta": "Alcance 1", "valor": por_alcance.get("alcance_1", {}).get("kg_co2e", 0) / 1000.0,
             "unidad": "tCO2e", "detalle": "Combustion y fugas propias"},
            {"etiqueta": "Alcance 2", "valor": por_alcance.get("alcance_2", {}).get("kg_co2e", 0) / 1000.0,
             "unidad": "tCO2e", "detalle": "Energia comprada"},
            {"etiqueta": "Alcance 3", "valor": por_alcance.get("alcance_3", {}).get("kg_co2e", 0) / 1000.0,
             "unidad": "tCO2e", "detalle": "Cadena de valor"},
        ]},
        {"tipo": "dona", "titulo": "Reparto por alcance", "unidad": "tCO2e",
         "datos": [{"etiqueta": NOMBRES_ALCANCE.get(clave, clave), "valor": valor["kg_co2e"] / 1000.0}
                   for clave, valor in sorted(por_alcance.items())]},
    ]

    mayores = sorted(resumen["por_recurso"].items(), key=lambda x: -x[1]["kg_co2e"])[:8]
    if mayores:
        bloques.append({"tipo": "barras", "titulo": "De donde vienen las emisiones", "unidad": "tCO2e",
                        "datos": [{"etiqueta": nombre.replace("_", " "), "valor": dato["kg_co2e"] / 1000.0}
                                  for nombre, dato in mayores]})

    periodos = sorted(k for k in resumen["por_periodo"] if k != "sin periodo")
    if len(periodos) > 1:
        bloques.append({"tipo": "lineas", "titulo": "Evolucion por periodo", "unidad": "tCO2e",
                        "series": [{"nombre": "Emisiones",
                                    "puntos": [(p, resumen["por_periodo"][p]["kg_co2e"] / 1000.0) for p in periodos]}]})

    if resumen["por_sitio"]:
        bloques.append({"tipo": "tabla", "columnas": ["Sitio", "tCO2e", "Registros"], "numericas": [1, 2],
                        "filas": [[sitio, dato["kg_co2e"] / 1000.0, dato["registros"]]
                                  for sitio, dato in sorted(resumen["por_sitio"].items(),
                                                            key=lambda x: -x[1]["kg_co2e"])]})

    if resumen["por_categoria_alcance3"]:
        bloques.append({"tipo": "titulo", "texto": "Alcance 3 por categoria", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Categoria", "Nombre", "tCO2e"], "numericas": [2],
                        "filas": [[clave, CATEGORIAS_ALCANCE3.get(clave, ""), dato["kg_co2e"] / 1000.0]
                                  for clave, dato in sorted(resumen["por_categoria_alcance3"].items(),
                                                            key=lambda x: -x[1]["kg_co2e"])]})

    calidad = resumen["calidad_datos"]["porcentaje"]
    bloques.extend([
        {"tipo": "titulo", "texto": "Calidad de los datos", "nivel": 2},
        {"tipo": "texto", "texto": "Cuanto de la huella viene de datos medidos y cuanto de estimaciones. "
                                   "Para una auditoria conviene subir la proporcion verificada."},
        {"tipo": "barras", "titulo": "", "unidad": "%", "datos": [
            {"etiqueta": "Verificado", "valor": calidad.get("verificado", 0)},
            {"etiqueta": "Reportado", "valor": calidad.get("reportado", 0)},
            {"etiqueta": "Estimado", "valor": calidad.get("estimado", 0)},
        ]},
    ])

    if resumen.get("problemas"):
        bloques.append({"tipo": "titulo", "texto": "Filas que no se pudieron calcular", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Fila", "Que pasa", "Que hacer"],
                        "filas": [[p.get("fila"), p.get("error"), p.get("sugerencia")]
                                  for p in resumen["problemas"]]})

    bloques.extend([
        {"tipo": "titulo", "texto": "Metodologia y fuentes", "nivel": 2},
        {"tipo": "lista", "items": [
            "Metodologia: GHG Protocol Corporate Standard (alcances 1, 2 y 3).",
            "Potenciales de calentamiento global: %s." % resumen.get("set_pcg", "AR5"),
            "Alcance 2 calculado por ubicacion (factor de la red electrica del pais).",
        ] + ["Factores: %s" % f for f in resumen.get("fuentes", [])]},
        {"tipo": "nota", "estilo": "aviso",
         "texto": "Este informe es un apoyo de gestion, no una verificacion. Antes de usarlo ante una "
                  "autoridad, un cliente o una auditoria, revisa los datos de origen y sus respaldos."},
    ])
    return bloques


def reporte(opciones):
    perfil, ruta_empresa = _contexto(opciones)
    periodo = opciones.get("periodo") if opciones.get("periodo") is not True else None
    nombre = "huella_%s.json" % (periodo or "completa")
    origen = espacio.ruta_de(ruta_empresa, "resultados", nombre)
    if not os.path.isfile(origen):
        raise Problema(
            "Todavia no hay un calculo de huella guardado%s." % (" para %s" % periodo if periodo else ""),
            "Primero ejecuta: huella calcular. Despues genero el informe.",
        )
    with open(origen, encoding="utf-8") as archivo:
        resumen = json.load(archivo)

    marca = perfil.get("marca") or {}
    destino = espacio.ruta_de(ruta_empresa, "reportes",
                              "huella-carbono-%s.html" % (periodo or "completa"))
    informe.escribir_html(
        destino,
        "Huella de carbono %s" % (periodo or ""),
        _bloques_informe(resumen, perfil),
        marca=marca,
        subtitulo="%s - %s" % (perfil.get("nombre", ""), perfil.get("sector", "") or "Informe de emisiones"),
    )
    return {
        "mensaje": "Informe listo: abrelo con doble clic y, si lo necesitas en PDF, imprimelo desde el navegador.",
        "archivo": destino,
        "total_t_co2e": resumen.get("total_t_co2e"),
        "empresa": perfil.get("nombre"),
    }


def factores(opciones):
    catalogo = carbono.cargar_factores()
    recurso = opciones.get("recurso") if opciones.get("recurso") is not True else None
    pais = (opciones.get("pais") if opciones.get("pais") is not True else None) or ""
    seleccion = catalogo
    if recurso:
        clave = carbono.normalizar_recurso(recurso)
        seleccion = [f for f in seleccion if clave in f["recurso"]]
    if pais:
        seleccion = [f for f in seleccion if f["pais"] in (pais.upper(), "*")]
    pcg = carbono.cargar_pcg()
    salida = []
    for factor in seleccion[:200]:
        valor, _ = carbono.kg_co2e_por_unidad(factor, pcg, factor["set_pcg"] or "AR5")
        salida.append({
            "id": factor["id"], "recurso": factor["recurso_original"], "uso": factor["uso"],
            "alcance": factor["alcance"], "pais": factor["pais"], "anio": factor["anio"],
            "kg_co2e_por": "%s %s" % (round(valor, 6), factor["unidad"]),
            "fuente": factor["fuente"], "url": factor["url"], "calidad": factor["calidad"],
        })
    return {
        "total": len(salida),
        "factores": salida,
        "mensaje": "Cada factor indica su fuente y año. Si falta uno, se puede agregar con respaldo.",
    }


ACCIONES = {"calcular": calcular, "reporte": reporte, "factores": factores}
