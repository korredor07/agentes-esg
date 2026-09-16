---
name: plan-descarbonizacion
description: Armar el plan de reducción de emisiones con costos: qué medidas conviene hacer primero, cuánto cuesta cada tonelada evitada y qué paquete cubre la meta (curva MACC). Úsala cuando pregunten cómo reducir, qué inversión conviene, cuánto cuesta bajar emisiones, o cuando necesiten justificar un proyecto ante la gerencia.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Plan de descarbonización

Ordena las acciones posibles de la más barata a la más cara **por tonelada
evitada**. La sorpresa habitual: varias medidas tienen costo negativo, es decir
**ahorran dinero** mientras reducen emisiones.

## 1. Juntar las medidas candidatas

```bash
python .claude/motor/esg.py plantilla crear --tipo medidas
```

Por cada acción hacen falta cinco datos: inversión inicial, costo anual de
operación, ahorro anual, años de vida útil y toneladas de CO2e que evita al año.

Si la empresa no tiene las toneladas evitadas, ayúdala a estimarlas con la
huella ya calculada: por ejemplo, cambiar la caldera a gas reduce el consumo de
diésel en X litros al año → esos litros por su factor de emisión.

Ideas para empezar, según lo que salió grande en la huella:

| Si lo grande es… | Medidas típicas a evaluar |
|---|---|
| Electricidad | Iluminación LED, motores eficientes, solar para autoconsumo, contrato con energía renovable certificada |
| Combustible de calderas | Recuperación de calor, aislación, control de combustión, cambio de combustible |
| Flota | Rutas y carga optimizadas, mantenimiento, cambio a eléctrico donde el uso lo permite |
| Compras (alcance 3) | Cambiar proveedores o materiales, reducir merma, rediseñar envases |
| Residuos | Separación, compostaje, reducción en origen |

## 2. Construir la curva

```bash
python .claude/motor/esg.py meta plan
python .claude/motor/esg.py meta plan --brecha 1320 --tasa-descuento 0.1
```

Si ya se estimó la probabilidad de la meta (skill `metas-net-zero`), la brecha
se toma automáticamente de ahí.

El motor calcula, para cada medida:

- **Costo por tonelada** = (inversión anualizada + costo de operación − ahorros)
  ÷ toneladas evitadas al año.
- La **inversión anualizada** usa el factor de recuperación de capital, que
  reparte la inversión a lo largo de su vida útil con una tasa de descuento
  (10 % por defecto; pregúntale si su empresa usa otra).

## 3. Cómo se lo explicas

En este orden, breve:

1. «Hay X medidas que **ahorran dinero** y juntas evitan N toneladas al año:
   parte por esas.»
2. «Para llegar a la meta faltan M toneladas más; la siguiente medida cuesta
   $Y por tonelada.»
3. «El paquete completo cuesta $Z al año y cubre la brecha.»

Si el paquete no alcanza a cubrir la brecha, dilo sin adornos: hay que buscar
más medidas, cambiar el plazo de la meta o revisar el alcance. **No maquilles
el resultado.**

## 4. Cerrar el círculo

Con las medidas elegidas, vuelve a la skill `metas-net-zero` y recalcula la
probabilidad incluyéndolas como proyectos. Repite hasta que la meta sea
creíble (80 % o más). Ese plan —medidas, costo, probabilidad y supuestos— es a
la vez el plan de transición que piden los marcos de reporte y la mejor defensa
frente a una acusación de greenwashing.

## Cuidados

- Los costos salen de las cotizaciones que cargó la empresa: si son antiguas o
  «a ojo», el resultado también lo es. Dilo.
- Una medida con costo negativo no siempre se hace sola: puede faltar capital,
  permisos o tiempo. Pregunta qué la bloquea.
- No recomiendes comprar bonos de carbono como sustituto de reducir: no cuentan
  como reducción en las metas y son el terreno más riesgoso para afirmaciones
  públicas.
