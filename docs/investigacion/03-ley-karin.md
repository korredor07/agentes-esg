# Ley Karin (Ley 21.643) y feriados legales de Chile

Fecha de investigación: 2026-09-15

> **Alcance:** insumo normativo para un motor Python de cálculo de plazos legales en días hábiles. Todos los datos llevan artículo, vigencia, URL y etiqueta [VERIFICADO] / [SECUNDARIO] / [NO VERIFICADO].

## Resumen

La **Ley N° 21.643 ("Ley Karin")** se publicó el **15-01-2024** y entró en vigencia el **1 de agosto de 2024** (art. primero transitorio: "el primer día del sexto mes subsiguiente a su publicación"). Modificó el **Código del Trabajo** (arts. 2°, 154 N° 12, 154 bis nuevo, y el Título IV del Libro II: **211-A, 211-B, 211-B bis, 211-C, 211-D y 211-E**) y, para el sector público, las leyes 18.575, 18.834, 18.883 y 18.695. Su cambio conceptual más relevante: el **acoso laboral ya no requiere reiteración** — basta **un solo acto**. Se suma la **violencia en el trabajo ejercida por terceros** (clientes, proveedores, usuarios).

Ha sido modificada dos veces: por la **Ley 21.687** (31-07-2024, corrección de una referencia al Estatuto Municipal) y por la **Ley 21.724** (03-01-2025), que le **agregó el artículo 6** (reporte semestral de denuncias a la SUSESO).

El procedimiento está desarrollado por el **Decreto Supremo N° 21, de 26-05-2024, del Ministerio del Trabajo y Previsión Social** (publicado el **03-07-2024**, vigente desde el 01-08-2024), y complementado por las **Circulares SUSESO N° 3.813 (07-06-2024), 3.819 y 3.825**, que incorporan el protocolo de prevención y el CEAL-SM al Compendio del Seguro de la Ley 16.744.

**Para el motor de plazos, el dato crítico es el art. 1° inciso 2° del DS 21:** *"los plazos contemplados en el presente reglamento serán de días hábiles, entendiéndose que son inhábiles los días sábados, domingos y festivos"*. Los dictámenes **ORD.N°386/10 (03-06-2025)** y **ORD.N°57/04 (26-01-2026)** de la Dirección del Trabajo lo confirman ("30 días hábiles administrativos") y agregan que el plazo **no se suspende** por feriado legal (vacaciones) ni por licencia médica. **La única excepción son los 15 días para aplicar medidas o sanciones: el art. 19 del DS 21 dice expresamente "quince días corridos".**

Cadena de plazos del procedimiento privado: medidas de resguardo **inmediatas** → **3 días hábiles** para informar a la DT o derivar → **30 días hábiles** para concluir la investigación → **2 días hábiles** para remitir el informe a la DT → **30 días hábiles** para el pronunciamiento de la DT (silencio = conclusiones válidas) → **15 días corridos** para aplicar medidas o sanciones.

La sección de **feriados** entrega las tablas 2025-2027 (fecha, nombre, ley, irrenunciabilidad) y las reglas algorítmicas de traslado (Leyes 19.668, 20.299, 20.983) y de los feriados móviles y variables (Pascua, solsticio de invierno de la Ley 21.357), más el tratamiento de los feriados por elecciones (art. 169 Ley 18.700). **En 2026 y 2027 no hay elecciones.**

## 1. Ley 21.643 "Ley Karin": identificación y vigencia

| Dato | Valor exacto | Fuente | Etiqueta |
|---|---|---|---|
| Número | Ley N° 21.643 | [1] | [VERIFICADO] |
| Título oficial | "MODIFICA EL CÓDIGO DEL TRABAJO Y OTROS CUERPOS LEGALES, EN MATERIA DE PREVENCIÓN, INVESTIGACIÓN Y SANCIÓN DEL ACOSO LABORAL, SEXUAL O DE VIOLENCIA EN EL TRABAJO" | [1] | [VERIFICADO] |
| Organismo | Ministerio del Trabajo y Previsión Social | [1] | [VERIFICADO] |
| Promulgación | 05-01-2024 | [1] | [VERIFICADO] |
| Publicación (Diario Oficial) | 15-01-2024 | [1] | [VERIFICADO] |
| Entrada en vigencia | **1 de agosto de 2024** (art. primero transitorio: "entrará en vigencia el primer día del sexto mes subsiguiente a su publicación en el Diario Oficial") | [1] | [VERIFICADO] |
| Última versión vigente en BCN | 03-01-2025 (modificada por Ley 21.724) | [1] | [VERIFICADO] |

Regla de transición (art. segundo transitorio): "Los procesos o investigaciones sobre acoso sexual, laboral o de violencia en el trabajo, iniciados antes de la vigencia de la presente ley, se regirán por las normas vigentes a la fecha de la presentación de la respectiva denuncia." [1] [VERIFICADO]

## 2. Definiciones (art. 2° inciso segundo del Código del Trabajo, texto fijado por Ley 21.643 art. 1 N°1 letra a)

Encabezado: "Las relaciones laborales deberán siempre fundarse en un trato libre de violencia, compatible con la dignidad de la persona y con perspectiva de género (…)". [1]

| Conducta | Definición legal (literal) | Norma |
|---|---|---|
| **Acoso sexual** | "el que una persona realice, en forma indebida, por cualquier medio, requerimientos de carácter sexual, no consentidos por quien los recibe y que amenacen o perjudiquen su situación laboral o sus oportunidades en el empleo" | Art. 2 inc. 2° letra a) CT [1] |
| **Acoso laboral** | "toda conducta que constituya agresión u hostigamiento ejercida por el empleador o por uno o más trabajadores, en contra de otro u otros trabajadores, por cualquier medio, **ya sea que se manifieste una sola vez o de manera reiterada**, y que tenga como resultado para el o los afectados su menoscabo, maltrato o humillación, o bien que amenace o perjudique su situación laboral o sus oportunidades en el empleo" | Art. 2 inc. 2° letra b) CT [1] |
| **Violencia en el trabajo (terceros)** | "la violencia en el trabajo ejercida por terceros ajenos a la relación laboral, entendiéndose por tal aquellas conductas que afecten a las trabajadoras y a los trabajadores, **con ocasión de la prestación de servicios, por parte de clientes, proveedores o usuarios, entre otros**" | Art. 2 inc. 2° letra c) CT [1] |

**Cambio clave respecto del texto anterior:** el acoso laboral ya NO exige reiteración — basta **un acto único**. [VERIFICADO] [1]

Además, la Ley 21.643 sustituyó en el art. 2 inciso cuarto CT la frase "u origen social," por ", origen social o cualquier otro motivo," (amplía las categorías de discriminación). [1] [VERIFICADO]

## 3. Artículos del Código del Trabajo modificados / creados

| N° del art. 1 de la Ley 21.643 | Norma del Código del Trabajo | Efecto |
|---|---|---|
| 1 | Art. 2°, incisos 2° y 4° | Nuevas definiciones (acoso sexual, acoso laboral, violencia de terceros) |
| 2 | Art. 154 N° 12 (Reglamento Interno) | El RIOHS debe contener el protocolo de prevención y el procedimiento |
| 3 | **Art. 154 bis (nuevo)** (el antiguo 154 bis pasa a ser **154 ter**) | Empleadores NO obligados a RIOHS: deben informar protocolo y procedimiento al suscribir el contrato |
| 4 | Epígrafe Título IV Libro II | Pasa a "DE LA PREVENCIÓN, INVESTIGACIÓN Y SANCIÓN DEL ACOSO SEXUAL, LABORAL Y LA VIOLENCIA EN EL TRABAJO" |
| 5 | Nuevo Párrafo 1° | "De la prevención del acoso sexual, laboral y la violencia en el trabajo" |
| 6 | **Art. 211-A (reemplazado)** | Derecho a prevención + protocolo de prevención (contenido mínimo) |
| 7 | Nuevo Párrafo 2° | "De la investigación y sanción del acoso sexual, laboral y la violencia en el trabajo" |
| 8 | **Art. 211-B (reemplazado)** | Principios del procedimiento + mandato de dictar Reglamento |
| 9 | **Art. 211-B bis (nuevo)** | Denuncia, medidas de resguardo, plazo de 2 días para la Inspección |
| 10 | **Art. 211-C (reemplazado)** | Investigación interna o derivación (3 días), 30 días de investigación, 30 días de pronunciamiento de la IT |
| 11 | **Art. 211-D**, nuevo inciso final | Vulneración de derechos fundamentales → art. 486 CT (tutela laboral) |
| 12 | **Art. 211-E (reemplazado)** | 15 días para aplicar medidas/sanciones; impugnación del despido |

> **Confirmado:** la numeración correcta es **211-A, 211-B, 211-B bis, 211-C, 211-D y 211-E** del Código del Trabajo. El artículo **211-B bis** (que muchas guías omiten) es el que contiene la denuncia y las medidas de resguardo. [VERIFICADO] [1]

Otros cuerpos legales modificados (arts. 2 a 6 de la ley):
- **Art. 2**: Ley 18.575 (Bases Generales de la Administración del Estado) — nuevo art. 14 (protocolo de prevención del sector público), art. 13 inc. final, art. 46 inc. 2°, art. 62 N° 10 nuevo.
- **Art. 3**: Ley 18.834 (Estatuto Administrativo) — arts. 12 e), 90, 119, 121, 125, 126, 129, 136, 137, 140, 143.
- **Art. 4**: Ley 18.883 (Estatuto Administrativo Municipal) — arts. 10 e), 88, 118, 120, 123, 124, 126, 127, 133, 135, 138, 141.
- **Art. 5**: Ley 18.695 (Orgánica Constitucional de Municipalidades) — arts. 60, 76, 77, 89.
- **Art. 6**: obligación de los organismos administradores de la Ley 16.744 de reportar semestralmente a la SUSESO las denuncias recibidas. [1] [VERIFICADO]

## 4. Obligaciones del empleador

### 4.1 Protocolo de prevención — contenido mínimo (art. 211-A CT)

Texto literal del art. 211-A incisos 1° y 2°:
- "Las trabajadoras y los trabajadores tienen derecho a que el empleador adopte e implemente las medidas destinadas a prevenir, investigar y sancionar las conductas de acoso sexual, laboral y la violencia en el lugar de trabajo."
- "Los empleadores deberán elaborar y poner a disposición de las trabajadoras y de los trabajadores un protocolo de prevención del acoso sexual, laboral y violencia en el trabajo, **a través de los organismos administradores de la ley N° 16.744**."

Contenido mínimo (art. 211-A inciso 3°, literales a) a e)): [VERIFICADO] [1]

| Literal | Contenido mínimo |
|---|---|
| a) | Identificación de los peligros y **evaluación de los riesgos psicosociales** asociados con acoso sexual, laboral y violencia en el trabajo, **con perspectiva de género** |
| b) | Medidas para prevenir y controlar tales riesgos, **con objetivos medibles**, para controlar su eficacia y velar por su mejoramiento y corrección continua |
| c) | Medidas para **informar y capacitar** a trabajadoras y trabajadores sobre riesgos identificados y evaluados, medidas de prevención y protección, derechos y responsabilidades |
| d) | Medidas para prevenir el acoso sexual, laboral y violencia en el trabajo, conforme a la naturaleza de los servicios y al funcionamiento del establecimiento o empresa |
| e) | Medidas de resguardo de la **privacidad y la honra** de todos los involucrados; medidas frente a **denuncias inconsistentes**; mecanismos de prevención, formación, educación y protección, independiente del resultado de la investigación |

**Obligación de información semestral (art. 211-A inciso 4°):** "las empleadoras y los empleadores tendrán el deber de informar **semestralmente** los canales que mantiene la empresa para la recepción de denuncias (…) así como las instancias estatales para denunciar cualquier incumplimiento a la normativa laboral y para acceder a las prestaciones en materia de seguridad social." [VERIFICADO] [1]

**Rol de la SUSESO (art. 211-A inciso final):** "La Superintendencia de Seguridad Social, mediante una norma de carácter general, entregará las directrices que deberán contemplarse por parte de las entidades administradoras de la ley N° 16.744 en el ejercicio de la asistencia técnica a los empleadores en todas las materias contempladas en este artículo." [VERIFICADO] [1]

### 4.2 Reglamento Interno (art. 154 N° 12 CT) y empleadores sin RIOHS (art. 154 bis CT)

- **Con RIOHS obligatorio:** el art. 154 N° 12 párrafo 1° pasa a exigir "El protocolo de prevención respecto del acoso sexual, laboral y la violencia en el trabajo, y el procedimiento al que se someterán las trabajadoras y los trabajadores, en conformidad a lo dispuesto en el Título IV del Libro II, el que considerará las medidas de resguardo que se adopten respecto de los involucrados y las sanciones que se aplicarán." [1] [VERIFICADO]
- **Sin RIOHS obligatorio (art. 154 bis nuevo):** el empleador "deberá poner en conocimiento de las trabajadoras y de los trabajadores el protocolo de prevención (…) y el procedimiento de investigación y sanción (…) **al momento de la suscripción del contrato de trabajo**". Además: "Lo anterior deberá constar por escrito y **se incorporará en el Reglamento a que se refiere el artículo 67 de la ley N° 16.744**." Y: "el empleador podrá contar con la **asistencia técnica del organismo administrador** de la ley referida al que se encuentre afiliado." [1] [VERIFICADO]

> **Diferencia por tamaño de empresa:** la Ley Karin NO distingue por número de trabajadores para la obligación sustantiva — **todos** los empleadores deben tener protocolo de prevención y procedimiento de investigación. La diferencia es el **vehículo formal**:
>
> | Dotación | Instrumento | Norma |
> |---|---|---|
> | **10 o más trabajadores permanentes** → obligado a RIOHS | Protocolo + procedimiento **dentro del Reglamento Interno de Orden, Higiene y Seguridad** | Art. 153 inc. 1° CT ("que ocupen normalmente **diez o más trabajadores permanentes**") + art. 154 N° 12 CT |
> | **Menos de 10** → no obligado a RIOHS | Entrega **por escrito al suscribir el contrato de trabajo** + incorporación al **Reglamento del art. 67 de la Ley 16.744**; puede pedir asistencia técnica al organismo administrador | Art. 154 bis CT |
>
> Además, el art. 153 inc. 2° CT obliga a remitir copia del reglamento **al Ministerio de Salud y a la Dirección del Trabajo dentro de los cinco días siguientes a su vigencia**. [VERIFICADO contra el texto vigente del Código del Trabajo en BCN] [27]
>
> La otra diferencia por tamaño está en la evaluación de riesgos psicosociales (ver sección 7): las empresas de **menos de 10 trabajadores no están obligadas a aplicar el CEAL-SM**.

## 5. El Reglamento: Decreto Supremo N° 21 de 2024 del Ministerio del Trabajo

| Dato | Valor exacto | Etiqueta |
|---|---|---|
| Norma | **Decreto N° 21**, Ministerio del Trabajo y Previsión Social, Subsecretaría del Trabajo | [VERIFICADO] [2] |
| Título | "APRUEBA REGLAMENTO QUE ESTABLECE LAS DIRECTRICES A LAS CUALES DEBERÁN AJUSTARSE LOS PROCEDIMIENTOS DE INVESTIGACIÓN DE ACOSO SEXUAL, LABORAL O DE VIOLENCIA EN EL TRABAJO" | [VERIFICADO] [2] |
| Promulgación | **26 de mayo de 2024** (no 28-05; el decreto dice "Núm. 21.- Santiago, 26 de mayo de 2024") | [VERIFICADO] [2] |
| Publicación (D.O.) | **3 de julio de 2024** | [VERIFICADO] [2] |
| Vigencia | Art. primero transitorio: "entrará en vigencia el día de su publicación en el Diario Oficial, **siempre que se encuentre vigente la ley N° 21.643**" → operativo desde el **1 de agosto de 2024** (BCN registra "Versión: Única - 01-AGO-2024") | [VERIFICADO] [2] |
| Habilitación legal | Art. 211-B inciso 2° CT | [VERIFICADO] [1][2] |
| Informe previo DT | Oficio ordinario N° 2000-14015/2024, de 25 de abril de 2024 | [VERIFICADO] [2] |

Estructura: Título I (Normas generales, arts. 1-10), Título II (Directrices del procedimiento, arts. 11-24), Título III (Denuncias ante tribunales, art. 25), Título IV (Reporte estadístico, art. 26) y tres disposiciones transitorias. [VERIFICADO] [2]

**Principios del art. 2° DS 21** (amplía los 4 del art. 211-B CT a nueve): a) perspectiva de género, b) no discriminación, c) **no revictimización o no victimización secundaria**, d) confidencialidad, e) imparcialidad, f) celeridad, g) razonabilidad, h) debido proceso, i) colaboración. [VERIFICADO] [2]

**Disposiciones transitorias relevantes:**
- Art. primero transitorio inc. 3°: mientras el empleador no haya actualizado su reglamento interno, "el empleador deberá derivar la denuncia a la Dirección del Trabajo de manera inmediata". [VERIFICADO] [2]
- Art. segundo transitorio: la DT debía implementar una plataforma electrónica de denuncias **dentro del plazo de un año contado desde la publicación** (es decir, a más tardar el 03-07-2025). [VERIFICADO] [2]
- Art. tercero transitorio: reporte estadístico web de la DT; primer reporte en la primera semana de enero de 2025 (período 01-08-2024 a 31-12-2024), luego a lo menos semestral. [VERIFICADO] [2]

## 6. Procedimiento paso a paso con plazos exactos

### 6.1 Denuncia (art. 211-B bis inc. 1° CT; arts. 11 y 12 DS 21)

- Forma: **verbal o escrita**, ante el empleador (empresa, establecimiento o servicio) **o** ante la Inspección del Trabajo / Dirección del Trabajo, **de manera presencial o electrónica**, "debiendo recibir un comprobante de la gestión realizada". [VERIFICADO] [1][2]
- Si es verbal: quien la recibe "deberá levantar un acta, la que será firmada por la persona denunciante. Una copia de ella deberá entregarse a la persona denunciante" (art. 211-B bis CT). El art. 12 DS 21 agrega que la copia se entrega "timbrada, fechada y con indicación de la hora de presentación". [VERIFICADO] [1][2]
- Contenido mínimo de la denuncia (art. 11 DS 21, literales a-e): identificación de la persona afectada (nombre completo, RUT, correo electrónico personal), identificación de la/s persona/s denunciada/s y sus cargos cuando sea posible, vínculo organizacional, relación de los hechos, y (si es ante la DT) identificación de la empresa y su RUT. [VERIFICADO] [2]
- **"No será posible considerar en los procedimientos de investigación un control de admisibilidad de la denuncia"** (art. 12 inc. 3° DS 21). [VERIFICADO] [2]
- Si la denuncia se dirige contra las personas del art. 4° inc. 1° CT (gerente, administrador, capitán de barco, quien representa al empleador), **siempre** debe derivarse a la Dirección del Trabajo (art. 12 inc. 5° DS 21). [VERIFICADO] [2]

### 6.2 Medidas de resguardo (art. 211-B bis incs. 2° y 3° CT; arts. 13 y 20 DS 21)

- El empleador debe adoptarlas **"de manera inmediata"** al recibir la denuncia, considerando "la gravedad de los hechos imputados, la seguridad de la persona denunciante y las posibilidades derivadas de las condiciones de trabajo". [VERIFICADO] [1]
- Medidas ejemplificadas en la ley: "la separación de los espacios físicos, la redistribución del tiempo de la jornada y proporcionar a la persona denunciante **atención psicológica temprana**, a través de los programas que dispone el organismo administrador respectivo de la ley N° 16.744". [VERIFICADO] [1][2]
- Si la denuncia se presenta ante la Inspección del Trabajo: "ésta solicitará al empleador la adopción de una o más medidas de resguardo (…) **en el plazo máximo de dos días hábiles**, las que se deberán adoptar de manera inmediata, una vez que se notifiquen de conformidad con el artículo 508" (art. 211-B bis inc. 3° CT; art. 20 DS 21). [VERIFICADO] [1][2]
- Notificación (art. 508 CT, según art. 20 DS 21): se entiende notificado **al tercer día hábil siguiente** contado desde la emisión del correo electrónico registrado en la DT, **o al sexto día hábil** de la recepción por la oficina de correos, si es por carta certificada. [VERIFICADO] [2]
- El empleador puede modificar o agregar medidas durante toda la investigación; la DT puede revisarlas y solicitar su modificación (art. 13 incs. 2° y 3° DS 21). [VERIFICADO] [2]
- Límite: "en ningún caso las medidas adoptadas podrán ser gravosas o perjudiciales para la persona denunciante, ni producir algún tipo de menoscabo" (art. 20 inc. 3° DS 21). [VERIFICADO] [2]

### 6.3 Decisión: investigación interna o derivación a la DT (art. 211-C inc. 1° CT; art. 12 inc. 4° DS 21)

- "el empleador dispondrá la realización de una investigación interna de los hechos o, **en el plazo de tres días**, remitirá los antecedentes a la Inspección del Trabajo respectiva" (art. 211-C inc. 1° CT). [VERIFICADO] [1]
- El reglamento precisa: si opta por investigación interna, "deberá informar a ese Servicio el inicio de una investigación, junto con las medidas de resguardo adoptadas, **en el plazo de tres días contados desde la (…) recepción de la denuncia**". Si deriva, o la persona denunciante lo solicita, en ese mismo plazo remite la denuncia con sus antecedentes (art. 12 inc. 4° DS 21). [VERIFICADO] [2]
- Cualquiera sea la decisión, debe informarse **por escrito** a la parte denunciante (art. 12 inc. final DS 21). [VERIFICADO] [2]

### 6.4 Persona investigadora (art. 211-C inc. final CT; art. 14 DS 21)

- "Cuando éstas se realicen por el empleador deberá designar **preferentemente** a un trabajador o trabajadora que cuente con **formación en materias de acoso, género o derechos fundamentales**" (art. 211-C inc. final CT). [VERIFICADO] [1]
- La designación "deberá ser informado por escrito a la persona denunciante" (art. 14 inc. 1° DS 21). [VERIFICADO] [2]
- Recusación: denunciante o denunciado, al declarar, pueden presentar antecedentes que afecten la imparcialidad del investigador y pedir su cambio; el empleador decide **fundadamente** y debe dejar registro en el informe (art. 14 inc. 2° DS 21). [VERIFICADO] [2]
- Obligaciones del investigador (art. 7° DS 21): actuar con imparcialidad, objetividad, diligencia y perspectiva de género; cumplir plazos; citar a declarar a todas las personas involucradas con registro escrito; guardar estricta reserva salvo requerimiento de Tribunales. [VERIFICADO] [2]

### 6.5 Investigación (art. 211-C incs. 2° y 3° CT; arts. 15-17 DS 21)

- **Plazo: 30 días** — "En cualquier caso, la investigación deberá concluirse en el plazo de treinta días" (art. 211-C inc. 2° CT). El art. 17 DS 21 precisa el punto de partida: **"contados desde la presentación de la denuncia o desde la fecha de recepción de la derivación por el empleador a la Dirección del Trabajo"**, y añade: "Para efectos del cómputo del plazo, en caso de derivación, la Dirección del Trabajo deberá emitir un certificado de recepción". [VERIFICADO] [1][2]
- Forma: "deberá constar por escrito, ser llevada en estricta reserva y garantizar que ambas partes sean oídas y puedan fundamentar sus dichos" (art. 211-C inc. 3° CT). [VERIFICADO] [1]
- **Denuncias inconsistentes** (incoherentes o incompletas): el investigador "proporcionará a la persona denunciante un **plazo razonable** a fin de completar los antecedentes" (art. 15 inc. 2° DS 21) — plazo abierto, no numérico. [VERIFICADO] [2]
- Antecedentes que deben considerarse especialmente (art. 15 inc. 3° DS 21): protocolo de prevención; reglamento interno; contratos de trabajo y anexos; registros de asistencia; DIEP/DIAT; Protocolo de Vigilancia de Riesgos Psicosociales en el Trabajo; **resultados del cuestionario CEAL-SM de la SUSESO**. [VERIFICADO] [2]
- Registro: escrito, en papel o electrónico; las declaraciones "deberán siempre constar en papel y con firma de quienes comparecen **en todas sus hojas**" (art. 15 inc. final DS 21). [VERIFICADO] [2]
- Contenido mínimo del informe (art. 16 DS 21, literales a-i): datos de la empresa; individualización de denunciante, denunciada e investigador; medidas de resguardo adoptadas y notificaciones; antecedentes y entrevistas; relación de hechos y alegaciones; **indicios o razonamientos coherentes y congruentes** que fundan las conclusiones; propuesta de medidas correctivas; propuesta de sanciones. [VERIFICADO] [2]
- Violencia de terceros: "las conclusiones contendrán las **medidas correctivas** que adoptará el empleador en relación con la causa que generó la denuncia" (art. 211-C inc. 4° CT; art. 23 DS 21). [VERIFICADO] [1][2]

### 6.6 Remisión del informe a la DT y pronunciamiento (art. 211-C inc. 3° CT; art. 18 DS 21)

- **Remisión: 2 días** — "El empleador dentro del plazo de **dos días de finalizada la investigación interna** remitirá el informe y sus conclusiones **de manera electrónica** a la Dirección del Trabajo. Dicho Servicio emitirá un certificado de la recepción" (art. 18 inc. 1° DS 21). Este plazo **no está en la ley**, lo agrega el reglamento. [VERIFICADO] [2]
- **Pronunciamiento DT: 30 días** — "la cual tendrá un plazo de treinta días para pronunciarse sobre ésta" (art. 211-C inc. 3° CT). El art. 18 inc. 2° DS 21 añade que el pronunciamiento "será puesto en conocimiento del empleador, la persona afectada, denunciante y denunciada". [VERIFICADO] [1][2]
- **Silencio positivo**: "En caso de cumplirse el plazo referido y de no existir tal pronunciamiento, **se considerarán válidas las conclusiones del informe**, especialmente para efectos de adoptar medidas respecto de las personas afectadas" (art. 211-C inc. 3° CT). El reglamento agrega que en ese caso el empleador "deberá notificarlo a la persona afectada, denunciante y denunciada" (art. 18 inc. 2° DS 21). [VERIFICADO] [1][2]

### 6.7 Adopción de medidas y sanciones (art. 211-E CT; art. 19 DS 21)

- **Ley (art. 211-E inc. 1° CT):** "el empleador deberá disponer y aplicar las medidas o sanciones que correspondan, **dentro de los siguientes quince días contados desde su recepción**" (recepción del informe de investigación). [VERIFICADO] [1]
- **Reglamento (art. 19 DS 21) — más preciso y con día distinto:**
  - Caso 1 (hay pronunciamiento DT): "Notificado el empleador del pronunciamiento de la Dirección del Trabajo, deberá disponer y aplicar las medidas o sanciones que correspondan dentro de los siguientes **quince días corridos**, informando a la persona denunciante como a la denunciada."
  - Caso 2 (silencio DT): "el empleador deberá disponer y aplicar las medidas o sanciones que correspondan, según su informe de investigación, dentro de los **quince días corridos**, una vez transcurrido **treinta días** desde la remisión del informe de investigación a la Dirección del Trabajo." [VERIFICADO] [2]
- Información a las partes: las medidas o sanciones "serán informadas dentro del plazo anteriormente referido, tanto a la persona denunciante como a la denunciada" (art. 211-E inc. 2° CT). [VERIFICADO] [1]
- Sanciones: el empleador "deberá, en los casos que corresponda, aplicar las sanciones conforme a lo establecido en las **letras b) o f) del N° 1 del artículo 160**" CT (conductas de acoso sexual y acoso laboral como causal de despido sin indemnización). "Con todo, en el caso de lo dispuesto en la letra f) del N° 1 deberá evaluar la gravedad de los hechos investigados, lo que consignará en las conclusiones del informe" (art. 211-E inc. 3° CT; art. 22 DS 21). [VERIFICADO] [1][2]
- Impugnación: la persona despedida "podrá impugnar dicha decisión ante el tribunal competente. Para ello deberá rendir en juicio las pruebas necesarias para desvirtuar los hechos o antecedentes contenidos en el informe" (art. 211-E inc. 4° CT). El art. 22 inc. final DS 21 recuerda que igualmente rige el art. 162 CT (carta de despido, cotizaciones al día). [VERIFICADO] [1][2]
- Obligación adicional: "el empleador estará obligado a entregar información a la persona denunciante respecto de los **canales de denuncias de hechos que puedan constituir eventuales delitos**" (art. 211-E inc. final CT; art. 6 letra g) y art. 23 inc. 2° DS 21 remiten a Ministerio Público, Carabineros, PDI y al art. 175 del Código Procesal Penal). [VERIFICADO] [1][2]

### 6.8 Medidas correctivas (art. 21 DS 21)

Objetivo: "prevenir y controlar los riesgos identificados en los hechos que dieron lugar a la denuncia, generando **garantía de no repetición**", evaluando mejoras al protocolo conforme al art. 211-A letra b) CT. Se aplican tanto a los involucrados como al resto de la dotación (refuerzo de información y capacitación, apoyo psicológico, reiteración de canales de denuncia). Si el protocolo se modifica, debe informarse a todas las personas trabajadoras (arts. 211-A inc. 2°, 154 N° 12 y 154 bis CT). [VERIFICADO] [2]

### 6.9 Subcontratación y servicios transitorios (art. 24 DS 21)

- Empresa principal/usuaria que recibe denuncia de trabajador de otro empleador: debe informar las instancias del art. 211-B bis CT y, conocida la decisión del trabajador, **remitir la denuncia en el plazo de tres días** a la instancia que sustanciará el procedimiento. [VERIFICADO] [2]
- Si los hechos involucran a trabajadores de distintas empresas: la persona puede denunciar ante la principal/usuaria, ante su empleador o ante la DT. Si denuncia ante su empleador, éste "deberá informar de ella a la empresa principal o usuaria, **dentro de los tres días** desde su recepción". **"La empresa principal o usuaria será siempre la responsable de realizar la investigación"**; cada empleador adopta medidas de resguardo y sanciones respecto de sus propios dependientes. [VERIFICADO] [2]

### 6.10 Confidencialidad y no represalias

- **Confidencialidad**: principio legal (art. 211-B inc. 1° CT) y principio reglamentario (art. 2° letra d) DS 21): "deber de los participantes de resguardar el acceso y divulgación de la información a la que accedan o conozcan en el proceso". Se vincula con el **art. 154 ter CT** (deber de reserva del empleador sobre datos privados de los trabajadores). Excepción: "la información podrá ser requerida por los Tribunales de Justicia o la Dirección del Trabajo en el ejercicio de sus funciones". La investigación interna debe ser "llevada en estricta reserva" (art. 211-C inc. 3° CT). [VERIFICADO] [1][2]
- **No revictimización** (art. 2° letra c) DS 21): evitar que la persona afectada "se vea expuesta a la continuidad de la lesión o vulneración sufrida como consecuencia de la conducta denunciada". [VERIFICADO] [2]
- **No represalias**: la Ley 21.643 **no contiene una cláusula expresa** de prohibición de represalias con esa denominación. La protección se articula por tres vías: (i) art. 211-A letra e) CT — medidas "destinadas a resguardar la debida actuación de las trabajadoras y de los trabajadores, **independiente del resultado de la investigación**"; (ii) art. 20 inc. 3° DS 21 — las medidas de resguardo no pueden ser "gravosas o perjudiciales para la persona denunciante, ni producir algún tipo de menoscabo"; (iii) art. 211-D inc. final CT — si la DT toma conocimiento de una **vulneración de derechos fundamentales** debe dar cumplimiento al art. 486 CT (**procedimiento de tutela laboral**), con excepción del inciso sexto (mediación previa) respecto del acoso sexual. [VERIFICADO en cuanto a los textos; la calificación "no hay cláusula expresa de represalias" es una lectura del texto — ver Pendientes.]

## 7. Gestión de riesgos psicosociales y organismo administrador Ley 16.744 (SUSESO)

| Norma | Fecha | Contenido | Etiqueta |
|---|---|---|---|
| **Circular N° 3.813 SUSESO** | 07-06-2024 | Imparte instrucciones a los organismos administradores de la Ley 16.744 y a las empresas con administración delegada sobre la asistencia técnica para la prevención del acoso sexual, laboral y violencia en el trabajo (Ley 21.643). Modifica los **Libros III, IV y V del Compendio de Normas del Seguro de la Ley 16.744**. Fundamento: Ley 16.395 arts. 2, 3, 30 y 38; Ley 16.744 arts. 12 y 72. Vigencia: desde su publicación. | [VERIFICADO] [5] |
| **Circular N° 3.819 SUSESO** | 26-07-2024 | Instrucciones complementarias sobre la misma materia | [VERIFICADO] [5] |
| **Circular N° 3.825 SUSESO** | 19-08-2024 | Instrucciones complementarias sobre la misma materia | [VERIFICADO] [5] |

Contenido del Compendio SUSESO, Libro IV, "Capítulo I. Elaboración e implementación del protocolo de prevención del acoso sexual, laboral y la violencia en el trabajo" [6]:

- Alcance: **todas las entidades empleadoras, del sector público y privado**, incluidas municipalidades, organismos públicos e instituciones de educación superior. [VERIFICADO] [6]
- El protocolo debe contener una política de prevención, los contenidos mínimos legales y **participación de trabajadores** (organizaciones sindicales y comités paritarios). [VERIFICADO] [6]
- **Identificación de riesgos psicosociales**: usar el *Protocolo de Vigilancia de Riesgos Psicosociales en el Trabajo* del MINSAL y aplicar el **cuestionario CEAL-SM/SUSESO**, analizando específicamente las **7 preguntas de la dimensión "violencia y acoso"** (que identifican situaciones ocurridas en los últimos 12 meses). [VERIFICADO] [6]
- **Diferencia por tamaño de empresa (la única explícita y relevante):** las empresas de **menos de 10 trabajadores NO están obligadas a aplicar el CEAL-SM**; pueden usar la *"Pauta sugerida para la evaluación de riesgos psicosociales"* (**Anexo N° 54** del Compendio). [VERIFICADO] [6]
- Medidas de prevención: objetivos medibles y controlables, plazos de análisis periódicos, mejora continua, capacitación periódica. Los procesos "deberán ser revisados permanentemente". La **periodicidad exacta de reevaluación** del riesgo psicosocial no queda fijada en la fuente consultada. [NO VERIFICADO — ver Pendientes]
- Capacitación y difusión: reconocimiento de conductas de acoso, efectos en salud y situaciones que **no** constituyen violencia laboral; publicación en medios disponibles (web u otros). [VERIFICADO] [6]

**Reporte estadístico (art. 6 Ley 21.643):** los organismos administradores deben remitir **semestralmente** a la SUSESO la cantidad de denuncias presentadas y las acciones/medidas adoptadas; los empleadores deben proporcionar esa información. La SUSESO remite al MINTRAB y al Consejo Superior Laboral, **en enero y julio de cada año**, un informe estadístico consolidado. [VERIFICADO] [1]

## 8. Sanciones, fiscalización y recursos oficiales

### 8.1 Multas

La Ley 21.643 **no creó un régimen sancionatorio propio**. Se aplica el régimen general del **artículo 506 del Código del Trabajo**: *"Las infracciones a este Código y sus leyes complementarias, que no tengan señalada una sanción especial, serán sancionadas de conformidad a lo dispuesto en los incisos siguientes, **según la gravedad de la infracción**."* [VERIFICADO contra el texto vigente en BCN] [27]

| Tamaño de empresa (art. 505 bis CT) | N° de trabajadores | Multa (art. 506 CT) |
|---|---|---|
| Micro empresa | 1 a 9 | **1 a 5 UTM** |
| Pequeña empresa | 10 a 49 | **1 a 10 UTM** |
| Mediana empresa | 50 a 199 | **2 a 40 UTM** |
| Gran empresa | 200 o más | **3 a 60 UTM** |

> **Corrección importante:** muchas guías comerciales agrupan "micro y pequeña: 1 a 10 UTM". El texto vigente del art. 506 CT **distingue** micro (1 a 5 UTM) de pequeña (1 a 10 UTM). Verificado literalmente. [VERIFICADO] [27]

Texto literal del art. 505 bis CT: *"se entenderá por micro empresa aquella que tuviere contratados de 1 a 9 trabajadores, pequeña empresa aquella que tuviere contratados de 10 a 49 trabajadores, mediana empresa aquella que tuviere contratados de 50 a 199 trabajadores y gran empresa aquella que tuviere contratados 200 trabajadores o más."* [VERIFICADO] [27]

**Sustitución de la multa (art. 506 ter CT):** tratándose de **micro y pequeñas empresas** que no hayan reclamado (arts. 503 y 511 CT), el inspector puede autorizar, a solicitud del sancionado y **sólo una vez al año respecto de la misma infracción**, sustituir la multa por (1) incorporación a un programa de asistencia al cumplimiento con asistencia técnica del organismo administrador de la Ley 16.744 (si la multa es por higiene y seguridad), o (2) asistencia obligatoria a programas de capacitación de la DT de hasta dos semanas. **La solicitud debe presentarse dentro del plazo de treinta días de notificada la resolución de multa administrativa.** [VERIFICADO] [27]

La Dirección del Trabajo incorporó las infracciones a la Ley 21.643 a su **tipificador de infracciones**, graduando la multa según gravedad y número de trabajadores afectados. [SECUNDARIO] [7]

### 8.2 Fiscalización

- Órgano fiscalizador: **Dirección del Trabajo / Inspección del Trabajo** (sector privado). Facultades fiscalizadoras reiteradas en el dictamen ORD.N°57/04 (26-01-2026): "sin perjuicio de las facultades fiscalizadoras de este Servicio". [VERIFICADO] [11]
- La revisión del informe por la Inspección **no genera presunción legal** respecto de los hechos investigados (art. 23 del DFL N° 2 de 1967 reserva la presunción a hechos constatados directamente por Inspectores). Dictamen 362/19, citado en ORD.N°57/04. [VERIFICADO] [11]
- La Inspección sólo verifica **cumplimiento procedimental y congruencia** entre informe y conclusiones; no emite pronunciamiento de fondo. [VERIFICADO] [11]
- **SUSESO** fiscaliza a los organismos administradores; **Contraloría General de la República** en el sector público.

### 8.3 Recursos oficiales

| Recurso | Ubicación | Etiqueta |
|---|---|---|
| Portal Ley Karin de la Dirección del Trabajo (modelo de protocolo, guías, preguntas frecuentes) | https://www.dt.gob.cl | [NO VERIFICADO — URL exacta de la sección Ley Karin no confirmada en esta pasada] |
| Dictámenes y normativa DT (buscador "Normativa 3.0") | https://www.dt.gob.cl/legislacion/1624/w3-propertyvalue-194488.html (índice "Ley Karin") | [VERIFICADO] [12] |
| Plataforma electrónica de denuncias de la DT (exigida por el art. 2° transitorio DS 21, plazo 03-07-2025) | — | [NO VERIFICADO — no se confirmó la URL ni la fecha efectiva de implementación] |
| Reporte estadístico semestral de la DT (art. 26 DS 21) | Sitio web DT | [NO VERIFICADO — URL exacta] |
| Compendio de Normas del Seguro de la Ley 16.744, SUSESO (Libro IV, Cap. I) | https://www.suseso.gob.cl/613/w3-propertyvalue-726761.html | [VERIFICADO] [6] |
| Cuestionario CEAL-SM/SUSESO y Anexo N° 54 (pauta para <10 trabajadores) | Compendio SUSESO | [VERIFICADO] [6] |

## 9. Sector público: diferencias principales (breve)

| Aspecto | Sector privado | Sector público |
|---|---|---|
| Norma base | Código del Trabajo, Título IV Libro II | Ley 18.575 (art. 14 nuevo), Ley 18.834 (Estatuto Administrativo), Ley 18.883 (Estatuto Municipal) |
| Instrumento de prevención | Protocolo art. 211-A CT (vía organismo administrador Ley 16.744) | Protocolo del **art. 14 de la Ley 18.575**, con contenido mínimo casi idéntico (letras a-e) pero con "enfoque inclusivo e integrado con perspectiva de género"; asistencia de organismos Ley 16.744 "en los casos que correspondan" |
| Procedimiento | Investigación interna del empleador o de la DT | **Sumario administrativo / investigación sumaria** (arts. 90 A y 90 B Ley 18.834), sujetos a los principios de confidencialidad, imparcialidad, celeridad y perspectiva de género (arts. 46 Ley 18.575, 119 Ley 18.834, 118 Ley 18.883) |
| Órgano de control | Dirección del Trabajo | **Contraloría General de la República** |
| Fiscal/investigador | Trabajador con formación en acoso, género o DDFF (preferentemente) | Fiscal con formación en prevención, investigación y sanción de acoso, género o DDFF (preferentemente) — art. 129 Ley 18.834 / art. 127 Ley 18.883 |
| Plazos propios | 3 / 30 / 2 / 30 / 15 días | **5 días** para notificar a la persona denunciante la resolución que desestima, sobresee, absuelve o aplica medida (arts. 126, 137 y 140 Ley 18.834; 124, 135 y 138 Ley 18.883); **20 días** para reclamar ante la CGR desde que tomó conocimiento; **20 días** para adoptar las medidas desde el vencimiento de los plazos de instrucción (art. 143 Ley 18.834 / art. 141 Ley 18.883); **3 días hábiles** para poner en conocimiento de la CGR cuando el denunciado o denunciante sea alcalde/alcaldesa, concejal o jefatura de dependencia directa del alcalde (art. 126 Ley 18.883) |
| Derechos de la víctima | Ser oída, aportar antecedentes | Aportar antecedentes, **conocer el contenido desde la formulación de cargos**, ser notificada e interponer recursos "en los mismos términos que el funcionario inculpado" (art. 129 Ley 18.834 / art. 127 Ley 18.883) |
| Sanción máxima | Despido art. 160 N°1 letras b) o f) CT | **Destitución**; el acoso pasa a ser prohibición funcionaria (art. 62 N° 10 Ley 18.575) y causal de destitución (art. 125 letra b) Ley 18.834) |
| Municipal | — | El alcalde declarado responsable incurre en **contravención grave a la probidad** → causal de cesación en el cargo (arts. 60, 76 g) y 77 Ley 18.695) |

Todos los datos de esta tabla provienen del texto de los artículos 2 a 5 de la Ley 21.643. [VERIFICADO] [1]

> La DT **no es competente** cuando la persona denunciante es funcionaria pública; corresponde consultar a la Contraloría General de la República (ORD.N°57/04, conclusión 8). [VERIFICADO] [11]
>
> La Contraloría impartió instrucciones sobre estas modificaciones mediante el **Dictamen N° E516610 de 19-07-2024**, aclarado posteriormente (folio E30538/2025). [SECUNDARIO — no verificado directamente en contraloria.cl]

## 10. Feriados legales de Chile

### 10.1 Marco normativo de los feriados (leyes base)

| Ley | Publicación | Qué establece (literal o sumario) | Etiqueta |
|---|---|---|---|
| **Ley 2.977** | 01-02-1915 | "FIJA LOS DIAS FERIADOS". Art. 1°: domingos; 1° de enero, 29 de junio, 15 de agosto, 1° de noviembre, 8 y 25 de diciembre y las fiestas movibles de la Ascensión y Corpus Christi; **Viernes y Sábado de Semana Santa**; 18 de septiembre; 19 de septiembre y 21 de mayo; y "el día que deba tener lugar la elección de electores de Presidente de la República". Nota BCN: el art. 144 de la Ley 16.840 suprimió el 29 de junio, la Ascensión y Corpus Christi (el 29 de junio fue luego repuesto). | [VERIFICADO] [17] |
| **Ley 19.668** | 10-03-2000 | Artículo único: "Trasládanse los feriados correspondientes al 29 de junio, día de San Pedro y San Pablo; 12 de octubre, día del descubrimiento de dos mundos; y el día de la fiesta Corpus Christi, **a los días lunes de la semana en que ocurren, en caso de corresponder a día martes, miércoles o jueves, o los días lunes de la semana siguiente, en caso de corresponder a día viernes**." | [VERIFICADO — texto citado por fuente secundaria que reproduce el artículo único; ver Pendientes] [18] |
| **Ley 19.973** | 10-09-2004 (últ. mod. 30-05-2016, Ley 20.918) | Art. 2°: "Los días **1 de mayo, 18 y 19 de septiembre, 25 de diciembre y 1 de enero** de cada año, serán feriados obligatorios e irrenunciables **para todos los dependientes del comercio**", con excepciones (clubes, restaurantes, cines, espectáculos, discotecas, pub, cabarets, locales en aeropuertos, casinos, expendio de combustibles, farmacias de urgencia y de turno, tiendas de conveniencia con elaboración de alimentos). Multa: 5 UTM por trabajador afectado; 10 UTM si el empleador tiene 50 o más trabajadores; 20 UTM si tiene 200 o más. Art. 3°: extiende el feriado del art. 169 de la Ley 18.700 a los trabajadores de centros o complejos comerciales. | [VERIFICADO] [19] |
| **Ley 20.148** | 06-01-2007 | "DECLARA FERIADO EL DIA 16 DE JULIO DE CADA AÑO EN QUE SE CELEBRA Y HONRA A LA VIRGEN DEL CARMEN EN REEMPLAZO DEL FERIADO CORRESPONDIENTE A CORPUS CHRISTI" | [VERIFICADO — título según el índice temático oficial de BCN; texto íntegro no leído] [20] |
| **Ley 20.299** | 11-10-2008 | Art. 1°: "Declárase feriado el día 31 de octubre, por conmemorarse el Día Nacional de las Iglesias Evangélicas y Protestantes." Art. 2°: "**Trasládase el feriado (…) al día viernes de la misma semana en caso de corresponder el 31 de octubre a día miércoles, y trasládase al día viernes de la semana inmediatamente anterior en caso de corresponder dicha fecha a día martes.**" | [VERIFICADO] [21] |
| **Ley 20.983** | 30-12-2016 | Artículo único: "Declárase feriado el día **viernes 17 de septiembre**, cada vez que el 18 y el 19 de septiembre de aquel año coincidan con sábado y domingo, respectivamente. Del mismo modo, **al recaer el 1 de enero en día domingo, el lunes 2 siguiente será feriado**." | [VERIFICADO] [22] |
| **Ley 21.357** | 19-06-2021 | Artículo único: "Declárase feriado legal el día del **solsticio de invierno** de cada año en el hemisferio sur, **Día Nacional de los Pueblos Indígenas**." (Art. transitorio: excepcionalmente, para 2021, el 21 de junio.) | [SECUNDARIO — texto citado por fuentes secundarias; no leído directamente en BCN en esta pasada] [23] |
| **Ley 18.700, art. 169** | — | "El día que se fije para la realización de las elecciones y plebiscitos será feriado legal. Los plebiscitos comunales se efectuarán en día domingo." | [SECUNDARIO — citado por la DT; texto no leído directamente en BCN] [24] |
| **Ley 21.791** | dic-2025 | Repone a nivel legal el **feriado bancario de fin de año** (31 de diciembre) y las normas del feriado bancario sabatino. | [SECUNDARIO] [25] |

Feriados regionales/comunales vigentes: **7 de junio** (Asalto y Toma del Morro de Arica — solo Región de Arica y Parinacota) y **20 de agosto** (Nacimiento del Prócer de la Independencia — solo comunas de Chillán y Chillán Viejo). [SECUNDARIO] [25]

### 10.2 Feriados 2025 (nacionales, salvo indicación)

| Fecha | Día | Nombre | Ley | Irrenunciable |
|---|---|---|---|---|
| 01-01-2025 | miércoles | Año Nuevo | 2.977 | **Sí** (19.973) |
| 18-04-2025 | viernes | Viernes Santo (móvil) | 2.977 | No |
| 19-04-2025 | sábado | Sábado Santo (móvil) | 2.977 | No |
| 01-05-2025 | jueves | Día Nacional del Trabajo | Cód. del Trabajo / 19.973 | **Sí** (19.973) |
| 21-05-2025 | miércoles | Día de las Glorias Navales | 2.977 | No |
| 07-06-2025 | sábado | Asalto y Toma del Morro de Arica *(solo Arica y Parinacota)* | 20.663 | No |
| 20-06-2025 | viernes | Día Nacional de los Pueblos Indígenas (solsticio) | 21.357 | No |
| 29-06-2025 | domingo | San Pedro y San Pablo (no se traslada: cae domingo) | 2.977 / 19.668 | No |
| 16-07-2025 | miércoles | Virgen del Carmen | 20.148 | No |
| 15-08-2025 | viernes | Asunción de la Virgen | 2.977 | No |
| 20-08-2025 | miércoles | Nacimiento del Prócer *(solo Chillán y Chillán Viejo)* | 20.768 | No |
| 18-09-2025 | jueves | Independencia Nacional | 2.977 | **Sí** (19.973) |
| 19-09-2025 | viernes | Día de las Glorias del Ejército | 2.977 | **Sí** (19.973) |
| 12-10-2025 | domingo | Encuentro de Dos Mundos (no se traslada: cae domingo) | 3.810 / 19.668 | No |
| 31-10-2025 | viernes | Día Nacional de las Iglesias Evangélicas y Protestantes (no se traslada: cae viernes) | 20.299 | No |
| 01-11-2025 | sábado | Día de Todos los Santos | 2.977 | No |
| 16-11-2025 | domingo | **Elección presidencial y parlamentaria (1ª vuelta)** | 18.700 art. 169 | Sí para centros comerciales (19.973 art. 3°) |
| 08-12-2025 | lunes | Inmaculada Concepción | 2.977 | No |
| 14-12-2025 | domingo | **Elección presidencial (2ª vuelta)** | 18.700 art. 169 | Sí para centros comerciales |
| 25-12-2025 | jueves | Navidad | 2.977 | **Sí** (19.973) |
| *31-12-2025* | *miércoles* | *Feriado **bancario** de fin de año (NO es feriado general)* | 21.791 | No |

Los números de ley de los feriados regionales (20.663 Arica; 20.768 Chillán) y del 12 de octubre (3.810) son **[NO VERIFICADO]** — ver Pendientes. Las fechas y días de semana fueron verificados por cálculo. [VERIFICADO el día de la semana]

### 10.3 Feriados 2026

| Fecha | Día | Nombre | Regla / Ley | Irrenunciable |
|---|---|---|---|---|
| 01-01-2026 | jueves | Año Nuevo | 2.977 | **Sí** |
| 03-04-2026 | viernes | Viernes Santo (Pascua = 05-04-2026) | 2.977 | No |
| 04-04-2026 | sábado | Sábado Santo | 2.977 | No |
| 01-05-2026 | viernes | Día Nacional del Trabajo | 19.973 | **Sí** |
| 21-05-2026 | jueves | Día de las Glorias Navales | 2.977 | No |
| 07-06-2026 | domingo | Morro de Arica *(regional)* | — | No |
| 21-06-2026 | domingo | Día Nacional de los Pueblos Indígenas (solsticio) | 21.357 | No |
| 29-06-2026 | **lunes** | San Pedro y San Pablo (ya cae lunes: no hay traslado) | 19.668 | No |
| 16-07-2026 | jueves | Virgen del Carmen | 20.148 | No |
| 15-08-2026 | sábado | Asunción de la Virgen | 2.977 | No |
| 20-08-2026 | jueves | Nacimiento del Prócer *(Chillán)* | — | No |
| 18-09-2026 | viernes | Independencia Nacional | 2.977 | **Sí** |
| 19-09-2026 | sábado | Glorias del Ejército | 2.977 | **Sí** |
| 12-10-2026 | **lunes** | Encuentro de Dos Mundos (ya cae lunes) | 19.668 | No |
| 31-10-2026 | sábado | Iglesias Evangélicas (cae sábado: no se traslada) | 20.299 | No |
| 01-11-2026 | domingo | Todos los Santos | 2.977 | No |
| 08-12-2026 | martes | Inmaculada Concepción | 2.977 | No |
| 25-12-2026 | viernes | Navidad | 2.977 | **Sí** |
| *31-12-2026* | *jueves* | *Feriado **bancario** de fin de año* | 21.791 | No |

**No hay elecciones en 2026** (pausa electoral: las siguientes son primarias regionales/municipales el 09-07-2028 y elecciones regionales y municipales el 29-10-2028). [SECUNDARIO] [26]

### 10.4 Feriados 2027

| Fecha | Día | Nombre | Regla / Ley | Irrenunciable |
|---|---|---|---|---|
| 01-01-2027 | viernes | Año Nuevo | 2.977 | **Sí** |
| 26-03-2027 | viernes | Viernes Santo (Pascua = 28-03-2027) | 2.977 | No |
| 27-03-2027 | sábado | Sábado Santo | 2.977 | No |
| 01-05-2027 | sábado | Día Nacional del Trabajo | 19.973 | **Sí** |
| 21-05-2027 | viernes | Glorias Navales | 2.977 | No |
| 07-06-2027 | lunes | Morro de Arica *(regional)* | — | No |
| 21-06-2027 | lunes | Pueblos Indígenas (solsticio) | 21.357 | No |
| **28-06-2027** | **lunes** | San Pedro y San Pablo — **TRASLADADO** (29-06-2027 cae martes → lunes de la misma semana) | 19.668 | No |
| 16-07-2027 | viernes | Virgen del Carmen | 20.148 | No |
| 15-08-2027 | domingo | Asunción de la Virgen | 2.977 | No |
| 20-08-2027 | viernes | Nacimiento del Prócer *(Chillán)* | — | No |
| **17-09-2027** | **viernes** | **"San Viernes"** — feriado adicional porque el 18 y 19 caen sábado y domingo | 20.983 | No |
| 18-09-2027 | sábado | Independencia Nacional | 2.977 | **Sí** |
| 19-09-2027 | domingo | Glorias del Ejército | 2.977 | **Sí** |
| **11-10-2027** | **lunes** | Encuentro de Dos Mundos — **TRASLADADO** (12-10-2027 cae martes → lunes de la misma semana) | 19.668 | No |
| 31-10-2027 | domingo | Iglesias Evangélicas (cae domingo: no se traslada) | 20.299 | No |
| 01-11-2027 | lunes | Todos los Santos | 2.977 | No |
| 08-12-2027 | miércoles | Inmaculada Concepción | 2.977 | No |
| 25-12-2027 | sábado | Navidad | 2.977 | **Sí** |
| *31-12-2027* | *viernes* | *Feriado **bancario** de fin de año* | 21.791 | No |

**No hay elecciones en 2027.** [SECUNDARIO] [26]

Fuente del calendario 2026-2027: [25] (secundaria, exhaustiva y con citas legales). **Todos los días de la semana y las fechas móviles (Pascua, traslados, San Viernes) fueron recalculados y verificados algorítmicamente en esta investigación.**

### 10.5 Reglas para calcular años futuros (motor Python)

1. **Fijos todos los años:** 01-01, 01-05, 21-05, 29-06 (trasladable), 16-07, 15-08, 18-09, 19-09, 12-10 (trasladable), 31-10 (trasladable), 01-11, 08-12, 25-12. Más todos los domingos.
2. **Móviles pascuales:** Viernes Santo = Domingo de Pascua − 2 días; Sábado Santo = Pascua − 1 día. Pascua se calcula con el algoritmo gregoriano de Gauss/Meeus.
3. **Traslado Ley 19.668** (aplica a **29 de junio** y **12 de octubre**):
   - cae **martes, miércoles o jueves** → se traslada al **lunes de esa misma semana** (retrocede 1, 2 o 3 días);
   - cae **viernes** → se traslada al **lunes de la semana siguiente** (avanza 3 días);
   - cae **sábado, domingo o lunes** → **no se traslada**.
4. **Traslado Ley 20.299** (31 de octubre, Iglesias Evangélicas):
   - cae **martes** → se traslada al **viernes de la semana inmediatamente anterior** = 31-10 **menos 4 días** (27 de octubre). Ejemplo histórico: 2023 (31-10 martes → feriado el viernes 27-10-2023).
   - cae **miércoles** → se traslada al **viernes de la misma semana** = 31-10 **más 2 días** (2 de noviembre). Ejemplo histórico: 2018 (31-10 miércoles → feriado el viernes 02-11-2018).
   - cualquier otro día de la semana → **no se traslada**.
   > Los dos ejemplos históricos son [SECUNDARIO]; la regla en sí es [VERIFICADO] contra el texto del art. 2° de la Ley 20.299.
5. **Ley 20.983 (condicionales):**
   - Si el **18-09 cae sábado** (y por tanto el 19 domingo) → el **viernes 17-09** es feriado;
   - Si el **01-01 cae domingo** → el **lunes 02-01** es feriado.
6. **Ley 21.357 (variable):** Día Nacional de los Pueblos Indígenas = **fecha del solsticio de invierno austral en hora de Chile continental**. Cae el 20 o el 21 de junio según el año. Requiere una tabla astronómica o una librería de efemérides; **no basta con fijar el 21 de junio**. (2025 → 20-jun; 2026 → 21-jun; 2027 → 21-jun.)
7. **Elecciones y plebiscitos (Ley 18.700 art. 169):** son feriado legal el día que se fije. No son predecibles por regla: deben cargarse manualmente desde el calendario del SERVEL.
8. **Feriados regionales/comunales:** 07-06 (Arica y Parinacota) y 20-08 (Chillán y Chillán Viejo). Deben modelarse con ámbito territorial, no nacional.
9. **No confundir:** el **feriado bancario** (todos los sábados y el 31 de diciembre) **no es feriado de ámbito general** y no debe usarse para contar días hábiles laborales/administrativos. El sábado es inhábil para la Ley Karin por el art. 1° del DS 21, no por ser feriado.

## Tabla de plazos

Leyenda del tipo de día: **H** = días hábiles (se excluyen sábados, domingos y festivos, art. 1° inc. 2° DS 21); **C** = días corridos; **INM** = inmediato, sin plazo numérico.

| # | Hito | Plazo | Tipo | Desde cuándo se cuenta | Artículo | Etiqueta |
|---|---|---|---|---|---|---|
| 1 | Adopción de medidas de resguardo por el empleador | INM ("de manera inmediata") | — | Recepción de la denuncia | Art. 211-B bis inc. 2° CT; art. 13 DS 21 | [VERIFICADO] |
| 2 | La Inspección del Trabajo solicita al empleador medidas de resguardo (denuncia hecha ante la IT) | **2** | H | Recepción de la denuncia por la IT | Art. 211-B bis inc. 3° CT; art. 20 inc. 1° DS 21 | [VERIFICADO] |
| 3 | Notificación electrónica del art. 508 CT: se entiende notificado | **3** | H | Emisión del correo electrónico registrado en la DT | Art. 20 inc. 1° DS 21 | [VERIFICADO] |
| 4 | Notificación por carta certificada: se entiende notificado | **6** | H | Recepción por la oficina de correos | Art. 20 inc. 1° DS 21 | [VERIFICADO] |
| 5 | Empleador informa a la DT el inicio de la investigación interna + medidas de resguardo **o** deriva la denuncia | **3** | H | Recepción de la denuncia | Art. 211-C inc. 1° CT; art. 12 inc. 4° DS 21 | [VERIFICADO] |
| 6 | Subcontratación/servicios transitorios: remitir la denuncia a quien debe investigar / informar a la empresa principal | **3** | H | Recepción de la denuncia | Art. 24 DS 21 | [VERIFICADO] |
| 7 | **Conclusión de la investigación** | **30** | H | Presentación de la denuncia; o recepción de la derivación por quien debe investigar (DT o empresa principal) | Art. 211-C inc. 2° CT; art. 17 DS 21; ORD.N°57/04 N°5 | [VERIFICADO] |
| 8 | Denuncia incompleta o incoherente: plazo para completarla | "plazo razonable" (sin número) | — | Requerimiento del investigador | Art. 15 inc. 2° DS 21; ORD.N°146/13 N°1 | [VERIFICADO] |
| 9 | Remisión del informe y conclusiones a la DT (vía electrónica) | **2** | H | Finalización de la investigación interna | Art. 18 inc. 1° DS 21 | [VERIFICADO] |
| 10 | **Pronunciamiento de la Dirección del Trabajo** sobre el informe | **30** | H | Recepción del informe por la DT (certificado de recepción) | Art. 211-C inc. 3° CT; art. 18 inc. 2° DS 21 | [VERIFICADO] |
| 11 | Silencio de la DT → conclusiones del informe se consideran válidas | al vencer el plazo 10 | H | — | Art. 211-C inc. 3° CT | [VERIFICADO] |
| 12a | Aplicación de medidas o sanciones — **con** pronunciamiento de la DT | **15** | **C (corridos)** | Notificación del pronunciamiento de la DT | Art. 19 inc. 1° DS 21 | [VERIFICADO] |
| 12b | Aplicación de medidas o sanciones — **sin** pronunciamiento de la DT | **15** | **C (corridos)** | Vencimiento de los 30 días desde la remisión del informe a la DT | Art. 19 inc. 2° DS 21 | [VERIFICADO] |
| 12c | (Texto legal, menos preciso) Aplicación de medidas o sanciones | **15** | no especificado en la ley | "desde su recepción" (del informe) | Art. 211-E inc. 1° CT | [VERIFICADO] |
| 13 | Información de las medidas/sanciones al denunciante y al denunciado | dentro del mismo plazo 12 | C | — | Art. 211-E inc. 2° CT; art. 19 DS 21 | [VERIFICADO] |
| 14 | Información semestral de canales de denuncia | **semestral** | — | — | Art. 211-A inc. 4° CT; art. 6 letra c) DS 21 | [VERIFICADO] |
| 15 | Reporte de organismos administradores a la SUSESO | **semestral** | — | — | Art. 6 Ley 21.643 (agregado por Ley 21.724) | [VERIFICADO] |
| 16 | Informe estadístico consolidado SUSESO → MINTRAB y Consejo Superior Laboral | **enero y julio** de cada año | — | — | Art. 6 inc. 3° Ley 21.643 | [VERIFICADO] |
| 17 | Reporte estadístico web de la DT | **semestral** | — | — | Art. 26 DS 21 | [VERIFICADO] |
| — | *Sector público:* notificar a la persona denunciante la resolución que desestima / sobresee / absuelve / sanciona | **5** | días (tipo no especificado) | Dictación del acto | Arts. 126, 137 y 140 Ley 18.834; arts. 124, 135 y 138 Ley 18.883 | [VERIFICADO el número; tipo de día NO VERIFICADO] |
| — | *Sector público:* reclamo ante la Contraloría General de la República | **20** | días (tipo no especificado) | Desde que tomó conocimiento de la resolución | Arts. 137 y 140 Ley 18.834; arts. 135 y 138 Ley 18.883 | [VERIFICADO el número] |
| — | *Sector público:* adopción de medidas disciplinarias | **20** | días (tipo no especificado) | Vencimiento de los plazos de instrucción | Art. 143 Ley 18.834; art. 141 Ley 18.883 | [VERIFICADO el número] |
| — | *Municipal:* poner en conocimiento de la CGR cuando el involucrado es alcalde/concejal/jefatura directa | **3** | **hábiles** (la ley lo dice expresamente) | — | Art. 126 Ley 18.883 | [VERIFICADO] |

> **Alerta para el motor**: los hitos 12a y 12b son los ÚNICOS plazos **en días corridos** del procedimiento Ley Karin. Todo lo demás es en días hábiles. Varias guías comerciales dicen erróneamente "15 días hábiles"; el art. 19 del DS 21 dice literalmente "quince días corridos".

## Cómo contar días hábiles

### Reglas

1. **Regla base (Ley Karin):** art. 1° inciso 2° del DS N°21/2024: *"Salvo disposición en contrario, los plazos contemplados en el presente reglamento serán de días hábiles, entendiéndose que son inhábiles los días **sábados, domingos y festivos**, a menos que expresamente en este reglamento se establezca de otra forma."* [VERIFICADO] [2]
2. **Confirmación por dictamen:** DT ORD.N°386/10, de 03-06-2025, conclusión 2: *"Los plazos establecidos para llevar a cabo los procedimientos de acoso sexual, laboral y violencia ejercida por terceros ajenos a la relación laboral, serán de días hábiles, entendiéndose que son inhábiles los días sábados, domingos y festivos, conforme a lo dispuesto en el artículo 1° del Reglamento contenido en el Decreto N°21 de 2024."* [VERIFICADO] [10]
3. **Calificación como "hábiles administrativos":** DT ORD.N°57/04, de 26-01-2026, conclusión 1: *"El plazo establecido para llevar a cabo la investigación (…) es de **30 días hábiles administrativos**, conforme a lo dispuesto en el artículo 1° del Reglamento."* [VERIFICADO] [11]
4. **NO se suspenden:** DT ORD.N°386/10, conclusión 1: *"La investigación (…) **no se suspende por el uso del feriado legal o la existencia de una licencia médica** de alguna de las personas involucradas en el procedimiento."* [VERIFICADO] [10]
5. **Excepción:** art. 19 del DS 21 dice expresamente "quince días **corridos**" → ahí se cuentan todos los días del calendario, incluidos sábados, domingos y festivos.
6. **Día inicial:** el reglamento no lo define. Al calificarse como plazo "hábil administrativo", la regla supletoria es el **art. 25 de la Ley 19.880**, que computa los plazos **desde el día siguiente** al de la notificación o del acto. Este documento asume esa regla. [NO VERIFICADO — el DS 21 no lo dice expresamente y no se encontró dictamen que lo resuelva de forma directa. Ver Pendientes.]
7. **Feriados a usar:** los feriados nacionales de la sección 10, más los feriados regionales/comunales cuando el establecimiento esté en el territorio respectivo. **No** usar los feriados bancarios (sábados y 31 de diciembre) como festivos generales: los sábados ya son inhábiles por la regla 1, y el 31 de diciembre **no** es festivo para estos efectos.

### Pseudocódigo

```
inhabil(d) = (d.weekday() in {SAB, DOM}) or (d in FERIADOS_NACIONALES) or (d in FERIADOS_LOCALES[territorio])

sumar_habiles(inicio, n):
    d = inicio          # día del hecho (denuncia, notificación, recepción)
    c = 0
    while c < n:
        d = d + 1 día
        if not inhabil(d): c += 1
    return d            # fecha de vencimiento

sumar_corridos(inicio, n):  return inicio + n días
```

### Ejemplo resuelto

**Supuesto:** una trabajadora presenta denuncia de acoso laboral **ante su empleador** el **martes 15 de septiembre de 2026**. La empresa decide investigar internamente. Feriados relevantes: viernes **18-09-2026** (Independencia) y sábado **19-09-2026** (Glorias del Ejército); luego lunes **12-10-2026** (Encuentro de Dos Mundos); sábado 31-10 y domingo 01-11 (ya inhábiles por fin de semana).

| Paso | Cálculo | Resultado |
|---|---|---|
| Medidas de resguardo | Inmediatas | martes **15-09-2026** |
| Informar a la DT el inicio de la investigación (3 días hábiles) | 16-09 (1), 17-09 (2) — 18-09 feriado, 19-09 feriado/sábado, 20-09 domingo — 21-09 (3) | vence **lunes 21-09-2026** |
| Conclusión de la investigación (30 días hábiles desde la denuncia) | día 1 = 16-09; día 10 = 30-09; día 20 = 15-10; día 30 = 29-10 | vence **jueves 29-10-2026** |
| Remisión del informe a la DT (2 días hábiles) | 30-10 (1) — 31-10 sábado, 01-11 domingo — 02-11 (2) | vence **lunes 02-11-2026** |
| Pronunciamiento de la DT (30 días hábiles) | desde el 03-11 | vence **martes 15-12-2026** |
| Aplicar medidas/sanciones (**15 días CORRIDOS**) | 15-12 + 15 días de calendario | vence **miércoles 30-12-2026** |

> Nota: si el empleador hubiera derivado la denuncia a la DT, el plazo de 30 días de investigación se contaría **desde la fecha de recepción de la derivación**, acreditada por el certificado de recepción de la DT (art. 17 DS 21 y ORD.N°57/04 N°5).

## Cambios recientes (2024–2026)

### Normativa

| Fecha | Norma | Cambio | Etiqueta |
|---|---|---|---|
| 15-01-2024 | Ley 21.643 publicada | Crea el régimen completo | [VERIFICADO] [1] |
| 03-07-2024 | DS N°21/2024 MINTRAB publicado | Reglamento de directrices de investigación | [VERIFICADO] [2] |
| **31-07-2024** | **Ley 21.687** | **Primera modificación de la Ley 21.643**: corrige un error de referencia en el **artículo 4** de la Ley 21.643 — las conductas están en el **art. 82 letras l) y m)** de la Ley 18.883 (Estatuto Municipal), no en el art. 84 | [VERIFICADO en cuanto a que modificó la ley (BCN registra "Última modificación: 31-JUL-2024 - Ley 21687"); el contenido preciso de la corrección es [SECUNDARIO]] [3] |
| 01-08-2024 | Entrada en vigencia | Ley 21.643 + DS 21 operativos | [VERIFICADO] [1][2] |
| **03-01-2025** | **Ley 21.724** (reajuste del sector público, "modifica diversos cuerpos legales") | **Agrega el artículo 6 a la Ley 21.643**: reporte semestral de denuncias de los organismos administradores a la SUSESO, obligación del empleador de entregar la información, y envío del informe estadístico consolidado al MINTRAB y al Consejo Superior Laboral en enero y julio. **Verificado por comparación directa de las dos versiones del texto en BCN**: la versión "Texto Original — de 01-AGO-2024 a 02-ENE-2025" **no contiene** el artículo 6; la versión vigente desde el 03-01-2025 sí. | [VERIFICADO] [1][4] |
| 07-06-2024 / 26-07-2024 / 19-08-2024 | Circulares SUSESO N° 3.813, 3.819 y 3.825 | Asistencia técnica de las mutualidades; modifican los Libros III, IV y V del Compendio | [VERIFICADO] [5] |
| 03-07-2025 (fecha límite) | Art. 2° transitorio DS 21 | La DT debía tener operativa una plataforma electrónica de denuncias | [VERIFICADO el mandato; su cumplimiento efectivo es NO VERIFICADO] [2] |

### Dictámenes de la Dirección del Trabajo (orden cronológico)

| Dictamen | Fecha | Criterio principal | Etiqueta |
|---|---|---|---|
| ORD. N°362/19 | 07-06-2024 | Fija sentido y alcance de la Ley 21.643. La Inspección sólo verifica el cumplimiento procedimental y la **congruencia** entre informe y conclusiones; **no** emite pronunciamiento de fondo ni genera presunción legal (art. 23 DFL N°2 de 1967) | [VERIFICADO] [8][11] |
| ORD. N°497/21 | 31-07-2024 | Medios idóneos para recibir denuncias | [VERIFICADO la existencia y fecha; contenido SECUNDARIO] [12] |
| ORD. N°834 | 05-12-2024 | (ordinario concordante) | [NO VERIFICADO el contenido] |
| **ORD.N°385/9** | **03-06-2025** | *"Para dar inicio al procedimiento de investigación (…) se requiere la **denuncia de la persona afectada, sin que el empleador pueda iniciarlo de oficio**."* Sin perjuicio del deber general de protección | [VERIFICADO] [9] |
| **ORD.N°386/10** | **03-06-2025** | Plazos en **días hábiles** (sábados, domingos y festivos inhábiles); la investigación **no se suspende** por feriado legal ni licencia médica | [VERIFICADO] [10] |
| **ORD.N°515/21** | **04-08-2025** | La persona investigadora debe elegirse priorizando a quien tenga formación en acoso/género/DDFF (acreditable por certificación de entidades reconocidas por el Estado); la ley no fija un estándar probatorio expreso, el informe debe exponer **indicios y razonamientos coherentes y congruentes** | [SECUNDARIO en cuanto al detalle; existencia y fecha VERIFICADAS] [12][13] |
| **ORD.N°57/04** | **26-01-2026** | (1) 30 **días hábiles administrativos**; (2) el plazo del art. 486 CT es sólo para la tutela laboral y **no libera al empleador** de investigar denuncias por hechos antiguos; (3) a hechos anteriores al 01-08-2024 se aplica la **definición de acoso vigente a la fecha de los hechos** (aunque el procedimiento sea el nuevo); (4) ante observaciones de la DT al informe, el empleador debe ajustarse a derecho; (5) en derivación por subcontratación el plazo corre **desde que la empresa que debe investigar recibe la denuncia**; (6) la investigación **siempre** la lleva la empresa principal o usuaria; (7) confidencialidad alcanza a todas las empresas; (8) la DT no es competente si la denunciante es funcionaria pública | [VERIFICADO] [11] |
| **ORD.N°146/13** | **24-02-2026** | Ante denuncias incompletas hay que dar **plazo razonable** para complementarlas y no se puede prescindir de ellas; las denuncias contra personas del art. 4 inc. 1° CT van **siempre** a la DT; **se requiere identificar a la persona denunciante** para iniciar el procedimiento (sin perjuicio del art. 184 CT) | [VERIFICADO] [14] |
| **ORD.N°168/15** | **27-02-2026** | Materia relacionada con Ley Karin | [NO VERIFICADO — no se pudo abrir el texto] |
| **ORD.N°196/17** | **06-03-2026** | Las medidas de resguardo **no pueden ser gravosas ni producir menoscabo**; si se modifica el puesto de trabajo de la denunciante, el empleador debe **garantizar al menos la misma remuneración, incluida la variable**, pagando la diferencia si es necesario | [VERIFICADO] [15] |
| **ORD.N°214** | **12-03-2026** | La normativa no prohíbe organizar actividades de empresa con consumo de alcohol, pero rige el **deber de protección del art. 184 CT** y esas actividades **deben considerarse en el protocolo de prevención** | [VERIFICADO] [16] |

### Feriados
- **Ley 21.791** (diciembre 2025) repuso a nivel legal el feriado **bancario** de fin de año y el sabatino. No afecta a los feriados de ámbito general. [SECUNDARIO] [25]
- **Pausa electoral 2026-2027**: no hay elecciones ni plebiscitos, por lo que no habrá feriados del art. 169 de la Ley 18.700 en esos años. Siguientes: primarias 09-07-2028, elecciones regionales y municipales 29-10-2028 (2ª vuelta regional 26-11-2028), presidenciales y parlamentarias 18-11-2029. [SECUNDARIO] [26]

## Pendientes y dudas

1. **Día inicial del cómputo.** Ni la Ley 21.643 ni el DS 21 dicen si el plazo empieza el mismo día del hecho o el siguiente. Se asumió el art. 25 de la Ley 19.880 ("desde el día siguiente"). **Conviene consultar a la DT o buscar un dictamen específico antes de dejarlo fijo en el motor.**
2. **Contradicción ley/reglamento en el plazo de sanciones.** El art. 211-E inc. 1° CT dice "quince días contados desde su recepción" (del informe); el art. 19 DS 21 dice "quince días **corridos**" contados desde la **notificación del pronunciamiento de la DT** (o desde el vencimiento de los 30 días). Se recomienda usar la regla del reglamento (es la más específica y la que fiscaliza la DT), pero el punto no está zanjado por dictamen expreso encontrado en esta investigación.
3. **Texto íntegro del Dictamen 362/19.** Sólo se obtuvo su sumario y las citas reproducidas en el ORD.N°57/04. El PDF completo está en la ficha de la DT y en previsionsocial.gob.cl; conviene leerlo entero antes de codificar reglas de detalle.
4. **ORD.N°168/15 (27-02-2026)**: identificado en las concordancias de la DT pero no se logró abrir su texto.
5. **Tipificador de infracciones de la DT para Ley Karin**: la graduación concreta de las multas por cada tipo de incumplimiento (qué conducta es "grave" y cuántas UTM implica) sólo se obtuvo de prensa especializada [SECUNDARIO]; falta la resolución o el tipificador oficial de la DT.
6. **Números de ley de algunos feriados**: 12 de octubre (¿Ley 3.810?), Morro de Arica (¿Ley 20.663?), Chillán (¿Ley 20.768?), Día Nacional del Trabajo (¿art. 35 CT / Ley 2.200?). No verificados.
7. **Ley 21.357** (Pueblos Indígenas): el texto del artículo único se tomó de fuentes secundarias; falta leerlo en BCN. Además, **falta definir la fuente astronómica oficial** para determinar el día del solsticio (¿SHOA? ¿decreto anual?) — esto es crítico para el motor.
8. **Ley 19.668**: el artículo único se obtuvo citado por una fuente secundaria (la búsqueda reproduce el texto); falta confirmarlo leyendo la ficha BCN idNorma=160270.
9. **Ley 18.700 art. 169**: citado por la DT; falta leerlo en BCN.
10. **Plataforma electrónica de denuncias de la DT** y **portal/modelo de protocolo oficial de la DT**: no se confirmaron URLs ni si están operativos.
11. **Periodicidad de reevaluación del riesgo psicosocial** (CEAL-SM) según el Compendio SUSESO: no se obtuvo un intervalo numérico.
12. **Contraloría**: el Dictamen N° E516610 de 19-07-2024 y su aclaración de 2025 no se verificaron en contraloria.cl.
13. **Tipo de día (hábil/corrido) de los plazos del sector público** (5 y 20 días): no determinado; probablemente días hábiles administrativos de la Ley 19.880, pero no se verificó.
14. **Feriados regionales adicionales** (por ejemplo, posibles feriados locales creados en 2025-2026) no fueron barridos exhaustivamente.

## Fuentes

1. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 21.643**, texto completo (versión 03-01-2025). https://www.bcn.cl/leychile/navegar?idNorma=1200096 — versión de impresión: https://www.bcn.cl/leychile/navegar/imprimir?idNorma=1200096 [OFICIAL]
2. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Decreto 21, de 26-05-2024, Ministerio del Trabajo y Previsión Social** (publicado 03-07-2024), Reglamento de directrices de investigación. https://www.bcn.cl/leychile/navegar?idNorma=1204689 — impresión: https://www.bcn.cl/leychile/navegar/imprimir?idNorma=1204689 [OFICIAL]
3. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 21.687**, de 31-07-2024 (primera modificación de la Ley 21.643). https://www.bcn.cl/leychile/navegar?idNorma=1205338 [OFICIAL]
4. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 21.724**, de 03-01-2025 (reajuste del sector público; agrega el art. 6 a la Ley 21.643). https://www.bcn.cl/leychile/Navegar?idNorma=1209939 [OFICIAL] — verificación por comparación de versiones: https://www.bcn.cl/leychile/navegar/imprimir?idNorma=1200096&idVersion=2024-08-01 (texto original, sin art. 6) vs. https://www.bcn.cl/leychile/navegar/imprimir?idNorma=1200096 (versión vigente, con art. 6)
5. Superintendencia de Seguridad Social — **Circular N° 3.813, de 07-06-2024**. https://www.suseso.gob.cl/612/w3-article-732037.html [OFICIAL]
6. Superintendencia de Seguridad Social — **Compendio de Normas del Seguro Social de Accidentes del Trabajo y Enfermedades Profesionales**, Libro IV, "Capítulo I. Elaboración e implementación del protocolo de prevención del acoso sexual, laboral y la violencia en el trabajo". https://www.suseso.gob.cl/613/w3-propertyvalue-726761.html [OFICIAL]
7. Diario Financiero — "Ya están claras las infracciones por las cuales las empresas podrían ser multadas por Ley Karin". https://www.df.cl/economia-y-politica/laboral-personas/ya-estan-claras-las-infracciones-por-las-cuales-las-empresas-podrian-ser [SECUNDARIO]
8. Dirección del Trabajo — **Dictamen ORD. N°362/19, de 07-06-2024**, "Fija sentido y alcance de las modificaciones introducidas por la Ley N°21.643 al Código del Trabajo". https://www.dt.gob.cl/legislacion/1624/w3-article-126267.html [OFICIAL]
9. Dirección del Trabajo — **Dictamen ORD.N°385/9, de 03-06-2025** (no procede investigación de oficio). https://www.dt.gob.cl/legislacion/1624/w3-article-127874.html [OFICIAL]
10. Dirección del Trabajo — **Dictamen ORD.N°386/10, de 03-06-2025** (plazos en días hábiles; no se suspenden por feriado legal ni licencia médica). https://www.dt.gob.cl/legislacion/1624/w3-article-127876.html [OFICIAL]
11. Dirección del Trabajo — **Dictamen ORD.N°57/04, de 26-01-2026** (30 días hábiles administrativos; subcontratación; art. 486 CT; definición aplicable a hechos anteriores). https://www.dt.gob.cl/legislacion/1624/w3-article-128901.html [OFICIAL]
12. Dirección del Trabajo — Índice de dictámenes "Ley Karin", Normativa 3.0. https://www.dt.gob.cl/legislacion/1624/w3-propertyvalue-194488.html [OFICIAL]
13. Dirección del Trabajo — **Dictamen ORD.N°515/21, de 04-08-2025** (persona investigadora y estándar probatorio). https://www.dt.gob.cl/legislacion/1624/w3-article-128099.html [OFICIAL]
14. Dirección del Trabajo — **Dictamen ORD.N°146/13, de 24-02-2026** (denuncias incompletas, denuncia anónima, denuncias contra el art. 4 inc. 1° CT). https://www.dt.gob.cl/legislacion/1624/w3-article-129021.html [OFICIAL]
15. Dirección del Trabajo — **Dictamen ORD.N°196/17, de 06-03-2026** (medidas de resguardo no pueden mermar la remuneración). https://www.dt.gob.cl/legislacion/1624/w3-article-129067.html [OFICIAL]
16. Dirección del Trabajo — **ORD.N°214, de 12-03-2026** (actividades de la empresa con consumo de alcohol y deber de protección). https://www.dt.gob.cl/legislacion/1624/w3-article-129095.html [OFICIAL]
17. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 2.977, de 01-02-1915**, "Fija los días feriados". https://www.bcn.cl/leychile/navegar?idNorma=23639 [OFICIAL]
18. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 19.668, de 10-03-2000**, "Traslada a los días lunes los feriados que indica". https://www.bcn.cl/leychile/navegar?idNorma=160270&idVersion=2000-03-10 [OFICIAL — el texto del artículo único se obtuvo citado por búsqueda, no leído directamente en esta pasada]
19. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 19.973, de 10-09-2004** (feriados irrenunciables), versión vigente 30-05-2016. https://www.bcn.cl/leychile/navegar?idNorma=230132 [OFICIAL]
20. Biblioteca del Congreso Nacional de Chile — Ley Chile, Legislación Temática "FERIADOS" (índice de leyes de feriados). https://www.bcn.cl/leychile/Consulta/listado_n_sel?comp=&agr=2&_grupo_aporte=&sub=1151 [OFICIAL]
21. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 20.299, de 11-10-2008** (Día Nacional de las Iglesias Evangélicas y Protestantes y su traslado). https://www.bcn.cl/leychile/navegar?idNorma=279294 [OFICIAL]
22. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 20.983, de 30-12-2016** (feriados 17 de septiembre y 2 de enero). https://www.bcn.cl/leychile/navegar?idNorma=1098384 [OFICIAL]
23. Biblioteca del Congreso Nacional de Chile — Ley Chile. **Ley 21.357, de 19-06-2021** (Día Nacional de los Pueblos Indígenas, solsticio de invierno). https://www.bcn.cl/leychile/navegar?idNorma=1161743 [OFICIAL — texto citado por fuentes secundarias, no leído directamente]
24. Dirección del Trabajo — Normativa 3.0, referencia "ley 18.700, artículo 169" (día de elección o plebiscito es feriado legal). https://www.dt.gob.cl/legislacion/1624/w3-propertyvalue-146206.html [OFICIAL — el texto del art. 169 fue citado por fuente secundaria]
25. feriadoschilenos.cl — "Días Feriados en Chile" (compendio actualizado hasta la Ley 21.791, con listados 2026 y 2027 y normativa asociada). https://www.feriadoschilenos.cl/ [SECUNDARIO — todos los días de la semana y las fechas trasladadas se recalcularon y verificaron algorítmicamente en esta investigación]
26. El Mostrador — "Cuándo son las próximas elecciones en Chile: así queda el calendario electoral a partir del 2026" (21-12-2025). https://www.elmostrador.cl/datos-utiles/2025/12/21/cuando-son-las-proximas-elecciones-en-chile-asi-queda-el-calendario-electoral-a-partir-del-2026/ [SECUNDARIO]
