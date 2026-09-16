# -*- coding: utf-8 -*-
"""Indicadores sociales a partir de la planilla de personas.

Calcula lo que piden los marcos de reporte y las normas laborales, con formulas
explicitas para que cualquiera pueda revisarlas:

    rotacion (%)            = desvinculaciones / dotacion promedio x 100
    contrataciones (%)      = contrataciones / dotacion promedio x 100
    brecha salarial (%)     = (promedio hombres - promedio mujeres) / promedio hombres x 100
    razon de remuneracion   = promedio mujeres / promedio hombres
    tasa de accidentabilidad (Chile) = accidentes / dotacion promedio x 100
    tasa de siniestralidad (Chile)   = dias perdidos / dotacion promedio x 100
    tasa de accidentes registrables (GRI 403-9) = accidentes x 200.000 / horas trabajadas
    horas de capacitacion por persona (GRI 404-1) = horas totales / dotacion

Las tasas chilenas usan la dotacion promedio del periodo, que es la convencion
del DS 67 para la evaluacion de siniestralidad; aqui se calcula con los datos
cargados, asi que es una aproximacion de gestion, no la cifra oficial de la
mutualidad.
"""

import math

from nucleo.salida import Problema

CATEGORIAS_DIRECCION = ("direccion", "gerencia", "jefatura", "alta direccion")


def _numero(valor):
    if valor in (None, ""):
        return 0.0
    try:
        return float(str(valor).replace(".", "").replace(",", ".")) if isinstance(valor, str) else float(valor)
    except (TypeError, ValueError):
        return 0.0


def _texto(valor):
    return str(valor or "").strip().lower()


def _hay_dato(fila, *columnas):
    """Distingue «escribio 0» de «dejo la celda vacia»."""
    return any(fila.get(c) not in (None, "") for c in columnas)


def _agregar(destino, clave, personas):
    destino[clave] = destino.get(clave, 0) + personas


def calcular(filas, periodo=None):
    """Calcula los indicadores sociales de un periodo."""
    if not filas:
        raise Problema(
            "La planilla de personas no tiene datos.",
            "Llena al menos una fila por grupo de trabajadores y vuelve a intentarlo.",
        )
    if periodo:
        filas = [f for f in filas if str(f.get("periodo", "")).startswith(str(periodo))]
        if not filas:
            raise Problema(
                "No hay filas del periodo %s en la planilla de personas." % periodo,
                "Revisa la columna Periodo: debe decir el año (2025) o el mes (2025-06).",
            )

    total = 0
    por_genero, por_categoria, por_contrato, por_jornada, por_sitio = {}, {}, {}, {}, {}
    contrataciones = desvinculaciones = 0
    accidentes = dias_perdidos = 0.0
    horas_trabajadas = horas_capacitacion = 0.0
    discapacidad = 0
    remuneraciones = {}
    direccion_total = direccion_mujeres = 0
    advertencias = []
    # Una columna vacia no es un cero: si nadie la lleno, el indicador no existe.
    con_dato = {"horas_capacitacion": False, "accidentes": False, "dias_perdidos": False,
                "horas_trabajadas": False, "discapacidad": False, "contrataciones": False,
                "desvinculaciones": False}

    for fila in filas:
        personas = int(_numero(fila.get("numero_de_personas") or fila.get("personas") or 0))
        if personas <= 0:
            advertencias.append("La fila %s no indica cuantas personas son: quedo fuera del calculo."
                                % fila.get("_fila", "?"))
            continue
        genero = _texto(fila.get("genero")) or "no declarado"
        categoria = _texto(fila.get("categoria")) or "sin categoria"
        total += personas
        _agregar(por_genero, genero, personas)
        _agregar(por_categoria, categoria, personas)
        _agregar(por_contrato, _texto(fila.get("tipo_de_contrato")) or "sin indicar", personas)
        _agregar(por_jornada, _texto(fila.get("jornada")) or "sin indicar", personas)
        _agregar(por_sitio, str(fila.get("sitio") or "sin sitio"), personas)

        contrataciones += int(_numero(fila.get("contrataciones")))
        desvinculaciones += int(_numero(fila.get("desvinculaciones")))
        accidentes += _numero(fila.get("accidentes_con_tiempo_perdido") or fila.get("accidentes"))
        dias_perdidos += _numero(fila.get("dias_perdidos"))
        horas_trabajadas += _numero(fila.get("horas_trabajadas"))
        horas_capacitacion += _numero(fila.get("horas_de_capacitacion") or fila.get("horas_capacitacion"))
        discapacidad += int(_numero(fila.get("personas_con_discapacidad")))

        con_dato["contrataciones"] |= _hay_dato(fila, "contrataciones")
        con_dato["desvinculaciones"] |= _hay_dato(fila, "desvinculaciones")
        con_dato["accidentes"] |= _hay_dato(fila, "accidentes_con_tiempo_perdido", "accidentes")
        con_dato["dias_perdidos"] |= _hay_dato(fila, "dias_perdidos")
        con_dato["horas_trabajadas"] |= _hay_dato(fila, "horas_trabajadas")
        con_dato["horas_capacitacion"] |= _hay_dato(fila, "horas_de_capacitacion", "horas_capacitacion")
        con_dato["discapacidad"] |= _hay_dato(fila, "personas_con_discapacidad")

        remuneracion = _numero(fila.get("remuneracion_promedio"))
        if remuneracion > 0:
            casilla = remuneraciones.setdefault(categoria, {})
            acumulado = casilla.setdefault(genero, {"suma": 0.0, "personas": 0})
            acumulado["suma"] += remuneracion * personas
            acumulado["personas"] += personas

        if categoria in CATEGORIAS_DIRECCION:
            direccion_total += personas
            if genero.startswith("mujer"):
                direccion_mujeres += personas

    if total == 0:
        raise Problema(
            "Ninguna fila indica cuantas personas son.",
            "Completa la columna «Numero de personas» en la planilla.",
        )

    dotacion_promedio = float(total)
    indicadores = {
        "periodo": periodo or "todos los periodos cargados",
        "dotacion_total": total,
        "por_genero": por_genero,
        "por_categoria": por_categoria,
        "por_tipo_de_contrato": por_contrato,
        "por_jornada": por_jornada,
        "por_sitio": por_sitio,
        "contrataciones": contrataciones,
        "desvinculaciones": desvinculaciones,
        "tasa_contratacion_pct": round(contrataciones / dotacion_promedio * 100.0, 1),
        "tasa_rotacion_pct": round(desvinculaciones / dotacion_promedio * 100.0, 1),
        "mujeres_pct": round(sum(v for k, v in por_genero.items() if k.startswith("mujer"))
                             / dotacion_promedio * 100.0, 1),
        "personas_con_discapacidad": discapacidad,
        "discapacidad_pct": round(discapacidad / dotacion_promedio * 100.0, 2),
        "accidentes_con_tiempo_perdido": int(accidentes),
        "dias_perdidos": int(dias_perdidos),
        "tasa_accidentabilidad_pct": round(accidentes / dotacion_promedio * 100.0, 2),
        "tasa_siniestralidad": round(dias_perdidos / dotacion_promedio * 100.0, 1),
        "horas_capacitacion": round(horas_capacitacion, 1),
        "horas_capacitacion_por_persona": round(horas_capacitacion / dotacion_promedio, 1),
    }

    if horas_trabajadas > 0:
        indicadores["horas_trabajadas"] = round(horas_trabajadas, 0)
        indicadores["tasa_accidentes_registrables"] = round(accidentes * 200000.0 / horas_trabajadas, 2)
        indicadores["nota_tasa_registrable"] = ("Accidentes por cada 200.000 horas trabajadas, "
                                                "la convencion del estandar GRI 403-9.")
    else:
        advertencias.append("Sin horas trabajadas no se puede calcular la tasa por 200.000 horas que pide "
                            "el estandar GRI 403-9.")

    if direccion_total:
        indicadores["mujeres_en_direccion_pct"] = round(direccion_mujeres / float(direccion_total) * 100.0, 1)
    else:
        advertencias.append("No hay filas de direccion o jefatura: no se pudo calcular la participacion "
                            "de mujeres en cargos de decision.")

    brechas = {}
    for categoria, generos in remuneraciones.items():
        mujeres = generos.get("mujer") or generos.get("mujeres")
        hombres = generos.get("hombre") or generos.get("hombres")
        if not mujeres or not hombres or not mujeres["personas"] or not hombres["personas"]:
            continue
        promedio_mujeres = mujeres["suma"] / mujeres["personas"]
        promedio_hombres = hombres["suma"] / hombres["personas"]
        if promedio_hombres <= 0:
            continue
        brechas[categoria] = {
            "promedio_mujeres": round(promedio_mujeres, 0),
            "promedio_hombres": round(promedio_hombres, 0),
            "razon_mujer_hombre": round(promedio_mujeres / promedio_hombres, 3),
            "brecha_pct": round((promedio_hombres - promedio_mujeres) / promedio_hombres * 100.0, 1),
        }
    indicadores["brecha_salarial_por_categoria"] = brechas
    if not brechas:
        advertencias.append("Falta la remuneracion promedio por grupo: sin ese dato no se puede calcular "
                            "la brecha salarial, que piden todos los marcos de reporte.")

    # Lo que nadie lleno se informa como sin dato, no como cero.
    SIN_DATO = {
        "horas_capacitacion": (["horas_capacitacion", "horas_capacitacion_por_persona"],
                               "horas de capacitacion"),
        "accidentes": (["accidentes_con_tiempo_perdido", "tasa_accidentabilidad_pct",
                        "tasa_accidentes_registrables"], "accidentes con tiempo perdido"),
        "dias_perdidos": (["dias_perdidos", "tasa_siniestralidad"], "dias perdidos"),
        "discapacidad": (["personas_con_discapacidad", "discapacidad_pct"],
                         "personas con discapacidad"),
        "contrataciones": (["contrataciones", "tasa_contratacion_pct"], "contrataciones"),
        "desvinculaciones": (["desvinculaciones", "tasa_rotacion_pct"], "desvinculaciones"),
    }
    sin_dato = []
    for clave, (afectados, etiqueta) in SIN_DATO.items():
        if con_dato[clave]:
            continue
        for indicador in afectados:
            indicadores[indicador] = None
        sin_dato.append(etiqueta)
    if sin_dato:
        indicadores["columnas_sin_llenar"] = sorted(sin_dato)
        advertencias.append(
            "La planilla no trae %s: esos indicadores quedan sin dato, no en cero. No los reportes "
            "como si valieran cero." % ", ".join(sorted(sin_dato)))

    indicadores["advertencias"] = advertencias
    indicadores["nota_metodologica"] = (
        "Tasas calculadas sobre la dotacion cargada en la planilla. Las cifras oficiales de "
        "accidentabilidad y siniestralidad las emite el organismo administrador del seguro de "
        "accidentes del trabajo; estas sirven para gestion interna.")
    return indicadores


def revisar_inclusion(indicadores, pais="CL"):
    """Revisa la cuota de inclusion laboral chilena (1 % desde 100 personas)."""
    if (pais or "").upper() != "CL":
        return {"aplica": False, "motivo": "La cuota de inclusion del 1 % es una obligacion chilena."}
    dotacion = indicadores.get("dotacion_total", 0)
    if dotacion < 100:
        return {"aplica": False, "dotacion": dotacion,
                "motivo": "La obligacion parte en 100 personas; la empresa tiene %d." % dotacion}
    exigidas = dotacion * 0.01
    contratadas = indicadores.get("personas_con_discapacidad", 0)
    return {
        "aplica": True,
        "dotacion": dotacion,
        "personas_exigidas": round(exigidas, 1),
        "personas_contratadas": contratadas,
        "cumple": contratadas >= exigidas,
        "faltan": max(0, int(math.ceil(exigidas)) - contratadas) if contratadas < exigidas else 0,
        "nota": ("La ley admite alternativas excepcionales y exige una comunicacion anual a la "
                 "Direccion del Trabajo. El redondeo de la cuota lo interpreta la autoridad: "
                 "confirma el detalle con la asesoria laboral."),
    }
