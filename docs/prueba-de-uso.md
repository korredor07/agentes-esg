# Prueba de uso — 16 de septiembre de 2026

Prueba de recorrido completo sobre una **copia** del repositorio (carpeta temporal
de la sesión). El repositorio original no se modificó salvo este documento.

**Caso simulado:** Marcela, dueña de una panadería en Arequipa (Perú), 12
trabajadores, sin conocimientos de sostenibilidad ni de computación. Un
supermercado le pidió «la huella de carbono de tus productos y tus datos de
sostenibilidad».

**Empresa creada en la prueba:** `Panaderia Delicias del Misti` (PE, pequeña, 12
personas, año base 2025, no exporta a la UE).

## Resumen

**El recorrido se pudo completar de punta a punta, pero el producto entrega a
Marcela un número equivocado y se lo presenta como si fuera correcto.**

Todas las etapas produjeron archivos: huella, indicadores sociales, diagnóstico,
normativa aplicable, tablero y borrador de reporte en Word. El motor no se cayó
nunca y sus mensajes de error son, en general, comprensibles.

Los tres problemas de fondo:

1. El **catálogo de la skill `asistente`** —que es el mapa que el asistente
   está obligado a consultar— no lista casi ninguna de las 16 skills. Siguiendo
   las instrucciones al pie de la letra, el asistente le habría dicho a Marcela
   que medir la huella de carbono «todavía no existe».
2. `huella calcular` devolvió **`"ok": true`** aunque **12 de 38 filas no se
   pudieron calcular**: los dos hornos a GLP, que son la principal fuente de
   alcance 1 de una panadería. El informe, el tablero y el borrador Word
   publican **44,6 tCO2e** sin decir en ningún lugar visible que falta
   aproximadamente **20,1 tCO2e** (un 31 % del total real).
3. Para Perú **no existe ningún factor de alcance 1** (ni GLP, ni gasolina, ni
   diésel). El motor usa el factor chileno, avisa por consola… y esa advertencia
   **no aparece en ninguno de los documentos** que Marcela le va a entregar al
   supermercado.

---

## Tabla de pasos

«Pasos» = llamadas al motor o acciones necesarias para llegar al resultado.

| # | Qué hice | Comando | ¿Funcionó? | Pasos |
|---|---|---|---|---|
| 1 | Leer `CLAUDE.md`, skill `asistente` y `catalogo.md` | — | Sí, pero el catálogo está casi vacío (H1) | 3 |
| 2 | Comprobar Python | `python --version` | Sí (3.14.0) | 1 |
| 3 | Ver empresas registradas | `esg.py empresa listar` | Sí, pero aparece la empresa demo chilena (H6, H14) | 1 |
| 4 | Registrar la panadería | `esg.py empresa crear --datos perfil.json` | Sí | 1 |
| 5 | Ver plantillas disponibles | `esg.py plantilla listar` | Sí | 1 |
| 6 | Crear planillas | `esg.py plantilla crear --tipo consumos\|personas\|alcance3 --empresa panaderia-delicias-del-misti` | Falla sin `--empresa`; ninguna skill lo documenta (H6) | 4 |
| 7 | Cargar los datos dictados por Marcela | **ninguno**: el motor no tiene acción de escritura; hubo que escribir un script Python propio (H7) | Sí, pero fuera de lo documentado | 1 |
| 8 | Ver qué se cargó | `esg.py datos resumen --empresa ...` | Sí | 1 |
| 9 | Buscar datos raros | `esg.py datos anomalias --empresa ...` | Sí («No encontré datos raros»), pero solo revisa `consumos.xlsx` (H15) | 1 |
| 10 | Calcular la huella | `esg.py huella calcular --periodo 2025 --empresa ...` | `"ok": true` con **13 filas caídas** (H2, H8) | 1 |
| 11 | Corregir el nombre del gasto de alcance 3 y recalcular | ídem | Sí; quedan **12 filas caídas** (el GLP) | 2 |
| 12 | Generar el informe de huella | `esg.py huella reporte --periodo 2025 --empresa ...` | Sí, pero publica el total incompleto (H2, H3) | 1 |
| 13 | Indicadores sociales | `esg.py social calcular --periodo 2025 --empresa ...` | Sí | 1 |
| 14 | Diagnóstico inicial | `esg.py diagnostico evaluar --empresa ...` | Sí (22,2/100) | 1 |
| 15 | Obtener las preguntas | `esg.py diagnostico preguntas --empresa ...` | Sí (13 preguntas) | 1 |
| 16 | Responder por Marcela | `esg.py diagnostico responder --indicador <id> --estado <estado> --nota "..."` | Sí | 12 |
| 17 | Reevaluar | `esg.py diagnostico evaluar --empresa ...` | Sí (40,8/100) | 1 |
| 18 | Normas aplicables | `esg.py cumplimiento revisar --empresa ...` | Sí, pero pregunta cosas chilenas a una empresa peruana (H9) | 1 |
| 19 | Informe de normativa | `esg.py cumplimiento informe --empresa ...` | Sí | 1 |
| 20 | Informe de diagnóstico | `esg.py diagnostico informe --empresa ...` | Sí | 1 |
| 21 | Tablero | `esg.py tablero generar --empresa ...` | Sí, con indicadores contradictorios (H10, H13) | 1 |
| 22 | Comparar marcos de reporte | `esg.py reporte marcos --empresa ...` | Sí | 1 |
| 23 | Cobertura VSME | `esg.py reporte cobertura --marco VSME --empresa ...` | Sí (42,5 %) | 2 |
| 24 | Borrador Word | `esg.py reporte borrador --marco VSME --empresa ...` | Sí, con texto repetido (H11) | 1 |
| 25 | Respaldar evidencia | `esg.py evidencia registrar --archivo datos/consumos.xlsx --descripcion "Consumos 2025" --empresa ...` y `evidencia verificar` | Sí | 2 |
| 26 | Correr las pruebas del proyecto | `python -m pytest tests -q` | **182 passed** (y aun así H4 pasa desapercibido) | 1 |

**Total: 26 etapas, ~44 llamadas al motor.** Ninguna se colgó.

---

## Hallazgos

Ordenados por gravedad.

### H1 — El catálogo que gobierna todo el enrutamiento está casi vacío

**Qué pasó.** `CLAUDE.md` obliga a invocar primero la skill `asistente`, y
`asistente/SKILL.md:36` obliga a enrutar leyendo `catalogo.md`. Ese catálogo
lista **3 skills** (`ayuda`, `inicio`, `preparar-equipo`) y unos comandos del
motor. Las otras **13 skills no están**: `huella-carbono`, `diagnostico-esg`,
`cargar-datos`, `alcance-3`, `tablero`, `brechas-cumplimiento`,
`social-personas`, `ley-karin`, `metas-net-zero`, `plan-descarbonizacion`,
`consultar-datos`, `evidencias`. La sección de agentes dice literalmente *«(La
lista de agentes se completa a medida que se agregan.)»* aunque hay 10 agentes
en `.claude/agents/`.

**Dónde.** `.claude/skills/asistente/catalogo.md:1-28`. El encabezado es
explícito: *«Si algo no está aquí, todavía no existe: dilo con honestidad en vez
de improvisar.»* Y `ayuda/SKILL.md:41` repite la regla.

**Por qué es un problema.** Es el primer mensaje de la conversación. Un
asistente que siga las instrucciones al pie de la letra le responde a Marcela
que medir la huella de carbono no existe todavía —cuando sí existe, está
completa y funciona. Marcela cierra la aplicación y no vuelve. Que la prueba
haya salido bien se debe a que yo leí las 16 skills a mano, cosa que el flujo no
pide.

**Qué propondría.** Completar el catálogo con las 16 skills y los 10 agentes, y
agregar una prueba automática que falle si existe una carpeta en
`.claude/skills/` que no esté nombrada en `catalogo.md`.

---

### H2 — La huella sale `"ok": true` aunque falte un tercio de las emisiones

**Qué pasó.** Marcela compra **12 balones de GLP de 45 kg al mes** para sus dos
hornos. Cargados como `540 kg` mensuales, las 12 filas fallaron:

```
"fila": 14,
"error": "El factor de «glp» esta en L y tus datos estan en kg.",
"sugerencia": "Revisa la unidad en la planilla o dime en que unidad esta realmente el consumo."
```

Aun así la respuesta global fue:

```
"ok": true,
"total_t_co2e": 44.560683097993525,
"registros_calculados": 26,
"registros_con_problema": 12,
```

El resultado se guardó en `resultados/huella_2025.json` y de ahí pasó, sin
ninguna marca de «incompleto», a los tres entregables:

- `reportes/huella-carbono-2025.html`: titular **«Huella total 44,6 tCO2e»**.
- `reportes/tablero.html`: **«Huella de carbono 44,6 tCO2e»** y, además,
  «Estado de los datos → **Cumple** → Energía y combustibles».
- `reportes/borrador-vsme-2025.docx`, sección B3: *«Alcance 1 (lo que la empresa
  quema o fuga): 5,1 tCO2e»*, *«Huella total: 44,6 tCO2e»* y *«Planilla de
  consumos: **36 filas** de energía y combustibles»* (solo se usaron 24).

Comprobé cuánto falta convirtiendo el GLP con la densidad que el propio
repositorio documenta (0,540 kg/L, `docs/investigacion/01-...md:535`): **20,1
tCO2e**. El total real ronda las **64,7 tCO2e**: lo publicado subestima en un
**31 %**, y el alcance 1 informado (5,1 t) es en realidad **25,2 t**, cinco veces
más.

**Dónde.** `.claude/motor/calculos/carbono.py:369` (`continuar_con_errores=True`
acumula en `problemas` y sigue); `.claude/motor/nucleo/unidades.py:120`
(`convertir` rechaza masa→volumen a propósito). La lista de filas caídas sí
aparece en el HTML de la huella, pero al final de la página, bajo el título
técnico «Filas que no se pudieron calcular», y **no aparece en absoluto** en el
tablero ni en el Word.

**Por qué es un problema.** Marcela no sabe qué es «el factor está en L y tus
datos están en kg», y el mensaje sugiere que *ella* se equivocó cuando su dato
(45 kg por balón, lo que dice el balón) es el correcto. Vio `ok`, vio un PDF
bonito con un número grande, y se lo mandó al supermercado. Si el supermercado
audita, el número no cuadra y la responsable es ella.

**Qué propondría.** Tres cosas: (a) que `huella calcular` devuelva
`"ok": false` —o al menos `"total_incompleto": true`— cuando haya filas caídas, y
que ese estado viaje dentro de `huella_2025.json`; (b) que el informe, el tablero
y el Word muestren un aviso arriba del total («Este total no incluye 12 filas de
GLP»); (c) agregar densidades de combustible al conversor (el dato ya está
investigado en `docs/investigacion/01`) o, como mínimo, un factor de GLP por kg,
que es como se compra el gas en toda Latinoamérica.

---

### H3 — Perú no tiene factores de alcance 1, y el aviso no llega al informe

**Qué pasó.** El catálogo de factores solo tiene, para Perú, **electricidad
2022, 2023 y 2024**. No hay GLP, ni gasolina, ni diésel, ni refrigerantes. Para
la camioneta de Marcela el motor usó el factor **chileno** y avisó:

```
"El factor disponible para gasolina es de CL, no de PE."
"No tengo factor propio de PE para residuos: use un factor internacional de referencia."
"Para electricidad use el factor de 2024, que es el mas cercano que tengo a 2025."
```

Las tres advertencias salen por consola. Revisé el HTML generado: la sección
«Metodología y fuentes» lista las fuentes, pero **no dice en ninguna parte que se
usó un factor de otro país ni de otro año**.

**Dónde.** `.claude/motor/datos/factores_emision.csv` (todas las filas de
alcance 1 son `pais=CL`); `.claude/motor/calculos/carbono.py:236-239` genera la
advertencia; `.claude/motor/nucleo/informe.py` no la imprime.

**Por qué es un problema.** El `plugin.json` promete cobertura para «Chile, Perú
y la Unión Europea», y el `README` invita a usarlo desde cualquier país. Marcela
entrega un informe que dice «factores oficiales» sin decir que su gas y su
gasolina se calcularon con la matriz chilena. Eso es exactamente lo que una
auditoría de cliente marca como hallazgo, y contradice la regla del propio
`CLAUDE.md`: «Marca la calidad del dato… un número estimado no se presenta como
si fuera medido».

**Qué propondría.** Que todas las `advertencias` del cálculo se impriman en el
informe, en un bloque «Supuestos y limitaciones» visible; y que el perfil de
empresa avise al registrarse en un país sin factores de alcance 1.

---

### H4 — La columna «Calidad del dato» nunca se lee: todo queda como «estimado»

**Qué pasó.** Marqué las 12 filas de electricidad como `reportado` (vienen de los
recibos de luz). El resultado dice:

```
"calidad_datos": {"porcentaje": {"estimado": 100.0, "reportado": 0.0, "verificado": 0.0}}
```

Reproducción mínima:

```
Calidad del dato -> 'calidad_del_dato'
con calidad_del_dato=verificado -> estimado      <-- lo que produce la plantilla
con calidad_dato=verificado     -> verificado    <-- lo que espera el motor
```

**Dónde.** La plantilla crea la columna **«Calidad del dato»**
(`.claude/motor/plantillas/definiciones.py:69` y `:93`), que
`nucleo/excel.normalizar_encabezado` convierte en `calidad_del_dato`. Pero
`.claude/motor/calculos/carbono.py:332` lee
`registro.get("calidad_dato") or registro.get("calidad") or "estimado"`. La
cadena `calidad_del_dato` **no existe en ninguna parte del motor**. Como el valor
por defecto (`estimado`) es válido, tampoco se dispara la advertencia «No
reconocí la calidad de dato».

**Consecuencias en cadena:**

- El informe de huella muestra «Calidad de los datos: Verificado 0 %, Reportado
  0 %, **Estimado 100 %**», siempre, para todo el mundo.
- El indicador `amb-calidad` del diagnóstico («Datos respaldados en boletas o
  mediciones») queda en `no_cumple` de forma permanente, con el mensaje «Casi
  todo son estimaciones (0 % respaldado)», porque exige ≥40 % respaldado
  (`calculos/puntaje.py:196-201`). Nadie puede aprobarlo jamás.
- El tablero lo sube a «Próximas cinco cosas por hacer»: *«Reemplazar
  estimaciones por boletas, facturas o lecturas de medidor»* — que es justo lo
  que Marcela ya hizo.
- Pasa lo mismo con la empresa de ejemplo que se distribuye
  (`ejemplo-alimentos-del-sur`: 76 filas, 0 problemas, **100 % estimado**).

**Por qué es un problema.** La skill `cargar-datos` dedica una sección entera a
explicarle a la persona que la calidad del dato «no es un detalle» y le pide
clasificar fila por fila. Ese trabajo se descarta en silencio. Y el producto la
castiga en el puntaje ESG por un dato que sí tiene.

**Por qué no lo detectaron las pruebas.** Las 182 pruebas pasan. `test_carbono.py`
construye los registros a mano con la clave interna `calidad_dato` (líneas 109,
149, 157-161) en vez de generar la plantilla y leerla. `test_cli.py` solo crea la
plantilla `sitios`, que no tiene columna de calidad. No hay ninguna prueba que
recorra plantilla → llenar → `leer_tabla` → `calcular`.

**Qué propondría.** Aceptar también `calidad_del_dato` (y renombrar la columna o
el campo), y agregar una prueba de extremo a extremo que cree la plantilla de
consumos, la llene con una fila `verificado` y compruebe que el resultado no dice
`estimado`.

---

### H5 — Los comandos documentados fallan en PowerShell, que es el shell por defecto en Windows

**Qué pasó.** Las 16 skills escriben los comandos así:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" empresa listar
```

En PowerShell, `${CLAUDE_SKILL_DIR}` no es una variable de entorno sino una
variable de PowerShell, y queda vacía. Resultado literal:

```
C:\Python314\python.exe: can't open file 'D:\\motor\\esg.py': [Errno 2] No such file or directory
```

En Bash funciona **solo si** el shell exporta la variable; sin ella da el mismo
error.

**Dónde.** Todos los `SKILL.md` (por ejemplo `asistente/SKILL.md:27` y `:52`,
`inicio/SKILL.md:17`, `huella-carbono/SKILL.md:33`). El `settings.json` habilita
tanto `Bash(python *)` como `PowerShell(python *)`, así que el asistente puede
elegir cualquiera de los dos.

**Por qué es un problema.** El `README` apunta a usuarias de Windows («botón
verde Code → Download ZIP»). Si el asistente elige PowerShell, el primer comando
falla y `asistente/SKILL.md:29` manda a la skill `preparar-equipo`, que es la de
*instalar Python* — cuando Python está perfectamente instalado. Marcela se pasa
la primera sesión intentando reinstalar algo que ya tiene.

**Qué propondría.** Usar una ruta relativa a la raíz del proyecto
(`python .claude/motor/esg.py ...`, que funciona en los dos shells y es más corta
de leer), o documentar las dos variantes.

---

### H6 — Ninguna skill documenta `--empresa`, y el repositorio viene con una empresa de ejemplo que hace fallar el primer comando

**Qué pasó.** El repositorio se distribuye con `empresas/ejemplo-alimentos-del-sur`.
En cuanto Marcela registra la suya hay **dos** empresas, y todos los comandos de
las skills —que nunca llevan `--empresa`— fallan:

```
"error": "Hay varias empresas registradas y no se cual usar.",
"sugerencia": "Indica una de estas: Alimentos del Sur SpA, Panaderia Delicias del Misti."
```

Busqué `--empresa` en los 16 `SKILL.md`: **cero apariciones**. La opción existe
(`modulos/huella.py:32` y equivalentes) pero solo se descubre leyendo el código
Python. La propia sugerencia dice «indica una de estas» sin decir *cómo*.

**Por qué es un problema.** Es el primer muro, y llega justo después de registrar
la empresa. El asistente tiene que adivinar el nombre de la opción o abrir el
código fuente; Marcela no puede hacer ninguna de las dos cosas.

**Qué propondría.** Añadir `--empresa` a los ejemplos de todas las skills;
incluir el nombre exacto de la opción en la sugerencia del error («usa
`--empresa panaderia-delicias-del-misti`»); y mover la empresa de ejemplo a
`docs/` o a una carpeta `ejemplos/` que no cuente como empresa registrada.

---

### H7 — La forma recomendada de cargar datos no tiene comando

**Qué pasó.** La skill `cargar-datos` pone como opción 1 y 3 (las más cómodas)
que el asistente escriba la planilla por la persona: *«léelos, extrae los datos y
escribe la planilla»*, *«anótalos tú en la planilla y sigue»*. Pero el motor
tiene `plantilla crear`, `datos leer`, `datos resumen`, `datos anomalias` — y
**ninguna acción de escritura**. Para cargar los datos que Marcela me dictó tuve
que escribir un script Python propio que importa `nucleo.excel.escribir_xlsx` y
`plantillas.definiciones`.

**Dónde.** `.claude/skills/cargar-datos/SKILL.md:13-32`;
`.claude/motor/modulos/datos.py` (solo `leer`, `resumen`, `anomalias`);
`.claude/motor/modulos/plantilla.py` (solo `listar`, `crear`).

**Por qué es un problema.** Cada asistente improvisa su propio script, con
formatos distintos, riesgo de romper la planilla y sin las validaciones del
motor. Además contradice `CLAUDE.md` («los números salen del motor»): la carga de
datos queda fuera del motor. Y si el script falla, Marcela ve un `Traceback` de
Python en pantalla.

**Qué propondría.** Una acción `datos agregar --archivo consumos.xlsx --fila
'{...}'` (o `--filas archivo.json`) que valide contra la definición de la
plantilla antes de escribir.

---

### H8 — Los nombres del alcance 3 «por gasto» no son descubribles, y elegir mal cambia el resultado 3,4 veces

**Qué pasó.** Marcela compra harina e insumos por **USD 9.000 al mes**. Escribí
la actividad como `gasto insumos`, que es como lo diría cualquiera:

```
"fila": 2,
"error": "No tengo un factor de emision para «gasto insumos».",
"sugerencia": "Puedo buscarlo en una fuente oficial y agregarlo con su respaldo, o puedes indicarme uno tu."
```

No hay ninguna lista de nombres válidos en la skill `alcance-3` ni en la
plantilla. Existen 38 nombres `gasto ...` en el catálogo, pero solo se ven
volcando las 108 filas del CSV o usando `huella factores`, **que no está
documentado en ninguna skill**. Y `huella factores --recurso glp --pais PE`
devuelve `"ok": true, "total": 0` con un mensaje genérico, sin decir «no
encontré nada».

Peor: hay dos candidatos plausibles para la harina, con nombres indistinguibles
para una persona no técnica, y una diferencia enorme:

| Nombre en el catálogo | Qué es en realidad | Resultado con USD 108.000 |
|---|---|---|
| `gasto alimentos` | NAICS 311812, «alimentos procesados tipo panadería» | **27,3 tCO2e** |
| `gasto agricultura` | NAICS 111150, «compra de granos y cultivos» | **91,6 tCO2e** |

Son **64,3 tCO2e de diferencia**, más que toda la huella medida de la panadería.
Para harina, lo correcto es `gasto agricultura`; `gasto alimentos` es el sector
de la propia Marcela. El motor acepta cualquiera de los dos sin decir nada.

**Dónde.** `.claude/motor/datos/factores_emision.csv:91` y `:94`;
`.claude/skills/alcance-3/SKILL.md:59-73` explica el método por gasto pero no da
la tabla de nombres.

**Por qué es un problema.** La elección más determinante de toda la huella queda
en manos de adivinar una palabra, sin ayuda y sin advertencia. Y el mensaje de
error no ofrece alternativas parecidas.

**Qué propondría.** Incluir en `alcance-3/SKILL.md` la tabla completa
«qué compro → qué nombre escribo»; que el error de factor desconocido sugiera los
nombres más parecidos; y documentar `huella factores` como la forma de consultar
el catálogo.

---

### H9 — El módulo de cumplimiento le hace preguntas chilenas a una empresa peruana, y su única obligación real no tiene skill

**Qué pasó.** `cumplimiento revisar` identificó **una** norma aplicable —**Ley
27942 (hostigamiento sexual laboral)**, riesgo **alto**, con multas de SUNAFIL— y
después le hizo a Marcela 8 preguntas pendientes, casi todas chilenas:

> «¿Venden productos envasados…?» *(para la Ley REP, que es chilena)*
> «¿Alguna instalación emite más de 100 toneladas de material particulado…?» *(impuesto verde chileno)*
> «¿Es sociedad anónima abierta o está supervisada por la **CMF**?» *(regulador chileno)*
> «¿Descargan aguas del proceso…?» *(RILes, término chileno)*

**Dónde.** `.claude/motor/calculos/aplicabilidad.py:272-302` define `PREGUNTAS`
como una lista plana, y la línea **320** las filtra únicamente por «ya
respondida», nunca por país: `pendientes = [p for p in PREGUNTAS if p["clave"] not in respuestas]`.

Además, el resultado enruta la Ley 27942 a la skill `social-personas`. Busqué
«Perú», «27942» y «hostigamiento» en `social-personas/SKILL.md` y
`ley-karin/SKILL.md`: **cero apariciones**. Ambas skills son íntegramente
chilenas.

Y el diagnóstico tampoco cubre el hueco: el indicador de protocolo de acoso
(`soc-karin`, `calculos/puntaje.py:94`) está limitado a `"paises": ["CL"]`, así
que a Marcela **nunca se le pregunta si tiene protocolo de acoso** —siendo que
no lo tiene y que es su única obligación de riesgo alto.

**Por qué es un problema.** Marcela contesta preguntas sobre un regulador que no
existe en su país (pierde confianza en todo el resto), y el único riesgo legal
real que el producto le detecta la deja sin camino: la skill a la que la mandan
habla de otra ley, de otro país.

**Qué propondría.** Filtrar `PREGUNTAS` por país igual que se filtran las reglas;
generalizar el indicador `soc-karin` a «protocolo de prevención del acoso» con
la norma local según el país; y extender `social-personas` con la sección de Perú
(Ley 27942 y su reglamento) o crear una skill equivalente.

---

### H10 — El tablero muestra indicadores en verde que contradicen el propio informe

**Qué pasó.** En `reportes/tablero.html`, generado el mismo día con los mismos
datos:

| Lo que dice el tablero | Lo que pasa de verdad |
|---|---|
| «**Listo para auditoría 66,7 %** — Indicadores con dato respaldado» | El informe de huella dice «Estimado **100 %**, Reportado 0 %» |
| «Evidencias **0** respaldos — **Cadena intacta**» | No hay ningún respaldo registrado; no hay nada que esté «intacto» |
| «Estado de los datos → **Cumple** → Energía y combustibles» | 12 de 36 filas de ese archivo no se pudieron calcular |
| «Huella de carbono **44,6 tCO2e**» | Sin ninguna marca de que faltan ~20 t |

El nombre «Listo para auditoría» además no significa lo que parece: es el
porcentaje de indicadores *automáticos* en estado `cumple`
(`calculos/puntaje.py:285-287`), no una medida de si la empresa resistiría una
auditoría. Aparece junto a «Puntaje ESG 40,8 / Nivel: inicial».

**Por qué es un problema.** Marcela mira el tablero, ve verde y «66,7 % listo
para auditoría», y decide que puede mandar todo. Dos documentos del mismo
producto dicen cosas opuestas y ella no tiene forma de saber cuál creer.

**Qué propondría.** Renombrar el indicador («Indicadores automáticos en verde:
6 de 9»); que «Cadena intacta» no aparezca con cero respaldos; y que el estado
por archivo refleje las filas caídas del último cálculo.

---

### H11 — El borrador Word repite la misma frase en cuatro secciones distintas

**Qué pasó.** En `reportes/borrador-vsme-2025.docx`, las secciones **B8**
(plantilla), **B9** (salud y seguridad), **B10** (remuneración, negociación
colectiva y formación) y **C5** (características adicionales) reciben
exactamente el mismo texto:

> «Planilla de personas: 12 personas (hombre 5, mujer 7); 3 contrataciones; 2
> desvinculaciones; 1 accidentes con tiempo perdido; 4 días perdidos.»

B10 pide brecha salarial y horas de formación. El motor **ya calculó** la brecha
(`brecha_pct: 5.3`, razón mujer/hombre 0,947) en `resultados/social_2025.json`,
pero el borrador no la usa. B9 pide accidentes y recibe también el recuento de
contrataciones.

También quedan detalles que descolocan: «1 **accidentes**» (concordancia) y, en
B3, «Planilla de consumos: **36 filas**» cuando solo 24 se usaron.

**Dónde.** `.claude/motor/modulos/reporte.py` (armado de las viñetas «Con los
datos de tu carpeta»).

**Por qué es un problema.** Es el documento que Marcela le manda al supermercado.
Leer cuatro veces la misma frase, una de ellas bajo el título «Remuneración»
hablando de accidentes, hace que el reporte parezca generado sin revisar — que es
justo la impresión contraria a la que busca.

**Qué propondría.** Una viñeta específica por contenido (B9 → accidentes y días
perdidos; B10 → brecha salarial y horas de capacitación) y singular/plural
correcto.

---

### H12 — Referencias rotas: dos skills que no existen y cuatro agentes sin registrar

**Qué pasó.**

- `huella-carbono/SKILL.md:97` termina proponiendo «preparar un reporte formal
  (`reportes`)». **No existe** ninguna skill `reportes`; el módulo del motor se
  llama `reporte` y ninguna skill lo cubre.
- `alcance-3/SKILL.md:56` dice «Para pedirlo usa la skill `proveedores`».
  **No existe.** Sí existe `.claude/agents/agente-proveedores.md`.
- `.claude-plugin/plugin.json` registra **6** agentes; en `.claude/agents/` hay
  **10**. Quedan fuera `agente-academia`, `agente-crm`, `agente-proveedores` y
  `agente-reportes`. Quien instale el plugin pierde cuatro agentes en silencio,
  incluido el de proveedores que la skill `alcance-3` necesita.

**Por qué es un problema.** El último paso de la skill más importante
(`huella-carbono`) apunta a la nada. Marcela pregunta «y el reporte formal, ¿cómo
lo hago?» y el asistente no tiene a dónde ir; el módulo `reporte borrador` existe
y funciona bien, pero nadie lo va a encontrar.

**Qué propondría.** Crear la skill `reportes` (envuelve `reporte marcos /
cobertura / borrador / indice`), corregir la referencia a `proveedores`, y una
prueba que verifique que toda skill o agente mencionado existe y está en
`plugin.json`.

---

### H13 — El gráfico del tablero mezcla el total anual con los meses

**Qué pasó.** «Emisiones por periodo» dibuja en el mismo eje el bucket **`2025`**
(31,1 t, que son las filas anuales del alcance 3) junto a `2025-01` … `2025-12`
(≈1,1 t cada uno). Queda una barra gigante y doce rayitas.

El informe de huella sí trae una nota («Los datos anuales… no aparecen aquí, pero
sí en el total») y excluye el bucket anual; el tablero no hace ni una cosa ni la
otra.

**Dónde.** `.claude/motor/modulos/tablero.py`.

**Por qué es un problema.** Marcela concluye que enero fue un mes catastrófico, o
que el gráfico está roto. No tiene cómo saber que «2025» no es un mes.

**Qué propondría.** Aplicar en el tablero el mismo filtro que ya usa el informe
de huella, o separar el anual en su propia barra etiquetada.

---

### H14 — Al primer «hola», el asistente saluda a un usuario nuevo con el nombre de una panadería ficticia chilena

**Qué pasó.** `asistente/SKILL.md:30` dice: «Si hay una [empresa], salúdala por
su nombre». Recién descomprimido, `empresa listar` devuelve exactamente una:
`Alimentos del Sur SpA` (CL), la empresa de ejemplo que viene en el repositorio.

**Por qué es un problema.** Marcela escribe «hola» y el producto le responde
saludando a una empresa chilena que no es la suya, con datos que no son los suyos
(85 trabajadores, planta en Chillán, exportación a Rotterdam). Su primera
impresión es que el programa se confundió o que sus datos se mezclaron con los de
otro. El `README` tampoco menciona que viene una empresa de ejemplo.

**Qué propondría.** Marcar la empresa de ejemplo en `empresa.json`
(`"es_ejemplo": true`), no contarla en `empresa listar` por defecto, y
mencionarla en el `README`.

---

### H15 — Hallazgos menores

1. **`datos anomalias` revisa solo `consumos.xlsx`.** El valor por defecto está
   fijado en `modulos/datos.py:100-101`. Dijo «No encontré datos raros» sin haber
   mirado `alcance3.xlsx` ni `personas.xlsx`. La skill `consultar-datos` lo
   presenta como la revisión general previa al cálculo.
2. **Un dato vacío se informa como cero.** Dejé «Horas de capacitación» en blanco
   y `social calcular` devolvió `horas_capacitacion: 0.0` y
   `horas_capacitacion_por_persona: 0.0`, sin advertencia (sí la hay para «horas
   trabajadas»). Eso llega al reporte como «0 horas de capacitación», que es una
   afirmación, no un vacío.
3. **`--ayuda` no muestra las opciones.** `esg.py --ayuda` lista módulos y
   acciones, pero ninguna opción (`--empresa`, `--periodo`, `--marco`,
   `--umbral`, `--pcg`…). No hay ayuda por módulo. Para saber qué acepta cada
   acción hay que leer el código.
4. **`huella factores` no está documentado** en ninguna skill, siendo la única
   forma de consultar qué factores existen (ver H8).
5. **El ejemplo de la skill `diagnostico-esg` usa un indicador chileno.** Las
   líneas 39 y 54 usan `--indicador soc-karin`, que para una empresa peruana no
   está en la lista de preguntas.
6. **La lista de países está incompleta para el alcance.** `nucleo/espacio.py:26`
   acepta 14 países; el `plugin.json` promete «la Unión Europea», pero de la UE
   solo está `ES`.

---

## Lo que funcionó bien

- **El motor nunca se cayó ni mostró un `Traceback`.** 44 llamadas, cero
  excepciones no controladas. Los errores salen como JSON con `error` y
  `sugerencia`.
- **Los mensajes de error están bien escritos** cuando la causa es clara: «Hay
  varias empresas registradas y no sé cuál usar», «No hay filas del periodo 2024
  en las planillas. Revisa la columna Periodo: debe decir el año (2025) o el mes
  (2025-03)».
- **No sobrescribe el trabajo de la persona.** Volver a crear una planilla
  existente falla con «Ya existe la planilla consumos.xlsx y no la voy a
  sobrescribir», y ofrece leerla tal como está.
- **El HTML es de buena calidad**: UTF-8 correcto, `<meta charset>`, responsive,
  se abre con doble clic y se imprime a PDF. Los colores salen de la marca del
  perfil.
- **El diagnóstico está bien pensado para una pyme**: 13 preguntas, en
  castellano cotidiano, cada una con «por qué importa» y «qué hacer primero», y
  se puede responder de a poco.
- **Las advertencias legales están donde deben.** Todos los entregables cierran
  con «es apoyo de gestión, no reemplaza asesoría legal ni una auditoría», y el
  diagnóstico aclara que el puntaje no es una calificación de mercado.
- **El módulo `evidencia` funciona y es honesto**: SHA-256 encadenado, y la
  skill aclara que no reemplaza una firma electrónica avanzada.
- **El borrador VSME en Word es un buen punto de partida**: separa lo que sale de
  los datos de lo que la empresa tiene que escribir, y marca cada sección como
  módulo básico o comprehensivo.
- **La investigación documental (`docs/investigacion/`) es sólida**, con fuentes,
  URLs y etiquetas de verificación. El problema es que no está conectada con el
  motor (ver H2: la densidad del GLP está documentada pero el conversor no la
  usa).

---

## Preguntas que Marcela habría hecho y el producto no responde

1. **«El supermercado me pide la huella **de mis productos**. ¿Cuánto CO2 tiene
   un pan?»** Todo el producto calcula la huella **de la organización**. No hay
   nada de huella de producto (ISO 14067, kg CO2e por kilo de pan), que es
   literalmente lo que le pidieron. Ningún módulo ni skill lo menciona, y nadie
   le explica la diferencia.
2. **«¿Está bien mi número? ¿Es mucho o poco para una panadería?»** No hay
   ninguna referencia sectorial ni intensidad por venta o por kilo producido. Las
   44,6 tCO2e no significan nada sin comparación.
3. **«Me dice que el GLP está en litros y yo lo compro en balones de 45 kilos.
   ¿Ahora qué hago?»** Sin respuesta. La densidad está en
   `docs/investigacion/01`, el conversor la rechaza y las reglas le prohíben al
   asistente inventar la conversión (ver H2).
4. **«¿Cuánto va a costar arreglar esto?»** El diagnóstico dice qué falta pero
   nunca cuánto cuesta ni cuánto demora. Para una panadería de 12 personas, «haz
   una matriz de riesgos» sin costo ni plazo es inaccionable.
5. **«¿Y ahora qué le mando al supermercado?»** Terminó el recorrido con seis
   archivos en `reportes/` y ninguna guía sobre cuál enviar, en qué orden o qué
   escribir en el correo. El producto no cierra el ciclo que lo originó.
6. **«¿Qué es VSME? ¿Es el que necesito?»** `reporte marcos` describe siete
   marcos, pero nadie le recomienda uno para su caso (pyme peruana, cliente
   nacional, no exporta a la UE). Yo elegí VSME —un marco **europeo**— sin que
   nada advirtiera que puede no ser el adecuado.
7. **«¿Tengo que tener protocolo de acoso?»** Sí: el módulo de cumplimiento
   detecta la Ley 27942 con riesgo alto. Pero el diagnóstico nunca se lo pregunta
   y la skill a la que la derivan habla de la ley chilena (H9).
8. **«¿Cómo mido el agua si nunca la he medido?»** El diagnóstico marca «Consumo
   de agua medido» como brecha y dice «Registrar los metros cúbicos de las
   boletas o del medidor», pero la plantilla de consumos no tiene fila de agua y
   la de alcance 3 la pide en m3 sin explicar de dónde sacarlos.
9. **«¿Esto lo puedo seguir el año que viene?»** No hay nada sobre comparar
   2025 con 2026, ni sobre recalcular cuando cambian los factores.
10. **«¿Quién revisa que esto esté bien?»** Todos los documentos dicen «no es una
    verificación», pero ninguno explica qué es una verificación, quién la hace ni
    cuándo le haría falta.

---

*Prueba realizada sobre una copia del repositorio. No se modificó código ni
skills: este documento es el único entregable.*
