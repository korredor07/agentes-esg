# Minería (relaves, seguridad y salud ocupacional, cierre de faenas) y huella hídrica

Fecha de investigación: 2026-09-16

> **Aviso de seguridad.** Este documento alimenta un motor de cálculo que puede generar alertas de
> seguridad para personas. Cada dato lleva su etiqueta de verificación. **Ningún valor etiquetado
> como `[NO VERIFICADO]` debe usarse para disparar o suprimir una alerta** sin validación humana
> contra la fuente oficial. Ante duda, el motor debe fallar hacia el lado conservador (más protector).

---

## Resumen

Investigación normativa vigente al **16 de septiembre de 2026** para el módulo de minería y agua de
**Agentes ESG**. Cubre ocho bloques y aporta los parámetros numéricos que alimentan el motor de cálculo
en Python (evaluación de relaves, ventilación, exposición química, huella hídrica AWARE).

**Los seis hallazgos que cambian el diseño del motor:**

1. **El DS 594 ya no corrige por jornada semanal.** Desde el **Decreto 123/2015** la corrección del
   Art. 62 es **diaria**: `Fj = (8/h) × ((24−h)/16)`, con `h` = horas trabajadas **por día**. La fórmula
   semanal `(48/h)·((168−h)/120)` que circula en manuales y PDF de 1999 **está derogada**. La corrección
   por altitud (`Fa = P/760`, Art. 63) se mantiene y **solo aplica a valores en mg/m³ y fibras/cc**,
   nunca a ppm; y **nunca se aplica Fj a los LPT ni a los LPA** (Art. 64).
2. **Los límites del DS 594 anteriores a 2015 son peligrosamente permisivos.** El arsénico pasó de
   0,16 a **0,01 mg/m³**. Cualquier base de datos del "DS 594 versión 1999" debe descartarse.
3. **El DS 594 se modificó el 16-ene-2026** (Decreto 40, MINSAL): nuevo **Art. 98 bis** con obligaciones
   frente a altas temperaturas y alertas de la DMC y SENAPRED, adicionales al índice TGBH clásico.
4. **Ni el DS 248 ni el DS 132 contienen niveles tipo TARP.** El TARP es una exigencia del **GISTM**
   (voluntario), no de la ley chilena. El DS 132 solo tiene un esquema binario de detención de equipos
   y retiro de personal; el DS 248 exige instrumentación y Manual de Emergencias, sin umbrales escalonados.
5. **Los factores AWARE 2.0 son CC BY 4.0: SÍ se pueden redistribuir** en el repositorio público con
   atribución. Pero AWARE 2.0 (abr-2025) **cambia todos los valores**, incluidos los promedios globales
   (no agrícola: 20 → **17,9**). Para minería corresponde el factor **no agrícola**, no el "unspecified".
6. **Hay tres reformas chilenas en curso** que el motor debe vigilar: el reemplazo del **DS 248** (consulta
   pública cerrada en ago-2024, sin publicar), el **DS 15/2026** que introduce la declaración jurada de
   cierre para faenas ≤ 5.000 t/mes (en toma de razón al 30-abr-2026), y la **Ley 21.770** (LMAS) que
   modifica la Ley 20.551 con vigencia diferida.

**Parámetros numéricos de referencia rápida:**

| Ámbito | Parámetro | Valor | Fuente |
|---|---|---|---|
| Relaves CL | Factor de seguridad mínimo | **1,2** | DS 248, Art. 14 o) |
| Relaves CL | Revancha mínima | **1 m** | DS 248, Art. 49 |
| Relaves CL | Método aguas arriba | **Prohibido** | DS 248, Art. 14 h) |
| Cierre CL | Umbral régimen general | **> 10.000 t brutas/mes** | Ley 20.551, Art. 10 |
| Cierre CL | Umbral declaración simplificada | **≤ 5.000 t/mes** | Ley 20.551, Art. 16 |
| Ventilación CL | Aire por persona | **3 m³/min** | DS 132, Art. 138 |
| Ventilación CL | Aire por HP diésel | **2,83 m³/min·HP** | DS 132, Art. 132 |
| Ventilación CL | Velocidad del aire | **15 – 150 m/min** | DS 132, Art. 138 |
| Ventilación CL | Oxígeno mínimo | **19,5 % en peso** | DS 132, Art. 144 |
| Ventilación CL | Detención por CO / NOx / HCHO | **40 / 20 / 1,6 ppm** | DS 132, Art. 135 |
| Higiene CL | Sílice cuarzo respirable | **0,08 mg/m³** | DS 594, Art. 66 |
| Higiene CL | Ruido, jornada 8 h | **85 dB(A)**, intercambio **3 dB** | DS 594, Arts. 74–75 |
| Higiene CL | TGBH trabajo continuo, carga pesada | **25,0 °C** | DS 594, Art. 96 |
| GISTM | Estructura | 6 temas · 15 principios · **77 requisitos** | Global Tailings Review |
| Agua | AWARE 2.0 Chile, no agrícola, anual | **45,5** | Zenodo, CC BY 4.0 |
| Agua | Zona con estrés hídrico (GRI 303) | *baseline water stress* **≥ 40 %** | GRI 303 · WRI Aqueduct 4.0 |
| Agua CL | Plazo MEE estándar Mayor | **4 meses** medición / **5 meses** transmisión | Res. DGA 1238/2019 |

Secciones: 1 GISTM · 2 DS 248/2007 · 3 Ley 20.551 y DS 41/2012 · 4 DS 594/1999 · 5 DS 132/2002 ·
6 ISO 14046 y AWARE · 7 GRI 303 · 8 Ley 21.435 y monitoreo DGA · Fórmulas y métodos ·
Cambios recientes · Pendientes y dudas · Fuentes.

---

## 1. GISTM — Estándar Global de Gestión de Relaves para la Industria Minera

### 1.1 Identificación y vigencia

| Atributo | Valor | Etiqueta |
|---|---|---|
| Nombre | Global Industry Standard on Tailings Management (GISTM) / Estándar Global de Gestión de Relaves para la Industria Minera | [VERIFICADO] |
| Publicación | 5 de agosto de 2020 | [VERIFICADO] |
| Promotores | Global Tailings Review: PNUMA (UNEP), PRI (Principios de Inversión Responsable) e ICMM | [VERIFICADO] |
| Estructura | 6 temas · 15 principios · **77 requisitos auditables** | [VERIFICADO] |
| Anexos | Anexo 1 (criterios de diseño), Anexo 2 (matriz de clasificación por consecuencias), Anexo 3 (tablas resumen de roles), glosario | [VERIFICADO] |
| Versión vigente a 2026-09-16 | La de agosto de 2020; **no se ha publicado una revisión del texto del Estándar** | [VERIFICADO] |
| Naturaleza jurídica | Estándar voluntario de industria. **No es ley en Chile, Perú ni la UE.** Obliga contractualmente a miembros ICMM y a signatarios del GTMI | [VERIFICADO] |

> **Nota metodológica.** El texto del GISTM es propiedad de la Global Tailings Review. Aquí solo se
> resumen sus contenidos con palabras propias y se citan datos estructurales (números, categorías,
> umbrales de tablas), no redacción literal.

### 1.2 Los 6 temas y los 15 principios (títulos resumidos)

Agrupación oficial tema → principios, según la versión en español del Estándar.

| Tema | Principios | Principio — título resumido (paráfrasis) | N.º requisitos |
|---|---|---|---|
| **I. Comunidades afectadas** | 1 | **P1** — Respetar los derechos de las personas afectadas por el proyecto y asegurar su participación significativa durante todo el ciclo de vida de la instalación, incluido el cierre | 4 (1.1–1.4) |
| **II. Base de conocimientos integrada** | 2 | **P2** — Construir y mantener una base de conocimientos interdisciplinaria (social, ambiental, económica y técnica) que sustente la gestión segura de relaves en todo el ciclo de vida | 4 (2.1–2.4) |
| | 3 | **P3** — Usar todos los elementos de esa base de conocimientos para fundamentar las decisiones a lo largo del ciclo de vida, incluido el cierre | 4 (3.1–3.4) |
| **III. Diseño, construcción, operación y monitoreo de la instalación de relaves** | 4 | **P4** — Desarrollar planes y criterios de diseño que minimicen el riesgo en todas las fases, incluidos cierre y poscierre | 8 (4.1–4.8) |
| | 5 | **P5** — Desarrollar un diseño sólido que integre la base de conocimientos y minimice el riesgo de falla para las personas y el ambiente (criterio ALARP) | 8 (5.1–5.8) |
| | 6 | **P6** — Planificar, construir y operar la instalación gestionando el riesgo en todas las fases del ciclo de vida | 6 (6.1–6.6) |
| | 7 | **P7** — Diseñar, implementar y operar sistemas de monitoreo para gestionar el riesgo en todas las fases | 5 (7.1–7.5) |
| **IV. Gestión y gobernanza** | 8 | **P8** — Establecer políticas, sistemas y rendición de cuentas (*accountability*) que respalden la seguridad e integridad de la instalación | 8 (8.1–8.8) |
| | 9 | **P9** — Nombrar y dotar de facultades a un **Ingeniero de Registro (IDR / EoR)** | 5 (9.1–9.5) |
| | 10 | **P10** — Establecer e implementar **niveles de revisión** independiente como parte de un sistema robusto de gestión de riesgo y calidad | 7 (10.1–10.7) |
| | 11 | **P11** — Desarrollar una cultura organizacional que promueva el aprendizaje, la comunicación y la detección temprana de problemas | 5 (11.1–11.5) |
| | 12 | **P12** — Establecer un canal para reportar y atender inquietudes, con protección a denunciantes (*whistleblowers*) | 2 (12.1–12.2) |
| **V. Respuesta ante emergencias y recuperación a largo plazo** | 13 | **P13** — Estar preparado para la respuesta ante emergencias en caso de falla de la instalación | 4 (13.1–13.4) |
| | 14 | **P14** — Prepararse para la recuperación a largo plazo ante una falla catastrófica | 5 (14.1–14.5) |
| **VI. Divulgación pública y acceso a la información** | 15 | **P15** — Hacer pública y accesible la información sobre las instalaciones de relaves para respaldar la rendición de cuentas | 3 (15.1–15.3) |

- Etiqueta de la agrupación tema→principio y de los títulos: **[VERIFICADO]** contra el texto oficial en
  español del Estándar (Global Tailings Review) [F1].
- **Distribución de requisitos por principio: [SECUNDARIO]** — obtenida por conteo automático sobre
  el PDF oficial en español. El conteo arroja **78** etiquetas `Requisito X.Y` (1.1 … 15.3), mientras que
  ICMM y la Global Tailings Review declaran oficialmente **77 requisitos auditables**. Ver
  *Pendientes y dudas*. **Para el motor: usar 77 como total oficial**; no usar la distribución por
  principio como criterio de conformidad.

### 1.3 Matriz de clasificación por consecuencias (Anexo 2, Tabla 1)

Cinco categorías. La clasificación se asigna **por la consecuencia más alta obtenida en cualquiera de
las cinco dimensiones** evaluadas (no por promedio). **[VERIFICADO]** [F1].

**Dimensiones A y B — población y vidas:**

| Clasificación | Población potencial en riesgo (personas) | Pérdida potencial de vidas |
|---|---|---|
| **Baja** | Ninguna | Ninguna esperada |
| **Significativa** | 1 – 10 | Sin especificar |
| **Alta** | 10 – 100 | Posible (1 – 10) |
| **Muy alta** | 100 – 1.000 | Probable (10 – 100) |
| **Extrema** | > 1.000 | Muchas (más de 100) |

**Dimensiones C, D y E — pérdidas incrementales (resumen):**

| Clasificación | Medio ambiente | Salud, ámbito cultural y social | Infraestructura y economía |
|---|---|---|---|
| **Baja** | Pérdida mínima y de corto plazo de hábitat o especies raras/en peligro | Efectos mínimos; sin efecto medible en salud humana; sin alteración de patrimonio ni bienes comunitarios | Pérdidas económicas bajas; escasa infraestructura o servicios en el área. **< USD 1 M** |
| **Significativa** | Sin pérdida significativa de hábitat; posible contaminación de agua para ganado/fauna sin efectos en salud; aguas de proceso de baja toxicidad; relaves sin potencial de generación de ácido; restauración en 1–5 años | Interrupción significativa de actividades económicas y servicios, o desintegración del tejido social; baja probabilidad de pérdida de patrimonio regional; baja probabilidad de efectos en salud | Pérdidas en instalaciones recreativas, lugares de trabajo estacionales y rutas de transporte poco usadas. **< USD 10 M** |
| **Alta** | Pérdida significativa de hábitat crítico o especies raras/en peligro; agua de proceso moderadamente tóxica; bajo potencial de drenaje ácido o lixiviación de metales; área de impacto **10–20 km²**; restauración difícil, > 5 años | **500–1.000 personas** afectadas por interrupción de actividad económica/servicios o desintegración del tejido social; perturbación de patrimonio regional; posibles efectos en salud a corto plazo | Grandes pérdidas económicas en infraestructura, transporte público, instalaciones comerciales o empleo; reubicación o indemnización moderada. **< USD 100 M** |
| **Muy alta** | Pérdida importante de hábitat crítico o especies raras/en peligro; aguas de proceso altamente tóxicas; alta posibilidad de drenaje ácido o lixiviación de metales; área de impacto **> 20 km²**; restauración muy difícil, 5–20 años | **> 1.000 personas** afectadas por más de un año; destrucción significativa de patrimonio nacional o bienes culturales; posibles efectos significativos en salud a largo plazo | Pérdidas muy grandes en obras de infraestructura o servicios importantes (autopistas, instalaciones industriales, almacenamiento de sustancias peligrosas) o empleo; reubicación/compensación importante. **< USD 1 B** |
| **Extrema** | Pérdida catastrófica de hábitat crítico o especies raras/en peligro; aguas de proceso altamente tóxicas; muy alta posibilidad de drenaje ácido o lixiviación; área de impacto **> 20 km²**; restauración imposible o **> 20 años** | **> 5.000 personas** afectadas durante años; destrucción significativa de patrimonio o bienes culturales nacionales; posibles efectos graves y/o de largo plazo en salud humana | Pérdidas económicas extremas en infraestructura o servicios críticos (hospitales, grandes complejos industriales, grandes depósitos de sustancias peligrosas) o empleo; reubicación/compensación muy importante y costos de reajuste social muy altos. **> USD 1 B** |

> **Uso en el motor de cálculo.** La clasificación resultante es `max(clase_A, clase_B, clase_C, clase_D, clase_E)`.
> Las bandas monetarias de la última columna son **acumulativas hacia arriba** (`< USD 1 M`, `< USD 10 M`, …),
> es decir, se debe asignar la banda más baja cuya cota superior no sea excedida.

### 1.4 Criterios de diseño por clasificación (Anexo 1, Tablas 2 y 3)

Probabilidad de excedencia anual para el diseño. **[VERIFICADO]** [F1].

| Clasificación | **Crecidas** — Operación y cierre (cuidado activo) | **Crecidas** — Poscierre (cuidado pasivo) | **Sísmico** — Operación y cierre | **Sísmico** — Poscierre |
|---|---|---|---|---|
| Baja | 1/200 | 1/10.000 | 1/200 | 1/10.000 |
| Significativa | 1/1.000 | 1/10.000 | 1/1.000 | 1/10.000 |
| Alta | 1/2.475 | 1/10.000 | 1/2.475 | 1/10.000 |
| Muy alta | 1/5.000 | 1/10.000 | 1/5.000 | 1/10.000 |
| Extrema | 1/10.000 | 1/10.000 | 1/10.000 | 1/10.000 |

Notas del Estándar (resumidas): los conceptos de **PMP** (Precipitación Máxima Probable) y **CMP**
(Crecida Máxima Probable) son aceptables si igualan o superan los criterios anteriores para la clase
Extrema y/o poscierre; la selección del sismo de diseño debe considerar el ambiente tectónico y la
aplicabilidad de métodos probabilísticos y determinísticos (el **MCE**, sismo máximo creíble, puede
ser controlante en algunas zonas); para instalaciones existentes, el Ingeniero de Registro con revisión
de la CIRR puede determinar que la actualización retroactiva no es factible, en cuyo caso el
Ejecutivo Responsable debe aprobar y documentar medidas para llevar el riesgo a **ALARP**.

### 1.5 Plazos de conformidad y estado (ICMM / GTMI)

| Hito | Fecha | Alcance | Etiqueta |
|---|---|---|---|
| Publicación del GISTM | 05-ago-2020 | — | [VERIFICADO] |
| Conformidad exigida a miembros ICMM (1.ª ola) | **05-ago-2023** | Instalaciones con clasificación **Extrema** o **Muy alta** | [VERIFICADO] |
| Conformidad exigida a miembros ICMM (2.ª ola) | **05-ago-2025** | Todas las demás instalaciones aplicables no en cierre seguro | [VERIFICADO] |
| Divulgaciones anuales de miembros ICMM | agosto de cada año | Requisito 15.1 del Estándar | [VERIFICADO] |
| Informe agregado de avance ICMM | **04-nov-2025** | 836 instalaciones de miembros ICMM | [VERIFICADO] |

**Estado a noviembre de 2025 (ICMM Tailings Progress Report)** [F4]:

| Indicador | Valor | Etiqueta |
|---|---|---|
| Instalaciones de miembros ICMM cubiertas | 836 | [VERIFICADO] |
| En **conformidad total** | 67 % | [VERIFICADO] |
| En **conformidad parcial** | 33 % | [VERIFICADO] |
| Conformidad total en clase **Extrema** y **Muy alta** | > 80 % | [VERIFICADO] |
| Conformidad total en clases **Alta / Significativa / Baja** | 53 % – 65 % | [VERIFICADO] |

ICMM reconoce que la alineación plena está tomando más tiempo del previsto y reafirma el compromiso,
pero **no anunció un nuevo plazo formal**. [VERIFICADO] [F4].

### 1.6 Protocolos de conformidad ICMM

| Atributo | Valor | Etiqueta |
|---|---|---|
| Documento | *Conformance Protocols: Global Industry Standard on Tailings Management* (ICMM) | [VERIFICADO] |
| Función | Marco estructurado para que operadores y terceros independientes evalúen la implementación y demuestren conformidad | [VERIFICADO] |
| Mapeo | Traduce los **77 requisitos** del Estándar en **219 criterios** de evaluación | [VERIFICADO] |
| Guía complementaria | *Tailings Management: Good Practice Guide* (ICMM) | [VERIFICADO] |

### 1.7 GTMI — Global Tailings Management Institute (2025–2026)

| Hito | Fecha | Detalle | Etiqueta |
|---|---|---|---|
| Lanzamiento del GTMI | enero de 2025 | Institución independiente sin fines de lucro, con sede en Sudáfrica. Fundadores: ICMM, PNUMA y PRI | [VERIFICADO] |
| Rol | — | Supervisar la implementación y la conformidad con el GISTM; acreditar y formar auditores independientes; abrir el régimen a **signatarios** más allá de los miembros ICMM | [VERIFICADO] |
| CEO inaugural y Comité Técnico | febrero de 2026 | Ed Toms designado CEO; se constituye el Comité Técnico (protocolos de auditoría, acreditación, formación e interpretación del GISTM) | [VERIFICADO] |
| Reunión del Comité Técnico | junio de 2026 (Canadá) | Discusión del marco de aseguramiento (protocolos de verificación de conformidad) | [SECUNDARIO] |
| Convocatoria de auditores y certificación | **pendiente a 2026-09-16** | Una vez finalizados los protocolos se abrirá la convocatoria de auditores y el proceso de formación/certificación; luego se invitará a mineras y empresas estatales a ser signatarias | [SECUNDARIO] |

> **Implicancia para el motor.** A la fecha de esta investigación **no existe aún un esquema de
> certificación GISTM operativo de terceros**. Cualquier afirmación de "certificación GISTM" de una
> empresa debe tratarse como **autodeclaración o aseguramiento privado**, no como certificación del GTMI.

---

## 2. Chile — DS 248/2007, Reglamento de depósitos de relaves

### 2.1 Identificación

| Atributo | Valor | Etiqueta |
|---|---|---|
| Norma | Decreto Supremo N.º 248, Ministerio de Minería | [VERIFICADO] |
| Título | Reglamento para la aprobación de proyectos de diseño, construcción, operación y cierre de los depósitos de relaves | [VERIFICADO] |
| Publicación (Diario Oficial) | 11 de abril de 2007 | [VERIFICADO] |
| Norma derogada | DS N.º 86 de 1970 (antiguo reglamento de construcción y operación de tranques de relaves) | [VERIFICADO] |
| Organismo fiscalizador | **SERNAGEOMIN** (Servicio Nacional de Geología y Minería) | [VERIFICADO] |
| Estructura | 8 títulos; **59 artículos permanentes + 2 transitorios** | [SECUNDARIO] |
| Versión vigente a 2026-09-16 | Texto original de 2007; **sin modificaciones publicadas** (ver §2.6) | [VERIFICADO] |

Títulos: I Disposiciones Generales · II Procedimientos de Aprobación · III Construcción ·
IV Operación y Mantención · V Cierre Temporal, Definitivo y Reanudación · VI Criterios de Control ·
VII Sanciones · Título Final. **[SECUNDARIO]**

### 2.2 Factores de seguridad exigidos

| Parámetro | Valor exacto | Unidad | Artículo | Etiqueta |
|---|---|---|---|---|
| Factor de seguridad mínimo del análisis de estabilidad (Fases I y II) | **1,2** | adimensional | **Art. 14, letra o)** | [VERIFICADO] |

**Fases del análisis de estabilidad exigidas por el Art. 14 letra o)** (paráfrasis del texto legal):

| Fase | Contenido | Etiqueta |
|---|---|---|
| **Fase I** | Simulación de estabilidad estática (análisis pseudo-estáticos) **asumiendo licuefacción total de los relaves de la cubeta** | [VERIFICADO] |
| **Fase II** | Simulación de estabilidad estática (análisis pseudo-estáticos) con **determinación simplificada de las presiones de poros** | [VERIFICADO] |
| **Fase III** | **Análisis dinámicos** basados en ensayos de propiedades dinámicas de los suelos | [VERIFICADO] |
| **Fase IV** | Análisis para la **condición de cierre**, incluyendo eventos solicitantes máximos | [VERIFICADO] |

Cita textual breve del reglamento (permitida por tratarse de texto legal):

> «El factor de Seguridad resultante del cálculo de las fases anteriores, no debe ser menor de uno coma
> dos (1,2). Para el caso de depósitos pequeños (con muros menores de 15 metros de alto) cumplida esta
> condición, no será necesario cumplir la fase III.» — DS 248/2007, Art. 14 letra o). **[VERIFICADO]**

**Regla derivada para el motor:**

```
FS_min = 1.2                      # aplicable a Fase I y Fase II
exige_fase_III = (altura_muro_m >= 15) or (FS_calculado < 1.2)
# "depósito pequeño" = muro de contención < 15 m de altura
```

> **Advertencia importante.** El DS 248 fija **un único FS mínimo explícito de 1,2** para las fases
> pseudo-estáticas descritas. **No se ha verificado** que el reglamento fije un FS estático puro
> distinto (por ejemplo 1,4 o 1,5), valor que sí es común en la práctica internacional
> (CDA, ANCOLD). **No se debe asumir 1,4/1,5 como exigencia del DS 248.** Ver *Pendientes y dudas*.

**Sismo de diseño:** el **Art. 14 letra p)** exige obtener el sismo de diseño a partir de estadísticas de
zonas sismogénicas, para estimar la aceleración máxima en la zona de emplazamiento. El reglamento
**no fija un valor numérico único de coeficiente sísmico** en el texto revisado. **[VERIFICADO]**
(ausencia de valor numérico verificada por búsqueda en el texto).

### 2.3 Revancha mínima

| Parámetro | Valor exacto | Unidad | Artículo | Etiqueta |
|---|---|---|---|---|
| Revancha mínima en depósitos de relaves | **1** | metro (m) | **Art. 49** | [VERIFICADO] |

> «La Revancha en los depósitos de relaves debe ser, como mínimo, de un (1) metro.» — DS 248/2007, Art. 49.

El propio artículo admite que fenómenos climáticos pueden exigir una revancha mayor, por lo que **1 m
es un piso absoluto, no un objetivo de diseño**. El motor debe tratar `revancha < 1 m` como
**no conformidad grave** y `1 m ≤ revancha < revancha_diseño` como **alerta**.

### 2.4 Métodos constructivos

| Método | Estado en DS 248 | Artículo | Etiqueta |
|---|---|---|---|
| **Aguas arriba** (*upstream*) | **PROHIBIDO** | **Art. 14, letra h)** | [VERIFICADO] |
| Aguas abajo (*downstream*) | Permitido (no prohibido) | — | [VERIFICADO] (por ausencia de prohibición) |
| Eje central (*centerline*) | Permitido (no prohibido) | — | [VERIFICADO] (por ausencia de prohibición) |

> «Se prohíbe la utilización del método aguas arriba.» — DS 248/2007, Art. 14 letra h).
> Búsqueda exhaustiva del texto: esta es **la única** aparición de la expresión "aguas arriba" en el
> reglamento, por lo que **la prohibición es absoluta y sin excepciones explícitas** en el DS 248.

**Muro de partida — Art. 54:** el muro de inicio o muro de partida debe tener una altura mínima
equivalente a **1/10 de la altura final** del muro de contención proyectado, **con un mínimo de 2 metros**.
**[VERIFICADO]**

```
h_muro_partida_min_m = max(0.10 * altura_final_muro_m, 2.0)
```

### 2.5 Monitoreo, reportes y emergencias

| Obligación | Contenido | Artículo | Etiqueta |
|---|---|---|---|
| **Instrumentación** | El proyecto debe describir la instrumentación para medir presiones de poros, niveles freáticos, desplazamientos y aceleraciones sísmicas | **Art. 14, letra n)** | [VERIFICADO] |
| **Informe trimestral** | El usuario debe enviar a SERNAGEOMIN un informe trimestral sobre la operación y mantención del depósito | **Art. 30** | [VERIFICADO] |
| **Manual de Emergencias** | El usuario debe elaborar y mantener **actualizado** el Manual de Emergencias del depósito | **Art. 34** | [VERIFICADO] |
| **Notificación de emergencia** | El usuario debe notificar **de inmediato** al Servicio la ocurrencia de cualquier emergencia | **Art. 35** | [VERIFICADO] |
| **Cierre** | Régimen de cierre temporal, definitivo y reanudación | **Título V (Arts. 39–47 aprox.)** | [SECUNDARIO] |

**Frecuencia de reporte para el motor:**

```
reporte_sernageomin = "trimestral"     # Art. 30 DS 248/2007
plazo_notificacion_emergencia = "inmediato"   # Art. 35 DS 248/2007 (sin plazo en horas explícito)
```

> **No existe en el DS 248 un esquema de niveles tipo TARP** (*Trigger Action Response Plan*) con
> umbrales verde/amarillo/naranja/rojo como los exige el GISTM (Requisitos del Principio 7). El
> DS 248 exige instrumentación (Art. 14 n) y Manual de Emergencias (Art. 34), pero **no define
> niveles de activación escalonados ni umbrales numéricos de instrumentación**. **[VERIFICADO]**
> (ausencia verificada por búsqueda sobre el texto completo). Un TARP en Chile es, por tanto,
> buena práctica GISTM y no una exigencia reglamentaria del DS 248.

### 2.6 Modificaciones posteriores y estado a 2026

| Hito | Fecha | Detalle | Etiqueta |
|---|---|---|---|
| Consulta ciudadana de modificación | Res. Ex. N.º 625, publicada **04-mar-2021** (30 días de comentarios) | Ampliar alcance a "disposición y almacenamiento de relaves"; énfasis en estabilidad física y química; incluir reprocesamiento de relaves existentes; sistema de gestión con planificación, evaluación de desempeño y reporte | [SECUNDARIO] |
| **Nueva consulta pública de reglamento de reemplazo** | **Res. Ex. N.º 1706 de 2024, Ministerio de Minería, publicada en el Diario Oficial el 05-jul-2024**. Plazo de observaciones hasta el **12-ago-2024** | Propuesta de **nuevo reglamento que reemplazaría el DS 248/2007**, alineado con estándares internacionales de ingeniería de relaves y con la experiencia nacional e internacional en estudios de falla | [VERIFICADO] |
| Publicación del nuevo reglamento | **No verificada a 2026-09-16** | No se encontró evidencia de publicación en el Diario Oficial de un decreto que derogue o reemplace el DS 248/2007 | [NO VERIFICADO] |

> **Regla operativa para el motor:** mientras no se publique el reglamento de reemplazo, **el DS 248/2007
> sigue vigente en su texto original**. El agente debe advertir al usuario que existe una reforma en
> tramitación desde 2024 y sugerir verificar el estado antes de decisiones de inversión de largo plazo.

---

## 3. Chile — Ley 20.551 (cierre de faenas e instalaciones mineras) y su reglamento

### 3.1 Identificación y vigencia

| Norma | Publicación | Última modificación relevante | Etiqueta |
|---|---|---|---|
| **Ley N.º 20.551**, Regula el cierre de faenas e instalaciones mineras | **11-nov-2011** (promulgada 28-oct-2011); entrada en vigencia **11-nov-2012** | Ley 21.169 (**18-jul-2019**); **Ley 21.770, art. 97 (D.O. 29-sep-2025)** con vigencia diferida | [VERIFICADO] |
| **DS N.º 41 de 2012**, Ministerio de Minería — Reglamento de la Ley de Cierre | **22-nov-2012** (promulgado 04-sep-2012) | DS N.º 6 de 2020 (D.O. 23-jun-2020); **DS N.º 15 de 2026** (ver §3.6) | [VERIFICADO] |

Estructura del DS 41/2012: Título I Disposiciones Generales · II Presentación y Aprobación del Plan de
Cierre · III Paralización Temporal de Faenas · IV Auditorías de Planes de Cierre · V Actualización del
Plan de Cierre. **[SECUNDARIO]**

### 3.2 Plan de cierre — obligación y contenido

| Aspecto | Contenido | Artículo | Etiqueta |
|---|---|---|---|
| Objetivo | Integrar y ejecutar el conjunto de medidas y acciones destinadas a mitigar los efectos de la actividad minera, asegurando **estabilidad física y química**; implementación progresiva durante toda la vida útil | **Ley 20.551, Art. 2** | [VERIFICADO] |
| Obligación | Toda empresa minera debe presentar, para aprobación del Servicio, un plan de cierre elaborado en conformidad con la Resolución de Calificación Ambiental (RCA) | **Ley 20.551, Art. 6** | [VERIFICADO] |
| Contenido mínimo (procedimiento general) | Identificación de la empresa; descripción de la faena; RCA; informe técnico sobre **vida útil**; medidas de cierre propuestas; **estimación de costos**; programa de **post cierre**; garantía; documentos de fundamento; programa de difusión comunitaria | **Ley 20.551, Art. 13** | [VERIFICADO] |
| Capítulo de garantías en el plan | El plan de cierre debe incluir un capítulo de garantías | **DS 41/2012, Art. 14 letra l)** | [VERIFICADO] |
| Costos | Deben expresarse en **Unidades de Fomento (UF)** | **DS 41/2012, Art. 14** | [SECUNDARIO] |

### 3.3 Régimen general vs. simplificado — umbrales

| Régimen | Umbral (capacidad de extracción de mineral) | Artículo | Etiqueta |
|---|---|---|---|
| **Procedimiento de aplicación general** | **> 10.000 toneladas brutas mensuales por faena minera** | **Ley 20.551, Art. 10** (y DS 41/2012, Art. 12) | [VERIFICADO] |
| **Procedimiento simplificado** | **≤ 10.000 t brutas mensuales** por faena, y actividades de exploración/prospección | **Ley 20.551, Arts. 10 y 16** (y DS 41/2012, Art. 28) | [VERIFICADO] |
| **Declaración simplificada** (sub-régimen) | **≤ 5.000 t mensuales**, sin plantas de producción ni depósitos de relaves | **Ley 20.551, Art. 16** | [VERIFICADO] |

Cita textual del umbral (texto legal):

> «Se sujetará al procedimiento de aplicación general la empresa minera cuyo fin sea la extracción o
> beneficio de uno o más yacimientos mineros, y cuya capacidad de extracción de mineral sea superior a
> diez mil toneladas brutas (10.000 t) mensuales por faena minera.» — Ley 20.551, Art. 10.

```python
def regimen_cierre(t_mensuales_brutas, tiene_planta, tiene_relaves):
    if t_mensuales_brutas > 10_000:
        return "general"                 # Art. 10 Ley 20.551
    if t_mensuales_brutas <= 5_000 and not tiene_planta and not tiene_relaves:
        return "declaracion_simplificada"  # Art. 16 Ley 20.551 / DS 15/2026
    return "simplificado"                # Art. 10 y 16 Ley 20.551
```

Contenido del plan en el **procedimiento simplificado**: solo los antecedentes de los literales a), b) y e)
del Art. 13, conforme a las guías metodológicas de SERNAGEOMIN (**Art. 16**). La resolución que se
pronuncia sobre estos planes se regula en el **Art. 17**. **[VERIFICADO]**

### 3.4 Garantía financiera

| Aspecto | Contenido | Artículo | Etiqueta |
|---|---|---|---|
| Quién debe constituirla | Empresas sujetas al **procedimiento de aplicación general** (> 10.000 t/mes) | Ley 20.551, Título V | [VERIFICADO] |
| Monto | **Valor presente** de los costos de implementación de todas las medidas de cierre hasta el término de la vida útil, **más** las medidas de post cierre; incluye costos administrativos; permite descontar proporcionalmente garantías ya constituidas conforme al Código de Aguas (Art. 297) | **Ley 20.551, Art. 50** | [VERIFICADO] |
| Tasa de descuento | Tasa de los **Bonos del Banco Central en Unidades de Fomento (BCU)**, plazo mínimo 10 años (BCU-10) | **Ley 20.551, Art. 50** | [VERIFICADO] |
| Instrumentos **Categoría A.1** | Certificados de depósito a la vista; boletas bancarias de garantía a la vista; certificados de depósito a menos de 360 días; cartas de crédito *stand by* (emisor con clasificación mínima A); **pólizas de garantía a primer requerimiento** de aseguradoras nacionales (incorporadas por Ley 21.169/2019; clasificación de riesgo BBB o superior; sin limitaciones para su cobro y pago; indemnización pagadera a SERNAGEOMIN a su solo requerimiento) | **Ley 20.551, Art. 52** | [VERIFICADO] |
| Custodia | Depósito Central de Valores o institución financiera autorizada | Ley 20.551, Art. 52 | [VERIFICADO] |
| Integridad | La empresa debe velar por la integridad, suficiencia y estabilidad de la garantía durante toda la vida útil; **3 días hábiles** para informar contingencias; **30 días** para que el Servicio resuelva | **Ley 20.551, Art. 51** | [VERIFICADO] |
| Plazo de constitución inicial | **30 días** desde la aprobación del plan de cierre | Ley 20.551, Título V | [SECUNDARIO] |
| Garantía adicional en paralización temporal excepcional (3.er período) | Monto adicional equivalente al **30 % del total inicial**, en instrumentos tipo A.1 | **DS 41/2012, Art. 34** | [SECUNDARIO] |

**Constitución por parcialidades** (guía metodológica oficial de SERNAGEOMIN):

| Parámetro | Valor | Etiqueta |
|---|---|---|
| Plazo total de constitución (N) si vida útil **< 20 años** | **2/3 de la vida útil** | [VERIFICADO] |
| Plazo total de constitución (N) si vida útil **≥ 20 años** | **15 años** | [VERIFICADO] |
| Primera parcialidad | **20 % del VPT** (valor presente total) | [SECUNDARIO] |
| Parcialidades siguientes | Progresión lineal del 20 % al 100 % del VPT a lo largo de N períodos | [SECUNDARIO] |

> **Advertencia.** La estructura de la progresión (`0,2 + 0,8·(i−1)/(N−1)`) se obtuvo de la guía oficial
> de SERNAGEOMIN, pero la extracción de texto del PDF quedó degradada. **Verificar visualmente antes
> de usarla en cálculos con consecuencias financieras.** El plazo (2/3 de la vida útil o 15 años) sí
> aparece de forma consistente en la guía y en fuentes secundarias.

### 3.5 Rol de SERNAGEOMIN, auditorías y fondo post cierre

| Función | Contenido | Artículo | Etiqueta |
|---|---|---|---|
| Rol del Servicio | Revisar y aprobar los aspectos técnicos y económicos de los planes; supervisar la suficiencia de las garantías y autorizar rebajas; elaborar el programa de fiscalización; disponer modificaciones y actualizaciones; aplicar sanciones administrativas | **Ley 20.551, Art. 5** (y DS 41/2012, Art. 3) | [VERIFICADO] |
| **Auditoría periódica** | **Cada 5 años** para empresas del procedimiento de aplicación general, **a costa de la empresa** | **Ley 20.551, Art. 18** (y DS 41/2012, Art. 44) | [VERIFICADO] |
| Auditoría extraordinaria | Procede ante deficiencias graves | DS 41/2012, Título IV | [SECUNDARIO] |
| Auditoría final | Obligatoria una vez completado el cierre | DS 41/2012, Título IV | [SECUNDARIO] |
| Actualización del plan | **90 días** desde la notificación de la resolución de auditoría para presentar el proyecto de actualización; **60 días** para que el Servicio resuelva | **Ley 20.551, Art. 23** | [VERIFICADO] |
| **Fondo para la Gestión de Faenas Mineras Cerradas** (fondo post cierre) | Creación, administración y formación del Fondo; aporte obligatorio antes de obtener el certificado de cierre; efectos del aporte | **Ley 20.551, Arts. 55–57** (Título XIV) | [SECUNDARIO] |
| Destino de multas | El producto de las multas aplicadas a las empresas mineras integra el Fondo | **Ley 20.551, Art. 43** | [SECUNDARIO] |

### 3.6 Cambios 2024–2026

| Hito | Fecha | Contenido | Etiqueta |
|---|---|---|---|
| **Ley 21.770** — Ley Marco de Autorizaciones Sectoriales (LMAS) | D.O. **29-sep-2025** | Su **art. 97** modifica la Ley 20.551. Crea el sistema SUPER (ventanilla única), la OASI y el Comité de Autorizaciones Sectoriales e Inversión; introduce **técnicas habilitantes alternativas** (entre ellas la declaración jurada). Vigencia **diferida**: las modificaciones a cuerpos legales sectoriales rigen conforme a los reglamentos que deben dictarse en plazos de 1 a 12 meses desde la publicación | [VERIFICADO] |
| **DS N.º 15 de 2026**, Ministerio de Minería | En toma de razón de Contraloría al **30-abr-2026** | Modifica el **Reglamento de la Ley de Cierre (DS 41/2012)** para adecuarlo a la LMAS. Innovación principal: la **declaración jurada** como mecanismo habilitante alternativo para faenas con capacidad **≤ 5.000 t/mes**; su presentación produce **los mismos efectos que la aprobación de un Plan de Cierre**, se tramita por el sistema **SUPER** y tiene **vigencia máxima de 60 meses**. Ante información falsa u omisiones relevantes, SERNAGEOMIN puede **ordenar la suspensión de la faena** y remitir antecedentes al Ministerio Público | [SECUNDARIO] |
| Entrada en vigencia del DS 15/2026 | Condicionada a toma de razón; rige el **primer día hábil del mes siguiente** a su publicación en el Diario Oficial | **[NO VERIFICADO]** — no se confirmó la publicación efectiva en el Diario Oficial a 2026-09-16 | [NO VERIFICADO] |

> **Regla operativa.** Para faenas ≤ 5.000 t/mes el agente debe preguntar si el DS 15/2026 ya está
> publicado; si lo está, la vía es la declaración jurada por SUPER (vigencia 60 meses). Si no, aplica el
> procedimiento simplificado clásico de los Arts. 16 y 17 de la Ley 20.551.

---

## 4. Chile — DS 594/1999 (MINSAL): límites permisibles, ruido y estrés térmico

### 4.1 Identificación y vigencia

| Atributo | Valor | Etiqueta |
|---|---|---|
| Norma | Decreto Supremo N.º 594 de 1999, Ministerio de Salud | [VERIFICADO] |
| Título | Reglamento sobre condiciones sanitarias y ambientales básicas en los lugares de trabajo | [VERIFICADO] |
| Promulgación / Publicación | 15-sep-1999 / **29-abr-2000** | [VERIFICADO] |
| **Versión vigente a 2026-09-16** | **Última versión: 16-ene-2026** | [VERIFICADO] |
| **Última modificación** | **Decreto 40 de SALUD, Art. único N.º 1, D.O. 16-ene-2026** — modifica el **Art. 98 bis** (protección frente a altas temperaturas) | [VERIFICADO] |

**Historial de modificaciones detectado en el texto consolidado** (marcas del BCN): **[VERIFICADO]**

| Decreto modificatorio | D.O. | Efecto principal |
|---|---|---|
| DTO 201, SALUD | 05-jul-2001 | Arts. 3 a 13 (varios), incl. Art. 60 (LPP) y ruido |
| DTO 57, SALUD | 07-nov-2003 | Asbesto azul – crocidolita (Art. 65) |
| Decreto 122, SALUD | 24-ene-2015 | Arts. 1 N.º 1 y 2 |
| **Decreto 123, SALUD** | **24-ene-2015** | **Reforma mayor: Arts. 61, 62, 63, 64 y 66 (tablas de límites permisibles y fórmulas de corrección)** |
| Decreto 30, SALUD | 14-feb-2018 | Art. 1 N.º 2 |
| Decreto 10, SALUD | 20-jun-2019 | Art. 22 (servicios higiénicos) |
| **Decreto 40, SALUD** | **16-ene-2026** | **Art. 98 bis (altas temperaturas)** |

### 4.2 Definiciones de límites (Art. 59)

| Concepto | Definición | Etiqueta |
|---|---|---|
| **LPP** — Límite Permisible Ponderado | Valor máximo permitido para el **promedio ponderado** de las concentraciones ambientales de contaminantes químicos existentes en los lugares de trabajo durante la jornada normal | [VERIFICADO] |
| **LPT** — Límite Permisible Temporal | Valor máximo permitido para las concentraciones ambientales medidas en un **período de 15 minutos continuos** durante la jornada | [SECUNDARIO] |
| **LPA** — Límite Permisible Absoluto | Valor máximo permitido para las concentraciones ambientales **medido en cualquier momento** de la jornada de trabajo | [VERIFICADO] |

**Regla de excedencias (Art. 60):** el promedio ponderado no debe superar el LPP; se pueden exceder
momentáneamente estos límites pero **en ningún caso superar cinco (5) veces su valor**; cuando exista
LPT, los excesos no pueden superarlo. Ni los excesos del LPP ni la exposición a LPT pueden repetirse
**más de cuatro veces en la jornada diaria ni más de una vez en una hora**. **[VERIFICADO]**

```python
# Art. 60 DS 594/1999
excede_lpp      = promedio_ponderado > LPP
excede_techo_5x = concentracion_instantanea > 5 * LPP   # prohibido siempre
max_excursiones_por_jornada = 4
max_excursiones_por_hora    = 1
```

### 4.3 Límites permisibles del Art. 66 (y Art. 61) para las sustancias solicitadas

Valores del **texto vigente** (tabla del Art. 66 según Decreto 123/2015). Todos **[VERIFICADO]**
sobre las imágenes oficiales de la tabla publicadas por la BCN [F13].

| Sustancia | CAS | LPP ppm | LPP mg/m³ | LPT ppm | LPT mg/m³ | Observaciones |
|---|---|---|---|---|---|---|
| **Sílice cristalizada — cuarzo** | 14808-60-7 | — | **0,08** | — | — | A.1 · **(4) fracción respirable** |
| Sílice cristalizada — cristobalita | 14464-46-1 | — | **0,04** | — | — | A.1 · (4) |
| Sílice cristalizada — tridimita | 15468-32-3 | — | **0,04** | — | — | A.1 · (4) |
| Sílice cristalizada — tierra de trípoli | 1317-95-9 | — | **0,08** | — | — | A.1 · (4) |
| **Polvos no especificados (total)** | — | — | **8** | — | — | **(3)** polvo total exento de asbesto y con < 1 % de sílice cristalizada libre |
| **Polvos no especificados (fracción respirable)** | — | — | **2,4** | — | — | (4) |
| **Arsénico y comp. solubles (como As)** | 7440-38-2 | — | **0,01** | — | — | A.1 |
| Arsina (hidrógeno arseniado) | 7784-42-1 | 0,04 | 0,18 | — | — | — |
| **Plomo — polvo y humos inorgánicos (como Pb)** | 7439-92-1 | — | **0,05** | — | — | A.3 |
| Plomo tetraetílico (como Pb) | 78-00-2 | — | 0,09 | — | — | Piel · A.4 |
| **Cobre — humos** | 7440-50-8 | — | **0,18** | — | — | — |
| **Cobre — polvo y nieblas (como Cu)** | 7440-50-8 | — | **0,88** | — | — | — |
| **Manganeso — humos** | 7439-96-5 | — | **0,88** | — | **3** | — |
| **Manganeso — polvo y compuestos** | 7439-96-5 | — | **0,9** | — | — | — |
| **Ácido sulfúrico** | 7664-93-9 | — | **0,88** | — | **3** | A.2 |
| **Amoníaco** | 7664-41-7 | **22** | **15** | **35** | **24** | — |
| **Monóxido de carbono (CO)** | 630-08-0 | **44** | **48** | — | — | — |
| Anhídrido carbónico (CO₂) | 124-38-9 | 4.375 | 7.875 | 30.000 | 54.000 | — |
| **Anhídrido sulfuroso (SO₂)** | 7446-09-5 | **1,7** | **4,4** | **5** | **13** | A.4 |
| **Dióxido de nitrógeno (NO₂)** | 10102-44-0 | **2,6** | **4,9** | **5** | **9,4** | A.4 |
| **Benceno** | 71-43-2 | **1,0** | **2,7** | **5** | **15** | Piel · A.1 |
| **Tolueno** | 108-88-3 | **87** | **328** | **150** | **560** | Piel · A.4 |
| **Sulfuro de hidrógeno / ácido sulfhídrico (H₂S)** | 7783-06-4 | **8,8** | **12,3** | **15** | **21** | — |
| H₂S — entrada duplicada «Hidrógeno sulfurado» | 04-06-7783 | 8,8 | **12,25** | 15 | 21 | — |

**Notas al pie de la tabla del Art. 66** (resumen, **[VERIFICADO]**):

| Nota | Significado |
|---|---|
| (1) | Muestras exentas de fibras tomadas con elutriador vertical |
| (2) | Recuento por microscopía de contraste de fase a 400–450 aumentos, en filtro de membrana, contando fibras de longitud > 5 µm y relación largo/diámetro ≥ 3:1 |
| **(3)** | **Polvo total exento de asbesto y con menos de 1 % de sílice cristalizada libre** |
| **(4)** | **Fracción respirable** |
| (5) | Solo en ausencia de elementos tóxicos en el metal base y los electrodos, y sin acumulación o producción de gases tóxicos |
| (6) | Recuento según (2), pero no debe existir más de 1,6 mg/m³ de polvo respirable |
| (7) | Anestésico mezclado con óxido nitroso: límite 3,76 mg/m³ (0,5 ppm) |
| (8) | Anestésico mezclado con óxido nitroso: límite 4,09 mg/m³ (0,5 ppm) |

**Calificativos:** «Piel» = la sustancia puede absorberse por vía cutánea (Art. 67). «A.1» =
cancerígeno comprobado para el ser humano (Art. 68); A.2, A.3, A.4 = categorías decrecientes de
evidencia cancerígena. **[VERIFICADO]**

> **Aviso para el motor.** El H₂S aparece **dos veces** en la tabla con valores mg/m³ marginalmente
> distintos (12,3 vs. 12,25). Usar **12,3 mg/m³** (entrada «Ácido Sulfhídrico») y documentar la
> discrepancia; la diferencia es de redondeo y no cambia ninguna decisión de alerta.
>
> **El arsénico bajó de 0,16 a 0,01 mg/m³** con el Decreto 123/2015. Cualquier base de datos anterior
> a 2015 (incluido el texto original de 1999 que circula en PDF) contiene valores **obsoletos y
> peligrosamente permisivos**. No usar el DS 594 «versión 1999».

**Mezclas (Art. 69):** cuando existan dos o más sustancias de efecto sinérgico o aditivo, se aplica la
regla de suma de fracciones. **[SECUNDARIO]**

### 4.4 Corrección por jornada — Art. 62

> **Cambio normativo clave.** Hasta 2015 el Art. 62 corregía por **jornada semanal > 48 horas**.
> El **Decreto 123/2015 (D.O. 24-ene-2015, Art. 1 N.º 12)** lo sustituyó por una corrección basada en
> la **jornada diaria > 8 horas**. **La fórmula semanal `Fj = (48/h)·((168−h)/120)` ya NO está vigente.**

| Aspecto | Contenido | Etiqueta |
|---|---|---|
| Artículo | **Art. 62 DS 594/1999** (texto según Decreto 123/2015) | [VERIFICADO] |
| Disparador | Jornada de trabajo que **sobrepase las 8 horas diarias** | [VERIFICADO] |
| Variable | `h` = número de **horas trabajadas diarias** | [VERIFICADO] |
| Fórmula | **Fj = (8 / h) × ((24 − h) / 16)** | [VERIFICADO] (imagen oficial de la fórmula, BCN) |
| Caso especial | Para jornada de **8 horas diarias con total semanal > 45 h y hasta 48 h**, se usa **Fj = 0,90** | [VERIFICADO] |
| Redondeo | Fj se expresa con **dos decimales**; el segundo decimal se eleva si el tercero es ≥ 5, y se desprecia si es < 5. **No deben efectuarse aproximaciones parciales** | [VERIFICADO] |
| Alcance | Se aplica **solo a los LPP** del Art. 66 | [VERIFICADO] |

### 4.5 Corrección por altitud — Art. 63

| Aspecto | Contenido | Etiqueta |
|---|---|---|
| Artículo | **Art. 63 DS 594/1999** | [VERIFICADO] |
| Disparador | Lugares de trabajo a **altura superior a 1.000 m s. n. m.** | [VERIFICADO] |
| Fórmula | **Fa = P / 760**, con `P` = presión atmosférica local **en milímetros de mercurio (mmHg)** | [VERIFICADO] |
| Alcance | Se aplica a los límites **absolutos, ponderados y temporales** expresados en **mg/m³ y en fibras/cc** de los Arts. 61 y 66. **No se aplica a los valores en ppm** | [VERIFICADO] |
| Redondeo | Dos decimales, misma regla que Fj | [VERIFICADO] |

### 4.6 Combinación jornada + altitud — Art. 64

> «En lugares de trabajo en altura y con jornada diaria mayor a 8 horas se corregirá el límite
> permisible ponderado multiplicándolo sucesivamente por cada uno de los factores definidos en los
> artículos 62 y 63, respectivamente. Se utilizará un Fj = 0,90 para la condición establecida en el
> inciso segundo del artículo 62 precedente. Los límites permisibles temporales y absolutos se ajustarán
> aplicando solamente el factor "Fa" del artículo 63.» — DS 594, **Art. 64**. **[VERIFICADO]**

```python
# Art. 62, 63 y 64 DS 594/1999 (texto vigente)
LPP_corr = LPP_tabla * Fj * Fa     # solo si el valor está en mg/m3 o fibras/cc para Fa
LPT_corr = LPT_tabla * Fa          # NUNCA se aplica Fj
LPA_corr = LPA_tabla * Fa          # NUNCA se aplica Fj
```

### 4.7 Ruido ocupacional (Arts. 70–82)

| Parámetro | Valor exacto | Unidad | Artículo | Etiqueta |
|---|---|---|---|---|
| Límite para ruido estable o fluctuante, jornada de 8 h | **85** | dB(A) lento, medido en la posición del oído | **Art. 74** | [VERIFICADO] |
| Techo absoluto sin protección auditiva | **115** | dB(A) lento | **Art. 77** | [VERIFICADO] |
| Límite para ruido impulsivo, jornada de 8 h | **95** | dB(C) Peak | **Art. 79** | [VERIFICADO] |
| Techo absoluto de ruido impulsivo sin protección | **140** | dB(C) Peak | **Art. 81** | [VERIFICADO] |
| Umbral de integración para la dosis | **80** | dB(A) lento (solo se suman los períodos con NPSeq ≥ 80) | **Art. 76** | [VERIFICADO] |
| Dosis diaria máxima permisible | **1** | = 100 % | **Art. 76** | [VERIFICADO] |
| Instrumentación | Sonómetro integrador o dosímetro tipo 0, 1 o 2 (IEC 651-1979, IEC 804-1985, ANSI S1.4-1983) | — | **Art. 72** | [VERIFICADO] |

**Criterio de intercambio: 3 dB.** El DS 594 no lo enuncia como fórmula, pero se deduce
inequívocamente de la tabla del **Art. 75**: 85 dB(A) → 8 h; 88 → 4 h; 91 → 2 h; 94 → 1 h. Cada
aumento de 3 dB(A) **reduce a la mitad** el tiempo permitido. **[VERIFICADO]** (deducción directa de la
tabla oficial).

**Tabla del Art. 75 — tiempo máximo de exposición diaria (extracto):** **[VERIFICADO]**

| NPSeq dB(A) lento | Tiempo permitido | NPSeq dB(A) lento | Tiempo permitido |
|---|---|---|---|
| 80 | 24,00 h | 97 | 30,00 min |
| 82 | 16,00 h | 100 | 15,00 min |
| 85 | **8,00 h** | 103 | 7,50 min |
| 88 | 4,00 h | 106 | 3,75 min |
| 91 | 2,00 h | 109 | 1,88 min |
| 94 | 1,00 h | 112 | 56,40 s |
| 95 | 47,40 min | 115 | 29,12 s |

**Dosis (Art. 76):** `D = Σ (Te_i / Tp_i)` donde `Te` = tiempo total de exposición a un NPSeq dado y
`Tp` = tiempo total permitido para ese NPSeq. `D ≤ 1`. **[VERIFICADO]**

**Protocolo PREXOR** (Protocolo de Exposición Ocupacional a Ruido, MINSAL):

| Aspecto | Valor | Etiqueta |
|---|---|---|
| Naturaleza | Protocolo del Ministerio de Salud, **obligatorio** para los organismos administradores de la Ley 16.744 y para las empresas y trabajadores con exposición ocupacional a ruido | [SECUNDARIO] |
| **Nivel de acción** (ruido estable/fluctuante) | **82 dB(A)**, equivalente a una **dosis de 0,5 (50 %)** para 8 h de exposición efectiva diaria | [SECUNDARIO] |
| **Nivel de acción** (ruido impulsivo) | **135 dB(C) Peak** | [SECUNDARIO] |
| Relación con el DS 594 | El PREXOR **no modifica** el límite legal de 85 dB(A); anticipa la vigilancia a la mitad de la dosis legal | [SECUNDARIO] |

> **Regla para el motor.** El PREXOR es un **criterio de gestión y vigilancia**, no un límite legal
> sancionable por sí mismo. Alerta amarilla en `dosis ≥ 0,5` u `NPSeq ≥ 82 dB(A)`; alerta roja en
> `dosis > 1` o `NPSeq > 85 dB(A)` sin protección, o `> 115 dB(A)` en cualquier caso.

### 4.8 Estrés térmico — exposición ocupacional a calor (Arts. 96–98 bis)

**Definición y cálculo del índice TGBH (Art. 96).** **[VERIFICADO]**

| Situación | Fórmula |
|---|---|
| Al aire libre **con** carga solar | **TGBH = 0,7·TBH + 0,2·TG + 0,1·TBS** |
| Al aire libre **sin** carga solar, o bajo techo | **TGBH = 0,7·TBH + 0,3·TG** |

donde TBH = temperatura de bulbo húmedo natural (°C); TG = temperatura de globo (°C);
TBS = temperatura de bulbo seco (°C). La lectura se toma una vez estabilizado el termómetro de globo
(**20 a 30 minutos**). El objetivo es que **la temperatura corporal profunda no exceda los 38 °C**, y los
valores se aplican a trabajadores **aclimatados, completamente vestidos y con provisión adecuada de
agua y sal**.

**Tabla de Valores Límites Permisibles del Índice TGBH, en °C** (Art. 96). **[VERIFICADO]**

| Tipo de trabajo (régimen trabajo/descanso por hora) | Carga **Liviana** (< 375 kcal/h) | Carga **Moderada** (375–450 kcal/h) | Carga **Pesada** (> 450 kcal/h) |
|---|---|---|---|
| **Trabajo continuo** | **30,0** | **26,7** | **25,0** |
| 75 % trabajo · 25 % descanso, cada hora | **30,6** | **28,0** | **25,9** |
| 50 % trabajo · 50 % descanso, cada hora | **31,4** | **29,4** | **27,9** |
| 25 % trabajo · 75 % descanso, cada hora | **32,2** | **31,1** | **30,0** |

**Promedio ponderado en el tiempo (Art. 97):** **[VERIFICADO]**

```
TGBH_promedio = Σ (TGBH_i × t_i) / Σ t_i        # t_i en horas
```

**Carga de trabajo (Art. 98):** se determina por el **costo energético ponderado en el tiempo**:
`M_promedio = Σ (M_i × t_i) / Σ t_i`. **[VERIFICADO]**

**Tabla «Costo energético según tipo de trabajo»** (Art. 98). **[VERIFICADO]**

| Actividad | kcal/h | Actividad | kcal/h |
|---|---|---|---|
| Sentado | 90 | Jardinería | 336 |
| De pie | 120 | Clavar con martillo (4,5 kg, 15 golpes/min) | 438 |
| Escribir a mano o a máquina | 120 | Palear (10 veces/min) | 468 |
| Limpiar ventanas | 220 | Aserrar madera (sierra de mano) | 540 |
| Planchar | 252 | Trabajo con hacha (35 golpes/min) | 600 |
| Caminando (5 km/h sin carga) | 270 | Andar en bicicleta (16 km/h) | 312 |

**Art. 98 bis — altas temperaturas (texto vigente por Decreto 40, D.O. 16-ene-2026).** **[VERIFICADO]**
Obliga a las entidades empleadoras a proteger la salud frente a **altas temperaturas y altas
temperaturas extremas** informadas por la Dirección Meteorológica de Chile y las alertas de **SENAPRED**,
sin perjuicio de las evaluaciones ambientales permanentes por estrés térmico. Acciones mínimas:

| Letra | Acción |
|---|---|
| a) | Informarse **diariamente** de las alertas meteorológicas de la Dirección Meteorológica de Chile y seguir las alertas por calor de SENAPRED |
| b) | Identificar y evaluar la exposición a altas temperaturas en cada puesto de trabajo (los organismos administradores de la Ley 16.744 deben entregar las herramientas) |
| c) | Elaborar, con el organismo administrador y **con participación de las personas trabajadoras**, un plan de gestión, reducción y respuesta ante emergencias, desastres y catástrofes, con medidas preventivas, de mitigación y de respuesta |
| d) | Observar las condiciones que fije el Ministerio de Salud mediante la norma técnica correspondiente |

---

## 5. Chile — DS 132/2002 (Reglamento de Seguridad Minera): ventilación y evacuación

### 5.1 Identificación y vigencia

| Atributo | Valor | Etiqueta |
|---|---|---|
| Norma | Decreto Supremo N.º 132 de 2002, Ministerio de Minería — Reglamento de Seguridad Minera | [VERIFICADO] |
| Promulgación / Publicación | 30-dic-2002 / **07-feb-2004** | [VERIFICADO] |
| Naturaleza | Modifica y fija el **texto refundido, sistematizado y coordinado** del DS N.º 72 de 1985 | [VERIFICADO] |
| **Versión vigente a 2026-09-16** | **Última versión: 09-abr-2024** | [VERIFICADO] |
| **Última modificación** | **Decreto N.º 1 de 2024, Ministerio de Minería (promulgado 12-ene-2024, D.O. 09-abr-2024)** | [VERIFICADO] |
| Fiscalizador | SERNAGEOMIN («el Servicio») | [VERIFICADO] |

### 5.2 Ventilación en minería subterránea — Capítulo Cuarto, Título correspondiente

| Parámetro | Valor exacto | Unidad | Artículo | Etiqueta |
|---|---|---|---|---|
| **Caudal mínimo de aire fresco por persona** | **3** | **m³/min por persona**, en cualquier sitio del interior de la mina | **Art. 138** | [VERIFICADO] |
| **Velocidad media del aire — máxima** | **150** | m/min (= 2,5 m/s) | **Art. 138** | [VERIFICADO] |
| **Velocidad media del aire — mínima** | **15** | m/min (= 0,25 m/s) | **Art. 138** | [VERIFICADO] |
| **Caudal por equipo diésel (si el fabricante no lo especifica)** | **2,83** | **m³/min por caballo de fuerza efectivo al freno (BHP)**, para máquinas en buenas condiciones de mantención | **Art. 132** | [VERIFICADO] |
| **Oxígeno mínimo** | **19,5** | **% en peso** en el aire | **Art. 144** | [VERIFICADO] |
| Aforo de ventilación en entradas y salidas principales | **trimestral** (al menos) | — | **Art. 139** | [VERIFICADO] |
| Control general de toda la mina | **semestral** | — | **Art. 139** | [VERIFICADO] |
| **Pérdidas de ventilación toleradas** | **≤ 15 %** | — | **Art. 139** | [VERIFICADO] |
| Aprobación del proyecto de ventilación | Obligatoria ante SERNAGEOMIN previo a su aplicación; el Servicio responde en **30 días** | — | **Art. 136** | [VERIFICADO] |
| Circuitos de ventilación | Obligatorios en toda mina subterránea (natural o forzada), con aire fresco permanente y retorno de aire viciado | — | **Art. 137** | [VERIFICADO] |
| Ventilación auxiliar en galerías en desarrollo | El extremo de la tubería no debe estar a más de **30 m** de la frente; a mayor distancia, sopladores, venturi o ventiladores adicionales (sistema impelente o aspirante) | — | **Art. 141** | [VERIFICADO] |
| Renovación en frentes de reconocimiento/desarrollo alejados | Tubos ventiladores u otros medios auxiliares | — | **Art. 146** | [VERIFICADO] |
| Alarma de ventilador principal | Todo ventilador principal debe tener sistema de alarma ante detención imprevista | — | **Art. 149** | [VERIFICADO] |
| Temperaturas máximas y mínimas | Se remite al **DS 594** del Ministerio de Salud | — | **Art. 143** | [VERIFICADO] |

Cita textual (texto legal):

> «En todos los lugares de la mina, donde acceda personal, el ambiente deberá ventilarse por medio de
> una corriente de aire fresco, de no menos de tres metros cúbicos por minuto (3 m3/min) por persona,
> en cualquier sitio del interior de la mina. […] Las velocidades, como promedio, no podrán ser mayores
> de ciento cincuenta metros por minuto (150 m/min.), ni inferiores a quince metros por minuto
> (15 m/min.).» — DS 132, **Art. 138**.

```python
# Caudal total de inyección mínimo (DS 132 Arts. 132 y 138)
Q_personas_m3min = 3.0 * n_personas                     # Art. 138
Q_diesel_m3min   = sum(2.83 * bhp_i for bhp_i in equipos)  # Art. 132 (si el fabricante no especifica)
Q_min_total      = Q_personas_m3min + Q_diesel_m3min     # Art. 132, inciso 2: SIEMPRE se suman
# Además: 15 m/min <= velocidad_media <= 150 m/min  (Art. 138)
# Además: O2 >= 19.5 % en peso  (Art. 144)
```

> **Nota importante (Art. 132, inciso 2):** el caudal requerido por los equipos diésel debe confrontarse
> con el aire necesario para controlar otros contaminantes, **y siempre debe sumarse el caudal calculado
> por número de personas**. No es un máximo entre ambos: es una suma.

### 5.3 Gases: máximos y umbrales de detención de equipos diésel

| Contaminante | Valor máximo ambiental que obliga a **detener el equipo diésel** | Artículo | Etiqueta |
|---|---|---|---|
| **Monóxido de carbono (CO)** | **40 ppm** | **Art. 135 letra a)** | [VERIFICADO] |
| **Óxidos de nitrógeno (NOx)** | **20 ppm** | **Art. 135 letra a)** | [VERIFICADO] |
| **Aldehído fórmico (formaldehído)** | **1,6 ppm** | **Art. 135 letra a)** | [VERIFICADO] |
| Resto de contaminantes químicos | Se aplica lo establecido en el **DS 594** del Ministerio de Salud | Art. 135 letra a) | [VERIFICADO] |
| CO medido **en el escape** de la máquina | **> 2.000 ppm** | **Art. 135 letra b)** | [VERIFICADO] |
| NOx medido **en el escape** de la máquina | **> 1.000 ppm** | **Art. 135 letra b)** | [VERIFICADO] |
| Desperfecto con riesgo evidente | Detención obligatoria | Art. 135 letra c) | [VERIFICADO] |

**Corrección por altitud dentro del propio DS 132 (Art. 135):** para lugares de trabajo sobre
**1.000 m s. n. m.** con concentraciones máximas en mg/m³ o fibras/cc:

```
L.P.P._p = (L.P.P. × p) / 760        # p = presión atmosférica local en mmHg
```

Es **la misma corrección Fa del Art. 63 del DS 594**, reexpresada. **[VERIFICADO]**

**Monitoreo de gases en minas con equipos diésel (Art. 133):** evaluar y registrar concentraciones
ambientales de **CO, óxidos de nitrógeno (NO + NO₂), dióxido de nitrógeno y aldehídos**; se recomienda
medir **al menos una vez por semana** o cuando las condiciones ambientales lo aconsejen. En áreas o
labores **críticas** debe haber **sensores y alarmas** que alerten cuando se excedan los valores
permitidos. Medición en el tubo de escape **a intervalos no superiores a un mes** (Art. 133 letra b).
**[VERIFICADO]**

> **CO₂ (anhídrido carbónico): el DS 132 NO fija un límite propio.** Se verificó por búsqueda sobre el
> texto completo consolidado: las expresiones «dióxido de carbono», «anhídrido carbónico» y «CO₂» no
> aparecen en el reglamento. El límite aplicable es el del **DS 594, Art. 66**: LPP **4.375 ppm /
> 7.875 mg/m³** y LPT **30.000 ppm / 54.000 mg/m³**, por remisión expresa del Art. 135. **[VERIFICADO]**

### 5.4 Evacuación, refugios y emergencias

| Obligación | Contenido | Artículo | Etiqueta |
|---|---|---|---|
| **Procedimientos de emergencia y rescate** | Deben comprender al menos alarmas, evacuación, salvamento con medios propios o ajenos, medios de comunicación y elementos necesarios. En minas subterráneas: organizar y mantener **Brigadas de Rescate Minero** seleccionadas, instruidas y dotadas | **Art. 75** | [VERIFICADO] |
| **Procedimiento de evacuación** | El Administrador debe elaborarlo y mantenerlo actualizado. Debe considerar: a) tipo de emergencia; b) señalización interna e indicación de **vías de escape y refugios**; c) sistemas de alarma y comunicaciones; d) instrucción del personal; e) **simulacros** y funcionamiento de brigadas de rescate | **Art. 99** | [VERIFICADO] |
| **Refugios** | Toda mina debe disponer de refugios en su interior que garanticen la sobrevivencia por un **período mínimo de 48 horas**. Dotación mínima: equipos autorrescatadores (en número relacionado con el personal del entorno), alimentos no perecibles, agua potable renovada frecuentemente, **tubos de oxígeno**, equipos de comunicación con superficie o áreas contiguas, ropa de recambio, elementos de primeros auxilios y manuales para auxiliar lesionados. Ubicación en función del avance de los frentes, **en lo posible transportables** | **Art. 100** | [VERIFICADO] |
| Iluminación | Nadie puede ingresar al interior de la mina sin sistema de iluminación personal aprobado; alumbrado de emergencia en todos los recintos | **Art. 101** | [VERIFICADO] |
| **Labores no ventiladas o abandonadas** | Deben bloquearse con tapados de malla o similar y señalizarse. Para acceder se requiere análisis exhaustivo previo de **oxígeno y gases nocivos** y, si es necesario, equipos autónomos de respiración | **Art. 145** | [VERIFICADO] |
| **Retiro obligatorio** | Si las concentraciones ambientales superan los máximos, es **obligatorio retirar al trabajador** del área contaminada hasta que las condiciones retornen a la normalidad, lo que debe **certificar personal calificado y autorizado** | **Art. 144** | [VERIFICADO] |
| **Simulacros** | Programas de simulacros de emergencia **al menos una vez al año** para todo el personal de la mina; control efectivo de ingresos y salidas; sistemas de alarma; equipos auxiliares de rescate y refugios señalizados | **Art. 197** (numeración del texto refundido) | [SECUNDARIO] |

### 5.5 ¿Existen niveles tipo TARP en el DS 132?

> **NO. El DS 132/2002 no contiene niveles tipo TARP** (*Trigger Action Response Plan*) ni un sistema
> de umbrales escalonados verde/amarillo/naranja/rojo. Verificado por búsqueda sobre el texto completo
> consolidado: no aparecen los términos «TARP» ni «alerta» en el sentido de nivel escalonado.
> **[VERIFICADO — ausencia comprobada]**
>
> Lo que sí existe es un **esquema binario de detención**: el Art. 135 fija valores que obligan a
> **detener** el equipo diésel, y el Art. 144 obliga a **retirar** al trabajador. No hay niveles
> intermedios de acción reglamentarios.
>
> El concepto TARP proviene del **GISTM (Principio 7 y 13)** y de las guías ICMM, y en Chile es
> **buena práctica voluntaria**, no exigencia del DS 132 ni del DS 248.

### 5.6 Cambios 2024 — Decreto 1 de 2024 (D.O. 09-abr-2024)

| Aspecto | Contenido | Etiqueta |
|---|---|---|
| Objeto | Modifica el **Título XV** del DS 132 («Normas de seguridad minera aplicables a faenas mineras»), Capítulo Segundo (arts. 595–670) | [SECUNDARIO] |
| Finalidad | Agilizar y flexibilizar la tramitación de permisos para la **pequeña minería (≤ 5.000 t/mes)**, con las figuras de **Declaración Minera** y **Proyecto Minero** | [SECUNDARIO] |
| Ventilación en el régimen de pequeña minería | **Art. 626 (nuevo):** toda mina subterránea con labores que alcancen **100 m de avance de túneles** debe disponer de circuitos de ventilación natural y/o forzada, con suministro permanente de aire fresco y retorno al exterior | [SECUNDARIO] |
| Mediciones para faenas > 1.000 t/mes | **Art. 628 (nuevo):** mediciones **mensuales** de oxígeno, monóxido de carbono y humos nitrosos; prohibición de trabajos con **O₂ < 19,5 %**; **aforos trimestrales** de entrada/salida y **control anual** de ventilación | [SECUNDARIO] |
| Refugios y evacuación | **Arts. 615–616 (nuevos):** permiten habilitar estocadas como refugios de seguridad en labores ciegas cuando la distancia sea **menor a 100 m**, con fortificación que garantice evacuación expedita y segura | [SECUNDARIO] |

> **Atención para el motor.** El régimen general (Arts. 132–153) **y** el régimen especial de pequeña
> minería (Arts. 595–670, incorporado en 2024) coexisten. El motor debe determinar primero el régimen
> aplicable por tamaño de faena antes de aplicar umbrales. Los valores del régimen especial están
> etiquetados **[SECUNDARIO]** porque provienen de una lectura indirecta del decreto modificatorio y
> no se verificaron artículo por artículo sobre el texto refundido.

---

## 6. Huella hídrica: ISO 14046 y método AWARE

### 6.1 ISO 14046 — Huella hídrica (resumen)

| Atributo | Valor | Etiqueta |
|---|---|---|
| Norma | **ISO 14046:2014** — *Environmental management — Water footprint — Principles, requirements and guidelines* | [VERIFICADO] |
| Publicación | 2014 (1.ª edición). Adopción europea: **EN ISO 14046:2016** | [VERIFICADO] |
| **Estado a 2026-09-16** | Sometida a **revisión sistemática** iniciada el **15-oct-2025**, con cierre de revisión previsto el **05-mar-2026**. El resultado (confirmación o revisión) **no se pudo verificar** | [NO VERIFICADO] |
| Relación con otras normas | Aplica los principios del ACV de **ISO 14040** e **ISO 14044** al ámbito del agua | [SECUNDARIO] |

**Qué es y qué no es (resumen con palabras propias):** ISO 14046 fija principios, requisitos y directrices
para realizar y comunicar una **evaluación de huella hídrica** de productos, procesos u organizaciones,
con perspectiva de ciclo de vida. Su diferencia esencial con un simple balance de consumo es que **no
mide solo cuánta agua se usa, sino el impacto ambiental potencial de ese uso, condicionado por dónde y
cuándo ocurre**. Puede realizarse como evaluación independiente o como parte de una evaluación
ambiental más amplia. **[SECUNDARIO]**

**Las cuatro fases** (estructura heredada del ACV): **[SECUNDARIO]**

| Fase | Contenido resumido |
|---|---|
| 1. **Definición del objetivo y el alcance** | Para qué se hace, qué sistema se estudia, unidad funcional, límites del sistema, categorías de impacto relacionadas con agua (escasez, degradación por calidad), resolución espacial y temporal, y supuestos |
| 2. **Análisis de inventario** | Recolección y cuantificación de entradas y salidas de agua a lo largo del ciclo de vida, diferenciadas por tipo de agua, origen, destino, calidad y localización geográfica y temporal |
| 3. **Evaluación de impacto** | Conversión de los datos de inventario en indicadores de impacto potencial mediante **factores de caracterización** (aquí entra AWARE para escasez hídrica). Puede cubrir escasez y/o degradación de calidad |
| 4. **Interpretación** | Identificación de puntos críticos, análisis de completitud, sensibilidad y consistencia; conclusiones, limitaciones y recomendaciones |

**Elementos adicionales relevantes para el motor de cálculo:** **[SECUNDARIO]**

- La norma exige **explicitar la resolución espacial y temporal**; una huella hídrica sin localización de
  cuenca ni periodo es incompleta.
- Un resultado de huella hídrica **de una sola cifra agregada no puede presentarse como "la huella
  hídrica"** sin declarar qué categorías de impacto cubre.
- Para **aseveraciones comparativas divulgadas al público**, se exige **revisión crítica por panel de
  partes interesadas** (regla heredada de ISO 14040/14044). **Esto es directamente relevante para el
  módulo antigreenwashing del proyecto.**

> **Nota de derechos.** El texto de ISO 14046 es de acceso pago y está protegido. Aquí solo se resume su
> contenido con palabras propias. **El motor no debe incluir fragmentos del texto normativo.**

### 6.2 Método AWARE — definición y fórmula

| Atributo | Valor | Etiqueta |
|---|---|---|
| Nombre | **AWARE** — *Available WAter REmaining* | [VERIFICADO] |
| Desarrollador | **WULCA** (grupo de trabajo de la *Life Cycle Initiative* del PNUMA) | [VERIFICADO] |
| Publicación original | Boulay et al. (2018), *Int. J. Life Cycle Assess.* 23(2), 368–378 | [VERIFICADO] |
| **Versión vigente a 2026-09-16** | **AWARE 2.0** (Seitfudem, Berger, Müller Schmied & Boulay, 2025, *Journal of Industrial Ecology*) | [VERIFICADO] |
| Modelo hidrológico base de AWARE 2.0 | **WaterGAP 2.2e** (Müller Schmied et al., 2024) | [VERIFICADO] |
| Qué mide | Escasez hídrica: **agua disponible remanente por unidad de superficie y tiempo**, una vez satisfecha la demanda de humanos y ecosistemas acuáticos | [VERIFICADO] |
| Unidad del factor | **Adimensional**, interpretado como **m³ mundo-eq / m³ consumido** | [VERIFICADO] |
| **Rango** | **0,1 a 100** (valores truncados en ambos extremos) | [VERIFICADO] |
| Significado del valor 1 | Corresponde al **promedio mundial** | [VERIFICADO] |
| Interpretación | Un CF de 10 significa que en esa cuenca/mes **queda 10 veces menos agua disponible** que el promedio mundial: consumir 1 m³ allí equivale a consumir 10 m³ "promedio mundo" | [VERIFICADO] |

**Construcción del factor (resumen):** **[VERIFICADO]**

1. Se calcula **AMD** (*Availability Minus Demand*) = disponibilidad de agua menos la demanda humana y
   ecosistémica, **por unidad de superficie y de tiempo** (m³·m⁻²·mes⁻¹), a nivel de cuenca y mes.
2. Se normaliza contra el promedio mundial: **AMD mundial = 0,0136 m³·m⁻²·mes⁻¹**.
3. Se **invierte** (escasez = 1 / disponibilidad remanente).
4. Se **trunca** el resultado al rango **[0,1 ; 100]**.

```
CF_AWARE(cuenca, mes) = min( 100 , max( 0,1 , AMD_mundo / AMD(cuenca, mes) ) )
donde AMD_mundo = 0,0136 m3 / (m2 · mes)
```

**Aplicación (huella de escasez hídrica):**

```
WSF [m3 mundo-eq] = Consumo de agua [m3] × CF_AWARE
```

### 6.3 Agregaciones: agrícola / no agrícola / no especificado, y anual / mensual

Los factores nativos son **por cuenca y por mes**. Cuando no se conoce la cuenca o el mes exactos, se
usan **agregaciones ponderadas por el consumo de agua del sector correspondiente** (no un promedio
aritmético simple), de modo que el factor refleje la probabilidad real de que el consumo ocurra en
determinada cuenca y mes. **[VERIFICADO]**

| Agregación | Ponderador | Cuándo usarla |
|---|---|---|
| **Agrícola** (*agri*) | Mapas espaciotemporales de consumo de agua para **riego** | Procesos agrícolas o de riego |
| **No agrícola** (*non-agri*) | Consumo de agua de los sectores **doméstico, industrial, energético y ganadero** | **Minería, industria, procesos fabriles, servicios** |
| **No especificado** (*unspecified / unknown*) | Consumo humano **total** | Cuando no se conoce el sector |
| **Mensual** | — | Cuando se conoce el mes del consumo. **Siempre preferible** |
| **Anual** | Ponderado por el consumo del sector a lo largo del año | Cuando el mes es desconocido o el inventario es anual |

> **Regla para el motor minero.** Para una faena minera el factor por defecto es el **no agrícola**
> (*non-agri*). Usar el factor *unspecified* sobrestima o subestima según el país (en Chile,
> *unspecified* 88,1 vs. *non-agri* 45,5 — casi el doble). **Declarar siempre qué agregación se usó.**

**Promedios globales AWARE 2.0 (región GLO):** **[VERIFICADO]**

| Agregación | CF anual global | Rango mensual global |
|---|---|---|
| No especificado | **39,5** | 24,2 (sep) – 54,8 (jun) |
| Agrícola | **43,1** | 25,4 (sep) – 58,1 (jun) |
| No agrícola | **17,9** | 14,8 (nov) – 22,2 (may) |

> **Atención al cambio de versión.** Los promedios globales de **AWARE 1.x** ampliamente citados eran
> **43 (no especificado), 46 (agrícola) y 20 (no agrícola)**. **AWARE 2.0 los actualiza a 39,5 / 43,1 /
> 17,9.** Un motor que mezcle factores de país de AWARE 2.0 con normalizaciones de AWARE 1.x producirá
> resultados inconsistentes. **Fijar la versión en la configuración y declararla en el reporte.**

### 6.4 Licencia y condiciones de uso de los factores AWARE

| Aspecto | Respuesta | Etiqueta |
|---|---|---|
| Repositorio oficial de AWARE 2.0 | Zenodo, **DOI 10.5281/zenodo.15133241** (v1.0.0, publicado **03-abr-2025**) | [VERIFICADO] |
| **Licencia** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** | [VERIFICADO] |
| **¿Se pueden redistribuir en un repositorio público?** | **SÍ.** CC BY 4.0 permite copiar, redistribuir, adaptar y usar comercialmente, **siempre que se atribuya** correctamente a los autores, se indique la licencia y se señalen los cambios | [VERIFICADO] |
| Dataset complementario de cultivos | Zenodo **DOI 10.5281/zenodo.16332127** (agregaciones AWARE 2.0 para 27 cultivos y categorías; factores específicos para 160 cultivos por país) | [SECUNDARIO] |
| Factores AWARE 1.2 (versión anterior) | Descarga directa desde el sitio de WULCA. **El sitio no publica términos de licencia explícitos para la v1.2** | [VERIFICADO] (ausencia de términos comprobada) |
| Agregaciones para minería en AWARE 2.0 | **No existen** agregaciones sector-específicas de minería para AWARE 2.0. Hay estudios previos sobre 25 *commodities* mineros con la metodología anterior | [SECUNDARIO] |

**Atribución mínima obligatoria que debe incluir el repositorio de Agentes ESG:**

```
Factores AWARE 2.0 — Licencia CC BY 4.0.
Dataset: Seitfudem, G., Berger, M., Müller Schmied, H., & Boulay, A.-M. (2025).
  The updated and improved method for water scarcity impact assessment in LCA,
  AWARE2.0 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15133241
Publicación: Seitfudem, G., Berger, M., Müller Schmied, H., & Boulay, A.-M. (2025).
  Journal of Industrial Ecology. https://doi.org/10.1111/jiec.70023
Método original: Boulay, A.-M., et al. (2018). Int J Life Cycle Assess 23(2), 368-378.
  https://doi.org/10.1007/s11367-017-1333-8
Modelo hidrológico: WaterGAP 2.2e — Müller Schmied, H., et al. (2024).
  Geosci. Model Dev. 17(23), 8817-8852. https://doi.org/10.5194/gmd-17-8817-2024
```

> **Si se usan los factores de AWARE 1.2** (no CC BY explícito), lo correcto es **no redistribuir el
> archivo** y, en su lugar, enlazar a la descarga de WULCA, o bien migrar a AWARE 2.0 (recomendado por
> WULCA y licenciado CC BY 4.0).

### 6.5 Factores AWARE 2.0 anuales por país

Agregación de país conforme a las definiciones **GLAM / Naciones Unidas** (el archivo también trae la
definición de geografías de **ecoinvent 3.10**). Fuente: dataset oficial AWARE 2.0, hoja
`CFs_unspecified`, `CFs_agri`, `CFs_nonagri`, columna `Annual`. **[VERIFICADO]** [F19]

| País | ISO3 | **No agrícola** (usar en minería) | Agrícola | No especificado |
|---|---|---|---|---|
| **Chile** | CHL | **45,5** | 91,3 | 88,1 |
| **Perú** | PER | **24,4** | 37,6 | 36,2 |
| **Argentina** | ARG | **6,23** | 41,5 | 33,5 |
| **Brasil** | BRA | **4,38** | 6,35 | 5,58 |
| **Colombia** | COL | **1,12** | 3,96 | 2,74 |
| **México** | MEX | **20,3** | 41,8 | 38,1 |
| **España** | ESP | **35,5** | 74,9 | 73,5 |
| **Estados Unidos** | USA | **11,3** | 37,4 | 33,7 |
| *Promedio mundial (GLO)* | — | *17,9* | *43,1* | *39,5* |

**Factores mensuales no agrícolas** (los más relevantes para minería), mismos países: **[VERIFICADO]**

| País | Ene | Feb | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Chile** | 84,9 | 84,1 | 70,4 | 67,7 | 59,8 | 5,19 | 8,81 | 7,03 | 7,78 | 9,40 | 63,1 | 79,7 |
| **Perú** | 12,2 | 10,3 | 8,89 | 42,2 | 65,0 | 50,2 | 27,3 | 17,0 | 15,2 | 14,9 | 14,5 | 14,1 |
| **Argentina** | 10,5 | 9,01 | 5,32 | 3,69 | 4,12 | 4,06 | 4,73 | 4,81 | 5,35 | 5,76 | 8,88 | 8,69 |
| **Brasil** | 3,55 | 3,29 | 6,74 | 2,50 | 1,92 | 2,45 | 2,84 | 3,63 | 5,43 | 7,63 | 5,51 | 6,89 |
| **Colombia** | 1,13 | 2,24 | 1,76 | 2,31 | 0,581 | 0,557 | 1,62 | 1,40 | 0,798 | 0,394 | 0,339 | 0,437 |
| **México** | 18,7 | 21,5 | 23,0 | 27,1 | 26,7 | 22,0 | 15,7 | 16,8 | 13,3 | 16,2 | 21,3 | 21,1 |
| **España** | 8,01 | 8,67 | 9,04 | 16,2 | 32,3 | 51,3 | 66,0 | 69,1 | 62,2 | 53,7 | 32,1 | 15,9 |
| **EE. UU.** | 7,98 | 6,66 | 6,51 | 8,06 | 9,46 | 14,9 | 16,8 | 17,9 | 14,4 | 12,4 | 12,3 | 8,27 |

> **Advertencia metodológica clave.** El factor de **país es una aproximación gruesa**. AWARE se define
> a nivel de **cuenca**. Para una faena minera concreta —especialmente en el norte de Chile o en la
> costa peruana, donde la variabilidad entre cuencas es extrema— **hay que usar el factor de la cuenca
> real** (archivo `AWARE20_Native_CFs.xlsx` o los archivos `.gpkg`/`.kmz` del mismo dataset). El factor
> país solo es defendible para inventarios de cadena de suministro sin trazabilidad geográfica.
>
> **Nota sobre España:** el archivo oficial advierte que los CF de España combinan territorio peninsular
> e insular tanto en ecoinvent como en GLAM, lo que eleva artificialmente los factores (especialmente
> los agrícolas en meses de invierno). **[VERIFICADO]**
>
> **Países con doble entrada** por diferencias de límites políticos entre GLAM y ecoinvent: China,
> Chipre, Finlandia, Francia, India, Israel, Países Bajos, Pakistán, Serbia, Somalia, Ucrania y Sahara
> Occidental. Ninguno de los ocho países solicitados está afectado. **[VERIFICADO]**

---

## 7. GRI 303: Agua y efluentes 2018

### 7.1 Identificación

| Atributo | Valor | Etiqueta |
|---|---|---|
| Norma | **GRI 303: Water and Effluents 2018** (Agua y efluentes) | [VERIFICADO] |
| Publicación | 2018 | [VERIFICADO] |
| **Vigencia** | Obligatoria para reportes u otros materiales publicados **a partir del 1 de enero de 2021** | [VERIFICADO] |
| Estado a 2026-09-16 | **Vigente, sin revisión anunciada** por el GSSB | [SECUNDARIO] |
| Enfoque | Agua como **recurso compartido**; pasa de un reporte puramente volumétrico a uno de gestión de impactos y contexto local | [VERIFICADO] |

### 7.2 Las cinco divulgaciones

| Código | Título | Contenido resumido |
|---|---|---|
| **303-1** | **Interacción con el agua como recurso compartido** | Cómo la organización interactúa con el agua: de dónde extrae, qué impactos causa, cómo aborda los impactos (incluidos los de la cadena de valor), y cómo alinea su enfoque con la política pública y el contexto local de cada zona **con estrés hídrico** |
| **303-2** | **Gestión de los impactos relacionados con la descarga de agua** | Estándares mínimos de calidad de los efluentes, cómo se determinaron esos estándares, y cómo se tratan los perfiles de calidad del agua receptora |
| **303-3** | **Extracción de agua** | Extracción total en **megalitros**, desglosada por fuente (agua superficial, subterránea, marina, agua producida, agua de terceros) **y** desglose específico de la extracción **en zonas con estrés hídrico**, ambas separando **agua dulce** y **otras aguas** |
| **303-4** | **Descarga de agua** | Descarga total en megalitros por destino, con desglose agua dulce / otras aguas, descarga en zonas con estrés hídrico, y sustancias prioritarias de preocupación para las cuales se realizan descargas |
| **303-5** | **Consumo de agua** | Consumo total en megalitros, consumo en zonas con estrés hídrico, y cambios en el almacenamiento de agua si son un impacto significativo |

*Divulgaciones 303-1 y 303-2 pertenecen a la sección de **enfoque de gestión**; 303-3 a 303-5 son
métricas cuantitativas.* **[VERIFICADO]**

### 7.3 Definiciones clave (glosario GRI 303)

| Término | Definición (resumen fiel del glosario oficial) | Etiqueta |
|---|---|---|
| **Extracción de agua** (*water withdrawal*) | Suma de **toda** el agua tomada de agua superficial, subterránea, marina o de un tercero, **para cualquier uso**, durante el periodo de reporte | [VERIFICADO] |
| **Descarga de agua** (*water discharge*) | Suma de efluentes, agua usada y agua no usada liberada a agua superficial, subterránea, marina o a un tercero, **para la que la organización ya no tiene uso**, durante el periodo. Puede ser puntual o difusa, y autorizada o no autorizada | [VERIFICADO] |
| **Consumo de agua** (*water consumption*) | Suma del agua extraída que ha sido **incorporada a productos**, usada en producción de cultivos, generada como residuo, **evaporada, transpirada**, consumida por personas o ganado, **o contaminada hasta ser inutilizable por otros usuarios**, y que por tanto **no se devuelve** a agua superficial, subterránea, marina ni a un tercero. **Incluye el agua almacenada** durante el periodo para uso o descarga en un periodo posterior | [VERIFICADO] |
| **Agua dulce** (*freshwater*) | **≤ 1.000 mg/L de sólidos disueltos totales (TDS)** | [VERIFICADO] |
| **Otras aguas** (*other water*) | **> 1.000 mg/L de TDS** | [VERIFICADO] |
| **Estrés hídrico** (*water stress*) | Capacidad, o falta de ella, para satisfacer la demanda humana y ecológica de agua. Puede referirse a **disponibilidad, calidad o accesibilidad**; se basa en elementos subjetivos y se evalúa de forma distinta según valores sociales; **se mide a nivel de cuenca como mínimo** (fuente: CEO Water Mandate, 2014) | [VERIFICADO] |

**Relación fundamental que debe implementar el motor:**

```
Consumo = Extracción - Descarga           # GRI 303-5, método de cálculo aceptado
```

> **Trampa habitual.** `Extracción − Descarga` es un método de cálculo válido, pero la **definición**
> de consumo del GRI es más amplia: incluye el agua **contaminada hasta ser inutilizable** y el agua
> **almacenada**. Si una faena devuelve agua a un cauce con calidad que la inutiliza para otros usuarios,
> el GRI la cuenta como consumida aunque físicamente haya sido descargada. El motor debe permitir
> registrar ese ajuste.
>
> **El consumo GRI 303-5 es el input correcto para la huella AWARE**, no la extracción.

### 7.4 Zonas con estrés hídrico y WRI Aqueduct

El GRI 303 identifica como herramientas públicas y creíbles para evaluar zonas con estrés hídrico el
**WRI *Aqueduct Water Risk Atlas*** y el **WWF *Water Risk Filter***. Según el estándar, el estrés hídrico
en una zona puede evaluarse considerando que el **estrés hídrico de referencia** (*baseline water
stress*) sea **alto (40–80 %)** o **extremadamente alto (> 80 %)**. **[VERIFICADO]**

**Categorías de *baseline water stress* de WRI Aqueduct** (ratio extracciones totales / suministro
renovable disponible): **[SECUNDARIO]**

| Categoría | Rango | ¿Cuenta como «zona con estrés hídrico» para GRI 303? |
|---|---|---|
| Bajo (*Low*) | < 10 % | No |
| Bajo–medio (*Low–Medium*) | 10 – 20 % | No |
| Medio–alto (*Medium–High*) | 20 – 40 % | No |
| **Alto (*High*)** | **40 – 80 %** | **Sí** |
| **Extremadamente alto (*Extremely High*)** | **> 80 %** | **Sí** |

**Versión vigente:** **Aqueduct 4.0** (WRI, 2023), con periodo base **1979–2019** y modelo hidrológico
**PCR-GLOBWB 2**, con proyecciones a 2030/2050/2080 bajo distintos escenarios climáticos.
**[SECUNDARIO]**

```python
ZONAS_ESTRES_GRI303 = {"High", "Extremely High"}   # baseline water stress >= 40 %
def es_zona_estres(bws_ratio: float) -> bool:
    return bws_ratio >= 0.40        # Aqueduct 4.0 / GRI 303-3-b
```

> **Precaución.** El GRI permite un **enfoque inclusivo**: una zona puede considerarse con estrés
> hídrico por razones de **calidad o accesibilidad** aunque su *baseline water stress* sea < 40 %.
> El motor debe permitir marcar manualmente una faena como "zona con estrés hídrico" aunque Aqueduct
> no la clasifique así, y debe registrar la justificación.
>
> **AWARE ≠ Aqueduct.** No son intercambiables: AWARE es un factor de caracterización de ACV
> (impacto por m³ consumido); el *baseline water stress* de Aqueduct es un indicador de riesgo
> (ratio de extracción/disponibilidad). **No convertir uno en otro.**

---

## 8. Chile — Ley 21.435 (reforma del Código de Aguas) y monitoreo de extracciones ante la DGA

### 8.1 Ley 21.435 — reforma del Código de Aguas

| Atributo | Valor | Etiqueta |
|---|---|---|
| Norma | **Ley N.º 21.435**, Reforma el Código de Aguas | [VERIFICADO] |
| Publicación | **06-abr-2022** (Diario Oficial N.º 43.222) | [VERIFICADO] |
| Objeto | Reforzar el carácter de **bien nacional de uso público** del agua; nueva regulación de constitución, ejercicio y extinción de los derechos de aprovechamiento; proteger la función del agua dulce en los ecosistemas | [VERIFICADO] |

**Cambios estructurales relevantes para una faena minera:**

| Cambio | Contenido | Artículo | Etiqueta |
|---|---|---|---|
| **Prioridad del consumo humano** | Siempre prevalece el uso para **consumo humano, uso doméstico de subsistencia y saneamiento** al otorgar o limitar derechos | **Art. 5 bis** | [VERIFICADO] |
| **Temporalidad de los nuevos derechos** | Los derechos concedidos tienen duración de **30 años**, prorrogables **por el solo ministerio de la ley** salvo que la autoridad acredite no uso efectivo o afectación a la sustentabilidad | **Art. 6** | [VERIFICADO] |
| **Extinción por no uso — consuntivos** | **5 años** de no uso efectivo | **Art. 6 bis** (y 129 bis 4 y ss.) | [VERIFICADO] |
| **Extinción por no uso — no consuntivos** | **10 años** de no uso efectivo | **Art. 6 bis** | [VERIFICADO] |
| Cómputo de los plazos | Desde la publicación de la resolución que incluye el derecho en el **listado de derechos afectos al pago de patente por no uso** | **Art. 129 bis 7** | [SECUNDARIO] |
| Procedimiento de extinción | Resolución anual, notificación, **30 días** para oposición, informe técnico y resolución fundada del Director General de Aguas | **Art. 134 bis** | [VERIFICADO] |
| **Inscripción obligatoria** | Plazo máximo de **5 años desde la publicación de la ley** (es decir, hasta el **6 de abril de 2027**) para anotar al margen de la inscripción en el Registro de Propiedad de Aguas la constancia de inscripción en el **Catastro Público de Aguas** | Disposiciones transitorias | [SECUNDARIO] |
| Destino del agua extinguida | Al terminar, caducar, extinguirse o renunciarse un derecho, las aguas quedan libres para ser **reservadas por el Estado** o para constituir nuevos derechos | — | [SECUNDARIO] |

> **Impacto directo sobre minería.** La combinación de (i) temporalidad de 30 años, (ii) extinción por
> no uso y (iii) el vínculo entre "uso efectivo" y el **monitoreo de extracciones efectivas** convierte
> el cumplimiento del MEE en un asunto de **conservación del derecho de agua**, no solo de
> cumplimiento administrativo. No transmitir datos de extracción puede alimentar la evidencia de no uso.

### 8.2 Obligación de monitoreo y reporte de extracciones efectivas ante la DGA

**Marco legal:** **[VERIFICADO]**

| Norma | Contenido |
|---|---|
| **Código de Aguas, arts. 67, 68 y 173** | El **art. 68** faculta a la DGA para exigir la instalación y mantención de sistemas de medición de caudales, volúmenes extraídos y niveles freáticos (estáticos y dinámicos) en las obras, más un **sistema de transmisión** de la información obtenida |
| **Ley N.º 21.064 (D.O. 27-ene-2018)** | Modificó el Código de Aguas y fortaleció las herramientas de fiscalización y monitoreo de la DGA. Es la base de la implementación del MEE |
| **Ley N.º 21.435 (D.O. 06-abr-2022)** | Reforma general del Código de Aguas (ver §8.1) |
| **Ley N.º 21.740 (D.O. 23-abr-2025)** | Modifica el Código de Aguas en materia de **procedimiento de fiscalización y vigilancia de la DGA**: colaboración de municipalidades y otros órganos del Estado, **procedimiento sancionatorio simplificado**, **paralización inmediata de extracciones no autorizadas** y notificación por medios electrónicos |

**Resoluciones DGA vigentes — aguas subterráneas:**

| Resolución | Fecha | Contenido | Etiqueta |
|---|---|---|---|
| **Res. DGA (Exenta) N.º 1238** | **21-jun-2019**, publicada en el D.O. el **01-jul-2019** | **Norma matriz nacional.** Determina las condiciones técnicas y los plazos a nivel nacional para instalar y mantener un sistema de monitoreo y transmisión de extracciones efectivas en obras de captación de **aguas subterráneas**. Define **4 estándares**, **3 sistemas de medición** y **3 sistemas de transmisión** | [VERIFICADO] |
| **Res. DGA (Exenta) N.º 564** | **13-abr-2020** | Rectifica la Res. 1238 (estándares y respaldo en Centro de Control) | [VERIFICADO] |
| **Res. DGA (Exenta) N.º 1608** | 2023 | Amplía los plazos de instalación para los estándares **Menor** y **Caudales Muy Pequeños** | [SECUNDARIO] |
| **Res. DGA N.º 2170** | junio de 2025, vigente desde **01-ago-2025** | Manual Técnico N.º 1 para la **transmisión online**: endpoints REST, formato JSON y controles de ciberseguridad, aplicable a Centros de Control MEE | [SECUNDARIO] |
| **Resoluciones DGA regionales** | Se dictan por región/zona geográfica | **Son las que activan la obligación** y las que fijan los **rangos de caudal (l/s)** que asignan cada estándar. **Los plazos se cuentan desde la publicación de la resolución regional en el Diario Oficial** | [VERIFICADO] |
| Res. DGA N.º 2129 de 2016 | 2016 | Titulares con orden previa de control de extracciones: mantienen su sistema y deben registrarse en el software MEE, transmitiendo **mensualmente** por formulario (totalizador, caudal y nivel freático) | [VERIFICADO] |

**Aguas superficiales:**

| Norma | Contenido | Etiqueta |
|---|---|---|
| **Decreto MOP N.º 53 de 2020** (03-abr-2020, D.O. **15-oct-2020**) | Reglamento de monitoreo de extracciones efectivas de **aguas superficiales**. Obliga a instalar y mantener dispositivos de control y aforo más sistema de transmisión instantánea. Cuatro niveles de exigencia, con rangos de caudal fijados en las resoluciones regionales | [VERIFICADO] |

### 8.3 ¿A quién aplica y qué debe hacer?

**Aplica a:** titulares de derechos de aprovechamiento cuya obra de captación esté en una **zona
geográfica cubierta por una resolución regional de MEE**; titulares con orden de control por la Res.
2129/2016 u otras resoluciones DGA (constitución de derechos, cambio de punto de captación, derechos
provisionales, procesos de fiscalización). **[VERIFICADO]**

**Cómo se determina el estándar:** por el **caudal total sumado de todos los derechos de
aprovechamiento que se ejercen en la misma obra de captación** (no por derecho individual). Los rangos
en l/s están en la **resolución regional**, no en la Res. 1238. **[VERIFICADO]**

**Los cuatro estándares (Res. DGA 1238/2019) — plazos oficiales:** **[VERIFICADO]** (tríptico oficial DGA)

| Estándar | Sistema de medición | Instalación del sistema de medición + registro de la obra en el Software MEE | Instalación del sistema de transmisión e inicio de transmisiones |
|---|---|---|---|
| **Mayor** | General | **4 meses** | **5 meses** |
| **Medio** | General o Básico | **10 meses** | **12 meses** |
| **Menor** | Básico | **60 meses** | **72 meses** |
| **Caudales Muy Pequeños** | Solo flujómetro | **60 meses** | **72 meses** |

*Los plazos se cuentan desde la publicación de la resolución regional en el Diario Oficial.*

**Frecuencias de medición y transmisión (aproximación de fuentes secundarias):** **[SECUNDARIO]**

| Estándar | Frecuencia de medición | Vía de transmisión | Desfase máximo |
|---|---|---|---|
| Mayor | 1 medición por hora | **Online** (API REST) | 7 días |
| Medio | 1 medición por día | **Archivo** (Excel) | 15 días |
| Menor | 1 medición por mes | **Formulario** | 1 mes |
| Caudales Muy Pequeños | 2 mediciones por año | **Formulario** | 1 mes |

**Sistemas de medición (Res. 1238/2019):** **[VERIFICADO]**

| Sistema | Componentes |
|---|---|
| **General** | Flujómetro (volumen y caudal) + sensor de nivel freático + **data logger** en la obra |
| **Básico** | Flujómetro igual al del sistema General + equipo para medir niveles freáticos, que **puede ser portátil** |
| **Caudales muy pequeños** | **Solo** flujómetro (no exige sensor de nivel freático ni data logger) |

**Sistemas de transmisión:** **Online** (desde un Centro de Control al Software DGA), **Archivo**
(carga de un Excel con el formato oficial) y **Formulario** (ingreso manual de caudales, volúmenes y
niveles freáticos). El flujómetro **no está obligado a medir caudal directamente**: el caudal puede
derivarse del volumen en un tiempo. La DGA **no acredita proveedores ni certifica instaladores**.
**[VERIFICADO]**

**Registro:** el titular designa un **informante** (puede ser un tercero autorizado, pero la
responsabilidad es siempre del titular), que debe tener **ClaveÚnica**, registrar la obra (se genera un
**código de obra y un código QR que debe exhibirse visiblemente en la obra**), los titulares, los
derechos y las características del sistema de medición. **[VERIFICADO]**

**Estado de los plazos a 2026 (fuente secundaria):** en Coquimbo, Valparaíso, Metropolitana, O'Higgins
y Maule los plazos de los estándares **Mayor** y **Medio** están **vencidos**; solo Maule mantiene plazo
remanente para usuarios del estándar Menor hasta 2028. **Sanciones:** multas en UTM, suspensión del
ejercicio del derecho, reducción del caudal autorizado y, en el marco de la Ley 21.435, riesgo de
**pérdida del derecho**. **[SECUNDARIO]**

> **Regla para el motor.** El motor **no puede** determinar por sí solo el estándar MEE de una faena:
> requiere (1) el caudal total de la obra en l/s y (2) la **resolución regional aplicable**. El agente
> debe pedir ambos datos y, si falta la resolución regional, **remitir al usuario a
> `dga.mop.gob.cl` → "Monitoreo de Extracciones Efectivas"** en lugar de asumir un estándar.

---

## Fórmulas y métodos

### M1. Corrección de límites permisibles por jornada y altitud (DS 594, Arts. 62–64)

**Fórmulas vigentes:**

```
Fj = (8 / h) × ((24 − h) / 16)          # h = horas trabajadas DIARIAS; solo si h > 8
Fj = 0,90                                # caso especial: jornada de 8 h/día con 45 h < semana <= 48 h
Fa = P / 760                             # P = presión atmosférica local en mmHg; solo si altitud > 1.000 m

LPP_corregido = LPP_tabla × Fj × Fa      # Fa solo sobre valores en mg/m3 y fibras/cc
LPT_corregido = LPT_tabla × Fa           # NUNCA Fj
LPA_corregido = LPA_tabla × Fa           # NUNCA Fj
```

Redondeo obligatorio: **Fj y Fa se expresan con dos decimales**; el segundo decimal se eleva si el
tercero es ≥ 5 y se desprecia si es < 5. **No se admiten aproximaciones parciales** (Arts. 62 y 63).

#### Ejemplo resuelto M1.a — Sílice cristalizada (cuarzo) en faena de altura

*Supuestos:* faena subterránea a **3.800 m s. n. m.**, turno de **12 horas diarias**. Presión
atmosférica local medida: **475 mmHg**.

| Paso | Cálculo | Resultado |
|---|---|---|
| 1. LPP de tabla (Art. 66, fracción respirable) | Sílice cristalizada — cuarzo | **0,08 mg/m³** |
| 2. Factor de jornada (h = 12 > 8) | `Fj = (8/12) × ((24−12)/16) = 0,6667 × 0,75 = 0,5000` | **Fj = 0,50** |
| 3. Factor de altitud (3.800 m > 1.000 m) | `Fa = 475 / 760 = 0,625` → redondeo a dos decimales (tercer decimal = 5 → se eleva) | **Fa = 0,63** |
| 4. LPP corregido (Art. 64) | `0,08 × 0,50 × 0,63` | **0,0252 → 0,025 mg/m³** |

**Interpretación:** el límite baja de 0,08 a **0,025 mg/m³**, es decir, a menos de un tercio. Una
concentración de 0,05 mg/m³ —que cumpliría el límite base— constituye **sobreexposición** en estas
condiciones.

```python
def corregir_lpp(lpp_tabla, horas_diarias, presion_mmHg, altitud_m, unidad="mg/m3"):
    """DS 594/1999 Arts. 62, 63 y 64 (texto vigente, Decreto 123/2015)."""
    # Fj — Art. 62
    if horas_diarias > 8:
        fj = round((8 / horas_diarias) * ((24 - horas_diarias) / 16), 2)
    else:
        fj = 1.0                      # usar 0.90 si 45 h < jornada_semanal <= 48 h con 8 h/dia
    # Fa — Art. 63 (solo mg/m3 y fibras/cc, y solo sobre 1.000 m s.n.m.)
    if altitud_m > 1000 and unidad in ("mg/m3", "fibras/cc"):
        fa = round(presion_mmHg / 760, 2)
    else:
        fa = 1.0
    return lpp_tabla * fj * fa, fj, fa
```

> **Advertencia de implementación.** El **DS 594 exige presión atmosférica local MEDIDA**, no estimada.
> Si el motor no dispone de una medición, puede estimar `P ≈ 760 · (1 − 2,25577×10⁻⁵ · h)^5,25588`
> (atmósfera estándar internacional), **pero debe marcar el resultado como estimación y exigir medición
> real antes de usarlo para una decisión de cumplimiento**. Esta fórmula **no está en el DS 594**.
> **[NO VERIFICADO — fórmula externa al reglamento]**

#### Ejemplo resuelto M1.b — CO y H₂S en el mismo escenario

| Sustancia | LPP tabla | Fj | Fa | LPP corregido |
|---|---|---|---|---|
| **Monóxido de carbono** (ppm) | 44 ppm | 0,50 | *no aplica a ppm* | **22 ppm** |
| **Monóxido de carbono** (mg/m³) | 48 mg/m³ | 0,50 | 0,63 | **15,1 mg/m³** |
| **H₂S** (ppm) | 8,8 ppm | 0,50 | *no aplica a ppm* | **4,4 ppm** |
| **H₂S** — LPT (ppm) | 15 ppm | *no aplica* | *no aplica a ppm* | **15 ppm** (sin cambio) |
| **H₂S** — LPT (mg/m³) | 21 mg/m³ | *no aplica* | 0,63 | **13,2 mg/m³** |

Obsérvese: el **LPT en ppm no se corrige en absoluto** (Fj no se aplica a LPT y Fa no se aplica a ppm).
Este es el error más frecuente en implementaciones caseras.

### M2. Caudal mínimo de ventilación en minería subterránea (DS 132, Arts. 132 y 138)

```
Q_personas [m3/min] = 3,0 × N_personas
Q_diesel   [m3/min] = 2,83 × Σ HP_efectivo_al_freno     # si el fabricante no especifica
Q_minimo   [m3/min] = Q_personas + Q_diesel
Restricción de velocidad media:  15 m/min <= v <= 150 m/min
Oxígeno: O2 >= 19,5 % en peso
```

#### Ejemplo resuelto M2

*Supuestos:* frente de producción con **12 personas** y **2 LHD diésel de 300 HP** cada uno, sin
especificación de caudal del fabricante. Sección de la galería principal: **20 m²**.

| Paso | Cálculo | Resultado |
|---|---|---|
| 1. Caudal por personas (Art. 138) | `3,0 × 12` | 36 m³/min |
| 2. Caudal por equipos diésel (Art. 132) | `2,83 × (2 × 300) = 2,83 × 600` | 1.698 m³/min |
| 3. Caudal mínimo total (Art. 132, inciso 2: se suman) | `36 + 1.698` | **1.734 m³/min ≈ 28,9 m³/s** |
| 4. Velocidad media resultante | `1.734 / 20` | **86,7 m/min** — dentro de 15–150 m/min ✔ |

**Conclusión:** los equipos diésel dominan el requerimiento (98 % del caudal). Reducir un LHD o
sustituirlo por eléctrico reduce el requerimiento a **885 m³/min**, con velocidad de 44,3 m/min,
también conforme.

### M3. Huella hídrica de escasez con AWARE

```
WSF_anual  [m3 mundo-eq] = Consumo_anual [m3] × CF_anual(pais_o_cuenca, sector)
WSF_mensual[m3 mundo-eq] = Σ_meses ( Consumo_mes [m3] × CF_mes(pais_o_cuenca, sector) )
```

El **consumo** debe calcularse según la definición del GRI 303-5 (extracción − descarga, más ajustes
por agua contaminada hasta inutilizarla y por almacenamiento).

#### Ejemplo resuelto M3.a — Faena minera en Chile, cálculo anual

*Supuestos:* extracción anual 1.500.000 m³; descarga anual 300.000 m³; sin agua almacenada ni
contaminada hasta inutilizarla.

| Paso | Cálculo | Resultado |
|---|---|---|
| 1. Consumo (GRI 303-5) | `1.500.000 − 300.000` | **1.200.000 m³** |
| 2. Factor AWARE 2.0 | Chile, **no agrícola**, anual | **45,5** |
| 3. Huella de escasez hídrica | `1.200.000 × 45,5` | **54.600.000 m³ mundo-eq** |
| 4. Comparación con promedio mundial | `1.200.000 × 17,9` (GLO no agrícola) | 21.480.000 m³ mundo-eq |

**Interpretación:** consumir 1,2 hm³ en Chile equivale, en términos de escasez, a **2,5 veces** el
impacto del mismo consumo en una ubicación mundial promedio del sector no agrícola.

**Error a evitar:** si se hubiera usado el factor *unspecified* de Chile (88,1), el resultado sería
**105.720.000 m³ mundo-eq**, casi el doble. Para minería corresponde el factor **no agrícola**.

#### Ejemplo resuelto M3.b — Efecto de la estacionalidad (mensual vs. anual)

*Supuestos:* mismo consumo total de 1.200.000 m³, Chile, sector no agrícola.

| Escenario | Cálculo | WSF (m³ mundo-eq) |
|---|---|---|
| **Factor anual** | `1.200.000 × 45,5` | **54.600.000** |
| **Mensual, consumo uniforme** (100.000 m³/mes) | `100.000 × (84,9+84,1+70,4+67,7+59,8+5,19+8,81+7,03+7,78+9,40+63,1+79,7)` = `100.000 × 547,91` | **54.791.000** |
| **Mensual, todo concentrado en enero** | `1.200.000 × 84,9` | **101.880.000** |
| **Mensual, todo concentrado en junio** | `1.200.000 × 5,19` | **6.228.000** |

**Interpretación:** con consumo uniforme, el factor anual es una buena aproximación (diferencia 0,3 %).
Pero con consumo estacional, el resultado varía **más de 16 veces** entre enero y junio. **Si la faena
tiene estacionalidad marcada, el cálculo mensual es obligatorio para no reportar una cifra engañosa.**

```python
CF_AWARE20_NONAGRI_ANUAL = {   # CC BY 4.0 — Seitfudem et al. 2025, doi:10.5281/zenodo.15133241
    "CHL": 45.5, "PER": 24.4, "ARG": 6.23, "BRA": 4.38,
    "COL": 1.12, "MEX": 20.3, "ESP": 35.5, "USA": 11.3, "GLO": 17.9,
}

def wsf_anual(consumo_m3: float, iso3: str) -> float:
    """Huella de escasez hídrica, m3 mundo-eq. Usar CF de CUENCA cuando se conozca."""
    return consumo_m3 * CF_AWARE20_NONAGRI_ANUAL[iso3]

def wsf_mensual(consumo_por_mes: list[float], cf_por_mes: list[float]) -> float:
    assert len(consumo_por_mes) == len(cf_por_mes) == 12
    return sum(c * f for c, f in zip(consumo_por_mes, cf_por_mes))
```

### M4. Clasificación de consecuencias GISTM

```
clase = max(clase_poblacion_en_riesgo,
            clase_perdida_de_vidas,
            clase_medio_ambiente,
            clase_salud_cultural_social,
            clase_infraestructura_economia)
```

Una vez asignada la clase, los **criterios de diseño de crecidas y sismo** (Anexo 1, §1.4) y los
**requisitos de gobernanza** quedan determinados: instalaciones **Alta / Muy alta / Extrema** requieren
CIRR (Comisión Independiente de Revisión de Relaves) y revisiones reforzadas.

---

## Cambios recientes (2024–2026)

| Fecha | Norma / hito | Qué cambió | Impacto en el motor | Etiqueta |
|---|---|---|---|---|
| **09-abr-2024** | **Decreto N.º 1/2024, Min. Minería** (D.O.) | Modifica el Título XV del **DS 132** (Reglamento de Seguridad Minera): régimen de **Declaración Minera y Proyecto Minero** para pequeña minería ≤ 5.000 t/mes; nuevos Arts. 615–616 (refugios en labores ciegas < 100 m), 626 (ventilación desde 100 m de avance) y 628 (mediciones mensuales de O₂, CO y humos nitrosos para faenas > 1.000 t/mes) | Añadir bifurcación por tamaño de faena antes de aplicar umbrales de ventilación | [SECUNDARIO] |
| **05-jul-2024** | **Res. Ex. N.º 1706/2024, Min. Minería** (D.O.) | Somete a **consulta pública un nuevo reglamento que reemplazaría el DS 248/2007** de depósitos de relaves. Observaciones hasta el 12-ago-2024 | Advertir al usuario de reforma en trámite; **el DS 248 sigue vigente** | [VERIFICADO] |
| **enero de 2025** | **Lanzamiento del GTMI** | Instituto independiente (ICMM + PNUMA + PRI) con sede en Sudáfrica para supervisar la conformidad con el GISTM y acreditar auditores | No existe aún certificación GISTM de terceros | [VERIFICADO] |
| **03-abr-2025** | **AWARE 2.0** (Zenodo v1.0.0, CC BY 4.0) | Nueva versión del método de escasez hídrica sobre WaterGAP 2.2e. **Cambian todos los factores y los promedios globales** (GLO no agrícola 20 → 17,9) | Migrar factores; fijar versión en configuración; **redistribución permitida con atribución** | [VERIFICADO] |
| **23-abr-2025** | **Ley N.º 21.740** (D.O.) | Modifica el Código de Aguas: procedimiento de **fiscalización y vigilancia** de la DGA, sancionatorio simplificado, **paralización inmediata de extracciones no autorizadas**, notificación electrónica | Elevar el riesgo asignado al incumplimiento del MEE | [SECUNDARIO] |
| **01-ago-2025** | **Res. DGA N.º 2170/2025** | Manual Técnico N.º 1 de transmisión **online** MEE: endpoints REST, JSON y ciberseguridad | Especificación técnica para integraciones automáticas | [SECUNDARIO] |
| **29-sep-2025** | **Ley N.º 21.770** — Ley Marco de Autorizaciones Sectoriales (D.O.) | Crea OASI, Comité y sistema **SUPER**; técnicas habilitantes alternativas (declaración jurada). Su **art. 97 modifica la Ley 20.551** de cierre de faenas, con vigencia diferida a los reglamentos | Nuevo canal de tramitación; revisar vigencia de cada reglamento | [VERIFICADO] |
| **04-nov-2025** | **ICMM Tailings Progress Report** | 836 instalaciones: 67 % en conformidad total, 33 % parcial; > 80 % en clases Extrema y Muy alta; 53–65 % en clases Alta/Significativa/Baja | Referencia de *benchmark* sectorial | [VERIFICADO] |
| **15-oct-2025 → 05-mar-2026** | **ISO 14046:2014** | En **revisión sistemática**. Resultado (confirmación o revisión) no verificado | Vigilar; puede requerir actualizar el módulo de huella hídrica | [NO VERIFICADO] |
| **16-ene-2026** | **Decreto N.º 40, MINSAL** (D.O.) | Modifica el **Art. 98 bis del DS 594**: obligaciones frente a **altas temperaturas y altas temperaturas extremas** (seguimiento diario de alertas DMC/SENAPRED, identificación y evaluación por puesto, plan de gestión con participación de trabajadores, norma técnica MINSAL) | Nuevo módulo de alertas por calor extremo, distinto del TGBH clásico | [VERIFICADO] |
| **febrero de 2026** | **GTMI** nombra CEO (Ed Toms) y constituye su **Comité Técnico** | Responsable de protocolos de auditoría, acreditación, formación e interpretación del GISTM | — | [VERIFICADO] |
| **junio de 2026** | Reunión del Comité Técnico del GTMI (Canadá) | Discusión del marco de aseguramiento; tras finalizarlo se convocará a auditores | — | [SECUNDARIO] |
| **30-abr-2026** | **DS N.º 15/2026, Min. Minería** en toma de razón | Modifica el **DS 41/2012** (reglamento de la Ley 20.551) para adecuarlo a la LMAS: **declaración jurada** para faenas ≤ 5.000 t/mes, con los mismos efectos que un Plan de Cierre aprobado, vía **SUPER**, **vigencia máxima 60 meses** | Nuevo régimen para pequeña minería; **confirmar publicación en el D.O. antes de aplicarlo** | [SECUNDARIO] |

---

## Pendientes y dudas

| # | Asunto | Estado | Cómo resolverlo |
|---|---|---|---|
| 1 | **Factor de seguridad estático "puro" del DS 248** | **[NO VERIFICADO]** | El DS 248 solo fija **FS ≥ 1,2** para las fases pseudo-estáticas del Art. 14 letra o). No se verificó que exista un FS estático distinto (1,4 / 1,5) en el reglamento. **No asumirlo.** Revisar el texto íntegro del Art. 14 en el Diario Oficial o pedir pronunciamiento a SERNAGEOMIN |
| 2 | **Publicación del nuevo reglamento de relaves que reemplaza el DS 248** | **[NO VERIFICADO]** | La consulta pública cerró el 12-ago-2024. Verificar en `bcn.cl/leychile` (Ministerio de Minería, decretos 2025–2026) y en `sernageomin.cl` |
| 3 | **Publicación efectiva del DS 15/2026 en el Diario Oficial** | **[NO VERIFICADO]** | Estaba en toma de razón de Contraloría al 30-abr-2026. Verificar en el Diario Oficial y en el Registro de Toma de Razón |
| 4 | **Contenido exacto del art. 97 de la Ley 21.770 sobre la Ley 20.551** | **[NO VERIFICADO]** | No se pudo leer el articulado completo. Consultar el texto en `bcn.cl/leychile` (idNorma 1216930) y verificar qué artículos de la Ley 20.551 quedaron modificados y desde cuándo rigen |
| 5 | **Número total de requisitos del GISTM: 77 vs. 78** | Discrepancia menor | El conteo automático sobre el PDF oficial en español arroja 78 etiquetas `Requisito X.Y`; ICMM y Global Tailings Review declaran **77**. **Usar 77** y verificar contra la versión en inglés cuál requisito está duplicado o mal numerado en la traducción |
| 6 | **Progresión exacta de las parcialidades de la garantía (Ley 20.551)** | **[SECUNDARIO]** | La estructura `0,2 + 0,8·(i−1)/(N−1)` se extrajo de la guía oficial de SERNAGEOMIN con OCR degradado. Verificar visualmente en `2020-GUIA-GARANTIA.pdf` antes de usarla para cálculos financieros |
| 7 | **Rangos de caudal (l/s) de cada estándar MEE** | **[NO VERIFICADO]** | No existen a nivel nacional: los fija **cada resolución regional**. El motor debe pedir al usuario la resolución regional aplicable o el rango que le fue notificado |
| 8 | **Frecuencias y desfases de transmisión MEE** | **[SECUNDARIO]** | La tabla de frecuencias (horaria/diaria/mensual/semestral y desfases de 7/15/30 días) proviene de fuentes secundarias. Contrastar con el texto de la Res. DGA 1238/2019 y la Res. 1608/2023 |
| 9 | **Resultado de la revisión sistemática de ISO 14046** | **[NO VERIFICADO]** | Cerró el 05-mar-2026. Consultar `iso.org/standard/43263.html` (devolvió HTTP 403 a la herramienta de investigación; revisar manualmente o vía INN Chile) |
| 10 | **Vigencia de la Res. DGA 1608/2023 y estado regional de plazos** | **[SECUNDARIO]** | Datos de estado regional (plazos vencidos en Coquimbo, Valparaíso, RM, O'Higgins, Maule) provienen de una consultora. Verificar en la DGA regional |
| 11 | **Numeración final de los Arts. 615–616, 626 y 628 del DS 132** | **[SECUNDARIO]** | Extraídos de una lectura indirecta del Decreto 1/2024. Verificar artículo por artículo sobre el texto refundido de BCN |
| 12 | **Factores AWARE de cuenca para faenas chilenas y peruanas concretas** | Pendiente de trabajo | Los factores de país son gruesos. Descargar `AWARE20_Native_CFs.xlsx` y los `.gpkg` del DOI 10.5281/zenodo.15133241 y hacer el cruce espacial faena→cuenca |
| 13 | **Tabla completa del Art. 61 del DS 594 (límites absolutos)** | Parcial | Solo se transcribieron los valores necesarios. Para el motor completo hay que digitalizar la tabla completa desde la imagen oficial (BCN, imagen `47020.jpg`) con verificación visual |
| 14 | **Protocolo PREXOR — versión y resolución vigente** | **[SECUNDARIO]** | El nivel de acción 82 dB(A) / 135 dB(C)Peak proviene de fuentes secundarias (IST, SIGWEB). Verificar el número y fecha de la resolución exenta MINSAL que aprueba la versión vigente del PREXOR en `minsal.cl` o `ispch.gob.cl` |
| 15 | **Correspondencia texto refundido DS 132 ↔ numeración citada** | Verificado parcialmente | Los Arts. 132, 136–146 se verificaron contra el texto refundido de BCN. El Art. 197 (simulacros anuales) se citó desde el listado de modificaciones; confirmar su numeración final |

---

## Fuentes

Marcadas **[OF]** oficial / primaria y **[SEC]** secundaria.

### GISTM y relaves internacionales
1. **[OF]** Global Tailings Review — *Estándar Global de Gestión de Relaves para la Industria Minera* (versión en español, agosto 2020). https://globaltailingsreview.org/wp-content/uploads/2020/08/global-industry-standard_ES.pdf
2. **[OF]** Global Tailings Review — *Global Industry Standard on Tailings Management* (versión en inglés). https://globaltailingsreview.org/global-industry-standard/
3. **[OF]** ICMM — *Global Industry Standard on Tailings Management* (estructura, plazos y protocolos de conformidad). https://www.icmm.com/our-principles/gistm
4. **[OF]** ICMM — *ICMM publishes report on members' collective progress towards full conformance with GISTM* (04-nov-2025). https://www.icmm.com/en-gb/news/2025/progress-towards-full-conformance-GISTM
5. **[OF]** ICMM — *Tailings Progress Report: Implementing the GISTM* (2025). https://www.icmm.com/en-gb/research/tailings-management/2025/tailings-progress-report
6. **[OF]** ICMM — *Member Disclosures on Progress Towards Conformance with the GISTM*. https://www.icmm.com/conformance-gistm
7. **[OF]** GTMI — *About the GTMI* y *GTMI Appoints Inaugural CEO and Technical Committee*. https://thegtmi.org/about-the-gtmi/ · https://thegtmi.org/gtmi-appoints-inaugural-ceo-and-technical-committee/
8. **[OF]** UNEP — *New independent institute to drive and assess the implementation of GISTM* (2025). https://www.unep.org/news-and-stories/press-release/new-independent-institute-drive-and-assess-implementation-global
9. **[SEC]** Canadian Mining Journal — *Global tailings institute advances toward certification rollout* (2026). https://www.canadianminingjournal.com/news/global-tailings-institute-advances-toward-certification-rollout-with-leadership-changes/

### Chile — relaves y cierre de faenas
10. **[OF]** BCN / Ley Chile — **Decreto 248 de 2007**, Ministerio de Minería (Reglamento de depósitos de relaves). https://www.bcn.cl/leychile/navegar?idNorma=259901
11. **[OF]** BCN / Ley Chile — **Ley 20.551** (cierre de faenas e instalaciones mineras). https://www.bcn.cl/leychile/navegar?idNorma=1032158
12. **[OF]** BCN / Ley Chile — **Decreto 41 de 2012**, Ministerio de Minería (Reglamento de la Ley de Cierre). https://www.bcn.cl/leychile/navegar?idNorma=1045967
13. **[OF]** BCN / Ley Chile — **Resolución 1706 exenta de 2024**, Ministerio de Minería (consulta pública nuevo reglamento de relaves). https://www.bcn.cl/leychile/navegar?i=1204711
14. **[OF]** SERNAGEOMIN — *Guía metodológica de cálculo, determinación y disposición de la garantía financiera que establece la Ley 20.551* (2020). https://www.sernageomin.cl/wp-content/uploads/2025/12/2020-GUIA-GARANTIA.pdf
15. **[OF]** SERNAGEOMIN — *Autorización de construcción de depósitos de relaves*. https://www.sernageomin.cl/autorizacion-construccion-relave/
16. **[SEC]** Carey Abogados — *Se modifica el Reglamento de la Ley de Cierre de Faenas Mineras incorporando declaración jurada como mecanismo habilitante* (05-may-2026). https://www.carey.cl/se-modifica-el-reglamento-de-la-ley-de-cierre-de-faenas-mineras-incorporando-declaracion-jurada-como-mecanismo-habilitante
17. **[SEC]** Carey Abogados — *Consulta ciudadana sobre modificación al Reglamento de Depósito de Relaves* (2021). https://www.carey.cl/consulta-ciudadana-sobre-modificacion-al-reglamento-de-deposito-de-relaves/
18. **[SEC]** Consejo Minero — *Normativas que aplican a los relaves en Chile*. https://consejominero.cl/plataformas-digitales/plataforma-de-relaves/normativas-relaves-chile/

### Chile — salud ocupacional y seguridad minera
19. **[OF]** BCN / Ley Chile — **Decreto 594 de 1999**, Ministerio de Salud. Texto vigente (última versión 16-ene-2026; última modificación Decreto 40, D.O. 16-ene-2026). Tablas de los Arts. 61, 62 y 66 publicadas como imágenes oficiales (`47020.jpg` a `47026.jpg`) y tablas TGBH / costo energético (`14086.jpg`, `14087.jpg`). https://www.bcn.cl/leychile/navegar?idNorma=167766
20. **[OF]** BCN / Ley Chile — **Decreto 132 de 2002**, Ministerio de Minería (Reglamento de Seguridad Minera). Texto refundido vigente, última versión 09-abr-2024 (Decreto 1 de 2024). https://www.bcn.cl/leychile/navegar?idNorma=221064
21. **[OF]** BCN / Ley Chile — **Decreto 1 de 2024**, Ministerio de Minería (modifica el DS 132, Título XV). https://www.bcn.cl/leychile/navegar?idNorma=1202464
22. **[OF]** Ministerio de Salud — *Protocolo sobre normas mínimas para el desarrollo de programas de vigilancia de la pérdida auditiva por exposición a ruido en los lugares de trabajo (PREXOR)*. https://www.minsal.cl/sites/default/files/files/protocolo_vigilancia_expuestos_a_ruido_minsal.pdf
23. **[OF]** Instituto de Salud Pública de Chile — sección *Ruidos*, Salud Ocupacional. https://www.ispch.gob.cl/salud-de-los-trabajadores/publicaciones-de-referencia/ruidos/
24. **[SEC]** IST — *Protocolo de Exposición Ocupacional a Ruido – PREXOR*. https://ist.cl/protocolo-de-exposicion-ocupacional-a-ruido-prexor/
25. **[OF]** SUSESO — Normativa: Decreto Supremo N.º 248 de 2007 y Decreto 132 de 2002. https://www.suseso.cl/612/w3-article-19172.html · https://www.suseso.gob.cl/612/w3-propertyvalue-189223.html

### Huella hídrica: ISO, AWARE, GRI, WRI
26. **[OF]** ISO — *ISO 14046:2014 Environmental management — Water footprint — Principles, requirements and guidelines*. https://www.iso.org/standard/43263.html
27. **[OF]** WULCA — *What is AWARE (Available WAter REmaining)?*. https://wulca-waterlca.org/what-is-aware/
28. **[OF]** WULCA — *Sector-specific AWARE Factors*. https://wulca-waterlca.org/what-is-aware/sector-specific-aware-factors/
29. **[OF]** WULCA — *Download AWARE Factors* y *Official versions of AWARE*. https://wulca-waterlca.org/what-is-aware/download-aware-factors/ · https://wulca-waterlca.org/what-is-aware/official-versions/
30. **[OF]** Seitfudem, G., Berger, M., Müller Schmied, H., & Boulay, A.-M. (2025). *The updated and improved method for water scarcity impact assessment in LCA, AWARE2.0* [Data set], Zenodo, v1.0.0, 03-abr-2025, **licencia CC BY 4.0**. https://doi.org/10.5281/zenodo.15133241
31. **[OF]** Seitfudem, G., Berger, M., Müller Schmied, H., & Boulay, A.-M. (2025). *The updated and improved method for water scarcity impact assessment in LCA, AWARE2.0*. **Journal of Industrial Ecology**. https://doi.org/10.1111/jiec.70023
32. **[OF]** Datos complementarios AWARE 2.0 (agregaciones por cultivo). https://doi.org/10.5281/zenodo.16332127
33. **[OF]** Boulay, A.-M., et al. (2018). *The WULCA consensus characterization model for water scarcity footprints (AWARE)*. **Int. J. Life Cycle Assess.** 23(2), 368–378. https://doi.org/10.1007/s11367-017-1333-8
34. **[OF]** Müller Schmied, H., et al. (2024). *WaterGAP v2.2e*. **Geosci. Model Dev.** 17(23), 8817–8852. https://doi.org/10.5194/gmd-17-8817-2024
35. **[OF]** GRI — *GRI 303: Water and Effluents 2018* (PDF oficial). https://www.globalreporting.org/publications/documents/english/gri-303-water-and-effluents-2018
36. **[OF]** GRI — *Topic Standard for Water and Effluents* (estado del estándar). https://www.globalreporting.org/standards/standards-development/topic-standard-for-water-and-effluents/
37. **[OF]** WRI — *Aqueduct 4.0: Updated Decision-Relevant Global Water Risk Indicators* (2023). https://www.wri.org/research/aqueduct-40-updated-decision-relevant-global-water-risk-indicators
38. **[OF]** WRI — *Prioritize Basins: Target Water Challenges by Thresholds*. https://www.wri.org/aqueduct/help-center/prioritize-basins-thresholds
39. **[OF]** WRI — *Aqueduct 4.0 data dictionary* (categorías y umbrales). https://github.com/wri/Aqueduct40/blob/master/data_dictionary_water-risk-atlas.md

### Chile — agua
40. **[OF]** BCN / Ley Chile — **Ley 21.435** (reforma del Código de Aguas, D.O. 06-abr-2022). https://www.bcn.cl/leychile/navegar?idNorma=1174443
41. **[OF]** BCN / Ley Chile — **Ley 21.740** (modifica el Código de Aguas en fiscalización y vigilancia de la DGA, D.O. 23-abr-2025). https://www.bcn.cl/leychile/navegar?idNorma=1212671
41 bis. **[OF]** BCN / Ley Chile — **Ley 21.770**, Ley Marco de Autorizaciones Sectoriales (D.O. 29-sep-2025). https://www.bcn.cl/leychile/navegar?idNorma=1216930
41 ter. **[OF]** BCN / Ley Chile — **Código de Aguas** (DFL 1.122 de 1981), arts. 67, 68 y 173. https://www.bcn.cl/leychile/navegar?idNorma=5605 · **Ley 21.064** (D.O. 27-ene-2018). https://www.bcn.cl/leychile/navegar?idNorma=1114175
42. **[OF]** DGA — *Monitoreo de Extracciones Efectivas: preguntas frecuentes, aguas subterráneas* (diciembre 2021). https://dga.mop.gob.cl/uploads/sites/13/2024/08/preguntas_frecuentes_aguas_subterraneas.pdf
43. **[OF]** DGA — *Tríptico MEE aguas subterráneas* (plazos por estándar). https://dga.mop.gob.cl/uploads/sites/13/2024/08/Triptico_MEE-Aguas-subterraneas.pdf
44. **[OF]** DGA — *Nuevo Reglamento de Monitoreo de Extracciones Efectivas de Aguas Superficiales* (Decreto MOP N.º 53 de 2020). https://dga.mop.gob.cl/nuevo-reglamento-de-monitoreo-de-extracciones-efectivas-de-aguas-superficiales-dga/
45. **[OF]** DGA — *Legislación*. https://dga.mop.gob.cl/legislacion/
46. **[SEC]** DLA Piper — *Chile: Nueva Ley N.º 21.740/2025 que modifica el Código de Aguas*. https://www.dlapiper.com/es-cl/insights/publications/2025/04/chile-amends-its-water-code
47. **[SEC]** DLA Piper — *Chile aprueba Ley Marco de Autorizaciones Sectoriales* (Ley 21.770). https://www.dlapiper.com/es-pr/insights/publications/2025/09/chile-approves-framework-law-on-sectoral-authorizations
48. **[SEC]** MiPozo — *Normativa MEE de la DGA: resoluciones, plazos y obligaciones*. https://mipozo.cl/dga/normativa
49. **[SEC]** Cruzat Ingeniería — *Control de Extracciones Efectivas DGA: plazos y multas 2026*. https://cruzat.com/noticias/control-de-extracciones-efectivas

---

*Documento preparado para el proyecto de código abierto **Agentes ESG**. Última revisión: 2026-09-16.
Los datos etiquetados `[NO VERIFICADO]` no deben alimentar alertas de seguridad sin validación humana
previa contra la fuente oficial.*
