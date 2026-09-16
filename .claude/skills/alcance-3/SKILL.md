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
python .claude/motor/esg.py plantilla crear --tipo alcance3
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
- **Escribe el nombre exacto del catálogo** en la columna «Recurso o actividad».
  La tabla de abajo dice cuál usar; si dudas, consulta el catálogo antes de
  calcular (ver «Cómo averiguar el nombre»).

### Qué compro → qué nombre escribo

El nombre se escribe **tal cual**, en minúsculas, en la columna «Recurso o
actividad». Todos van en **USD** y son alcance 3.

| Lo que compra la empresa | Nombre que se escribe | kg CO2e por USD |
|---|---|---|
| Maíz, trigo, arroz u oleaginosas **en grano**, sin procesar | `gasto agricultura` | 0,848 |
| Pan, pasteles o galletas comprados ya hechos | `gasto alimentos` | 0,253 |
| Carne de vacuno | `gasto carne bovina` | 2,893 |
| Leche, queso, mantequilla, crema, yogurt | `gasto lacteos` | 1,724 |
| Bebidas, jugos, aguas envasadas | `gasto bebidas` | 0,214 |
| Botellas, bolsas, potes, tapas, envases plásticos | `gasto envases plastico` | 0,579 |
| Cajas de cartón, estuches, bandejas | `gasto envases carton` | 0,479 |
| Resinas, film, polietileno a granel | `gasto plasticos` | 1,045 |
| Cemento, hormigón, mortero | `gasto cemento` | 3,924 |
| Acero, fierro, perfiles, estructuras metálicas | `gasto acero` | 0,787 |
| Obras, ampliaciones, remodelaciones | `gasto construccion` | 0,224 |
| Químicos, solventes, detergentes industriales, aditivos | `gasto quimicos` | 1,184 |
| Fertilizantes, urea, salitre, abonos | `gasto fertilizantes` | 1,137 |
| Medicamentos, insumos farmacéuticos | `gasto farmaceuticos` | 0,099 |
| Telas, hilados, géneros | `gasto textiles` | 0,507 |
| Ropa de trabajo, uniformes, calzado de seguridad | `gasto vestuario` | 0,120 |
| Escritorios, sillas, estanterías, muebles | `gasto muebles` | 0,240 |
| Resmas, cuadernos, artículos de oficina | `gasto papeleria` | 0,296 |
| Impresión de etiquetas, folletos, catálogos | `gasto imprenta` | 0,236 |
| Notebooks, servidores, impresoras, teléfonos | `gasto computadores` | 0,058 |
| Licencias, suscripciones, ERP, antivirus | `gasto software` | 0,080 |
| Soporte informático, desarrollo, hosting | `gasto servicios ti` | 0,089 |
| Telefonía, internet, plan de datos | `gasto telecomunicaciones` | 0,075 |
| Asesorías, auditorías, contabilidad externa, marketing | `gasto consultoria` | 0,078 |
| Abogados, notaría, estudios jurídicos | `gasto legal` | 0,041 |
| Seguros | `gasto seguros` | 0,051 |
| Comisiones bancarias, mantención de cuentas | `gasto banca` | 0,059 |
| Personal por faena, reemplazos, empresas de aseo | `gasto personal temporal` | 0,051 |
| Arriendo de oficinas, locales, salas de venta | `gasto arriendo oficinas` | 0,246 |
| Maquinaria, hornos, amasadoras, grúa horquilla | `gasto maquinaria` | 0,228 |
| Motores, bombas, tableros, equipos eléctricos | `gasto equipos electricos` | 0,152 |
| Pasajes de avión sin kilómetros conocidos | `gasto transporte aereo` | 0,644 |
| Fletes por camión sin toneladas-kilómetro | `gasto transporte camion` | 0,595 |
| Fletes marítimos sin toneladas-kilómetro | `gasto transporte maritimo` | 0,816 |
| Bodegaje, arriendo de bodega, frío de terceros | `gasto almacenamiento` | 0,244 |
| Retiro de basura, gestión de residuos | `gasto residuos` | 0,988 |
| Cuenta del agua sin metros cúbicos | `gasto agua` | 0,578 |
| Combustible del que solo se tiene el monto | `gasto combustibles` | 0,270 |

**Lo que no está en la tabla no tiene factor.** Tres casos que aparecen seguido:

- **Harina.** Es trigo molido (código NAICS 311211, molienda de harina) y ese
  factor **no está en el catálogo**. No uses `gasto alimentos`: es el de las
  panaderías. Tampoco `gasto agricultura` como si fuera exacto: es el del grano,
  no el del molido.
- **Azúcar, frutas y verduras.** Tampoco tienen factor propio en el catálogo.
- **Cualquier compra que no calce con una fila de la tabla.**

Para esos casos, en este orden:

1. **Pedirle el dato al proveedor** (su huella por kilo): es lo mejor y no
   depende de un promedio de otro país. Usa la skill `proveedores`.
2. **Buscar el factor oficial** con el `agente-investigador` y agregarlo al
   catálogo con su fuente y su año.
3. Solo si la persona lo acepta, usar el factor más cercano como
   **aproximación declarada** (por ejemplo, `gasto agricultura` para la harina)
   y dejarlo escrito como supuesto en la columna de notas y en el informe.

### Cómo averiguar el nombre

```bash
python .claude/motor/esg.py huella factores --recurso trigo
```

Busca primero por nombre y, si no encuentra, por la descripción del factor: con
`trigo` devuelve `gasto agricultura`. **Si no devuelve nada (por ejemplo, con
`harina`), es que no hay factor**: no fuerces el más parecido sin decirlo. También sirve `--uso gasto` para ver los
38 nombres completos, `--alcance 3` y `--pais CL`. Cada resultado trae la fuente,
el año, la unidad y qué cubre.

Si escribes un nombre que no existe, el error te devuelve los nombres parecidos
en vez de dejarte adivinando. **No inventes un nombre nuevo ni elijas por ti:**
muéstrale las alternativas a la persona y que ella confirme cuál describe lo que
compra.

**6. Calcula y analiza el punto caliente.**

```bash
python .claude/motor/esg.py huella calcular --periodo 2025
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
