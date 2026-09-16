# Factores y métodos para Alcance 3: transporte de carga y cálculo por gasto

Fecha de investigación: 2026-09-15

## Resumen

Este documento reúne los factores y métodos para calcular el **Alcance 3** en transporte de carga, viajes de negocios y compras por gasto, con valores listos para alimentar el motor de cálculo en Python de "Agentes ESG".

**Las cuatro conclusiones que condicionan el diseño del proyecto:**

1. **DESNZ 2026 es la base de datos redistribuible por excelencia.** Publicada el 11 de junio de 2026 bajo **Open Government Licence v3.0**, permite copia, adaptación y **explotación comercial** con sólo mantener la atribución. Los valores de esta investigación se leyeron **directamente del libro Excel oficial**, hoja por hoja y fila por fila, no de fuentes secundarias.
2. **Los factores EPA por gasto son de dominio público** (17 U.S.C. § 105) y por tanto redistribuibles **sin restricción alguna**. La versión vigente sigue siendo **v1.3.0 (julio 2024)**, en kg CO2e por **USD de 2022 a precio de comprador**. Usar siempre la columna **SEF+MEF** y **deflactar el gasto al año base**, o se sobreestiman las emisiones en la magnitud de la inflación acumulada.
3. **Los valores por defecto del GLEC Framework NO se pueden redistribuir** en un repositorio open source: su licencia es efectivamente *NonCommercial* y exige **permiso previo por escrito** de Smart Freight Centre para cualquier fin comercial. La **metodología sí es libre de implementar** (los algoritmos no son objeto de copyright). La ruta recomendada es reconstruir la cobertura desde **las fuentes primarias abiertas que el propio GLEC declara**: DESNZ (OGL v3), ADEME Base Carbone (Licence Ouverte) y EPA SmartWay (dominio público).
4. **El GHG Protocol Scope 3 Standard de 2011 sigue plenamente vigente**, pero ha dejado de revisarse por separado: desde el **29 de julio de 2026** se consolida con el Corporate Standard, Scope 2 y AMI en un único **Corporate Standard v3.0** co-publicado con **ISO**. Consulta pública única en **Q2 2027**; publicación estimada en **Q4 2028**. Nada de la revisión en borrador (umbral del 95 %, Categoría 16, cambio PCAF) debe implementarse todavía.

**Cifras de referencia rápidas (DESNZ 2026, kg CO2e):**

| Concepto | TTW | WTW |
|---|---|---|
| Camión HGV promedio no refrigerado | 0,10356 /t·km | 0,12715 /t·km |
| Tren de carga | 0,02583 /t·km | 0,03274 /t·km |
| Portacontenedores promedio | 0,01612 /t·km | 0,01977 /t·km |
| Granelero promedio | 0,00353 /t·km | 0,00433 /t·km |
| Carga aérea largo radio (con RF) | 0,89939 /t·km | 1,03455 /t·km |
| Vuelo largo radio, económica (con RF) | 0,11704 /pas·km | — |
| Hotel Chile / España / Reino Unido | 27,6 / 7,0 / 10,4 por habitación-noche | — |
| Agua: suministro + tratamiento | 0,19130 + 0,17088 /m³ | — |

**Advertencias transversales:** el factor eléctrico británico cayó un 26 % en 2026 por **cambio de metodología**, no por desempeño — la comparabilidad interanual está rota. Los factores DESNZ de **reciclaje e incineración cubren sólo el transporte**, no el proceso, así que "reciclar casi no emite" es una lectura equivocada que la interfaz debe prevenir. **No existe factor de hotel para Perú** en DESNZ 2025 ni 2026. Y el método por gasto es el **último recurso** de la jerarquía: sirve para detectar dónde está la materialidad, no para gestionarla.

**Verificación:** 5 factores EPA de códigos NAICS altos quedaron **[NO VERIFICADO]** y se consignan sin cifra, porque la lectura remota del CSV se trunca y dos rutas independientes devolvieron valores contradictorios. Ver «Pendientes y dudas».

---

## 1. UK DESNZ/DEFRA — GHG Conversion Factors 2026

### 1.0 Identificación de la fuente

| Campo | Valor |
|---|---|
| Publicación | *Greenhouse gas reporting: conversion factors 2026* |
| Organismo | Department for Energy Security and Net Zero (DESNZ), Reino Unido |
| Fecha de publicación | 11 junio 2026 (actualizado 31 julio 2026: revisión del *flat file*) |
| Versión de los factores | Version 1, Year 2026 (celda declarada en cada hoja) |
| Próxima publicación | Junio 2027 |
| Licencia | **Open Government Licence v3.0 (OGL v3)** — © Crown copyright |
| Archivo usado | `ghg-conversion-factors-2026-full-set.xlsx` (2,01 MB, 40 hojas) |
| URL del archivo | https://assets.publishing.service.gov.uk/media/6a29392bade52dc0882218a8/ghg-conversion-factors-2026-full-set.xlsx |
| URL de la publicación | https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026 |

Etiqueta de verificación para toda la sección 1: **[VERIFICADO]** — los valores se leyeron directamente del libro Excel oficial (`full set`) publicado en GOV.UK. Se indica hoja ("tab") y fila de origen.

#### Atribución exigida por la OGL v3

La OGL v3 permite copiar, publicar, distribuir, adaptar y explotar comercialmente la información, incluso combinándola con otra información y en productos propios, **siempre que** se reconozca la fuente incluyendo la declaración de atribución y, cuando sea posible, un enlace a la licencia. Texto de atribución recomendado para el repositorio y para el motor de cálculo:

```
Contiene información del sector público licenciada bajo la Open Government Licence v3.0.
Fuente: UK Government GHG Conversion Factors for Company Reporting 2026,
Department for Energy Security and Net Zero (DESNZ). © Crown copyright 2026.
Licencia: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
```

> **Implicación práctica para "Agentes ESG":** los factores DESNZ **sí** se pueden redistribuir dentro de un repositorio de código abierto (a diferencia de GLEC, ver sección 4), siempre que se conserve la atribución anterior y no se sugiera respaldo oficial del proyecto por parte de DESNZ.

---

### 1.1 Carga (freight) por tonelada·km — hoja `Freighting goods`

Unidad: **kg CO2e por tonne.km** (TTW, *tank-to-wheel* — combustión directa). Columna usada: "Average laden" (carga media real del parque británico) salvo indicación. Los factores WTT correspondientes están en la hoja `WTT- delivery vehs & freight` y se listan en 1.5.

#### 1.1.1 Camión pesado (HGV) y furgoneta — diésel

| Actividad | Tipo | Unidad | kg CO2e (TTW, average laden) | kg CO2e WTT | **WTW total** | Fila |
|---|---|---|---|---|---|---|
| Vans (furgoneta) | Average (up to 3.5 tonnes), diésel | tonne.km | 0,63511 | 0,15095 | 0,78606 | 35 / 30 |
| Vans | Class I (hasta 1,305 t), diésel | tonne.km | 0,87948 | 0,20817 | 1,08765 | 26 / 21 |
| Vans | Class III (1,74–3,5 t), diésel | tonne.km | 0,63229 | 0,15037 | 0,78266 | 32 / 27 |
| HGV no refrigerado | **Average non-refrigerated HGVs** | tonne.km | **0,10356** | **0,02359** | **0,12715** | 63 / 58 |
| HGV no refrigerado | Average non-refrigerated rigids | tonne.km | 0,19947 | 0,04332 | 0,24279 | 51 / 46 |
| HGV no refrigerado | Average non-refrigerated artics | tonne.km | 0,07926 | 0,01823 | 0,09749 | 60 / 55 |
| HGV no refrigerado | Rigid (>3,5–7,5 t) | tonne.km | 0,54001 | 0,12296 | 0,66297 | 42 / 37 |
| HGV no refrigerado | Rigid (>7,5–17 t) | tonne.km | 0,43002 | 0,09246 | 0,52248 | 45 / 40 |
| HGV no refrigerado | Rigid (>17 t) | tonne.km | 0,17256 | 0,03736 | 0,20992 | 48 / 43 |
| HGV no refrigerado | Articulated (>3,5–33 t) | tonne.km | 0,12292 | 0,02731 | 0,15023 | 54 / 49 |
| HGV no refrigerado | Articulated (>33 t) | tonne.km | 0,07835 | 0,01799 | 0,09634 | 57 / 52 |
| HGV refrigerado | Average refrigerated HGVs | tonne.km | 0,12122 | 0,02769 | 0,14891 | 91 / 86 |
| HGV refrigerado | Average refrigerated artics | tonne.km | 0,09166 | 0,02114 | 0,11280 | 88 / 83 |

> **Recomendación por defecto del motor**: para "camión HGV promedio" usar **Average non-refrigerated HGVs = 0,10356 kg CO2e/t·km (TTW)** y **0,12715 kg CO2e/t·km (WTW)**.

Además de "Average laden", la hoja ofrece columnas **0 % laden**, **50 % laden** y **100 % laden** (para HGV; para vans hay columnas por combustible: diésel, gasolina, CNG, LPG, desconocido, PHEV, BEV). Ejemplo para Average non-refrigerated HGVs: 50 % laden = 0,12320; 100 % laden = 0,07488 kg CO2e/t·km (fila 63).

#### 1.1.2 Tren de carga

| Actividad | Tipo | Unidad | kg CO2e (TTW) | kg CO2e WTT | WTW | Fila |
|---|---|---|---|---|---|---|
| Rail | Freight train | tonne.km | 0,02583 | 0,00691 | 0,03274 | 106 / 101 |

#### 1.1.3 Marítimo — portacontenedores, granelero y otros (hoja `Freighting goods`, filas 111–165)

| Tipo de buque | Tamaño | Unidad | kg CO2e (TTW) | kg CO2e WTT | WTW |
|---|---|---|---|---|---|
| **Container ship** | **Average** | tonne.km | **0,01612** | **0,00365** | **0,01977** |
| Container ship | 8000+ TEU | tonne.km | 0,01266 | 0,00287 | 0,01553 |
| Container ship | 5000–7999 TEU | tonne.km | 0,01681 | 0,00381 | 0,02062 |
| Container ship | 3000–4999 TEU | tonne.km | 0,01681 | 0,00381 | 0,02062 |
| Container ship | 2000–2999 TEU | tonne.km | 0,02025 | 0,00459 | 0,02484 |
| Container ship | 1000–1999 TEU | tonne.km | 0,03250 | 0,00737 | 0,03987 |
| Container ship | 0–999 TEU | tonne.km | 0,03675 | 0,00833 | 0,04508 |
| **Bulk carrier (granelero)** | **Average** | tonne.km | **0,00353** | **0,00080** | **0,00433** |
| Bulk carrier | 200 000+ dwt | tonne.km | 0,00253 | 0,00057 | 0,00310 |
| Bulk carrier | 100 000–199 999 dwt | tonne.km | 0,00304 | 0,00069 | 0,00373 |
| Bulk carrier | 60 000–99 999 dwt | tonne.km | 0,00415 | 0,00094 | 0,00509 |
| Bulk carrier | 35 000–59 999 dwt | tonne.km | 0,00577 | 0,00131 | 0,00708 |
| Bulk carrier | 10 000–34 999 dwt | tonne.km | 0,00800 | 0,00181 | 0,00981 |
| Bulk carrier | 0–9999 dwt | tonne.km | 0,02956 | 0,00670 | 0,03626 |
| General cargo | Average | tonne.km | 0,01321 | 0,00300 | 0,01621 |
| Vehicle transport | Average | tonne.km | 0,03852 | 0,00873 | 0,04725 |
| RoRo-Ferry | Average | tonne.km | 0,05158 | 0,01170 | 0,06328 |
| Refrigerated cargo | All dwt | tonne.km | (ver hoja) | 0,00296 | — |
| Crude tanker | Average | tonne.km | 0,00457 | 0,00104 | 0,00561 |
| Products tanker | Average | tonne.km | 0,00902 | — | — |
| Chemical tanker | Average | tonne.km | 0,01031 | — | — |
| LNG tanker | Average | tonne.km | 0,01153 | — | — |
| LPG tanker | Average | tonne.km | 0,01037 | — | — |

#### 1.1.4 Carga aérea (hoja `Freighting goods`, filas 98–101)

Dos juegos: **con RF** (incluye efectos indirectos no-CO2: vapor de agua, estelas, NOx — un **+70 % sobre el factor CO2**) y **sin RF** (solo CO2, CH4, N2O directos).

| Tipo de vuelo | Unidad | kg CO2e **con RF** | kg CO2e **sin RF** | kg CO2e WTT |
|---|---|---|---|---|
| Domestic, to/from UK | tonne.km | 4,60397 | 2,71931 | 0,57429 |
| Short-haul, to/from UK | tonne.km | 1,27835 | 0,75539 | 0,20515 |
| Long-haul, to/from UK | tonne.km | 0,89939 | 0,53130 | 0,13516 |
| International, to/from non-UK | tonne.km | 0,89939 | 0,53130 | 0,13516 |

> Nota DESNZ (fila 14): los factores internacionales de carga aérea se fijan **iguales** a los de largo recorrido desde/hacia UK.
> Nota DESNZ (fila 12): si se dispone de km de vehículo, esos factores son más exactos que los de t·km para vans y HGV; los t·km derivan de los de km usando estadísticas nacionales y son más útiles para **comparar modos**.

---

### 1.2 Viajes de negocios por pasajero·km

#### 1.2.1 Avión (hoja `Business travel- air`, filas 23–36)

Todos los factores incluyen un **uplift de distancia del 8 %** (rutas no directas, esperas en circuito).

| Haul | Clase | Unidad | kg CO2e **con RF** | kg CO2e **sin RF** |
|---|---|---|---|---|
| Domestic, to/from UK | Average passenger | passenger.km | 0,22928 | 0,13552 |
| Short-haul, to/from UK | Average passenger | passenger.km | 0,12786 | 0,07559 |
| Short-haul, to/from UK | Economy class | passenger.km | 0,12576 | 0,07435 |
| Short-haul, to/from UK | Business class | passenger.km | 0,18863 | 0,11152 |
| Long-haul, to/from UK | Average passenger | passenger.km | 0,15282 | 0,09043 |
| Long-haul, to/from UK | Economy class | passenger.km | 0,11704 | 0,06926 |
| Long-haul, to/from UK | Premium economy | passenger.km | 0,18726 | 0,11081 |
| Long-haul, to/from UK | Business class | passenger.km | 0,33940 | 0,20083 |
| Long-haul, to/from UK | First class | passenger.km | 0,46814 | 0,27701 |
| International, to/from non-UK | Average passenger | passenger.km | 0,14253 | 0,08420 |
| International, to/from non-UK | Economy class | passenger.km | 0,10916 | 0,06449 |
| International, to/from non-UK | Premium economy | passenger.km | 0,17465 | 0,10318 |
| International, to/from non-UK | Business class | passenger.km | 0,31656 | 0,18701 |
| International, to/from non-UK | First class | passenger.km | 0,43663 | 0,25794 |

**Definición de haul** (hoja `Haul definition`, ~200 territorios con código ISO3): *Domestic* = GBR, GGY, IMN, JEY. *Short haul* ≈ Europa. *Long haul* = fuera de Europa (Chile CHL, Perú PER y toda Latinoamérica → **Long Haul**; España ESP → Short Haul). DESNZ recomienda usar por defecto los factores **con RF** (indirect effects).

#### 1.2.2 Auto, bus y tren (hoja `Business travel- land`)

Columnas por combustible: D=Diésel, H=Gasolina, L=Híbrido, P=CNG, T=LPG, X=Desconocido, AB=PHEV, AF=BEV.

| Actividad | Tipo | Unidad | Combustible | kg CO2e | Fila |
|---|---|---|---|---|---|
| Cars (by size) | **Average car** | km | Diésel | **0,17265** | 53 |
| Cars (by size) | Average car | km | Gasolina | 0,16152 | 53 |
| Cars (by size) | Average car | km | Híbrido | 0,12961 | 53 |
| Cars (by size) | Average car | km | Desconocido | 0,16591 | 53 |
| Cars (by size) | Average car | km | PHEV | 0,09918 | 53 |
| Cars (by size) | Average car | km | BEV | 0,02951 | 53 |
| Cars (by size) | Small car | km | Diésel | 0,14327 | 47 |
| Cars (by size) | Small car | km | Gasolina | 0,14257 | 47 |
| Motorbike | Average | km | — | 0,11367 | 65 |
| Taxis | Regular taxi | passenger.km | — | 0,14861 | 71 |
| Taxis | Black cab | passenger.km | — | 0,20402 | 73 |
| Bus | **Average local bus** | passenger.km | — | **0,10151** | 81 |
| Bus | Local bus (not London) | passenger.km | — | 0,12552 | 79 |
| Bus | Local London bus | passenger.km | — | 0,06360 | 80 |
| Bus | Coach (autocar) | passenger.km | — | 0,03948 | 82 |
| Rail | **National rail** | passenger.km | — | **0,03092** | 87 |
| Rail | International rail (Eurostar) | passenger.km | — | 0,01135 | 88 |
| Rail | Light rail and tram | passenger.km | — | 0,02121 | 89 |
| Rail | London Underground | passenger.km | — | 0,01549 | 90 |

> Distinción clave (fila 12): los factores **por km de vehículo** se aplican al vehículo completo (auto, taxi); los **passenger.km** se usan cuando una sola persona viaja en transporte masivo.
> Los factores de tren fueron actualizados en 2026 con datos ORR 2025 y TfL (antes usaban datos 2019 pre-COVID).

---

### 1.3 Hotel por noche (hoja `Hotel stay`)

Unidad: **kg CO2e por habitación-noche** ("Room per night"); no diferencia por número de ocupantes de la habitación. Clase de hotel promedio.

| País | Unidad | kg CO2e | Fila |
|---|---|---|---|
| **Chile** | Room per night | **27,6** | 34 |
| **Perú** | Room per night | **(sin valor en el set 2026)** | 63 |
| **España** | Room per night | **7,0** | 73 |
| **Reino Unido** | Room per night | **10,4** | 22 |
| Reino Unido (Londres) | Room per night | 11,5 | 23 |
| Brasil | Room per night | 8,7 | 32 |
| Colombia | Room per night | 14,7 | 36 |
| México | Room per night | 19,3 | 58 |
| Argentina | Room per night | (sin valor) | 28 |
| Canadá | Room per night | 7,4 | 33 |
| Costa Rica | Room per night | 4,7 | 37 |
| Francia | Room per night | 6,7 | 42 |
| Alemania | Room per night | 13,2 | 43 |
| Italia | Room per night | 14,3 | 50 |
| Países Bajos | Room per night | 14,8 | 59 |
| Portugal | Room per night | 19,0 | 66 |
| Suiza | Room per night | 6,6 | 74 |
| Bélgica | Room per night | 12,2 | 31 |
| China | Room per night | 53,5 | 35 |
| India | Room per night | 58,9 | 46 |
| Japón | Room per night | 39,0 | 51 |
| Estados Unidos | Room per night | 16,1 | 79 |
| Turquía | Room per night | 32,1 | 77 |
| Tailandia | Room per night | 43,4 | 76 |
| Emiratos Árabes Unidos | Room per night | 63,8 | 78 |
| Vietnam | Room per night | 38,5 | 80 |

**Perú, Argentina, Austria, Chequia, Fiyi, Finlandia, Grecia, Irlanda, Israel, Kazajistán, Macao, Nueva Zelanda, Panamá, Polonia, Rumanía** aparecen listados **sin valor** en el set 2026. Guía oficial (fila 90): si falta el país, se puede seguir usando el factor del último set disponible, o consultar https://www.hotelfootprints.org (datos más granulares por ciudad y segmento).

Origen metodológico (fila 86): los factores provienen del **Hotel Footprinting Tool** (International Tourism Partnership + Greenview), derivados del **Cornell Hotel Sustainability Benchmarking Index (CHSB)**.

**Comprobación cruzada con el set 2025** [VERIFICADO]: se descargó y leyó también `ghg-conversion-factors-2025-full-set.xlsx` (publicado el 10 junio 2025, https://assets.publishing.service.gov.uk/media/6846a4f55e92539572806125/ghg-conversion-factors-2025-full-set.xlsx). **La hoja `Hotel stay` es idéntica en 2025 y 2026** (mismos países, mismos valores: Chile 27,6; España 7,0; UK 10,4; Perú también vacío). Es decir, los factores de hotel **no se actualizaron** en el ciclo 2026 y **Perú lleva al menos dos ediciones sin valor**.

> **Decisión sugerida para el motor:** para Perú **no existe factor DESNZ**. Opciones: (a) consultar https://www.hotelfootprints.org y etiquetar el valor **[SECUNDARIO]**; (b) usar un país proxy de la región documentando el supuesto (p. ej. Colombia 14,7 o Chile 27,6 — diferencia de casi 2×, así que la elección es material); (c) dejar el cálculo en blanco y exigir dato primario del hotel. Recomendado: (a) con (c) como preferencia.

---

### 1.4 Residuos por tonelada (hoja `Waste disposal`) y agua (hojas `Water supply` / `Water treatment`)

#### 1.4.1 Residuos — kg CO2e por tonelada

**Advertencia metodológica esencial (filas 11–12):** en línea con el GHG Protocol, para **combustión, reciclaje, compostaje y digestión anaerobia** el factor DESNZ cubre **únicamente el transporte** hasta la planta de recuperación/valorización; las emisiones del proceso se atribuyen al usuario del material reciclado o al generador eléctrico, no al productor del residuo. Solo el **relleno sanitario (landfill)** es "gate-to-grave" (incluye recogida, transporte y emisiones del vertedero). Por eso el reciclaje y la incineración tienen el mismo valor genérico de transporte para casi todos los materiales.

| Tipo de residuo | Relleno (Landfill) | Combustión | Reciclaje ciclo cerrado | Reciclaje ciclo abierto | Compostaje | Digestión anaerobia |
|---|---|---|---|---|---|---|
| **Household residual waste (mixto doméstico)** | **497,28993** | 4,65358 | 4,65358 | 4,65358 | — | 9,00687 |
| **Commercial and industrial waste (mixto comercial)** | **520,58023** | 4,65358 | 4,65358 | — | — | 9,00687 |
| **Paper and board: paper** | **1164,51317** | 4,65358 | 4,65358 | — | 9,00687 | — |
| Paper and board: board | 1164,51317 | 4,65358 | 4,65358 | — | 9,00687 | — |
| Paper and board: mixed | 1164,51317 | 4,65358 | 4,65358 | — | 9,00687 | — |
| Books | 1164,51317 | 4,65358 | 4,65358 | — | 9,00687 | — |
| **Plastics: average plastics** | **9,00687** | 4,65358 | 4,65358 | 4,65358 | — | — |
| Plastics: average plastic film | 9,00687 | 4,65358 | 4,65358 | 4,65358 | — | — |
| Plastics: average plastic rigid | 9,00687 | 4,65358 | 4,65358 | 4,65358 | — | — |
| Plastics: PET / HDPE / LDPE / PP / PS / PVC (incl. forming) | 9,00687 | 4,65358 | 4,65358 | 4,65358 | — | — |
| **Organic: food and drink waste** | **700,33263** | 4,65358 | — | — | **9,00687** | **9,00687** |
| Organic: garden waste | 646,72934 | 4,65358 | — | — | 9,00687 | 9,00687 |
| Organic: mixed food and garden waste | 656,10991 | 4,65358 | — | — | 9,00687 | 9,00687 |
| Clothing (textil) | 496,80605 | 4,65358 | 4,65358 | — | — | — |
| Glass | 9,00687 | 4,65358 | 4,65358 | 4,65358 | — | — |
| Metal: mixed cans / aluminio / acero / chatarra | 9,00687 | 4,65358 | 4,65358 | 4,65358 | — | — |
| Wood | 925,36725 | 4,65358 | 4,65358 | — | 9,00687 | — |
| WEEE (RAEE) - mixed / large / small | 9,00687 | 4,65358 | — | 4,65358 | — | — |
| Baterías | 9,00687 | — | — | 4,65358 | — | — |
| Construction: average construction | — | 4,65358 | 1,01398 | 1,01398 | — | — |
| Construction: concreto / ladrillo / asfalto / áridos | 1,27043 | — | 1,01398 | 1,01398 | — | — |
| Construction: suelos | 19,55376 | — | 1,01398 | — | — | — |
| Construction: plasterboard (yeso-cartón) | 71,95 | — | 4,65358 | — | — | — |
| Construction: asbesto | 5,94839 | — | — | — | — | — |

> **"Re-use" no tiene factores**: DESNZ lo excluye porque no es un método de eliminación al final de vida (fila 98).
> Estos factores **no** sirven para comparar el mérito de ciclo de vida de opciones de gestión (fila 11), ni para bienes adquiridos (usar la hoja `Material use`).

#### 1.4.2 Agua potable y tratamiento

| Actividad | Tipo | Unidad | kg CO2e | Hoja / fila |
|---|---|---|---|---|
| Water supply (suministro de agua potable por red) | Water supply | m³ (cubic metres) | **0,19130** | `Water supply` / 18 |
| Water treatment (tratamiento de aguas residuales) | Water treatment | m³ (cubic metres) | **0,17088** | `Water treatment` / 17 |

> Para una contabilidad completa del agua en Alcance 3 hay que sumar ambos componentes (suministro + tratamiento del agua devuelta al alcantarillado).

---

### 1.5 Factores WTT (Well-to-Tank) de combustibles y electricidad

#### 1.5.1 Combustibles (hoja `WTT- fuels`)

| Combustible | Unidad | kg CO2e (WTT) | Fila |
|---|---|---|---|
| **Diésel (average biofuel blend)** | litro | **0,61101** | 71 |
| Diésel (average biofuel blend) | tonelada | 733,64436 | 70 |
| Diésel (average biofuel blend) | kWh (Net CV) | 0,06181 | 72 |
| Diésel (average biofuel blend) | kWh (Gross CV) | 0,05816 | 73 |
| Diésel (100 % mineral diesel) | litro | 0,62409 | 75 |
| Diésel (100 % mineral diesel) | tonelada | 752,02760 | 74 |
| **Gasolina (petrol, average biofuel blend)** | litro | **0,58094** | 95 |
| Gasolina (average biofuel blend) | tonelada | 777,33392 | 94 |
| Gasolina (average biofuel blend) | kWh (Net CV) | 0,06480 | 96 |
| Gasolina (average biofuel blend) | kWh (Gross CV) | 0,06140 | 97 |
| Gasolina (100 % mineral petrol) | litro | 0,60664 | 99 |
| **Gas natural** | m³ | **0,33660** | 39 |
| Gas natural | kWh (Gross CV) | 0,03021 | 41 |
| Gas natural | kWh (Net CV) | 0,03347 | 40 |
| Gas natural | tonelada | 423,16368 | 38 |
| Gas natural (100 % mineral blend) | kWh (Gross CV) | 0,03021 | 45 |
| GLP (LPG) | litro | 0,18551 | 35 |
| GLP (LPG) | tonelada | 349,29282 | 34 |
| Fuel oil | litro | 0,69539 | 79 |
| Gas oil | litro | 0,62665 | 83 |

> Regla DESNZ (fila 13): quien compra combustible en estación de servicio debe usar el **"average biofuel blend"**; para gas natural de red UK debe usar **"natural gas"** (no el "100 % mineral blend").

#### 1.5.2 Electricidad (hojas `UK electricity`, `Transmission and distribution`, `WTT- UK electricity`)

| Concepto | Alcance | Unidad | Año | kg CO2e | Hoja / fila |
|---|---|---|---|---|---|
| Electricity generated — Electricity: UK | Alcance 2 | kWh | 2026 | **0,13096** | `UK electricity` / 25 |
| T&D – UK electricity (pérdidas de red) | Alcance 3 cat. 3 | kWh | 2026 | **0,01299** | `Transmission and distribution` / 22 |
| **WTT – UK electricity (generación)** | Alcance 3 cat. 3 | kWh | 2026 | **0,03682** | `WTT- UK electricity` / 19 |
| **WTT – UK electricity (T&D)** | Alcance 3 cat. 3 | kWh | 2026 | **0,00359** | `WTT- UK electricity` / 24 |
| Distribución calor y vapor distrital (5 % pérdida) | Alcance 3 | kWh | 2026 | 0,00945 | `Transmission and distribution` / 27 |

Suma "electricity consumption" (fuera del marco de alcances) = generación + T&D = 0,13096 + 0,01299 = **0,14395 kg CO2e/kWh**; con WTT completo = 0,14395 + 0,03682 + 0,00359 = **0,18436 kg CO2e/kWh**.

> **Aviso importante (2026):** el factor de electricidad UK bajó ~26 % respecto a 2025 por un **cambio de metodología** (el desfase de datos pasó de 2 años a 1 año), no solo por descarbonización. Este cambio afecta en cascada a EV, ferrocarril y teletrabajo. **No es comparable año contra año sin re-baselining.**


---

## 2. US EPA — Supply Chain GHG Emission Factors for US Industries and Commodities

### 2.0 Qué es, versión vigente, licencia y unidades

| Campo | Valor | Etiqueta |
|---|---|---|
| Título | *Supply Chain Greenhouse Gas Emission Factors v1.3 by NAICS-6* | [VERIFICADO] |
| Versión vigente a 2026-09-15 | **v1.3.0** (no existe v1.4 publicada) | [VERIFICADO] |
| Autor / editor | US EPA, Office of Research and Development (ORD) — autor: Wesley Ingwersen | [VERIFICADO] |
| Fecha de publicación | 5 julio 2024 (registro Science Inventory: 10 julio 2024) | [VERIFICADO] |
| Registro oficial | https://cfpub.epa.gov/si/si_public_record_report.cfm?dirEntryId=362515&Lab=CESER | [VERIFICADO] |
| Nº de commodities | **1.016** commodities NAICS-2017 a 6 dígitos (353 conjuntos únicos de factores) | [VERIFICADO] |
| Unidad | **kg CO2e / USD de 2022, a precios de comprador (purchaser price)** | [VERIFICADO] |
| Año base monetario | **2022 USD** (v1.2 = 2021 USD; v1.1 = 2018 USD) | [VERIFICADO] |
| Año de datos de emisiones | 2022 (US GHG Inventory 1990–2022, EPA 430-R-24-004) | [VERIFICADO] |
| GWP | **IPCC AR5, horizonte 100 años** (v1.2 usaba AR4) | [VERIFICADO] |
| Modelo subyacente | SAM-GHG (atribución sectorial) + **USEEIO v2.2.22-GHG**, tablas IO benchmark 2017 de BEA | [VERIFICADO] |
| Licencia | **Dominio público** (17 U.S.C. § 105: obra del gobierno federal de EE. UU., sin protección de copyright doméstico). Redistribución comercial y en repositorios open source **permitida sin restricción**. Atribución no exigida legalmente, pero recomendada. Prohibido usar el sello de EPA o insinuar respaldo. | [VERIFICADO] |
| URL licencia | https://pasteur.epa.gov/license/sciencehub-license.html | [VERIFICADO] |
| CSV CO2e | https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv | [VERIFICADO] |
| CSV por gas | https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_byGHG_USD2022.csv | [VERIFICADO] |
| Documentación oficial | https://pasteur.epa.gov/uploads/10.23719/1531143/documents/Aboutv1.3SupplyChainGHGEmissionFactors.docx | [VERIFICADO] |
| Código fuente | https://github.com/USEPA/supply-chain-factors | [VERIFICADO] |

**Qué son.** Estiman las emisiones de GEI directas **e indirectas** asociadas a un bien o servicio estadounidense **por dólar gastado**, sobre las fases de ciclo de vida cubiertas por el modelo input-output ambientalmente extendido USEEIO. Se crearon a petición de la General Services Administration para estimar la huella de Alcance 3 de las agencias federales. Están **destinados a las categorías 1 (bienes y servicios adquiridos) y 2 (bienes de capital)** del GHG Protocol; su uso en otras categorías es posible pero queda a criterio del usuario. [VERIFICADO]

**Los tres tipos de factor (con y sin márgenes):** [VERIFICADO]

| Sigla | Nombre | Qué representa |
|---|---|---|
| SEF | Supply Chain Emission Factors **without Margins** | Emisiones directas + indirectas del bien/servicio, **sin** los márgenes de distribución |
| MEF | **Margins** of Supply Chain Emission Factors | Emisiones de los márgenes: transporte, comercio mayorista y minorista incorporados al precio de comprador |
| SEF+MEF | Supply Chain Emission Factors **with Margins** | **El que se debe usar con datos de gasto** (precio efectivamente pagado) |

> **Regla oficial:** *no* sumar el resultado calculado con SEF y/o MEF al resultado calculado con SEF+MEF — sería doble contabilidad. [VERIFICADO]
> Los MEF son distintos de cero sólo en el 45 % de las commodities y siempre son menores que su SEF correspondiente.

**Distribución de valores (SEF+MEF, kg CO2e/USD 2022):** mín. 0,029 · 1er cuartil 0,108 · **mediana 0,173** · media 0,2819 · 3er cuartil 0,3292 · **máx. 3,924**. [VERIFICADO]

**Exclusiones importantes:** [VERIFICADO]

- **Electricidad (NAICS 221100) está EXCLUIDA a propósito**: EPA la eliminó porque la electricidad comprada corresponde al **Alcance 2**, no al 3. No existe factor de gasto en electricidad en este set.
- Sectores de **gobierno** (G\*) y sectores especiales de balance IO (S\*) también eliminados.
- En v1.3 **todos** los sectores de residuos `562*` comparten el mismo factor (0,988), porque no hubo datos para desagregar el sector de residuos con las tablas IO 2017. En v1.2 sí había desagregación (p. ej. relleno sanitario 562212 = 10,989 → 0,988 en v1.3, una caída del 91 %). Es el cambio más drástico entre versiones.

---

### 2.1 Factores representativos por código NAICS para cálculo por gasto

Unidad en todas las filas: **kg CO2e por USD de 2022 a precio de comprador**. Columna a usar con datos de gasto: **SEF+MEF**.

| # | NAICS 2017 | Título (EN) | Uso típico (ES) | SEF | MEF | **SEF+MEF** | Etiqueta |
|---|---|---|---|---|---|---|---|
| 1 | 322230 | Stationery Product Manufacturing | Papelería | 0,265 | 0,031 | **0,296** | [VERIFICADO] |
| 2 | 334111 | Electronic Computer Manufacturing | TI — computadores | 0,030 | 0,028 | **0,058** | [VERIFICADO] |
| 3 | 541512 | Computer Systems Design Services | TI — servicios | 0,089 | 0 | **0,089** | [VERIFICADO] |
| 4 | 511210 | Software Publishers | Software / licencias | 0,036 | 0,045 | **0,080** | [VERIFICADO] |
| 5 | 541611 | Administrative Management and General Management Consulting Services | Consultoría | 0,078 | 0 | **0,078** | [VERIFICADO] |
| 6 | 541110 | Offices of Lawyers | Servicios legales | 0,041 | 0 | **0,041** | [VERIFICADO] |
| 7 | 541810 | Advertising Agencies | Publicidad | — | — | **pendiente** | **[NO VERIFICADO]** |
| 8 | 517311 | Wired Telecommunications Carriers | Telecomunicaciones | 0,075 | 0 | **0,075** | [VERIFICADO] |
| 9 | 722511 | Full-Service Restaurants | Restaurantes | — | — | **pendiente** | **[NO VERIFICADO]** |
| 10 | 721110 | Hotels (except Casino Hotels) and Motels | Hoteles | — | — | **pendiente** | **[NO VERIFICADO]** |
| 11 | 481111 | Scheduled Passenger Air Transportation | Transporte aéreo | 0,644 | 0 | **0,644** | [VERIFICADO] |
| 12 | 484121 | General Freight Trucking, Long-Distance, Truckload | Camión larga distancia | 0,595 | 0 | **0,595** | [VERIFICADO] |
| 13 | 484110 | General Freight Trucking, Local | Camión local | 0,595 | 0 | **0,595** | [VERIFICADO] |
| 14 | 483111 | Deep Sea Freight Transportation | Marítimo de altura | 0,816 | 0 | **0,816** | [VERIFICADO] |
| 15 | 493110 | General Warehousing and Storage | Almacenamiento | 0,244 | 0 | **0,244** | [VERIFICADO] |
| 16 | 236220 | Commercial and Institutional Building Construction | Construcción | 0,224 | 0 | **0,224** | [VERIFICADO] |
| 17 | 327310 | Cement Manufacturing | Cemento — **el factor más alto del set** | 3,846 | 0,078 | **3,924** | [VERIFICADO] |
| 18 | 327410 | Lime Manufacturing | Cal | 1,560 | 0,063 | **1,623** | [VERIFICADO] |
| 19 | 331110 | Iron and Steel Mills and Ferroalloy Manufacturing | Acero | 0,769 | 0,018 | **0,787** | [VERIFICADO] |
| 20 | 325211 | Plastics Material and Resin Manufacturing | Plásticos (resinas) | 1,022 | 0,024 | **1,045** | [VERIFICADO] |
| 21 | 326160 | Plastics Bottle Manufacturing | Envases plásticos | 0,553 | 0,025 | **0,579** | [VERIFICADO] |
| 22 | 325110 | Petrochemical Manufacturing | Petroquímica | 0,794 | 0,016 | **0,811** | [VERIFICADO] |
| 23 | 325199 | All Other Basic Organic Chemical Manufacturing | Químicos orgánicos básicos | 1,166 | 0,018 | **1,184** | [VERIFICADO] |
| 24 | 325120 | Industrial Gas Manufacturing | Gases industriales | 1,163 | 0,048 | **1,211** | [VERIFICADO] |
| 25 | 325311 | Nitrogenous Fertilizer Manufacturing | Fertilizante nitrogenado | 1,114 | 0,023 | **1,137** | [VERIFICADO] |
| 26 | 325312 | Phosphatic Fertilizer Manufacturing | Fertilizante fosfatado | 1,114 | 0,023 | **1,137** | [VERIFICADO] |
| 27 | 111150 | Corn Farming | Agricultura — maíz (igual para trigo, arroz, oleaginosas) | 0,809 | 0,040 | **0,848** | [VERIFICADO] |
| 28 | 112111 | Beef Cattle Ranching and Farming | Producción animal — bovino carne | 2,847 | 0,045 | **2,893** | [VERIFICADO] |
| 29 | 112120 | Dairy Cattle and Milk Production | Producción animal — leche | 1,682 | 0,042 | **1,724** | [VERIFICADO] |
| 30 | 112210 | Hog and Pig Farming | Producción animal — porcino | 1,077 | 0,051 | **1,128** | [VERIFICADO] |
| 31 | 112310 | Chicken Egg Production | Producción animal — huevos / aves | — | — | **0,438** | [VERIFICADO] |
| 32 | 311812 | Commercial Bakeries | Alimentos — panadería | 0,213 | 0,040 | **0,253** | [VERIFICADO] |
| 33 | 312111 | Soft Drink Manufacturing | Bebidas — refrescos | 0,173 | 0,042 | **0,214** | [VERIFICADO] |
| 34 | 312120 | Breweries | Bebidas — cerveza | 0,209 | 0,066 | **0,274** | [VERIFICADO] |
| 35 | 313210 | Broadwoven Fabric Mills | Textiles | 0,480 | 0,027 | **0,507** | [VERIFICADO] |
| 36 | 315990 | Apparel Accessories and Other Apparel Manufacturing | Vestuario | 0,060 | 0,060 | **0,120** | [VERIFICADO] |
| 37 | 337214 | Office Furniture (except Wood) Manufacturing | Muebles de oficina | 0,184 | 0,056 | **0,240** | [VERIFICADO] |
| 38 | 221100 | Electric Power Generation, Transmission and Distribution | Electricidad | — | — | **EXCLUIDO del set (es Alcance 2)** | [VERIFICADO] |
| 39 | 221310 | Water Supply and Irrigation Systems | Agua | 0,578 | 0 | **0,578** | [VERIFICADO] |
| 40 | 562111 y todo `562*` | Solid Waste Collection / Waste Management | Residuos | — | — | **0,988** | [VERIFICADO] |
| 41 | 524113 | Direct Life Insurance Carriers | Seguros | — | 0 | **0,051** | [VERIFICADO] |
| 42 | 522110 | Commercial Banking | Banca | 0,059 | 0 | **0,059** | [VERIFICADO] |
| 43 | 531120 | Lessors of Nonresidential Buildings | Arriendo de oficinas / locales | 0,246 | 0 | **0,246** | [VERIFICADO] |
| 44 | 531110 | Lessors of Residential Buildings and Dwellings | Inmobiliario residencial | 0,033 | 0 | **0,033** | [VERIFICADO] |
| 45 | 333120 | Construction Machinery Manufacturing | Maquinaria | 0,201 | 0,027 | **0,228** | [VERIFICADO] |
| 46 | 335312 | Motor and Generator Manufacturing | Equipos eléctricos | 0,133 | 0,019 | **0,152** | [VERIFICADO] |
| 47 | 325412 | Pharmaceutical Preparation Manufacturing | Farmacéuticos | 0,045 | 0,053 | **0,099** | [VERIFICADO] |
| 48 | 322211 | Corrugated and Solid Fiber Box Manufacturing | Envases de cartón | 0,449 | 0,030 | **0,479** | [VERIFICADO] |
| 49 | 323110 | Commercial Printing (except Screen and Books) | Imprenta | 0,202 | 0,034 | **0,236** | [VERIFICADO] |
| 50 | 324110 | Petroleum Refineries | Combustibles | 0,248 | 0,022 | **0,270** | [VERIFICADO] |
| 51 | 486110 / 486210 / 486910 / 486990 | Pipeline Transportation | Ductos (crudo, gas, refinados) | 1,619 | 0 | **1,619** | [VERIFICADO] |
| 52 | 561720 | Janitorial Services | Limpieza | — | — | **pendiente** | **[NO VERIFICADO]** |
| 53 | 561612 / 561610 | Security Guards / Investigation and Security Services | Seguridad | — | — | **pendiente** | **[NO VERIFICADO]** |
| 54 | 561311 / 561320 | Employment Placement / Temporary Help Services | RR. HH. y personal temporal | — | — | **0,051** | [VERIFICADO] |

**Nota de verificación.** Los valores [VERIFICADO] se leyeron del CSV oficial de EPA y/o de las tablas 1, 2, 4 y 5 del documento oficial `Aboutv1.3SupplyChainGHGEmissionFactors.docx`. La lectura remota del CSV **se trunca en el codigo NAICS 541720** (y la del CSV de cambios relativos, en 524127). Se intentaron dos rutas independientes para los cinco codigos altos (541810, 722511, 721110, 561720, 561612) y **devolvieron valores contradictorios entre si**, senal inequivoca de lectura fuera del rango realmente recibido. Por eso **no se consignan cifras**: hay que abrir el CSV completo en local antes de cargarlos en el motor — ver «Pendientes y dudas».

---

### 2.2 Metodología oficial de uso (EPA) y adaptación fuera de EE. UU.

#### 2.2.1 Procedimiento oficial EPA, 4 pasos [VERIFICADO]

1. **Mapear** cada bien o servicio comprado al código NAICS más cercano, usando las descripciones NAICS.
2. **(Opcional pero RECOMENDADO) Ajustar el año-dólar** del factor para que coincida con el año-dólar del dato de gasto, usando un **índice de precios anual específico de la commodity** (chain-type price index del BEA, transformado a forma de commodity con un enfoque de market shares). EPA advierte que, al momento de la publicación, los índices a nivel detallado no estaban disponibles después de 2022.
3. **Multiplicar** el gasto (USD) por el factor → kg CO2e directos + indirectos.
4. **No sumar** el resultado de SEF y/o MEF al resultado de SEF+MEF (duplicación).

#### 2.2.2 Adaptación para Chile, Perú y la UE — procedimiento propuesto

> **ADVERTENCIA:** la EPA **no publica** guía oficial para aplicar estos factores fuera de EE. UU. Lo siguiente es un procedimiento construido a partir de la práctica estándar con modelos EEIO; **[NO VERIFICADO] como guía oficial**. Debe documentarse como supuesto del motor y declararse en el reporte.

**Fórmula completa:**

```
E_kgCO2e = Gasto_local(año t)
           ÷ FX(moneda_local → USD, promedio año t)   (1) conversión de moneda
           × (IPC_US_2022 / IPC_US_t)                  (2) deflactación al año base 2022
           × FE_NAICS(SEF+MEF)                         (3) factor EPA
           × k_pais                                    (4) ajuste país (opcional)
```

**(1) Conversión de moneda.** Convertir el gasto local a USD con el tipo de cambio **promedio del mismo año del gasto**, no el de hoy. Fuentes estables para el motor: dólar observado promedio anual del Banco Central de Chile, tipo de cambio del BCRP para Perú, tipo de cambio de referencia del BCE para el euro. Alternativa técnicamente superior pero más discutible ante auditores: **paridad de poder adquisitivo (PPA)** del Banco Mundial, que corrige la diferencia de nivel de precios — un mismo bien cuesta menos USD nominales en Chile o Perú que en EE. UU., de modo que usar sólo el tipo de cambio de mercado **subestima** las emisiones.

**(2) Ajuste por inflación al año base.** El denominador de todos los factores v1.3 es el **USD de 2022**. Si el gasto es de 2025 o 2026, hay que **deflactarlo a USD 2022** antes de multiplicar (equivalentemente, envejecer el factor dividiéndolo por el índice de precios, que es como lo plantea EPA). Si no se hace, se introduce un error sistemático igual a la inflación acumulada entre ambos años que **SOBREESTIMA** las emisiones: el mismo bien físico cuesta más dólares nominales hoy, y esos dólares extra se cuentan como si fueran emisiones adicionales. Orden de preferencia:

1. Índice de precios encadenado específico de la commodity del BEA (lo que EPA usa internamente) — lo más correcto, pero sólo disponible hasta 2022 a nivel detallado.
2. **US CPI-U** o deflactor del PIB de EE. UU. — aproximación práctica y auditable.
3. Regenerar los factores en el año-dólar deseado ejecutando el código `useeior` / `supply-chain-factors` de EPA, que soporta producir los factores en el año-dólar indicado por el usuario. [VERIFICADO]

**(3) Factor EPA.** Usar siempre la columna **SEF+MEF** con datos de gasto (precios de comprador).

**(4) Ajuste país (opcional y el más delicado).** Los factores reflejan la **estructura productiva y la matriz eléctrica de EE. UU.** Aplicarlos tal cual a Chile, Perú o España asume que un dólar gastado allí genera las mismas emisiones que en EE. UU. Opciones:

- **k = 1** (sin ajuste): lo más simple, transparente y auditable; se declara como limitación. Es lo que hace la mayoría de las plataformas comerciales.
- Ajustar por la **intensidad de carbono de la economía** (kg CO2e/USD de PIB) del país destino frente a EE. UU.: mejora el orden de magnitud, pero no es práctica estandarizada.
- Sustituir por una base EEIO regional (EXIOBASE para la UE; no hay equivalente oficial abierto para Chile ni Perú) — ver «Pendientes y dudas».

#### 2.2.3 Incertidumbre — qué debe advertir el motor

| Fuente de incertidumbre | Efecto | Mitigación |
|---|---|---|
| **Agregación sectorial** | Los 1.016 NAICS se resuelven en sólo **353 conjuntos únicos** de factores; todos los `562*` comparten valor | Documentar el mapeo; priorizar datos de proveedor |
| **Homogeneidad de precio** | El modelo asume misma intensidad por dólar dentro del sector: un producto premium parece más contaminante sólo por costar más | No usar gasto en categorías materiales; migrar a datos de actividad |
| **Año-dólar / inflación** | **Sobreestimación** sistemática si no se deflacta el gasto al año base del factor (2022) | Paso (2) obligatorio en el motor |
| **Tipo de cambio vs PPA** | Subestimación sistemática en países con menor nivel de precios | Declarar el criterio elegido; opción PPA configurable |
| **Geografía** | Matriz eléctrica y tecnología de EE. UU. ≠ Chile / Perú / UE | Declarar como limitación; `k_pais` documentado |
| **Deriva entre versiones** | La mediana de los SEF cayó **−18 %** de v1.2 a v1.3; 796 de 1.016 factores bajaron >5 % y 139 subieron >5 %; el relleno sanitario `562212` pasó de 10,989 a 0,988 | Fijar la versión del set en la configuración y **re-baselinear** al cambiar |

> **Regla de oro para el motor:** el método por gasto es el **último recurso** en la jerarquía del GHG Protocol. Sirve para un primer barrido y para detectar dónde está la materialidad; identificadas las categorías materiales, hay que migrar a datos de proveedor o de actividad física.

---

## 3. GHG Protocol — Corporate Value Chain (Scope 3) Standard

### 3.0 Documentos vigentes a septiembre de 2026

| Documento | Versión / fecha | Estado a 2026-09-15 | Etiqueta |
|---|---|---|---|
| *Corporate Value Chain (Scope 3) Accounting and Reporting Standard* | © WRI/WBCSD **septiembre 2011**, ISBN 978-1-56973-772-9 (e-reader con correcciones may-2013) | **Vigente** | [VERIFICADO] |
| *Technical Guidance for Calculating Scope 3 Emissions* (Scope 3 Calculation Guidance) | **v1.0**, © WRI & WBCSD **2013**, desarrollado con Carbon Trust | **Vigente** | [VERIFICADO] |

---

### 3.1 Las 15 categorías

Definiciones redactadas con palabras propias (no texto del estándar). Fuente: Tablas 5.3 y 5.4, cap. 5 del Scope 3 Standard. [VERIFICADO]

| # | Nombre oficial (EN) | Nombre en español | Flujo | Definición breve |
|---|---|---|---|---|
| 1 | Purchased goods and services | Bienes y servicios comprados | Arriba | Emisiones cuna-a-puerta de producir los bienes y servicios adquiridos en el año, excluyendo los que cubren las categorías 2 a 8. |
| 2 | Capital goods | Bienes de capital | Arriba | Emisiones cuna-a-puerta de extraer, producir y transportar los bienes de capital comprados en el año: planta, maquinaria, equipos, edificios. |
| 3 | Fuel- and energy-related activities | Actividades de combustibles y energía no incluidas en alcance 1 o 2 | Arriba | Emisiones aguas arriba de combustibles y electricidad comprados, pérdidas de transmisión y distribución, y energía comprada revendida a usuarios finales. |
| 4 | Upstream transportation and distribution | Transporte y distribución aguas arriba | Arriba | Transporte de productos comprados entre proveedores tier 1 y la empresa, más todo servicio logístico contratado, en vehículos de terceros. |
| 5 | Waste generated in operations | Residuos generados en las operaciones | Arriba | Disposición y tratamiento en instalaciones de terceros de los residuos generados por las operaciones propias durante el año. |
| 6 | Business travel | Viajes de negocios | Arriba | Transporte de empleados por motivos laborales en vehículos de terceros: avión, tren, autobús, automóvil. Alojamiento opcional. |
| 7 | Employee commuting | Desplazamientos casa–trabajo | Arriba | Traslado diario de empleados entre su domicilio y su lugar de trabajo en vehículos no propiedad de la empresa. |
| 8 | Upstream leased assets | Activos arrendados aguas arriba | Arriba | Operación de activos que la empresa arrienda como arrendataria y que no están ya incluidos en alcance 1 o 2. |
| 9 | Downstream transportation and distribution | Transporte y distribución aguas abajo | Abajo | Transporte, almacenamiento y venta minorista de los productos vendidos hasta el consumidor final, cuando no los paga la empresa. |
| 10 | Processing of sold products | Procesamiento de productos vendidos | Abajo | Transformación posterior, por empresas aguas abajo, de los productos intermedios que la empresa vendió durante el año. |
| 11 | Use of sold products | Uso de productos vendidos | Abajo | Emisiones del uso final de los productos vendidos a lo largo de su vida útil esperada. |
| 12 | End-of-life treatment of sold products | Fin de vida de productos vendidos | Abajo | Disposición y tratamiento de residuos de los productos vendidos al llegar al final de su vida útil. |
| 13 | Downstream leased assets | Activos arrendados aguas abajo | Abajo | Operación de activos propiedad de la empresa arrendados a terceros, reportada por el arrendador, fuera de alcance 1 o 2. |
| 14 | Franchises | Franquicias | Abajo | Operación de franquicias por los franquiciados, reportada por el franquiciador, fuera de alcance 1 o 2. |
| 15 | Investments | Inversiones | Abajo | Operación de inversiones —capital, deuda y financiación de proyectos— durante el año, fuera de alcance 1 o 2. |

Reglas estructurales [VERIFICADO]: las categorías son **mutuamente excluyentes** para una misma empresa; **reportar por categoría es obligatorio**; las categorías 1–8 son aguas arriba y 9–15 aguas abajo.

---

### 3.2 Límites mínimos (minimum boundaries)

Propósito declarado: estandarizar el alcance de cada categoría y asegurar que entren las actividades mayores, dejando claro a la vez que **la empresa no debe contabilizar las emisiones de cada entidad de su cadena de valor indefinidamente**. [VERIFICADO]

Dos lógicas de diseño: [VERIFICADO]

| Lógica | Categorías | Qué exige |
|---|---|---|
| **Cuna-a-puerta completa** | 1, 2, 3 | Todas las emisiones aguas arriba del producto o combustible comprado, desde la extracción de materias primas hasta la compra por la empresa. |
| **Alcances 1 y 2 del socio de la cadena** | 4–14 | Sólo los alcances 1 y 2 del socio relevante (transportista, gestor de residuos, empleado, arrendador, franquiciado, usuario final). El razonamiento: el grueso está en el uso de energía de esa entidad, no en fabricar su infraestructura — el combustible del avión, no la construcción del avión ni del aeropuerto. |

**Exclusiones:** se pueden excluir actividades dentro del límite mínimo **siempre que la exclusión se divulgue y se justifique** (cap. 6). También se puede incluir voluntariamente por encima del mínimo. [VERIFICADO]

#### Detalle de las tres categorías solicitadas

**Categoría 1 — Purchased goods and services** [VERIFICADO]
- Límite mínimo: **todas** las emisiones cuna-a-puerta de los bienes y servicios comprados.
- Incluye extracción de materias primas, actividades agrícolas, manufactura y procesamiento, electricidad consumida aguas arriba, tratamiento de residuos generados aguas arriba, **uso y cambio de uso de la tierra**, y transporte de materiales **entre proveedores**.
- **Frontera con la categoría 4:** el transporte desde el proveedor **tier 1** hasta la empresa va en la categoría 4. El transporte aguas arriba del tier 1 (p. ej. entre tier 2 y tier 1) ya está dentro de la categoría 1 y **no se exige reportarlo aparte**.
- El uso de los productos comprados va a alcance 1 (combustible) o 2 (electricidad), no a alcance 3.

**Categoría 4 — Upstream transportation and distribution** [VERIFICADO]
- Límite mínimo: los **alcances 1 y 2 de los proveedores de transporte y distribución**. La fabricación de vehículos e infraestructura es **opcional**.
- Cubre (a) el transporte de productos comprados entre proveedores tier 1 y la empresa en vehículos de terceros, incluido el multimodal; y (b) **todos los servicios de transporte y distribución contratados por la empresa**, directamente o vía intermediario: logística de entrada, **logística de salida** y transporte entre instalaciones propias.
- **Punto crítico y contraintuitivo:** la **logística de salida contratada y pagada por la empresa se clasifica como aguas arriba (categoría 4)**, no como categoría 9, porque es un servicio comprado. La categoría 9 es para el transporte aguas abajo que la empresa **no paga**.
- Modos: aéreo, ferroviario, carretera y marítimo, **más almacenamiento** en almacenes, centros de distribución e instalaciones minoristas.
- Fronteras: vehículos propios → alcance 1/2; vehículos arrendados y operados por la empresa fuera de alcance 1/2 → categoría 8; fabricación de vehículos comprados → categoría 2; transporte de los combustibles consumidos → categoría 3.

**Categoría 6 — Business travel** [VERIFICADO]
- Límite mínimo: los **alcances 1 y 2 de los transportistas** (aerolíneas, ferrocarriles) durante el uso de los vehículos. Fabricación de vehículos e infraestructura **opcional**.
- Modos: avión, tren, autobús, automóvil (alquiler o vehículo propio del empleado distinto del commuting) y otros.
- **Hoteles: OPCIONALES.** El estándar dice que las empresas *pueden* incluir las emisiones del alojamiento; no forman parte del límite mínimo. (El motor debe ofrecerlo como casilla opcional y declararlo en el reporte.)
- Fronteras: vehículos propios o controlados → alcance 1 o 2; arrendados y operados por la empresa fuera de alcance 1/2 → categoría 8; traslados casa-trabajo → categoría 7.

---

### 3.3 Métodos de cálculo

#### 3.3.1 Categoría 1 — los cuatro métodos

Fuente: Technical Guidance v1.0, cap. 1. [VERIFICADO]

| Método | Qué hace | Datos de actividad | Factores | Tipo de dato |
|---|---|---|---|---|
| **Supplier-specific** (específico de proveedor) | Toma del proveedor su inventario GEI **cuna-a-puerta a nivel de producto** | Cantidad comprada por proveedor | Datos de emisión específicos del producto del proveedor | 100 % primario, específico del producto |
| **Hybrid** (híbrido) | Combina datos primarios del proveedor con secundarios para los huecos: (a) alcances 1 y 2 asignados del proveedor, (b) emisiones aguas arriba desde datos de actividad del proveedor (materiales, combustible, electricidad, distancia, residuos), (c) secundarios donde no haya datos | Mezcla | Mezcla de específicos y secundarios | Alcances 1 y 2 específicos; resto específico o promedio |
| **Average-data** (datos promedio) | Estima desde **unidades físicas** compradas | Masa u otra unidad física | Secundarios de **proceso** (promedio de industria por unidad de bien) | 100 % secundario (proceso) |
| **Spend-based** (por gasto) | Estima desde el **valor económico** de lo comprado | Valor monetario | Secundarios **EEIO** por unidad monetaria | 100 % secundario (EEIO) |

#### 3.3.2 La jerarquía de preferencia — matiz crítico que casi todos se saltan

Este punto es importante para el diseño del motor y para no dar consejos equivocados a usuarios no técnicos. El texto oficial es explícito: [VERIFICADO]

1. Los métodos **se listan en orden de cuán específicos son respecto al proveedor individual**, no como una jerarquía obligatoria de preferencia.
2. El estándar dice literalmente que las empresas **no siempre necesitan usar el método más específico como primera preferencia**.
3. **Box 1.1, "The difference between data specificity and data accuracy":** aunque supplier-specific e hybrid son más específicos, **pueden no producir resultados más exactos**. El dato de un proveedor **puede ser menos exacto** que un promedio de industria, porque la exactitud depende de la granularidad, de la fiabilidad de las fuentes del proveedor y sobre todo de **qué técnicas de asignación (allocation) usó** — asignar las emisiones de una planta a un producto concreto puede añadir mucha incertidumbre.
4. Recoger datos de proveedores tiene **coste y carga elevados**, así que el estándar indica hacer **primero un cribado (screening)** para priorizar y decidir método.
5. Se pueden **usar métodos distintos para distintos bienes y servicios dentro de la misma categoría 1** — más específicos para las familias de compra que más pesan.

**Regla oficial de primarios vs secundarios (sección 7.2 del Standard):** [VERIFICADO]
- Objetivo = fijar metas de reducción, seguir el desempeño de operaciones concretas o involucrar proveedores → **datos primarios**.
- Objetivo = entender magnitudes relativas, identificar *hot spots* y priorizar → **datos secundarios**.
- Usar secundarios también cuando el socio no pueda aportar datos y cuando **la calidad del secundario sea mayor que la del primario**.

#### 3.3.3 Categoría 4 — los tres métodos

Fuente: Technical Guidance v1.0, cap. 4. [VERIFICADO]

| Método | Qué hace | Datos requeridos |
|---|---|---|
| **Fuel-based** | Determina el combustible consumido (los alcances 1 y 2 del transportista) y aplica el factor del combustible | Tipo y cantidad de combustible; opcionalmente fugas de refrigerante y energía adicional |
| **Distance-based** | Determina **masa, distancia y modo** por envío y aplica el factor masa-distancia | Masa, distancia y modo por envío; si varios productos comparten vehículo, cantidades de cada uno |
| **Spend-based** | Determina el dinero gastado por modo y aplica factores **EEIO** | Gasto monetario por modo |

**Árbol de decisión oficial de la categoría 4:** [VERIFICADO]
1. ¿Hay masa, distancia y modo por envío? → **distance-based**.
2. ¿El transporte contribuye significativamente al alcance 3 (según cribado) o involucrar transportistas es relevante para el negocio, y hay datos de combustible? → **fuel-based**.
3. Si no → **spend-based**.

**Árbol de decisión de la categoría 6:** ¿hay gasto en proveedores de viaje? → spend-based; ¿hay distancia recorrida? → distance-based; si los viajes son significativos y hay datos de combustible → fuel-based. [VERIFICADO]

#### 3.3.4 Cómo se corresponden los métodos entre categorías

No son cuatro métodos universales: son familias distintas adaptadas a cada categoría. [VERIFICADO]

| Nivel de especificidad | Categoría 1 | Categorías 4 / 6 |
|---|---|---|
| Primario del socio de la cadena | Supplier-specific | **Fuel-based** (consumo real del transportista) |
| Primario parcial + relleno secundario | Hybrid | **Distance-based** (actividad física real + factores masa-distancia) |
| Secundario de proceso | Average-data | *(no existe como método separado; la distancia cumple ese rol)* |
| Secundario económico | **Spend-based** | **Spend-based** |

El único método con **nombre y lógica idénticos en ambas categorías es el spend-based**, y en ambos casos es el menos específico.

> **Advertencia oficial sobre la herramienta de transporte del GHG Protocol** [VERIFICADO]: la herramienta *GHG emissions from transport or mobile sources* combina fuel-based y distance-based (el CO2 se estima mejor desde el combustible; CH4 y N2O desde la distancia), pero **se desarrolló para alcance 1** y viene precargada con **factores de combustión**. Para alcance 3 hay que **sustituirlos por factores de ciclo de vida**.

---

### 3.4 Criterios de calidad de datos

Fuente: Scope 3 Standard (2011), cap. 7 "Collecting Data", sección 7.3, **Tabla 7.6** y Box 7.2. Los indicadores están adaptados de Weidema & Wesnaes (1996), *Journal of Cleaner Production* 4(3-4):167-174. [VERIFICADO]

> Corrección de una confusión frecuente: muchas fuentes citan "Tabla 7.2"; el texto oficial la numera **Tabla 7.6**.

#### Los cinco indicadores

| Indicador | Qué mide |
|---|---|
| **Technological representativeness** | Grado en que el dato refleja la tecnología realmente usada |
| **Temporal representativeness** | Grado en que el dato refleja el año real o la antigüedad de la actividad |
| **Geographical representativeness** | Grado en que el dato refleja la ubicación geográfica real (país o sitio) |
| **Completeness** | Grado en que el dato es **estadísticamente representativo**: porcentaje de emplazamientos con datos sobre el total, y tratamiento de fluctuaciones estacionales |
| **Reliability** | Grado en que las fuentes, los métodos de recolección y los **procedimientos de verificación** son confiables |

Los tres primeros describen **representatividad**; los dos últimos, **calidad de la medición**. Se aplican a datos de emisiones directas, datos de actividad y factores de emisión. [VERIFICADO]

#### Puntuación cualitativa de cuatro niveles (Box 7.2) — es un **ejemplo**, no una escala numérica obligatoria

| Puntuación | Tecnología | Tiempo | Geografía | Completitud | Fiabilidad |
|---|---|---|---|---|---|
| **Very good** | Misma tecnología | < 3 años de diferencia | Misma zona | Todos los emplazamientos relevantes, periodo adecuado | Datos **verificados** basados en mediciones |
| **Good** | Tecnología similar pero distinta | < 6 años | Zona similar | > 50 % de los emplazamientos, periodo adecuado | Verificados parcialmente basados en supuestos, **o** no verificados basados en mediciones |
| **Fair** | Tecnología diferente | < 10 años | Zona diferente | < 50 % de emplazamientos, o > 50 % en periodo más corto | No verificados parcialmente basados en supuestos, o **estimación cualificada** (experto sectorial) |
| **Poor** | Tecnología desconocida | > 10 años o antigüedad desconocida | Zona desconocida | < 50 % en periodo corto, o representatividad desconocida | **Estimación no cualificada** |

**Salvedad del propio estándar** [VERIFICADO]: el sistema *tiene elementos de subjetividad*. Ejemplo que da: algunos factores de combustibles no han cambiado significativamente en años, así que un factor de más de 10 años (que puntuaría *Poor*) puede no diferir de uno de menos de 6 (*Good*).

#### Requisitos de reporte ligados a la calidad [VERIFICADO]

- **Obligatorio** reportar los tipos y fuentes de datos usados (actividad, factores de emisión, valores de GWP) **y el porcentaje de emisiones calculadas con datos obtenidos de proveedores u otros socios de la cadena de valor**.
- **Obligatorio** describir la **calidad de los datos** de las emisiones reportadas.
- Sección 7.6: en los primeros años puede ser necesario usar datos de calidad baja; hay que priorizar la mejora donde coincidan **baja calidad + emisiones altas**, y recalcular el año base cuando haya mejoras significativas (sección 9.3).
- Mayor incertidumbre en alcance 3 **es aceptable** mientras sirva a los objetivos de la empresa.
- Dato útil para el motor: la incertidumbre de los valores de **GWP** de los seis GEI principales se estima en **±35 % al 90 % de confianza** (IPCC AR4, Apéndice B). [VERIFICADO]

---

### 3.5 Estado de la revisión 2025–2026

#### El titular: el Scope 3 Standard ya no se revisa por separado

El **29 de julio de 2026** el GHG Protocol anunció que el **Corporate Standard, la Scope 2 Guidance, el Scope 3 Standard y el workstream Actions and Market Instruments (AMI) se consolidan en un único estándar**: el **Corporate Accounting and Reporting Standard, Version 3.0**, con múltiples partes, **co-publicado y con doble logo junto con ISO**, integrando además **ISO 14064-1**. El Standard Development Plan consolidado v2.0 **deroga** los cuatro planes individuales de 20 diciembre 2024. [VERIFICADO]

**Consecuencia práctica: no habrá consulta pública separada de Scope 3.** Entra en una consulta **única e integrada en Q2 2027**. [VERIFICADO]

#### Cronología

| Fecha | Hito |
|---|---|
| Nov 2022 – mar 2023 | Encuesta global de stakeholders; Scope 3 recibió más de 350 respuestas y más de 100 propuestas |
| Sep 2024 | Arranca el Scope 3 Technical Working Group (TWG) |
| 20 dic 2024 | Publicación de los 4 SDP v1.0 — hoy derogados |
| **9 sep 2025** | **Alianza estratégica ISO – GHG Protocol** para co-desarrollar estándares corporativos, de producto y de proyecto |
| 20 oct 2025 – 31 ene 2026 | Dos consultas públicas: actualización de la Scope 2 Guidance y métodos consecuenciales para emisiones evitadas del sector eléctrico |
| Dic 2025 | Corporate Standard Phase 1 Progress Update |
| Fin 2025 | 42 reuniones del Scope 3 TWG desde sep 2024 |
| **30 ene 2026** | **Publicación del Land Sector and Removals (LSR) Standard**. Entra en vigor el **1 enero 2027**. Introduce los primeros requisitos de trazabilidad del GHGP para alcance 3 |
| Q1 2026 | Miembros de ISO/TC 207/SC 7/WG4 se incorporan a los TWG; ISO entra en el Independent Standards Board como Observing Entity |
| **31 mar 2026** | **Scope 3 Standard Revisions: Phase 1 Progress Update** |
| Mar 2026 | AMI Phase 1 White Paper — Request for Information |
| **29 jul 2026** | **Anuncio de consolidación + SDP v2.0** + Scope 2 Public Consultation Summary (~1.100 respuestas de 56 países) |
| Q3–Q4 2026 (en curso) | El Scope 2 TWG procesa el feedback; el ISB decide las revisiones post-consulta |
| **Q2 2027 (estimado)** | **Borrador consolidado a consulta pública**; revisión ISO en etapa de committee draft |
| **Q4 2028 (estimado)** | **Publicación del estándar revisado** con doble logo GHGP–ISO |
| Futuro | Revisiones posteriores cada cinco años desde la publicación |

Todas las filas: [VERIFICADO].

**Vigencia** [VERIFICADO]: los estándares existentes de ambas organizaciones **siguen en vigor hasta que se publiquen los nuevos**, que incluirán periodos de transición. A 15 septiembre 2026, el Scope 3 Standard (2011) y la Technical Guidance v1.0 (2013) son **plenamente vigentes** y son la base normativa aplicable al motor.

#### Qué propone la revisión (Phase 1 Progress Update, 31 marzo 2026)

> **Estatus legal del documento** [VERIFICADO]: lleva en cada página *"This is not a GHG Protocol Standard; all content is draft and subject to change"*. El contenido **NO está sujeto a consulta pública** ahora; el Secretariado **no acepta ni procesa** feedback anticipado. El ISB aprobó publicarlo por transparencia pero **no ha aprobado** el texto. El trabajo reflejado es **anterior** a la entrada de ISO en los TWG.

**Serie A — Calidad de datos** [VERIFICADO]

| Rev. | Propuesta |
|---|---|
| A1 | **Desagregación obligatoria de las emisiones de alcance 3 por tipo de dato**, en niveles diferenciados, para incentivar datos primarios |
| A2 | **Divulgación de verificación**: declarar por inventario o por categoría si está *Fully verified*, *Partially verified* o *Not verified* |
| A5 | Favorecer factores de emisión con **alta completitud**; clarificar expectativas sobre factores regionales |
| A6 | Fijar **objetivos de especificidad de datos** y métricas de desempeño |
| A7 | Fijar **objetivos de mejora de calidad de datos** |
| A8 | **Restringir la asignación de datos corporativos a proveedores homogéneos** |

**Serie B — Límites** [VERIFICADO]

| Rev. | Propuesta |
|---|---|
| **B1** | **Umbral de exclusión del 5 %**: reportar al menos el **95 % del total de emisiones de alcance 3 requeridas**. Sustituye el enfoque cualitativo actual por un mínimo cuantitativo |
| B2, B3, B5 | Cuantificar **todas** las emisiones requeridas para validar que las exclusiones suman menos del 5 %; se admite **cualquier método, incluido el análisis de hotspots**, y excluir *de minimis* |
| B4, B6, B8 | Divulgar y justificar exclusiones; notación; ejemplos |
| B7 | **Reportar por separado** las emisiones requeridas frente a las opcionales |
| B9 | Exclusión justificada de emisiones aguas abajo de productos intermedios |
| B10a–d | Completitud y relevancia; criterios de actividades relevantes; lista de acciones que indican influencia |
| **B11** | **Nueva Categoría 16 — "Other value chain activities"**, para lo no cubierto por 1–15, incluidas **emisiones facilitadas** (actividades de terceros de las que la empresa obtiene ingreso directo y transaccional sin comprar, vender ni poseer). Incluye subcategoría de **licenciamiento**. La mayoría de sus subcategorías serían **opcionales** |
| B12 | Referencia a estándares, marcos y legislación sectoriales |

**Serie C — Inversiones (categoría 15)** [VERIFICADO]

| Rev. | Propuesta |
|---|---|
| C1 | Aplicabilidad de la categoría 15 a **todas** las empresas |
| C2–C4 | **Estrechar la categoría 15 a sólo inversiones** (financed emissions). **Seguros, underwriting y otros servicios financieros se reclasifican a la nueva categoría 16 (opcional)** |
| C5 | **Todas** las inversiones listadas son requeridas |
| **C6** | El límite requerido de inversiones incluye los **alcances 1, 2 Y 3 del investee** |
| C7 | El umbral del 5 % aplica también a la categoría 15 |
| C8 | Exclusión justificada para instrumentos sin métodos o datos |
| C9 | Divulgar el **porcentaje de valor en libros** (carrying value) cubierto |
| **C10** | La proporcionalidad de la inversión en capital incluye ahora **capital Y deuda en el denominador** — alineación con **PCAF** |
| C11–C13 | Estándares sectoriales de terceros; consolidación; límite temporal |

**Fase 2 (iniciada)** [VERIFICADO]: Serie D — límites por categoría; Serie E — categorías 10 y 11; Serie F — **circularidad** (reciclaje, cutoffs, bienes reutilizados).

#### Revisión del Corporate Standard (Phase 1, dic 2025) — lo que toca al alcance 3 [VERIFICADO]

- **Adoptar un requisito de alcance 3 en el propio Corporate Standard**, armonizado con el Scope 3 Standard y con umbral cuantitativo de exclusión.
- Umbrales cuantitativos de exclusión del **1 % para alcance 1** y **1 % para alcance 2**.
- **Límites organizacionales: eliminar el enfoque de participación accionarial (equity share)** y exigir consolidación **por control**, recomendando **control financiero** y manteniendo el control operacional como opción.
- Actualizaciones de principios: relevancia y materialidad; consistencia entre unidades y entre empresas; transparencia externa vs verificabilidad interna; nueva guía sobre **conservadurismo**.

#### Scope 2 y AMI [VERIFICADO]

- **Scope 2**: ~1.100 respuestas de 56 países; amplio apoyo a mejorar exactitud, comparabilidad e integridad de la contabilidad eléctrica. Una propuesta central es un requisito de **hourly matching y deliverability** para el método basado en mercado [SECUNDARIO en este punto concreto].
- **AMI**: se sincroniza con Scope 2; fuerte respaldo preliminar a un enfoque de reporte **multi-statement** con tres componentes: emisiones físicas, emisiones basadas en mercado ligadas a instrumentos, y declaraciones de impacto GEI con métodos consecuenciales.
- La consolidación responde a compromisos de la **COP30 Action Agenda** para armonizar estándares globales de contabilidad de GEI.

---

### 3.6 Licencia y condiciones de uso — **restrictivas**

- **Copyright © WRI y WBCSD**, 2011 (Scope 3 Standard) y 2013 (Technical Guidance v1.0). [VERIFICADO]
- **Terms of Use** [VERIFICADO]: el GHG Protocol o sus licenciantes poseen todos los derechos de propiedad intelectual. **No se puede modificar, enmarcar, reproducir, archivar, vender, arrendar, intercambiar, crear obras derivadas, publicar, mostrar, diseminar, distribuir ni retransmitir** el contenido **con fines públicos o comerciales** sin acuerdo escrito. Prohibido el *scraping* y la minería de datos. Prohibido usar el contenido sugiriendo afiliación. **La licencia es revocable** y no mantener los avisos de copyright **la anula**.
- **Respuesta directa: NO son libremente redistribuibles.** Descargar y usar internamente, sí. Redistribuir, republicar, incorporar en un producto o traducir y difundir, **requiere autorización escrita**.
- **Únicas dos excepciones bajo Creative Commons Attribution 4.0 (CC-BY 4.0)** [VERIFICADO]: *Potential Emissions from Fossil Fuel Reserves* y *Estimating and Reporting Avoided Emissions*. **El Scope 3 Standard y la Technical Guidance NO están entre ellas.**
- Existe una **Draft Licensing Policy** royalty-free cuya premisa es permitir el uso y reproducción gratuitos de herramientas y estándares para desarrollar aplicaciones de valor añadido, incluida su comercialización. **Pero sigue etiquetada como borrador y con fechas inconsistentes; no se pudo confirmar que esté finalizada ni vigente a septiembre de 2026** — **[NO VERIFICADO]**. El documento exigible hoy es el Terms of Use restrictivo.
- **Factores de emisión propios: no existen como base redistribuible.** El GHG Protocol ofrece **herramientas de cálculo**, no una base de datos de factores. Los factores provienen de terceros (IPCC, IEA, EPA, DEFRA, inventarios nacionales, bases LCA comerciales), **cada uno con su propia licencia**, que es la que rige. [VERIFICADO para la herramienta de transporte; [NO VERIFICADO] en el detalle de cada dataset, porque el portal de calculation tools devuelve HTTP 403]

> **Implicación para "Agentes ESG":** se puede **implementar la metodología** del GHG Protocol y **citarla**, pero **no se puede empaquetar ni redistribuir el texto del estándar** en el repositorio. Los factores que sí se pueden redistribuir vienen de DESNZ (OGL v3) y EPA (dominio público), no del GHG Protocol.

### 3.7 Advertencias de uso para el equipo

1. **No implementar todavía** el umbral del 95 %, la Categoría 16 ni el cambio PCAF de la categoría 15: son **borradores** explícitamente sujetos a cambio y no aprobados. Lo vigente y auditable es el estándar de 2011.
2. **La "jerarquía de los 4 métodos" es una simplificación extendida pero inexacta**: el estándar los ordena por **especificidad**, no por preferencia obligatoria, y advierte que más específico **no implica** más exacto.
3. **No existe consulta pública separada de Scope 3**: quien quiera incidir debe prepararse para la consulta integrada de **Q2 2027**.
4. **La fecha realista del estándar revisado es Q4 2028.** Las fuentes de terceros que citan "estándar final a finales de 2027" están desactualizadas respecto al SDP consolidado de julio 2026.

---

## 4. GLEC Framework e ISO 14083:2023

### 4.1 GLEC Framework — versión vigente

| Dato | Valor | Etiqueta |
|---|---|---|
| **Versión vigente a 2026-09-15** | **v3.2, octubre de 2025** | [VERIFICADO] |
| Publica | Smart Freight Centre (SFC), ONG sin ánimo de lucro, Ámsterdam | [VERIFICADO] |
| Programa | Global Logistics Emissions Council (GLEC), creado en 2014 | [VERIFICADO] |
| ISBN / ID | 978-90-833629-0-8 · SFC-GUID-001 v3.2 · 183 páginas | [VERIFICADO] |
| Cita oficial sugerida | *Smart Freight Centre. Global Logistics Emissions Council Framework for Logistics Emissions Accounting and Reporting; v3.2 edition, revised and updated (October 2025).* | [VERIFICADO] |
| URL del PDF | https://smart-freight-centre-media.s3.amazonaws.com/documents/GLEC_FRAMEWORK_v3.2_21_10_25_1.pdf | [VERIFICADO] |

**Historial de versiones** (tabla oficial, pág. 182 del v3.2) [VERIFICADO]

| Versión | Año | Cambios principales |
|---|---|---|
| 1.0 | 2016 | Versión inicial |
| 2.0 | 2019 | Alineación con GHG Protocol; sitios logísticos, vías navegables interiores, correo y paquetería |
| 3.0 | 2023 (sept) | **Alineación de lenguaje con ISO 14083**; factores actualizados |
| 3.1 | 2024 (oct; revisión mar 2025) | Valores para China, whitepaper de vehículos eléctricos, **introducción del Distance Adjustment Factor (DAF)** |
| **3.2** | **2025 (oct)** | **Valores para India, nuevo módulo de metodología de contaminantes atmosféricos** (con Stockholm Environment Institute) |

**Relación con ISO 14083 — bidireccional** [VERIFICADO]: el GLEC Framework v2 fue un **input clave** para desarrollar ISO 14083 (trabajo iniciado en 2019 a petición de la industria). Publicada la norma en 2023, SFC **reintegró las disposiciones de ISO 14083:2023 dentro del GLEC v3**. Alan Lewis (CTO de SFC) fue project manager de ISO 14083 y Verena Ehrler fue *convenor* del comité. El documento declara alineación además con GHG Protocol (Corporate, Scope 2, Scope 3), IPCC, SBTi, IATA RP 1678/1726, SmartWay, EcoTransIT World, IMO EEOI, Clean Cargo y Fraunhofer IML (hubs).

**¿Acreditado por el GHG Protocol?** Sí, con un matiz importante. [VERIFICADO]
- Lleva la marca **"Built on GHG Protocol"**, que significa que la guía se desarrolló en estrecha colaboración con el GHG Protocol y se revisó para conformidad **en el momento de su publicación**.
- La entrada del listado oficial dice: *"Global Logistics Emissions Council (GLEC) Framework (June 2016, updated Sept 2023)"* — es decir, referencia la **v3.0**.
- **Las versiones v3.1 (2024) y v3.2 (2025) no aparecen listadas individualmente** con la marca. El propio GHG Protocol advierte que documentos anteriores a estándares más nuevos pueden no reflejar requisitos actuales. Afirmar "acreditado por GHG Protocol" específicamente para v3.2 es **[NO VERIFICADO]**.

---

### 4.2 ISO 14083:2023

| Campo | Valor | Etiqueta |
|---|---|---|
| **Título oficial** | *Greenhouse gases — Quantification and reporting of greenhouse gas emissions arising from transport chain operations* | [VERIFICADO] |
| Fecha de publicación | **2023-03-20** · Edición 1 | [VERIFICADO] |
| Estado | **Publicada — Stage 60.60** (International Standard published) | [VERIFICADO] |
| Páginas / idiomas / precio | 117 pp. · inglés y francés · CHF 227 | [VERIFICADO] |
| Comité | **ISO/TC 207/SC 7** — el mismo comité con el que ahora se alía el GHG Protocol | [VERIFICADO] |
| ICS | 13.020.40 | [VERIFICADO] |
| **Sustituye a** | **IWA 16:2015** | [VERIFICADO] |
| ODS | 9, 11, 13 | [VERIFICADO] |

**Alcance**: establece una metodología común para cuantificar y reportar emisiones de GEI de la operación de cadenas de transporte de **pasajeros y mercancías**, cubriendo todos los modos (aéreo, marítimo, vías navegables interiores, carretera, ferrocarril, tuberías, teleféricos) e **incluyendo explícitamente las operaciones de hubs** (puertos, terminales, aeropuertos, centros logísticos). [VERIFICADO el alcance formal; el detalle de modos, [SECUNDARIO]]

**Versión europea: EN ISO 14083:2023** [SECUNDARIO]
- Adopción idéntica sin modificaciones; aprobada por CEN el **10 de marzo de 2023**, publicada hacia el 12 de abril de 2023.
- Adopciones nacionales: **UNE-EN ISO 14083** (España), DIN EN (Alemania), BS EN (Reino Unido), I.S. EN (Irlanda), entre otras. Toda norma nacional en conflicto se retira.

**¿Revisión, enmienda o Parte 2 en 2025–2026?** No se encontró evidencia de enmienda publicada, revisión en curso ni de una ISO 14083-2. La norma sigue en Stage 60.60. **[NO VERIFICADO]** — `iso.org` devuelve HTTP 403 a peticiones automatizadas y los metadatos se obtuvieron del espejo oficial `committee.iso.org`. Conviene comprobarlo manualmente en https://www.iso.org/standard/78864.html.

#### El desarrollo normativo más relevante de 2025–2026 es europeo, no de ISO

**Reglamento (UE) 2026/1030 — "CountEmissionsEU"** [VERIFICADO]

| Dato | Valor |
|---|---|
| Objeto | Contabilización de emisiones de GEI de los servicios de transporte |
| Adopción | **29 de abril de 2026** (2.ª lectura del Parlamento Europeo; acuerdo provisional 5 nov 2025) |
| **Entrada en vigor** | **1 de junio de 2026** |
| Norma base | **EN ISO 14083:2023** |
| Carácter | **Voluntario**: aplica a las empresas de la UE que **divulguen voluntariamente** emisiones de transporte; quien divulgue, debe hacerlo conforme al reglamento |
| Principio | **Well-to-Wheel** explícitamente |
| Aplicación plena esperada | finales de 2030 |
| Bases de datos | La Comisión, con apoyo de la AEMA, establecerá **dos bases de datos públicas y gratuitas** de factores, con un sistema escalonado de calidad de datos (desde valores por defecto hasta datos reales granulares) — [SECUNDARIO] |

> **Muy relevante para "Agentes ESG":** la UE creará bases de valores por defecto **públicas y gratuitas** alineadas con EN ISO 14083. Es potencialmente **la mejor alternativa futura** a los defaults de GLEC para el mercado europeo. Pendiente de actos delegados y de ejecución — poner en vigilancia.

---

### 4.3 Resumen metodológico (redacción propia)

#### 4.3.1 WTW = WTT + TTW

| Sigla | Qué abarca |
|---|---|
| **WTT** (Well-to-Tank) | Emisiones de **proveer el vector energético**: extracción o cultivo de la materia prima, refino o procesado, almacenamiento, transporte y distribución hasta el punto de repostaje o recarga. En electricidad incluye generación y pérdidas de transmisión y distribución. |
| **TTW** (Tank-to-Wheel) | Emisiones de **operar el vehículo**: combustión a bordo o consumo de energía durante la marcha. Es lo que mide el tubo de escape. |
| **WTW** (Well-to-Wheel) | La suma. En aire y mar el documento usa el término equivalente **Well-to-Wake**. |

**Por qué ISO 14083 exige WTW:** sin WTT las comparaciones entre tecnologías energéticas quedan sesgadas y se puede "mover" la emisión aguas arriba en lugar de reducirla. Un camión eléctrico tiene TTW ≈ 0 pero un WTT significativo según el mix eléctrico; un biocombustible puede tener un CO2 de combustión considerado compensado por el secuestro en el cultivo, pero emisiones reales en producción. Sólo el ciclo completo del vector energético permite comparar honestamente diésel, HVO, GNL, hidrógeno y electricidad. El GLEC v3.2 lo formula como requisito: **toda cadena de transporte debe reportarse en WTW**. [VERIFICADO]

**Exclusiones explícitas del sistema** [VERIFICADO]: producción y suministro de refrigerantes, residuos generados, procesos administrativos y overhead, **fabricación de vehículos y equipos de transbordo** (emisiones embebidas) y mantenimiento de vehículos.

**GEI incluidos** [VERIFICADO]: CO2, CH4, N2O, HFC, PFC, SF6, NF3, CFC, expresados en CO2e mediante GWP. La v3.2 añade un módulo separado de **contaminantes atmosféricos** (PM, black carbon, NOx, SOx); el black carbon se trata como forzador climático de vida corta.

#### 4.3.2 Tonelada-kilómetro y "transport activity"

```
t·km = masa del envío (toneladas) × distancia de actividad de transporte (km)
```

Una t·km = una tonelada de carga movida un kilómetro. Es el denominador común de eficiencia del transporte de mercancías. [VERIFICADO]

**Reglas de masa** [VERIFICADO]

| Situación | Regla GLEC v3.2 |
|---|---|
| Base general | **Masa real del envío** en toneladas métricas |
| Embalaje del expedidor | **SÍ se incluye** |
| Palés y contenedores (portadores de carga) | **NO se incluyen** |
| Contenedores vacíos transportados | Se consideran **carga**; su tara es la masa del flete |
| TEU sin peso conocido | **10 t/TEU** por defecto; **6 t/TEU** carga ligera; **14,5 t/TEU** carga pesada (si se justifica) |
| Correo y paquetería | Puede usarse el **número de ítems** como unidad alternativa, documentándolo |
| Aéreo | Masa real del envío, **no** proxies como el peso tarifable (*chargeable weight*) |
| Pasajeros | Masa real + equipaje; por defecto **100 kg** si no hay dato primario |

La distancia se cuenta **de expedidor (consignor) a destinatario (consignee)**, no sólo el tramo contratado. La actividad se calcula **por envío y por TCE por separado**, y luego se suman.

#### 4.3.3 Determinación de distancias

Tres enfoques, en orden de preferencia: [VERIFICADO]

| Enfoque | Descripción | Cuándo |
|---|---|---|
| **SFD** (Shortest Feasible Distance) | Ruta practicable más corta **considerando condiciones operativas reales**: restricciones de peso y altura del vehículo, tipo de vía, topografía y congestión. Se obtiene con software de planificación de rutas. **No** es la distancia más corta a secas. | **Recomendada en la mayoría de situaciones** |
| **GCD** (Great Circle Distance) | Distancia geodésica, incluyendo la curvatura terrestre. Atractiva para armonizar cadenas multimodales, pero hoy **sólo ampliamente aceptada en aviación**. | Aéreo (obligatoria); opcional en otros modos |
| **Distancia real + DAF** | Distancia efectivamente recorrida (odómetro, bitácora, telemática) corregida por un **Distance Adjustment Factor**. | Cuando no hay SFD ni GCD, o cuando la intensidad del TOC se calculó sobre una base de distancia distinta |

**El rol del DAF**: no es un recargo arbitrario. Se aplica **cuando el tipo de distancia usado para la actividad del TCE difiere del tipo de distancia con el que se calculó la intensidad de emisión del TOC**, para que numerador y denominador sean homogéneos. En aviación opera en sentido inverso al intuitivo: convierte distancia real → GCD, y por definición la GCD **nunca** puede superar a la distancia real.

**Factores de corrección por modo (GLEC v3.2)** [VERIFICADO — leídos del PDF oficial]

| Modo | Distancia requerida | DAF | Notas |
|---|---|---|---|
| **Carretera** | SFD (red viaria) o GCD | **+5 %** | Los valores por defecto de GLEC **ya incorporan** el +5 % por *diversionary and/or out-of-route distances*. Aplica a las tablas de Norteamérica, Europa/Sudamérica y China |
| **Ferrocarril** | SFD (inicio–fin del trayecto) | **Caso a caso**, sin default publicado | El ferrocarril tiene opciones de enrutado muy limitadas; con distancia real se exige análisis específico |
| **Marítimo (contenedor)** | SFD o GCD | **+15 % (DAF = 1,15)** | Recomendación de **Clean Cargo**: las distancias reales resultaron en promedio 15 % superiores a la ruta puerto-a-puerto factible más corta. Las tablas 16 y 17 del Módulo 2 **ya vienen ajustadas** |
| **Marítimo (no contenedor)** | SFD o GCD | **+15 %** | Las tablas incluyen columna "With 15 % DAF" |
| **Aéreo** | **GCD** entre aeropuertos, **por tramo (leg)** | **+95 km absolutos** (no porcentaje) | Partiendo de distancia real: `DAF = GCD / (GCD + 95 km)`. Los 95 km representan maniobras, rodaje y desviaciones. Los defaults GLEC ya los incluyen. Lat/lon desde la AIP nacional o fuentes basadas en ella (p. ej. OACI) |
| **Vías navegables interiores** | Bitácora > software/telemática > SFD o GCD | **No se requiere DAF** | Red con pocas opciones de ruta |
| **Teleférico / cable car** | SFD | **No se requiere DAF** | La trayectoria la define físicamente el cable |

Fuente adicional citada por GLEC para distancias marítimas: base de datos de distancias del **CERDI**. [VERIFICADO]

> **Regla de escalas (aéreo)** [VERIFICADO]: cada tramo cuenta como un TCE separado y se calcula por separado. Ignorar escalas produce **subestimación sistemática** de distancia y emisiones.

#### 4.3.4 TCE, Hub, TOC y HOC — cómo se estructura la cadena

```
Transport Chain (expedidor → destinatario)
  └── TCE ── TCE ── TCE ── TCE ...
       │      │
       │      └── cada TCE se vincula a un TOC (transporte) o a un HOC (hub)
       └── un TCE = un tramo con un vehículo, o una operación de hub
```

| Concepto | Definición operativa | Etiqueta |
|---|---|---|
| **TCE** (Transport Chain Element) | Unidad atómica: la carga movida por **un único vehículo** en un tramo. **Cada cambio de vehículo y cada paso por un hub obliga a definir un TCE nuevo.** Los TCE de hub tienen **distancia cero**. Es el nivel donde se calculan actividad y emisiones. | [VERIFICADO] |
| **Hub** | Nodo donde se transborda, transfiere o almacena carga: puerto, terminal, aeropuerto, centro de distribución, cross-docking. Genera su propio TCE con distancia cero. | [VERIFICADO] |
| **TOC** (Transport Operation Category) | Agrupación de operaciones de transporte con características similares en un periodo (normalmente un año natural). Criterios: modo, tipo de trayecto, tipo de carga, temperatura controlada, *trade lane*, naturaleza del acuerdo contractual. Es el nivel al que se calcula la **intensidad de emisión**. | [VERIFICADO] |
| **HOC** (Hub Operation Category) | El equivalente para hubs. Clusters por **procesos** (sólo transbordo de carga / sólo pasajeros / mixto / transbordo + almacenamiento), **tipo de carga** (media/mixta, contenedor o cajas móviles, paletizada, break bulk, granel seco, granel líquido, transporte de vehículos, otros) y **condiciones** (ambiente / temperatura controlada). | [VERIFICADO] |

Recomendaciones de granularidad de TOC [VERIFICADO]:
- Alinear las definiciones de TOC/HOC con las de los principales *stakeholders*, para que un cliente pueda **sumar emisiones de proveedores distintos** de forma consistente.
- Separar en TOC propio cualquier grupo cuyo impacto se quiera aislar (cambio de fuente energética, proyectos de *insetting*).
- En aéreo, los TOC **deben** considerar clusters de distancia (corto y largo radio), porque despegue y aterrizaje pesan mucho y la intensidad **no es lineal** con la distancia; también tamaño de aeronave y tipo (pasaje vs. carguero).

#### 4.3.5 Factor de carga y viajes vacíos

- **Load factor**: grado de utilización de la capacidad, expresado como porcentaje de la *Vehicle Load Capacity* (masa máxima de carga legalmente permitida). Es el principal determinante de la intensidad por t·km: la misma energía repartida entre más toneladas baja el g CO2e/t·km.
- **Empty running**: porcentaje de recorrido sin carga (retornos en vacío, reposicionamiento), expresado como % de trayectos vacíos sobre el total.
- **Regla operativa clave** [VERIFICADO]: si los datos de combustible o distancia cubren **sólo los trayectos cargados**, deben ajustarse por *empty running* añadiendo la parte de combustible correspondiente al porcentaje de trayectos vacíos sobre el total de operaciones. GLEC publica factores de *empty running* por defecto en el Módulo 2.

Ejemplo ilustrativo de las tablas GLEC v3.2 (**ferrocarril europeo, tracción diésel**) [VERIFICADO]:

| Tipo de carga | Load factor | Empty running | WTT | TTW | **WTW** (g CO2e/t·km) |
|---|---|---|---|---|---|
| Media/mixta | 60 % | 33 % | 7,1 | 23,6 | **30,7** |
| Contenedor | 50 % | 17 % | 6,6 | 21,9 | **28,5** |
| Automóviles | 85 % | 33 % | 15,3 | 50,7 | **66,0** |
| Cereales | 100 % | 38 % | 4,7 | 15,5 | **20,2** |

Se ve el efecto: "Automóviles" tiene alto load factor en masa pero intensidad altísima porque **el volumen limita antes que el peso**, más un 33 % de vacíos.

Intensidades ferroviarias WTW por región (GLEC v3.2) [VERIFICADO]:

| Región | WTW (g CO2e/t·km) | Desglose |
|---|---|---|
| UE — media (tracción desconocida) | **18,4** | Proxy: 62 % de vías electrificadas (UIC Railway Handbook 2017) |
| UE — diésel | **31** | — |
| UE — eléctrica | **10,8** | Con mix eléctrico UE medio |
| EE. UU. — diésel | **16,1** | WTT 2,7 / TTW 13,4 |
| India — mixta | **10,6** | WTT 6,4 / TTW 4,1 |

Otro ajuste documentado: **uplift del 12 %** para ferrocarril de temperatura controlada (extrapolado del uplift de carretera ante la ausencia de valores específicos de rail). [VERIFICADO]

#### 4.3.6 Intensidad GEI y asignación (allocation)

```
Emisión GEI del TCE de transporte = Actividad (t·km) × Intensidad GEI del TOC × DAF
Emisión GEI del TCE de hub        = Actividad de hub × Intensidad GEI del HOC
```

(el DAF entra sólo cuando difieren los tipos de distancia del TCE y del TOC) [VERIFICADO]

**Actividad de hub**: se cuantifica sobre las **toneladas de throughput de los envíos que SALEN** del centro (carga *outbound*). [VERIFICADO]

**Cálculo de la intensidad del TOC** (sentido inverso): energía total consumida por el TOC en el periodo → convertida a CO2e con factores WTT + TTW → dividida por la actividad total del TOC en t·km. Sin dato primario de combustible se deriva de la actividad: `combustible = t·km × intensidad de combustible (kg/t·km)`. [VERIFICADO]

**Categorías de datos (jerarquía ISO 14083)** [VERIFICADO]

| Categoría | Definición | Uso típico |
|---|---|---|
| **Primarios** | Valor cuantificado de un proceso o actividad por **medición directa** o cálculo basado en mediciones directas | Alcance 1 del operador; objetivo para el alcance 3 del comprador |
| **Secundarios — modelados** | Datos establecidos con un **modelo** que considera datos primarios y/o parámetros relevantes de la operación | Herramientas y calculadoras |
| **Secundarios — default** | **Último recurso**: valores representativos de promedios de industria | Tablas del Módulo 2 del GLEC |

**Asignación (allocation)** [VERIFICADO]
- **Principio jerárquico: la asignación debe evitarse siempre que sea posible**, mediante una desagregación más detallada de los datos.
- Cuando es inevitable (cargas consolidadas, rondas de recogida y entrega, reparto urbano multiparada), **la base de reparto es la cuota de t·km directas de cada envío** sobre el total del TCE.
- Ejemplo trabajado del propio GLEC (ronda de recogida con 14 paradas): un ítem de 250 g con 0,0024 t·km directas sobre un total de 0,3631 t·km recibe el **0,7 %** de las emisiones de la ronda. Los 4,8 litros de diésel de la ronda se convierten a 15,734 kg CO2e con el factor WTW de EE. UU., y se reparte ese total.
- En hubs, diferenciar las toneladas que requieren tratamiento especial (temperatura controlada) permite asignar en consecuencia.
- En ferry/RoRo: la intensidad se refiere a la **carga bruta de camión + mercancía**; esas emisiones deben ser **reasignadas a la carga dentro del camión** por el propietario de la mercancía.

---

### 4.4 ¿Se pueden redistribuir los valores por defecto de GLEC en un repositorio público?

### **NO.** No con una licencia open source permisiva (MIT, Apache-2.0, BSD, GPL, CC-BY).

El PDF es de **descarga gratuita y sin registro**, pero **gratuito no es libre**. La página 6 del GLEC Framework v3.2 contiene el aviso de copyright. [VERIFICADO — leído literalmente del PDF oficial]

Resumen del aviso: © Smart Freight Centre 2025. La publicación puede reproducirse total o parcialmente, en cualquier formato, **con fines educativos o sin ánimo de lucro** y sin permiso especial, siempre que se reconozca la fuente. **Queda prohibido cualquier uso para reventa o para cualquier otro fin comercial sin permiso previo por escrito de Smart Freight Centre.**

| Condición | Qué dice | Implicación para el repo |
|---|---|---|
| Descarga | Gratuita, sin muro de registro | Se puede consultar |
| Reproducción total o parcial | **Permitida** en cualquier formato | Pero sólo bajo la condición siguiente |
| Finalidad permitida | **Sólo educativa o sin ánimo de lucro** | Un repo MIT/Apache permite explícitamente uso comercial a cualquier tercero |
| Atribución | **Obligatoria** | Fácil de cumplir |
| Reventa / uso comercial | **Prohibido sin permiso previo POR ESCRITO** — con el énfasis de *"any other commercial purpose whatsoever"* | **Bloqueante** |

**Por qué es incompatible con open source.** Es efectivamente una cláusula tipo **NonCommercial (NC)**. El problema no es el uso propio, sino el de los usuarios aguas abajo:
1. Las licencias aprobadas por la OSI (MIT, Apache-2.0, GPL, BSD) **exigen** permitir el uso comercial; la Open Source Definition prohíbe discriminar campos de actividad.
2. Aunque "Agentes ESG" sea sin ánimo de lucro, publicar los valores en un repo bajo licencia permisiva equivale a **sublicenciar** a terceros derechos que no se poseen.
3. Ni siquiera CC BY-NC bastaría: la cláusula de SFC exige **permiso previo por escrito**, no sólo una restricción automática.

**Qué SÍ se puede hacer** [VERIFICADO]

| Acción | ¿Permitida? |
|---|---|
| Implementar **la metodología** (fórmulas, estructura TCE/TOC/HOC, lógica del DAF, regla de allocation) | **Sí** — los métodos y algoritmos no son objeto de copyright, sólo su expresión concreta. Esta sección es un ejemplo: describe el método con palabras propias |
| Citar valores puntuales con atribución en documentación | Zona razonablemente segura bajo cita |
| Enlazar al PDF oficial para que el usuario lo descargue | Sí |
| Ofrecer un *adaptador* que lea un fichero GLEC que el usuario aporte por su cuenta | Sí — el usuario gestiona su propia licencia |
| **Volcar las tablas del Módulo 2 como CSV/JSON en el repo bajo MIT/Apache** | **No**, sin permiso escrito de SFC |
| Pedir permiso escrito a SFC | Recomendado: `info@smartfreightcentre.org` |

**Contraste revelador: la licencia de Clean Cargo es distinta** [VERIFICADO]. El documento *Clean Cargo Ocean Containership GHG Emission Intensity Calculation Methods* (mayo 2025), **también de Smart Freight Centre**, permite el uso para reventa o fines comerciales **siempre que el usuario notifique previamente por escrito** a `info@smartfreightcentre.org`. Es la diferencia entre *opt-out* y *opt-in*: para Clean Cargo basta **notificar**; para GLEC hace falta **obtener permiso**. Si se necesitan factores marítimos de contenedor, esa vía es mucho más practicable — y vale la pena preguntar a SFC si aceptarían alinear la cláusula del GLEC con la de Clean Cargo.

---

### 4.5 Alternativas públicas redistribuibles

| Fuente | Licencia exacta | ¿Redistribución comercial? | ¿Apta para repo open source? | URL |
|---|---|---|---|---|
| **UK DESNZ/DEFRA GHG Conversion Factors 2026** | **Open Government Licence v3.0** | **Sí** — copiar, publicar, distribuir, adaptar y **explotar comercialmente**; única obligación: atribución | **SÍ — mejor opción general** | gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026 |
| **ADEME Base Empreinte / Base Carbone®** | **Licence Ouverte / Open Licence** (SPDX `etalab-2.0`) | **Sí** — reproducir, redistribuir, adaptar y explotar comercialmente; obligación: atribución con fuente y fecha de última actualización | **SÍ — compatible con CC-BY 4.0 y ODbL** | data.ademe.fr/datasets/base-carboner |
| **US EPA** (SmartWay, GHG Emission Factors Hub, Supply Chain Factors) | **Dominio público** (17 U.S.C. § 105) | **Sí, sin restricciones** | **SÍ — la más permisiva** (sin obligación de atribución, aunque es buena práctica) | epa.gov/climateleadership/ghg-emission-factors-hub |
| **NZ Measuring Emissions Catalogue 2026** | **CC BY 4.0** [SECUNDARIO] | Sí, con atribución | Sí — útil para Oceanía y marítimo internacional | measuringemissionsguide.environment.govt.nz/8_freight.html |
| **EcoTransIT World** | *"The use or reproduction of data, diagrams or formulas requires the express written permission of the authors or publishers"* [VERIFICADO — leído del PDF de metodología v4.0] | **No** — sólo se permite **referenciar** con atribución | **NO** | ecotransit.org |
| **Clean Cargo (SFC)** — marítimo contenedor | Uso comercial permitido **con notificación escrita previa** | Condicionado | **Posible tras notificar** — no es open source estricto, pero es viable | smart-freight-centre-media.s3.amazonaws.com |
| **GLEC Framework v3.2** | NC + permiso escrito para uso comercial | **No** | **NO** | (ver 4.4) |
| **NTM** (Network for Transport Measures) | Membresía **100–1.000 €** según facturación [SECUNDARIO] | No — acceso por socios | No | transportmeasures.org |
| **IMO** (EEOI, MEPC) | Los documentos IMO suelen llevar copyright de la Organización | Sin verificar | **Verificar antes de usar** | **[NO VERIFICADO]** |
| **Bases CountEmissionsEU (CE / AEMA)** | Aún no publicadas; pendientes de actos delegados. Anunciadas como **públicas y gratuitas** | Probablemente CC-BY 4.0 (política estándar de datos abiertos de la UE) | **Vigilar — posible mejor opción futura** | [SECUNDARIO] |

#### El hallazgo más accionable: reconstruir desde las fuentes primarias del propio GLEC

El GLEC Framework **declara sus fuentes primarias**, y varias son abiertas. En la pág. 99 lista como inputs de sus valores de carretera: [VERIFICADO]

1. SmartWay truck data 2024 (Norteamérica) → **EPA, dominio público** ✅
2. HBEFA database → licencia comercial ❌
3. **UK Government GHG Conversion Factors** → **OGL v3** ✅
4. **Base Carbone** (art. L.1431-3 del Código de Transportes francés) → **Licence Ouverte** ✅
5. NTM → membresía ❌

Es decir: **se puede reconstruir gran parte de la cobertura desde las fuentes abiertas aguas arriba**, implementando la metodología GLEC/ISO 14083 (que es libre de usar) sobre datasets con licencia compatible.

**Arquitectura de datos propuesta para el repositorio**

| Capa | Fuente | Licencia |
|---|---|---|
| **Metodología** (TCE/TOC/HOC, WTW, DAF, allocation) | ISO 14083 / GLEC — reimplementada con palabras propias | Libre (los métodos no son copyrightables) |
| **Carretera Europa** | DESNZ 2026 + ADEME Base Empreinte | OGL v3 + Etalab 2.0 |
| **Carretera Norteamérica** | EPA SmartWay + Emission Factors Hub | Dominio público |
| **Ferrocarril, aéreo y marítimo** | DESNZ 2026 (cubre los tres) + NZ MfE | OGL v3 + CC BY 4.0 |
| **Marítimo contenedor por trade lane** | Clean Cargo, previa notificación escrita a SFC | Condicionada |
| **Futuro (2027+)** | Bases CountEmissionsEU | Por determinar |

> Documentar en el README la **procedencia y licencia de cada factor**, y añadir un test automatizado que verifique la **ausencia de valores GLEC** en los datos versionados.

---

### 4.6 Acreditación y verificación

Existen **dos mecanismos distintos** que conviene no confundir: [SECUNDARIO — la web de SFC es JS-only y no fue legible; los datos provienen de terceros fiables]

| Programa | Qué certifica |
|---|---|
| **SFC Certification** (antes "GLEC-accredited tools") | **Herramientas y programas de cálculo**: conformidad metodológica con ISO 14083 y correcta aplicación del GLEC Framework, en cálculo y en reporte. Incluye revisión documental y pruebas con cálculos de muestra |
| **SFC Conformity Assessment Scheme (CAS)** | **Aseguramiento independiente de reportes de emisiones**. Aprueba *Validation and Verification Bodies* (VVB) para el alcance ISO 14083 |

**VVB aprobados para ISO 14083** [SECUNDARIO]: **Verifavia** (Normec, el primero, 2023), **SGS** (mayo 2024), **SCS Global Services**, y un cuarto organismo.
**Herramientas con certificación SFC** (ejemplos) [SECUNDARIO]: Colissimo (oct 2024), Dcycle, Flexport, Fluent Cargo, Flock Freight (abr 2025).

**¿Es obligatorio?** **No, es completamente voluntario.** [VERIFICADO]
- ISO 14083 es una norma voluntaria, sin certificación obligatoria asociada.
- Incluso el Reglamento (UE) 2026/1030 **es voluntario** en cuanto a la divulgación: sólo obliga a seguir su método a quien decida publicar datos de emisiones de transporte.
- Para un proyecto open source la certificación SFC no aporta nada obligatorio. Se puede declarar **"metodología alineada con ISO 14083 / GLEC Framework v3.2"** sin certificación, siempre que **no se afirme estar *certificado* ni *acreditado***, lo que sería engañoso.

**¿Cuánto cuesta?** **SFC no publica tarifas** — **[NO VERIFICADO]**. Hay que contactar `certification@smartfreightcentre.org`. El coste del aseguramiento bajo CAS lo fija cada VVB de forma independiente, no SFC.

---

## Fórmulas y métodos

### F.1 Transporte de carga por tonelada·kilómetro (categorías 4 y 9)

```
Actividad_de_transporte [t·km] = Masa_carga [t] × Distancia [km]

E_TTW [kg CO2e] = Actividad_de_transporte × FE_TTW [kg CO2e / t·km]
E_WTT [kg CO2e] = Actividad_de_transporte × FE_WTT [kg CO2e / t·km]
E_WTW [kg CO2e] = E_TTW + E_WTT
```

Reglas de implementación:

1. **Masa en toneladas métricas**, incluido el embalaje que viaja con la carga.
2. **Distancia**: preferir la real recorrida; si no, distancia de red; si no, distancia geodésica corregida por un factor de rodeo por modo (ver sección 4).
3. **Una fila por tramo (TCE)**: una cadena puerta-a-puerta se descompone en tramos con modo propio, y la emisión total es la suma de los tramos más los hubs.
4. **Sumar siempre WTT**: reportar sólo TTW subestima entre un 15 % y un 30 % según el modo.
5. **Carga aérea**: elegir explícitamente "con RF" o "sin RF" y mantener el criterio en toda la serie temporal. DESNZ recomienda usar "con RF" (+70 % sobre el CO2).

### F.2 Cadena multimodal

```
E_total = Σ_tramos ( masa_t × distancia_km × FE_modo_WTW )  +  Σ_hubs ( masa_t × FE_hub )
```

### F.3 Viajes de negocios

```
E_vuelo  = Σ ( pasajeros × distancia_km × FE_haul_clase[conRF|sinRF] )
E_auto   = distancia_km × FE_auto_por_combustible          (factor de vehículo completo)
E_tren   = pasajeros × distancia_km × FE_tren              (factor por pasajero·km)
E_hotel  = habitaciones × noches × FE_pais_por_habitacion_noche
```

> El uplift de distancia del 8 % **ya está incluido** en los factores aéreos DESNZ: no aplicarlo otra vez.

### F.4 Residuos y agua

```
E_residuos = Σ_material Σ_via ( toneladas × FE_material_via )
E_agua     = m3_suministrados × FE_suministro  +  m3_vertidos × FE_tratamiento
```

### F.5 Método por gasto (categoría 1 y 2)

```
E = Gasto_local(año t) ÷ FX(local→USD, promedio año t)
      × (IPC_US_base / IPC_US_t)
      × FE_NAICS(SEF+MEF)
      × k_pais
```

### F.6 Jerarquía de métodos que debe implementar el motor

| Prioridad | Método | Cuándo usarlo | Incertidumbre |
|---|---|---|---|
| 1 | Datos de proveedor / específico | El proveedor entrega su huella verificada del producto | Baja |
| 2 | Híbrido | Mezcla datos primarios del proveedor con factores promedio para los vacíos | Media-baja |
| 3 | Datos de actividad física (promedio) | Hay masa, distancia, litros, kWh, toneladas de residuo, m3 de agua | Media |
| 4 | Gasto | Sólo hay la factura en pesos, soles o euros | Alta |

El motor debe **etiquetar cada línea de cálculo con el método usado** y reportar el porcentaje del inventario que proviene de cada nivel: es el indicador de calidad que exigen tanto CSRD como SBTi.

### F.7 Ejemplo numérico completo — PyME exportadora chilena

**Caso.** "Frutas del Maule SpA", Talca, Chile. Ejercicio 2026. Envía **18 toneladas** de fruta a Rotterdam y hace un viaje comercial a Madrid.

**Tramo 1 — camión refrigerado Talca → Puerto de San Antonio, 320 km**

Se usa el factor DESNZ "HGV (refrigerated, all diesel) — Average refrigerated artics", porque es carga refrigerada en camión articulado.

```
Actividad  = 18 t × 320 km = 5.760 t·km
E_TTW = 5.760 × 0,09166 = 527,96 kg CO2e
E_WTT = 5.760 × 0,02114 = 121,77 kg CO2e
E_WTW = 649,73 kg CO2e
```

**Tramo 2 — portacontenedores San Antonio → Rotterdam, 13.200 km (distancia marítima aproximada)**

Factor "Container ship — Average".

```
Actividad  = 18 t × 13.200 km = 237.600 t·km
E_TTW = 237.600 × 0,01612 = 3.830,11 kg CO2e
E_WTT = 237.600 × 0,00365 =   867,24 kg CO2e
E_WTW = 4.697,35 kg CO2e
```

**Tramo 3 — camión Rotterdam → cliente, 150 km, HGV no refrigerado promedio**

```
Actividad  = 18 t × 150 km = 2.700 t·km
E_WTW = 2.700 × (0,10356 + 0,02359) = 2.700 × 0,12715 = 343,31 kg CO2e
```

**Subtotal categoría 4 (transporte aguas arriba): 649,73 + 4.697,35 + 343,31 = 5.690,39 kg CO2e ≈ 5,69 t CO2e**

> Lectura para el usuario no técnico: **el 83 % de la huella logística de este envío está en el barco**, no por ser ineficiente (el barco es, por t·km, unas 6 veces mejor que el camión) sino por la distancia. Optimizar el camión chileno mueve poco la aguja; consolidar carga y llenar el contenedor sí.

**Viaje de negocios — Santiago → Madrid ida y vuelta, clase económica, 2 noches de hotel**

Distancia sin escalas ≈ 10.750 km por trayecto → 21.500 km ida y vuelta. Chile es **Long Haul** según la hoja `Haul definition`. Factor "Long-haul, to/from UK — Economy class, con RF" = 0,11704 kg CO2e/pasajero·km.

```
E_vuelo = 1 pasajero × 21.500 km × 0,11704 = 2.516,36 kg CO2e
E_hotel = 1 habitación × 2 noches × 7,0 (España) = 14,0 kg CO2e
Total viaje = 2.530,36 kg CO2e ≈ 2,53 t CO2e
```

> Un solo viaje ida y vuelta a Europa en económica equivale a **casi la mitad** de toda la logística de un contenedor de 18 toneladas. En business (0,33940) el mismo vuelo daría 7.297,10 kg CO2e, casi **3 veces más**.

**Compras por gasto — categoría 1, servicios de consultoría**

La empresa gastó **8.500.000 CLP** en consultoría en 2026. Tipo de cambio promedio 2026 supuesto: **950 CLP/USD** (el motor debe leer el valor real del Banco Central). Inflación acumulada USA 2022→2026 supuesta: **12 %** (el motor debe leer el CPI-U real).

```
Gasto_USD_nominal_2026 = 8.500.000 / 950            = 8.947,37 USD
Gasto_USD_2022 (deflactado) = 8.947,37 / 1,12       = 7.988,72 USD 2022
FE NAICS 541611 (SEF+MEF)                           = 0,078 kg CO2e/USD 2022
E = 7.988,72 × 0,078                                = 623,12 kg CO2e ≈ 0,62 t CO2e
```

> **Sentido del error:** si se omite la deflactación y se aplica el factor directamente sobre los 8.947,37 USD nominales, el resultado es 697,89 kg CO2e, un **12 % más alto** que el valor correcto de 623,12 kg. Es decir, **no deflactar SOBREESTIMA** las emisiones: los dólares extra que aporta la inflación se contabilizan como si fueran actividad física adicional. Deflactar es obligatorio para no contar inflación como si fuera carbono.

**Resumen del ejemplo**

| Partida | Categoría GHG Protocol | t CO2e | Método | Calidad |
|---|---|---|---|---|
| Logística del envío (3 tramos) | Cat. 4 | 5,69 | Actividad física (t·km) | Media |
| Viaje de negocios + hotel | Cat. 6 | 2,53 | Actividad física (pas·km, noches) | Media |
| Consultoría | Cat. 1 | 0,62 | Gasto | Alta incertidumbre |
| **Total del ejemplo** | | **8,84** | | |

---

## Cambios recientes (2024–2026)

### DESNZ / DEFRA

| Año | Cambio | Impacto para el motor | Etiqueta |
|---|---|---|---|
| **2026** | **Nueva metodología de la electricidad UK**: el desfase de datos pasa de 2 años a 1. El factor cae ~26 % respecto de 2025 (0,13096 kg CO2e/kWh). Afecta en cascada a EV, ferrocarril y teletrabajo. | Romper la comparabilidad interanual; obliga a **re-baselinear** si se comparan 2025 y 2026. | [VERIFICADO] |
| **2026** | **Factores ferroviarios actualizados** con datos de la Office of Rail and Road (2025) y Transport for London; los anteriores usaban datos 2019 pre-COVID y no se tocaban desde 2021. Afecta national rail, Eurostar, light rail/tram y London Underground. | Cambian los factores de viaje de negocios en tren. | [VERIFICADO] |
| **2026** | **Renombres en HGV**: `HGV (all diesel)` → `HGV (non-refrigerated, all diesel)`; `HGV refrigerated (all diesel)` → `HGV (refrigerated, all diesel)`; `All rigids/artics/HGVs` → `Average rigids/artics/HGVs`. Las tablas se reordenaron para poner "Average laden" justo después de Activity/Type/Unit. | **Rompe cualquier parser que busque los nombres antiguos.** Hay que mapear alias. | [VERIFICADO] |
| **2026** | Nueva explicación (FAQ) sobre cómo capturar todas las emisiones de PHEV y BEV a través de las distintas hojas. | Sólo documental, sin cambio de valores. | [VERIFICADO] |
| **2026** | Los factores de **hotel** NO se actualizaron: la hoja `Hotel stay` es idéntica a la de 2025. | Se puede reutilizar la tabla 2025 sin cambios. | [VERIFICADO] |
| **2025** | **Mejora en aviación**: se reemplazaron los datos confidenciales CAA de 2012 por datos públicos recientes de la CAA para repartir vuelos, km y tonelada-km entre doméstico, corto y largo radio. | Cambió toda la familia de factores aéreos. | [VERIFICADO] |
| **2025** | **Residuos**: el factor de separación mecánica bajó de 3,44 a 1,64, más actualización de HGV de recogida y del factor de red eléctrica. Afecta ciclo abierto, ciclo cerrado y combustión. | Caída proporcional grande, pero absoluta pequeña (~2 kg/t). | [VERIFICADO] |
| **2025** | La vía antes llamada **"combustion"** se aclaró como **"incineración con recuperación de energía"**: para el generador del residuo sólo cuentan recogida y transporte al primer punto de proceso; la combustión se asigna al usuario final de la energía. **No existe factor para incineración sin recuperación de energía**, y usar éste en ese caso **subestima**. (El libro 2026 mantiene el encabezado de columna `Combustion`.) | Advertencia obligatoria en la UI del motor. | [VERIFICADO] |

### US EPA Supply Chain Factors

| Año | Cambio | Impacto | Etiqueta |
|---|---|---|---|
| **2024 (v1.3, vigente)** | Datos de emisiones 2022; **GWP AR5** en lugar de AR4; tablas input-output **benchmark 2017** de BEA; modelo de atribución sectorial mejorado; año-dólar 2022. | Cambio de año base monetario 2021 → 2022: obliga a rehacer la deflactación. | [VERIFICADO] |
| **2024 (v1.3)** | **Pérdida de desagregación del sector residuos**: todos los `562*` comparten un único factor 0,988. El relleno sanitario `562212` cayó de 10,989 (v1.2) a 0,988, un −91 %. | Si el motor usaba v1.2 para residuos por gasto, los resultados caen un orden de magnitud. | [VERIFICADO] |
| **2024 (v1.3)** | Mediana de cambio de los SEF respecto a v1.2: **−18 %**. 796 de 1.016 factores bajaron más de 5 %; 139 subieron más de 5 %. Las caídas en agricultura y minería se explican porque el producto económico 2019→2022 creció más que las emisiones. | Congelar la versión en configuración y re-baselinear al migrar. | [VERIFICADO] |
| **2025–2026** | **No se publicó v1.4.** v1.3.0 (5 julio 2024) sigue siendo la versión vigente a 15 septiembre 2026. | El motor puede fijar v1.3 con seguridad. | [VERIFICADO] |

---

## Pendientes y dudas

### P.1 Valores que NO se pudieron verificar y hay que confirmar antes de cargarlos al motor

| # | Qué falta | Por qué no se pudo | Cómo resolverlo |
|---|---|---|---|
| 1 | **Cinco factores EPA de códigos NAICS altos**: 541810 (publicidad), 722511 (restaurantes), 721110 (hoteles), 561720 (limpieza), 561612/561610 (seguridad) | La lectura remota del CSV se **trunca en el código 541720**; dos rutas independientes devolvieron **valores contradictorios entre sí**, señal de lectura fuera del rango realmente recibido | Abrir localmente el CSV completo: https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv |
| 2 | **Factor de hotel para Perú** | **No existe** en los sets DESNZ 2025 ni 2026 (verificado en ambos libros) | Consultar https://www.hotelfootprints.org (Cornell CHSB) y etiquetar **[SECUNDARIO]**; o exigir dato primario del hotel |
| 3 | Factores de hotel de Argentina, Austria, Chequia, Finlandia, Grecia, Irlanda, Israel, Kazajistán, Macao, Nueva Zelanda, Panamá, Polonia, Rumanía, Taiwán | Sin valor en DESNZ 2026 | Misma vía: hotelfootprints.org |
| 4 | **Estado de la revisión sistemática de ISO 14083:2023** (¿hay enmienda o Parte 2 en curso?) | `iso.org` devuelve **HTTP 403** a peticiones automatizadas; los metadatos se obtuvieron del espejo `committee.iso.org` | Comprobar manualmente https://www.iso.org/standard/78864.html |
| 5 | **Licencia de los documentos IMO** (EEOI, MEPC) para factores marítimos | No verificada | Revisar los términos de uso de imo.org antes de usar cualquier valor |
| 6 | **Tarifas de certificación SFC** | SFC no las publica | Contactar `certification@smartfreightcentre.org` |
| 7 | **Detalle de las dos bases de datos públicas de CountEmissionsEU** (contenido, licencia, fecha) | Aún no publicadas; pendientes de actos delegados y de ejecución | Vigilar transport.ec.europa.eu y la AEMA |
| 8 | **Estado de la Draft Licensing Policy del GHG Protocol** | Sigue etiquetada como borrador, con fechas inconsistentes en la página | Consultar directamente al GHG Protocol si se quisiera redistribuir texto del estándar |
| 9 | **Términos de licencia de los datasets de factores enlazados por el GHG Protocol** | El portal de *calculation tools* redirige a un Zendesk que devuelve **HTTP 403** | Revisar caso por caso el metadato de cada dataset |
| 10 | Valores DESNZ 2026 de *Products/Chemical/LNG/LPG tanker* y *Refrigerated cargo* en su componente **WTT** | No se extrajeron todas las filas en esta pasada | Están en la hoja `WTT- delivery vehs & freight` del mismo libro ya identificado |

### P.2 Archivos que hay que abrir localmente (URLs exactas)

| Archivo | URL |
|---|---|
| DESNZ 2026 — full set (fuente de toda la sección 1) | https://assets.publishing.service.gov.uk/media/6a29392bade52dc0882218a8/ghg-conversion-factors-2026-full-set.xlsx |
| DESNZ 2026 — flat file (para procesamiento automático) | https://assets.publishing.service.gov.uk/media/6a6c9748862aaf18d9c62ac9/ghg-conversion-factors-2026-flat-format-revised.xlsx |
| DESNZ 2026 — metodología (152 pp.) | https://assets.publishing.service.gov.uk/media/6a2940543b15d05a7ce3202e/2026-GHG-conversion-factors-methodology-report.pdf |
| DESNZ 2026 — cambios mayores (18 pp.) | https://assets.publishing.service.gov.uk/media/6a2940653b15d05a7ce3202f/2026-GHG-conversion-factors-major-changes-report.pdf |
| DESNZ 2025 — full set (comparación) | https://assets.publishing.service.gov.uk/media/6846a4f55e92539572806125/ghg-conversion-factors-2025-full-set.xlsx |
| EPA — CSV CO2e v1.3 | https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv |
| EPA — CSV por gas v1.3 | https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_byGHG_USD2022.csv |
| EPA — CSV de cambio relativo v1.2→v1.3 | https://pasteur.epa.gov/uploads/10.23719/1531143/documents/RelativeChangefromv1.2tov1.3.0inSEFsinCO2e.csv |
| GLEC Framework v3.2 (consulta, **no redistribuir**) | https://smart-freight-centre-media.s3.amazonaws.com/documents/GLEC_FRAMEWORK_v3.2_21_10_25_1.pdf |

> **Sobre el flat file DESNZ:** es la vía recomendada para poblar la base de datos del motor, porque está en formato largo (una fila por combinación actividad/tipo/unidad) en lugar de tablas anchas por combustible. Fue **revisado el 31 de julio de 2026** — usar esa versión, no la original de junio.

### P.3 Decisiones de diseño que el equipo debe tomar

1. **Radiative forcing en aviación: ¿con RF o sin RF por defecto?** DESNZ recomienda "con RF" (+70 % sobre el CO2) pero advierte de la **incertidumbre científica significativa**. Cambiar el criterio a mitad de serie obliga a re-baselinear. **Recomendación: "con RF" por defecto, configurable, y siempre declarado en el reporte.**
2. **Hoteles: son OPCIONALES en la categoría 6 del GHG Protocol.** Decidir si se incluyen por defecto y declararlo.
3. **`k_país` en el método por gasto:** ¿k = 1 (simple y auditable) o ajuste por intensidad de carbono nacional? **Recomendación: k = 1 con la limitación declarada**, y `k` configurable para usuarios avanzados.
4. **Tipo de cambio de mercado vs PPA** en la conversión de moneda. El de mercado **subestima** en Chile y Perú; la PPA es más correcta técnicamente pero más difícil de defender ante un auditor.
5. **Versionado de sets de factores.** DESNZ cambia cada junio y EPA sin calendario fijo. El motor debe **fijar la versión en configuración**, registrarla en cada cálculo y advertir cuando el usuario compare años con sets distintos.
6. **Alias de nombres DESNZ.** El cambio de nombres de HGV en 2026 (`All rigids` → `Average rigids`, etc.) rompe parsers. Mantener una tabla de alias.
7. **No empaquetar valores GLEC.** Añadir un test automatizado que verifique su ausencia en los datos versionados.

### P.4 Dudas metodológicas señaladas

- **DESNZ no publica factores por gasto para viajes aéreos** y lo dice explícitamente: *no hay benchmarks de industria fiables de CO2e por libra gastada en transporte aéreo*; recomienda mejorar la recogida de datos para reportar por distancia. Conviene replicar esa advertencia en la UI.
- **La comparabilidad interanual del factor eléctrico del Reino Unido está rota en 2026** por el cambio de metodología (−26 %). No es una mejora de desempeño del usuario.
- **Los factores DESNZ de residuos para reciclaje e incineración cubren sólo transporte.** Un usuario no técnico puede concluir erróneamente que "reciclar casi no emite". Hay que explicarlo en la interfaz.
- **El factor único de residuos de EPA (0,988 para todo `562*`) es una regresión** respecto a v1.2. Si el motor estimaba residuos por gasto, cambió un orden de magnitud.
- **Los factores DESNZ son británicos.** Aplicados a Chile o Perú arrastran el mix eléctrico y el parque vehicular del Reino Unido. Para carretera son razonables como proxy; para cualquier cosa que dependa de electricidad, no. Declararlo siempre.

---

## Fuentes

### Fuentes oficiales primarias (leídas directamente)

1. **UK DESNZ — Greenhouse gas reporting: conversion factors 2026** (publicado 11 jun 2026, actualizado 31 jul 2026). Licencia OGL v3.0. https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2026
2. **DESNZ 2026 — full set (.xlsx, 40 hojas)** — fuente de todos los valores de la sección 1. https://assets.publishing.service.gov.uk/media/6a29392bade52dc0882218a8/ghg-conversion-factors-2026-full-set.xlsx
3. **DESNZ 2026 — flat file revisado (jul 2026)**. https://assets.publishing.service.gov.uk/media/6a6c9748862aaf18d9c62ac9/ghg-conversion-factors-2026-flat-format-revised.xlsx
4. **DESNZ 2026 — methodology report (PDF, 152 pp.)**. https://assets.publishing.service.gov.uk/media/6a2940543b15d05a7ce3202e/2026-GHG-conversion-factors-methodology-report.pdf
5. **DESNZ 2026 — major changes report (PDF, 18 pp.)**. https://assets.publishing.service.gov.uk/media/6a2940653b15d05a7ce3202f/2026-GHG-conversion-factors-major-changes-report.pdf
6. **DESNZ 2025 — full set (.xlsx)**, usado para comparación interanual. https://assets.publishing.service.gov.uk/media/6846a4f55e92539572806125/ghg-conversion-factors-2025-full-set.xlsx
7. **Colección DESNZ de factores de conversión** (todos los años, 2002–2026). https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting
8. **Open Government Licence v3.0**. https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
9. **US EPA — Supply Chain GHG Emission Factors v1.3 by NAICS-6** (Science Inventory). https://cfpub.epa.gov/si/si_public_record_report.cfm?dirEntryId=362515&Lab=CESER
10. **EPA — CSV de factores CO2e v1.3.0 (USD 2022)**. https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_CO2e_USD2022.csv
11. **EPA — CSV de factores por gas v1.3.0**. https://pasteur.epa.gov/uploads/10.23719/1531143/SupplyChainGHGEmissionFactors_v1.3.0_NAICS_byGHG_USD2022.csv
12. **EPA — "About the Supply Chain GHG Emission Factors v1.3 NAICS-6 Datasets"** (Ingwersen, 5 jul 2024) — metodología, tablas 1–5, notas de uso. https://pasteur.epa.gov/uploads/10.23719/1531143/documents/Aboutv1.3SupplyChainGHGEmissionFactors.docx
13. **EPA ScienceHub — licencia de datos (dominio público, 17 U.S.C. § 105)**. https://pasteur.epa.gov/license/sciencehub-license.html
14. **EPA — catálogo del dataset en data.gov**. https://catalog.data.gov/dataset/supply-chain-greenhouse-gas-emission-factors-v1-3-by-naics-6
15. **EPA — código fuente de los factores**. https://github.com/USEPA/supply-chain-factors
16. **GHG Protocol — Corporate Value Chain (Scope 3) Accounting and Reporting Standard** (2011, e-reader 2013). https://ghgprotocol.org/sites/default/files/standards/Corporate-Value-Chain-Accounting-Reporing-Standard-EReader_041613_0.pdf
17. **GHG Protocol — Technical Guidance for Calculating Scope 3 Emissions v1.0** (2013), introducción. https://ghgprotocol.org/sites/default/files/2022-12/Intro_GHGP_Tech.pdf
18. **Technical Guidance — Capítulo 1 (Categoría 1: los 4 métodos, Box 1.1)**. https://ghgprotocol.org/sites/default/files/2022-12/Chapter1.pdf
19. **Technical Guidance — Capítulo 4 (Categoría 4: los 3 métodos, árbol de decisión)**. https://ghgprotocol.org/sites/default/files/2022-12/Chapter4.pdf
20. **Technical Guidance — Capítulo 6 (Categoría 6: viajes de negocios, hoteles opcionales)**. https://ghgprotocol.org/sites/default/files/2022-12/Chapter6.pdf
21. **GHG Protocol — Scope 3 Standard Revisions: Phase 1 Progress Update (31 mar 2026)**. https://ghgprotocol.org/sites/default/files/2026-03/S3-Phase1ProgressUpdate-20260331.pdf
22. **GHG Protocol — Consolidated Standard Development Plan v2.0 (29 jul 2026)**. https://ghgprotocol.org/sites/default/files/2026-07/Consolidated-StandardDevelopmentPlan(SDP)-2026.07.29.pdf
23. **GHG Protocol — anuncio de consolidación de estándares (29 jul 2026)**. https://ghgprotocol.org/blog/ghg-protocol-announces-key-standard-development-updates
24. **GHG Protocol — FAQ del anuncio** (consulta Q2 2027, publicación Q4 2028). https://ghgprotocol.org/blog/ghg-protocol-announces-key-standard-development-updates-faq-resource
25. **GHG Protocol — FAQ de la alianza con ISO (9 sep 2025)**. https://ghgprotocol.org/blog/iso-ghg-protocol-partnership-frequently-asked-questions
26. **GHG Protocol — Corporate Standard Phase 1 Progress Update (dic 2025)**. https://ghgprotocol.org/sites/default/files/2025-12/CS-Phase1-ProgressUpdate.pdf
27. **GHG Protocol — lanzamiento del Land Sector and Removals Standard (30 ene 2026)**. https://ghgprotocol.org/blog/release-ghg-protocol-launches-its-first-ever-global-standard-corporate-accounting-land-sector
28. **GHG Protocol — Terms of Use** (licencia restrictiva; excepciones CC-BY 4.0). https://ghgprotocol.org/terms-use
29. **GHG Protocol — listado "Built on GHG Protocol"** (incluye GLEC Framework, actualización sept 2023). https://ghgprotocol.org/guidance-built-ghg-protocol
30. **Smart Freight Centre — GLEC Framework v3.2 (oct 2025, 183 pp.)** — consulta permitida, **redistribución comercial prohibida**. https://smart-freight-centre-media.s3.amazonaws.com/documents/GLEC_FRAMEWORK_v3.2_21_10_25_1.pdf
31. **Smart Freight Centre — anuncio de GLEC Framework v3.2**. https://smartfreightcentre.org/news/13311209
32. **Smart Freight Centre — Clean Cargo Ocean Containership GHG Emission Intensity Calculation Methods (may 2025)** — licencia más abierta que GLEC. https://smart-freight-centre-media.s3.amazonaws.com/documents/Clean_Cargo_GHG_Emission_Intensity_Calculation_Methods_2025-05-16.pdf
33. **ISO 14083:2023 — metadatos oficiales** (espejo `committee.iso.org`; `iso.org` devuelve HTTP 403). https://committee.iso.org/es/sites/isoorg/contents/data/standard/07/88/78864.html
34. **ISO 14083:2023 — ficha oficial** (inaccesible a fetch automatizado). https://www.iso.org/standard/78864.html
35. **Comisión Europea — Reglamento (UE) 2026/1030 "CountEmissionsEU"**, en vigor el 1 jun 2026. https://transport.ec.europa.eu/news-events/news/new-eu-rules-harmonising-transport-emissions-calculations-take-effect-2026-06-01_en
36. **ADEME — Base Carbone®, Licence Ouverte (Etalab 2.0)**. https://data.ademe.fr/datasets/base-carboner
37. **ADEME — descarga de Base Empreinte**. https://base-empreinte.ademe.fr/donnees/download-data
38. **data.gouv.fr — registro de licencias abiertas**. https://www.data.gouv.fr/pages/legal/licences/
39. **US EPA — GHG Emission Factors Hub**. https://www.epa.gov/climateleadership/ghg-emission-factors-hub
40. **EcoTransIT World — Methodology Report v4.0 (ISO 14083)** — cláusula de propiedad intelectual restrictiva. https://www.ecotransit.org/wp-content/uploads/EcoTransIT_World_Methodology_Report_Version_4_ISO14083.pdf
41. **Hotel Footprinting Tool** (origen de los factores de hotel de DESNZ). https://www.hotelfootprints.org
42. **WRAP — Carbon Waste and Resources Metric** (citada por DESNZ; no apta para reportar alcance 3). https://wrap.org.uk/resources/report/carbon-waste-and-resources-metric

### Fuentes secundarias (marcadas como [SECUNDARIO] en el texto)

43. **EN ISO 14083:2023 — catálogo CEN**. https://standards.iteh.ai/catalog/standards/cen/b3847a9b-7881-4a67-a592-8726e0d8538d/en-iso-14083-2023
44. **CEN-CENELEC — webinar sobre EN ISO 14083 (2024)**. https://www.cencenelec.eu/media/CEN-CENELEC/Events/Webinars/2024/2024-04-16_webinar_en_iso14083.pdf
45. **EUR-Lex — propuesta original de CountEmissionsEU (2023)**. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:52023PC0441
46. **New Zealand MfE — Measuring Emissions Catalogue 2026, factores de flete (CC BY 4.0)**. https://measuringemissionsguide.environment.govt.nz/8_freight.html
47. **SGS — aprobación como VVB del SFC CAS (may 2024)**. https://www.sgs.com/en-us/news/2024/05/sgs-approved-as-a-verification-body-under-smart-freight-centre-conformity-assessment-scheme
48. **Normec Verifavia — SFC Conformity Assessment**. https://normecverifavia.com/services/sustainability/smart-freight-centre-conformity-assessment-mbm-audit/
49. **SCS Global Services — aprobación como VVB**. https://www.scsglobalservices.com/news/smart-freight-centre-approves-scs-global-services-as-a-verification-body-for-its-conformity
50. **Network for Transport Measures (NTM) — membresía**. https://www.transportmeasures.org/en/membership/
51. **SFC — página de certificación** (JS-only, no legible automáticamente). https://www.smartfreightcentre.org/en/our-programs/emissions-accounting/global-logistics-emissions-council/certification/

### Fuentes consultadas que resultaron inaccesibles

52. `https://ghgptechassistance.zendesk.com/hc/en-us/categories/27448673565716-Calculation-Tools-and-Guidance` — HTTP 403.
53. `https://webstore.ansi.org/standards/iso/iso140832023` — HTTP 403.
54. `https://edg.epa.gov/epa_data_license.html` — conexión rechazada (confirmado vía espejo, fuente 13).
