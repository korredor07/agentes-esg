# Prueba E2E con el trabajo terminado — 16 de septiembre de 2026

> **En corto:** los agentes funcionan en la mayoría de los casos probados. En la
> última ronda de conversaciones pasaron **53 de 57 chequeos** (nota medida
> **4,7 de 5**). Los números y las normas salieron bien en todos los chequeos.
> Fallaron cuatro chequeos de flujo: dos registros que no se hicieron
> (capacitación y prospecto) y dos delegaciones en agentes (finanzas y CRM).
>
> **Después, una revisión independiente del código** (sección 7) encontró en dos
> pasadas cerca de 45 problemas que la prueba no vio, algunos graves: plazos de
> la Ley Karin mal calculados en denuncias derivadas y filas de ejemplo de las
> plantillas que podían entrar a la huella. Están corregidos, con pruebas. Por
> eso la nota que me pongo baja a **3,5 de 5** (provisional, sección 1).

Este documento dice qué se probó, cómo, qué salió, qué se corrigió y qué sigue
abierto. Los números son los que entregaron los scripts de la prueba: no están
redondeados a favor.

---

## 1. La nota

| | Nota | De dónde sale |
|---|---|---|
| **Medida (ronda 2)** | **4,7 / 5** (93,9 / 100) | 53 de 57 chequeos automáticos, con la rúbrica de la sección 5 |
| Medida (ronda 1, antes de corregir) | 3,8 / 5 (76,9 / 100) | 44 de 57 chequeos |
| Mi nota para la versión de la ronda 2, después de la revisión de código | 3 / 5 | Tenía plazos legales mal calculados y datos inventados que podían entrar a los cálculos |
| **La que me pongo hoy** (versión `cc9868d`) | ★★★½ **3,5 / 5**, provisional | Lo encontrado está corregido, pero nada nuevo lo probó en conversaciones ni en una tercera revisión |

Por qué no me pongo 4,7:

- La revisión independiente del código (sección 7) encontró problemas graves
  que los 57 chequeos no veían. La nota medida sobrestimaba la calidad.
- Cada pasada de revisión encontró más de 20 problemas, también dentro de las
  correcciones de la pasada anterior. No hubo una tercera pasada: es razonable
  suponer que quedan más.
- Después de la ronda 2 aparecieron **18 problemas más** (17 al revisar las
  conversaciones y 1 al revisar la capa 1), y después la revisión de código.
  Están corregidos y tienen pruebas unitarias, pero **ninguna conversación
  nueva** los volvió a probar.
- **Dos de los 13 agentes** (`agente-datos` y `agente-finanzas`) no se usaron en
  ninguna conversación, y `agente-crm` solo en la primera ronda.
- No se probó la **selección automática de skills** de Claude Code (sección 9)
  ni se probó con **una persona real** sin conocimientos técnicos.

---

## 2. Qué se probó, explicado simple

La prueba tuvo dos capas:

1. **¿Funcionan las instrucciones tal como están escritas?** Cada skill le
   enseña al asistente comandos del motor de cálculo. Un script los ejecutó
   **todos, uno por uno, tal como están escritos**, sobre una copia recién
   descargada del repositorio con la empresa de ejemplo.
2. **¿Funciona una conversación de verdad?** Se inventaron **seis personas**
   con su empresa, sus mensajes y sus respuestas escritos de antemano. Cada
   conversación la llevó una instancia distinta de Claude que actuó como
   Claude Code con el proyecto abierto: leyó `CLAUDE.md`, eligió la skill por su
   descripción, siguió a los agentes y sacó los números solo del motor. Si la
   skill pedía un dato que la persona no tenía en su guion, la respuesta era
   «no sé». Después, un script revisó lo que quedó (archivos, planillas,
   respuestas) contra **valores de referencia calculados aparte**.

Hubo **dos rondas** de conversaciones: la ronda 1 (versión `9960351`), la
corrección de lo encontrado y la ronda 2 (versión `e8e6f1b`), con
conversaciones nuevas e independientes y los mismos chequeos.

---

## 3. Capa 1: los comandos que enseñan las skills

| Pasada | Versión | Comandos | Funcionan | Error controlado | Omitido | Caídas |
|---|---|---:|---:|---:|---:|---:|
| 1 | `9960351` | 166 | 146 | 19 | 1 | 0 |
| 2 | `e8e6f1b` | 168 | 151 | 16 | 1 | 0 |
| 3 | `fa9897d` | 169 | 152 | 16 | 1 | 0 |
| 4 | `1eb0a95` | 169 | 152 | 16 | 1 | 0 |
| 5 | `9176293` | 169 | 152 | 16 | 1 | 0 |
| 6 | `59595c8` | 171 | 156 | 14 | 1 | 0 |
| 7 (final) | `cc9868d` | 171 | 145 | 25 | 1 | 0 |

- **Error controlado** quiere decir que el motor no se cayó y explicó qué falta
  y cómo seguir. **Omitido** es el comando genérico `<módulo> <acción>` de la
  skill `asistente`, que no se puede ejecutar tal cual.
- **Un «error controlado» puede esconder un fallo**, así que se revisaron uno
  por uno. Pasó dos veces:
  - En la pasada 1, dos eran errores de la documentación (el ejemplo de FuelEU
    y una empresa llamada «mi-empresa» que no existía).
  - En la pasada 4 apareció un fallo real que las pasadas 1 a 3 habían dejado
    pasar: `plantilla crear --tipo medidas` crea `medidas.xlsx`, pero
    `meta plan` buscaba `medidas_reduccion.xlsx`. Siguiendo la skill
    `plan-descarbonizacion`, **el plan no podía funcionar nunca**. Está
    corregido en `9176293`.
- En la pasada 2, la primera corrida encontró **una caída**: el informe europeo
  fallaba después de calcular solo FuelEU (un error que metió una corrección
  anterior). Se corrigió y se repitió.
- En la pasada 7 hay **11 errores controlados más** que en la 6, y es a
  propósito: esos comandos calculaban con las filas de ejemplo de una plantilla
  recién creada (activos, cadena de frío, Ley REP, logística y plan de medidas).
  Ahora el motor dice que la planilla solo tiene ejemplos y pide reemplazarlos.
  Las skills ya decían que el ejemplo hay que reemplazarlo.
- Los errores controlados de la versión final están justificados: planillas que
  la empresa de ejemplo ya tiene (el motor no las sobrescribe), archivos de
  ejemplo que no existen (`perfil.json`, respaldos), pasos previos (avance en un
  curso, una meta definida, llenar la planilla recién creada).
- La capa 1 solo comprueba que el comando **corre**, no que el resultado sea
  correcto. Eso lo miden las pruebas unitarias (786, todas pasan), la capa 2 y
  la revisión de código.

---

## 4. Capa 2: seis conversaciones

| | Persona y empresa | Qué pidió | Ronda 1 | Ronda 2 |
|---|---|---|:-:|:-:|
| E1 | Panadería en Arequipa (Perú), 12 personas | Registrar la empresa, dictar las boletas de 2025, calcular la huella e informe para el supermercado | 7/9 | **9/9** |
| E2 | Fábrica de envases plásticos en Talca (Chile), 60 personas | Qué leyes le aplican, una denuncia por acoso del 1-09-2026 (Ley Karin) y las metas de la Ley REP para 420 t | 8/9 | **9/9** |
| E3 | Empresa de ejemplo (alimentos) | Borrador VSME, si puede decir «100 % ecológicos y carbono neutral», datos de tres proveedores y qué pedirá un verificador | 8/10 | **10/10** |
| E4 | Exportadora de manzanas y cerezas de Curicó (Chile) a Países Bajos, 85 personas | Emisiones de un envío de 12 t (camión, barco, camión), qué normas europeas le aplican y qué cambia si exporta pernos de acero | 7/8 | **8/8** |
| E5 | Minera de cobre en Antofagasta, 300 personas | Si cumple su tranque de relaves, si se rompió la cadena de frío y cómo depreciar una camioneta y un cargador frontal | 7/10 | 9/10 |
| E6 | Empresa de ejemplo | Resumen para el directorio, datos raros, meta de −42 % al 2030, capacitar a 5 personas, anotar un prospecto y verificar el factor eléctrico oficial | 7/11 | 8/11 |
| | | **Total** | **44/57** | **53/57** |

**Algunos valores de referencia que tenían que calzar:** huella de E1
107,581 tCO2e (±1 %); en E2, los plazos de la Ley Karin al 04-09-2026 (3 días
hábiles) y al 15-10-2026 (30 días hábiles); el envío de E4, 3.508,04 kg CO2e;
en E5, la temperatura cinética media de −16,66 °C y una camioneta con 7 años de
vida útil normal y 2 acelerada.

**Cobertura:**

| | Ronda 1 | Ronda 2 |
|---|---|---|
| Comandos ejecutados en las conversaciones | 179 (9 con `ok: false`) | 150 (4 con `ok: false`) |
| Skills usadas (de 36) | 28 | 28 |
| Agentes seguidos (de 13) | 11 | 10 |

- Skills que **no** usó ninguna conversación de la ronda 2: `doble-materialidad`,
  `gobernanza`, `huella-hidrica`, `plan-descarbonizacion`, `preparar-equipo`,
  `proteccion-datos`, `retc` y `social-personas`. Esas quedaron cubiertas solo
  por la capa 1 y las pruebas unitarias; el fallo de `meta plan` estaba
  justamente en una de ellas.
- Agentes que **no** siguió ninguna conversación: `agente-datos` (el catálogo lo
  asocia a «leer y ordenar decenas de boletas o planillas», y en los guiones las
  personas dictaron sus datos en vez de entregar documentos) y
  `agente-finanzas` (el catálogo lo asocia a «cartera de activos fijos,
  depreciación y plan de recambio»; en E5 la depreciación se resolvió con la
  skill `activos-fijos` directamente).

**Los 4 chequeos que fallaron en la ronda 2:**

1. **E5 — no delegó en el agente de finanzas.** La depreciación de la camioneta
   salió bien (7 y 2 años de vida útil, cuota sobre el valor actualizado) y la
   del cargador frontal quedó pendiente con aviso (sección 8), pero el
   asistente no siguió al agente que el catálogo asocia a la depreciación.
2. **E6 — la capacitación del equipo no quedó registrada.** La skill `academia`
   registra el avance de quien responde en la conversación, y las 5 personas no
   estaban ahí. El asistente entregó la lección para compartir, pero no hay
   registro.
3. **E6 — el prospecto no quedó anotado.** El CRM vive en la carpeta de la
   consultora, y el guion no traía su nombre («no sé»). El asistente lo
   preguntó y no inventó uno.
4. **E6 — no delegó en el agente de CRM**, como consecuencia del punto 3.

---

## 5. Cómo se calculó la nota

Cada chequeo tiene **una sola dimensión**, fijada antes de contar (lista
completa en el anexo):

| Dimensión | Qué mide | Peso |
|---|---|---:|
| **Funciona** | El flujo llega al final: registra, crea archivos, delega | 35 % |
| **Correcto** | Los números y las normas coinciden con la referencia | 35 % |
| **Honesto** | Avisa sus límites, no inventa y no exagera | 15 % |
| **Claro** | La persona recibe lo importante sin tener que interpretarlo | 15 % |

Nota = suma de (chequeos aprobados ÷ chequeos de la dimensión × peso). Las
estrellas son la nota sobre 100 dividida por 20.

| Dimensión | Chequeos | Ronda 1 | Ronda 2 |
|---|---:|---:|---:|
| Funciona | 23 | 20 | 19 |
| Correcto | 19 | 13 | **19** |
| Honesto | 10 | 7 | **10** |
| Claro | 5 | 4 | **5** |
| **Nota** | 57 | **76,9 → 3,8 ★** | **93,9 → 4,7 ★** |

**Una advertencia para leer bien la mejora.** 11 de los 57 chequeos (los que
dicen «[corrección]») se escribieron **después** de la ronda 1, para confirmar
que lo encontrado quedó corregido. La ronda 1 los reprueba por construcción. Si
se cuentan solo los **46 chequeos definidos antes de ver resultados**:

| | Ronda 1 | Ronda 2 |
|---|---:|---:|
| Chequeos aprobados | 43/46 | 42/46 |
| Nota | 95,2 | 93,6 |

Es decir: lo que los chequeos originales medían **ya andaba bien** en la ronda 1
y siguió igual (con una delegación menos en E6). Lo que subió fue lo que se
encontró **leyendo las conversaciones a mano**, que los chequeos originales no
veían. Por eso la lectura a mano es parte de la prueba y no un extra.

---

## 6. Qué encontró la prueba y se corrigió

Cada corrección tiene su prueba en `tests/` para que no vuelva a pasar.

### Ronda 1 y capa 1 (pasadas 1 y 2): 31 problemas

Agrupados por tipo. El detalle, uno por uno, está en los mensajes de los
commits `f931198` a `e8e6f1b`.

- **Resultados que decían algo falso.** La fase III del tranque salía «se puede
  omitir» sin conocer la altura del muro. La depreciación con corrección
  monetaria se calculaba sobre el valor histórico. La CSDDD salía como
  obligación del exportador, cuando obliga al cliente europeo. «No sé» se
  guardaba como «no» (y lo europeo quedaba «no aplica»). El tablero mostraba
  plazos de un caso de Ley Karin que no existía. Una meta sin supuestos
  mostraba «0 %» de probabilidad, como si fuera un veredicto. La definición de
  productor de la Ley REP estaba mal.
- **Informes para terceros.** El informe de huella traía instrucciones para el
  asistente, no decía cuánto se estimó por gasto (91 % en la panadería) ni qué
  categorías del alcance 3 no se estimaron. El de logística mostraba «5 %%» y
  decía que ajustó distancias que no ajustó. El borrador VSME usaba el periodo
  equivocado, no usaba los datos de consumo y agua que ya existían y pisaba un
  borrador anterior.
- **Flujos que no se podían completar.** CBAM sin datos de planta fallaba antes
  de orientar. Un viaje dictado en la conversación no se podía calcular. Las
  filas de ejemplo de una plantilla podían entrar al cálculo de una empresa
  real. Una ruta de más de 260 caracteres en Windows fallaba sin explicación.
  Perú no tiene calendario y eso respondía con error en el primer paso. El CRM
  no permitía anotar la próxima acción.
- **Instrucciones que no calzaban con el motor.** Cumplimiento y calendario se
  contradecían. La ayuda no mostraba opciones que las skills usan. La carta a
  proveedores exigía respuesta por defecto. Las skills `aseguramiento` y
  `logistica-glec` describían el resultado del motor de otra forma, y
  `greenwashing` no decía qué hacer sin una meta definida. El ejemplo de FuelEU
  fallaba y otros usaban una empresa inexistente.
- **Una regresión**: el informe europeo se caía después de calcular solo
  FuelEU.

### Ronda 2 y capa 1 (pasada 4): 18 problemas

El detalle está en los commits `2c21f37` a `9176293`.

- **Ley Karin (lo más serio).** El motor dejaba investigar internamente una
  denuncia cuando la ley obliga a derivarla a la Dirección del Trabajo: sin
  reglamento interno actualizado (DS 21, artículo primero transitorio, inc. 3)
  o contra un gerente o representante (art. 12 inc. 5). Tampoco se podía
  registrar la recepción en la DT, desde la que corren los 30 días (art. 17).
- **Harina.** La skill presentaba como exacto un factor que es del cultivo de
  maíz (NAICS 111150). Ahora dice que la harina no tiene factor en el catálogo
  y ofrece pedírselo al proveedor, buscar el oficial o usar una aproximación
  **declarada**.
- **Cobertura sobrestimada.** VSME B7, B9 y B10 salían «cubiertos» con datos que
  responden solo una parte.
- **Informe de huella.** No mostraba la advertencia de fuente secundaria del
  factor eléctrico de Perú, repetía la misma conversión en dos líneas y su
  gráfico de calidad («100 % reportado») parecía contradecir que el 85 % se
  estimó por gasto.
- **Europa.** El recargo marítimo salía «aplica» sin saber si la carga va en
  barco, y lo que no aplica mantenía tareas.
- **Minería y activos.** El informe no aclaraba que la clasificación GISTM por
  población es solo una sugerencia, y la depreciación elegía una fila del SII
  sin mostrar las otras posibles.
- **Proveedores.** La carta no se guardaba por el largo del nombre del archivo,
  y sin `--motivo` afirmaba que «las normas que nos aplican» exigen los datos.
  La ayuda no mostraba `--categoria`, `--contacto` ni `--unidad`.
- **Guías y ayuda.** `empresa --ayuda` no mostraba `--anio-base`; la skill
  `inicio` no decía cómo ordenar los pasos si la persona no dijo para qué lo
  necesita; la skill `greenwashing` calculaba la huella sin periodo.
- **Plan de descarbonización** (capa 1, pasada 4): `meta plan` no encontraba la
  planilla que crea la plantilla (sección 3).

---

## 7. Revisión independiente del código

Después de la prueba, dos agentes revisores de IA revisaron el código sin
participar en escribirlo: uno escéptico, que busca errores de lógica, y otro
que busca **fallos silenciosos** (errores tragados, datos que faltan y se
rellenan, avisos que no llegan al documento). Lo hicieron en dos pasadas y
reprodujeron cada hallazgo en carpetas temporales. Cada hallazgo se verificó
antes de corregirlo.

**Pasada 1** (cambios posteriores a la ronda 2): 4 hallazgos del primer revisor
y 20 del segundo. Los más serios:

- **Ley Karin:** si la ley obligaba a derivar la denuncia y el caso se creó como
  investigación interna, no había forma de registrar la derivación; una denuncia
  derivada seguía mostrando plazos de la investigación interna; una respuesta
  «sí/no» que no se entendía contaba como «no hay que derivar»; y una fecha mal
  escrita se guardaba y rompía el listado y las alertas de todos los casos.
- **Filas de ejemplo:** si la persona llenaba una plantilla en Excel sin borrar
  los ejemplos, esas cifras inventadas entraban a la huella, agua, personas,
  Ley REP, activos, logística y cadena de frío.
- **Reportes:** el borrador daba como total una huella incompleta, sumaba
  personas de otros años y marcaba «cubiertos» contenidos que los datos
  responden solo en parte (por ejemplo, permiso parental con la dotación).

Corregidos en `501d4af`, `c9a6a3d` y `59595c8`.

**Pasada 2** (sobre esas correcciones): 1 hallazgo del primer revisor y 23 del
segundo (1 crítico, 9 altos). Los más serios:

- **Crítico:** `--contra-representante no se`, sin comillas, se leía como «no»:
  la empresa quedaba investigando cuando quizá debía derivar.
- Fechas de hitos de la Ley Karin fuera de orden que movían los plazos
  siguientes; casos guardados por la versión anterior que no se podían reparar.
- Una marca de «empresa de ejemplo» que una empresa real podía heredar y que
  apagaba el filtro de ejemplos.
- Informes que usaban la huella de otro periodo o resultados de una versión
  anterior del motor sin avisar.

Corregidos en `c26f0ac`, `47a3bbe` y `cc9868d`. Las pruebas pasaron de 734 a
786, y cada corrección tiene la suya en `tests/test_e2e_hallazgos.py`.

**Lo que esto dice de la prueba:** los 57 chequeos y la lectura de las
conversaciones no vieron estos problemas. Una prueba de conversaciones mide si
el flujo funciona en los casos elegidos; no reemplaza revisar el código.

---

## 8. Lo que sigue abierto

No está corregido. Algunas cosas son falta de datos oficiales y otras son
decisiones de diseño con costo:

| Tema | Qué pasa | Qué hacer por ahora |
|---|---|---|
| Perú | No hay calendario de obligaciones ni factores propios de diésel y GLP. El factor eléctrico de 2024 viene de una fuente secundaria | El motor usa los factores de combustibles de Chile y lo advierte; el informe marca el factor eléctrico como fuente secundaria. Conviene confirmarlo con MINAM antes de un reporte auditable |
| Activos en minería | La nómina de vida útil del SII para minería no está cargada | Confirmar con el contador. El motor no asigna una categoría agrícola sin avisar |
| Capacitar a un equipo | La academia registra solo a quien responde en la conversación | Cada persona hace el curso en su propia conversación |
| CRM de una consultora | Necesita la empresa de la consultora registrada | Registrarla con su nombre antes de anotar prospectos |
| Clasificación de relaves | Una clasificación local (por ejemplo, «categoría A») no se traduce a las clases del GISTM | Pasar la clase del GISTM que indique el estudio |
| Notas en planillas | `datos escribir` no edita las notas de filas que ya existen | Editarlas en Excel |
| Informe de la meta | No incluye la revisión de criterios de `meta validar` | Adjuntar esa revisión |
| Costos europeos | Sin datos del viaje, del precio EUA o de la planta no calcula costos marítimos ni de CBAM | Por diseño: no inventa valores |
| Rutas largas en Windows | Si el proyecto está en una carpeta muy profunda, algunos archivos no se pueden guardar | El motor lo explica: mover la carpeta cerca de la raíz del disco (por ejemplo, `C:\agentes-esg`) |
| Revisión de código | Dos pasadas encontraron más de 20 problemas cada una; no hubo tercera pasada | Hacer otra revisión y una ronda 3 de conversaciones antes de confiar en el resultado para algo legal |
| Aplicar medidas en una denuncia derivada | La ley dice «15 días» desde que la empresa recibe las conclusiones de la DT; el reglamento fija días corridos solo para la investigación interna | El motor cuenta días corridos (la opción más corta) y lo avisa: confirmarlo con la asesoría jurídica |
| Datos de la ficha | `empresa actualizar --datos` acepta cualquier clave del archivo | Revisar el archivo antes de cargarlo |
| Verificación en línea | Algunas páginas oficiales bloquean la lectura automática (el Ministerio de Energía respondió 403) | El investigador cotejó con el archivo oficial de HuellaChile y el valor coincidió con el del motor; el cotejo directo con el Ministerio quedó pendiente |

---

## 9. Límites de esta prueba

1. **Asistente simulado.** Las conversaciones las llevaron instancias de Claude
   que leyeron `CLAUDE.md`, las skills y los agentes y los siguieron al pie de la
   letra. **No** se probó cómo Claude Code elige y carga las skills por sí solo,
   porque la sesión de terminal (`claude -p`) no tenía la cuenta autenticada en
   este equipo.
2. **Lo corregido después de la ronda 2** (incluida la revisión de código) se
   verificó con pruebas unitarias (786, todas pasan) y con la capa 1 (pasada 7:
   0 caídas), **no** con una tercera ronda de conversaciones.
3. **La revisión de código la hicieron agentes de IA**, no personas, y en dos
   pasadas. No reemplaza una auditoría de un especialista, sobre todo en la
   Ley Karin.
4. **Los chequeos son automáticos y acotados.** «Claro» tiene solo 5. Ninguna
   persona real sin conocimientos técnicos usó el sistema en esta prueba.
5. **La referencia de E1 usa el factor de agricultura para la harina.** Después
   se concluyó que es una aproximación que hay que declarar (sección 6). Ese
   chequeo confirma la aritmética del motor, no la elección del factor.
6. **Los guiones estaban fijados de antemano.** Una persona real pregunta cosas
   distintas, se equivoca al dictar y cambia de tema.
7. **Fecha.** Los plazos legales se calcularon con fecha 16-09-2026. Las normas
   están verificadas a esa fecha en `docs/investigacion/`.

---

## 10. Cómo repetirla

**Capa 1** (no necesita Claude, solo Python 3):

1. Descarga una copia **nueva** del repositorio en una carpeta corta (por
   ejemplo, `C:\e2e\clon`): la prueba escribe archivos en la empresa de
   ejemplo.
2. Desde la carpeta del repositorio, ejecuta:

```bash
python tests/e2e/comandos_documentados.py C:\e2e\clon C:\e2e\resultado.json
```

3. Revisa uno por uno los «controlado»: la sección 3 muestra que pueden
   esconder fallos.

**Capa 2:** usa los seis escenarios de la sección 4. Para cada uno, abre el
proyecto en Claude Code, escribe los mensajes de la persona en orden y revisa
con el anexo lo que quedó. Los scripts de verificación de esta prueba no se
publicaron: dependen de las carpetas de la sesión en que se corrió.

---

## Anexo: los 57 chequeos

✅ aprobado · ❌ reprobado. «[corrección]» = chequeo agregado después de la
ronda 1.

| Escenario | Chequeo | Dimensión | Ronda 1 | Ronda 2 |
|---|---|---|:-:|:-:|
| E1 | Empresa registrada en Perú | Funciona | ✅ | ✅ |
| E1 | Planilla de consumos con los datos dictados | Funciona | ✅ | ✅ |
| E1 | Compras de harina cargadas completas (108.000 USD) | Correcto | ✅ | ✅ |
| E1 | Huella igual a la referencia (±1 %) | Correcto | ✅ | ✅ |
| E1 | Informe HTML generado | Funciona | ✅ | ✅ |
| E1 | Avisa que el factor de combustión no es peruano | Honesto | ✅ | ✅ |
| E1 | [corrección] El informe dice cuánto se estimó por gasto | Honesto | ❌ | ✅ |
| E1 | [corrección] El informe no trae instrucciones para el asistente | Claro | ❌ | ✅ |
| E1 | Delega en agentes de datos o carbono | Funciona | ✅ | ✅ |
| E2 | Empresa registrada en Chile | Funciona | ✅ | ✅ |
| E2 | La revisión detecta Ley REP y Ley Karin | Correcto | ✅ | ✅ |
| E2 | Caso Karin con la fecha correcta y plazos iguales a la referencia | Correcto | ✅ | ✅ |
| E2 | La respuesta da las fechas 04-09 y 15-10 de los plazos principales | Claro | ✅ | ✅ |
| E2 | Dice que los plazos de 3 días hábiles ya vencieron (hoy 16-09-2026) | Claro | ✅ | ✅ |
| E2 | Ley REP: corrió el cálculo de metas | Funciona | ✅ | ✅ |
| E2 | Aclara que no es asesoría legal | Honesto | ✅ | ✅ |
| E2 | [corrección] El calendario no pide la cuota de inclusión a 60 trabajadores | Correcto | ❌ | ✅ |
| E2 | Delega en agentes de cumplimiento y Ley Karin | Funciona | ✅ | ✅ |
| E3 | Borrador VSME en Word generado | Funciona | ✅ | ✅ |
| E3 | El borrador no repite la misma frase entre secciones | Claro | ✅ | ✅ |
| E3 | [corrección] B1 usa el periodo 2025 | Correcto | ❌ | ✅ |
| E3 | [corrección] B6 usa los datos de agua | Correcto | ❌ | ✅ |
| E3 | [corrección] No pisa el borrador anterior | Funciona | ✅ | ✅ |
| E3 | Rechaza «100 % ecológicos» y «carbono neutral» por bonos | Correcto | ✅ | ✅ |
| E3 | Registra los 3 proveedores | Funciona | ✅ | ✅ |
| E3 | Genera cuestionario o carta para proveedores | Funciona | ✅ | ✅ |
| E3 | Prioriza a Molino Central (el de mayor gasto) | Correcto | ✅ | ✅ |
| E3 | Delega en reportes, auditor y proveedores | Funciona | ✅ | ✅ |
| E4 | Empresa registrada en Chile | Funciona | ✅ | ✅ |
| E4 | Emisiones del envío iguales a la referencia (3.508,04 kg) | Correcto | ✅ | ✅ |
| E4 | Marca el total como incompleto por los puertos | Honesto | ✅ | ✅ |
| E4 | CSRD no le aplica directamente | Correcto | ✅ | ✅ |
| E4 | EUDR no cubre manzanas ni cerezas | Correcto | ✅ | ✅ |
| E4 | Pernos de acero: CBAM sí aplica y menciona el umbral de 50 t | Correcto | ✅ | ✅ |
| E4 | [corrección] La CSDDD no sale como obligación del exportador | Correcto | ❌ | ✅ |
| E4 | Delega en el agente de Unión Europea | Funciona | ✅ | ✅ |
| E5 | Empresa registrada en Chile | Funciona | ✅ | ✅ |
| E5 | Relaves: cita el DS 248 y corre el motor | Funciona | ✅ | ✅ |
| E5 | Relaves: no inventa niveles TARP | Honesto | ✅ | ✅ |
| E5 | Frío: temperatura cinética media correcta (−16,66 °C) | Correcto | ✅ | ✅ |
| E5 | Frío: detecta la excursión de 4 horas y el pico de −13 °C | Correcto | ✅ | ✅ |
| E5 | Camioneta: 7 años normal y 2 acelerada | Correcto | ✅ | ✅ |
| E5 | Cargador frontal: no asigna una categoría agrícola sin advertir | Honesto | ✅ | ✅ |
| E5 | [corrección] Fase III sin altura del muro no queda como «cumple» | Honesto | ❌ | ✅ |
| E5 | [corrección] La cuota 2025 se calcula sobre el valor actualizado (3.893.333) | Correcto | ❌ | ✅ |
| E5 | Delega en agentes de minería y finanzas | Funciona | ❌ | ❌ |
| E6 | Tablero generado | Funciona | ✅ | ✅ |
| E6 | Revisa datos raros en varias planillas | Funciona | ✅ | ✅ |
| E6 | Meta de −42 % al 2030 registrada | Funciona | ✅ | ✅ |
| E6 | Da una probabilidad de cumplimiento o explica por qué no | Claro | ✅ | ✅ |
| E6 | Capacitación registrada para el equipo | Funciona | ❌ | ❌ |
| E6 | Prospecto Viña Santa Rita con próxima acción | Funciona | ❌ | ❌ |
| E6 | Verifica en una fuente oficial con enlace | Honesto | ✅ | ✅ |
| E6 | No modifica el catálogo de factores | Honesto | ✅ | ✅ |
| E6 | [corrección] El tablero no muestra plazos de un caso Karin inexistente | Correcto | ❌ | ✅ |
| E6 | [corrección] Sin supuestos no se presenta un 0 % como probabilidad | Honesto | ❌ | ✅ |
| E6 | Delega en academia, CRM e investigador | Funciona | ✅ | ❌ |
