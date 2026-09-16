---
name: huella-hidrica
description: Medir el agua de la empresa y su huella hídrica. Úsala cuando pidan huella hídrica, consumo o extracción de agua, indicadores de agua para un reporte (GRI 303), escasez hídrica, riesgo hídrico, cuando un cliente o un banco pregunte cuánta agua usan, o cuando pregunten por la obligación de informar las extracciones a la DGA en Chile.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Huella hídrica y gestión del agua

Con el agua no basta con sumar metros cúbicos. **Importa dónde y cuándo se
usa.** Un metro cúbico consumido en una cuenca del norte de Chile, donde casi
no queda agua disponible, pesa muchísimo más que el mismo metro cúbico
consumido en el sur de Brasil, donde sobra. Por eso este módulo hace dos cosas
distintas y hay que explicarlas por separado:

1. **La contabilidad**: cuánta agua entró, cuánta salió y cuánta se quedó. Es
   lo que pide el estándar de reporte GRI 303.
2. **El impacto**: cuánto pesa ese consumo según la escasez del lugar. Es la
   huella hídrica propiamente tal (ISO 14046, con el método AWARE).

## Las tres palabras que hay que dejar claras

La gente suele decir «consumo de agua» para todo, y eso confunde el reporte.

| Palabra | Qué significa | Ejemplo de una planta de alimentos |
|---|---|---|
| **Extracción** | Toda el agua que la empresa tomó: de la red pública, de un pozo, de un río, del mar o de un tercero. Da igual para qué la usó. | Los 28.500 m³ que marcan las boletas de la sanitaria |
| **Descarga** | El agua que devolvió y que ya no usa: al alcantarillado, a un río, al mar o a un tercero. | Los 24.000 m³ que se van al alcantarillado |
| **Consumo** | La que **se quedó**: se evaporó, se fue dentro del producto, la bebió la gente o los animales, o se regó. No vuelve. | 28.500 − 24.000 = **4.500 m³** |

La fórmula que usa el motor es `Consumo = Extracción − Descarga`, que es un
método de cálculo aceptado por GRI 303-5.

**Advierte siempre esta trampa:** la definición del estándar es más ancha que
esa resta. También cuenta como consumida el agua que la empresa **guardó** para
otro periodo y el agua que devolvió **tan contaminada que nadie más la puede
usar**. Si a la empresa le pasa alguna de esas dos cosas, la resta queda corta y
hay que ajustarla a mano; el motor lo advierte, pero no lo puede calcular solo.

**Y el dato que importa para la huella es el consumo, nunca la extracción.** El
agua que se devuelve al mismo lugar en condiciones de uso no genera escasez.

## Zona de estrés hídrico: qué es y cómo saberlo

Una **zona con estrés hídrico** es una cuenca donde el agua no alcanza para
todos los que la necesitan: las personas, las actividades productivas y los
ecosistemas. Puede ser por cantidad, por calidad o porque simplemente no hay
cómo llegar a ella.

Cómo averiguar si un sitio está en una:

1. Entra a **WRI Aqueduct Water Risk Atlas** (`wri.org/aqueduct`) o al **WWF
   Water Risk Filter**. Son las dos herramientas públicas que el propio GRI 303
   reconoce.
2. Ubica el sitio en el mapa y mira el indicador **«baseline water stress»**
   (estrés hídrico de referencia).
3. Si sale **alto (40–80 %)** o **extremadamente alto (más de 80 %)**, para el
   estándar el sitio está en zona con estrés hídrico: escribe `si` en la
   planilla.
4. El estándar también permite marcarlo por problemas de **calidad** o de
   **acceso** al agua aunque el mapa no lo clasifique así. Si es el caso, escribe
   `si` igual y **deja anotada la razón en la columna Notas**.

Si la persona no lo sabe todavía, que escriba `no se`. El motor lo separa y lo
reporta aparte, en vez de suponer.

> **No confundas dos cosas parecidas.** El «estrés hídrico» de Aqueduct es un
> indicador de riesgo de la cuenca. El **factor AWARE** es otra cosa: mide el
> impacto de cada metro cúbico consumido. **No se convierte uno en otro.**

## Qué exige el estándar de reporte (GRI 303)

GRI 303: Agua y efluentes 2018 es obligatorio para los reportes publicados
desde el 1 de enero de 2021. Tiene cinco divulgaciones:

| Código | Qué pide | ¿Lo calcula el motor? |
|---|---|---|
| **303-1** | Contar cómo se relaciona la empresa con el agua: de dónde la saca, qué impactos genera, cómo los aborda y cómo se hace cargo del contexto local | No: es un texto que se escribe |
| **303-2** | Qué estándares de calidad cumple el agua que devuelve y cómo se fijaron | No: es un texto que se escribe |
| **303-3** | **Extracción** total y por fuente (superficial, subterránea, de mar, producida, de terceros), más el desglose en zonas con estrés | Sí |
| **303-4** | **Descarga** total y por destino, en zonas con estrés, y qué sustancias prioritarias contiene | Sí, menos las sustancias |
| **303-5** | **Consumo** total, en zonas con estrés, y los cambios en el agua almacenada | Sí, menos el almacenamiento |

Los volúmenes se reportan en **megalitros (ML)**: 1 ML = 1.000 m³. El motor los
entrega en las dos unidades.

**Dos datos que el motor no puede completar y tú tienes que pedir:**

- **Agua dulce vs. otras aguas.** El estándar separa el agua con hasta 1.000
  mg/L de sólidos disueltos totales (dulce) del resto. La planilla no tiene
  columna de salinidad, así que ese desglose sale del análisis de laboratorio.
- **Sustancias prioritarias de preocupación** en la descarga: salen del
  monitoreo del efluente, no de esta planilla.

## Paso a paso

**1. Confirma la empresa y el periodo.** Normalmente el año calendario anterior.

**2. Crea la planilla si no existe y explícale qué llenar.**

```bash
python .claude/motor/esg.py plantilla crear --tipo agua
```

Queda en `datos/agua.xlsx`. Una fila por periodo, sitio y **origen del agua**:
si una planta saca agua de la red y además de un pozo, son dos filas.

| Dato | Dónde lo encuentra |
|---|---|
| Extracción de la red pública | Boletas de la sanitaria (vienen en m³) |
| Extracción de pozo o río | Lectura del flujómetro o del totalizador; si no hay, la estimación por horas de bombeo |
| Descarga al alcantarillado | Suele venir en la misma boleta de la sanitaria |
| Descarga a un cauce o al mar | Informes de monitoreo del efluente o la resolución que autoriza la descarga |
| Zona de estrés hídrico | WRI Aqueduct (ver más arriba) |

Si tiene boletas en PDF o fotos, **léelas tú y llena la planilla por ella**, y
confirma los valores antes de guardarlos. Para el detalle de la carga usa la
skill `cargar-datos`.

**3. Calcula la contabilidad.**

```bash
python .claude/motor/esg.py agua calcular --periodo 2025
```

Lee con atención `advertencias` y `problemas`:

- «la descarga es mayor que la extracción» → esa fila queda fuera del total.
  Casi siempre es agua lluvia, agua de otro sitio o agua guardada: hay que
  separarla en su propia fila.
- «no está definido si el sitio está en zona de estrés hídrico» → es la mitad
  de lo que pide el estándar. Insiste en cerrarlo.
- «no pude clasificar el origen» → pregúntale de dónde sale realmente esa agua.

**4. Pondera por la escasez del lugar.**

```bash
python .claude/motor/esg.py agua escasez --periodo 2025
```

La primera vez **no calcula nada**: te propone el factor AWARE del país y te
pide confirmarlo. Eso es a propósito. Explícale por qué:

- El factor AWARE dice cuánta agua queda disponible en ese lugar comparada con
  el promedio mundial. Va de 0,1 a 100. **Chile no agrícola es 45,5**: consumir
  1 m³ en Chile afecta la disponibilidad como consumir 45,5 m³ en el lugar de
  referencia del método.
- Pero **ese 45,5 es un promedio de todo el país**, y AWARE se define por
  cuenca y por mes. En Chile la diferencia entre enero (84,9) y junio (5,19) es
  de más de 16 veces. Para una faena concreta, el número de su cuenca puede ser
  muy distinto.

Entonces:

```bash
# si el promedio del país le sirve (por ejemplo, para una primera estimación)
python .claude/motor/esg.py agua escasez --periodo 2025 --confirmar

# si ya tiene el factor de su cuenca, o el del mes que corresponde
python .claude/motor/esg.py agua escasez --periodo 2025 --factor 63.1
```

Opciones útiles: `--agregacion agricola` si el agua va a riego (por defecto usa
la no agrícola, que es la de industria, minería y servicios), `--mes 3` si el
consumo se concentra en un mes, y `--pais PE` si el sitio no está en el país del
perfil.

Si el país no está en el catálogo, el motor **no inventa un factor**: te dice
dónde bajarlo (el conjunto de datos oficial en Zenodo o el sitio de WULCA) para
que se lo pases con `--factor`.

**5. Explícale el resultado en palabras simples.** En este orden:

1. Cuánta agua extrajo y cuánta devolvió.
2. Cuánta **se quedó** (el consumo) y por qué esa es la cifra que importa.
3. Cuánto de todo eso ocurrió en zonas con estrés hídrico.
4. Cuánto pesa ese consumo según la escasez del lugar, si se calculó.
5. Qué falta para que el dato sirva ante un tercero.

**6. Genera el informe.**

```bash
python .claude/motor/esg.py agua informe --periodo 2025
```

Queda en `reportes/` como HTML: se abre con doble clic y se imprime a PDF desde
el navegador (Ctrl+P). Dile dónde quedó.

**7. Si la empresa es chilena y saca agua con derechos de aprovechamiento,
revisa la obligación con la DGA.**

```bash
python .claude/motor/esg.py agua dga
```

**8. Respalda la evidencia** si el número se va a usar ante terceros:

```bash
python .claude/motor/esg.py evidencia registrar --archivo datos/agua.xlsx --descripcion "Agua 2025"
```

## La obligación chilena: monitorear las extracciones (MEE)

En Chile, quien tiene derechos de aprovechamiento de agua debe **medir cuánta
agua saca realmente y transmitírselo a la Dirección General de Aguas (DGA)**.
Se llama Monitoreo de Extracciones Efectivas.

**Por qué importa de verdad, y no es solo un trámite:** con la reforma del
Código de Aguas (Ley 21.435), los derechos **se extinguen si no se usan** —5
años en los consuntivos, 10 en los no consuntivos—. El monitoreo es justamente
la prueba del uso efectivo. Dejar de transmitir no solo arriesga una multa:
alimenta la evidencia de que el derecho no se está usando. Desde la Ley 21.740
(2025) la DGA además puede ordenar la paralización inmediata de extracciones no
autorizadas.

**Hay dos reglamentos distintos**, y si la empresa saca agua de las dos formas
le aplican los dos:

- **Aguas subterráneas** (pozos, norias, sondajes): Resolución DGA 1238/2019.
- **Aguas superficiales** (ríos, canales, esteros): Decreto MOP 53/2020.

**Lo que decide todo es la resolución regional.** Ella activa la obligación en
cada zona, fija los rangos de caudal que asignan el estándar (Mayor, Medio,
Menor o Caudales Muy Pequeños) y marca desde cuándo corren los plazos, que se
cuentan desde su publicación en el Diario Oficial.

> **El motor no puede decirle qué estándar le toca.** No existen rangos de
> caudal a nivel nacional. Hacen falta dos datos: el **caudal total sumado de
> todos los derechos que se ejercen en la misma obra de captación** (no de cada
> derecho por separado) y la **resolución regional aplicable**. Si no la tiene,
> mándalo a `dga.mop.gob.cl` → «Monitoreo de Extracciones Efectivas». **Nunca
> supongas el estándar ni el plazo.**

La acción `agua dga` entrega la lista de verificación completa: a quién aplica,
los cuatro estándares con sus plazos, qué equipos exige cada uno, cómo se
transmite, cómo se registra la obra (con ClaveÚnica, código de obra y un código
QR que hay que exhibir en la obra) y qué queda fuera de lo que el motor puede
determinar.

## Detalles que hacen la diferencia

- **Una fila por origen.** Si mezclas el pozo y la red en una sola fila, la
  divulgación 303-3 queda mal y no se puede arreglar después.
- **Usa el mismo nombre de sitio** en todas las planillas, así los informes
  cuadran entre sí.
- **Mes a mes es mejor que el año completo** cuando el uso de agua es
  estacional (riego, temporada de proceso): con el factor mensual el resultado
  puede cambiar más de diez veces.
- **Nunca inventes un factor AWARE**, ni un umbral de estrés hídrico, ni un
  plazo de la DGA. Si falta el dato, dilo, regístralo como brecha y ofrece
  buscarlo en la fuente oficial con el agente `agente-investigador`.
- **Declara siempre la versión y la agregación** que usaste (por ejemplo: AWARE
  2.0, no agrícola, anual). Mezclar versiones da resultados inconsistentes.
- **Para comparar entre años**, mira el consumo y la huella de escasez, no solo
  la extracción: una empresa puede extraer lo mismo y consumir mucho menos.

## Cierre

Termina siempre diciendo: qué se obtuvo, dónde quedó el archivo, qué tan sólido
es el dato y cuál es el siguiente paso. Y recuerda que esto es un apoyo de
gestión: para una declaración oficial, un reporte público o una auditoría, los
datos deben verificarse, y si se va a publicar una comparación de huella
hídrica, ISO 14046 exige además una revisión crítica por un panel externo.
