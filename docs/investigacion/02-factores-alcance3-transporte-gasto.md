# Factores y métodos para Alcance 3: transporte de carga y cálculo por gasto

Fecha de investigación: 2026-09-15

> **Estado del documento:** PARCIAL — en construcción. Secciones completadas: 1 (UK DESNZ/DEFRA), 2 (US EPA Supply Chain Factors).

## Resumen

(Se completará al final.)

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
