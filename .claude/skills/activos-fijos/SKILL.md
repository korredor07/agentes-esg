---
name: activos-fijos
description: Activos fijos y depreciación en Chile: en cuántos años se deprecia cada bien según la tabla del SII, depreciación normal o acelerada, corrección monetaria y resumen de la cartera (inversión, depreciación del ejercicio y valor libro). Úsala cuando pregunten cuánto dura un bien para el SII, cómo depreciar una camioneta o una máquina, qué valor tienen los equipos en los libros, o cuándo conviene renovar la maquinaria.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Activos fijos y depreciación

## Qué es depreciar, en una línea

Un bien que dura años —una camioneta, un galpón, una cámara de frío— **no se
anota como gasto el año en que se compra**: su costo se reparte a lo largo de
los años en que se usa. Ese reparto es la depreciación.

Tres ideas que conviene tener a mano cuando expliques:

- **Vida útil**: cuántos años dura el bien *para efectos tributarios*. No la
  elige la empresa: la fija el SII en una tabla (Resolución Exenta N° 43 de
  2002, más la Res. Ex. N° 56 de 2021 que agregó los vehículos eléctricos).
- **Valor libro**: lo que le queda al bien por depreciar. Es lo que aparece en
  la contabilidad, no lo que el bien vale si se vende.
- **La cuenta empieza cuando el bien se usa**, no cuando se compra. Si la
  máquina llegó en abril, ese primer año se deprecian solo 9 meses.

Lo que **no** se deprecia: los terrenos (no se desgastan), los intangibles como
un software o una marca (no son bienes físicos) y las mercaderías o materias
primas (son para vender, no para usar por años). Si alguien compró un inmueble,
hay que separar cuánto vale el terreno y cuánto la construcción: solo la
construcción se deprecia.

## Para qué sirve esto en ESG

Esta es la razón por la que el módulo existe, y conviene decirla:

> Saber qué equipos tiene la empresa, desde cuándo y cuánto les queda de vida
> útil es la base para planificar el recambio. Un equipo que ya cumplió su vida
> útil es el mejor candidato a ser reemplazado por uno más eficiente, y ese
> recambio —motores, calderas, frío, flota— es la columna vertebral del plan de
> reducción de emisiones.

Cuando termines un resumen de cartera, mira la lista de equipos por renovar y
conéctala con las skills `plan-descarbonizacion` (cuánto cuesta cada tonelada
evitada) y `huella-carbono` (dónde está el consumo grande).

## 1. Consultar en cuántos años se deprecia un bien

```bash
python .claude/motor/esg.py activos vida-util --bien camioneta
python .claude/motor/esg.py activos vida-util --bien camioneta --actividad agricola
```

Escríbelo como lo diría la persona: `camioneta`, `computador`, `galpón`,
`cámara de frío`, `tractor`, `maquinaria`. El motor devuelve **todas** las
opciones parecidas de la tabla del SII con su código, sus años y su fuente.

- Si hay varias opciones, **no elijas tú**: muéstralas y pregunta cuál calza.
  Por ejemplo, «herramientas» puede ser pesadas (8 años) o livianas (3 años).
- Si no encuentra nada, el motor lo dice. **No inventes una vida útil**: ofrece
  preguntarle al contador en qué ítem de la tabla clasifica ese bien.

La tabla cargada está en `.claude/motor/datos/vida_util_sii.csv` y cada fila
trae la resolución de la que sale y la fecha en que se verificó.

## 2. Llenar la planilla de activos

El módulo lee `datos/activos_fijos.xlsx`. Si no existe, **el motor la crea vacía
la primera vez que se la pide** y avisa dónde quedó:

```bash
python .claude/motor/esg.py activos cartera
```

Columnas de la planilla (no cambies los títulos):

| Columna | Qué se escribe |
|---|---|
| Nombre del activo | Como le dicen en la empresa. Ej: *Camioneta Hilux PPU ABCD-12* |
| Bien según la tabla del SII | En palabras simples: camioneta, computador, galpón, cámara de frío |
| Actividad | `generico` (por defecto) o `agricola` |
| Categoría | Agrupación propia para los totales: flota, edificios, equipos, oficina |
| Sitio | Dónde está. Usa el mismo nombre que en la planilla de sitios |
| Fecha de compra | AAAA-MM-DD |
| Fecha de puesta en uso | Solo si empezó a usarse después de comprarse |
| Valor de compra | En pesos, sin el IVA que la empresa recupera |
| Condición | nuevo, usado o importado |
| Método | normal, acelerada, 5_bis o propyme |
| Vida útil normal (años) | Vacía: la busca el motor. Llénala solo si el contador indica otra |
| Estado | en uso, vendido o dado de baja |
| Notas | Lo que quieran recordar |

Si la persona tiene el listado en otro formato (una planilla propia, el detalle
del contador, fotos de facturas), **léelo tú y llena la planilla por ella**, y
confirma los valores antes de guardar.

## 3. Depreciar

```bash
# un activo suelto
python .claude/motor/esg.py activos depreciar --valor 18500000 --bien camioneta --anio-inicio 2024 --mes-inicio 5
# con depreciación acelerada
python .claude/motor/esg.py activos depreciar --valor 24000000 --bien "camara de frio" --metodo acelerada
# todos los activos de la planilla
python .claude/motor/esg.py activos depreciar
```

Devuelve la tabla año por año: cuánto se deprecia, cuánto se lleva acumulado y
con qué valor libro queda el bien.

### Normal o acelerada: cómo se lo explicas

| | Depreciación normal | Depreciación acelerada |
|---|---|---|
| Años | Los que fija la tabla del SII | **Un tercio** de esos años, sin decimales y con mínimo 1 |
| Ejemplo | Camioneta: 7 años | Camioneta: 2 años |
| Requisitos | Ninguno especial | Bien **nuevo comprado o importado** (el importado sí puede ser usado) y vida útil normal de **3 años o más** |

La diferencia práctica: la acelerada reparte el mismo costo en menos años, así
que **rebaja más la utilidad tributaria los primeros años y menos después**. No
regala plata: adelanta el efecto. Dos cosas que hay que decir siempre:

1. Para los registros empresariales del artículo 14 solo se considera la
   depreciación **normal**; la diferencia entre la acelerada y la normal se
   controla aparte y queda afecta a los impuestos finales.
2. **La elección es de la empresa con su contador**, porque depende de cómo
   viene el resultado del año y de qué régimen tributario tiene.

Hay dos regímenes más, y el motor los calcula si se los piden:

- `--metodo 5_bis --ingresos-uf 90000`: el artículo 31 N° 5 bis. Con ingresos
  promedio de hasta 25.000 UF la vida útil es de **1 año**; entre 25.000 y
  100.000 UF es **un décimo** de la vida útil normal (mínimo 1 año).
- `--metodo propyme`: en el régimen Pro Pyme (artículo 14 letra D N° 3) el bien
  se deprecia **entero en el mismo ejercicio** en que se compra o fabrica,
  siempre que **esté pagado**. Estas empresas no aplican corrección monetaria.

## 4. Corrección monetaria

La inflación desordena los libros: un galpón comprado hace cinco años vale, en
pesos de hoy, más de lo que dice la factura. La corrección monetaria **actualiza
el valor de los bienes con la variación del IPC** para que la contabilidad esté
en pesos comparables. No es una ganancia: solo pone el valor al día.

```bash
python .claude/motor/esg.py activos depreciar --valor 18500000 --bien camioneta --anio-inicio 2023 --correccion 2025
python .claude/motor/esg.py activos cartera --anio 2025 --corregir
```

Dos reglas, y el motor elige la que corresponde:

- Bien que **ya estaba** en la empresa al empezar el año: se actualiza con el
  mismo porcentaje del capital propio inicial (para el ejercicio 2025, **3,4 %**).
- Bien **comprado durante el año**: se usa el factor del mes de la compra (marzo
  de 2025, por ejemplo, es 1,022).
- Si el porcentaje resulta negativo, **se iguala a cero**.

El orden importa: primero se actualiza el valor y recién sobre ese valor
actualizado se calcula la cuota del año.

**El motor solo trae los factores oficiales que están verificados (ejercicio
2025).** Para otro año pedirá el porcentaje —`--porcentaje 3.4`— en vez de
inventarlo. Es correcto que lo pida: dile a la persona que se lo consulte a su
contador o lo busque en el sitio del SII.

## 5. Resumen de la cartera e informe

```bash
python .claude/motor/esg.py activos cartera --anio 2025
python .claude/motor/esg.py activos informe --anio 2025
```

El resumen entrega: cuánto se invirtió en total, cuánto se deprecia este
ejercicio, con qué valor libro queda la cartera y qué equipos ya cumplieron o
están por cumplir su vida útil. El informe queda en `reportes/` como HTML: se
abre con doble clic y se imprime a PDF con Ctrl+P.

Explícalo en este orden:

1. «La empresa tiene N activos por $X; este año la depreciación es $Y.»
2. «El valor libro de la cartera es $Z, un W % ya está depreciado.»
3. «Estos equipos ya cumplieron su vida útil: son los primeros candidatos a
   reemplazo por unos más eficientes.»
4. Las filas que el motor no pudo calcular y qué falta en cada una.

## Lo que este módulo NO tiene verificado

Dilo cuando corresponda, en vez de rellenar el hueco:

- De la tabla del SII están cargadas la **nómina genérica** y la **nómina
  agrícola**. Las nóminas de construcción, minería, transporte marítimo y
  terrestre, energía eléctrica y telecomunicaciones quedaron con lectura parcial
  en la investigación y **no están cargadas**.
- Algunos ítems de detalle de la nómina genérica tampoco se pudieron leer
  completos.
- La vida útil de los **viñedos** depende de la variedad (entre 11 y 23 años):
  la tabla la trae sin número y el motor pide confirmarla.
- Que el bien totalmente depreciado quede en **$1** está verificado para el caso
  de la Ley 21.256; como regla general es práctica establecida pero no quedó
  confirmada. El motor la usa por defecto y lo advierte.
- El **crédito por activo fijo del artículo 33 bis** no se calcula aquí.
- Los regímenes transitorios de depreciación instantánea de las leyes 21.210 y
  21.256 **ya no están vigentes** para compras nuevas: sus ventanas cerraron el
  31.12.2021 y el 31.12.2022.

## Cierre obligatorio

Termina siempre dejando esto claro:

> Este cálculo es **apoyo de gestión, no asesoría tributaria ni contable**. La
> vida útil y las fórmulas salen de la tabla y de los artículos que el motor
> cita en cada resultado, pero **no reemplaza a un contador**: qué régimen usar,
> cómo clasificar un bien y cómo declararlo lo decide la empresa con su asesor.

Y si el número se va a usar ante el SII, un banco o una auditoría, respalda los
documentos:

```bash
python .claude/motor/esg.py evidencia registrar --archivo datos/activos_fijos.xlsx --descripcion "Activos fijos 2025"
```
