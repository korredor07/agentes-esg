---
name: mineria
description: Seguridad en faenas mineras de Chile: depósitos de relaves (DS 248/2007), ventilación en minería subterránea (DS 132/2002), límites de exposición a polvo, sílice y gases (DS 594/1999), plan de cierre y garantía (Ley 20.551) y conformidad con el GISTM. Úsala cuando hablen de relaves, revancha, factor de seguridad, muro de contención, ventilación, oxígeno, gases en la mina, sílice, polvo respirable, jornada de altura, plan de cierre, SERNAGEOMIN o GISTM.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Minería: relaves, ventilación, exposición, cierre y GISTM

Este módulo toca la seguridad de personas. Dos reglas que no se negocian:

1. **Si un valor está fuera de rango, la acción va primero y el informe después.**
   Oxígeno bajo 19,5 % no es un hallazgo: es una evacuación.
2. **Nunca inventes un límite, un caudal, un factor de seguridad ni un artículo.**
   El motor solo trae valores verificados. Cuando algo no está verificado, lo dice
   y no calcula. Repite eso tal cual; no lo rellenes con lo que "suele usarse".

## Lo primero: ¿hay alguien en riesgo ahora mismo?

Antes de explicar nada, pregunta si hay gente trabajando en la condición que te
están describiendo. Si la respuesta es sí y el valor está fuera de rango, di la
acción inmediata en la primera frase.

| Situación | Acción inmediata | Norma |
|---|---|---|
| Oxígeno bajo **19,5 %** | **Evacuar la labor ahora.** No se vuelve a entrar hasta que personal calificado y autorizado certifique las condiciones. Para medir de nuevo, equipo autónomo de respiración | Art. 144 DS 132 |
| CO **40 ppm**, NOx **20 ppm** o aldehído fórmico **1,6 ppm** en el ambiente | **Detener el equipo diésel y ventilar.** Si hay personas con síntomas, evacuar | Art. 135 a) DS 132 |
| CO sobre **2.000 ppm** o NOx sobre **1.000 ppm** en el escape | **Sacar el equipo de servicio** hasta que mantención lo corrija y se vuelva a medir | Art. 135 b) DS 132 |
| Revancha bajo **1 metro** | **Suspender el depósito de relaves en la cubeta** y recuperar la revancha. Si hay riesgo de rebalse, es emergencia y hay que notificar de inmediato a SERNAGEOMIN | Arts. 49 y 35 DS 248 |
| Factor de seguridad bajo **1,2** (fases I y II) | **Detener el crecimiento del muro** y avisar hoy al Ingeniero de Registro y a la administración | Art. 14 letra o) DS 248 |
| Muro construido **aguas arriba** | Está **prohibido en Chile**, sin excepciones escritas. Se corrige cambiando el método con proyecto aprobado, no con un informe | Art. 14 letra h) DS 248 |
| Concentración sobre **5 veces** el límite permisible | **Sacar a la gente del área**, ventilar y volver a medir. El DS 594 lo prohíbe en cualquier momento de la jornada | Art. 60 DS 594 |

## Qué norma aplica a qué

- **DS 248/2007** — depósitos de relaves: diseño, construcción, operación y cierre.
  Fiscaliza SERNAGEOMIN.
- **DS 132/2002** (Reglamento de Seguridad Minera) — ventilación, gases,
  evacuación y refugios en minería subterránea.
- **DS 594/1999** (MINSAL) — límites permisibles de contaminantes químicos en
  cualquier lugar de trabajo, incluida la mina. Aplica también a lo que el DS 132
  no regula: por ejemplo el CO₂, que el DS 132 no limita y remite al DS 594.
- **Ley 20.551 y DS 41/2012** — plan de cierre de faenas y su garantía financiera.
- **GISTM** — estándar **voluntario** de industria. **No es ley en Chile.** Obliga
  por contrato a los miembros de ICMM. Lo obligatorio acá es el DS 248.

## Ventilación subterránea

El caudal mínimo **se suma**, no se elige el mayor. Es el error más común:

```
Q mínimo = 3 m³/min × personas  +  2,83 m³/min × HP diésel
```

3 m³/min por persona es el art. 138; 2,83 m³/min por caballo de fuerza efectivo
al freno es el art. 132, y solo se usa cuando el fabricante no especifica el
caudal del equipo. El inciso 2 del art. 132 dice expresamente que los dos
caudales se suman.

```bash
python .claude/motor/esg.py mineria ventilacion --personas 20 --hp-diesel 300 --oxigeno 20.5 --caudal 900
```

Opciones: `--personas` (obligatoria), `--hp-diesel`, `--caudal` (m³/min medidos),
`--oxigeno` (%), `--velocidad` (m/min), `--co`, `--nox`, `--aldehido` (ppm
ambientales), `--co-escape`, `--nox-escape` (ppm en el tubo de escape), `--co2`
(ppm), `--caudal-diesel-fabricante` (m³/min), `--perdidas` (%).

Otros valores del DS 132 que conviene tener a mano:

- Velocidad media del aire: entre **15 y 150 m/min** (art. 138).
- Pérdidas de ventilación toleradas: hasta **15 %** (art. 139).
- Aforo de entradas y salidas principales: **trimestral**; control general de la
  mina: **semestral** (art. 139).
- El proyecto de ventilación se aprueba ante SERNAGEOMIN antes de aplicarlo
  (art. 136).
- Refugios que garanticen sobrevivencia por al menos **48 horas** (art. 100) y
  procedimiento de evacuación actualizado con simulacros (art. 99).

## Depósitos de relaves

```bash
python .claude/motor/esg.py mineria relaves --revancha 1.4 --revancha-diseno 2 --factor-seguridad 1.25 --fase i --metodo aguas_abajo --altura-muro 18 --altura-final-muro 30 --muro-partida 3
```

Opciones: `--revancha` y `--revancha-diseno` (m), `--factor-seguridad`, `--fase`
(`i`, `ii`, `iii`, `iv`; también acepta `estatico`, `pseudoestatico`, `sismico`,
`dinamico`, `cierre`), `--metodo` (`aguas_arriba`, `aguas_abajo`, `eje_central`),
`--altura-muro`, `--altura-final-muro`, `--muro-partida` (m).

Lo que el motor revisa y con qué artículo:

| Qué se mide | Exigencia | Artículo |
|---|---|---|
| Método constructivo | Aguas arriba **prohibido** | 14 letra h) |
| Factor de seguridad, fases I y II | **No menor que 1,2** | 14 letra o) |
| Revancha | **1 metro como mínimo** | 49 |
| Muro de partida | Un décimo de la altura final, **nunca menos de 2 m** | 54 |
| Fase III (análisis dinámicos) | Solo se puede omitir en depósitos con muro **bajo 15 m** que cumplen el 1,2 | 14 letra o) |

Además, de forma permanente: informe **trimestral** a SERNAGEOMIN (art. 30),
Manual de Emergencias actualizado (art. 34), notificación **inmediata** de
cualquier emergencia (art. 35) e instrumentación para presiones de poros,
niveles freáticos, desplazamientos y aceleraciones sísmicas (art. 14 letra n).

**Cuidado con estos tres puntos** (el motor los repite en cada resultado):

- El DS 248 fija **un solo** factor de seguridad explícito: 1,2 para las fases I
  y II. Que la práctica internacional (CDA, ANCOLD) use 1,4 o 1,5 **no lo
  convierte en exigencia chilena**, y no está verificado que el reglamento tenga
  otro. No lo afirmes.
- Para las fases III y IV el reglamento no fija un número: el criterio lo define
  el proyecto aprobado y su revisor.
- **Ni el DS 248 ni el DS 132 tienen niveles tipo TARP** (verde/amarillo/rojo).
  Lo que existe es un esquema binario: detener el equipo y retirar al trabajador.
  El TARP es buena práctica del GISTM, no exigencia chilena.

## Exposición a polvo, sílice y gases

Esto es lo que más se equivoca, porque **el límite de la tabla casi nunca es el
límite que aplica**. Hay que corregirlo dos veces:

```
Fj = (8 / h) × ((24 − h) / 16)    solo si el turno pasa de 8 horas diarias (art. 62)
Fj = 0,90                          jornada de 8 h con semana de más de 45 y hasta 48 h
Fa = P / 760                       P = presión local medida en mmHg, solo sobre 1.000 m (art. 63)

LPP corregido = LPP × Fj × Fa      (art. 64)
LPT y LPA      = valor × Fa        nunca se les aplica Fj
```

Tres detalles que cambian el resultado:

- Desde el Decreto 123/2015 la corrección es por **jornada diaria**. La fórmula
  semanal antigua está derogada: usarla subestima el riesgo.
- **Fa no se aplica a los valores en ppm**, solo a mg/m³ y fibras/cc.
- Si la faena está sobre 1.000 m y no tienes la **presión medida**, el motor **no
  calcula**: el DS 594 exige presión medida y no hay fórmula reglamentaria para
  deducirla de la altitud. Pide un barómetro antes de concluir nada. Con
  `--estimar-presion` se puede estimar para dimensionar el problema, pero el
  resultado queda marcado como referencial y no sirve para declarar cumplimiento.

```bash
python .claude/motor/esg.py mineria exposicion --agente "Silice cristalizada - cuarzo" --concentracion 0.05 --unidad mg/m3 --horas 12 --altitud 3800 --presion 475
```

Opciones: `--agente`, `--concentracion`, `--unidad` (`mg/m3` o `ppm`), `--tipo`
(`ponderado`, `temporal` o `absoluto`), `--horas` (jornada diaria),
`--horas-semana`, `--altitud` (m), `--presion` (mmHg), `--estimar-presion`,
`--listar` (muestra los agentes cargados).

Ejemplo real del cálculo anterior: la sílice cuarzo tiene 0,08 mg/m³ de límite,
pero con turno de 12 horas a 3.800 m (475 mmHg) queda en **0,025 mg/m³**. Una
medición de 0,05 mg/m³ —que "cumpliría" el límite de tabla— es **sobreexposición
al doble**.

Cómo leer el resultado:

- **Sobre 100 %** del límite corregido: no cumple. Hay que controlar la fuente
  (ventilación, humectación, encierro, cambio de proceso). La mascarilla es una
  medida transitoria, no la solución.
- **Sobre 50 %**: cumple, pero sin holgura. Ese 50 % es un criterio de gestión del
  motor para anticiparse, **no una exigencia del DS 594**; dilo así.
- **Sobre 5 veces el límite**: prohibido siempre (art. 60), en cualquier momento
  de la jornada. Sacar a la gente.
- Si el agente es **A.1** (sílice, arsénico, benceno), avisa que es cancerígeno
  comprobado para el ser humano: cumplir el límite no vuelve segura la exposición.

Solo están cargados los agentes que la investigación verificó sobre la tabla del
art. 66. **La tabla de límites absolutos del art. 61 no está digitalizada**: si
te piden un LPA, dilo y no lo inventes.

## Plan de cierre (Ley 20.551)

```bash
python .claude/motor/esg.py mineria cierre --toneladas-mes 15000 --vida-util 12
```

Opciones: `--toneladas-mes` (toneladas brutas mensuales), `--vida-util` (años),
`--planta` y `--deposito-relaves` (banderas).

| Régimen | Cuándo | Artículo |
|---|---|---|
| Aplicación general | Más de **10.000 t brutas al mes** | 10 |
| Simplificado | Hasta 10.000 t/mes, y exploración o prospección | 10 y 16 |
| Declaración simplificada | Hasta **5.000 t/mes**, sin planta ni depósito de relaves | 16 |

Solo el régimen general exige **garantía financiera**: valor presente de todas
las medidas de cierre más el post cierre, descontado con la tasa de los bonos del
Banco Central en UF a 10 años (BCU-10), con instrumentos de la categoría A.1
(art. 52). La garantía se constituye por parcialidades en **dos tercios de la
vida útil** si la faena dura menos de 20 años, o en **15 años** si dura 20 o más.

El motor **no calcula el monto de cada parcialidad**: la progresión del 20 % al
100 % viene de una guía leída con OCR degradado y no está verificada. Dilo en vez
de estimar, porque ahí hay plata de por medio.

Otros plazos del régimen general: auditoría **cada 5 años** (art. 18),
actualización del plan **90 días** desde la notificación y 60 para que el
Servicio resuelva (art. 23), **3 días hábiles** para informar contingencias de la
garantía (art. 51).

Si la faena tiene hasta 5.000 t/mes, pregunta si el **DS 15/2026** ya se publicó
en el Diario Oficial: crearía la declaración jurada por el sistema SUPER con
vigencia de 60 meses, pero a la fecha de la investigación seguía en toma de razón
y **no está verificada su publicación**.

## GISTM

```bash
python .claude/motor/esg.py mineria gistm --clasificacion "muy alta" --requisitos 60 --miembro-icmm
```

Opciones: `--clasificacion` (`baja`, `significativa`, `alta`, `muy alta`,
`extrema`), `--requisitos` (cuántos de los 77 se cumplen), `--poblacion`
(personas potencialmente en riesgo, para sugerir la clasificación),
`--principios` (lista separada por comas, del 1 al 15), `--miembro-icmm`.

Son **6 temas, 15 principios y 77 requisitos auditables**. La clasificación de
consecuencias es el **máximo** de cinco dimensiones (población en riesgo, pérdida
de vidas, medio ambiente, salud y aspectos sociales, infraestructura y economía),
no un promedio, y de ella dependen los criterios de diseño de crecidas y sismo.
Las instalaciones alta, muy alta y extrema requieren además una Comisión
Independiente de Revisión de Relaves (CIRR).

Dos cosas que hay que decir siempre:

- El GISTM **no es ley en Chile**. Cumplirlo no sustituye el DS 248.
- **No existe todavía certificación GISTM de terceros**: el GTMI aún no abre la
  convocatoria de auditores. Si alguien dice estar "certificado GISTM", es una
  autodeclaración o un aseguramiento privado.

## Informe

```bash
python .claude/motor/esg.py mineria informe --personas 20 --hp-diesel 300 --oxigeno 19.2 --caudal 900 --revancha 0.8 --factor-seguridad 1.1 --metodo aguas_arriba
```

Arma un HTML en la carpeta `reportes/` de la empresa con las secciones para las
que hayas entregado datos, con las acciones inmediatas arriba y una sección de
"lo que no calculo aquí". Se abre con doble clic y se imprime a PDF con Ctrl+P.

## Cómo conversas esto

- Primero la acción, después la explicación. Si hay gente expuesta, no empieces
  con el marco legal.
- Habla en palabras de faena: "aire que entra al frente", "altura libre entre el
  agua y la coronación del muro", "polvo que se respira".
- Cita siempre el artículo. Da seguridad y permite que el experto lo verifique.
- No opines sobre responsabilidades ni sanciones de personas.
- Si un dato falta, pídelo: es mejor una respuesta incompleta que una tranquilizadora.

## Límites honestos

- **Esto no reemplaza al experto en prevención de riesgos de la faena**, al
  Ingeniero de Registro del depósito ni a la asistencia técnica del organismo
  administrador de la Ley 16.744 (ACHS, Mutual, IST o ISL). Tampoco reemplaza al
  Comité Paritario ni al Departamento de Prevención de Riesgos.
- No presenta nada ante SERNAGEOMIN ni ante la autoridad sanitaria: eso lo hace
  la empresa por sus canales.
- Las mediciones valen lo que vale el instrumento: deben hacerse con equipos
  calibrados y por personal competente.
- El régimen especial de pequeña minería del Decreto 1/2024 (faenas de hasta
  5.000 t/mes) no está verificado artículo por artículo: el motor aplica el
  régimen general de ventilación.
- Desde 2024 hay en trámite un reglamento que reemplazaría al DS 248. Mientras no
  se publique, rige el DS 248/2007 original.
