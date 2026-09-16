# Factores de emisión para Alcance 1 y Alcance 2 (Chile, Perú, IPCC, PCG, UK)

Fecha de investigación: 2026-09-15

> **Estado del documento:** PARCIAL — en construcción. Secciones 1, 2, 3, 4 y 7 completas. Secciones 5 y 6 en investigación.
>
> **Convención de etiquetas:**
> - `[VERIFICADO]` = leído directamente en la fuente oficial primaria (PDF/XLSX/página del organismo emisor).
> - `[SECUNDARIO]` = fuente no oficial (prensa, consultora, blog) o derivado de fuente oficial por un tercero.
> - `[NO VERIFICADO]` = no se pudo confirmar en fuente oficial; **no usar en producción sin verificar**.
> - `[CALCULADO]` = valor derivado aritméticamente por esta investigación a partir de valores verificados; se muestra la fórmula.

---

## Resumen

**Chile.** El programa **HuellaChile** (Ministerio del Medio Ambiente) publica la base de datos oficial de factores de emisión. La versión vigente para el año de reporte 2025 es la **v2, fechada 2026-05-04** [1]. Hallazgos clave:

- El factor del **Sistema Eléctrico Nacional (SEN)** que HuellaChile usa para **Alcance 2 por ubicación** es el **promedio anual de la red** publicado por el Ministerio de Energía en Energía Abierta, calculado con **PCG AR5**. Valores: **2022 = 0,327363**, **2023 = 0,255874**, **2024 = 0,213140**, **2025 = 0,246725 kgCO2e/kWh**.
- **NO es un margen de operación (OM)** y **NO incluye pérdidas de transmisión y distribución**. Las pérdidas se contabilizan aparte, en la categoría **2.2 Pérdidas por T&D**, aplicando un **5,7 %** sobre el factor de red.
- **Alerta crítica:** los factores del SEN **fueron revisados retroactivamente** de 2021 a 2025. Los valores del PDF "Nivel básico" v3 (nov-2024) están **obsoletos** y difieren hasta un ~9 % de los actuales. Ver §8.
- HuellaChile usa **IPCC 2006 Vol.2 Cap.2 Cuadro 2.4** (Comercial/Institucional) para combustión estacionaria y **Cuadros 3.2.1/3.2.2** para móvil, combinados con **densidades y poderes caloríficos del Balance Nacional de Energía (BNE) 2024** de la CNE.
- **PCG usados por HuellaChile: AR5** (CO2=1, CH4=28, N2O=265), explícito en el libro oficial.

**Perú.** El marco es **RM N° 185-2021-MINAM** (Huella de Carbono Perú, voluntario). Tres diferencias estructurales frente a Chile:
- **No hay resolución que apruebe valores numéricos**: los factores se cargan en la plataforma y se anclan al inventario nacional INFOCARBONO.
- La plataforma entrega **tres factores por gas separados** (tCO2/MWh, tCH4/MWh, tN2O/MWh), **no un CO2e único**. El motor debe modelar Perú con 3 factores.
- Los valores del SEIN **solo son accesibles tras login**; los de este documento provienen de informes ISO 14064-1 verificados y están marcados `[SECUNDARIO]`.
- Perú **no publica factores propios de combustible**: usa defaults IPCC 2006 con poderes caloríficos peruanos (en **TJ/galón**), salvo el gas natural, que sí tiene factor nacional (**56 293 kg CO2/TJ**).
- **Perú también usa AR5**, igual que Chile.

**IPCC.** El **Refinamiento 2019 NO cambió** ninguno de los cuadros relevantes (1.2, 1.3, 1.4, 2.2–2.5, 3.2.1, 3.2.2): siguen vigentes los valores de 2006. El **IPCC no publica densidades**; hay que tomarlas de otra fuente y documentarla (para Chile: BNE 2024).

**Reino Unido.** La publicación vigente es **DESNZ 2026** (11-jun-2026), que **sigue usando AR5**. El factor de electricidad UK cayó **−26 %** (0,17700 → 0,13096 kgCO2e/kWh) por un cambio de método. Datos bajo **Open Government Licence v3.0**.

**Convergencia útil:** Chile (HuellaChile), Perú (MINAM) y Reino Unido (DESNZ) usan **todos AR5** a septiembre de 2026. Un solo set de PCG cubre los tres.

---

## 1. Chile — Factor de emisión del Sistema Eléctrico Nacional (SEN), Alcance 2

### 1.1 ¿Qué factor usa HuellaChile para Alcance 2 por ubicación?

| Pregunta | Respuesta | Etiqueta |
|---|---|---|
| Fuente del factor | Ministerio de Energía, plataforma **Energía Abierta** (CNE) | [VERIFICADO] |
| Tipo de factor | **Promedio anual de la red** (grid average), no margen de operación | [VERIFICADO] |
| ¿Margen de operación (OM) / build margin (BM) / combined margin (CM)? | **No se usa** en HuellaChile. El OM/BM/CM pertenece a metodologías de proyecto (MDL/Artículo 6), no al inventario corporativo | [VERIFICADO] (por ausencia en la base oficial) |
| ¿Incluye pérdidas de T&D? | **NO.** Las pérdidas son una categoría separada (**2.2 Pérdidas por T&D**) | [VERIFICADO] |
| PCG aplicado | **AR5** (explícito en la fuente: "Ministerio de Energía 2025 (AR5)") | [VERIFICADO] |
| Categoría en la herramienta | Alcance 2 · **2.1 Electricidad** · "Emisiones indirectas por energía importada" | [VERIFICADO] |
| Granularidad | Promedio anual. La fuente también publica factores mensuales | [VERIFICADO] |

### 1.2 Factor del SEN por año — valores oficiales vigentes

Fuente: HuellaChile, *Base de datos factores de emisión 2025 — Organizaciones y Eventos*, v2 (2026-05-04), hoja `2.1 Electricidad` [1]. Origen primario: Ministerio de Energía / Energía Abierta [2].

| Año de reporte | kgCO2e/kWh (valor publicado completo) | kgCO2e/kWh (redondeado) | tCO2e/MWh | Etiqueta |
|---|---|---|---|---|
| 2018 | 0,4187 | 0,4187 | 0,4187 | [VERIFICADO] |
| 2019 | 0,4056 | 0,4056 | 0,4056 | [VERIFICADO] |
| 2020 | 0,3834 | 0,3834 | 0,3834 | [VERIFICADO] |
| 2021 | 0,4199378573275227 | 0,41994 | 0,41994 | [VERIFICADO] |
| **2022** | **0,327362906277725** | **0,32736** | **0,32736** | [VERIFICADO] |
| **2023** | **0,255873741774226** | **0,25587** | **0,25587** | [VERIFICADO] |
| **2024** | **0,21313980791418277** | **0,21314** | **0,21314** | [VERIFICADO] |
| **2025** | **0,2467249809219505** | **0,24672** | **0,24672** | [VERIFICADO] |
| 2026 | No publicado aún | — | — | [NO VERIFICADO] |

> **Nota de unidades:** 1 kgCO2e/kWh = 1 tCO2e/MWh (numéricamente idéntico). La base oficial publica la misma fila en kWh, MWh y GWh.

> **Nota sobre 2025:** el año 2025 ya tiene factor SEN publicado, pero la propia base advierte que *"el promedio anual del último año corresponde al promedio de los meses disponibles"* [2]. El valor **sube** respecto de 2024 (0,2467 vs 0,2131).

### 1.3 Sistemas eléctricos medianos (fuera del SEN)

Para instalaciones en Aysén, Magallanes y Los Lagos, HuellaChile publica factores propios. **No usar el factor del SEN en esas zonas.**

| Sistema | 2022 | 2023 | 2024 | 2025 | Etiqueta |
|---|---|---|---|---|---|
| Sistema Eléctrico de Aysén (SEA) | 0,38650 | 0,33625 | 0,30450 | PENDIENTE | [VERIFICADO] |
| Sistema Eléctrico de Magallanes (SEM) | 0,56275 | 0,59283333 | 0,58720 | PENDIENTE | [VERIFICADO] |
| Sistema Eléctrico de Los Lagos | 0,62508333333 | 0,62416666667 | 0,62850 | PENDIENTE | [VERIFICADO] |

Unidad: kgCO2e/kWh. "PENDIENTE" es literal en la fuente: la base oficial declara estar *"en espera de publicación de FE para sistemas medianos desde Energía Abierta (Ministerio de Energía)"* [1].

> Sistemas históricos ya fusionados en el SEN (referencia): SING 2017 = 0,7730; SIC 2017 = 0,3364 kgCO2e/kWh [VERIFICADO].

### 1.4 Pérdidas de transmisión y distribución (categoría 2.2)

**Metodología oficial [VERIFICADO]:** HuellaChile aplica una **tasa fija de pérdidas del 5,7 %** sobre el factor de red del sistema correspondiente.

```
FE_pérdidas_T&D = FE_sistema_eléctrico × 0,057
```

Fuente de la tasa: *Base de Información de Eficiencia Energética — CEPAL/Enerdata, 2018* [1].

| Año | FE SEN (kgCO2e/kWh) | FE Pérdidas T&D (kgCO2e/kWh) | Etiqueta |
|---|---|---|---|
| 2022 | 0,327362906277725 | 0,018659685657830327 | [VERIFICADO] |
| 2023 | 0,255873741774226 | 0,014584803281130883 | [VERIFICADO] |
| 2024 | 0,21313980791418277 | 0,012148969051108419 | [VERIFICADO] |
| 2025 | 0,2467249809219505 | 0,01406332391255118 | [VERIFICADO] |

Comprobación: 0,21313980791418277 × 0,057 = 0,012148969051108418 ✔ [CALCULADO]

> **Implicación para el motor de cálculo:** el Alcance 2 *por ubicación* usa únicamente el factor de §1.2. Las pérdidas de T&D son **Alcance 3** en la lógica del GHG Protocol (categoría 3 "actividades relacionadas con energía"); HuellaChile las numera como 2.2 pero las trata como línea separada. **No sumarlas al Alcance 2** ni multiplicar dos veces.

---

## 2. Chile — Factores HuellaChile para combustibles (Alcance 1)

Fuente: HuellaChile, *Base de datos factores de emisión 2025*, v2 (2026-05-04), hojas `1.1 Combustión estacionaria` y `1.2 Combustión móvil` [1].

**Gases incluidos en TODOS los factores de esta sección: CO2 + CH4 + N2O**, agregados con **PCG AR5** (CO2=1, CH4=28, N2O=265) [VERIFICADO]. No incluyen emisiones WTT (upstream).

### 2.1 Combustión estacionaria (calderas, generadores)

Factores IPCC de base: **IPCC 2006, Vol.2, Cap.2, Cuadro 2.4 (Comercial/Institucional)** [VERIFICADO].

| Combustible (nombre HuellaChile) | Nombre IPCC | Unidad | Factor kgCO2e/unidad | CO2 kg/TJ | CH4 kg/TJ | N2O kg/TJ | Etiqueta |
|---|---|---|---|---|---|---|---|
| **Petróleo 2 (Diésel)** | Gas/Diesel Oil | m³ | **2714,5332574466397** | 74 100 | 10 | 0,6 | [VERIFICADO] |
| Petróleo 2 (Diésel) | Gas/Diesel Oil | litro | 2,71453325744664 | — | — | — | [VERIFICADO] |
| **Gasolina** | Motor Gasoline | m³ | **2267,8922621174397** | 69 300 | 10 | 0,6 | [VERIFICADO] |
| Gasolina | Motor Gasoline | litro | 2,2678922621174396 | — | — | — | [VERIFICADO] |
| **Gas licuado de petróleo (GLP)** | Liquefied Petroleum Gases | m³ | **1674,6640209139498** | 63 100 | 5 | 0,1 | [VERIFICADO] |
| GLP | Liquefied Petroleum Gases | litro | 1,6746640209139498 | — | — | — | [VERIFICADO] |
| **Gas natural** | Natural gas | m³ | **1,9804687688971803** | 56 100 | 5 | 0,1 | [VERIFICADO] |
| Gas natural | Natural gas | tonelada | 2469,412430046359 | — | — | — | [VERIFICADO] |
| **Gas ciudad (cañería)** | Natural gas | m³ | **1,9804687688971803** | 56 100 | 5 | 0,1 | [VERIFICADO] |
| **Kerosene** | Other Kerosene | m³ | **2586,939781149539** | 71 900 | 10 | 0,6 | [VERIFICADO] |
| Kerosene | Other Kerosene | litro | 2,5869397811495394 | — | — | — | [VERIFICADO] |
| **Petróleo 5 (fuel oil)** | Residual Fuel Oil | m³ | **3013,50628726749** | 77 400 | 10 | 0,6 | [VERIFICADO] |
| **Petróleo 6 (fuel oil)** | Residual Fuel Oil | m³ | **3072,02097245715** | 77 400 | 10 | 0,6 | [VERIFICADO] |
| **Carbón térmico** | Other Bituminous Coal | tonelada | **2652,7371160499997** | 94 600 | 10 | 1,5 | [VERIFICADO] |
| **Carbón metalúrgico** | Coking Coal | tonelada | **2652,7371160499997** | 94 600 | 10 | 1,5 | [VERIFICADO] |
| Petcoke | Petroleum Coke | tonelada | 3155,342485014 | 97 500 | 10 | 0,6 | [VERIFICADO] |
| Nafta | Naphtha | m³ | 2361,016079667 | 73 300 | 10 | 0,6 | [VERIFICADO] |
| Gas de refinería | Refinery Gas | m³ | 0,9787943975633998 | 57 600 | 5 | 0,1 | [VERIFICADO] |
| Gas de alto horno | Blast Furnace Gas | tonelada | 578,3501295 | 260 000 | 5 | 0,1 | [VERIFICADO] |

> **Nota:** carbón térmico y metalúrgico comparten factor porque HuellaChile aplica el mismo poder calorífico BNE (7 000 kcal/kg) y, en el Cuadro 2.4, ambos tienen CO2 = 94 600 kg/TJ.

### 2.2 LEÑA / BIOMASA — hallazgo importante

**La base de datos HuellaChile 2025 NO incluye un factor de Alcance 1 para leña ni biomasa en combustión estacionaria.** [VERIFICADO por ausencia]

Lo único que existe:

| Ítem | Alcance | Unidad | Factor | Fuente | Etiqueta |
|---|---|---|---|---|---|
| Leña | **3** (Adq. bienes y servicios) | tonelada | 52,14 kgCO2e/t | DEFRA 2025, hoja WTT-bioenergy | [VERIFICADO] |
| Madera y productos de madera | 3 | tonelada | 269,50416 kgCO2e/t | DEFRA 2025, Material use | [VERIFICADO] |
| Madera (disposición) | 3 | tonelada | 4,68568 kgCO2e/t | DEFRA 2025, Waste disposal | [VERIFICADO] |

**Interpretación (razonamiento propio, no afirmación oficial):** esto es coherente con la regla del IPCC/GHG Protocol de que el **CO2 biogénico de la biomasa se reporta fuera de alcances**, y solo el **CH4 y N2O** de su combustión van a Alcance 1. HuellaChile aparentemente no publica ese CH4/N2O de leña. **El motor de cálculo debe tratar la leña como caso especial y no inventar un factor.** Ver §10 (Pendientes).

El BNE 2024 sí publica poder calorífico de biomasa (3 500 kcal/kg) y pellet (3 941 kcal/kg, densidad 0,6 t/m³) [VERIFICADO], lo que permitiría construir el factor CH4/N2O con el Cuadro 2.4 del IPCC, pero **eso sería un cálculo propio, no el factor oficial de HuellaChile**.

### 2.3 Combustión móvil (vehículos de pasajeros o carga)

Factores IPCC de base: **IPCC 2006, Vol.2, Cap.3, Cuadros 3.2.1 y 3.2.2** [VERIFICADO].

| Combustible | Nombre IPCC | Unidad | Factor kgCO2e/unidad | CO2 kg/TJ | CH4 kg/TJ | N2O kg/TJ | Etiqueta |
|---|---|---|---|---|---|---|---|
| **Petróleo 2 (Diésel)** | Gas/Diesel Oil | m³ | **2740,160339286552** | 74 100 | 3,9 | 3,9 | [VERIFICADO] |
| Petróleo 2 (Diésel) | Gas/Diesel Oil | litro | 2,7401603392865517 | — | — | — | [VERIFICADO] |
| **Gasolina** | Motor Gasoline | m³ | **2345,3216986751995** | 69 300 | 25 | 8 | [VERIFICADO] |
| Gasolina | Motor Gasoline | litro | 2,3453216986751997 | — | — | — | [VERIFICADO] |
| **Gas licuado (GLP)** | Liquefied Petroleum Gases | m³ | **1717,6115899106999** | 63 100 | 62 | 0,2 | [VERIFICADO] |
| GLP | Liquefied Petroleum Gases | litro | 1,7176115899106998 | — | — | — | [VERIFICADO] |
| **Gas natural (GNC)** | Natural gas | m³ | **2,09326078848132** | 56 100 | 92 | 3 | [VERIFICADO] |
| **Kerosene** | Other Kerosene | m³ | **2579,930557948979** | 71 900 | 3 | 0,6 | [VERIFICADO] |
| Kerosene | Other Kerosene | litro | 2,579930557948979 | — | — | — | [VERIFICADO] |

> **Diferencia estacionaria vs móvil:** para el mismo combustible el CO2/TJ es idéntico; cambian CH4 y N2O. Ejemplo diésel: estacionaria CH4=10 / N2O=0,6; móvil CH4=3,9 / N2O=3,9. El N2O móvil es 6,5× mayor (catalizadores).

### 2.4 Densidades y poderes caloríficos oficiales de Chile (BNE 2024)

Fuente: **Balance Nacional de Energía 2024**, Ministerio de Energía / CNE, reproducido en la hoja `1.1 y 1.2 CUADRO A1 - BNE 2024` de la base HuellaChile [1]. **Esta es la fuente correcta de densidades para Chile** (el IPCC 2006 no publica densidades).

| Producto | Densidad (t/m³) | Poder calorífico **superior** (PCS) | Unidad PCS | Etiqueta |
|---|---|---|---|---|
| Petróleo Diésel | **0,84** | 10 900 | kcal/kg | [VERIFICADO] |
| Gasolina Motor | **0,73** | 11 200 | kcal/kg | [VERIFICADO] |
| Gas Licuado (GLP) | **0,55** | 12 100 | kcal/kg | [VERIFICADO] |
| Kerosene | **0,81** | 11 100 | kcal/kg | [VERIFICADO] |
| Kerosene de Aviación | 0,81 | 11 100 | kcal/kg | [VERIFICADO] |
| Nafta | 0,70 | 11 500 | kcal/kg | [VERIFICADO] |
| Gasolina de Aviación | 0,70 | 11 400 | kcal/kg | [VERIFICADO] |
| Petróleo Combustible 5 | 0,927 | 10 500 | kcal/kg | [VERIFICADO] |
| Petróleo Combustible 6 | 0,945 | 10 500 | kcal/kg | [VERIFICADO] |
| Petróleo Combustible IFO 180 | 0,936 | 10 500 | kcal/kg | [VERIFICADO] |
| Petróleo Crudo Nacional | 0,8245 | 10 963 | kcal/kg | [VERIFICADO] |
| Petróleo Crudo Importado | 0,855 | 10 860 | kcal/kg | [VERIFICADO] |
| Gas Natural | — | 9 341 | kcal/m³ | [VERIFICADO] |
| Gas Natural Licuado | 0,45 | 9 555 | kcal/m³ | [VERIFICADO] |
| Carbón | — | 7 000 | kcal/kg | [VERIFICADO] |
| Coque Mineral | — | 7 000 | kcal/kg | [VERIFICADO] |
| Coque de Petróleo | — | 8 100 | kcal/kg | [VERIFICADO] |
| Biomasa | — | 3 500 | kcal/kg | [VERIFICADO] |
| Pellet de Biomasa | 0,60 | 3 941 | kcal/kg | [VERIFICADO] |
| Licor Negro | — | 2 885 | kcal/kg | [VERIFICADO] |
| Biogás | — | 5 600 | kcal/m³ | [VERIFICADO] |
| Gas de Refinería | — | 4 260 | kcal/m³ | [VERIFICADO] |
| Electricidad | — | 860 | kcal/kWh | [VERIFICADO] |

> Densidad de gas natural usada internamente por HuellaChile: **0,000802 t/m³** (fuente secundaria citada: DEFRA 2025, *Fuel properties*) [VERIFICADO].

### 2.5 Refrigerantes / emisiones fugitivas (Alcance 1)

Fuente: HuellaChile v2 2025, hoja `1.4 Emisiones fugitivas`; base IPCC 2006 Vol.3 Cap.7 Cuadro 7.8 + **PCG AR5** (IPCC AR5 Cap.8 Tabla 8.A.1) [1].

| Refrigerante / gas | kgCO2e/kg | Etiqueta |
|---|---|---|
| HFC-32 | 677 | [VERIFICADO] |
| HFC-125 | 3 170 | [VERIFICADO] |
| HFC-134a | 1 300 | [VERIFICADO] |
| HFC-143a | 4 800 | [VERIFICADO] |
| HCFC-22 / R22 | 1 760 | [VERIFICADO] |
| **R404A** | **3 942,8** | [VERIFICADO] |
| **R407C** | **1 624,21** | [VERIFICADO] |
| **R410A** | **1 923,5** | [VERIFICADO] |
| **R507** | **3 985** | [VERIFICADO] |
| R407A | 1 923,4 | [VERIFICADO] |
| R407B | 2 546,7 | [VERIFICADO] |
| R410B | 2 048,15 | [VERIFICADO] |
| SF6 | 23 500 | [VERIFICADO] |
| NF3 | 16 100 | [VERIFICADO] |
| CH4 | 28 | [VERIFICADO] |
| N2O | 265 | [VERIFICADO] |
| CO2 (extintor) | 1 | [VERIFICADO] |

> Estos valores **confirman que HuellaChile usa AR5**: CH4=28, N2O=265, SF6=23 500, NF3=16 100, HFC-134a=1 300 son exactamente los PCG-100 de AR5. Comparación AR5 vs AR6 en §5.

---

## 3. Perú — Factor del SEIN y combustibles (MINAM)

### 3.0 Tres hallazgos estructurales (leer antes de implementar)

1. **Ninguna resolución ministerial aprueba valores numéricos del factor SEIN.** La Guía HC-Perú (§6.4.2) solo establece que los factores *"se adecúan a los factores de emisión de GEI usados en el Inventario Nacional de GEI – INFOCARBONO"*. Los valores anuales se cargan administrativamente en la plataforma, no por norma. [VERIFICADO]
2. **HC-Perú NO entrega un factor único en tCO2e/MWh.** Entrega **tres factores separados por gas** (tCO2/MWh, tCH4/MWh, tN2O/MWh); el CO2e lo construye el usuario aplicando PCG. **El motor debe modelar Perú con 3 factores, no 1.**
3. **El factor de consumo del SEIN NO incluye pérdidas de T&D.** Las pérdidas son una línea de factor aparte (Categoría 3 / aguas arriba en ISO 14064-1). [VERIFICADO]

### 3.1 Factor del SEIN — Alcance 2 por ubicación

| Año | CO2 (tCO2/MWh) | CH4 (tCH4/MWh) | N2O (tN2O/MWh) | Documento | Etiqueta |
|---|---|---|---|---|---|
| 2022 | 0,19989608 | 0,00001025 | 0,00000128 | ISA CTM 2022, Tabla 26 — "Fuente: MINAM" | [SECUNDARIO] |
| 2023 | 0,213031882 | 0,000010400 | 0,000001298 | ISA CTM 2023, Tabla 26 — "Fuente: MINAM" | [SECUNDARIO] |
| 2024 | 0,170232636063711 | 0,0000095198 | 0,00000117053 | ISA CTM 2024, Tabla 25 — "Fuente: MINAM 2024" | [SECUNDARIO] |
| 2025 | — | — | — | No publicado públicamente | **[NO VERIFICADO]** |
| 2026 | — | — | — | No existiría aún (se carga ex-post) | **[NO VERIFICADO]** |

> **Por qué [SECUNDARIO]:** la tabla oficial está dentro de la plataforma MINAM, que **requiere login**. Los valores provienen de informes ISO 14064-1 verificados por tercera parte que los transcriben con atribución literal "Fuente: MINAM". La precisión de los dígitos (0,170232636063711) indica copia directa desde la calculadora, no reelaboración. **Aun así, deben confirmarse antes de un reporte auditable.**

**CO2e agregado — [CALCULADO], NO es cifra oficial de MINAM.** Aplicando PCG AR5 (CH4=28, N2O=265):

| Año | tCO2e/MWh (derivado) | kgCO2e/kWh (derivado) |
|---|---|---|
| 2022 | ≈ 0,20052 | ≈ 0,2005 |
| 2023 | ≈ 0,21367 | ≈ 0,2137 |
| 2024 | ≈ 0,17081 | ≈ 0,1708 |

### 3.2 Pérdidas de transmisión y distribución (Perú) — factor separado

| Año | CO2 (tCO2/MWh) | CH4 (tCH4/MWh) | N2O (tN2O/MWh) | Etiqueta en el documento |
|---|---|---|---|---|
| 2022 | 0,153564417 | 0,000008683 | 0,000001075 | "Transmisión de energía eléctrica" |
| 2023 | 0,001740484 | 0,000000089 | 0,000000011 | "Pérdidas por transmisión" |
| 2024 | 0,001668375 | 0,000000081 | 0,000000010 | "Pérdidas por transmisión" |

Todos [SECUNDARIO].

> ⚠️ **Inconsistencia no resuelta:** el valor de 2022 tiene una magnitud ~100× mayor que 2023–2024. Parece aplicarse a **MWh perdidos**, mientras 2023–24 se aplican a **MWh consumidos**. **No usar la serie 2022 junto a 2023–24 sin confirmar la base con MINAM.** [NO VERIFICADO]

### 3.3 Metodología: ¿promedio de red o margen combinado?

**[NO VERIFICADO]** — no existe documento MINAM que lo declare explícitamente. Evidencia circunstancial fuerte de que es **factor promedio de red (generación)**, no margen combinado:

- Los valores de margen combinado MDL en Perú son ~2,5–3× mayores: **0,52144 tCO2eq/MWh** (Poechos II, MDL 2017) y **0,4367 tCO2e/MWh** (MINEM 2016) — ambos [SECUNDARIO].
- La Guía HC-Perú ancla los factores a INFOCARBONO, cuyo inventario nacional es por naturaleza un promedio (emisiones totales ÷ generación total).

> ⛔ **NO usar 0,52144 ni 0,4367 para Alcance 2 en HC-Perú:** pertenecen al marco MDL y a otros años.

### 3.4 Marco normativo peruano

| Ítem | Dato | Etiqueta |
|---|---|---|
| Guía vigente | **RM N° 185-2021-MINAM**, *Guía para el funcionamiento de la herramienta Huella de Carbono Perú* (2ª versión), 13-oct-2021 | [VERIFICADO] |
| Deroga | RM N° 237-2020-MINAM (23-nov-2020) | [VERIFICADO] |
| ¿Aprueba valores numéricos? | **NO.** Ni la RM ni la guía traen tabla de factores | [VERIFICADO] |
| Vigencia a sep-2026 | **Sigue vigente**; no hay tercera versión de la guía | [VERIFICADO] |
| Carácter | **Voluntario** (programa de reconocimiento, no obligación de reporte) | [VERIFICADO] |

### 3.5 Factores de combustibles en Perú

**HC-Perú no publica factores propios de combustible.** Usa **defaults del IPCC 2006** combinados con **poderes caloríficos peruanos** de INFOCARBONO.

Fuente primaria: **RAGEI 2019 Sector Energía, Tabla 17** (MINEM/DGEE, Lima 2023) [VERIFICADO]
https://infocarbono.minam.gob.pe/wp-content/uploads/2023/05/Informe-RAGEI_2019_Energia_CE_EF_VF.pdf

| Combustible | CO2 (kg/TJ) | CH4 (kg/TJ) ¹ | N2O (kg/TJ) ¹ | Etiqueta |
|---|---|---|---|---|
| Gas/Diésel Oil (**diésel / DB5**) | 74 100 | 3,00 | 0,60 | [VERIFICADO] |
| Gasolina para motores (**gasohol**) | 69 300 | 3,00 | 0,60 | [VERIFICADO] |
| **Gas natural (FACTOR NACIONAL PERUANO)** | **56 293** | 1,00 | 0,10 | [VERIFICADO] |
| Gas Natural Licuado | 64 200 | 3,00 | 0,60 | [VERIFICADO] |
| **GLP** | 63 100 | 1,00 | 0,10 | [VERIFICADO] |
| **Fuelóleo residual / petróleo industrial** | 77 400 | 3,00 | 0,60 | [VERIFICADO] |
| Antracita (**carbón**) | 98 300 | 1,00 | 1,50 | [VERIFICADO] |
| Carbón de coque | 94 600 | 1,00 | 1,50 | [VERIFICADO] |
| Kerosene | 71 900 | 3,00 | 0,60 | [VERIFICADO] |
| Biogasolina | 70 800 | 3,00 | 0,60 | [VERIFICADO] |
| Biodiésel | 70 800 | 3,00 | 0,60 | [VERIFICADO] |
| Madera / desechos de madera (leña) | 112 000 | 300,00 | 4,00 | [VERIFICADO] |
| Carbón vegetal | 112 000 | 200,00 | 4,00 | [VERIFICADO] |
| Otra biomasa sólida primaria | 100 000 | 30,00 | 4,00 | [VERIFICADO] |
| Gas de vertedero | 54 600 | 1,00 | 0,10 | [VERIFICADO] |

¹ Columna de industrias energéticas y manufactureras (1A1/1A2). Para 1A4a/1A4b/1A4c los CH4/N2O difieren (ej. líquidos: 10,00 kgCH4/TJ).

**Gases incluidos: CO2, CH4, N2O.**

> **Dato diferenciador de Perú:** el **gas natural usa factor nacional propio, 56 293 kg CO2/TJ** (RAGEI Tabla 33), vs el default IPCC de 56 100 (+0,34 %), dentro del rango IPCC 54 300–58 300. Derivado de un promedio de 35,84 MJ/m³. [VERIFICADO]

### 3.6 Poderes caloríficos netos peruanos — RAGEI Tabla 18

[VERIFICADO] **Nota de unidades: Perú usa TJ/galón para líquidos**, no TJ/Gg.

| Combustible | VCN | Unidad | Fuente citada |
|---|---|---|---|
| **Diésel** | 1,35E-04 | TJ/galón | REPSOL |
| **Gasolina** | 1,18E-04 | TJ/galón | REPSOL |
| **GLP** | 2,64E-02 | TJ/m³ | REPSOL y PETROPERU |
| **Gas Natural** | 3,60E-05 | TJ/m³ | Calidda |
| Petróleo Industrial 500 | 1,51E-04 | TJ/galón | REPSOL y PETROPERU |
| Petróleo Industrial 6 | 1,50E-04 | TJ/galón | REPSOL y PETROPERU |
| Petróleo Industrial | 1,51E-04 | TJ/galón | REPSOL y PETROPERU |
| Bagazo | 1,16E-02 | TJ/t | IPCC GL2006 |

> ⚠️ Las filas de carbón vegetal, carbón mineral, gas de refinería, etanol, biocombustible y biogás salieron **desalineadas** en la extracción de texto. Los valores existen (2,95E-02; 2,67E-02; 6,49E-05; 9,05E-05; 9,05E-05; 6,12E-05) pero **no se pudieron asignar con certeza a cada fila**. Ver §10.2. [NO VERIFICADO]

**Conversión útil:** 1 galón US = 3,785411784 litros. Diésel: 1,35E-04 TJ/gal ÷ 3,785411784 = **3,5665E-05 TJ/litro** [CALCULADO].

### 3.7 PCG usados por Huella de Carbono Perú

**Respuesta: AR5 (100 años). NO AR6.** [VERIFICADO]

| Evidencia | Etiqueta |
|---|---|
| RAGEI 2019 Sector Energía: declara usar el PCG del *"Quinto Informe de Evaluación (AR5)"* | [VERIFICADO — primario] |
| RAGEI 2019, tabla de recálculos ítem 8: *"Se cambió los PCG… de los reportados por el IPCC AR2 a AR5"* | [VERIFICADO — primario] |
| Guía HC-Perú §6.4.2: factores se adecúan a INFOCARBONO → hereda AR5 | [VERIFICADO — primario] |
| COFIDE 2024 (verificado por SGS): *"El programa voluntario 'Huella de Carbono Perú' usa AR5 y no el AR6"* | [SECUNDARIO] |

Valores AR5 en uso: CO2=1; CH4=28 (biogénico)/30 (fósil); N2O=265; SF6=23 500; NF3=16 100 [SECUNDARIO].

**Histórico:** la Guía N°1 INFOCARBONO (2016) usaba **SAR** (CH4=21, N2O=310) — **superada** [VERIFICADO].

**¿Migración a AR6 en 2024–2026?** **[NO VERIFICADO]** — sin evidencia de cambio. Nota: algunas empresas reportan en AR6 por decisión propia, no porque HC-Perú lo exija.

> **Coincidencia útil para el motor:** **Chile y Perú usan ambos AR5.** Un solo set de PCG cubre los dos países.

### 3.8 Actualizaciones normativas Perú 2024–2026

| Norma | Fecha | Contenido | Etiqueta |
|---|---|---|---|
| **D.S. N° 010-2024-MINAM** | nov-2024 | Funcionamiento del **RENAMI**. Obligatorio para autoridades sectoriales y formuladores de medidas de mitigación del mercado de carbono. Reporte en los primeros 60 días hábiles del año | [VERIFICADO] |
| **RD N° 00001-2025-MINAM/VMDERN/DGCCD** | 30-ene-2025 | Reconoce de oficio los estándares **GS4CC** (Gold Standard) y **VCS** (Verra) + 4 metodologías | [VERIFICADO — texto completo leído] |
| **RD N° D000003-2026-MINAM-VMDERN-DGCCD** | ~jun-2026 | Incorpora **Protocolo de Cercarbono** y **TREES** + 17 metodologías | [SECUNDARIO] |
| RM N° 309-2024-MINAM | 2024 | Proyecto: metodología de contabilidad en **UTCUTS** (bosques amazónicos) | [SECUNDARIO] |
| **Resolución N° 001-2026-EF/30** (Consejo Normativo de Contabilidad) | 2026 | Adopta **NIIF S1 y NIIF S2** (ISSB). Umbral: ingresos ≥ **2 300 UIT**. **Obligatoria desde 1-ene-2029** | [SECUNDARIO] |
| Ley N° 30754 (LMCC) + D.S. 013-2019-MINAM | 2018/2019 | Marco base — **sin modificación** detectada en 2024–2026 | [VERIFICADO] |

> ⚠️ Sobre la Res. 001-2026-EF/30 las fuentes secundarias dan fechas distintas (18-mar-2026 / 23-jun-2026 / "abril 2026"). **Fecha no confirmada en El Peruano.** [NO VERIFICADO]

---

## 4. IPCC 2006 Vol.2 — Factores por defecto, poderes caloríficos y densidades

Fuentes primarias [7]:
- Cap.1 Introducción: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_1_Ch1_Introduction.pdf
- Cap.2 Combustión estacionaria: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_2_Ch2_Stationary_Combustion.pdf
- Cap.3 Combustión móvil: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/2_Volume2/V2_3_Ch3_Mobile_Combustion.pdf

### 4.0 ⚠️ Estado del Refinamiento 2019 — NINGÚN valor cambió

[VERIFICADO] Leído en los PDF del *2019 Refinement*:

| Capítulo | Estado |
|---|---|
| Vol.2 Cap.1 (Tablas 1.2, 1.3, 1.4) | **"No refinement"** — siguen vigentes sin cambios |
| Vol.2 Cap.2 §2.3.2 *Choice of emission factors* | **"No refinement"** — Cuadros 2.2–2.5 vigentes sin cambios |
| Vol.2 Cap.3 (Combustión móvil) | **"No Refinement"** — el capítulo entero no se refinó |

> **Conclusión para 2026: se usan los valores del 2006 GL tal cual.** Lo único refinado en el Cap.2 fue §2.3.3.4 (tratamiento conceptual de biomasa, sin valores nuevos).

### 4.1 Combustión estacionaria — Cuadro 2.3, Industrias manufactureras y construcción (1A2)

Unidad: **kg GEI/TJ sobre poder calorífico NETO**. [VERIFICADO]

| Combustible | CO2 def. | CO2 inf. | CO2 sup. | CH4 def. | CH4 inf. | CH4 sup. | N2O def. | N2O inf. | N2O sup. |
|---|---|---|---|---|---|---|---|---|---|
| Gas/Diesel Oil (gasóleo) | 74 100 | 72 600 | 74 800 | 3 | 1 | 10 | 0,6 | 0,2 | 2 |
| Motor Gasoline | 69 300 | 67 500 | 73 000 | 3 | 1 | 10 | 0,6 | 0,2 | 2 |
| Liquefied Petroleum Gases (GLP) | 63 100 | 61 600 | 65 600 | 1 | 0,3 | 3 | 0,1 | 0,03 | 0,3 |
| Natural Gas | 56 100 | 54 300 | 58 300 | 1 | 0,3 | 3 | 0,1 | 0,03 | 0,3 |
| Other Kerosene | 71 900 | 70 800 | 73 700 | 3 | 1 | 10 | 0,6 | 0,2 | 2 |
| Residual Fuel Oil | 77 400 | 75 500 | 78 800 | 3 | 1 | 10 | 0,6 | 0,2 | 2 |
| Other Bituminous Coal | 94 600 | 89 500 | 99 700 | 10 | 3 | 30 | 1,5 | 0,5 | 5 |
| **Wood/Wood Waste (leña)** | **112 000** | 95 000 | 132 000 | **30** | 10 | 100 | **4** | 1,5 | 15 |

### 4.2 Combustión estacionaria — Cuadro 2.4, Comercial/Institucional (1A4a)

**Este es el cuadro que usa HuellaChile** (§2.1). Unidad: kg GEI/TJ, base NETA. [VERIFICADO]

| Combustible | CO2 def. | CO2 inf. | CO2 sup. | CH4 def. | CH4 inf. | CH4 sup. | N2O def. | N2O inf. | N2O sup. |
|---|---|---|---|---|---|---|---|---|---|
| Gas/Diesel Oil (gasóleo) | 74 100 | 72 600 | 74 800 | **10** | 3 | 30 | 0,6 | 0,2 | 2 |
| Motor Gasoline | 69 300 | 67 500 | 73 000 | **10** | 3 | 30 | 0,6 | 0,2 | 2 |
| Liquefied Petroleum Gases (GLP) | 63 100 | 61 600 | 65 600 | **5** | 1,5 | 15 | 0,1 | 0,03 | 0,3 |
| Natural Gas | 56 100 | 54 300 | 58 300 | **5** | 1,5 | 15 | 0,1 | 0,03 | 0,3 |
| Other Kerosene | 71 900 | 70 800 | 73 700 | **10** | 3 | 30 | 0,6 | 0,2 | 2 |
| Residual Fuel Oil | 77 400 | 75 500 | 78 800 | **10** | 3 | 30 | 0,6 | 0,2 | 2 |
| Other Bituminous Coal | 94 600 | 89 500 | 99 700 | 10 | 3 | 30 | 1,5 | 0,5 | 5 |
| **Wood/Wood Waste (leña)** | **112 000** | 95 000 | 132 000 | **300** | 100 | 900 | **4** | 1,5 | 15 |

> **Regla clave para el motor de cálculo:** el **CO2 es IDÉNTICO** en los Cuadros 2.2, 2.3, 2.4 y 2.5 (depende solo del contenido de carbono del combustible). Lo que cambia entre categorías de actividad son **CH4 y N2O**. Por tanto basta con una tabla de CO2 y una matriz `(combustible × categoría)` para CH4/N2O.
>
> *Errata del original:* en el Cuadro 2.4 la fila "Coal Tar" imprime CH4 = 10 con límite inferior 30 (inconsistente); así aparece en el PDF oficial.

### 4.3 CH4 / N2O en las demás categorías estacionarias (Cuadros 2.2 y 2.5)

[VERIFICADO] El CO2 es el mismo de §4.1/§4.2.

| Combustible | 2.2 Energy Ind. CH4 | 2.2 N2O | 2.5 Residencial/Agric. CH4 | 2.5 N2O |
|---|---|---|---|---|
| Gas/Diesel Oil | 3 (1–10) | 0,6 (0,2–2) | 10 (3–30) | 0,6 (0,2–2) |
| Motor Gasoline | 3 (1–10) | 0,6 (0,2–2) | 10 (3–30) | 0,6 (0,2–2) |
| GLP | 1 (0,3–3) | 0,1 (0,03–0,3) | 5 (1,5–15) | 0,1 (0,03–0,3) |
| Natural Gas | 1 (0,3–3) | 0,1 (0,03–0,3) | 5 (1,5–15) | 0,1 (0,03–0,3) |
| Other Kerosene | 3 (1–10) | 0,6 (0,2–2) | 10 (3–30) | 0,6 (0,2–2) |
| Other Bituminous Coal | 1 (0,3–3) | 1,5 (0,5–5) | 300 (100–900) | 1,5 (0,5–5) |
| Wood/Wood Waste | 30 (10–100) | 4 (1,5–15) | 300 (100–900) | 4 (1,5–15) |

### 4.4 Combustión móvil terrestre — Cuadro 3.2.1 (CO2)

[VERIFICADO] kg CO2/TJ, base NETA. Asumen 100 % de oxidación del carbono; los valores provienen de la Tabla 1.4 del Cap.1.

| Fuel Type | CO2 def. | Inf. | Sup. |
|---|---|---|---|
| Motor Gasoline | 69 300 | 67 500 | 73 000 |
| Gas/Diesel Oil | 74 100 | 72 600 | 74 800 |
| Liquefied Petroleum Gases (GLP) | 63 100 | 61 600 | 65 600 |
| Kerosene | 71 900 | 70 800 | 73 700 |
| **Compressed Natural Gas (GNC/CNG)** | **56 100** | 54 300 | 58 300 |
| Liquefied Natural Gas (GNL) | 56 100 | 54 300 | 58 300 |
| Lubricants | 73 300 | 71 900 | 75 200 |

### 4.5 Combustión móvil terrestre — Cuadro 3.2.2 (CH4 y N2O)

[VERIFICADO] kg/TJ, base NETA.

| Fuel Type / tecnología de control | CH4 def. | CH4 inf. | CH4 sup. | N2O def. | N2O inf. | N2O sup. |
|---|---|---|---|---|---|---|
| Motor Gasoline — **Uncontrolled** | 33 | 9,6 | 110 | 3,2 | 0,96 | 11 |
| Motor Gasoline — **Oxidation Catalyst** | 25 | 7,5 | 86 | 8,0 | 2,6 | 24 |
| Motor Gasoline — **Low Mileage LDV, 1995 o posterior** | 3,8 | 1,1 | 13 | 5,7 | 1,9 | 17 |
| Gas/Diesel Oil | 3,9 | 1,6 | 9,5 | 3,9 | 1,3 | 12 |
| **Natural Gas (GNC)** | **92** | 50 | 1 540 | **3** | 1 | 77 |
| **Liquefied petroleum gas (GLP)** | **62** | n.d. | n.d. | **0,2** | n.d. | n.d. |
| Ethanol, trucks, US | 260 | 77 | 880 | 41 | 13 | 123 |
| Ethanol, cars, Brazil | 18 | 13 | 84 | n.d. | n.d. | n.d. |

> **Advertencias del propio cuadro IPCC [VERIFICADO]:**
> - **No existe un valor único de "Motor Gasoline"**: hay que elegir la tecnología de control. Para flotas modernas (post-1995 con catalizador) corresponde *Low Mileage LDV 1995 or Later* (CH4 3,8 / N2O 5,7).
> - **HuellaChile usa CH4 = 25 / N2O = 8 para gasolina móvil** (§2.3), es decir, la fila *Oxidation Catalyst*. Es una elección conservadora y deliberada del MMA.
> - **GLP: sin rangos de incertidumbre.** El valor de 62 kg CH4/TJ se derivó asumiendo 50 MJ/kg de PCI, que **no coincide** con el PCI por defecto de la Tabla 1.2 (47,3 TJ/Gg).
> - **Gas natural:** el rango superior de CH4 (1 540) y N2O (77) es enorme; la incertidumbre es muy alta.

### 4.6 Poderes caloríficos netos por defecto — Tabla 1.2 (TJ/Gg)

[VERIFICADO] Los límites son el intervalo de confianza del 95 %. *1 TJ/Gg = 1 GJ/t = 1 MJ/kg.*

| Combustible | NCV (TJ/Gg) | Inferior | Superior |
|---|---|---|---|
| Motor Gasoline | **44,3** | 42,5 | 44,8 |
| Gas/Diesel Oil | **43,0** | 41,4 | 43,3 |
| Liquefied Petroleum Gases | **47,3** | 44,8 | 52,2 |
| Natural Gas | **48,0** | 46,5 | 50,4 |
| Other Kerosene | **43,8** | 42,4 | 45,2 |
| Residual Fuel Oil | **40,4** | 39,8 | 41,7 |
| Other Bituminous Coal | **25,8** | 19,9 | 30,5 |
| Wood/Wood Waste | **15,6** | 7,90 | 31,0 |

Extras útiles: Jet Kerosene 44,1 (42,0–45,0); Crude Oil 42,3 (40,1–44,8); Anthracite 26,7; Lignite 11,9; Charcoal 29,5; Biodiesels 27,0; Landfill Gas 50,4. [VERIFICADO]

### 4.7 Tablas 1.3 y 1.4 — Contenido de carbono y CO2

[VERIFICADO] Tabla 1.4 = Tabla 1.3 × factor de oxidación (**siempre 1,0**) × 44/12 × 1000. Todos los CO2 de los Cuadros 2.x y 3.2.1 salen de aquí.

| Combustible | C (kg/GJ) — T.1.3 | CO2 (kg/TJ) — T.1.4 |
|---|---|---|
| Motor Gasoline | 18,9 | 69 300 |
| Gas/Diesel Oil | 20,2 | 74 100 |
| Liquefied Petroleum Gases | 17,2 | 63 100 |
| Natural Gas | 15,3 | 56 100 |
| Other Kerosene | 19,6 | 71 900 |
| Residual Fuel Oil | 21,1 | 77 400 |
| Other Bituminous Coal | 25,8 | 94 600 |
| Wood/Wood Waste | 30,5 | 112 000 |

### 4.8 Densidades para convertir litros → kg

**⚠️ CONFIRMADO: el IPCC 2006 NO publica densidades** en las Tablas 1.2/1.3/1.4 ni en los Cuadros 2.x/3.2.x. [VERIFICADO por ausencia] Hay que usar otra fuente y **documentar cuál**.

**Opción A — Chile: usar el BNE 2024 (§2.4).** Es la fuente oficial nacional y la que usa HuellaChile. **Recomendada para Chile.**

**Opción B — Internacional: UNSD Energy Statistics Yearbook 2009, Tabla IV** [VERIFICADO]
https://unstats.un.org/unsd/energy/yearbook/2009/2009_xliv.pdf

| Producto (nombre UNSD) | L/tonelada (publicado) | kg/L (= 1000 ÷ L/t) |
|---|---|---|
| Motor gasolene (gasolina) | 1 351 | **0,740** |
| Gas-diesel oil (diésel) | 1 149 | **0,870** |
| Kerosene | 1 235 | **0,810** |
| Liquefied petroleum gas (GLP) | 1 852 | **0,540** |
| Residual fuel oil | 1 053 | 0,950 |
| Jet fuel | 1 235 | 0,810 |
| Crude petroleum (promedio) | 1 164 | 0,859 |

**Opción C — Colombia: UPME / FECOC, Tabla 2** [VERIFICADO]
https://app.upme.gov.co/Calculadora_Emisiones1/new/Informe_Final_FECOC_Correcciones_UPME_FunNatura.pdf

| Combustible | Densidad (kg/L) | PCS (kJ/kg) | PCI (kJ/kg) |
|---|---|---|---|
| Gasolina Motor | 0,741 | 48 317 | 45 329,53 |
| Diésel | 0,856 | 45 338 | 42 326,53 |
| GLP Genérico | 0,560 | 49 065 | 45 414,53 |
| Jet A1 (queroseno) | 0,826 | 38 488 | 35 576,91 |

**Opción D — Normas EN 228 / EN 590** [SECUNDARIO — texto normativo CEN de pago, valores vía resúmenes técnicos]

| Norma | Producto | Densidad @15 °C |
|---|---|---|
| EN 228 | Gasolina sin plomo | 720–775 kg/m³ |
| EN 590 | Diésel automoción (ULSD) | 820–845 kg/m³ |

**Comparativa y dispersión real [CALCULADO]:**

| Combustible | Chile BNE | UNSD | FECOC | EN | Dispersión |
|---|---|---|---|---|---|
| Gasolina | 0,730 | 0,740 | 0,741 | 0,720–0,775 | ~2 % |
| **Diésel** | **0,840** | **0,870** | **0,856** | **0,820–0,845** | **~5 %** |
| GLP | 0,550 | 0,540 | 0,560 | — | ~4 % |
| Kerosene | 0,810 | 0,810 | 0,826 | — | ~2 % |

> **Recomendación para el motor:** el diésel tiene una dispersión real de ~5 % según el mercado. **Para Chile usar 0,84 (BNE 2024); para Perú y UE documentar explícitamente la fuente elegida.** Nunca mezclar densidad de una fuente con poder calorífico de otra.

### 4.9 Poder calorífico NETO (NCV/LHV) vs BRUTO (GCV/HHV)

**Definiciones — IPCC 2006 Vol.2 Cap.1, Recuadro 1.1** [VERIFICADO]:
- **GCV / HHV (bruto / superior):** valor calorífico medido en condiciones de laboratorio.
- **NCV / LHV (neto / inferior):** valor calorífico útil en planta de caldera.
- La diferencia es esencialmente el **calor latente del vapor de agua** producido en la combustión.

**Factor de conversión IPCC — §1.4.1.2** [VERIFICADO]:

| Tipo de combustible | Relación | Fórmula |
|---|---|---|
| Carbón y petróleo (sólidos y líquidos) | NCV ≈ GCV − 5 % | `NCV = GCV × 0,95` |
| Gas natural y gases manufacturados | NCV ≈ GCV − 10 % | `NCV = GCV × 0,90` |

Estos son exactamente los coeficientes que aplica HuellaChile (§8.2). [VERIFICADO]

**Fórmula exacta (ISO, base "as received", MJ/kg)** — Recuadro 1.1 [VERIFICADO]:
```
Net CV = Gross CV − 0,212·H − 0,0245·M − 0,008·Y
```
donde H = % hidrógeno, M = % humedad, Y = % oxígeno del análisis último.

> ⚠️ **Error de cálculo más común:** aplicar un factor del IPCC (definido sobre base NETA) a una cifra de energía expresada en base BRUTA. Sobreestima el CO2 en **~5 %** (líquidos/sólidos) o **~11 %** en gas natural (porque 1/0,90 = 1,111). **Verificar siempre la base antes de multiplicar.**
>
> El Reino Unido factura en base **GCV**, al revés del IPCC. Por eso DESNZ publica ambas bases y hay que usar el factor Gross CV para el gas natural facturado (§7.2). [VERIFICADO]

### 4.10 Implicación: factor de leña para Chile

El IPCC **sí** publica factores para *Wood/Wood Waste* (§4.1/§4.2), que HuellaChile no incorporó (§2.2). Si el motor necesita cubrir leña en Chile:

```
CO2 biogénico  → 112 000 kg/TJ, se reporta FUERA DE ALCANCES (no suma al Alcance 1)
CH4 + N2O      → SÍ van a Alcance 1
```

Con Cuadro 2.4 (Comercial/Institucional), PCG AR5 y PCI de biomasa del BNE (3 500 kcal/kg × 0,95):
```
PCI = 3 325 kcal/kg → E = 3 325 × 4,1868 × 1000 / 1e9 = 0,013921 TJ/t
CH4: 0,013921 × 300 × 28  = 116,94 kgCO2e/t
N2O: 0,013921 × 4   × 265 = 14,75  kgCO2e/t
Alcance 1 (no biogénico) ≈ 131,7 kgCO2e/t de leña
CO2 biogénico (fuera de alcances) = 0,013921 × 112 000 = 1 559,2 kgCO2e/t
```
> **[CALCULADO] — NO es un factor oficial de HuellaChile.** Marcar como estimación propia en el motor y advertirlo al usuario. La humedad de la leña afecta fuertemente el PCI real.

---

## 5. PCG a 100 años — AR5 y AR6

> ⏳ **EN INVESTIGACIÓN.** Sección pendiente de completar.
>
> **Ya confirmado:** HuellaChile usa **AR5** [VERIFICADO, §2.5]. DESNZ 2026 usa **AR5** [VERIFICADO, §7.5].

---

## 6. Alcance 2 basado en mercado en Chile (I-REC, mezcla residual)

> ⏳ **EN INVESTIGACIÓN.** Sección pendiente de completar.

---

## 7. Reino Unido — DESNZ 2026 (año más reciente)

### 7.1 Publicación vigente

| Concepto | Dato | Etiqueta |
|---|---|---|
| Año más reciente a sept-2026 | **2026** | [VERIFICADO] |
| Fecha de publicación | **11 de junio de 2026** | [VERIFICADO] |
| Última actualización | 31 de julio de 2026 (corrección del *flat file*) | [VERIFICADO] |
| Organismo | Department for Energy Security and Net Zero (**DESNZ**) — ya no BEIS ni Defra | [VERIFICADO] |
| PCG usados | **AR5**, horizonte 100 años | [VERIFICADO] |
| Próxima publicación | Junio 2027 | [VERIFICADO] |

### 7.2 Combustibles — Alcance 1 (hoja `Fuels`, 2026)

Columnas oficiales: `kg CO2e` (total) y el desglose en **kgCO2e *de* cada gas** (ya multiplicado por su PCG), no masa de gas.

| Combustible | Unidad | **Total kgCO2e** | de CO2 | de CH4 | de N2O | Etiqueta |
|---|---|---|---|---|---|---|
| **Diesel (average biofuel blend)** | litro | **2,58354** | 2,55035 | 0,00029 | 0,03290 | [VERIFICADO] |
| **Petrol (average biofuel blend)** | litro | **2,07500** | 2,06107 | 0,00806 | 0,00587 | [VERIFICADO] |
| Diesel (100% mineral diesel) | litro | 2,66155 | 2,62818 | 0,00029 | 0,03308 | [VERIFICADO] |
| Petrol (100% mineral petrol) | litro | 2,35372 | 2,33955 | 0,00820 | 0,00597 | [VERIFICADO] |
| **Natural gas** | **kWh (Gross CV)** | **0,18231** | 0,18194 | 0,00028 | 0,00009 | [VERIFICADO] |
| Natural gas | kWh (Net CV) | 0,20199 | 0,20158 | 0,00031 | 0,00010 | [VERIFICADO] |
| Natural gas | m³ | 2,02633 | 2,02231 | 0,00307 | 0,00095 | [VERIFICADO] |
| **LPG** | **litro** | **1,55713** | 1,55491 | 0,00136 | 0,00086 | [VERIFICADO] |
| LPG | kWh (Gross CV) | 0,21450 | 0,21419 | 0,00019 | 0,00012 | [VERIFICADO] |

> **Gross CV vs Net CV:** la hoja oficial indica que la facturación energética suele darse en **Gross CV** (= PCS/HHV) y el transporte en **Net CV** (= PCI/LHV). **Para gas natural facturado en el Reino Unido usar 0,18231 (Gross CV).** [VERIFICADO]
>
> **Regla oficial:** toda organización que reporte gas natural debe usar el factor "natural gas" de red, no el "100% mineral blend" [VERIFICADO].

### 7.3 Alcance 1 vs WTT (Alcance 3)

**La hoja `Fuels` es SOLO Alcance 1 (combustión)** — su celda B6 dice literalmente `Scope 1`. El **WTT es una hoja separada** (`WTT- fuels`), clasificada como **Alcance 3**, y **solo publica el total kgCO2e, sin desglose por gas** [VERIFICADO].

| Combustible | Alcance 1 (litro) | Alcance 3 WTT (litro) | Etiqueta |
|---|---|---|---|
| Diesel (average biofuel blend) | 2,58354 | 0,61101 | [VERIFICADO] |
| Petrol (average biofuel blend) | 2,07500 | 0,58094 | [VERIFICADO] |
| LPG | 1,55713 | 0,18551 | [VERIFICADO] |
| Natural gas (por kWh Gross CV) | 0,18231 | 0,03021 | [VERIFICADO] |

**CO2 biogénico ("outside of scopes"):** los blends con biocombustible obligan a reportar aparte la porción biogénica — Diesel blend **0,14** kgCO2e/litro; Petrol blend **0,13** kgCO2e/litro. No suma al total [VERIFICADO].

### 7.4 Electricidad UK 2026 (referencia)

| Concepto | Alcance | kgCO2e/kWh | Etiqueta |
|---|---|---|---|
| Electricity generated | **2** | **0,13096** | [VERIFICADO] |
| T&D — UK electricity | 3 | 0,01299 | [VERIFICADO] |
| WTT — generación | 3 | 0,03682 | [VERIFICADO] |
| WTT — T&D | 3 | 0,00359 | [VERIFICADO] |
| **Ciclo de vida total** | — | **0,18436** | [CALCULADO] (suma de los 4 anteriores) |

### 7.5 Licencia y atribución

| Concepto | Dato | Etiqueta |
|---|---|---|
| Licencia | **Open Government Licence v3.0 (OGL v3)** | [VERIFICADO] |
| URL de la licencia | https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ | [VERIFICADO] |
| ¿DESNZ exige una cita concreta? | **No.** Aplica la fórmula estándar de la OGL v3 | [VERIFICADO] |

**Texto de atribución exacto exigido por OGL v3** [VERIFICADO]:

```
Contains public sector information licensed under the Open Government Licence v3.0.
```

La OGL v3 obliga además a **enlazar la licencia**. Atribución recomendada para el repositorio (construida, no prescrita):

```
Department for Energy Security and Net Zero (2026), UK Government GHG Conversion
Factors for Company Reporting 2026. Contains public sector information licensed
under the Open Government Licence v3.0.
https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026
https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
```

> **Compatibilidad de licencias:** OGL v3 es compatible con CC-BY 4.0. Los factores DESNZ pueden redistribuirse en un proyecto open source citando la atribución anterior. [SECUNDARIO — basado en la declaración de compatibilidad de la propia OGL v3]

---

## 8. Fórmulas y métodos

### 8.1 Alcance 1 — Combustión (fórmula general)

```
E_CO2e = Q × FE
```
- `Q` = cantidad de combustible consumido (litros, m³, kg, t)
- `FE` = factor de emisión de §2.1 / §2.3 (kgCO2e por esa misma unidad)

### 8.2 Alcance 1 — Reconstrucción del factor desde primeros principios (método HuellaChile)

Esta es la cadena exacta que usa HuellaChile [VERIFICADO en la hoja de cálculo oficial]:

```
PCI = PCS × f_estado                      f_estado = 0,95 (sólidos y líquidos) | 0,90 (gaseosos)
E_unidad [TJ/unidad] = PCI [kcal/kg] × 4,1868 [kJ/kcal] × densidad [t/m³] × 1000 [kg/t] / 1e9 [kJ/TJ]
FE [kgCO2e/m³] = E_unidad × (CO2_kg/TJ × 1 + CH4_kg/TJ × 28 + N2O_kg/TJ × 265)
```

**Constantes oficiales [VERIFICADO]:**

| Constante | Valor | Fuente |
|---|---|---|
| 1 kcal | 4,1868 kJ | IPCC, Annex II: Metrics & Methodology |
| 1 TJ | 1 000 000 000 kJ | — |
| PCI/PCS combustibles **sólidos y líquidos** | **0,95** | IPCC Vol.2 Cap.1 (intervalo de confianza) |
| PCI/PCS combustibles **gaseosos** | **0,90** | IPCC Vol.2 Cap.1 (intervalo de confianza) |
| PCG CO2 / CH4 / N2O | 1 / 28 / 265 | IPCC **AR5** |

> ⚠️ **Detalle crítico 1:** el BNE 2024 publica **poder calorífico SUPERIOR (PCS/GCV)**, y HuellaChile lo convierte a **INFERIOR (PCI/NCV)** antes de aplicar los factores IPCC, que están definidos sobre PCI. Omitir este paso sobreestima las emisiones ~5 %.

> ⚠️ **Detalle crítico 2 — clasificación de estado (fuente de error frecuente):** el coeficiente 0,95 vs 0,90 **NO** depende de la familia IPCC del combustible, sino de la columna *"Estado del combustible"* del libro oficial. **HuellaChile clasifica el GLP como LÍQUIDO (0,95), no como gaseoso.** Clasificación oficial completa [VERIFICADO]:

| Estado en HuellaChile | Coef. PCI/PCS | Combustibles |
|---|---|---|
| **Líquido** | **0,95** | Diésel (Petróleo 2), Gasolina, Kerosene, Nafta, Petróleo 5, Petróleo 6, **GLP**, **Gas de refinería** |
| **Sólido** | **0,95** | Carbón térmico, Carbón metalúrgico, Petcoke |
| **Gaseoso** | **0,90** | Gas natural, Gas ciudad, Gas de alto horno |

> Nota: que el **gas de refinería** figure como "Líquido" es una anomalía de la fuente (es un gas), pero es lo que publica el libro oficial y lo que reproduce sus factores. Se documenta tal cual.

**Validación de la fórmula [CALCULADO]:** se reprodujeron **12 de 12** factores publicados de combustión estacionaria y móvil con error ≤ 5e-13, aplicando la tabla de estados anterior. La fórmula es exacta.

### 8.3 Ejemplo numérico verificable — Diésel estacionario en Chile

Datos de entrada:
- Densidad diésel = **0,84 t/m³** (BNE 2024)
- PCS diésel = **10 900 kcal/kg** (BNE 2024)
- IPCC Cuadro 2.4, Gas/Diesel Oil: CO2 = **74 100**, CH4 = **10**, N2O = **0,6** kg/TJ

Paso 1 — PCI:
```
PCI = 10 900 × 0,95 = 10 355 kcal/kg
```

Paso 2 — contenido energético por m³:
```
E = 10 355 kcal/kg × 4,1868 kJ/kcal × 0,84 t/m³ × 1 000 kg/t ÷ 1e9 kJ/TJ
E = 0,03641762376 TJ/m³
```

Paso 3 — emisiones por gas (kg/m³):
```
CO2 = 0,03641762376 × 74 100 = 2 698,545920616
CH4 = 0,03641762376 × 10     = 0,3641762376
N2O = 0,03641762376 × 0,6    = 0,021850574256
```

Paso 4 — agregación con PCG AR5:
```
CO2e = 2 698,545920616×1 + 0,3641762376×28 + 0,021850574256×265
CO2e = 2 698,545920616 + 10,1969346528 + 5,79040221784
CO2e = 2 714,5332574466 kgCO2e/m³
```

✔ **Coincide exactamente con el valor publicado: 2 714,5332574466397 kgCO2e/m³** [VERIFICADO].

**Caso de uso completo:** una PYME en Santiago consume 3 500 litros de diésel en su caldera durante 2025.
```
E = 3 500 L × 2,71453325744664 kgCO2e/L = 9 500,87 kgCO2e = 9,50 tCO2e  (Alcance 1)
```

### 8.3-bis Ejemplo del caso trampa — GLP estacionario

El GLP usa **CH4/N2O de la fila "gaseosa" del Cuadro 2.4** (5 / 0,1) pero **coeficiente PCI de LÍQUIDO (0,95)**:

```
PCI = 12 100 × 0,95 = 11 495 kcal/kg
E   = 11 495 × 4,1868 × 0,55 × 1 000 ÷ 1e9 = 0,026469993 TJ/m³
CO2e = 0,026469993 × (63 100×1 + 5×28 + 0,1×265)
     = 0,026469993 × 63 266,5
     = 1 674,6640209 kgCO2e/m³
```
✔ Coincide con el valor publicado **1 674,6640209139498** [VERIFICADO].

> Si se aplicara erróneamente 0,90 (por tratarlo como gas), el resultado sería **1 586,52 kgCO2e/m³**, un **−5,3 % de subestimación**.

### 8.4 Alcance 2 — Electricidad, método por ubicación (location-based)

```
E_alcance2 = Consumo_kWh × FE_sistema_eléctrico_año
```

**Ejemplo:** la misma PYME consume 120 000 kWh del SEN en 2025.
```
E = 120 000 kWh × 0,2467249809219505 kgCO2e/kWh = 29 606,998 kgCO2e = 29,61 tCO2e
```

Pérdidas de T&D asociadas (línea separada, NO sumar al Alcance 2):
```
E_T&D = 120 000 × 0,01406332391255118 = 1 687,60 kgCO2e = 1,69 tCO2e
```
Equivalente: `29 606,998 × 0,057 = 1 687,60` ✔ [CALCULADO]

### 8.5 Conversión litros ↔ kg (Chile)

```
masa_t = volumen_m³ × densidad_t/m³
```
| Combustible | 1 000 L pesan | Etiqueta |
|---|---|---|
| Diésel | 840 kg | [VERIFICADO] |
| Gasolina | 730 kg | [VERIFICADO] |
| GLP | 550 kg | [VERIFICADO] |
| Kerosene | 810 kg | [VERIFICADO] |

---

## 9. Cambios recientes (2024–2026)

### 9.1 ⚠️ Chile — Revisión retroactiva de los factores del SEN (CRÍTICO)

**Los factores del SEN fueron corregidos hacia arriba de forma retroactiva para 2021–2025.** El control de cambios oficial del libro lo declara: *"Se actualiza de manera retroactiva los factores de emisión desde 2021 a 2025"* [VERIFICADO] [1].

| Año | Valor ANTIGUO (PDF Nivel básico v3, 28-11-2024) | Valor VIGENTE (base v2, 04-05-2026) | Diferencia | Etiqueta |
|---|---|---|---|---|
| 2021 | 0,3907 | 0,4199378573275227 | **+7,5 %** | [VERIFICADO] ambos |
| 2022 | 0,3006 | 0,327362906277725 | **+8,9 %** | [VERIFICADO] ambos |
| 2023 | 0,2421 | 0,255873741774226 | **+5,7 %** | [VERIFICADO] ambos |

Unidad: kgCO2e/kWh.

> **Acción requerida para el motor de cálculo:** cualquier implementación que haya tomado los valores del PDF "Nivel básico" v3 (0,3907 / 0,3006 / 0,2421) está **desactualizada**. Usar los de §1.2. El PDF de nivel básico **no ha sido reeditado** desde noviembre de 2024 y sigue publicado en el sitio, lo que es una trampa real para usuarios no técnicos.

### 9.2 Chile — Otros cambios documentados

| Versión | Fecha | Cambio | Etiqueta |
|---|---|---|---|
| Base 2025 v1 | 2026 | Actualización retroactiva FE SEN y T&D 2021–2025 | [VERIFICADO] |
| Base 2025 v1 | 2026 | Actualización de densidades y poderes caloríficos al **BNE 2024** (sin variaciones respecto del anterior) | [VERIFICADO] |
| Base 2025 v1 | 2026 | Migración de factores de Alcance 3 a **DEFRA/DESNZ 2025** | [VERIFICADO] |
| **Base 2025 v2** | **2026-05-04** | Se renombra la fuente de los factores eléctricos para **indicar explícitamente que se usa AR5** | [VERIFICADO] |
| Base 2025 v2 | 2026-05-04 | Actualización de factores de vehículo eléctrico y van eléctrica, por cálculo propio de HuellaChile | [VERIFICADO] |
| — | pendiente | Sistemas eléctricos medianos 2025: **en espera de publicación** por Energía Abierta | [VERIFICADO] |

### 9.3 Chile — Verificación cruzada base 2024 (v6) vs base 2025 (v2)

HuellaChile publica una base por **año de reporte**. Se compararon ambas [VERIFICADO]:

| Comprobación | Resultado |
|---|---|
| FE del SEN 2018–2024 | **Idénticos** en ambas bases (incluida la corrección retroactiva) |
| FE del SEN 2025 | Solo presente en la base 2025 |
| Factores de combustión estacionaria y móvil | **Idénticos dígito a dígito** en ambas bases |

> **Implicación práctica:** el motor puede usar una única tabla de factores de combustible para 2024 y 2025. Solo el factor eléctrico depende del año de reporte. Aun así, conviene versionar la tabla por año, porque HuellaChile ya demostró que revisa valores retroactivamente (§9.1).

### 9.4 Reino Unido — DESNZ 2025 → 2026

Cuatro cambios, según la hoja oficial `What's new` [VERIFICADO]:

1. **Revisión del método de cálculo de la electricidad UK.** El método anterior dividía las emisiones del inventario nacional (GHGI) entre la generación total, con un **desfase de 2 años**; el nuevo usa datos más actuales del mix, **reduciendo el desfase a 1 año**. Impacto declarado: *"una disminución significativa del factor de electricidad"*.
2. **Factores ferroviarios actualizados** con datos de Office of Rail and Road (2025) y Transport for London (la última actualización de CO2 era de 2021 con datos pre-COVID de 2019).
3. **Nueva guía para vehículos eléctricos e híbridos enchufables** (qué pestaña usar para Alcance 1, 2 y 3) — solo texto, sin cambio de factores.
4. **Renombre de categorías HGV** y reordenación de tablas — sin cambio numérico.

| Factor | Unidad | 2025 | 2026 | Variación | Etiqueta |
|---|---|---|---|---|---|
| **Electricity generated (UK)** | kWh | 0,17700 | **0,13096** | **−26,0 %** | [VERIFICADO] |
| Diesel (average biofuel blend) | litro | 2,57082 | 2,58354 | +0,49 % | [VERIFICADO] |
| Petrol (average biofuel blend) | litro | 2,06916 | 2,07500 | +0,28 % | [VERIFICADO] |
| Diesel (100% mineral) | litro | 2,66155 | 2,66155 | sin cambio | [VERIFICADO] |
| Petrol (100% mineral) | litro | 2,33984 | 2,35372 | +0,59 % | [VERIFICADO] |
| Natural gas | kWh (Gross CV) | 0,18296 | 0,18231 | −0,36 % | [VERIFICADO] |
| LPG | litro | 1,55713 | 1,55713 | sin cambio | [VERIFICADO] |

> **NO hubo migración a AR6** en DESNZ ni en 2025 ni en 2026 [VERIFICADO].

---

## 10. Pendientes y dudas

### 10.1 Bloqueos de acceso encontrados

**Chile**

| Recurso | Problema | URL exacta |
|---|---|---|
| Ministerio de Energía — Indicadores ambientales FE del SEN | **HTTP 403 / conexión rechazada** en todos los intentos (WebFetch y navegador). No se pudo leer la página fuente primaria del Ministerio | https://energia.gob.cl/indicadores-ambientales-factor-de-emisiones-gei-del-sistema-electrico-nacional |
| Coordinador Eléctrico Nacional | **HTTP 403 / navegación denegada** | https://www.coordinador.cl/novedades/sistema-electrico-redujo-21-sus-emisiones-en-2023-y-se-espera-que-siga-creciendo-participacion-de-energia-renovable-variable/ |
| Energía Abierta — dataset descargable de FE | Redirige a un **XLSX en SharePoint de la CNE**; no leído | https://3b9x.short.gy/NbpSO1 → https://comisionenergia-my.sharepoint.com/:x:/g/personal/infoestadistica_cne_cl/IQCjzmz_JzmnRaMYs3v1mHVnAX7quhEFMVkcmz89F8UdvmA |
| Energía Abierta — visualización FE | La página es un contenedor JS; los valores no están en el HTML | https://energiaabierta.cne.cl/visualizaciones/factor-de-emision-sic-sing/ |

**Perú**

| Recurso | Problema | URL exacta |
|---|---|---|
| **Calculadora HC-Perú (tabla oficial de factores)** | **Requiere credenciales.** Es la ÚNICA fuente primaria con los valores numéricos del SEIN | https://huellacarbonoperu.minam.gob.pe/huellaperu/#/login |
| Anexo RM 185-2021 (Guía 2ª versión, texto íntegro) | **HTTP 403** (bloqueo anti-bot del CDN gob.pe) | https://cdn.www.gob.pe/uploads/document/file/2249723/ANEXO%20RM.%20185-2021-MINAM%20-%20Guia%20Funcionamiento%20HC-Peru.pdf.pdf |
| Anexo RM 110-2020 | HTTP 403 | https://cdn.www.gob.pe/uploads/document/file/868713/ANEXO_RM._110-2020-MINAM__GUIA_PARA_EL_FUNCIONAMIENTO_DE_LA_HUELLA_DE_CARBONO_PERU.pdf |
| Manuales y plantillas HC-Perú | Enlaces "Clic aquí" son handlers JavaScript sin `href`; destinos no resueltos | https://huellacarbonoperu.minam.gob.pe/huellaperu/#/metodoCalculo |

**Internacional**

| Recurso | Problema | URL exacta |
|---|---|---|
| DESNZ hoja `Fuel properties` (densidades oficiales UK) | Solo existe dentro del XLSX; no extraída | https://assets.publishing.service.gov.uk/media/6a29392bade52dc0882218a8/ghg-conversion-factors-2026-full-set.xlsx |
| IEA Energy Statistics Manual, Anexo 3 (densidades + GCV) | Tabla no extraíble del PDF (196 pp., probablemente vectorizada) | https://iea.blob.core.windows.net/assets/67fb0049-ec99-470d-8412-1ed9201e576f/EnergyStatisticsManual.pdf |
| SEAI (Irlanda) Conversion Factors | **HTTP 403 Forbidden** | https://www.seai.ie/data-and-insights/seai-statistics/conversion-factors |
| EN 228 / EN 590 (texto normativo) | Norma CEN **de pago** | https://standards.iteh.ai/catalog/standards/cen/afae4da1-e17c-4def-9e92-19752938de62/en-590-2025 |

> **Mitigación aplicada:** los factores del SEN se obtuvieron de la **base de datos oficial de HuellaChile (MMA)**, que reproduce los valores del Ministerio de Energía y **cita la URL de Energía Abierta como fuente**. Es fuente oficial primaria del MMA y secundaria respecto del Ministerio de Energía. **Queda pendiente el cotejo directo contra Energía Abierta.**

### 10.2 Dudas abiertas

1. **[NO VERIFICADO] Margen de operación (OM) del SEN chileno.** No se localizó publicación oficial de OM/BM/CM para Chile en 2024–2026. HuellaChile no lo usa. Si el motor necesita OM (p. ej. para proyectos de mitigación), hay que buscar fuente específica.
2. **[NO VERIFICADO] Factor SEN 2026.** Aún no publicado.
3. **[NO VERIFICADO] Factores 2025 de sistemas medianos** (Aysén, Magallanes, Los Lagos). Marcados literalmente "PENDIENTE" en la fuente oficial.
4. **[NO VERIFICADO] Leña / biomasa, Alcance 1 en Chile.** HuellaChile no publica factor de CH4/N2O para combustión de leña. No inventar uno.
5. **[NO VERIFICADO] Valor "0,444 tCO2e/MWh" para el SEN 2024** que aparece en resultados de buscador. **Contradice la fuente oficial (0,21314)**. Muy probablemente corresponda a otro país u otro concepto. **Descartado — no usar.**
6. **[NO VERIFICADO] Metodología exacta de Energía Abierta**: no se pudo confirmar en la fuente del Ministerio si el promedio anual es ponderado por generación o por inyección, ni el tratamiento de las importaciones/exportaciones.
7. **[NO VERIFICADO] Cambio de densidad del petrol 100% mineral en DESNZ** entre 2025 y 2026 (el factor por litro cambió pero el factor por tonelada no). Requiere leer la hoja `Fuel properties`.
8. **⚠️ DESNZ 2026 — revisión de julio 2026.** El *flat file* fue corregido el 31-jul-2026 "para corregir valores que salían como 0". Los valores reportados aquí provienen del *full set* (Version 1) y son internamente consistentes, pero conviene cotejar contra el flat file revisado: https://assets.publishing.service.gov.uk/media/6a6c9748862aaf18d9c62ac9/ghg-conversion-factors-2026-flat-format-revised.xlsx
9. **[NO VERIFICADO] Factores SEIN 2025 y 2026 de Perú.** No hay fuente pública; requieren login en la plataforma MINAM.
10. **[NO VERIFICADO] Base de la serie de pérdidas de T&D en Perú.** El valor 2022 es ~100× mayor que 2023–24 y parece aplicarse a MWh perdidos en vez de MWh consumidos. No reconciliado. **No usar la serie completa sin confirmar con MINAM.**
11. **[NO VERIFICADO] Metodología del factor SEIN peruano** (promedio de red vs OM/BM/CM). No documentada explícitamente por MINAM.
12. **[NO VERIFICADO] RAGEI Tabla 18, filas desalineadas.** Carbón vegetal, carbón mineral, gas de refinería, etanol, biocombustible y biogás: los valores existen (2,95E-02; 2,67E-02; 6,49E-05; 9,05E-05; 9,05E-05; 6,12E-05) pero no se pudieron asignar con certeza a cada fila. Requiere lectura visual de la pág. 46 del PDF.
13. **[NO VERIFICADO] Fecha oficial de la Resolución 001-2026-EF/30 (Perú).** Fuentes secundarias dan tres fechas distintas.
14. **[NO VERIFICADO] Densidades oficiales DESNZ** (hoja `Fuel properties`). Los valores de gasolina 0,750 / diésel 0,832 / kerosene 0,803 / GLP 0,530 kg/L circulan en recopiladores terciarios pero **no se verificaron** contra la hoja oficial.
15. **[NO VERIFICADO] Cambio de densidad del petrol 100 % mineral en DESNZ** entre 2025 y 2026 (el factor por litro cambió pero el factor por tonelada no).

**Recomendación operativa para Perú:** para un inventario auditable, solicitar a MINAM (huellacarbonoperu@minam.gob.pe) la tabla de factores del año de reporte, o extraerla de la calculadora con cuenta propia. Los valores de §3.1 son utilizables como referencia de trabajo, pero su trazabilidad documental es **indirecta**.

### 10.3 Archivos fuente para consulta directa (no procesados en su totalidad)

| Archivo | URL |
|---|---|
| HuellaChile FE 2025 Org y Ev v2 — **versión completa** | https://huellachile.mma.gob.cl/wp-content/uploads/2026/05/HuellaChile-Factores-de-emision2025_-Org-y-Ev_v2-Version-completa.xlsx |
| HuellaChile FE 2025 Org y Ev v2 — versión resumen | https://huellachile.mma.gob.cl/wp-content/uploads/2026/05/HuellaChile-Factores-de-emision2025_-Org-y-Ev_v2-Version-resumen.xlsx |
| HuellaChile FE **2024** Org y Ev v6 — versión completa | https://huellachile.mma.gob.cl/wp-content/uploads/2026/05/HuellaChile-Factores-de-emision2024_-Org-y-Ev_v6-Version-completa.xlsx |
| HuellaChile FE 2024 Org y Ev v6 — versión resumen | https://huellachile.mma.gob.cl/wp-content/uploads/2026/05/HuellaChile-Factores-de-emision2024_-Org-y-Ev_v6-Version-resumen.xlsx |
| HuellaChile FE Comunal | https://huellachile.mma.gob.cl/wp-content/uploads/2025/04/HuellaChile-Factores-de-emision-Comunal.xlsx |
| DESNZ 2026 full set | https://assets.publishing.service.gov.uk/media/6a29392bade52dc0882218a8/ghg-conversion-factors-2026-full-set.xlsx |
| DESNZ 2026 methodology report (152 pp) | https://assets.publishing.service.gov.uk/media/6a2940543b15d05a7ce3202e/2026-GHG-conversion-factors-methodology-report.pdf |
| DESNZ 2026 major changes report | https://assets.publishing.service.gov.uk/media/6a2940653b15d05a7ce3202f/2026-GHG-conversion-factors-major-changes-report.pdf |

---

## Fuentes

1. **HuellaChile (Ministerio del Medio Ambiente de Chile)** — *Base de datos de factores de emisión 2025, Organizaciones y Eventos, versión 2* (fecha de última actualización: 2026-05-04). Hojas consultadas: `INICIO`, `RESUMEN`, `CONTROL DE CAMBIOS`, `1.1 Combustión estacionaria`, `1.2 Combustión móvil`, `1.1 y 1.2 CUADRO A1 - BNE 2024`, `1.4 Emisiones fugitivas`, `2.1 Electricidad`, `2.2 Pérdidas por T&D`. — https://huellachile.mma.gob.cl/wp-content/uploads/2026/05/HuellaChile-Factores-de-emision2025_-Org-y-Ev_v2-Version-completa.xlsx
2. **Ministerio de Energía de Chile / Comisión Nacional de Energía — Energía Abierta**, *Factores de Emisión SIC-SING / Sistema Eléctrico Nacional*. — https://energiaabierta.cne.cl/visualizaciones/factor-de-emision-sic-sing/
3. **HuellaChile (MMA)** — *Factores de emisión para el cálculo de la huella de carbono, Nivel básico*, versión 3 (28-11-2024). ⚠️ Contiene factores eléctricos **superados** por [1]. — https://huellachile.mma.gob.cl/wp-content/uploads/2024/11/HuellaChile-DCC-Factores-de-emision-nivel-basico_v3.pdf
4. **HuellaChile (MMA)** — *Recursos: Material de Apoyo — Factores de Emisión*. — https://huellachile.mma.gob.cl/recursos-material-de-apoyo/
5. **HuellaChile (MMA)** — *Actualización de los factores de emisión, para Huellas de Carbono del 2024 en adelante* (19-02-2025, act. 29-04-2025). — https://huellachile.mma.gob.cl/actualizacion-de-factores-de-emision-organizaciones-y-eventos-2024/
6. **Ministerio de Energía / CNE (Chile)** — *Balance Nacional de Energía (BNE) 2024*, Cuadro A1: Densidades y Poderes Caloríficos (reproducido en [1]).
7. **IPCC (2006)** — *2006 IPCC Guidelines for National Greenhouse Gas Inventories, Volume 2: Energy*. Cap.1 (Tabla 1.2), Cap.2 (Cuadros 2.2, 2.3, 2.4), Cap.3 (Cuadros 3.2.1, 3.2.2, 3.3.1). — https://www.ipcc-nggip.iges.or.jp/public/2006gl/vol2.html
8. **IPCC (2006)** — *2006 IPCC Guidelines, Volume 3: IPPU*, Cap.7, Cuadro 7.8 (refrigerantes y mezclas).
9. **IPCC (2013)** — *AR5, WG1, Capítulo 8, Tabla 8.A.1* (PCG a 100 años). — https://www.ipcc.ch/report/ar5/wg1/
10. **MINEM / DGEE (Perú)** — *Informe del Reporte Anual de Gases de Efecto Invernadero (RAGEI) 2019, Sector Energía*, Lima 2023. Tablas 17 (factores por defecto), 18 (poderes caloríficos netos peruanos) y 33 (factor nacional de gas natural). — https://infocarbono.minam.gob.pe/wp-content/uploads/2023/05/Informe-RAGEI_2019_Energia_CE_EF_VF.pdf
11. **MINAM (Perú)** — *RM N° 185-2021-MINAM, Guía para el funcionamiento de la herramienta Huella de Carbono Perú*, 2ª versión (13-10-2021). Deroga la RM N° 237-2020-MINAM.
12. **MINAM (Perú)** — Plataforma *Huella de Carbono Perú* (requiere login para la calculadora de factores). — https://huellacarbonoperu.minam.gob.pe/
13. **MINAM (Perú)** — *RD N° 00001-2025-MINAM/VMDERN/DGCCD* (30-01-2025), reconocimiento de estándares de carbono.
14. **ISA CTM (Perú)** — Informes de Huella de Carbono Corporativa ISO 14064-1, ejercicios 2022, 2023 y 2024, verificados por tercera parte. **Fuente secundaria** de los factores SEIN, con atribución literal "Fuente: MINAM". — https://peru.isaenergia.com/DocumentosISACTM/Reporte%20Sostenibilidad/Informe%20Final%20-%20HC%202024%20CTM%20(VF).pdf
15. **UNSD (Naciones Unidas)** — *Energy Statistics Yearbook 2009, Tabla IV: Selected conversion factors for crude petroleum and petroleum products* (densidades). — https://unstats.un.org/unsd/energy/yearbook/2009/2009_xliv.pdf
16. **UPME / FECOC (Colombia)** — *Informe Final FECOC*, Tabla 2: caracterización de combustibles sólidos y líquidos (densidades, PCS, PCI). — https://app.upme.gov.co/Calculadora_Emisiones1/new/Informe_Final_FECOC_Correcciones_UPME_FunNatura.pdf
17. **IPCC (2019)** — *2019 Refinement to the 2006 IPCC Guidelines, Volume 2*. Confirma "No refinement" en Cap.1, Cap.2 §2.3.2 y Cap.3. — https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol2.html
18. **DESNZ (Reino Unido)** — *Greenhouse gas reporting: conversion factors 2026* (publicado 11-06-2026; act. 31-07-2026). — https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026
19. **DESNZ (Reino Unido)** — *UK Government GHG Conversion Factors for Company Reporting 2026 — full set (XLSX)*. Hojas: `Introduction`, `What's new`, `Fuels`, `WTT- fuels`, `UK electricity`, `Transmission and distribution`, `Outside of scopes`. — https://assets.publishing.service.gov.uk/media/6a29392bade52dc0882218a8/ghg-conversion-factors-2026-full-set.xlsx
20. **DESNZ (Reino Unido)** — *Government conversion factors for company reporting (colección)*. — https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting
21. **DESNZ (Reino Unido)** — *Greenhouse gas reporting: conversion factors 2025* (publicado 10-06-2025). — https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2025
22. **The National Archives (Reino Unido)** — *Open Government Licence v3.0*. — https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
23. **CEPAL / Enerdata** — *Base de Información de Eficiencia Energética* (2018). Origen de la tasa de pérdidas T&D de 5,7 % usada por HuellaChile (citado en [1]).
