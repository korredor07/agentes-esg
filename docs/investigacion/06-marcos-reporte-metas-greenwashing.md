# Marcos de reporte, aseguramiento, metas climáticas, MACC y greenwashing

Fecha de investigación: 2026-09-15

> Convenciones de etiquetado: **[VERIFICADO]** = dato leído directamente en la fuente oficial primaria (texto del estándar, norma o regulador). **[SECUNDARIO]** = fuente no oficial (consultora, prensa especializada) o resumen de buscador no confirmado en el documento primario. **[NO VERIFICADO]** = no se pudo confirmar en esta investigación; requiere revisión humana antes de usar en producto.
> Nota de propiedad intelectual: no se reproduce texto literal de GRI, SASB, IFRS, ESRS, ISO ni SBTi. Se citan solo códigos y títulos de divulgaciones (identificadores necesarios para la interoperabilidad) y se resume el contenido con palabras propias.

## Resumen

**Qué hay que saber en una página.**

**1. Los marcos se están reescribiendo a la vez, y casi todo entra en vigor entre 2026 y 2028.** GRI publicó GRI 101 (biodiversidad, vigente desde el 1-ene-2026) y GRI 102 y 103 (clima y energía, vigentes desde el 1-ene-2027), que **retiran** GRI 302, GRI 305-1 a 305-5 y GRI 201-2. El ISSB emitió en diciembre de 2025 enmiendas a NIIF S2 (vigentes 1-ene-2027). La Comisión Europea adoptó el 3-jul-2026 los **ESRS simplificados**, con **61 % menos de datapoints obligatorios**, obligatorios desde el ejercicio 2027. El SBTi publicó el **Corporate Net-Zero Standard V2.0** el 11-jun-2026, en vigor el 31-ene-2027. **ISSA 5000** sustituye a ISAE 3410 el 15-dic-2026. Conclusión de diseño: el motor debe tratar la **versión del marco** como parámetro, nunca como constante.

**2. Chile prorrogó un año; Perú va por otra vía y llega en 2029.** La CMF publicó la **NCG 572 (27-jul-2026)**, que mueve la obligación de reportar bajo NIIF S1/S2 de las memorias del año 2026 a las del **año 2027**. En Perú, la adopción vino del Consejo Normativo de Contabilidad (no del regulador de valores), con obligatoriedad reportada desde el **1-ene-2029** para empresas no supervisadas con ingresos ≥ 2.300 UIT (dato **[SECUNDARIO]**, pendiente de verificar).

**3. La UE redujo el alcance de la CSRD pero endureció la publicidad ambiental.** La Directiva (UE) 2026/470 ("Omnibus I", en vigor el 18-mar-2026) subió el umbral a **1.000 empleados y 450 M EUR**, eliminó el mandato de normas de aseguramiento razonable y suprimió las normas sectoriales obligatorias. En paralelo, la **Directiva (UE) 2024/825 se aplica desde el 27 de septiembre de 2026** —doce días después de la fecha de esta investigación— y prohíbe **en toda circunstancia** las alegaciones ambientales genéricas, las que cubren todo el producto cuando la evidencia cubre una parte, y las de neutralidad **basadas solo en compensación**. Las promesas a futuro exigen plan detallado y **verificación por un tercero independiente**.

**4. Chile ya sanciona el greenwashing hoy.** La Ley 19.496 castiga la publicidad falsa o engañosa con hasta **1.500 UTM**, que suben a **2.250 UTM** cuando la publicidad incide sobre la salud, la seguridad o **el medio ambiente**. No hace falta una ley nueva: el argumento ya existe.

**5. Las cifras de SBTi que hay que implementar bien.** Tasa lineal de **4,2 % anual** para Alcances 1+2 (1,5 °C) y **2,5 %** para Alcance 3 — pero **ajustadas dinámicamente** según año base y año net-zero, no fijas. Metas de corto plazo de **5 a 10 años** desde la presentación. Alcance 3 obligatorio si representa **≥ 40 %** del total, con cobertura mínima del **67 %**. Meta de largo plazo: **90 %** de reducción. Créditos de carbono y emisiones evitadas **no cuentan** como progreso.

**6. El encadenamiento que da valor al producto.** Trayectoria SBTi → Monte Carlo (probabilidad y brecha) → MACC (qué medidas cubren la brecha y a qué costo) → nueva simulación hasta superar el umbral de credibilidad. El ejemplo trabajado en este documento arroja una probabilidad de cumplimiento del **11,5 %** con una brecha mediana de **1.320 tCO2e/año**: exactamente el tipo de hallazgo que convierte una meta publicitada en un riesgo legal bajo el art. 6(2)(d) de la Directiva 2024/825.

**7. Advertencia legal para un proyecto de código abierto.** El uso no comercial de los estándares SASB e NIIF es gratuito, pero **integrarlos en un producto o servicio requiere licencia de la Fundación IFRS**, y eso incluye SICS®. Referenciar por código y enlazar; no empaquetar el contenido.

**8. Veinte puntos quedaron sin verificar** (ver "Pendientes y dudas"), casi todos por bloqueo técnico de las fuentes: `iso.org` devolvió 403, `fsb-tcfd.org` 403, el portal peruano `gob.pe` 418 y el servicio de texto legal chileno truncó la Ley 19.496 en el artículo 24. Ninguno se rellenó con suposiciones.

---

## 1. GRI (Global Reporting Initiative)

### 1.1 Arquitectura del sistema GRI

El sistema GRI se organiza en tres series de estándares interrelacionados [1]:

| Serie | Estándares | Uso |
|---|---|---|
| **Universales** | GRI 1: Foundation 2021; GRI 2: General Disclosures 2021; GRI 3: Material Topics 2021 | Los aplican **todas** las organizaciones que reportan con GRI. Vigentes desde el 1 de enero de 2023. [VERIFICADO] [1][2] |
| **Sectoriales** | GRI 11, 12, 13, 14 (ver 1.2) | Se usan según el/los sector(es) en que opera la organización, para identificar temas probablemente materiales. [VERIFICADO] [1] |
| **Temáticos** | Serie 101–103 (nueva numeración) y series 200/300/400 heredadas de 2016–2020 | Se seleccionan según la lista de temas materiales determinada con GRI 3. [VERIFICADO] [1] |

Roles en palabras propias:

- **GRI 1: Foundation 2021** — Explica el propósito del sistema, los conceptos clave (impacto, debida diligencia, grupos de interés, materialidad de impacto) y fija los **nueve requisitos obligatorios** para poder declarar reporte "de conformidad con". Contiene además los **ocho principios de reporte**. Fecha de vigencia: informes publicados desde el 1 de enero de 2023. [VERIFICADO] [2]
- **GRI 2: General Disclosures 2021** — Divulgaciones sobre la propia organización: perfil, entidades incluidas, periodo de reporte, reexpresiones, aseguramiento externo, actividades y trabajadores, gobernanza, estrategia, políticas y prácticas, y participación de grupos de interés. [VERIFICADO] [3]
- **GRI 3: Material Topics 2021** — Proceso paso a paso para determinar temas materiales y las divulgaciones 3-1 (proceso), 3-2 (lista de temas materiales) y 3-3 (gestión de cada tema material). [VERIFICADO] [2]

**Dato operativo clave para el motor:** GRI **no** exige un número mínimo de divulgaciones por estándar temático; la organización reporta solo las divulgaciones relevantes para sus impactos en ese tema material. [VERIFICADO] [2][4]

### 1.2 Estándares sectoriales vigentes (incluida minería)

| Estándar | Publicación | Vigencia (informes publicados desde) | Versión |
|---|---|---|---|
| GRI 11: Oil and Gas Sector | Octubre 2021 | 1 de enero de 2023 | 2021 V1.1 [VERIFICADO] [5][6] |
| GRI 12: Coal Sector | Marzo 2022 | 1 de enero de 2024 | 2022 V1.1 [VERIFICADO] [5][6] |
| GRI 13: Agriculture, Aquaculture and Fishing Sectors | Junio 2022 | 1 de enero de 2024 | 2022 V1.1 [VERIFICADO] [5][6] |
| **GRI 14: Mining Sector** | **Febrero 2024** | **1 de enero de 2026** | 2024 V1.1 [VERIFICADO] [5][6] |

En desarrollo por el GSSB (sin fecha de publicación confirmada): sectoriales de **servicios financieros** y **textil y confección**; temáticos de **trabajo/derechos laborales**, **impacto económico** y **contaminación**. [VERIFICADO] [5]

**Alineación de sectoriales con los nuevos temáticos de clima y energía:** GRI indica que las secciones de reporte actualizadas de GRI 11, 12, 13 y 14 con las nuevas divulgaciones de clima y energía se pondrán a disposición el **1 de enero de 2026** y serán obligatorias cuando entre en vigor GRI 103. [VERIFICADO] [4]

### 1.3 Nuevos estándares temáticos: GRI 101, 102 y 103

#### GRI 101: Biodiversity 2024 — vigencia: informes publicados desde el **1 de enero de 2026** [VERIFICADO] [7]

Estructura: Sección 1 con tres divulgaciones de gestión; Sección 2 con cinco divulgaciones de impacto. [VERIFICADO] [7]

| Código | Título | Qué pide (resumen propio) |
|---|---|---|
| 101-1 | Policies to halt and reverse biodiversity loss | Políticas y compromisos de la organización orientados a detener y revertir la pérdida de biodiversidad. |
| 101-2 | Management of biodiversity impacts | Cómo se gestionan los impactos, incluida la aplicación de la jerarquía de mitigación (evitar, minimizar, restaurar/rehabilitar, compensar). |
| 101-3 | Access and benefit-sharing | Acceso a recursos genéticos y reparto justo y equitativo de beneficios derivados de su uso. |
| 101-4 | Identification of biodiversity impacts | Proceso para identificar dónde ocurren los impactos sobre biodiversidad (operaciones propias y cadena de suministro). |
| 101-5 | Locations with biodiversity impacts | Emplazamientos concretos donde hay impactos significativos, incluidas áreas ecológicamente sensibles. |
| 101-6 | Direct drivers of biodiversity loss | Información por motor directo de pérdida: cambio de uso de suelo/mar, explotación de recursos, cambio climático, contaminación y especies exóticas invasoras. |
| 101-7 | Changes to the state of biodiversity | Cambios medidos o estimados en el estado de la biodiversidad (condición de ecosistemas, tamaño y extensión, especies). |
| 101-8 | Ecosystem services | Servicios ecosistémicos afectados y personas/comunidades que dependen de ellos. |

Temas conexos que GRI remite a otros estándares al reportar biodiversidad: GRI 303 (agua), GRI 305 (emisiones), 306-3 de GRI 306: Effluents and Waste 2016 (derrames significativos), GRI 411 (derechos de pueblos indígenas) y GRI 413 (comunidades locales). [VERIFICADO] [7]

#### GRI 102: Climate Change 2025 — vigencia: informes publicados desde el **1 de enero de 2027** (se anima la adopción anticipada) [VERIFICADO] [8][9]

Estructura: Sección 1 con dos divulgaciones de gestión; Sección 2 con ocho divulgaciones de impacto. [VERIFICADO] [8]

| Código | Título | Qué pide (resumen propio) |
|---|---|---|
| 102-1 | Transition plan for climate change mitigation | Plan de transición para mitigar el cambio climático: contenido, alineación, gobernanza y avance. |
| 102-2 | Climate change adaptation plan | Plan de adaptación: riesgos físicos, medidas y su gestión. |
| 102-3 | Just transition | Efectos de la transición sobre trabajadores y comunidades, y medidas de transición justa (incluye plantillas de métricas por género y tipo de empleo). |
| 102-4 | GHG emissions reduction targets and progress | Metas de reducción de GEI (corto, medio y largo plazo) y progreso frente a ellas. |
| 102-5 | Scope 1 GHG emissions | Emisiones directas. |
| 102-6 | Scope 2 GHG emissions | Emisiones indirectas por energía comprada. |
| 102-7 | Scope 3 GHG emissions | Otras emisiones indirectas de la cadena de valor. |
| 102-8 | GHG emissions intensity | Ratio(s) de intensidad de emisiones. |
| 102-9 | GHG removals in the value chain | Remociones de GEI en la cadena de valor. |
| 102-10 | Carbon credits | Créditos de carbono cancelados y comprados no cancelados, por tipo de proyecto. |

**Efecto de sustitución:** cuando GRI 102 entre en vigor, se retiran **GRI 305: Emissions 2016 divulgaciones 305-1 a 305-5** (y el Requisito 1.2 de GRI 305) y **la divulgación 201-2** de GRI 201: Economic Performance 2016. Las divulgaciones 305-6 (sustancias que agotan la capa de ozono) y 305-7 (NOx, SOx y otras emisiones al aire) **permanecen** en GRI 305. [VERIFICADO] [10][11]

#### GRI 103: Energy 2025 — vigencia: informes publicados desde el **1 de enero de 2027** (se anima la adopción anticipada) [VERIFICADO] [4][12]

| Código | Título | Qué pide (resumen propio) |
|---|---|---|
| 103-1 | Energy policies and commitments | Políticas y compromisos de energía y los impactos derivados del consumo energético y de la transición a renovables. |
| 103-2 | Energy consumption and self-generation within the organization | Consumo de combustible y electricidad dentro de la organización, autogeneración y electricidad vendida, con desglose por fuente y carácter renovable/no renovable; criterios de calidad si se usan instrumentos contractuales. |
| 103-3 | Upstream and downstream energy consumption | Consumo energético significativo aguas arriba y aguas abajo, listando las categorías de Alcance 3 implicadas. |
| 103-4 | Energy intensity | Ratio(s) de intensidad energética. |
| 103-5 | Reduction in energy consumption | Reducciones logradas y en qué parte de la cadena de valor ocurren (integra el contenido de la antigua 302-5). |

**Efecto de sustitución:** **GRI 302: Energy 2016** queda retirado cuando entre en vigor GRI 103. La portada de GRI 302 indica vigencia "hasta el 31 de diciembre de 2026". [VERIFICADO] [12][13]

> ⚠️ **Errata detectada en fuente oficial:** el documento de preguntas frecuentes de GRI 103 (junio 2025), pregunta 6, escribe "GRI 305: Energy 2016 will be withdrawn" cuando por contexto debe referirse a **GRI 302: Energy 2016**. La portada del propio GRI 302 confirma que es GRI 302 el que se retira. Usar GRI 302 en el motor. [VERIFICADO — errata en [4]; confirmado por [13]]

**Puentes entre GRI 103 y GRI 102 (útiles para validación cruzada en el motor):** el consumo de combustible no renovable alimenta Alcance 1 (102-5); la electricidad comprada alimenta Alcance 2 (102-6); el consumo energético aguas arriba/abajo alimenta Alcance 3 (102-7). [VERIFICADO] [4]

**Por qué cambió la numeración:** con la reforma de 2021 los temáticos dejaron de agruparse en series 200 (económico) / 300 (ambiental) / 400 (social); los estándares revisados se renumeran secuencialmente desde 101. [VERIFICADO] [4]

### 1.4 Tabla de estándares temáticos clave (códigos y descripción propia)

Todos los títulos y códigos siguientes fueron leídos en el índice ("Content") del PDF oficial de cada estándar. [VERIFICADO]

| Estándar (vigencia) | Código | Título de la divulgación | Descripción propia |
|---|---|---|---|
| **GRI 201: Economic Performance 2016** (desde 1-jul-2018) | 201-1 | Direct economic value generated and distributed | Valor económico generado y distribuido: ingresos, costos operativos, salarios, pagos a proveedores de capital, pagos a gobiernos, inversión en comunidad y valor retenido. |
| | 201-2 | Financial implications and other risks and opportunities due to climate change | Riesgos y oportunidades climáticos con efecto financiero. **Se retira** cuando entre en vigor GRI 102 (1-ene-2027). |
| | 201-3 | Defined benefit plan obligations and other retirement plans | Cobertura de las obligaciones de planes de pensiones de prestación definida y otros planes de jubilación. |
| | 201-4 | Financial assistance received from government | Ayudas financieras recibidas de gobiernos (subsidios, créditos fiscales, incentivos). |
| **GRI 205: Anti-corruption 2016** (desde 1-jul-2018) | 205-1 | Operations assessed for risks related to corruption | Operaciones evaluadas por riesgos de corrupción y riesgos significativos detectados. |
| | 205-2 | Communication and training about anti-corruption policies and procedures | Comunicación y formación en políticas y procedimientos anticorrupción, por categoría y región. |
| | 205-3 | Confirmed incidents of corruption and actions taken | Casos confirmados de corrupción y medidas adoptadas. |
| **GRI 207: Tax 2019** (desde 1-ene-2021) | 207-1 | Approach to tax | Enfoque fiscal: estrategia tributaria, quién la aprueba y cómo se vincula con la estrategia de negocio y sostenibilidad. |
| | 207-2 | Tax governance, control, and risk management | Gobernanza fiscal, control interno, gestión de riesgos tributarios y mecanismos de denuncia. |
| | 207-3 | Stakeholder engagement and management of concerns related to tax | Diálogo con grupos de interés y gestión de inquietudes en materia fiscal, incluida la relación con autoridades. |
| | 207-4 | Country-by-country reporting | Reporte país por país: jurisdicciones, ingresos, resultados, impuestos devengados y pagados, empleados y activos. |
| **GRI 301: Materials 2016** (desde 1-jul-2018) | 301-1 | Materials used by weight or volume | Materiales usados por peso o volumen, distinguiendo renovables y no renovables. |
| | 301-2 | Recycled input materials used | Porcentaje de insumos reciclados utilizados. |
| | 301-3 | Reclaimed products and their packaging materials | Productos y envases recuperados al final de su vida útil. |
| **GRI 302: Energy 2016** (vigente hasta 31-dic-2026) | 302-1 | Energy consumption within the organization | Consumo energético dentro de la organización por fuente. |
| | 302-2 | Energy consumption outside of the organization | Consumo energético fuera de la organización. |
| | 302-3 | Energy intensity | Ratio de intensidad energética. |
| | 302-5 | Reductions in energy requirements of products and services | Reducción de los requerimientos energéticos de productos y servicios. |
| **GRI 303: Water and Effluents 2018** (desde 1-ene-2021) | 303-1 | Interactions with water as a shared resource | Interacción con el agua como recurso compartido: cómo y dónde se capta, usa y descarga. |
| | 303-2 | Management of water discharge-related impacts | Gestión de los impactos de los vertidos, incluidos estándares de calidad aplicados. |
| | 303-3 | Water withdrawal | Captación de agua por fuente, con desglose en zonas de estrés hídrico. |
| | 303-4 | Water discharge | Vertido de agua por destino y calidad. |
| | 303-5 | Water consumption | Consumo de agua (captación menos vertido) y variación de almacenamiento. |
| **GRI 304: Biodiversity 2016** (ver nota) | 304-1 a 304-4 | (ver 1.5) | Sustituido por GRI 101: Biodiversity 2024. |
| **GRI 305: Emissions 2016** (desde 1-jul-2018) | 305-1 | Direct (Scope 1) GHG emissions | Emisiones directas de GEI. **Se retira** el 1-ene-2027. |
| | 305-2 | Energy indirect (Scope 2) GHG emissions | Emisiones indirectas por energía adquirida (location-based y market-based). **Se retira** el 1-ene-2027. |
| | 305-3 | Other indirect (Scope 3) GHG emissions | Otras emisiones indirectas de la cadena de valor. **Se retira** el 1-ene-2027. |
| | 305-4 | GHG emissions intensity | Intensidad de emisiones. **Se retira** el 1-ene-2027. |
| | 305-5 | Reduction of GHG emissions | Reducción de emisiones lograda. **Se retira** el 1-ene-2027. |
| | 305-6 | Emissions of ozone-depleting substances (ODS) | Emisiones de sustancias que agotan la capa de ozono. **Permanece.** |
| | 305-7 | Nitrogen oxides (NOx), sulfur oxides (SOx), and other significant air emissions | NOx, SOx y otras emisiones significativas al aire. **Permanece.** |
| **GRI 306: Waste 2020** (desde 1-ene-2022) | 306-1 | Waste generation and significant waste-related impacts | Generación de residuos e impactos significativos asociados a lo largo de la cadena de valor. |
| | 306-2 | Management of significant waste-related impacts | Gestión de esos impactos, incluidas acciones de circularidad y control sobre terceros gestores. |
| | 306-3 | Waste generated | Residuos generados en toneladas, por composición. |
| | 306-4 | Waste diverted from disposal | Residuos desviados de eliminación (preparación para reutilización, reciclaje, otras operaciones de valorización). |
| | 306-5 | Waste directed to disposal | Residuos destinados a eliminación (incineración con y sin recuperación energética, vertedero, otras). |
| **GRI 308: Supplier Environmental Assessment 2016** (desde 1-jul-2018) | 308-1 | New suppliers that were screened using environmental criteria | Porcentaje de nuevos proveedores evaluados con criterios ambientales. |
| | 308-2 | Negative environmental impacts in the supply chain and actions taken | Impactos ambientales negativos detectados en la cadena de suministro y acciones tomadas. |
| **GRI 401: Employment 2016** (desde 1-jul-2018) | 401-1 | New employee hires and employee turnover | Nuevas contrataciones y rotación, por edad, género y región. |
| | 401-2 | Benefits provided to full-time employees that are not provided to temporary or part-time employees | Beneficios que reciben los empleados a tiempo completo y no los temporales o a tiempo parcial. |
| | 401-3 | Parental leave | Permiso parental: uso, retorno y retención. |
| **GRI 403: Occupational Health and Safety 2018** (desde 1-ene-2021) | 403-1 | Occupational health and safety management system | Sistema de gestión de SST y su alcance. |
| | 403-2 | Hazard identification, risk assessment, and incident investigation | Identificación de peligros, evaluación de riesgos e investigación de incidentes. |
| | 403-3 | Occupational health services | Servicios de salud ocupacional. |
| | 403-4 | Worker participation, consultation, and communication on occupational health and safety | Participación, consulta y comunicación con trabajadores en SST. |
| | 403-5 | Worker training on occupational health and safety | Formación de trabajadores en SST. |
| | 403-6 | Promotion of worker health | Promoción de la salud de los trabajadores. |
| | 403-7 | Prevention and mitigation of occupational health and safety impacts directly linked by business relationships | Prevención y mitigación de impactos de SST vinculados directamente por relaciones comerciales. |
| | 403-8 | Workers covered by an occupational health and safety management system | Trabajadores cubiertos por el sistema de gestión de SST. |
| | 403-9 | Work-related injuries | Lesiones por accidente laboral (tasas, fatalidades, lesiones de consecuencia grave). |
| | 403-10 | Work-related ill health | Dolencias y enfermedades laborales. |
| **GRI 404: Training and Education 2016** (desde 1-jul-2018) | 404-1 | Average hours of training per year per employee | Horas medias de formación por empleado y año, por género y categoría. |
| | 404-2 | Programs for upgrading employee skills and transition assistance programs | Programas de mejora de competencias y de asistencia a la transición (recolocación, fin de carrera). |
| | 404-3 | Percentage of employees receiving regular performance and career development reviews | Porcentaje de empleados con evaluaciones periódicas de desempeño y desarrollo. |
| **GRI 405: Diversity and Equal Opportunity 2016** (desde 1-jul-2018) | 405-1 | Diversity of governance bodies and employees | Diversidad de órganos de gobierno y plantilla por género, edad y otros indicadores. |
| | 405-2 | Ratio of basic salary and remuneration of women to men | Brecha salarial: razón entre salario base y remuneración de mujeres y hombres, por categoría y ubicación. |
| **GRI 406: Non-discrimination 2016** (desde 1-jul-2018) | 406-1 | Incidents of discrimination and corrective actions taken | Casos de discriminación y medidas correctivas adoptadas. |
| **GRI 413: Local Communities 2016** (desde 1-jul-2018) | 413-1 | Operations with local community engagement, impact assessments, and development programs | Porcentaje de operaciones con participación comunitaria, evaluaciones de impacto y programas de desarrollo. |
| | 413-2 | Operations with significant actual and potential negative impacts on local communities | Operaciones con impactos negativos significativos reales o potenciales sobre comunidades locales. |
| **GRI 414: Supplier Social Assessment 2016** (desde 1-jul-2018) | 414-1 | New suppliers that were screened using social criteria | Porcentaje de nuevos proveedores evaluados con criterios sociales. |
| | 414-2 | Negative social impacts in the supply chain and actions taken | Impactos sociales negativos en la cadena de suministro y acciones tomadas. |
| **GRI 418: Customer Privacy 2016** (desde 1-jul-2018) | 418-1 | Substantiated complaints concerning breaches of customer privacy and losses of customer data | Reclamaciones fundamentadas por violaciones de privacidad de clientes y pérdidas de datos. |

### 1.5 Requisitos del índice de contenidos: "de conformidad con" vs "con referencia a"

**Los nueve requisitos de "de conformidad con" (in accordance with)** — hay que cumplirlos **todos** [VERIFICADO] [2]:

| # | Requisito (título) | Nota operativa |
|---|---|---|
| 1 | Aplicar los principios de reporte | Los ocho principios de la sección 4 de GRI 1: exactitud, equilibrio, claridad, comparabilidad, exhaustividad, contexto de sostenibilidad, oportunidad y verificabilidad. |
| 2 | Reportar las divulgaciones de GRI 2 | Se permiten razones de omisión en todas **salvo** 2-1, 2-2, 2-3, 2-4 y 2-5. |
| 3 | Determinar los temas materiales | Incluye revisar los estándares sectoriales aplicables y **listar en el índice** los temas del sectorial considerados no materiales, con explicación. |
| 4 | Reportar las divulgaciones de GRI 3 | 3-1 (proceso), 3-2 (lista), 3-3 (gestión de cada tema). Solo se admite omisión en 3-3. |
| 5 | Reportar divulgaciones de los estándares temáticos por cada tema material | Sin mínimo de divulgaciones. Si el sectorial lista divulgaciones y no se reportan, hay que usar la razón de omisión "no aplicable" con explicación. |
| 6 | Dar razones de omisión para lo que no se pueda cumplir | Se declaran en el índice de contenidos, con explicación. |
| 7 | Publicar un índice de contenidos GRI | Ver contenido obligatorio abajo. |
| 8 | Incluir una declaración de uso | Fórmula: "[Nombre] has reported in accordance with the GRI Standards for the period [fechas inicio y fin]". |
| 9 | Notificar a GRI | Correo a `reportregistration@globalreporting.org`. Sin costo. |

**Contenido obligatorio del índice "de conformidad con"** — doce elementos (Requisito 7-a, i–xii) [VERIFICADO] [2]:

1. El título "GRI content index".
2. La declaración de uso.
3. El título del GRI 1 utilizado.
4. Los títulos de los estándares sectoriales GRI aplicables.
5. La lista de temas materiales de la organización.
6. La lista de temas del/los sectorial(es) determinados como **no** materiales, con la explicación del porqué.
7. La lista de divulgaciones reportadas, **incluyendo los títulos** de las divulgaciones.
8. Los títulos de los estándares GRI y otras fuentes de las que provienen esas divulgaciones.
9. Cuando no se reporten divulgaciones temáticas para un tema material del sectorial: la lista de esas divulgaciones y la razón de omisión requerida.
10. Los números de referencia del estándar sectorial para las divulgaciones tomadas de él.
11. La ubicación donde se encuentra la información de cada divulgación.
12. Cualquier razón de omisión utilizada.

Además (Requisito 7-b): si se publica un informe de sostenibilidad independiente y el índice no está dentro del informe, hay que incluir un enlace o referencia al índice en el informe. [VERIFICADO] [2]

**Los tres requisitos de "con referencia a" (with reference to)** — hay que cumplir los tres [VERIFICADO] [2]:

1. Publicar un índice de contenidos GRI.
2. Proporcionar una declaración de uso.
3. Notificar a GRI (mismo correo).

**Contenido obligatorio del índice "con referencia a"** — seis elementos [VERIFICADO] [2]:

1. El título "GRI content index".
2. La declaración de uso.
3. El título del GRI 1 utilizado.
4. La lista de divulgaciones reportadas de los estándares GRI, con sus títulos.
5. Los títulos de los estándares GRI de los que provienen.
6. La ubicación de la información de cada divulgación.

Fórmula de la declaración de uso "con referencia a": "[Nombre] has reported the information cited in this GRI content index for the period [fechas] with reference to the GRI Standards". [VERIFICADO] [2]

**Diferencias prácticas (para el skill de diagnóstico):**

| Aspecto | De conformidad con | Con referencia a |
|---|---|---|
| Requisitos a cumplir | 9 | 3 |
| Obligación de GRI 2 completo | Sí | No |
| Obligación de materialidad (GRI 3) | Sí (3-1, 3-2, 3-3) | No (solo *recomendado* usar 3-3) |
| Uso obligatorio de sectoriales | Sí, si existen para el sector | No |
| Principios de reporte | Obligatorios | Recomendados |
| Elementos del índice | 12 | 6 |
| Casos de uso típicos | Informe de sostenibilidad completo | Uso parcial de GRI, o cumplimiento de una regulación temática concreta (p. ej. clima) |

GRI ofrece plantillas en los Apéndices 1 ("de conformidad con") y 2 ("con referencia a") de GRI 1; se puede usar otro formato mientras se cumplan los requisitos. [VERIFICADO] [2]

---

## 2. NIIF S1 y NIIF S2 (ISSB / IFRS Foundation)

### 2.1 Qué son y estructura

| Norma | Título | Vigencia |
|---|---|---|
| **NIIF S1** | General Requirements for Disclosure of Sustainability-related Financial Information | Periodos anuales que comiencen el **1 de enero de 2024** o después; aplicación anticipada permitida siempre que se aplique también NIIF S2. [VERIFICADO] [14] |
| **NIIF S2** | Climate-related Disclosures | Idem: periodos anuales desde el **1 de enero de 2024**; aplicación anticipada permitida junto con NIIF S1. [VERIFICADO] [15] |

**Objetivo (resumen propio):** ambas normas exigen divulgar información sobre riesgos y oportunidades de sostenibilidad (S1) y de clima (S2) que razonablemente puedan afectar los flujos de efectivo, el acceso a financiación o el costo de capital de la entidad en el corto, mediano o largo plazo. La audiencia primaria son inversionistas, prestamistas y acreedores (perspectiva de materialidad financiera, no de doble materialidad). [VERIFICADO] [14][15][16]

### 2.2 Los cuatro pilares de contenido central

Ambas normas organizan las divulgaciones en los mismos cuatro pilares [VERIFICADO] [14][15]:

| Pilar | Qué exige (resumen propio) |
|---|---|
| **Gobernanza** | Procesos, controles y procedimientos con que la entidad vigila, gestiona y supervisa los riesgos y oportunidades. Incluye el rol del órgano de gobierno y de la administración. |
| **Estrategia** | Enfoque de la entidad para gestionar esos riesgos y oportunidades: modelo de negocio y cadena de valor, efectos financieros actuales y previstos, plan de transición (en clima) y resiliencia de la estrategia mediante análisis de escenarios climáticos. |
| **Gestión de riesgos** | Procesos para identificar, evaluar, priorizar y monitorear los riesgos y oportunidades, y su integración en la gestión de riesgos general. |
| **Métricas y metas** | Desempeño frente a los riesgos y oportunidades, incluidas las métricas transversales (emisiones GEI, entre otras), las métricas por industria y el progreso frente a metas propias o exigidas por regulación. |

### 2.3 Requisitos de Alcance 1, 2 y 3 en NIIF S2

| Tema | Requisito (resumen propio) | Etiqueta |
|---|---|---|
| Norma de medición | Las emisiones se miden conforme al **GHG Protocol: A Corporate Accounting and Reporting Standard (2004)**, salvo que una autoridad jurisdiccional o la bolsa donde cotiza exija otro método (párrafo 29(a)(ii)). | [VERIFICADO] [17][18] |
| Los tres alcances | NIIF S2 exige divulgar **Alcance 1, Alcance 2 y Alcance 3**, en términos brutos absolutos del periodo, sujeto a materialidad. | [VERIFICADO] [17] |
| Alcance 2 | Se divulga por el **método basado en ubicación** (location-based), acompañado de información sobre los instrumentos contractuales relevantes para la energía adquirida. | [VERIFICADO] [18] |
| Alcance 3 | Debe indicarse **cuáles de las 15 categorías** del *GHG Protocol Corporate Value Chain (Scope 3) Accounting and Reporting Standard (2011)* se incluyen en la medición. | [VERIFICADO] [17][18] |
| Marco de medición de Alcance 3 | NIIF S2 incorpora un "Scope 3 measurement framework" propio del ISSB (párrafo B40) que obliga a **priorizar insumos y supuestos** según características especificadas; es de uso obligatorio para todas las entidades que apliquen NIIF S2. | [VERIFICADO] [17] |
| Desagregación | Las emisiones se desagregan entre las entidades del **grupo contable consolidado** y **otras participadas excluidas** del grupo consolidado, para dar comparabilidad pese a la libertad de elegir enfoque (control operacional vs. control financiero). | [VERIFICADO] [17] |
| Emisiones financiadas | Entidades con actividades de gestión de activos, banca comercial o seguros deben divulgar información adicional sobre emisiones financiadas (categoría 15). | [VERIFICADO] [17][19] |
| Metas | NIIF S2 **no obliga a fijar** metas de emisiones; obliga a divulgar las que existan (propias o exigidas por ley) y, si la meta es neta, información específica adicional. | [VERIFICADO] [17] |

### 2.4 Métricas por industria

- Las **exigencias por industria** están en el **Apéndice B** de NIIF S2 y se derivaron, en gran medida sin cambios, de los estándares SASB. [VERIFICADO] [20]
- La *Industry-based Guidance on implementing IFRS S2* cubre **68 industrias en 11 sectores**; los estándares SASB completos cubren **77 industrias en 11 sectores**. [VERIFICADO] [20][21]
- En **julio de 2025** el ISSB publicó dos borradores para consulta proponiendo enmiendas a los estándares SASB y enmiendas consecuentes a la guía por industria de NIIF S2; el trabajo continuaba en 2026 con una revisión integral de los SASB prioritarios. [VERIFICADO] [20][22]

### 2.5 Alivios de transición y mecanismos de proporcionalidad

**Alivios de transición (solo el primer periodo anual de aplicación)** [VERIFICADO] [23]:

| Alivio | Contenido (resumen propio) |
|---|---|
| "Clima primero" | En el primer año de aplicación de NIIF S1 se puede divulgar únicamente lo relativo a riesgos y oportunidades **climáticos** (conforme a NIIF S2). El resto de temas de sostenibilidad se exige desde el segundo año. |
| Momento del reporte | NIIF S1 exige publicar las divulgaciones **al mismo tiempo** que los estados financieros. En el primer año se permite publicarlas después, junto con el informe financiero semestral. |
| Información comparativa | No se exige comparativo en el primer año. En el segundo año sí; y si en el primer año solo se reportó clima, el comparativo solo se exige para clima. |
| GHG Protocol | Si la entidad ya venía usando otro método de medición de GEI, puede continuar usándolo en el primer año de aplicación de NIIF S2. |
| Alcance 3 | No se exige divulgar emisiones de Alcance 3 en el primer año de aplicación de NIIF S2. |

Usar estos alivios **no impide** declarar cumplimiento con las normas ISSB; extenderlos más allá del primer año, sí. [VERIFICADO] [23]

**Mecanismos de proporcionalidad (siempre disponibles)** [VERIFICADO] [23]:

| Requisito | ¿Información razonable y sustentable sin costo o esfuerzo indebido? | ¿Enfoque cualitativo si faltan capacidades? |
|---|---|---|
| Determinación de efectos financieros previstos | Sí | Sí |
| Análisis de escenarios climáticos | Sí | Sí |
| Medición de Alcance 3 | Sí | — |
| Identificación de riesgos y oportunidades | Sí | — |
| Determinación del alcance de la cadena de valor | Sí | — |
| Cálculo de métricas de algunas categorías transversales | Sí | — |

**Declaración de cumplimiento:** el párrafo 72 de NIIF S1 exige una declaración explícita y sin reservas de cumplimiento; si no se cumple todo, la entidad debe declarar **aplicación parcial** e identificar qué requisitos no cumplió. [VERIFICADO] [23]

### 2.6 Enmiendas de 2025 a NIIF S2 y su vigencia

**"Amendments to Greenhouse Gas Emissions Disclosures (Amendments to IFRS S2)", emitidas en diciembre de 2025.** Vigencia: periodos anuales que comiencen el **1 de enero de 2027** o después; **se permite aplicación anticipada**. [VERIFICADO] [24][25]

Contenido (cuatro alivios, resumidos con palabras propias):

1. Se aclara que la entidad **puede limitar** la medición y divulgación de las emisiones de **Alcance 3 categoría 15** a las *emisiones financiadas* tal como las define NIIF S2.
2. Se permite usar **sistemas de clasificación alternativos** al GICS (Global Industry Classification Standard) para desagregar la información sobre emisiones financiadas.
3. Se **amplía el alivio jurisdiccional** respecto del uso del GHG Protocol: ahora aplica también cuando solo **una parte** de la entidad está obligada por regulación a usar otro método de medición.
4. Se introduce un **alivio jurisdiccional** respecto de usar los valores de potencial de calentamiento global (GWP) del último Informe de Evaluación del IPCC al convertir gases a CO2e.

Además, el ISSB emitió enmiendas consecuentes a **tres estándares SASB** para alinear las métricas de emisiones financiadas. [VERIFICADO] [24]

> ⚠️ Implicación para el motor: hasta que apliquen las enmiendas, la conversión a CO2e debe usar GWP del último IPCC AR, salvo alivio jurisdiccional. Parametrizar el set de GWP (AR5 vs AR6) por jurisdicción y por año de reporte.

### 2.7 Adopción en Chile, Perú y Latinoamérica

#### Chile — CMF

| Norma | Fecha | Contenido |
|---|---|---|
| **NCG 461** | 12 de noviembre de 2021 | Reestructura la memoria anual de emisores de valores (memoria anual integrada), incorporando contenidos de sostenibilidad y gobierno corporativo, con referencia a estándares SASB. [VERIFICADO] [26] |
| **NCG 519** | **28 de octubre de 2024** | Modifica las NCG 30, 461, 431 y 475. Su sección III agrega el numeral **9.1 "Estándares NIIF"**, que obliga a reportar conforme a **NIIF S1 y NIIF S2 del ISSB** para el mismo periodo anual de la memoria. Redacción original: sección III en vigor el **31 de diciembre de 2026**, aplicable a memorias referidas al **año 2026**; adopción voluntaria anticipada permitida declarándolo expresamente. Para el primer periodo de aplicación remite al **régimen de transición de las propias NIIF S1/S2**, que la entidad debe describir en la memoria. [VERIFICADO — texto leído de la norma] [26] |
| **NCG 572** | **27 de julio de 2026** | Modifica la NCG 519: reemplaza la fecha de vigencia de la sección III, que pasa a entrar en vigor el **31 de diciembre de 2027** y por tanto aplica a las **memorias referidas al año 2027** (primer reporte obligatorio publicado en 2028). Es decir, **una prórroga de un año**. [VERIFICADO — texto leído de la norma] [27] |

Otros datos relevantes de la NCG 519 [VERIFICADO] [26]:
- Excepción por tamaño: las entidades con **activos consolidados promedio de los dos ejercicios anteriores que no superen 1.000.000 de unidades de fomento** quedan exceptuadas del formulario del numeral C.1 y de varias exigencias de información (numerales 3.1, 3.5, 3.6, 3.7, 4.1, 4.2, 5, 7, 8 y 9 del C.2), pero deben describir igualmente su estructura de gobierno corporativo y su marco de gestión de riesgos y control interno.
- La norma menciona expresamente el reporte en formato **XBRL** para el estándar SASB de la sección 9.
- Diversidad de directorio: referencia a que los integrantes de un mismo sexo en las nóminas de candidatos no superen el **60 %** del total (o explicar por qué no).

La CMF acompaña la implementación con talleres (junio de 2026 con expertos de la Fundación IFRS) y sesiones de retroalimentación técnica para entidades que reporten **voluntariamente** en 2027 respecto del ejercicio 2026. [VERIFICADO] [28]

#### Perú

- **Resolución del Consejo Normativo de Contabilidad N.° 001-2026-EF/30**: oficializa **NIIF S1** ("Requerimientos Generales para la Información Financiera vinculada a la Sostenibilidad") y **NIIF S2** ("Información a revelar sobre Clima"). Fecha reportada: aprobación el **18 de marzo de 2026**, publicación/difusión el **27 de marzo de 2026**. **[SECUNDARIO]** — el portal gob.pe devolvió error al intentar leer el texto oficial; falta confirmar número, fechas y artículos exactos. [29][30]
- **Obligatoriedad**: a partir del **1 de enero de 2029**, para entidades **no supervisadas por la SMV ni por la SBS** cuyos ingresos anuales por actividades ordinarias sean **iguales o mayores a 2.300 UIT** al cierre del ejercicio anterior. **[SECUNDARIO]** [29][30]
- **SMV**: incorporó en su **Agenda Regulatoria 2026-2027** el alineamiento de la Memoria Anual con NIIF S1 y S2, con fecha tentativa hasta el **30 de junio de 2027** para remitir la propuesta a la Comisión Multisectorial de Calidad Regulatoria. **[SECUNDARIO]** [30]
- La SMV mantiene desde antes el **Reporte de Sostenibilidad Corporativa** como anexo a la memoria anual de emisores. [SECUNDARIO] [31]

#### Latinoamérica (panorama)

- **Brasil — CVM Resolução 193 (2023)**: adopción de las normas ISSB, voluntaria desde 2024 y **obligatoria para ejercicios iniciados a partir del 1 de enero de 2026** para compañías abiertas. **[SECUNDARIO]** — verificar en cvm.gov.br. [32]
- **México — CNBV**: incorporación de NIIF S1/S2, con primer reporte obligatorio en 2026 sobre el ejercicio 2025. **[SECUNDARIO]** [32]
- Según recuentos citados en prensa especializada, **nueve de las ~40 jurisdicciones** que han incorporado o anunciado la incorporación de las normas ISSB están en América Latina. **[NO VERIFICADO]** — cifra no confirmada en la fuente primaria de la Fundación IFRS. [32]

---

## 3. TCFD y su traspaso al ISSB

### 3.1 Estado institucional

| Hito | Fecha | Detalle |
|---|---|---|
| El FSB declara completado el trabajo del TCFD | **julio de 2023** | [VERIFICADO] [33] |
| Disolución del TCFD | **octubre de 2023** | [VERIFICADO] [33] |
| La Fundación IFRS asume el monitoreo del progreso en divulgación climática | **desde 2024** | Primer informe: *Progress on Corporate Climate-related Disclosures — 2024 Report*, publicado en **noviembre de 2024**. [VERIFICADO] [33] |
| Incorporación de las recomendaciones | — | Las **once divulgaciones recomendadas del TCFD están plenamente incorporadas en NIIF S2**. Una entidad que aplica NIIF S2 satisface las recomendaciones del TCFD y además cumple requisitos adicionales: métricas por industria, uso de créditos de carbono y emisiones financiadas. [VERIFICADO] [33] |

### 3.2 Las once divulgaciones recomendadas (títulos)

| Pilar | # | Divulgación recomendada (traducción propia) |
|---|---|---|
| **Gobernanza** | a) | Describir la supervisión del directorio sobre los asuntos climáticos. |
| | b) | Describir el rol de la administración en evaluar y gestionar los asuntos climáticos. |
| **Estrategia** | a) | Describir los riesgos y oportunidades climáticos identificados a corto, mediano y largo plazo. |
| | b) | Describir el impacto de esos riesgos y oportunidades en el negocio, la estrategia y la planificación financiera. |
| | c) | Describir la resiliencia de la estrategia considerando distintos escenarios climáticos, incluido uno de 2 °C o menos. |
| **Gestión de riesgos** | a) | Describir los procesos para identificar y evaluar los riesgos climáticos. |
| | b) | Describir los procesos para gestionar los riesgos climáticos. |
| | c) | Describir cómo esos procesos se integran en la gestión de riesgos global de la organización. |
| **Métricas y metas** | a) | Divulgar las métricas usadas para evaluar riesgos y oportunidades climáticos, en línea con la estrategia y el proceso de gestión de riesgos. |
| | b) | Divulgar las emisiones de Alcance 1, Alcance 2 y, si procede, Alcance 3, y los riesgos asociados. |
| | c) | Describir las metas usadas para gestionar riesgos y oportunidades climáticos y el desempeño frente a ellas. |

[VERIFICADO — reproducidas desde la guía oficial del Gobierno del Reino Unido que transcribe el marco TCFD; el sitio fsb-tcfd.org devolvió 403 y el PDF del FSB devolvió error 500] [34]

> Nota: la guía del sector público británico marca con un símbolo propio la adaptación de Estrategia b) ("operaciones" añadido) para el sector público; en el marco TCFD original la redacción es sobre negocio, estrategia y planificación financiera. Tenerlo presente si se cita literalmente. [VERIFICADO] [34]

### 3.3 Uso práctico para el proyecto

Para una empresa de Chile, Perú o la UE que ya reporta TCFD: el mapeo a NIIF S2 es directo en los cuatro pilares, pero hay que añadir (i) métricas por industria del Apéndice B, (ii) divulgación sobre créditos de carbono usados en las metas netas, (iii) emisiones financiadas si aplica, (iv) el marco de medición de Alcance 3 del ISSB, y (v) la declaración explícita de cumplimiento. [VERIFICADO — derivado de [33] y sección 2]

---

## 4. SASB

### 4.1 Cómo identificar la industria (SICS)

- **SICS® (Sustainable Industry Classification System®)** agrupa empresas según **riesgos de sostenibilidad compartidos**, no según fuente de ingresos como hacen las clasificaciones financieras tradicionales. [VERIFICADO] [35]
- La empresa se ubica en una **industria SICS primaria**; se puede consultar con la herramienta de búsqueda SICS introduciendo el ticker. Para consultas de reclasificación, la Fundación IFRS indica el correo `SICS@ifrs.org`. [VERIFICADO] [35]
- Si las operaciones abarcan varios sectores, la organización **debería considerar aplicar más de un estándar**. Si el modelo de negocio es atípico y no encaja en la clasificación, puede tomar temas de divulgación y métricas de varias industrias con actividades similares, eligiendo las que mejor comuniquen información material a los inversionistas. [VERIFICADO] [35][36]
- Cobertura: **77 industrias SICS**, agrupadas en **11 sectores**. [VERIFICADO] [21][35]

**Procedimiento sugerido para el skill (no oficial, derivado):**
1. Identificar el/los flujo(s) principal(es) de ingresos y las actividades productivas reales.
2. Buscar la empresa (o una comparable cotizada) en la herramienta SICS; si no existe, ubicar la industria por descripción de actividad.
3. Si más del ~20 % de los ingresos o de los impactos provienen de otra industria, evaluar un segundo estándar.
4. Documentar la elección y su justificación en el expediente de auditoría (ver sección 6).

### 4.2 Estructura de un estándar SASB

Cada estándar SASB tiene cuatro componentes [VERIFICADO] [35]:

| Componente | Qué es | Promedio por industria |
|---|---|---|
| **Disclosure Topics** (temas de divulgación) | Riesgos u oportunidades de sostenibilidad específicos de esa industria. | ~6 |
| **Metrics** (métricas contables) | Medidas estandarizadas, cuantitativas o cualitativas, asociadas a cada tema. | ~13 |
| **Technical Protocols** (protocolos técnicos) | Orientación sobre definiciones, alcance, implementación y presentación, para que la compilación sea consistente. | — |
| **Activity Metrics** (métricas de actividad) | Medidas cuantitativas de la escala operativa, usadas para **normalizar** los datos y permitir comparación. | — |

Además existen las **General Issue Categories**, versión agnóstica de industria de los temas de divulgación, que permiten comparar entre industrias distintas. [VERIFICADO] [36]

**Códigos:** cada métrica lleva un código con prefijo de industria SICS (por ejemplo, la familia `RT-xx-yyy` para Resource Transformation, `EM-xx` para Extractives & Minerals Processing). No se listan aquí códigos concretos porque deben tomarse del estándar de la industria específica. **[NO VERIFICADO en detalle]** — el motor debe leerlos del PDF de la industria correspondiente.

### 4.3 Relación con NIIF S1 / S2

- Los requisitos por industria del **Apéndice B de NIIF S2** derivan de los SASB, en gran medida sin cambios. [VERIFICADO] [20]
- **NIIF S1** exige considerar los temas y métricas de los SASB al identificar riesgos, oportunidades y divulgaciones cuando no hay una norma NIIF específica; la Fundación IFRS remite a la guía de acompañamiento de NIIF S1 (párrafos IG11–IG24 e IE1–IE15). [VERIFICADO] [35]
- Los SASB están siendo revisados para mejorar su aplicabilidad internacional (proyecto en curso 2025–2026). [VERIFICADO] [20][22]

### 4.4 Condiciones de uso (crítico para un proyecto de código abierto)

- El **uso no comercial** —por ejemplo, para preparar las divulgaciones corporativas de la propia empresa— **es gratuito**. [VERIFICADO] [37]
- **Otros usos, incluida la integración en productos y servicios, requieren una licencia de la Fundación IFRS.** El contenido licenciable incluye **NIIF S1, NIIF S2, los estándares SASB y el propio SICS®**. [VERIFICADO] [37]

> 🚨 **Riesgo legal para "Agentes ESG":** incorporar el texto, las tablas de métricas o los códigos SASB/SICS dentro de skills o de un motor Python distribuido puede constituir "integración en un producto o servicio" y exigir licencia de la Fundación IFRS. Recomendación: (a) no empaquetar el contenido de los estándares; (b) referenciar por código y enlazar al documento oficial; (c) consultar a `licences@ifrs.org` antes de distribuir mapeos completos. **[SECUNDARIO — interpretación propia de los términos publicados; requiere validación legal]**

---

## 5. ESRS / CSRD y VSME (Unión Europea)

### 5.1 El Set 1 de ESRS (Reglamento Delegado (UE) 2023/2772)

**Reglamento Delegado (UE) 2023/2772 de la Comisión, de 31 de julio de 2023**, que completa la Directiva 2013/34/UE en lo relativo a las normas de información sobre sostenibilidad. Publicado en el DOUE el **22 de diciembre de 2023**; primera aplicación para ejercicios iniciados a partir del **1 de enero de 2024**. [VERIFICADO] [38]

Estructura del Anexo I — **12 normas** [VERIFICADO] [38]:

| Grupo | Norma | Título | Contenido (resumen propio) |
|---|---|---|---|
| **Transversales** | ESRS 1 | General requirements | Arquitectura general: doble materialidad, cadena de valor, horizontes temporales, debida diligencia, estructura de la declaración de sostenibilidad, incorporación por referencia y disposiciones transitorias. No contiene requisitos de divulgación propios. |
| | ESRS 2 | General disclosures | Divulgaciones obligatorias **para todas** las empresas en ámbito, sea cual sea el resultado de la materialidad: base de preparación, gobernanza (GOV), estrategia (SBM), gestión de impactos/riesgos/oportunidades (IRO) y métricas y objetivos (MDR). |
| **Ambientales** | ESRS E1 | Climate change | Plan de transición, políticas, acciones, metas, consumo de energía, emisiones brutas Alcances 1-2-3 y totales, remociones y proyectos de mitigación, créditos de carbono, precio interno del carbono, efectos financieros de riesgos físicos y de transición. |
| | ESRS E2 | Pollution | Contaminación del aire, agua y suelo; sustancias preocupantes y de muy alta preocupación; microplásticos. |
| | ESRS E3 | Water and marine resources | Consumo, extracción y vertido de agua; áreas de estrés hídrico; recursos marinos. |
| | ESRS E4 | Biodiversity and ecosystems | Plan de transición para biodiversidad, sitios en o cerca de áreas sensibles, motores de pérdida, estado de especies y ecosistemas, servicios ecosistémicos. |
| | ESRS E5 | Resource use and circular economy | Entradas y salidas de recursos, residuos, circularidad. |
| **Sociales** | ESRS S1 | Own workforce | Trabajadores propios: condiciones laborales, igualdad, otros derechos; incluye métricas de plantilla, brecha salarial, negociación colectiva, salud y seguridad, formación. |
| | ESRS S2 | Workers in the value chain | Trabajadores de la cadena de valor. |
| | ESRS S3 | Affected communities | Comunidades afectadas, incluidos pueblos indígenas. |
| | ESRS S4 | Consumers and end-users | Consumidores y usuarios finales. |
| **Gobernanza** | ESRS G1 | Business conduct | Conducta empresarial: cultura corporativa, protección de denunciantes, anticorrupción y soborno, actividad de lobby, prácticas de pago a proveedores. |

El Anexo II del Reglamento contiene el glosario/lista de acrónimos y definiciones. [VERIFICADO] [38]

### 5.2 Doble materialidad explicada

La doble materialidad es la regla de decisión que determina **qué** debe reportar la empresa. Un asunto de sostenibilidad es material si lo es por **cualquiera** de estas dos vías (basta con una) [VERIFICADO — concepto de ESRS 1; explicación propia] [38][39]:

| Perspectiva | Pregunta que responde | Criterios típicos |
|---|---|---|
| **Materialidad de impacto** ("inside-out") | ¿Qué efectos tiene la empresa, a través de sus operaciones y de su cadena de valor, sobre las personas y el medio ambiente? | Gravedad del impacto (escala, alcance, carácter irremediable) y, para impactos potenciales, **probabilidad**. Para impactos negativos sobre derechos humanos, la gravedad prima sobre la probabilidad. |
| **Materialidad financiera** ("outside-in") | ¿Qué riesgos y oportunidades de sostenibilidad pueden afectar los flujos de efectivo, el desempeño, la posición financiera, el costo de capital o el acceso a financiación de la empresa en el corto, mediano o largo plazo? | Magnitud potencial del efecto financiero × probabilidad de ocurrencia. |

Puntos prácticos para el skill de materialidad:

1. Las dos perspectivas están **conectadas**: un impacto material hoy suele convertirse en riesgo financiero mañana (vía regulación, reputación, litigio o costo de insumos).
2. La evaluación debe cubrir **toda la cadena de valor**, no solo las operaciones propias.
3. El resultado de la evaluación de doble materialidad determina qué ESRS temáticos se aplican; **ESRS 2 se reporta siempre**.
4. A diferencia de NIIF S1/S2, que solo miran la materialidad financiera, ESRS obliga a las dos. Un mismo dato puede ser material bajo ESRS y no bajo NIIF S2, y viceversa.

> Contraste rápido para el agente: **GRI** = materialidad de impacto; **NIIF S1/S2** = materialidad financiera; **ESRS** = ambas.

### 5.3 Simplificación 2025–2026: Omnibus I y los ESRS revisados

#### Directiva (UE) 2026/470 ("Omnibus I")

| Elemento | Dato | Etiqueta |
|---|---|---|
| Título | Directiva (UE) 2026/470 del Parlamento Europeo y del Consejo, de **24 de febrero de 2026**, por la que se modifican las Directivas 2006/43/CE, 2013/34/UE, (UE) 2022/2464 y (UE) 2024/1760 | [VERIFICADO] [40] |
| Publicación en el DOUE | **26 de febrero de 2026** | [VERIFICADO] [40] |
| Entrada en vigor | **18 de marzo de 2026** | [VERIFICADO] [41] |
| Plazo de transposición | **19 de marzo de 2027** | [VERIFICADO] [41] |
| Nuevo umbral CSRD | Empresas que superen **450.000.000 EUR de volumen de negocios neto** **y** una media de **1.000 empleados** en el ejercicio | [VERIFICADO] [40] |
| Aplicación de los nuevos artículos 19a/29a | Ejercicios iniciados a partir del **1 de enero de 2027** (primeros informes en 2028) | [VERIFICADO] [40] |
| Nuevo umbral CSDDD (Dir. 2024/1760) | **5.000 empleados** y **1.500.000.000 EUR** de volumen de negocios mundial neto | [VERIFICADO] [40] |
| Aplicación CSDDD | **26 de julio de 2029** (fecha única para todas las empresas en ámbito); directrices de la Comisión antes del **26 de julio de 2027** | [VERIFICADO] [40] |
| Responsabilidad civil CSDDD | Se elimina el régimen armonizado a nivel de la Unión; rigen las normas nacionales. Se suprimen las disposiciones sobre plan de transición climática. Tope de sanción: **3 % del volumen de negocios mundial neto** | [VERIFICADO] [40] |
| **Aseguramiento** | La Comisión debe adoptar normas de **aseguramiento limitado** antes del **1 de julio de 2027** (aplazado desde el 1 de octubre de 2026). **Se elimina por completo** el mandato de adoptar normas de aseguramiento razonable | [VERIFICADO] [40] |
| **Normas sectoriales** | Se **suprime** la facultad de la Comisión de adoptar normas sectoriales obligatorias; en su lugar, orientación y plantillas **no vinculantes** | [VERIFICADO] [40] |
| **Tope de cadena de valor** ("value chain cap") | Se crean "empresas protegidas" (menos de 1.000 empleados) con derecho a **rechazar** solicitudes de información que excedan lo previsto en la norma voluntaria; la empresa que reporta debe informarles de ese derecho. Basta una autodeclaración para acreditar el tamaño | [VERIFICADO] [40] |
| Omisiones permitidas | Información que perjudicaría gravemente la posición comercial, secretos comerciales (Dir. 2016/943), información clasificada o protegida, o cuya divulgación amenace la privacidad o la seguridad | [VERIFICADO] [40] |

#### Reglamento Delegado de ESRS revisados ("ESRS 2026")

| Elemento | Dato | Etiqueta |
|---|---|---|
| Documento | **C(2026) 5010 final** — Reglamento Delegado de la Comisión por el que se modifica el Reglamento Delegado (UE) 2023/2772 en lo relativo a la simplificación de determinadas normas de información sobre sostenibilidad | [VERIFICADO] [41] |
| Fecha de adopción | **3 de julio de 2026** | [VERIFICADO] [41] |
| Asesoramiento técnico de EFRAG | Entregado el **2 de diciembre de 2025**; análisis costo-beneficio y documentos de apoyo el **23 de diciembre de 2025**. Consulta pública de EFRAG sobre los borradores simplificados: **29 de julio – 29 de septiembre de 2025** | [VERIFICADO] [41] |
| Consulta pública de la Comisión sobre el borrador | Borrador publicado el **6 de mayo de 2026**; consulta cerrada el **3 de junio de 2026** | [SECUNDARIO] [42] |
| Qué hace | Sustituye íntegramente el Anexo I y el Anexo II del Reglamento 2023/2772 | [VERIFICADO] [41] |
| Aplicación obligatoria | Ejercicios iniciados a partir del **1 de enero de 2027** | [VERIFICADO] [41] |
| Aplicación anticipada | Permitida para ejercicios iniciados entre el **1 de enero y el 31 de diciembre de 2026** | [VERIFICADO] [41] |
| Entrada en vigor | Fecha de adopción + 4 meses + 1 semana (el texto adoptado deja la fecha exacta a la Oficina de Publicaciones). Está sujeto a un periodo de escrutinio del Parlamento y el Consejo de **2 meses, prorrogable 2 meses más**; si no hay objeción, se publica en el DOUE | [VERIFICADO texto del acto] [41] · [SECUNDARIO para el mecanismo de escrutinio] [42] |
| Reducción de datapoints | **−61 % de datapoints obligatorios** frente al Set 1 de 2023 | [VERIFICADO] [41] |
| Ahorro estimado (EFRAG) | Ahorro medio del **34 %** de los costos base en cinco años (28 % en 2027, 38 % en 2028, 33–36 % desde 2029); acumulado de **3.700 millones EUR**, hasta **~4.700 millones EUR** (≈44 %) incluyendo efectos de cadena de valor, 2027–2031 | [VERIFICADO] [41] |

**Cambios de fondo más relevantes (resumen propio)** [VERIFICADO] [41]:

- **Materialidad**: enfoque más proporcionado y basado en principios. El texto pasa de "no está obligada a reportar" a "**no deberá** reportar" información no material, salvo circunstancias definidas. Se refuerza el enfoque **descendente (top-down)** para evitar evaluar la materialidad de cada impacto, riesgo u oportunidad individual.
- **Presentación fiel (fair presentation)**: se aclara que aplica a la declaración de sostenibilidad **en conjunto**, no a cada dato individual.
- **Agregación/desagregación**: mayor discreción sobre contextos geográficos; el nivel de desagregación usado para evaluar materialidad no obliga a reportar a ese mismo nivel.
- **Efectos financieros previstos**: se admite explícitamente que implican estimaciones actualizables sin que ello sea un "error"; un año adicional de introducción gradual para información cualitativa y cuantitativa.
- **Emisiones de GEI**: se permite elegir entre el enfoque de **control financiero** o **control operacional** al definir el límite de reporte (mayor alineación con las normas globales).
- **Planes de transición climática**: quien reporte un plan con metas no compatibles con 1,5 °C debe **declararlo expresamente**.
- **Microplásticos**: la exigencia se limita a microplásticos **primarios**.
- **Contaminantes**: la decisión sobre qué contaminantes son materiales se toma mediante evaluación de gestión según actividad y sector.
- **Sustancias de muy alta preocupación**: nueva introducción gradual de un año para usuarios de artículos que las contengan.

**Régimen transitorio para ejercicios que comiencen entre el 1-ene-2026 y el 31-dic-2026** — la empresa puede elegir [VERIFICADO] [41]:

(a) los ESRS del Anexo I de 2023/2772 tal como fue modificado por última vez por el Reglamento Delegado (UE) **2025/1416** (de 11 de julio de 2025, sobre aplazamiento de la fecha de aplicación de ciertos requisitos), **o** los ESRS del nuevo Anexo I; **o**
(b) los ESRS de 2023/2772 (versión 2025/1416) **con** determinados alivios del nuevo Anexo I, entre ellos: ESRS 1 §27 (enfoque descendente de la evaluación de doble materialidad), ESRS 1 §§32-33 (costo/esfuerzo indebido y limitación de cadena de valor) y ESRS 1 §§74-75 (nuevas adquisiciones y enajenaciones).

En cualquier caso, la empresa debe **declarar expresamente en su declaración de sostenibilidad qué versión aplica**. [VERIFICADO] [41]

> ⚠️ Implicación de diseño para el motor: hay que soportar **tres variantes** de ESRS para el ejercicio 2026 (2023/2772 original; 2023/2772 + alivios; ESRS 2026) y una sola desde 2027. Modelar la versión como un parámetro explícito del reporte.

### 5.4 VSME: la norma voluntaria para pymes

| Elemento | Dato | Etiqueta |
|---|---|---|
| Origen | EFRAG desarrolla el VSME tras la **SME Relief Package** de la Comisión (12 de septiembre de 2023, Acción 14). Entrega la norma a la Comisión en **diciembre de 2024** | [VERIFICADO] [43] |
| Instrumento vigente | **Recomendación de la Comisión C(2025) 4984 final, de 30 de julio de 2025**, sobre una norma voluntaria de información en materia de sostenibilidad para pequeñas y medianas empresas. Referencia como Recomendación (UE) 2025/1710 | [VERIFICADO el documento C(2025) 4984] [43] · [SECUNDARIO el número 2025/1710] [44] |
| Naturaleza jurídica | **Recomendación** (art. 292 TFUE): **no vinculante**. Es una "solución intermedia" hasta que se adopte una norma voluntaria por acto delegado bajo el paquete Omnibus | [VERIFICADO] [43] |
| Destinatarios | Pymes **no cotizadas** y microempresas que quieran reportar voluntariamente; y quienes les piden información (grandes empresas e intermediarios financieros), a quienes se les pide limitar sus peticiones a lo coherente con el VSME | [VERIFICADO] [43] |
| Aseguramiento | **No se exige**: basta una **autodeclaración** de la pyme. Se considera proporcionado | [VERIFICADO] [43] |
| Anexos | Anexo I: módulos básico y comprehensivo. Anexo II: guía práctica complementaria de EFRAG | [VERIFICADO] [43] |
| Relación con Omnibus | El acto delegado que sustituirá esta Recomendación se basará en el VSME, pero su contenido **puede diferir**; define el "tope de cadena de valor" para empresas de hasta 1.000 empleados. La Comisión adoptó un acto delegado con una **norma voluntaria** el **3 de julio de 2026**, junto con los ESRS revisados | [VERIFICADO] [43][45] |

**Regla de uso:** reportar el **módulo básico es prerrequisito** para reportar el módulo comprehensivo. Para microempresas el módulo básico es el "enfoque objetivo" (pueden usar solo partes de él); para pequeñas y medianas es el "requisito mínimo". [VERIFICADO] [43]

#### Módulo básico — B1 a B11 [VERIFICADO — Anexo I de C(2025) 4984] [45]

| Código | Título (original) | Contenido (resumen propio) |
|---|---|---|
| B1 | Basis for preparation | Base de preparación: si se usa solo el módulo básico o también el comprehensivo, base individual o consolidada, entidades incluidas, sector, países, sitios, certificaciones. |
| B2 | Practices, policies and future initiatives for transitioning towards a more sustainable economy | Prácticas, políticas e iniciativas futuras para la transición a una economía más sostenible. |
| B3 | Energy and greenhouse gas emissions | Consumo de energía y emisiones de GEI (Alcances 1 y 2; Alcance 3 si procede). |
| B4 | Pollution of air, water and soil | Contaminación del aire, el agua y el suelo (cuando exista obligación legal de informarla). |
| B5 | Biodiversity | Biodiversidad: sitios en o cerca de áreas sensibles y uso del suelo. |
| B6 | Water | Captación y consumo de agua. |
| B7 | Resource use, circular economy and waste management | Uso de recursos, economía circular y gestión de residuos. |
| B8 | Workforce — General characteristics | Plantilla: características generales (número, tipo de contrato, país, género). |
| B9 | Workforce — Health and safety | Salud y seguridad: accidentes y fatalidades. |
| B10 | Workforce — Remuneration, collective bargaining and training | Remuneración (salario mínimo, brecha de género), negociación colectiva y formación. |
| B11 | Convictions and fines for corruption and bribery | Condenas y multas por corrupción y soborno. |

#### Módulo comprehensivo — C1 a C9 [VERIFICADO — Anexo I de C(2025) 4984] [45]

| Código | Título (original) | Contenido (resumen propio) |
|---|---|---|
| C1 | Strategy: Business Model and Sustainability-Related Initiatives | Estrategia: modelo de negocio e iniciativas relacionadas con la sostenibilidad. |
| C2 | Description of practices, policies and future initiatives for transitioning towards a more sustainable economy | Descripción ampliada de prácticas, políticas e iniciativas de transición. |
| C3 | GHG reduction targets and climate transition | Metas de reducción de GEI y transición climática. |
| C4 | Climate risks | Riesgos climáticos (físicos y de transición). |
| C5 | Additional (general) workforce characteristics | Características adicionales de la plantilla. |
| C6 | Additional own workforce information — Human rights policies and processes | Políticas y procesos de derechos humanos aplicados a la plantilla propia. |
| C7 | Severe negative human rights incidents | Incidentes graves de derechos humanos (incluida la cadena de valor). |
| C8 | Revenues from certain activities and exclusion from EU reference benchmarks | Ingresos de determinadas actividades controvertidas y exclusión de los índices de referencia de la UE. |
| C9 | Gender diversity ratio in the governance body | Ratio de diversidad de género en el órgano de gobierno. |

> Uso recomendado para "Agentes ESG": el VSME es el **punto de entrada natural** para pymes de Chile y Perú que reciben cuestionarios de bancos o de clientes grandes de la UE. No es obligatorio en LatAm, pero permite responder con una sola estructura y es compatible con el tope de cadena de valor europeo.

---

## 6. Aseguramiento (assurance) de información de sostenibilidad

### 6.1 Mapa de normas

| Norma | Título | Vigencia | Estado |
|---|---|---|---|
| **ISAE 3000 (Revisada)** | Assurance Engagements Other than Audits or Reviews of Historical Financial Information | Encargos cuyo **informe de aseguramiento lleve fecha igual o posterior al 15 de diciembre de 2015** | Vigente. Ha sido la norma de referencia para el aseguramiento de reportes de sostenibilidad. [VERIFICADO] [46] |
| **ISAE 3410** | Assurance Engagements on Greenhouse Gas Statements | Informes que cubran **periodos terminados el 30 de septiembre de 2013 o después** | **Se retira el 15 de diciembre de 2026**, fecha en que entra en vigor ISSA 5000. [VERIFICADO] [47] |
| **ISSA 5000** | General Requirements for Sustainability Assurance Engagements | **Periodos que comiencen el 15 de diciembre de 2026 o después**; se permite y se fomenta la adopción anticipada | Aprobada y certificada en 2024; **publicada el 12 de noviembre de 2024**. [VERIFICADO] [48][49][50] |
| **IESSA** | International Ethics Standards for Sustainability Assurance (IESBA) | Misma fecha: periodos que comiencen el **15 de diciembre de 2026** o después, en las jurisdicciones que las adopten | Emitida en enero de 2025 junto con ISSA 5000 en un anuncio conjunto IAASB-IESBA. [VERIFICADO] [49][51] |

**Características de ISSA 5000 (resumen propio):**
- Norma **autónoma y completa**, apta para **cualquier** encargo de aseguramiento de sostenibilidad. [VERIFICADO] [50]
- **Agnóstica de profesión**: puede ser aplicada por contadores públicos y por proveedores de aseguramiento no contables. [VERIFICADO] [48]
- **Neutral respecto del marco**: sirve para información preparada bajo ESRS, NIIF S1/S2, GRI u otros. [VERIFICADO] [48][50]
- Cubre **aseguramiento limitado y razonable**, y se aplica tanto a encargos **obligatorios** como **voluntarios**. [VERIFICADO] [48]
- ISAE 3000 (Revisada) sigue existiendo para materias **distintas** de sostenibilidad. **[NO VERIFICADO en la fuente primaria]** — confirmar en el texto de ISSA 5000/FAQ del IAASB.

> ⚠️ Contexto UE: la Directiva (UE) 2026/470 aplazó al **1 de julio de 2027** la adopción por la Comisión de normas de **aseguramiento limitado**, y **eliminó** el mandato de adoptar normas de aseguramiento **razonable**. Hasta entonces rigen las normas nacionales de aseguramiento de cada Estado miembro. [VERIFICADO] [40]

### 6.2 Aseguramiento limitado vs razonable

| Dimensión | Aseguramiento **limitado** | Aseguramiento **razonable** |
|---|---|---|
| Riesgo del encargo | Se reduce a un nivel aceptable, pero **mayor** que en el razonable | Se reduce a un nivel **aceptablemente bajo** |
| Alcance de los procedimientos | Procedimientos **limitados** respecto de los necesarios en un encargo razonable, pero planificados para obtener un nivel de seguridad **significativo** (meaningful) | Procedimientos suficientes para respaldar una opinión positiva |
| Forma de la conclusión | **Negativa** ("no se ha puesto de manifiesto nada que nos haga pensar que...") | **Positiva** ("en nuestra opinión, la información está preparada, en todos los aspectos materiales, de conformidad con...") |
| Nivel de seguridad | **Sustancialmente menor** que el razonable | Alto (no absoluto) |
| Costo y esfuerzo típicos | Menor | Bastante mayor (pruebas de controles, muestreo sustantivo, recálculos) |

[VERIFICADO — definiciones de ISAE 3000 (Revisada)] [46]

**Implicación para el producto:** la mayoría de los reportes de sostenibilidad en LatAm y la UE parten con aseguramiento **limitado**. El salto a razonable exige que los controles internos sobre los datos ESG sean **auditables**, no solo que el número final sea correcto. De ahí la importancia de la sección siguiente.

### 6.3 Principios ALCOA+ aplicados a la evidencia ESG

ALCOA+ es un marco de **integridad de datos** procedente de la regulación farmacéutica (GxP). La guía oficial de la MHRA del Reino Unido lo define así [VERIFICADO] [52]:

| Letra | Principio | Qué significa (resumen propio) | Traducción al expediente ESG |
|---|---|---|---|
| **A** | Attributable (atribuible) | Se sabe **quién** generó o modificó el dato y **cuándo** | Cada factor de emisión, factura y lectura de medidor lleva responsable identificado y fecha |
| **L** | Legible (legible) | El dato es legible y permanece legible durante todo su ciclo de vida | Nada de fotos borrosas ni PDFs escaneados sin OCR; nombres de archivo normalizados |
| **C** | Contemporaneous (contemporáneo) | Se registra **en el momento** en que ocurre la actividad | Las lecturas se cargan en el periodo, no reconstruidas a fin de año |
| **O** | Original (original) | Se conserva el registro original o una copia certificada verdadera | La factura del distribuidor eléctrico, no la hoja de cálculo intermedia |
| **A** | Accurate (exacto) | Correcto, completo, veraz y fiable | Unidades, conversiones y factores verificados; errores documentados y corregidos con traza |
| **+C** | Complete | Incluye todos los datos, reprocesos y metadatos | Todas las sedes y meses; las exclusiones se justifican |
| **+C** | Consistent | Secuencia cronológica y metodología coherentes | Misma metodología año a año; cambios documentados como reexpresión |
| **+E** | Enduring | Duradero durante todo el periodo de retención | Almacenamiento estable; no solo en el correo de una persona |
| **+A** | Available | Accesible para revisión y auditoría durante el periodo de retención | El auditor puede llegar del número del reporte al documento fuente en pocos pasos |

> [SECUNDARIO — aplicación a ESG] ALCOA+ no es una norma de sostenibilidad; su traslado al ámbito ESG es una buena práctica ampliamente usada por firmas de auditoría, pero **no está codificada en ISSA 5000 ni en ESRS**. Presentarla como recomendación, no como requisito normativo.

### 6.4 Qué contiene un expediente listo para auditoría

Lista de trabajo derivada de los requisitos de ISAE 3000 (Revisada)/ISSA 5000, del principio de **verificabilidad** de GRI 1 y de la exigencia de **exactitud** de ESRS. **[SECUNDARIO — síntesis propia]**

| Bloque | Contenido |
|---|---|
| **1. Gobernanza del reporte** | Quién aprueba el informe (en GRI, divulgación 2-14); acta del órgano de gobierno; organigrama del equipo de sostenibilidad; matriz RACI por indicador |
| **2. Alcance y límites** | Entidades incluidas y excluidas y su conciliación con el perímetro de los estados financieros (GRI 2-2; NIIF S1); enfoque de consolidación de GEI elegido (control operacional o financiero) y su justificación |
| **3. Materialidad** | Metodología, lista de grupos de interés consultados, evidencias de consulta, umbrales usados, matriz o lista priorizada, acta de aprobación (GRI 3-1/3-2; ESRS 1) |
| **4. Por cada indicador: ficha técnica** | Definición, unidad, fórmula, fuente del dato, sistema de origen, responsable, frecuencia, controles aplicados, factores de emisión con versión y fuente, supuestos y estimaciones |
| **5. Trazabilidad del dato** | Cadena completa: documento fuente → hoja de cálculo o sistema → agregación → cifra publicada. Cada salto debe ser reproducible |
| **6. Reexpresiones** | Cifras del año anterior modificadas, motivo, efecto y aprobación (GRI 2-4) |
| **7. Estimaciones y su incertidumbre** | Qué se estimó, con qué técnica, qué supuestos y qué limitaciones (principio de exactitud de GRI 1) |
| **8. Metas** | Año base, alcance cubierto, metodología de fijación, evidencia de validación externa si la hay (por ejemplo SBTi), cálculo del progreso |
| **9. Aseguramiento** | Alcance del encargo, norma aplicada, tipo (limitado/razonable), independencia del proveedor, carta de encargo, hallazgos y su resolución (GRI 2-5) |
| **10. Índice y mapeo** | Índice de contenidos GRI, tabla de correspondencia GRI ↔ ESRS ↔ NIIF S2, y ubicación de cada dato |
| **11. Control de versiones** | Registro de cambios del informe y de los archivos de cálculo; bloqueo de la versión publicada |

---

## 7. SBTi: metas climáticas basadas en ciencia

### 7.1 Estado de los estándares a septiembre de 2026

| Documento | Versión vigente | Fecha | Estado |
|---|---|---|---|
| **Corporate Net-Zero Standard (CNZS)** | **V1.3.1** | Abril de 2026 (en vigor desde el 14 de abril de 2026) | Vigente para validaciones hasta el **31 de enero de 2028** [VERIFICADO] [53][54] |
| **Corporate Net-Zero Standard** | **V2.0** | Publicada el **11 de junio de 2026** | **Entra en vigor el 31 de enero de 2027**. Validaciones contra V2.0 disponibles desde el **Q1 2027**; obligatoria para toda nueva presentación desde el **1 de febrero de 2028** [VERIFICADO] [54][55] |
| **Corporate Near-Term Criteria** | **V5.3.1** | Abril de 2026 (en vigor desde el 14 de abril de 2026) | Vigente [VERIFICADO] [53] |
| **FLAG Guidance** | **V1.2** | Marzo de 2026 | Vigente; alineada con el GHG Protocol Land Sector and Removals Standard [SECUNDARIO — página web de SBTi] [56] |

**Cronología de V2.0** [VERIFICADO] [54]:
- Revisión desarrollada entre **abril de 2024 y mayo de 2026**.
- Primera consulta pública: **marzo–junio de 2025**. Segunda consulta: **noviembre–diciembre de 2025**.
- Aprobada por el Consejo Técnico el **8 de mayo de 2026**; adoptada por el Consejo de Administración el **21 de mayo de 2026**.
- Escala del cambio: **42 % de las secciones de V2.0 son enteramente nuevas**; 58 % son modificaciones o ampliaciones. No existe un mapeo criterio a criterio entre V1.3.1 y V2.0.

### 7.2 Criterios clave de las metas de corto plazo (V1.3.1 / Near-Term Criteria V5.3.1)

| Criterio | Contenido | Etiqueta |
|---|---|---|
| **C13 — Años base y meta** | Las metas absolutas y de intensidad deben cubrir **mínimo 5 años y máximo 10 años** desde la fecha de presentación a validación. El año base **no puede ser anterior a 2015**. Alcances 1 y 2 deben usar el mismo año base. No se aceptan años base promedio plurianuales (salvo que lo indique la guía sectorial) | [VERIFICADO] [53] |
| **R7 — Año meta 2030** | Se recomienda elegir 2030 como año meta; si se aplica, la empresa queda **exenta del requisito de 5–10 años** de C13 | [VERIFICADO] [53] |
| **C1 — Límite organizacional** | Presentar al nivel de matriz o grupo, no de filial; la matriz incluye las emisiones de todas las filiales dentro de su enfoque de consolidación | [VERIFICADO] [53] |
| **C2 — Gases** | Los **siete** GEI del GHG Protocol: CO2, CH4, N2O, HFC, PFC, SF6 y NF3 | [VERIFICADO] [53] |
| **C3 — Alcances 1 y 2** | Cobertura **de toda la empresa** | [VERIFICADO] [53] |
| **C4 — Umbral de Alcance 3** | Si el Alcance 3 relevante representa **40 % o más** del total de Alcances 1+2+3, **debe** incluirse en las metas de corto plazo. Además, toda empresa que venda o distribuya gas natural u otros combustibles fósiles debe fijar metas separadas de Alcance 3 por uso de productos vendidos, **sin importar** el porcentaje | [VERIFICADO] [53] |
| **C5 — Exclusiones** | No más del **5 %** de las emisiones combinadas de Alcances 1+2 y no más del **5 %** del inventario total de Alcance 3 | [VERIFICADO] [53] |
| **C6 — Cobertura de Alcance 3** | Las metas de reducción y/o de involucramiento de proveedores o clientes deben cubrir en conjunto al menos el **67 %** del total de Alcance 3 reportado y excluido | [VERIFICADO] [53] |
| **C11 — Créditos de carbono** | **No cuentan** como reducciones para el progreso de las metas de corto plazo. Solo sirven para neutralizar emisiones residuales o para financiar mitigación adicional fuera de la meta | [VERIFICADO] [53] |
| **C12 — Emisiones evitadas** | Pertenecen a un sistema contable distinto; **no cuentan** para las metas | [VERIFICADO] [53] |
| **C15–C17 — Ambición Alcances 1 y 2** | Como mínimo, consistentes con **1,5 °C**. Metas absolutas: al menos tan ambiciosas como el mínimo del rango aprobado de escenarios 1,5 °C. Metas de intensidad: solo si se modelan con una ruta sectorial 1,5 °C aprobada | [VERIFICADO] [53] |
| **C18 — Ambición Alcance 3** | Como mínimo, **muy por debajo de 2 °C** (well-below 2 °C) | [VERIFICADO] [53] |
| **C20 — Metas combinadas** | Al presentar una meta combinada, la porción de Alcance 1+2 debe cumplir al menos 1,5 °C y la porción de Alcance 3 al menos "muy por debajo de 2 °C" | [VERIFICADO] [53] |
| **C21 — Electricidad renovable (solo Alcance 2)** | Alternativa aceptable a la meta de reducción de Alcance 2: contratación activa de electricidad renovable. Umbrales identificados por SBTi, en línea con RE100: **80 % al 2025 y 100 % al 2030**; para metas de largo plazo hay que mantener el 100 % más allá de 2030 | [VERIFICADO] [53] |

### 7.3 Tasas de reducción: la "regla del 4,2 %" y la meta de largo plazo

Con la **ruta transversal** (cross-sector pathway) del método de **contracción absoluta** [VERIFICADO] [54]:

| Parámetro | Valor |
|---|---|
| Tasa lineal anual mínima, **Alcances 1 y 2**, corto plazo, 1,5 °C | **4,2 % anual** |
| Tasa lineal anual mínima, **Alcance 3**, corto plazo, muy por debajo de 2 °C | **2,5 % anual** |
| Reducción mínima de la **meta de largo plazo**, todos los alcances | **90 %** |
| Año de referencia de la ruta transversal para el 90 % | **2050** (niveles de 2020) |

> ⚠️ **Matiz crítico que suele omitirse y que el motor debe implementar bien:** desde V1.3/V1.3.1 la tasa **no es un 4,2 % fijo**. Es **dependiente del año base** y se ajusta dinámicamente según el tiempo que resta entre el año base de la empresa y el año net-zero de la ruta (o el año net-zero propio de la empresa, si es anterior). **La tasa aumenta cuando el plazo se acorta**: con años base más recientes y/o años net-zero más tempranos, la tasa exigida es mayor que 4,2 %. El 4,2 % corresponde al caso de referencia del año base 2020 con net-zero en 2050. [VERIFICADO] [54]

> ⚠️ **Ajuste de Alcance 2:** para limitar emisiones acumuladas, en las metas de Alcance 2 de corto plazo y en las combinadas 1+2 se aplica un ajuste de cálculo que asume que el **Alcance 2 llega a cero en 2040** (siguiendo el supuesto de descarbonización del sistema eléctrico global). Los supuestos de Alcance 1 no cambian: 90 % de reducción a 2050 o antes. La ambición de una meta combinada 1+2 se calcula con una **tasa promedio ponderada** según el inventario 1+2 del año más reciente. [VERIFICADO] [54]

### 7.4 Ruta pymes

- Bajo **V1.3.1**, las pymes pueden elegir entre el **Corporate Net-Zero Standard completo** o la **ruta simplificada para pymes** (SME route), en la que parte del contenido del estándar no aplica. Los criterios corporativos de corto plazo (V5.3.1) **no aplican** a pymes ni a instituciones financieras: las pymes pueden usar la ruta SME o la ruta de validación regular. [VERIFICADO] [53][54]
- Bajo **V2.0**, la ruta SME separada **desaparece**: se sustituye por una **categorización formal de empresas (Categoría A y Categoría B)** con obligaciones diferenciadas según **facturación, geografía, emisiones y número de empleados**. [VERIFICADO] [54]
- Los umbrales numéricos exactos que separan Categoría A de Categoría B, y los requisitos concretos de la ruta SME de V1.3.1 (número de empleados, si se exige meta de Alcance 3, tarifas), **[NO VERIFICADO]** — están en el texto de CNZS V2.0, en la definición de pyme de SBTi y en las FAQ de pymes; requieren lectura directa.

### 7.5 Guía FLAG (Forest, Land and Agriculture)

| Aspecto | Contenido | Etiqueta |
|---|---|---|
| Quién **debe** fijar metas FLAG | (1) Empresas cuyas emisiones FLAG sumen **20 % o más** del total en todos los alcances; y (2) empresas de estos sectores: Forest and Paper Products (silvicultura, madera, pulpa y papel, caucho); Food Production – Agricultural Production; Food Production – Animal Source; Food and Beverage Processing; Food and Staples Retailing; Tobacco | [VERIFICADO] [53] |
| Relación con las metas de energía/industria | Las metas FLAG son **complementarias y separadas** de las metas científicas que cubren emisiones no-FLAG | [VERIFICADO] [53] |
| Cobertura mínima | Las metas FLAG de corto plazo deben cubrir al menos **95 % de las emisiones FLAG de Alcances 1 y 2** y al menos **67 % de las emisiones FLAG de Alcance 3** | [VERIFICADO] [53] |
| Métodos | Reducción absoluta sectorial (corto plazo y largo plazo — este último solo agricultura) y **rutas por materia prima** para metas de intensidad de corto plazo | [VERIFICADO] [53] |
| Rutas por materia prima disponibles (10) | Carne de vacuno, pollo, lácteos, cuero, maíz, aceite de palma, cerdo, arroz, soya y trigo. Una empresa cuyas emisiones de una de estas materias primas representen **10 % o más** de sus emisiones FLAG brutas totales **puede** usar esa ruta (no está obligada) | [VERIFICADO] [53] |
| Madera y fibra de madera | Las empresas del sector forestal o con emisiones de madera/fibra ≥ 10 % de sus emisiones FLAG **deben** usar esa ruta. **No existe actualmente ruta de largo plazo** para madera y fibra: sus metas deben llevar una nota al pie indicando la exclusión, y deben (re)presentar la meta FLAG de largo plazo cuando la ruta esté disponible | [VERIFICADO] [53] |
| Deforestación | Fecha de corte de deforestación **2020 o anterior**; no se admiten fechas posteriores a tres años antes de la primera presentación a validación. Compromiso de deforestación cero conforme al Accountability Framework | [SECUNDARIO — página web SBTi] [56] |
| Meta FLAG de largo plazo | Reducción mínima del **72 %** a 2050 | [SECUNDARIO — página web SBTi; confirmar en la FLAG Guidance] [56] |

### 7.6 Principales cambios de CNZS V2.0 (para planificar el roadmap del motor)

[VERIFICADO — documento oficial "Main Changes"] [54]

| Área | Cambio |
|---|---|
| Categorización | Se sustituye la ruta pyme separada por **Categorías A y B** con obligaciones diferenciadas (facturación, geografía, emisiones, empleados) |
| Gobernanza | **Nuevo**: requisitos obligatorios de gobernanza de net-zero, rendición de cuentas del directorio, planificación de la transición y divulgación (CNZS-C1 y C2) |
| Aseguramiento | **Nuevo**: modelo formal de aseguramiento con validación de metas y evaluaciones de fin de ciclo por organismos de validación reconocidos; **aseguramiento limitado obligatorio** para empresas Categoría A sobre inventarios y métricas de fijación de metas (CNZS-C7) |
| Año base | Se reemplaza el año base histórico por un **año base de la meta** basado en los datos comprensivos más recientes; se permite seguir comunicando frente a años anteriores si se valida la equivalencia |
| Actividades intensivas (EIA) | **Nuevo**: para Categoría A, identificación y cuantificación obligatoria de *emissions-intensive activities* y reporte de las que representen **≥ 5 % del Alcance 3** |
| Alcance 1 | **Metas separadas** de Alcance 1 (antes iban combinadas con Alcance 2), cubriendo el **100 %** de las emisiones directas. Nueva opción de "transición de activos" para sectores con capital de larga vida |
| Alcance 2 | **Metas separadas** de Alcance 2 cubriendo el **100 %** de electricidad, calor, vapor y frío comprados. Las metas de alineación pasan de "renovable" a **"electricidad baja en carbono"**. Se **elimina** la opción de metas de intensidad. Las metas de emisiones de Alcance 2 se basan **solo en el inventario físico (location-based)**. Las Categoría A que aumenten su demanda eléctrica **más de 20 % anual** deben fijar metas de emisiones |
| Alcance 3 — límite | Se sustituye el umbral de porcentaje fijo por un enfoque **basado en significancia**: cubrir todas las categorías de Alcance 3 que representen **≥ 5 % de las emisiones de las categorías 1–14**, con exclusiones opcionales específicas en las categorías 3, 7, 8, 9, 10 y 14 cuando no haya capacidad práctica de influir, reportando y justificando cada exclusión |
| Alcance 3 — métodos | Las metas de involucramiento de proveedores/clientes se amplían a **rutas de alineación** (porcentaje de proveedores/clientes "en transición" o "alineados a net-zero"). Nuevos métodos de alineación por **volumen, uso del producto y fin de vida**. Se **elimina** el método de intensidad económica y física de Alcance 3 (el del 7 % anual compuesto) por falta de rutas de referencia científicas. Las metas de largo plazo de Alcance 3 pasan a ser **opcionales** |
| Ciclo de metas | Todas las metas se fijan sobre base de **5 años**; se retira la revisión obligatoria quinquenal y se pasa a evaluación continua |
| Implementación | **Nuevo**: jerarquía de implementación que prioriza reducciones directas a nivel de actividad antes de acciones en "pools" de actividad o a nivel sectorial |
| Instrumentos de mercado | **Nuevo**: criterios de integridad para acciones, proyectos e instrumentos (verificabilidad, alineación temporal, no doble contabilidad, adicionalidad, fugas). Para electricidad: PPA físicos y financieros, contratos de electricidad baja en carbono y certificados no empaquetados, con **coincidencia geográfica** y **límite de 15 años de antigüedad del generador**; medición horaria para grandes consumidores |
| Bioenergía | **Nuevo**: los insumos de base biológica deben cumplir criterios mínimos de sostenibilidad de terceros y de SBTi, prohibiendo la asociación con deforestación o conversión de ecosistemas naturales |
| Remociones | **Nuevo**: requisito prospectivo de apoyar remociones de carbono **a partir de 2035** para empresas Categoría A ("post-2035 responsibility requirement", CNZS-C45) |
| Neutralización | Se integra en un marco más amplio de "ongoing emissions responsibility" (OER), con requisitos detallados de **durabilidad del almacenamiento**, responsabilidad sobre emisiones directas e indirectas, condiciones de doble contabilidad y reporte |
| BVCM | La recomendación de "beyond value chain mitigation" se estandariza en el marco OER como programa de reconocimiento **opcional** |

---

## 8. Greenwashing: regulación y normas técnicas

### 8.1 Directiva (UE) 2024/825 — "Empoderar a los consumidores para la transición verde"

| Elemento | Dato | Etiqueta |
|---|---|---|
| Título | Directiva (UE) 2024/825 del Parlamento Europeo y del Consejo, de **28 de febrero de 2024**, por la que se modifican las Directivas 2005/29/CE y 2011/83/UE en lo que respecta a empoderar a los consumidores para la transición ecológica mediante una mejor protección contra las prácticas desleales y una mejor información | [VERIFICADO] [57] |
| Publicación en el DOUE | **6 de marzo de 2024** | [VERIFICADO] [57] |
| Entrada en vigor | 20 días tras la publicación | [VERIFICADO] [57] |
| **Plazo de transposición** | **27 de marzo de 2026** | [VERIFICADO] [57] |
| **Fecha de aplicación** | **27 de septiembre de 2026** | [VERIFICADO] [57] |

> 📌 Nota de contexto temporal: a la fecha de esta investigación (15 de septiembre de 2026), **faltan 12 días** para que las normas nacionales de transposición empiecen a aplicarse. Es el cambio regulatorio más inminente del documento.

#### Nuevas prácticas prohibidas "en toda circunstancia" (lista negra del Anexo I de la Directiva 2005/29/CE)

Resumidas con palabras propias [VERIFICADO] [57]:

| Punto | Práctica prohibida |
|---|---|
| **2a** | Exhibir una etiqueta de sostenibilidad que no se base en un sistema de certificación o que no haya sido establecida por autoridades públicas. |
| **4a** | Formular una **alegación ambiental genérica** (por ejemplo "ecológico", "verde", "respetuoso con el medio ambiente") sin poder demostrar un desempeño ambiental excelente y reconocido. |
| **4b** | Formular una alegación ambiental sobre **todo el producto o toda la empresa** cuando en realidad solo concierne a un aspecto concreto o a una actividad concreta. |
| **4c** | Afirmar que un producto tiene impacto ambiental **neutro, reducido o positivo** en materia de emisiones de GEI **basándose exclusivamente en compensación** (offsetting). |
| **10a** | Presentar como rasgo distintivo de la oferta algo que es un **requisito legal obligatorio** para todos los productos de esa categoría. |
| **23d–23e** | Ocultar información sobre el impacto negativo de una actualización de software en la funcionalidad; o presentar como necesaria una actualización que solo mejora la funcionalidad. |
| **23f–23g** | Comercializar un bien con una característica que **limita su durabilidad** sin informarlo; o afirmar falsamente una durabilidad determinada en condiciones normales de uso. |
| **23h** | Presentar como reparables bienes que no lo son. |
| **23i** | Inducir a sustituir consumibles antes de lo técnicamente necesario. |
| **23j** | Ocultar que el uso de componentes no originales deteriorará la funcionalidad, o afirmarlo falsamente. |

#### Cambios en los artículos 6 y 7 (prácticas engañosas, evaluación caso a caso)

[VERIFICADO] [57]

- **Art. 6(1)(b)**: se añaden como "características principales" del producto las **características ambientales o sociales**, los accesorios y los **aspectos de circularidad** (durabilidad, reparabilidad, reciclabilidad). Es decir, engañar sobre ellos es práctica engañosa evaluable caso a caso.
- **Art. 6(2)(d)** — **alegaciones sobre desempeño ambiental futuro** (tipo "seremos neutros en 2030"): solo son admisibles si se basan en **compromisos claros, objetivos, públicamente disponibles y verificables**, recogidos en un **plan de implementación detallado y realista**, con **verificación periódica por un tercero experto independiente**.
- **Art. 6(2)(e)**: se prohíbe publicitar **beneficios irrelevantes** que no se deriven de ninguna característica real del producto o del negocio.
- **Art. 7** — **comparaciones**: cuando se comparan productos por características ambientales, sociales o de circularidad, se considera información sustancial (cuya omisión es engañosa) el **método de comparación**, **qué productos se comparan y sus proveedores**, y las **medidas para mantener actualizada** esa información.
- **Etiquetas de sostenibilidad**: los sistemas de certificación que las respaldan deben cumplir cuatro condiciones: acceso abierto a todo operador que cumpla, desarrollo de requisitos con **consulta a partes interesadas**, procedimientos frente a incumplimiento (incluida la retirada de la etiqueta) y **seguimiento por un tercero** basado en normas internacionales, de la Unión o nacionales. Las etiquetas establecidas por autoridades públicas están exentas del requisito de sistema de certificación.

#### Traducción operativa para el skill anti-greenwashing (UE)

1. ¿La alegación es genérica sin desempeño ambiental excelente demostrado? → prohibida (4a).
2. ¿La alegación de neutralidad se apoya solo en compensación? → prohibida (4c).
3. ¿La alegación cubre el producto entero pero la evidencia solo cubre un componente o una planta? → prohibida (4b).
4. ¿Es una promesa a futuro? → exige plan detallado, público, con hitos y verificación independiente periódica (art. 6(2)(d)).
5. ¿Es una comparación? → publicar método, productos comparados y proveedores, y cómo se actualiza (art. 7).
6. ¿Es un sello propio o de una asociación sin sistema de certificación? → prohibido (2a).
7. ¿La ventaja anunciada es en realidad una obligación legal? → prohibida (10a).

### 8.2 Directiva de Alegaciones Ecológicas (Green Claims Directive) — estado

| Hito | Fecha | Etiqueta |
|---|---|---|
| Propuesta de la Comisión, COM(2023) 166 final (procedimiento 2023/0085(COD)) | **23 de marzo de 2023** | [VERIFICADO] [58] |
| Dictamen del Comité Económico y Social Europeo | 14 de junio de 2023 | [VERIFICADO] [58] |
| Dictamen del Comité Europeo de las Regiones | 10 de octubre de 2023 | [VERIFICADO] [58] |
| Posición del Parlamento Europeo en primera lectura | **12 de marzo de 2024** | [VERIFICADO] [58] |
| Debates en el Consejo | junio–julio de 2024 | [VERIFICADO] [58] |
| **Estado registrado en EUR-Lex al 15-sep-2026** | **"En curso" (Ongoing), en fase de primera lectura. EUR-Lex no registra ningún acto de adopción, retirada ni acuerdo en trílogo posterior a julio de 2024** | [VERIFICADO — ficha de procedimiento de EUR-Lex] [58] |
| Acontecimientos de 2025–2026 (intención de retirada anunciada por la Comisión, suspensión de trílogos, etc.) | — | **[NO VERIFICADO]** — no se pudo confirmar en fuente oficial dentro de esta investigación. La ficha de EUR-Lex y la página de la Comisión sobre *green claims* no registran eventos posteriores a 2024. **Verificar antes de publicar cualquier afirmación sobre su estado.** |

> ⚠️ Instrucción para el producto: mientras no se confirme, el agente debe decir que la Directiva de Alegaciones Ecológicas **no está en vigor** y que la norma aplicable en la UE es la Directiva (UE) 2024/825 transpuesta al derecho nacional. No afirmar que fue retirada ni que fue aprobada.

### 8.3 Reino Unido: CMA Green Claims Code

| Elemento | Dato | Etiqueta |
|---|---|---|
| Emisor | **Competition and Markets Authority (CMA)** | [VERIFICADO] [59] |
| Publicación | **20 de septiembre de 2021** | [VERIFICADO] [59] |
| Naturaleza | **Guía**, no norma autónoma: ayuda a las empresas a cumplir obligaciones ya existentes de derecho del consumidor. No es asesoría legal | [VERIFICADO] [59] |
| Base legal original | Consumer Protection from Unfair Trading Regulations 2008 y Business Protection from Misleading Marketing Regulations 2008 | [VERIFICADO] [60] |
| Base legal actual | Las disposiciones de protección frente al comercio desleal están ahora en la **Digital Markets, Competition and Consumers Act 2024**, sobre la que la CMA publicó la guía **CMA207** | [VERIFICADO] [61] |

**Los seis principios del Green Claims Code** (parafraseados) [VERIFICADO] [60]:

| # | Principio | Qué implica |
|---|---|---|
| 1 | Las alegaciones deben ser **veraces y exactas** | El producto o servicio debe entregar realmente el beneficio ambiental anunciado, sin exageración ni insinuaciones engañosas |
| 2 | Deben ser **claras y no ambiguas** | Lenguaje comprensible; evitar términos vagos como "eco-friendly" sin explicación |
| 3 | No deben **omitir ni ocultar información importante** | No destacar lo positivo callando impactos negativos significativos que influirían en la decisión de compra |
| 4 | Las **comparaciones** deben ser justas y significativas | Comparar productos similares con mediciones consistentes y base transparente |
| 5 | Deben considerar el **ciclo de vida completo** | Fabricación, transporte, uso y fin de vida |
| 6 | Deben estar **fundamentadas** | Evidencia robusta, creíble y actualizada |

> Útil como checklist universal: los seis principios de la CMA son el instrumento más claro y más fácil de explicar a una pyme, y son compatibles con la Directiva 2024/825 y con la Ley 19.496 chilena.

### 8.4 Chile: Ley 19.496 y el SERNAC

| Elemento | Dato | Etiqueta |
|---|---|---|
| Norma | **Ley N° 19.496**, sobre protección de los derechos de los consumidores | [VERIFICADO] [62] |
| Publicación | **7 de marzo de 1997** | [VERIFICADO] [62] |
| Multa general por infracción | Hasta **300 UTM** | [VERIFICADO — art. 24] [62] |
| **Multa por publicidad falsa o engañosa** difundida por medios de comunicación social, en relación con los elementos del artículo 28 | Hasta **1.500 UTM** | [VERIFICADO — art. 24] [62] |
| **Multa agravada si la publicidad falsa o engañosa incide sobre la salud, la seguridad o el medio ambiente** | Hasta **2.250 UTM** | [VERIFICADO — art. 24] [62] |
| Circunstancias que el tribunal debe ponderar | Atenuantes (reparación del daño, autodenuncia, colaboración) y agravantes (reincidencia, daño patrimonial grave, riesgo a la seguridad) | [VERIFICADO — art. 24] [62] |
| Vínculo con el contrato | Las "condiciones objetivas" señaladas en el **artículo 28** que se comunican en la publicidad se entienden **incorporadas al contrato** (art. 1° N°4 y art. 4) | [VERIFICADO] [62] |

> 🔑 **Punto clave para Chile:** la ley chilena **ya sanciona hoy** el greenwashing, sin necesidad de una norma específica: una alegación ambiental falsa o engañosa cae bajo el artículo 28 y, por incidir sobre el medio ambiente, activa el tramo agravado de **2.250 UTM** del artículo 24. Ese es el argumento más fuerte para convencer a una empresa chilena de fundamentar sus alegaciones.

**Pendientes de verificación en Chile [NO VERIFICADO]:**
- Texto literal del **artículo 28** (letras a–g: componentes, idoneidad, características relevantes, precio, condiciones de garantía, etc.) y del **artículo 28 A** (publicidad comparativa / conductas que inducen a error). El servicio de texto de la Biblioteca del Congreso Nacional truncó el documento en el artículo 24 en los tres intentos realizados.
- **Guías, circulares interpretativas o pronunciamientos específicos del SERNAC sobre alegaciones ambientales** ("eco", "biodegradable", "carbono neutral", "sustentable"). No se localizó ninguno navegando el portal institucional del SERNAC; la sección de noticias no muestra contenidos sobre publicidad ambiental. **No afirmar que existe una guía del SERNAC sobre greenwashing hasta confirmarlo.**
- Aplicación de la **Ley 21.081 (2018)**, que fortaleció facultades del SERNAC y elevó multas, y de la **Ley 21.398 ("Pro Consumidor", 2021)**.

### 8.5 Normas ISO relevantes

> ⚠️ **Limitación de esta investigación:** `iso.org` devolvió **HTTP 403** en los cuatro intentos de lectura (páginas de catálogo y plataforma OBP). Los datos siguientes provienen de conocimiento previo y **no** fueron confirmados en la fuente oficial en esta sesión. **[NO VERIFICADO]** — validar número de edición, año y alcance en `iso.org` antes de usarlos en producto.

#### ISO 14021 — Autodeclaraciones ambientales (etiquetado Tipo II) [NO VERIFICADO]

Principios que rigen las autodeclaraciones ambientales, resumidos:

- La declaración debe ser **exacta, verificable, pertinente y no engañosa**.
- Debe ser **específica**: indicar a qué se refiere (producto, envase, componente o servicio).
- **No se admiten declaraciones vagas** o inespecíficas como "amigable con el medio ambiente", "verde", "no contaminante", "seguro para la naturaleza".
- **No debe implicar** una mejora ambiental que no exista, ni basarse en la ausencia de una sustancia que el producto nunca contuvo o que ya está prohibida.
- Debe poder **sustentarse con evidencia** disponible antes de hacerse pública y mantenerse actualizada.
- Define términos concretos con requisitos de uso (reciclable, contenido reciclado, compostable, degradable, reutilizable, recargable, consumo reducido de energía, entre otros) y **símbolos** como el lazo de Möbius.
- El marco general del etiquetado ambiental está en la familia ISO 14020 (Tipo I: ISO 14024, etiquetas con certificación por tercero; Tipo II: ISO 14021, autodeclaradas; Tipo III: ISO 14025, declaraciones ambientales de producto con datos cuantificados de ACV).

#### ISO 14068-1:2023 — Gestión del cambio climático: transición a cero neto, Parte 1: Carbono neutralidad [NO VERIFICADO]

Ideas principales, resumidas:

- Establece principios, requisitos y orientación para lograr y **demostrar la neutralidad en carbono** de un "sujeto" (organización, producto, servicio, edificio, evento, etc.).
- **Jerarquía obligatoria**: primero **medir** la huella de carbono, luego **reducir** las emisiones mediante acciones propias y de la cadena de valor conforme a un **plan de gestión de carbono** con metas y plazos, y **solo al final compensar** el remanente con créditos de carbono que cumplan criterios de calidad.
- Exige que la compensación sea **residual**, no un sustituto de la reducción, y que los créditos usados sean **verificables, adicionales, permanentes, sin doble contabilidad y con tratamiento de fugas**; establece expectativas crecientes de uso de **remociones** frente a créditos de reducción a lo largo del tiempo.
- Requiere **transparencia documental**: alcance del sujeto, límites, periodo, metodología, cantidad compensada y tipo de créditos, y disponibilidad pública de la declaración.
- Sustituye en la práctica a la especificación británica PAS 2060.

> ⚠️ **Interacción crítica con la UE:** el punto **4c** de la lista negra de la Directiva (UE) 2024/825 prohíbe afirmar impacto climático neutro **basándose exclusivamente en compensación**. Una certificación de "carbono neutral" bajo ISO 14068-1 **no protege** por sí sola frente a esa prohibición si la reducción real es marginal y la neutralidad descansa en créditos. El agente debe advertirlo siempre.

---

## 9. MACC: curva de costos marginales de abatimiento

### 9.1 Qué es y para qué sirve

Una **MACC** (Marginal Abatement Cost Curve) es un gráfico de barras que ordena las medidas de reducción de emisiones de **menor a mayor costo por tonelada evitada**. Cada barra tiene:

- **Ancho** = potencial anual de abatimiento de la medida, en tCO2e/año.
- **Alto** = costo marginal de abatimiento, en moneda por tCO2e (puede ser **negativo** si la medida ahorra dinero neto).

El eje horizontal acumula el abatimiento total; el vertical cruza el cero, de modo que las medidas que están **bajo la línea de cero** son las que pagan por sí mismas ("no-regret"). La curva responde a tres preguntas de negocio: cuánto puedo reducir, en qué orden conviene hacerlo y cuánto cuesta cada tramo.

> Aclaración metodológica honesta: la MACC es una herramienta de **priorización**, no de predicción. Es estática (no captura interacciones ni curvas de aprendizaje), sensible a la tasa de descuento y a la vida útil asumidas, e ignora costos de transacción y barreras no económicas. Presentarla siempre con sus supuestos visibles. **[SECUNDARIO — síntesis propia]**

### 9.2 Fórmula del costo marginal de abatimiento

$$\text{CMA} = \frac{\text{CAPEX} \times \text{FRC}(i, n) + \text{OPEX}_{\text{anual}} - \text{Ahorros}_{\text{anuales}}}{\text{Abatimiento anual (tCO}_2\text{e)}}$$

donde el **factor de recuperación de capital** (FRC, *capital recovery factor*) anualiza la inversión:

$$\text{FRC}(i,n) = \frac{i\,(1+i)^{n}}{(1+i)^{n} - 1}$$

- $i$ = tasa de descuento anual (costo de capital real de la empresa).
- $n$ = vida útil de la medida en años.
- Los **ahorros** incluyen energía evitada, combustible evitado, menor mantenimiento, ingresos por excedentes y, si aplica, impuestos al carbono evitados.
- Si la medida es de inversión cero (por ejemplo un cambio de procedimiento), FRC × CAPEX = 0 y el costo es simplemente (OPEX − ahorros) / tCO2e.

**Convención de signos:** un CMA **negativo** significa que la medida genera un beneficio económico neto además de reducir emisiones.

### 9.3 Cómo construir la curva (procedimiento para el motor)

1. **Inventario de medidas.** Listar todas las opciones técnicamente viables, cada una con CAPEX, OPEX incremental, ahorros anuales, vida útil y abatimiento anual.
2. **Definir el escenario base** (*business as usual*). El abatimiento se mide **contra ese escenario**, no contra el año actual. Si la red eléctrica se descarboniza sola, ese efecto pertenece a la línea base, no a la medida.
3. **Homogeneizar supuestos**: misma tasa de descuento, misma moneda y año base, mismos factores de emisión, mismo horizonte.
4. **Evitar doble contabilidad**: si dos medidas actúan sobre el mismo consumo (por ejemplo LED + sensores de presencia), calcular la segunda **de forma incremental** sobre la primera, o agruparlas en un paquete.
5. **Calcular el CMA** de cada medida con la fórmula anterior.
6. **Ordenar de menor a mayor CMA** y acumular el abatimiento en el eje X.
7. **Trazar la brecha**: superponer la línea vertical del abatimiento anual que exige la meta (por ejemplo, la trayectoria SBTi). Lo que queda a la derecha de esa línea es el remanente sin solución identificada.
8. **Analizar sensibilidad**: recalcular con $i$ ± 3 pp, precios de energía ± 30 % y vida útil ± 25 %. El **orden** de las medidas suele ser más robusto que los valores absolutos.

### 9.4 Cómo leer la curva

| Zona | Lectura | Acción |
|---|---|---|
| Barras anchas y bajo cero (izquierda) | Ahorro neto con volumen relevante | Ejecutar ya; financian el resto del plan |
| Barras estrechas y bajo cero | Ahorran dinero pero mueven poca emisión | Hacerlas, pero no son la respuesta a la meta |
| Barras anchas y sobre cero | El núcleo del costo del plan | Negociar financiamiento, escalonar, buscar incentivos |
| Barras muy altas y estrechas | Costo desproporcionado por poca tonelada | Posponer; esperar cambio tecnológico o de precios |
| Espacio a la derecha de la línea de meta | Brecha sin solución | Señal de alerta: la meta no es alcanzable con lo identificado |

---

## 10. Monte Carlo para la probabilidad de cumplir una meta

### 10.1 Por qué Monte Carlo

Una trayectoria determinista dice "en 2030 emitiremos 9.350 tCO2e". Eso es falso en el sentido estricto: el crecimiento del negocio, la velocidad de descarbonización de la red eléctrica, el éxito de cada proyecto y la calidad de los factores de emisión son **inciertos**. Monte Carlo convierte la pregunta binaria ("¿cumplimos?") en una distribución de resultados y una **probabilidad**, que es lo que un directorio o un banco necesita para decidir.

### 10.2 Enfoque recomendado

**Paso 1 — Escribir el modelo de emisiones como una función explícita.** Por ejemplo, para un horizonte de $H$ años:

$$E_H = E_0 \prod_{y=1}^{H} \Big[ (1 + g_y)\,(1 - d_y)\,(1 - e_y) \Big] \times \prod_{k} (1 - p_k \cdot s_k)$$

donde $g_y$ = crecimiento de la actividad, $d_y$ = descarbonización exógena (red eléctrica), $e_y$ = eficiencia continua, y cada proyecto discreto $k$ aporta una reducción $s_k$ que ocurre solo si el proyecto se ejecuta ($p_k$ = variable Bernoulli).

**Paso 2 — Elegir distribuciones por variable.** Regla práctica: usar la distribución más simple que refleje honestamente lo que se sabe.

| Variable incierta | Distribución sugerida | Por qué |
|---|---|---|
| Crecimiento de la producción o ventas | **Normal** o **lognormal** (si no puede ser negativa) | Suma de muchos efectos pequeños; se parametriza con el plan de negocio y su desviación histórica |
| Factor de emisión de la red eléctrica | **Triangular** (mín, más probable, máx) o **PERT** | Hay proyección oficial (valor central) y rangos de escenarios |
| Ahorro real de un proyecto de eficiencia | **Triangular** | Se conoce el diseño (más probable) y el rango de desempeño típico |
| ¿Se ejecuta el proyecto? | **Bernoulli** | Modela riesgo de aprobación, permisos o financiamiento |
| Año de puesta en marcha | **Discreta** o **triangular discretizada** | Captura retrasos |
| Incertidumbre del factor de emisión | **Normal** con CV del inventario | Se puede tomar del análisis de incertidumbre del inventario GEI |
| Precio de la energía o del carbono | **Lognormal** o escenarios discretos ponderados | Colas asimétricas |

**Paso 3 — Modelar correlaciones.** Es el error más frecuente: tratar todo como independiente. Si la producción crece, el consumo energético crece y la inversión disponible aumenta. Implementar al menos las correlaciones obvias (crecimiento ↔ consumo; precio de energía ↔ ahorro monetario) mediante una **cópula gaussiana** o, más simple, generando un factor común compartido.

**Paso 4 — Iteraciones.** El error estándar de una probabilidad estimada es $\sqrt{p(1-p)/N}$, máximo en $p=0{,}5$:

| N iteraciones | Error estándar máximo de la probabilidad |
|---|---|
| 1.000 | ±1,58 puntos porcentuales |
| 5.000 | ±0,71 pp |
| **10.000** | **±0,50 pp** |
| 50.000 | ±0,22 pp |
| 100.000 | ±0,16 pp |

**Recomendación:** **10.000 iteraciones** como mínimo para reportar una probabilidad con una cifra decimal; 100.000 si se van a reportar percentiles de cola (P5, P95). Fijar siempre una **semilla** para reproducibilidad — es un requisito de auditabilidad, no un detalle técnico.

**Paso 5 — Reportar.**

- **Probabilidad de cumplir la meta**: fracción de iteraciones con $E_H \le \text{meta}$.
- **Percentiles** de emisiones en el año meta: P5, P25, **P50 (mediana)**, P75, P95.
- **Brecha esperada**: mediana menos meta.
- **Análisis de sensibilidad**: correlación de rangos (Spearman) entre cada variable de entrada y el resultado, presentada como diagrama de tornado. Esto dice **dónde invertir en reducir incertidumbre**.
- **Supuestos de cada distribución**, con su fuente. Sin esto, el resultado no es auditable.

**Paso 6 — Interpretar con honestidad.** Una probabilidad del 40 % no es "vamos por buen camino con matices": significa que el plan actual no alcanza. Umbrales sugeridos para el agente:

| Probabilidad | Lectura | Mensaje |
|---|---|---|
| ≥ 80 % | Meta robusta | Mantener y monitorear |
| 50–80 % | Meta alcanzable pero frágil | Añadir medidas de respaldo del MACC |
| 20–50 % | Meta improbable | Replantear el plan; identificar la brecha |
| < 20 % | Meta no creíble | **Riesgo de greenwashing**: anunciarla públicamente sin plan es exactamente lo que prohíbe el art. 6(2)(d) de la Directiva (UE) 2024/825 |

### 10.3 Referencias metodológicas

- El **análisis de incertidumbre de inventarios GEI** está tratado en la guía de incertidumbre del GHG Protocol, que distingue incertidumbre **científica**, de **parámetro/estimación** y de **modelo**, y admite métodos estadísticos y de simulación para propagarla. **[NO VERIFICADO]** — el enlace directo al PDF devolvió 404; localizar el documento vigente en `ghgprotocol.org` antes de citarlo. [64]
- Las **Directrices del IPCC de 2006 para inventarios nacionales de GEI (Vol. 1, Cap. 3)** definen dos enfoques: propagación de errores (Enfoque 1) y **simulación de Monte Carlo (Enfoque 2)**, este último recomendado cuando hay incertidumbres grandes, distribuciones no normales o correlaciones. **[NO VERIFICADO]** — verificar capítulo y numeración en `ipcc-nggip.iges.or.jp`.
- Para valorar el costo-efectividad en moneda por tonelada, el **HM Treasury Green Book supplementary guidance: "Valuation of energy use and greenhouse gas emissions for appraisal"** (Reino Unido, última actualización el **30 de noviembre de 2023**, alineada con los valores de CO2-equivalencia del IPCC AR5) define valores del carbono en £/tCO2e, tasas de descuento y el cálculo de costo-efectividad de políticas climáticas (su capítulo 5). Es la referencia pública más citable para parametrizar una MACC. [VERIFICADO] [65]

---

## Fórmulas y métodos

Todos los ejemplos numéricos de esta sección fueron **calculados** durante la investigación (no estimados a ojo) y son reproducibles con los parámetros indicados.

### F1. Trayectoria SBTi de contracción absoluta (lineal)

$$E_t = E_{base} \times \big(1 - r \times (t - t_{base})\big)$$

- $r$ = tasa lineal anual. Mínimos de la ruta transversal: **4,2 %** para Alcances 1 y 2 (1,5 °C) y **2,5 %** para Alcance 3 (muy por debajo de 2 °C), **ajustados dinámicamente** según el año base y el año net-zero. [VERIFICADO] [54]
- La reducción acumulada es $r \times (t - t_{base})$ y **no** se compone.

**Ejemplo numérico.** Empresa con año base **2024** y **12.500 tCO2e** de Alcances 1+2. Tasa 4,2 % anual.

| Año | Años desde base | Reducción acumulada | Emisiones permitidas (tCO2e) |
|---|---|---|---|
| 2025 | 1 | 4,2 % | 11.975 |
| 2026 | 2 | 8,4 % | 11.450 |
| 2027 | 3 | 12,6 % | 10.925 |
| 2028 | 4 | 16,8 % | 10.400 |
| 2029 | 5 | 21,0 % | 9.875 |
| **2030** | **6** | **25,2 %** | **9.350** |
| 2031 | 7 | 29,4 % | 8.825 |
| 2032 | 8 | 33,6 % | 8.300 |
| 2033 | 9 | 37,8 % | 7.775 |
| **2034** | **10** | **42,0 %** | **7.250** |

Nota: una reducción lineal del 42 % en 10 años equivale a una tasa **compuesta** del **5,302 % anual**. Confundir ambas es un error frecuente al comparar con metas expresadas en CAGR.

**Validaciones que el motor debe ejecutar:**
- Año base ≥ 2015 (C13).
- Horizonte entre 5 y 10 años desde la presentación (C13), salvo que el año meta sea 2030 (R7).
- Si Alcance 3 ≥ 40 % del total 1+2+3 → exigir meta de Alcance 3 (C4).
- Cobertura de Alcance 3 ≥ 67 % del total reportado y excluido (C6).
- Exclusiones ≤ 5 % en 1+2 y ≤ 5 % en 3 (C5).
- No acreditar créditos de carbono ni emisiones evitadas como progreso (C11, C12).

### F2. Umbral de Alcance 3

$$\text{Ratio}_{3} = \frac{E_{3}}{E_{1} + E_{2} + E_{3}}$$

Si $\text{Ratio}_{3} \ge 0{,}40$ → la meta de Alcance 3 es **obligatoria**. [VERIFICADO] [53]

**Ejemplo.** $E_1$ = 3.000, $E_2$ = 9.500, $E_3$ = 41.000 tCO2e. Total = 53.500. Ratio₃ = 41.000 / 53.500 = **76,6 %** → meta de Alcance 3 obligatoria, y debe cubrir al menos 67 % × 41.000 = **27.470 tCO2e**.

### F3. Meta de largo plazo

$$E_{2050} \le E_{base} \times (1 - 0{,}90)$$

Mínimo del **90 %** de reducción en todos los alcances. Las emisiones residuales deben **neutralizarse** con remociones permanentes para poder declarar net-zero. [VERIFICADO] [54]

**Ejemplo.** Con $E_{base}$ = 12.500 tCO2e: $E_{2050} \le$ **1.250 tCO2e**, y esas 1.250 t deben neutralizarse.

### F4. Factor de recuperación de capital y costo marginal de abatimiento

$$\text{FRC}(i,n) = \frac{i(1+i)^n}{(1+i)^n-1} \qquad\qquad \text{CMA} = \frac{\text{CAPEX}\cdot\text{FRC} + \text{OPEX} - \text{Ahorros}}{\text{tCO}_2\text{e evitadas}}$$

**Ejemplo completo de MACC** — tasa de descuento $i$ = 10 %, valores anuales en USD:

| Medida | CAPEX | n (años) | FRC | CAPEX anualizado | OPEX | Ahorros | tCO2e/año | **CMA (USD/tCO2e)** |
|---|---|---|---|---|---|---|---|---|
| Iluminación LED | 45.000 | 10 | 0,16275 | 7.324 | 1.200 | 14.000 | 38 | **−144,1** |
| Motores eficientes | 120.000 | 12 | 0,14676 | 17.612 | 3.000 | 26.000 | 70 | **−77,0** |
| Solar FV autoconsumo | 320.000 | 20 | 0,11746 | 37.587 | 6.500 | 52.000 | 160 | **−49,5** |
| Recuperador de calor | 210.000 | 15 | 0,13147 | 27.609 | 8.000 | 22.000 | 130 | **+104,7** |
| Electrificación de flota | 480.000 | 8 | 0,18744 | 89.973 | 12.000 | 40.000 | 145 | **+427,4** |

**Verificación del primer caso:** FRC(10 %, 10) = 0,10 × 1,10¹⁰ / (1,10¹⁰ − 1) = 0,16275. CAPEX anualizado = 45.000 × 0,16275 = 7.324. CMA = (7.324 + 1.200 − 14.000) / 38 = −5.476 / 38 = **−144,1 USD/tCO2e**.

**Curva resultante (orden de ejecución y abatimiento acumulado):**

| Orden | Medida | CMA (USD/tCO2e) | Abatimiento acumulado (tCO2e/año) |
|---|---|---|---|
| 1 | Iluminación LED | −144,1 | 38 |
| 2 | Motores eficientes | −77,0 | 108 |
| 3 | Solar FV autoconsumo | −49,5 | 268 |
| 4 | Recuperador de calor | +104,7 | 398 |
| 5 | Electrificación de flota | +427,4 | 543 |

**Lectura:** las tres primeras medidas suman **268 tCO2e/año con ahorro neto**. Si la meta exige 400 tCO2e/año, hay que llegar hasta el recuperador de calor; el costo neto del paquete completo hasta ese punto sigue siendo favorable porque las medidas negativas financian la positiva. La electrificación de flota, a 427 USD/tCO2e, solo se justifica si hay precio del carbono, obligación regulatoria o beneficio reputacional cuantificado.

### F5. Monte Carlo — ejemplo reproducible

**Configuración.** Misma empresa: $E_0$ = 12.500 tCO2e en 2024, meta SBTi 2030 = 9.350 tCO2e (F1). Horizonte 6 años. 100.000 iteraciones, semilla 20260915.

| Variable | Distribución | Parámetros |
|---|---|---|
| Crecimiento anual de la actividad | Normal | media 2,5 %, desviación 1,5 % |
| Descarbonización anual de la red | Triangular | mín 1,0 %, moda 2,5 %, máx 4,5 % |
| Eficiencia anual continua | Triangular | mín 0 %, moda 2,0 %, máx 3,0 % |
| ¿Se ejecuta el proyecto solar? | Bernoulli | p = 0,70 |
| Reducción puntual del solar (año 3) | Triangular | mín 3 %, moda 6 %, máx 9 % |

**Resultados calculados:**

| Indicador | Valor |
|---|---|
| **Probabilidad de cumplir la meta** | **11,5 %** (error estándar ±0,10 pp) |
| Media de emisiones en 2030 | 10.731 tCO2e |
| Desviación estándar | 1.182 tCO2e |
| P5 | 8.899 tCO2e |
| P10 | 9.264 tCO2e |
| P25 | 9.902 tCO2e |
| **P50 (mediana)** | **10.670 tCO2e** |
| P75 | 11.492 tCO2e |
| P90 | 12.282 tCO2e |
| P95 | 12.776 tCO2e |
| **Brecha mediana frente a la meta** | **+1.320 tCO2e** |

**Interpretación:** con 11,5 % de probabilidad, la meta **no es creíble** con el plan actual. La brecha mediana de 1.320 tCO2e/año es exactamente el insumo que se lleva a la MACC: hay que encontrar medidas que cubran ~1.320 tCO2e/año adicionales. Anunciar públicamente esta meta sin ese plan es el supuesto que la Directiva (UE) 2024/825 exige respaldar con "un plan de implementación detallado y realista" verificado por un tercero.

**Encadenamiento MACC ↔ Monte Carlo (el núcleo del motor):**

1. Trayectoria SBTi → define la **meta anual** (F1).
2. Monte Carlo sobre el plan actual → **probabilidad y brecha** (F5).
3. MACC → **qué medidas** cubren esa brecha y a qué costo (F4).
4. Se añaden las medidas seleccionadas al modelo y se vuelve a correr Monte Carlo → nueva probabilidad.
5. Se itera hasta superar el umbral de credibilidad (≥ 80 %).
6. El resultado —plan, costo, probabilidad y supuestos— es a la vez el **plan de transición** (NIIF S2 / ESRS E1 / GRI 102-1) y la **defensa anti-greenwashing**.

---

## Cambios recientes (2024–2026)

Línea de tiempo consolidada de todo lo verificado en este documento.

| Fecha | Hito | Marco |
|---|---|---|
| **28-feb-2024** | Directiva (UE) 2024/825 (empoderar a los consumidores) | Greenwashing UE |
| **feb-2024** | Publicación de GRI 14: Mining Sector | GRI |
| **06-mar-2024** | Publicación en el DOUE de la Directiva (UE) 2024/825 | Greenwashing UE |
| **12-mar-2024** | Posición del Parlamento Europeo en primera lectura sobre la Green Claims Directive | Greenwashing UE |
| **ene-2024** | Publicación de GRI 101: Biodiversity 2024 | GRI |
| **abr-2024** | Inicio de la revisión del SBTi Corporate Net-Zero Standard hacia V2.0 | SBTi |
| **28-oct-2024** | CMF Chile publica la NCG 519 (adopción de NIIF S1 y S2) | ISSB / Chile |
| **12-nov-2024** | IAASB publica **ISSA 5000** | Aseguramiento |
| **dic-2024** | EFRAG entrega el estándar **VSME** a la Comisión Europea | ESRS / pymes |
| **ene-2025** | IAASB e IESBA presentan conjuntamente ISSA 5000 e IESSA | Aseguramiento |
| **26-feb-2025** | La Comisión adopta la propuesta del paquete **Omnibus I** | CSRD / CSDDD |
| **mar–jun-2025** | Primera consulta pública del SBTi sobre CNZS V2 | SBTi |
| **jun-2025** | Publicación de **GRI 102: Climate Change 2025** y **GRI 103: Energy 2025** | GRI |
| **11-jul-2025** | Reglamento Delegado (UE) 2025/1416 (aplazamiento de fechas de aplicación de ciertos ESRS) | ESRS |
| **jul-2025** | El ISSB publica dos borradores de enmiendas a los estándares SASB y a la guía por industria de NIIF S2 | ISSB / SASB |
| **29-jul-2025** | **Recomendación de la Comisión C(2025) 4984** sobre la norma voluntaria VSME | ESRS / pymes |
| **30-jul-2025** | Fecha de la Recomendación VSME | ESRS / pymes |
| **29-jul – 29-sep-2025** | Consulta pública de EFRAG sobre los borradores de ESRS simplificados | ESRS |
| **15-sep-2025** | Entran en vigor SBTi CNZS V1.3 y Near-Term Criteria V5.3 | SBTi |
| **nov–dic-2025** | Segunda consulta pública del SBTi sobre CNZS V2 | SBTi |
| **02-dic-2025** | EFRAG entrega a la Comisión su asesoramiento técnico sobre los ESRS revisados | ESRS |
| **dic-2025** | El ISSB emite las **enmiendas a NIIF S2** sobre divulgación de emisiones de GEI | ISSB |
| **23-dic-2025** | EFRAG entrega el análisis costo-beneficio y documentos de apoyo | ESRS |
| **01-ene-2026** | Entra en vigor **GRI 101: Biodiversity 2024**; entra en vigor **GRI 14: Mining Sector** | GRI |
| **01-ene-2026** | GRI pone a disposición las secciones actualizadas de los sectoriales con clima y energía | GRI |
| **24-feb-2026** | Se adopta la **Directiva (UE) 2026/470 (Omnibus I)** | CSRD / CSDDD |
| **26-feb-2026** | Publicación en el DOUE de la Directiva (UE) 2026/470 | CSRD / CSDDD |
| **mar-2026** | SBTi FLAG Guidance V1.2 | SBTi |
| **18-mar-2026** | Entrada en vigor de la Directiva (UE) 2026/470 | CSRD / CSDDD |
| **~18/27-mar-2026** | Perú: el Consejo Normativo de Contabilidad oficializa NIIF S1 y S2 (Res. 001-2026-EF/30) **[SECUNDARIO]** | ISSB / Perú |
| **27-mar-2026** | **Plazo de transposición** de la Directiva (UE) 2024/825 | Greenwashing UE |
| **14-abr-2026** | Entran en vigor SBTi CNZS V1.3.1 y Near-Term Criteria V5.3.1 | SBTi |
| **06-may-2026** | La Comisión publica el borrador del acto delegado de ESRS revisados | ESRS |
| **08-may-2026** | El Consejo Técnico del SBTi aprueba CNZS V2.0 | SBTi |
| **21-may-2026** | El Consejo de Administración del SBTi adopta CNZS V2.0 | SBTi |
| **03-jun-2026** | Cierre de la consulta pública sobre el acto delegado de ESRS | ESRS |
| **11-jun-2026** | **SBTi publica el Corporate Net-Zero Standard V2.0** | SBTi |
| **jun-2026** | Talleres CMF–Fundación IFRS en Chile | ISSB / Chile |
| **03-jul-2026** | La Comisión adopta el **acto delegado C(2026) 5010** con los **ESRS simplificados (2026)** y un acto delegado con una norma voluntaria | ESRS |
| **27-jul-2026** | CMF Chile publica la **NCG 572**: prórroga de un año de la obligación NIIF S1/S2 | ISSB / Chile |
| **15-sep-2026** | *(fecha de esta investigación)* | — |
| **27-sep-2026** | **Fecha de aplicación** de la Directiva (UE) 2024/825 | Greenwashing UE |
| **15-dic-2026** | Entra en vigor **ISSA 5000** (e IESSA); se **retira ISAE 3410** | Aseguramiento |
| **31-dic-2026** | Último día de vigencia de **GRI 302: Energy 2016** | GRI |
| **01-ene-2027** | Entran en vigor **GRI 102: Climate Change 2025** y **GRI 103: Energy 2025**; se retiran GRI 305-1 a 305-5 y GRI 201-2 | GRI |
| **01-ene-2027** | Aplicación obligatoria de los **ESRS (2026)**; aplicación de los nuevos umbrales CSRD | ESRS |
| **01-ene-2027** | Vigencia de las **enmiendas de dic-2025 a NIIF S2** | ISSB |
| **31-ene-2027** | Entra en vigor el **SBTi CNZS V2.0**; validaciones disponibles desde el Q1 2027 | SBTi |
| **01-jul-2027** | Fecha límite para que la Comisión adopte normas de **aseguramiento limitado** | Aseguramiento UE |
| **19-mar-2027** | Plazo de transposición de la Directiva (UE) 2026/470 | CSRD |
| **31-dic-2027** | Entra en vigor la sección III de la NCG 519 chilena (memorias del año 2027) | ISSB / Chile |
| **31-ene-2028** | Último día para presentar metas al SBTi bajo V1.3.1 | SBTi |
| **26-jul-2029** | Aplicación de la CSDDD reformada | CSDDD |
| **01-ene-2029** | Obligatoriedad de NIIF S1/S2 en Perú para empresas no supervisadas con ingresos ≥ 2.300 UIT **[SECUNDARIO]** | ISSB / Perú |

### Qué significa esto para "Agentes ESG"

1. **Todo lo importante cambia entre 2026 y 2028.** El motor debe tratar la **versión del marco** como un parámetro de primera clase (año de reporte → versión aplicable), no como una constante.
2. **Chile se relajó un año** (NCG 572): la ventana de preparación es 2026–2027, no 2026. Argumento comercial: quien reporte voluntariamente el ejercicio 2026 accede a retroalimentación técnica de la CMF.
3. **Perú llega más tarde y por una vía distinta** (Consejo Normativo de Contabilidad, no el regulador de valores), con un umbral en UIT que hay que recalcular cada año.
4. **La UE redujo drásticamente el alcance** (1.000 empleados + 450 M EUR) pero **endureció la publicidad ambiental** desde el 27 de septiembre de 2026. Para una pyme latinoamericana exportadora, el riesgo ya no es tanto "tener que reportar CSRD" como (a) responder cuestionarios de cadena de valor —para lo que sirve el VSME— y (b) no poder usar alegaciones ambientales en su marketing europeo.
5. **El aseguramiento se unifica** en ISSA 5000 desde diciembre de 2026, y SBTi V2.0 lo hace **obligatorio (limitado)** para empresas Categoría A. El expediente auditable deja de ser opcional.

---

## Pendientes y dudas

Lista de todo lo que **no** quedó verificado y debe resolverse antes de usarse en producto.

| # | Pendiente | Por qué quedó abierto | Dónde verificar |
|---|---|---|---|
| 1 | **GRI 304: Biodiversity 2016** — títulos exactos de 304-1 a 304-4 y fecha de fin de vigencia | Los dos enlaces `pdf.ashx?id=12499` devolvieron error de servidor de GRI | `globalreporting.org`, centro de descargas |
| 2 | **Códigos de métricas SASB** por industria (prefijos y numeración) | No se abrió ningún estándar SASB concreto | `navigator.sasb.ifrs.org` |
| 3 | **Licencia necesaria** para incorporar contenido SASB/SICS/NIIF en un producto de código abierto | Interpretación propia de los términos publicados | `licences@ifrs.org` / IFRS Sustainability Licensing |
| 4 | **Perú**: número, fecha y articulado exactos de la Resolución CNC N.° 001-2026-EF/30; confirmación del umbral de 2.300 UIT y de la fecha del 1-ene-2029 | `gob.pe` devolvió HTTP 418 | `gob.pe` / `mef.gob.pe` (Consejo Normativo de Contabilidad) |
| 5 | **Brasil (CVM 193) y México (CNBV)**: fechas y alcance exactos | Solo fuentes secundarias | `cvm.gov.br`, `gob.mx/cnbv` |
| 6 | Cifra de **"nueve de ~40 jurisdicciones latinoamericanas"** que adoptaron ISSB | Cifra de prensa, no de la Fundación IFRS | `ifrs.org` — jurisdictional profiles |
| 7 | **Redacción literal de las 11 divulgaciones del TCFD** en el documento original del FSB | `fsb-tcfd.org` devolvió 403 y el PDF del FSB devolvió 500; se usó la transcripción oficial del Gobierno del Reino Unido, que incluye una adaptación al sector público en Estrategia b) | `fsb.org` o archivo del TCFD |
| 8 | **ISSA 5000**: confirmación textual de que cubre aseguramiento limitado y razonable y de que ISAE 3000 (Revisada) sigue vigente para otras materias | Se leyeron páginas índice del IAASB, no el texto de la norma | Texto de ISSA 5000 y FAQ del IAASB |
| 9 | **ISO 14021** e **ISO 14068-1:2023**: número de edición, año, título exacto y alcance | `iso.org` devolvió HTTP 403 en los cuatro intentos (catálogo y plataforma OBP) | `iso.org` o un organismo nacional de normalización |
| 10 | **Green Claims Directive**: qué ocurrió en 2025–2026 (¿retirada?, ¿trílogos suspendidos?, ¿sigue viva?) | EUR-Lex marca el procedimiento "en curso" sin eventos posteriores a julio de 2024 | Programa de Trabajo de la Comisión 2026 (Anexo de retiradas), EU Law Tracker, Observatorio Legislativo del PE |
| 11 | **Chile**: texto literal de los artículos **28** y **28 A** de la Ley 19.496 | El servicio XML de la BCN truncó el documento en el artículo 24 en tres intentos | `bcn.cl/leychile` (versión completa) |
| 12 | **SERNAC**: existencia de guías, circulares interpretativas o pronunciamientos sobre **alegaciones ambientales** | No se localizó ninguno navegando `sernac.cl`; la sección de noticias no muestra contenido ambiental | `sernac.cl`, Ley del Consumidor, circulares interpretativas |
| 13 | **SBTi V2.0**: umbrales numéricos que separan **Categoría A y Categoría B**; requisitos concretos de la antigua ruta pyme (empleados, tarifas, si exigía meta de Alcance 3) | Solo se leyó el documento de "Main Changes" | Texto de CNZS V2.0 y definición de pyme del SBTi |
| 14 | **SBTi**: ecuación exacta del **ajuste dinámico** de la tasa de reducción según año base y año net-zero | Está en el "CNZS v1.3.1 Method Appendix", no leído | `sciencebasedtargets.org` — Method Appendix y Corporate Near-Term Tool |
| 15 | **SBTi FLAG**: confirmación del **72 % a 2050** y de la fecha de corte de deforestación en el texto de la FLAG Guidance V1.2 | Solo página web de SBTi | FLAG Guidance V1.2 (PDF) |
| 16 | **GHG Protocol**: documento vigente de análisis de incertidumbre y su recomendación sobre Monte Carlo | El PDF citado devolvió 404 | `ghgprotocol.org` |
| 17 | **IPCC 2006 Guidelines Vol. 1 Cap. 3**: numeración exacta de los Enfoques 1 y 2 de incertidumbre | No verificado en esta sesión | `ipcc-nggip.iges.or.jp` |
| 18 | **ESRS (2026)**: confirmar si ya se publicó en el DOUE tras el periodo de escrutinio, y su número de Reglamento Delegado | Al 15-sep-2026 solo se localizó el documento adoptado C(2026) 5010, con la fecha de entrada en vigor pendiente de completar por la Oficina de Publicaciones | `eur-lex.europa.eu` |
| 19 | **VSME**: confirmar el número oficial de la Recomendación (se cita como (UE) 2025/1710 en fuentes secundarias) y el contenido del acto delegado de norma voluntaria adoptado el 3-jul-2026 | Solo se leyó el documento C(2025) 4984 y su Anexo I | `eur-lex.europa.eu` |
| 20 | **Errata de GRI**: confirmar con GRI que la FAQ de GRI 103 (pregunta 6) contiene un error tipográfico al decir "GRI 305: Energy 2016" en lugar de "GRI 302" | Deducido por contexto y por la portada de GRI 302 | `gssbsecretariat@globalreporting.org` |

## Fuentes

1. GRI — GRI 102: Climate Change 2025 (PDF oficial), sección "System of GRI Standards". https://globalreporting.org/pdf.ashx?id=29514
2. GRI — GRI 1: Foundation 2021 (PDF oficial), secciones 3 "Reporting in accordance with the GRI Standards", "Reporting with reference to the GRI Standards" y 4 "Reporting principles". https://globalreporting.org/pdf.ashx?id=12334
3. GRI — GRI 2: General Disclosures 2021 (PDF oficial). https://www.globalreporting.org/how-to-use-the-gri-standards/gri-standards-english-language/
4. GRI — "GRI 103: Energy 2025 Frequently Asked Questions (FAQs)", junio 2025, preguntas 4, 6, 7, 8 y 11. https://globalreporting.org/media/mead5ytn/gri-103-energy-2025-frequently-asked-questions-faqs.pdf
5. GRI — Standards development (página de proyectos del GSSB). https://www.globalreporting.org/standards/standards-development/
6. GRI — GRI Standards English Language (listado oficial de descargas y versiones). https://www.globalreporting.org/how-to-use-the-gri-standards/gri-standards-english-language/
7. GRI — GRI 101: Biodiversity 2024 (PDF oficial), portada, índice y "Using this Standard". https://www.globalreporting.org/pdf.ashx?id=24534
8. GRI — GRI 102: Climate Change 2025 (PDF oficial), portada e índice. https://globalreporting.org/pdf.ashx?id=29514
9. GRI — Topic Standard for Climate Change and Energy (página de proyecto). https://www.globalreporting.org/standards/standards-development/topic-standard-for-climate-change-and-energy/
10. GRI — GRI 305: Emissions 2016 (PDF oficial), nota de portada del índice: Requisito 1.2 y divulgaciones 305-1 a 305-5 superadas por GRI 102: Climate Change 2025. https://globalreporting.org/pdf.ashx?id=12510
11. GRI — GRI 201: Economic Performance 2016 (PDF oficial), nota del índice sobre 201-2. https://www.globalreporting.org/pdf.ashx?id=12368
12. GRI — GRI 103: Energy 2025 (PDF oficial), portada e índice. https://globalreporting.org/pdf.ashx?id=29537
13. GRI — GRI 302: Energy 2016 (PDF oficial), portada ("effective ... until 31 December 2026") y nota del índice. https://www.globalreporting.org/pdf.ashx?id=12467
14. IFRS Foundation — IFRS S1 General Requirements for Disclosure of Sustainability-related Financial Information (página oficial del Sustainability Standards Navigator). https://www.ifrs.org/issued-standards/ifrs-sustainability-standards-navigator/ifrs-s1-general-requirements/
15. IFRS Foundation — IFRS S2 Climate-related Disclosures (página oficial del Sustainability Standards Navigator). https://www.ifrs.org/issued-standards/ifrs-sustainability-standards-navigator/ifrs-s2-climate-related-disclosures/
16. IFRS Foundation — Introduction to the ISSB and IFRS Sustainability Disclosure Standards. https://www.ifrs.org/sustainability/knowledge-hub/introduction-to-issb-and-ifrs-sustainability-disclosure-standards/
17. IFRS Foundation — Educational material: "Greenhouse Gas Emissions — Disclosure requirements applying IFRS S2 Climate-related Disclosures", mayo 2025 (preguntas 1, 2, 3, 4, 6, 7, 10, 11, 12). https://www.ifrs.org/content/dam/ifrs/supporting-implementation/ifrs-s2/ghg-ifrs-s2-educational-material.pdf
18. IFRS Foundation — Staff paper "Scope 3 GHG emissions applying IFRS S2" (TIG, noviembre 2025). https://www.ifrs.org/content/dam/ifrs/meetings/2025/november/tig/ap3-scope-3-ghg-emissions-applying-ifrs-s2.pdf
19. IFRS Foundation — "ISSB announces guidance and reliefs to support Scope 3 GHG emission disclosures" (diciembre 2022). https://www.ifrs.org/news-and-events/news/2022/12/issb-announces-guidance-and-reliefs-to-support-scope-3-ghg-emiss/
20. IFRS Foundation — Appendix B: Industry-based disclosure requirements (proyecto Climate-related Disclosures). https://www.ifrs.org/projects/completed-projects/2023/climate-related-disclosures/appendix-b-industry-based-disclosure-requirements/
21. IFRS Foundation — Educational material "Using ISSB Industry-based Guidance". https://www.ifrs.org/content/dam/ifrs/supporting-implementation/issb-standards/issb-industry-based-guidance-applying-issb-standards.pdf
22. IFRS Foundation — "ISSB proposes comprehensive review of priority SASB Standards and targeted amendments to others" (julio 2025). https://www.ifrs.org/news-and-events/news/2025/07/issb-comprehensive-review-sasb/
23. IFRS Foundation — "Voluntarily applying ISSB Standards — A guide for preparers", septiembre 2024, secciones "Transition reliefs", "Proportionality mechanisms" y "Communicating partial application". https://www.ifrs.org/content/dam/ifrs/supporting-implementation/issb-standards/issb-voluntary-application-preparers.pdf
24. IFRS Foundation — "ISSB issues targeted amendments to IFRS S2 to support implementation" (diciembre 2025). https://www.ifrs.org/news-and-events/news/2025/12/issb-issues-targeted-amendments-ifrs-s2/
25. IFRS Foundation — Amendments to Greenhouse Gas Emissions Disclosures (Amendments to IFRS S2), diciembre 2025. https://www.ifrs.org/content/dam/ifrs/publications/amendments/english/2025/issb-2025-1-amendments-ifrs-s2.pdf
26. CMF Chile — Norma de Carácter General N°519, de 28 de octubre de 2024 (texto íntegro; secciones I, II, III y "Vigencia"). https://www.cmfchile.cl/normativa/ncg_519_2024.pdf
27. CMF Chile — Norma de Carácter General N°572, de 27 de julio de 2026 (modifica la vigencia de la sección III de la NCG 519). https://www.cmfchile.cl/normativa/ncg_572_2026.pdf
28. CMF Chile — "CMF amplía plazo para que empresas reporten conforme a NIIF S1 y NIIF S2" (comunicado, 27 de julio de 2026) y página institucional de Sostenibilidad. https://www.cmfchile.cl/portal/prensa/625/w4-article-112141.html · https://www.cmfchile.cl/portal/principal/623/w4-propertyvalue-50301.html
29. MEF Perú — Resolución de Consejo Normativo de Contabilidad N.° 001-2026-EF/30 (ficha en la Plataforma del Estado Peruano; **no se pudo abrir el texto: HTTP 418**). https://www.gob.pe/institucion/mef/normas-legales/7937774-001-2026-ef-30
30. [SECUNDARIO] TPC Group — "Adopción de estándares internacionales de sostenibilidad: aprobación de las NIIF S1 y S2 en el Perú"; y Gestión (gestion.pe) — reportaje sobre NIIF S1/S2 en Perú. https://tpcgroup-int.com/sin-categoria/adopcion-de-estandares-internacionales-de-sostenibilidad-aprobacion-de-las-niif-s1-y-s2-en-el-peru/
31. SMV Perú — Reporte de Sostenibilidad Corporativa (formato anexo a la memoria anual). https://www.smv.gob.pe/
32. [SECUNDARIO] Recuentos de adopción regional citados en prensa especializada y consultoras (Brasil CVM 193, México CNBV). Requiere verificación en cvm.gov.br y gob.mx/cnbv.
33. IFRS Foundation — Página oficial sobre el TCFD y el traspaso al ISSB. https://www.ifrs.org/sustainability/tcfd/
34. HM Treasury (GOV.UK) — "TCFD-aligned disclosure for the UK public sector: Application Guidance", sección "Summary requirements" (transcribe las 11 divulgaciones recomendadas del TCFD). https://assets.publishing.service.gov.uk/media/6a57c3c32f6185941a9a65fc/TCFD_Application_Guidance.pdf
35. IFRS Foundation — "Understanding SASB Standards" (SICS, estructura de los estándares, relación con NIIF S1/S2). https://www.ifrs.org/issued-standards/sasb-standards/understanding-sasb-standards/
36. IFRS Foundation — SASB Standards Navigator y Materiality Finder. https://navigator.sasb.ifrs.org/ · https://sasb.ifrs.org/standards/materiality-finder/
37. IFRS Foundation — "IFRS Sustainability Licensing" y página de licenciamiento de SASB. https://www.ifrs.org/products-and-services/sustainability-products-and-services/ifrs-sustainability-licensing/ · https://sasb.ifrs.org/licensing-use/
38. EUR-Lex — Reglamento Delegado (UE) 2023/2772 de la Comisión, de 31 de julio de 2023 (ESRS Set 1; Anexos I y II). http://data.europa.eu/eli/reg_del/2023/2772/oj
39. EFRAG — Sustainability Reporting / ESRS Knowledge Hub. https://www.efrag.org/en/sustainability-reporting · https://knowledgehub.efrag.org/
40. EUR-Lex — Directiva (UE) 2026/470 del Parlamento Europeo y del Consejo, de 24 de febrero de 2026 ("Omnibus I"). http://data.europa.eu/eli/dir/2026/470/oj
41. Comisión Europea — C(2026) 5010 final, Reglamento Delegado de 3 de julio de 2026 que modifica el Reglamento Delegado (UE) 2023/2772 en cuanto a la simplificación de determinadas normas de información sobre sostenibilidad (exposición de motivos, considerandos y artículos 1 a 3). https://ec.europa.eu/finance/docs/level-2-measures/csrd-delegated-act-2026-5010_en.pdf · Documento de trabajo: SWD(2026) 500 final, https://ec.europa.eu/finance/docs/level-2-measures/csrd-staff-working-document-2026-500_en.pdf
42. EFRAG — "European Commission Publishes Delegated Act on Revised ESRS and Voluntary Sustainability Reporting Standard" (noticia, julio 2026). https://www.efrag.org/en/news-and-calendar/news/european-commission-publishes-delegated-act-on-revised-esrs-and-voluntary-sustainability-reporting
43. Comisión Europea — Recomendación de la Comisión C(2025) 4984 final, de 30 de julio de 2025, sobre una norma voluntaria de información en materia de sostenibilidad para pymes (considerandos 3, 7, 8, 10, 11, 13–16). https://ec.europa.eu/finance/docs/law/250730-recommendation-vsme_en.pdf
44. [SECUNDARIO] Referencias al número de publicación Recomendación (UE) 2025/1710 en análisis de firmas profesionales (PwC, Linklaters, HSF Kramer).
45. Comisión Europea — Anexo I de C(2025) 4984 final (norma VSME: módulos básico B1–B11 y comprehensivo C1–C9). https://ec.europa.eu/finance/docs/law/250730-recommendation-vsme-annex-1_en.pdf
46. IAASB — ISAE 3000 (Revised), Assurance Engagements Other than Audits or Reviews of Historical Financial Information (definiciones de aseguramiento limitado y razonable; fecha de vigencia). https://www.iaasb.org/publications/international-standard-assurance-engagements-isae-3000-revised-assurance-engagements-other-audits-or
47. IAASB — "Assurance on a Greenhouse Gas Statement (to be withdrawn Dec. 15, 2026)" — página de proyecto de ISAE 3410. https://www.iaasb.org/consultations-projects/assurance-greenhouse-gas-statement
48. IAASB — "ISSA 5000 Frequently Asked Questions: Applicability Matters". https://www.iaasb.org/publications/issa-5000-frequently-asked-questions-applicability-matters
49. IAASB — "ISSA 5000 Adoption and Implementation" y "Understanding the International Standard on Sustainability Assurance 5000". https://www.iaasb.org/consultations-projects/issa-5000-adoption-and-implementation · https://www.iaasb.org/focus-areas/understanding-international-standard-sustainability-assurance-5000
50. IAASB — International Standard on Sustainability Assurance 5000, General Requirements for Sustainability Assurance Engagements (publicación, 12 de noviembre de 2024). https://www.iaasb.org/publications/international-standard-sustainability-assurance-5000-general-requirements-sustainability-assurance
51. IAASB/IESBA — "IAASB and IESBA Unveil New Standards and Guidance to Strengthen Sustainability Reporting and Assurance" (enero 2025). https://www.iaasb.org/news-events/2025-01/iaasb-iesba-unveil-new-standards-and-guidance-strengthen-sustainability-reporting-and-assurance
52. MHRA (GOV.UK) — "MHRA GXP Data Integrity Guidance and Definitions", Revisión 1, marzo de 2018 (definición de ALCOA y ALCOA+). https://assets.publishing.service.gov.uk/media/5aa2b9ede5274a3e391e37f3/MHRA_GxP_data_integrity_guide_March_edited_Final.pdf
53. SBTi — "SBTi Corporate Near-Term Criteria", Versión 5.3.1, abril de 2026 (criterios C1–C22, R5–R11 y requisitos sectoriales FLAG). https://files.sciencebasedtargets.org/production/files/SBTi-criteria.pdf
54. SBTi — "SBTi Corporate Net-Zero Standard", Versión 1.3.1, abril de 2026 (secciones 1.3, 2.2, 2.3, 3.3, Anexo B.1). https://files.sciencebasedtargets.org/production/files/Net-Zero-Standard.pdf · y "Main Changes Document — Corporate Net-Zero Standard V2.0", Versión 1, junio de 2026. https://files.sciencebasedtargets.org/production/files/Corporate-Net-Zero-Standard-V2-Main-Changes-Document.pdf
55. SBTi — "The Corporate Net-Zero Standard" y "The new Corporate Net-Zero Standard Version 2.0". https://sciencebasedtargets.org/net-zero · https://sciencebasedtargets.org/corporate-net-zero-standard-v2 · Texto V2.0: https://files.sciencebasedtargets.org/production/files/Corporate-Net-Zero-Standard-version-2.pdf
56. SBTi — Sector Forest, Land and Agriculture (página oficial). https://sciencebasedtargets.org/sectors/forest-land-and-agriculture
57. EUR-Lex — Directiva (UE) 2024/825 del Parlamento Europeo y del Consejo, de 28 de febrero de 2024 (Anexo I modificado de la Directiva 2005/29/CE; artículos 6 y 7). http://data.europa.eu/eli/dir/2024/825/oj
58. EUR-Lex — Ficha de procedimiento 2023/0085(COD), propuesta de Directiva sobre fundamentación y comunicación de alegaciones ambientales explícitas (COM(2023) 166 final). https://eur-lex.europa.eu/procedure/EN/2023_85 · Comisión Europea, página temática "Green claims": https://environment.ec.europa.eu/topics/circular-economy/green-claims_en
59. CMA (GOV.UK) — "Green claims code: making environmental claims" (publicación de 20 de septiembre de 2021). https://www.gov.uk/government/publications/green-claims-code-making-environmental-claims
60. CMA (GOV.UK) — "Making environmental claims on goods and services" (guía completa; seis principios y marco legal). https://www.gov.uk/government/publications/green-claims-code-making-environmental-claims/environmental-claims-on-goods-and-services
61. CMA (GOV.UK) — "Unfair commercial practices (CMA207)": guía sobre las disposiciones de protección frente al comercio desleal de la Digital Markets, Competition and Consumers Act 2024. https://www.gov.uk/government/publications/unfair-commercial-practices-cma207
62. Biblioteca del Congreso Nacional de Chile — Ley N° 19.496, sobre protección de los derechos de los consumidores (texto vía servicio XML de Ley Chile; artículos 1, 4 y 24). https://www.bcn.cl/leychile/navegar?idNorma=61438
63. [NO VERIFICADO] ISO — ISO 14021 (Etiquetas y declaraciones ambientales — Autodeclaraciones ambientales, etiquetado Tipo II) e ISO 14068-1:2023 (Gestión del cambio climático — Transición a cero neto — Parte 1: Carbono neutralidad). `iso.org` devolvió HTTP 403 en todos los intentos. Verificar en https://www.iso.org/standards.html
64. [NO VERIFICADO] GHG Protocol — Guía de evaluación de incertidumbre de inventarios de GEI. El enlace directo al PDF devolvió HTTP 404; localizar el documento vigente en el centro de herramientas y guías. https://ghgprotocol.org/
65. HM Treasury / DESNZ (GOV.UK) — "Valuation of energy use and greenhouse gas emissions for appraisal" (Green Book supplementary guidance), última actualización de 30 de noviembre de 2023, alineada con los valores de CO2-equivalencia del IPCC AR5; incluye valores del carbono en £/tCO2e, tasas de descuento y el cálculo de costo-efectividad (capítulo 5). https://www.gov.uk/government/publications/valuation-of-energy-use-and-greenhouse-gas-emissions-for-appraisal
66. Cálculos propios de esta investigación (trayectoria SBTi, FRC/MACC y simulación Monte Carlo), ejecutados en Python con NumPy; semilla 20260915 y 100.000 iteraciones para la simulación. Todos los parámetros están explicitados en la sección "Fórmulas y métodos" para permitir su reproducción.
