# -*- coding: utf-8 -*-
"""Curva de costos marginales de abatimiento (MACC).

Responde: que medidas reducen emisiones, cuanto reducen y cuanto cuesta cada
tonelada evitada. Las medidas con costo negativo ahorran dinero.

    FRC(i, n) = i (1+i)^n / ((1+i)^n - 1)          factor de recuperacion de capital
    CMA = (CAPEX x FRC + OPEX - Ahorros) / tCO2e evitadas al año

La curva ordena las medidas de menor a mayor costo por tonelada y acumula el
abatimiento: asi se ve hasta donde hay que llegar para cubrir una brecha.
"""

import re

from nucleo.salida import Problema


def factor_recuperacion_capital(tasa, anios):
    """FRC: cuanto hay que pagar cada año para amortizar una inversion."""
    try:
        tasa = float(tasa)
        anios = float(anios)
    except (TypeError, ValueError):
        raise Problema("La tasa de descuento o la vida util no son numeros validos.",
                       "Usa por ejemplo tasa 0,1 (10 %) y vida util 10 años.")
    if anios <= 0:
        raise Problema("La vida util debe ser de al menos un año.",
                       "Indica cuantos años dura la medida.")
    if tasa == 0:
        return 1.0 / anios
    factor = (1 + tasa) ** anios
    return tasa * factor / (factor - 1)


def _numero(valor, nombre, medida):
    if valor in (None, ""):
        # Una celda vacia puede ser «cero» o «falta la cotizacion»: no se adivina, porque cambia el orden de la curva.
        raise Problema("En la medida «%s» falta %s." % (medida, nombre),
                       "Si de verdad es cero, escribe 0. Si falta la cotizacion, la medida queda fuera hasta tenerla.")
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace(" ", "")
    if re.match(r"^-?\d{1,3}(\.\d{3})+$", texto):
        # «45.000» puede ser cuarenta y cinco mil o 45 con decimales: no se adivina.
        raise Problema("En la medida «%s», no se si «%s» (%s) son miles o decimales." % (medida, texto, nombre),
                       "Escribelo sin puntos de miles (45000) o con coma decimal (45,5).")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "")
    try:
        return float(texto.replace(",", "."))
    except (TypeError, ValueError):
        raise Problema("En la medida «%s», el valor de %s no es un numero." % (medida, nombre),
                       "Escribe solo el numero, sin simbolos de moneda.")


def costo_marginal(medida, tasa_descuento=0.10):
    """Calcula el costo por tonelada evitada de una medida."""
    nombre = medida.get("medida") or medida.get("nombre") or "sin nombre"
    abatimiento = _numero(medida.get("tco2e_evitadas") or medida.get("abatimiento"), "toneladas evitadas", nombre)
    if abatimiento <= 0:
        raise Problema("La medida «%s» no indica cuantas toneladas de CO2e evita al año." % nombre,
                       "Sin ese dato no se puede calcular su costo por tonelada.")
    capex = _numero(medida.get("capex"), "la inversion", nombre)
    opex = _numero(medida.get("opex"), "el costo anual de operacion", nombre)
    ahorros = _numero(medida.get("ahorros"), "los ahorros anuales", nombre)
    vida_util = medida.get("vida_util") if medida.get("vida_util") not in (None, "") else medida.get("anios")
    vida = _numero(vida_util, "la vida util", nombre)
    if vida <= 0:
        raise Problema("En la medida «%s», la vida util tiene que ser de al menos un año." % nombre,
                       "Escribe cuantos años dura la medida.")
    tasa = _numero(medida.get("tasa_descuento") if medida.get("tasa_descuento") not in (None, "") else tasa_descuento,
                   "la tasa de descuento", nombre)

    frc = factor_recuperacion_capital(tasa, vida)
    capex_anualizado = capex * frc
    costo_anual = capex_anualizado + opex - ahorros
    return {
        "medida": nombre,
        "capex": capex, "opex": opex, "ahorros": ahorros,
        "vida_util": vida, "tasa_descuento": tasa,
        "frc": round(frc, 5),
        "capex_anualizado": round(capex_anualizado, 1),
        "costo_anual_neto": round(costo_anual, 1),
        "tco2e_evitadas": abatimiento,
        "costo_por_tonelada": round(costo_anual / abatimiento, 1),
        "ahorra_dinero": costo_anual < 0,
        "notas": medida.get("notas", ""),
    }


def curva(medidas, tasa_descuento=0.10, brecha=None):
    """Ordena las medidas por costo por tonelada y acumula el abatimiento."""
    if not medidas:
        raise Problema("No hay medidas de reduccion cargadas.",
                       "Agrega al menos una: que se haria, cuanto cuesta y cuanto reduce al año.")
    calculadas = []
    con_problema = []
    for medida in medidas:
        try:
            calculadas.append(costo_marginal(medida, tasa_descuento))
        except Problema as problema:
            # Una medida con un dato faltante queda fuera y se dice cual y por que; no tumba ni distorsiona el resto.
            con_problema.append({"medida": medida.get("medida") or medida.get("nombre") or "sin nombre",
                                 "fila": medida.get("_fila"), "problema": problema.mensaje,
                                 "que_hacer": problema.sugerencia})
    if not calculadas:
        raise Problema("No pude calcular ninguna de las medidas cargadas.",
                       "; ".join("%s: %s" % (p["medida"], p["problema"]) for p in con_problema))
    calculadas.sort(key=lambda m: m["costo_por_tonelada"])

    acumulado = 0.0
    costo_acumulado = 0.0
    for orden, medida in enumerate(calculadas, start=1):
        acumulado += medida["tco2e_evitadas"]
        costo_acumulado += medida["costo_anual_neto"]
        medida["orden"] = orden
        medida["abatimiento_acumulado"] = round(acumulado, 1)
        medida["costo_anual_acumulado"] = round(costo_acumulado, 1)

    con_ahorro = [m for m in calculadas if m["ahorra_dinero"]]
    potencial_con_ahorro = sum(m["tco2e_evitadas"] for m in con_ahorro)
    resultado = {
        "tasa_descuento": tasa_descuento,
        "medidas": calculadas,
        "potencial_total": round(acumulado, 1),
        "potencial_con_ahorro": round(potencial_con_ahorro, 1),
        "costo_anual_total": round(costo_acumulado, 1),
        "costo_promedio_por_tonelada": round(costo_acumulado / acumulado, 1) if acumulado else 0.0,
        "medidas_con_problema": con_problema,
        "completo": not con_problema,
    }

    if brecha:
        brecha = float(brecha)
        seleccionadas = []
        suma = 0.0
        costo = 0.0
        for medida in calculadas:
            if suma >= brecha:
                break
            seleccionadas.append(medida["medida"])
            suma += medida["tco2e_evitadas"]
            costo += medida["costo_anual_neto"]
        resultado["plan_para_la_brecha"] = {
            "brecha": brecha,
            "medidas": seleccionadas,
            "abatimiento_logrado": round(suma, 1),
            "alcanza": suma >= brecha,
            "faltante": round(max(brecha - suma, 0.0), 1),
            "costo_anual_del_paquete": round(costo, 1),
            "costo_por_tonelada_del_paquete": round(costo / suma, 1) if suma else 0.0,
        }
        if con_problema:
            plan = resultado["plan_para_la_brecha"]
            plan["incompleto"] = True
            plan["medidas_fuera"] = [p["medida"] for p in con_problema]
            if not plan["alcanza"]:
                # Una medida que quedo fuera podria cerrar la brecha: no se puede concluir que no alcanza.
                plan["alcanza"] = None
            plan["nota"] = ("Quedaron fuera %d medida(s) por datos que faltan. Con ellas el paquete podria ser otro, "
                            "mas barato o suficiente: completa esos datos antes de decidir." % len(con_problema))
    return resultado
