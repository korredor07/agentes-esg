---
name: cadena-frio
description: Revisar los registros de temperatura de la cadena de frío: temperatura cinética media (MKT), excursiones fuera de rango y qué exige la norma chilena para alimentos congelados, refrigerados y medicamentos. Úsala cuando pregunten si se rompió la cadena de frío, cuando haya que revisar un registrador de temperatura, cuando un cliente o la autoridad pida el registro de un envío, o cuando pregunten a qué temperatura hay que guardar algo.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Cadena de frío

## Por qué el promedio engaña

El daño que sufre un producto por calor **no crece en línea recta con la
temperatura: crece exponencialmente**. Dos horas a 14 °C hacen mucho más daño
que el que compensan dos horas a 6 °C.

Por eso las farmacopeas no usan el promedio, usan la **temperatura cinética
media (MKT)**: la temperatura constante que habría causado el mismo daño que
toda la serie real. Y es **siempre igual o mayor que el promedio**.

El caso que lo explica todo:

| | Bodega medida durante 12 meses |
|---|---|
| Promedio simple | **24,0 °C** → parece cumplir holgado un límite de 25 °C |
| Temperatura cinética media | **25,02 °C** → **incumple** |

Un informe hecho con el promedio habría dicho que todo estaba bien.

## 1. Consigue las lecturas

Casi todos los registradores (los data loggers de las cámaras y los camiones)
exportan un CSV. Pídeselo a la persona y pégalo en la planilla:

```bash
python .claude/motor/esg.py frio plantilla
```

**Lo importante: las lecturas tienen que estar a intervalos regulares.** Si el
registrador midió cada 15 minutos, todas deben ser cada 15 minutos. Mezclar
intervalos sin ponderarlos sesga el resultado, y el motor lo advierte.

Pregunta también **dónde estaba el sensor**: la temperatura del aire de la
cámara y la del centro del producto no son lo mismo, y varios artículos de la
norma chilena exigen la del centro de la masa.

## 2. Averigua qué exige la norma

**No hay una sola temperatura de «refrigerado».** El Reglamento Sanitario de los
Alimentos fija una por tipo de producto y situación:

```bash
python .claude/motor/esg.py frio limites --producto "alimento congelado" --situacion "transporte local"
```

Lo más usado, todo del DS 977/96 (Reglamento Sanitario de los Alimentos):

| Producto y situación | Temperatura | Artículo |
|---|---|---|
| Congelados: cámara de almacenamiento | −18 °C o menos, con registro continuo | 189 |
| Congelados: transporte interurbano | −18 °C, se tolera hasta **−15 °C** por poco tiempo | 190 |
| Congelados: transporte local y exhibición | nunca por sobre **−12 °C** | 191 y 192 |
| Aves faenadas y trozadas | 2 °C al enfriar, hasta 6 °C en el punto de venta | 286 |
| Cecinas crudas y cocidas | 0 a 6 °C | 302 y 303 |
| Comidas preparadas frías | máximo 5 °C | 466 |
| Comidas preparadas calientes | **65 °C uniforme y permanente** (aquí el riesgo es enfriarse) | 466 |
| Pescados, mariscos y carnes en ferias | 0 a 5 °C toda la jornada | 4 letra d |
| Medicamentos refrigerados | 2 a 8 °C (Norma Técnica 208 del MINSAL) | Decreto Ex. 48/2019 |

Sin lista completa: pídela con `frio limites` sin argumentos.

**Si el producto no está en la tabla, dilo.** No inventes una temperatura: hay
que buscar el artículo que le corresponde. Una temperatura equivocada aquí puede
liberar comida que no está apta.

## 3. Revisa

```bash
python .claude/motor/esg.py frio revisar --registro "Camara 1 enero" --producto "alimento congelado" --situacion "transporte local" --minutos-por-lectura 15
```

O con el rango directo, si lo sabes:

```bash
python .claude/motor/esg.py frio revisar --temperaturas "4.0 4.5 5.0 12.0 14.0 5.5" --minimo 2 --maximo 8 --minutos-por-lectura 60
```

Devuelve: la MKT, el promedio (para que se vea la diferencia), cada excursión
con cuánto duró y qué tan lejos llegó, y el porcentaje de lecturas fuera.

## 4. Cómo se lee el resultado

Se miran **tres cosas a la vez**, y cumplir una no borra las otras:

1. **La MKT está dentro del límite** del período completo.
2. **Cada excursión duró menos** de lo tolerado (típicamente 24 h, pero depende
   del producto).
3. **No hubo picos** por sobre el máximo absoluto.

Frase para explicarlo:

> «Hubo una excursión de tres horas que llegó a 14 °C. La temperatura cinética
> media del período quedó en 7,2 °C, todavía bajo los 8 °C. Eso es información
> útil, pero **no es una liberación**: quién decide si el producto sirve es
> quien tiene el registro sanitario, con sus datos de estabilidad.»

**Esto es lo más importante de toda la skill:** el motor describe lo que pasó
con la temperatura. **No decide si el lote se libera o se rechaza.** Esa decisión
es del titular del registro sanitario. Dilo siempre, sin excepción.

## Vida útil a otra temperatura

```bash
python .claude/motor/esg.py frio vida-util --vida-referencia 20 --temperatura-referencia 4 --temperatura 8 --q10 2.5
```

Aplica la regla Q10: por cada 10 °C de más, el deterioro se multiplica por Q10.
**El Q10 lo tiene que aportar la empresa**, de sus estudios de estabilidad
(suele estar entre 2 y 3 en alimentos, pero es propio de cada producto). El
motor **se niega a inventarlo**, y hace bien: un Q10 equivocado aquí puede
liberar producto que no está apto.

## Qué no está verificado

Dilo cuando corresponda, en vez de rellenar el hueco:

- Los rangos de la **Norma Técnica 208** (medicamentos refrigerados, 2–8 °C) y
  las definiciones de la **USP ⟨659⟩** vienen de fuentes secundarias: el texto
  oficial no fue accesible. Antes de usarlos para una decisión sanitaria hay que
  confirmarlos en el documento original.
- La USP propuso bajar el rango de temperatura ambiente controlada de 20–25 °C a
  **15–25 °C**, pero no se pudo confirmar si ya es texto oficial.
- El **rango de congelados de la NT 208** no está confirmado.
- No hay valores por defecto de Q10 ni de energía de activación por producto, y
  no los va a haber: son del fabricante.

## Cierre

Termina siempre con: qué dicen los registros, contra qué norma se comparó, qué
pasó exactamente, y que la decisión sobre el producto la toma quien tiene el
registro sanitario. Si el resultado va a un cliente o a la autoridad, respalda
el archivo original del registrador con la skill `evidencias`.
