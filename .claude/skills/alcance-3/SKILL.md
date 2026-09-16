---
name: alcance-3
description: Estimar el alcance 3 (cadena de valor) de la huella de carbono: compras, fletes, viajes, residuos, agua y uso de productos. Úsala cuando pidan alcance 3, emisiones indirectas, huella de la cadena de suministro, o cuando un cliente grande o una norma europea les pida datos de sus proveedores.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Alcance 3 — la cadena de valor

En la mayoría de las empresas el alcance 3 es **la mayor parte de la huella**
(a menudo 70–90 %). También es el más difícil de medir, así que el objetivo no
es precisión perfecta: es **saber dónde está lo grande** y mejorar desde ahí.

## Las 15 categorías, en cristiano

| N.º | Nombre | En palabras simples |
|---|---|---|
| 1 | Bienes y servicios comprados | Todo lo que la empresa compra para operar |
| 2 | Bienes de capital | Máquinas, vehículos, edificios que compró |
| 3 | Combustibles y energía (no 1 ni 2) | Producir y transportar el combustible y la electricidad que usa |
| 4 | Transporte aguas arriba | Fletes que le traen insumos |
| 5 | Residuos | Basura y aguas servidas que genera |
| 6 | Viajes de negocios | Vuelos, hoteles, taxis |
| 7 | Traslado de trabajadores | Cómo llegan al trabajo |
| 8 | Activos arrendados (arriba) | Lo que arrienda y usa |
| 9 | Transporte aguas abajo | Fletes con los que despacha sus productos |
| 10 | Procesamiento de lo vendido | Lo que otro hace con su producto |
| 11 | Uso de lo vendido | Energía que consume el producto al usarse |
| 12 | Fin de vida de lo vendido | Qué pasa con el producto y su envase |
| 13 | Activos arrendados (abajo) | Lo que arrienda a terceros |
| 14 | Franquicias | Emisiones de sus franquiciados |
| 15 | Inversiones | Emisiones de lo que financia |

**No hace falta medirlas todas.** Se reportan las relevantes y se explica por
qué las otras no lo son.

## Paso a paso

**1. Decide qué categorías importan** según el negocio. Preguntas rápidas:

- ¿Compra mucha materia prima? → categoría 1 (casi siempre la mayor).
- ¿Despacha o exporta productos? → 4 y 9.
- ¿Viajan por trabajo? → 6.
- ¿Genera residuos importantes? → 5.
- ¿Su producto consume energía al usarse? → 11.
- ¿Tiene franquicias, arriendos o inversiones? → 8, 13, 14, 15.

**2. Crea la planilla y explícale cómo llenarla.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" plantilla crear --tipo alcance3
```

**3. Elige el mejor método disponible para cada línea** (en este orden):

1. **Dato del proveedor**: el proveedor entrega su huella real por producto. Es
   el mejor. Para pedirlo usa la skill `proveedores`.
2. **Por actividad**: toneladas × kilómetros de un flete, pasajeros × kilómetros
   de un vuelo, toneladas de residuos, m3 de agua. Es lo habitual y sirve bien.
3. **Por gasto**: cuánto dinero se gastó en cada tipo de compra. Es el último
   recurso: sirve para ordenar prioridades, no para fijar metas.

**4. Para fletes**, con toneladas y kilómetros basta: el motor calcula las
toneladas-kilómetro. Si no conocen la distancia, ayúdales a estimarla entre
ciudades o puertos y **anótalo como supuesto** en la columna de notas.

**5. Para el método por gasto**, los factores están en dólares de 2022 de la
economía de Estados Unidos. Entonces:

- Convierte el gasto a dólares con el tipo de cambio promedio del año y **deja
  escrito el valor usado**.
- Adviértele que es una estimación gruesa: una empresa eficiente y una
  ineficiente que gastan lo mismo dan el mismo resultado.
- Úsalo para descubrir dónde está el bulto, no para prometer reducciones.

**6. Calcula y analiza el punto caliente.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" huella calcular --periodo 2025
```

El resultado incluye `por_categoria_alcance3` y las mayores fuentes. Con eso:

- Muéstrale la **regla 80/20**: qué dos o tres categorías explican la mayoría.
- Propón mejorar el dato **solo** de esas (pedir datos al proveedor, medir mejor).
- Para el resto, la estimación es suficiente por ahora.

**7. Informe y cierre.** Genera el informe con `huella reporte`, indica qué
categorías se incluyeron, cuáles se excluyeron y por qué, y qué supuestos se
usaron. Esa transparencia es lo que revisa un auditor o un cliente exigente.

## Advertencias

- **Nunca sumes dos veces lo mismo**: el combustible de camiones propios es
  alcance 1, no categoría 4; la electricidad comprada es alcance 2, no
  categoría 3.
- Los factores de transporte, viajes, residuos y agua vienen del Reino Unido
  (DESNZ) y los de gasto de Estados Unidos (EPA): son referencias
  internacionales, no valores locales. Dilo en el informe.
- Si una categoría no se puede estimar con lo que hay, **dilo**: en un reporte
  serio se declara qué queda fuera y por qué.
