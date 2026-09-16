# -*- coding: utf-8 -*-
"""Huella de carbono: calcula alcances 1, 2 y 3 desde las planillas de la empresa."""

import json
import os

from calculos import carbono
from nucleo import espacio, excel, informe
from nucleo.salida import Problema, Respuesta
from plantillas import definiciones

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


# Sube cuando cambia lo que guarda un calculo (por ejemplo, las notas de cada factor). Un informe armado
# con un resultado de una version anterior podria omitir advertencias: se recalcula antes.
VERSION_CALCULO = 2


def _leer_planilla(ruta_empresa, nombre, alcance=None):
    ruta = espacio.ruta_de(ruta_empresa, "datos", nombre)
    if not os.path.isfile(ruta):
        return [], None, None
    tabla, aviso = definiciones.leer_sin_ejemplos(ruta)
    return _preparar_filas(tabla, alcance), ruta, aviso


def calcular(opciones):
    """Calcula la huella de carbono del periodo y guarda el resultado."""
    perfil, ruta_empresa = _contexto(opciones)
    periodo = opciones.get("periodo") if opciones.get("periodo") is not True else None
    conjunto = (opciones.get("pcg") if opciones.get("pcg") is not True else None) or "AR5"

    registros, archivo_consumos, aviso_consumos = _leer_planilla(ruta_empresa, "consumos.xlsx")
    registros_a3, archivo_a3, aviso_a3 = _leer_planilla(ruta_empresa, "alcance3.xlsx", alcance=3)
    avisos_de_ejemplo = [aviso for aviso in (aviso_consumos, aviso_a3) if aviso]
    registros = registros + registros_a3
    if not registros and avisos_de_ejemplo:
        raise Problema(
            "Las planillas de %s solo tienen las filas de ejemplo de la plantilla." % perfil.get("nombre"),
            "Reemplazalas por los consumos reales de la empresa y avisame para calcular.",
        )
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
    resumen["version_calculo"] = VERSION_CALCULO
    resumen["advertencias"] = avisos_de_ejemplo + list(resumen["advertencias"])
    resumen["empresa"] = perfil.get("nombre")
    resumen["periodo"] = periodo or "todos los periodos cargados"
    resumen["archivos"] = [a for a in (archivo_consumos, archivo_a3) if a]

    destino = espacio.ruta_de(ruta_empresa, "resultados",
                              "huella_%s.json" % (periodo or "completa").replace("/", "-"))
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2, default=str)

    liviano = {clave: resumen[clave] for clave in
               ("total_kg_co2e", "total_t_co2e", "completo", "aviso_principal",
                "registros_calculados", "registros_con_problema",
                "por_alcance", "por_sitio", "por_recurso", "por_periodo", "por_categoria_alcance3",
                "calidad_datos", "set_pcg", "problemas", "fuentes", "empresa", "periodo")}
    liviano["resultado_guardado_en"] = destino
    liviano["mayores_fuentes"] = sorted(
        ({"recurso": k, "t_co2e": v["kg_co2e"] / 1000.0} for k, v in resumen["por_recurso"].items()),
        key=lambda x: -x["t_co2e"])[:5]
    liviano["mensaje"] = (
        "Huella calculada: %s tCO2e en %s." % (round(resumen["total_t_co2e"], 1), resumen["periodo"])
        if resumen["completo"] else
        "%s No presentes este total como definitivo hasta resolver esas filas."
        % resumen["aviso_principal"])
    advertencias = list(resumen["advertencias"])
    if not resumen["completo"]:
        advertencias.insert(0, resumen["aviso_principal"])
    return Respuesta(liviano, advertencias=advertencias, fuentes=resumen["fuentes"])


def _bloques_informe(resumen, perfil):
    total_t = resumen["total_t_co2e"]
    por_alcance = resumen["por_alcance"]
    bloques = []
    if not resumen.get("completo", True):
        bloques.append({
            "tipo": "nota", "estilo": "riesgo",
            "texto": "%s Revisa al final de este informe la lista de filas con problema: hasta "
                     "resolverlas, esta cifra no sirve para entregar a un cliente ni a una autoridad."
                     % resumen.get("aviso_principal", "Este total esta incompleto."),
        })
    bloques += [
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
        bloques.append({"tipo": "barras", "titulo": "De dónde vienen las emisiones", "unidad": "tCO2e",
                        "datos": [{"etiqueta": nombre.replace("_", " "), "valor": dato["kg_co2e"] / 1000.0}
                                  for nombre, dato in mayores]})

    periodos = sorted(k for k in resumen["por_periodo"] if k != "sin periodo")
    mensuales = [p for p in periodos if len(p) == 7]
    if len(mensuales) > 1:
        bloques.append({"tipo": "lineas", "titulo": "Evolución mes a mes", "unidad": "tCO2e",
                        "series": [{"nombre": "Emisiones",
                                    "puntos": [(p, resumen["por_periodo"][p]["kg_co2e"] / 1000.0)
                                               for p in mensuales]}]})
        if len(mensuales) < len(periodos):
            bloques.append({"tipo": "texto",
                            "texto": "La curva muestra solo los datos cargados mes a mes. Los datos anuales "
                                     "(por ejemplo la cadena de valor) no aparecen aqui, pero si en el total."})
    elif len(periodos) > 1:
        bloques.append({"tipo": "lineas", "titulo": "Evolución por periodo", "unidad": "tCO2e",
                        "series": [{"nombre": "Emisiones",
                                    "puntos": [(p, resumen["por_periodo"][p]["kg_co2e"] / 1000.0) for p in periodos]}]})

    if resumen["por_sitio"]:
        bloques.append({"tipo": "tabla", "columnas": ["Sitio", "tCO2e", "Registros"], "numericas": [1, 2],
                        "filas": [[sitio, dato["kg_co2e"] / 1000.0, dato["registros"]]
                                  for sitio, dato in sorted(resumen["por_sitio"].items(),
                                                            key=lambda x: -x[1]["kg_co2e"])]})

    if resumen["por_categoria_alcance3"]:
        bloques.append({"tipo": "titulo", "texto": "Alcance 3 por categoría", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Categoria", "Nombre", "tCO2e"], "numericas": [2],
                        "filas": [[clave, CATEGORIAS_ALCANCE3.get(clave, ""), dato["kg_co2e"] / 1000.0]
                                  for clave, dato in sorted(resumen["por_categoria_alcance3"].items(),
                                                            key=lambda x: -x[1]["kg_co2e"])]})
    # Lo que no se estimo tambien es parte del resultado: el GHG Protocol pide declarar que quedo fuera.
    incluidas = {str(clave) for clave in (resumen.get("por_categoria_alcance3") or {})}
    fuera = [(clave, nombre) for clave, nombre in sorted(CATEGORIAS_ALCANCE3.items(), key=lambda x: int(x[0]))
             if clave not in incluidas]
    if fuera:
        bloques.append({"tipo": "titulo", "texto": "Categorías del alcance 3 que no se estimaron", "nivel": 3})
        bloques.append({"tipo": "texto",
                        "texto": "No se calcularon en este informe. Algunas pueden no aplicar al negocio; las que si "
                                 "apliquen quedan como brecha por medir."})
        bloques.append({"tipo": "lista", "items": ["%s. %s" % (clave, nombre) for clave, nombre in fuera]})

    calidad = resumen["calidad_datos"]["porcentaje"]
    por_gasto = resumen["calidad_datos"].get("estimado_por_gasto_pct") or 0.0
    bloques.extend([
        {"tipo": "titulo", "texto": "Calidad de los datos de origen", "nivel": 2},
        {"tipo": "texto", "texto": "De dónde salen las cantidades: una boleta o factura (reportado), una "
                                   "verificación de un tercero (verificado) o una estimación. No mide qué tan "
                                   "fino es el factor usado: eso se indica aparte, debajo."},
        {"tipo": "barras", "titulo": "", "unidad": "%", "datos": [
            {"etiqueta": "Verificado", "valor": calidad.get("verificado", 0)},
            {"etiqueta": "Reportado", "valor": calidad.get("reportado", 0)},
            {"etiqueta": "Estimado", "valor": calidad.get("estimado", 0)},
        ]},
    ])
    if por_gasto >= 1:
        bloques.append({"tipo": "nota", "estilo": "aviso",
                        "texto": "El %s %% de la huella se estimo por gasto (dinero gastado por un factor por "
                                 "dolar). Aunque el monto este bien respaldado, es el metodo mas grueso: sirve "
                                 "para ver donde esta el grueso, no para fijar metas ni comparar años."
                                 % informe.formatear_numero(round(por_gasto, 1))})

    if resumen.get("problemas"):
        bloques.append({"tipo": "titulo", "texto": "Filas que no se pudieron calcular", "nivel": 2})
        bloques.append({"tipo": "tabla", "columnas": ["Fila", "Que pasa", "Que hacer"],
                        "filas": [[p.get("fila"), p.get("error"), p.get("sugerencia")]
                                  for p in resumen["problemas"]]})

    # Todos los factores usados, con su nota y cuanto pesan en la huella. Antes se elegian por palabras clave
    # y quedaban fuera, por ejemplo, un factor provisional o uno usado fuera de lo que cubre.
    total_kg = resumen.get("total_kg_co2e") or 0.0
    usados = {}
    supuestos = []
    for fila in resumen.get("detalle") or []:
        factor = fila.get("factor") or {}
        ficha = usados.setdefault(factor.get("id"), {"recursos": set(), "kg": 0.0, "factor": factor})
        ficha["recursos"].add(str(fila.get("recurso") or ""))
        ficha["kg"] += fila.get("kg_co2e") or 0.0
        if fila.get("notas_de_la_fila"):
            supuestos.append("%s (fila %s): %s" % (fila.get("recurso"), fila.get("fila"), fila["notas_de_la_fila"]))
    if usados:
        bloques.append({"tipo": "titulo", "texto": "Factores usados y lo que dice su fuente", "nivel": 2})
        bloques.append({"tipo": "tabla",
                        "columnas": ["Para", "Factor y fuente", "Parte de la huella", "Nota de la fuente"],
                        "filas": [[", ".join(sorted(f["recursos"])),
                                   "%s (%s, %s)" % (clave, f["factor"].get("fuente"), f["factor"].get("anio")),
                                   "%s %%" % informe.formatear_numero(round(f["kg"] / total_kg * 100, 1))
                                   if total_kg else "-",
                                   f["factor"].get("notas") or "-"]
                                  for clave, f in sorted(usados.items(), key=lambda par: -par[1]["kg"])]})
    if supuestos:
        bloques.append({"tipo": "titulo", "texto": "Supuestos anotados en los datos", "nivel": 2})
        bloques.append({"tipo": "lista", "items": sorted(set(supuestos))})

    advertencias = [a for a in resumen.get("advertencias", []) if a]
    if advertencias:
        bloques.append({"tipo": "titulo", "texto": "Supuestos y limitaciones", "nivel": 2})
        bloques.append({"tipo": "texto",
                        "texto": "Esto es lo que hubo que asumir para calcular. Quien revise el dato "
                                 "necesita verlo: forma parte del resultado."})
        bloques.append({"tipo": "lista", "items": advertencias})

    bloques.extend([
        {"tipo": "titulo", "texto": "Metodología y fuentes", "nivel": 2},
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
    """Arma el informe HTML de la huella de carbono."""
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
    aviso_version = None
    if resumen.get("version_calculo") != VERSION_CALCULO:
        pcg = resumen.get("set_pcg") or opciones.get("pcg")
        try:
            # Con el mismo conjunto de potenciales que el calculo guardado, para no cambiar la cifra por eso.
            calcular(dict(opciones, pcg=pcg))
        except Problema as problema:
            raise Problema(
                "El calculo guardado es de una version anterior del motor y no se pudo recalcular: %s"
                % problema.mensaje,
                "%s No armo el informe con un resultado viejo: corrige eso y ejecuta huella calcular."
                % (problema.sugerencia or ""))
        with open(origen, encoding="utf-8") as archivo:
            resumen = json.load(archivo)
        aviso_version = ("El calculo guardado era de una version anterior del motor: se recalculo con los datos "
                         "actuales y los potenciales %s antes de armar el informe." % resumen.get("set_pcg"))
        resumen.setdefault("advertencias", []).insert(0, aviso_version)

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
    return Respuesta({
        "mensaje": "Informe listo: abrelo con doble clic y, si lo necesitas en PDF, imprimelo desde el navegador.",
        "archivo": destino,
        "total_t_co2e": resumen.get("total_t_co2e"),
        "empresa": perfil.get("nombre"),
    }, advertencias=[aviso_version] if aviso_version else [])


def factores(opciones):
    """Consulta el catalogo: que nombres existen, con que unidad y de que fuente.

    Es la forma de averiguar como hay que escribir una actividad en la planilla
    antes de calcular, sobre todo en el alcance 3 por gasto.
    """
    catalogo = carbono.cargar_factores()
    recurso = opciones.get("recurso") if opciones.get("recurso") is not True else None
    pais = (opciones.get("pais") if opciones.get("pais") is not True else None) or ""
    uso = opciones.get("uso") if opciones.get("uso") is not True else None
    alcance = opciones.get("alcance") if opciones.get("alcance") is not True else None

    seleccion = catalogo
    por_descripcion = False
    if recurso:
        clave = carbono.normalizar_recurso(recurso)
        palabras = [p for p in clave.split("_") if p]
        seleccion = [f for f in seleccion
                     if clave in f["recurso"] or all(p in f["recurso"] for p in palabras)]
        if not seleccion:
            # Nadie escribe «gasto agricultura» para la harina: buscamos tambien
            # en la descripcion del factor, que dice que cubre cada uno.
            seleccion = [f for f in catalogo
                         if all(p in carbono.normalizar_recurso(f["notas"]) for p in palabras)]
            por_descripcion = bool(seleccion)
    if uso:
        clave_uso = carbono.normalizar_recurso(uso)
        seleccion = [f for f in seleccion if f["uso"] == clave_uso]
    if alcance:
        try:
            numero = int(str(alcance).strip())
        except ValueError:
            raise Problema("El alcance se escribe 1, 2 o 3.", "Por ejemplo: --alcance 3")
        seleccion = [f for f in seleccion if f["alcance"] == numero]
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
            "que_cubre": factor["notas"],
            "fuente": factor["fuente"], "url": factor["url"], "calidad": factor["calidad"],
        })

    usos = sorted({f["uso"] for f in catalogo if f["uso"]})
    if not salida:
        pedido = ", ".join(t for t in [recurso and "recurso «%s»" % recurso,
                                       uso and "uso «%s»" % uso,
                                       alcance and "alcance %s" % alcance,
                                       pais and "pais %s" % pais] if t)
        return {
            "total": 0,
            "factores": [],
            "usos_disponibles": usos,
            "nombres_parecidos": carbono.parecidos(catalogo, recurso) if recurso else [],
            "mensaje": "No hay ningun factor con %s en el catalogo. Prueba con menos filtros, "
                       "o mira los nombres parecidos. Usos disponibles: %s."
                       % (pedido or "esos filtros", ", ".join(usos)),
        }
    return {
        "total": len(salida),
        "truncado": len(seleccion) > 200,
        "coincidencia": "por descripcion" if por_descripcion else "por nombre",
        "factores": salida,
        "usos_disponibles": usos,
        "mensaje": ("Ninguno se llama «%s», pero estos lo mencionan en su descripcion. " % recurso
                    if por_descripcion else "") +
                   "Cada factor indica su fuente y año. El nombre de la columna «recurso» es el que "
                   "hay que escribir tal cual en la planilla. Si falta uno, se puede agregar con respaldo.",
    }


ACCIONES = {"calcular": calcular, "reporte": reporte, "factores": factores}
