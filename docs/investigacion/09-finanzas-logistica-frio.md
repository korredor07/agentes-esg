# Activos fijos y tributación en Chile, facturación electrónica, logística y cadena de frío

Fecha de investigación: 2026-09-16

> Documento de insumo para el motor de cálculo en Python de **Agentes ESG**.
> Etiquetas de confianza: **[VERIFICADO]** = leído en fuente oficial primaria (sii.cl, bcn.cl, ine.gob.cl, ispch.gob.cl, minsal.cl, gs1.org, smartfreightcentre.org, usp.org, iso.org) · **[SECUNDARIO]** = fuente profesional/consultora seria, no oficial · **[NO VERIFICADO]** = no se pudo confirmar en esta investigación, **no programar sin verificar**.

---

## Resumen

1. La **tabla de vida útil** del activo inmovilizado sigue siendo la de la **Resolución Exenta SII N° 43 de 26.12.2002**, vigente desde el 01.01.2003. La única modificación posterior confirmada es la **Res. Ex. SII N° 56 de 09.06.2021**, que agrega vehículos eléctricos/híbridos enchufables y cero emisiones con vida útil normal 3 años y acelerada 1 año, para vehículos usados hasta el 14.02.2031 (AT 2022 a 2032). **No hay reemplazo de la tabla en 2024, 2025 ni 2026**.
2. La **depreciación acelerada** del art. 31 N° 5 LIR es `floor(vida_útil_normal / 3)` con mínimo 1 año, solo para bienes **nuevos o importados** con vida útil normal **≥ 3 años**. El art. 31 N° 5 bis permite `floor(vida_útil_normal / 10)` (mínimo 1 año) para contribuyentes con ingresos promedio ≤ 100.000 UF, y **vida útil de 1 año** para los de ≤ 25.000 UF.
3. El régimen **Pro Pyme del art. 14 letra D) N° 3** deprecia **instantánea e íntegramente** el activo fijo en el ejercicio de adquisición o fabricación, con la condición de que el bien **esté pagado** (base caja). Estas empresas **no aplican corrección monetaria**.
4. Los regímenes **transitorios** de depreciación instantánea (Ley 21.210 arts. vigésimo primero y vigésimo segundo transitorios; ampliados por Ley 21.256) **ya no están vigentes** para nuevas adquisiciones: cubrían adquisiciones hasta el 31.12.2021 y 31.12.2022 respectivamente.
5. La **corrección monetaria** del art. 41 LIR usa variación de IPC con **desfase de un mes** (y de dos meses para el arranque del ejercicio). Para el ejercicio 01.01.2025–31.12.2025 el capital propio inicial se reajusta **3,4 %** y los factores mensuales directos van de **1,036** (enero 2025) a **1,000** (diciembre 2025) — Circular SII N° 5 de 21.01.2026. Regla dura: **si el porcentaje es negativo, se iguala a cero**.
6. En logística, **ISO 14083:2023** es la norma internacional de cuantificación de GEI de la cadena de transporte y el **GLEC Framework v3.1 (Smart Freight Centre)** es su implementación práctica; **los factores por defecto de GLEC no son redistribuibles**: para software abierto hay que usar alternativas públicas (DEFRA/BEIS, ADEME Base Empreinte, EPA SmartWay, EcoTransIT World público).
7. En cadena de frío, la **temperatura cinética media (MKT)** es la fórmula de Haynes; el valor por defecto de energía de activación más usado es **83,144 kJ/mol** (equivale a `Ea/R = 10.000 K`), con `R = 8,314462618 J·mol⁻¹·K⁻¹`. En Chile, el **Reglamento Sanitario de los Alimentos (DS 977/1996)** fija los rangos de almacenamiento y el **ISP** regula el almacenamiento y las alertas de medicamentos.

---

## 1. SII — Tabla de vida útil de los bienes físicos del activo inmovilizado

### 1.1 Norma vigente

| Ítem | Dato | Vigencia | Fuente |
|---|---|---|---|
| Norma base | **Resolución Exenta SII N° 43, de 26.12.2002** — "Fija vida útil normal a los bienes físicos del activo inmovilizado para los efectos de su depreciación, conforme a las normas del N° 5 del artículo 31 de la Ley de la Renta" | Desde **01.01.2003**, sin derogación posterior | [1] [VERIFICADO] |
| Instrucciones | Circular SII N° 6, de 14.01.2003 | Vigente | [2] [VERIFICADO] |
| Modificación vigente | **Res. Ex. SII N° 56, de 09.06.2021** — incorpora vehículos eléctricos/híbridos enchufables y cero emisiones | Vehículos utilizados **desde el 13.02.2021 y hasta el 14.02.2031**; códigos en F22 **AT 2022 a 2032** | [3] [VERIFICADO] |
| Ámbito | Bienes adquiridos **nuevos**, construidos o **internados** (nuevos o usados) desde la publicación de la Ley N° 19.840 (23.11.2002). Los bienes adquiridos/construidos antes, o usados adquiridos después, siguen con las tablas anteriores hasta depreciarse totalmente | Vigente | [1] [VERIFICADO] |
| Cambios 2024–2026 | **Ninguno**. La página del SII de la tabla no registra actualizaciones posteriores a junio de 2021 | — | [4] [VERIFICADO] |

> **Nota para el motor de cálculo:** la columna "depreciación acelerada" de la propia tabla del SII ya viene calculada como `floor(vida_útil_normal / 3)` con mínimo 1 año. Se verificó la consistencia en todos los pares leídos (80→26, 50→16, 40→13, 30→10, 20→6, 15→5, 10→3, 9→3, 8→2, 7→2, 6→2, 5→1, 4→1, 3→1, 70→23, 75→25, 45→15, 18→6, 13→4, 12→4, 11→3). **Regla programable: `acelerada = max(1, floor(normal/3))`, aplicable solo si `normal >= 3`.**

### 1.2 Nómina de ACTIVOS GENÉRICOS (Res. Ex. 43/2002)

Todas las cifras en años. [VERIFICADO] contra la página oficial del SII [1].

| N° | Bien | Vida útil normal | Depreciación acelerada |
|---:|---|---:|---:|
| 1 | Construcciones con estructuras de acero, cubierta y entrepisos de perfiles acero o losas hormigón armado | 80 | 26 |
| 2 | Edificios, casas y otras construcciones, con muros de ladrillos o de hormigón, con cadenas, pilares y vigas hormigón armado | 50 | 16 |
| 3 | Edificios fábricas de material sólido albañilería de ladrillo, de concreto armado y estructura metálica | 40 | 13 |
| 4 | Construcciones de adobe o madera en general | 30 | 10 |
| 5 | Galpones de madera o estructura metálica | 20 | 6 |
| 6 | Otras construcciones definitivas (caminos, puentes, túneles, vías férreas) | 20 | 6 |
| 7 | Construcciones provisorias | 10 | 3 |
| 8 | Instalaciones en general (eléctricas, de oficina) | 10 | 3 |
| 9 | Camiones de uso general | 7 | 2 |
| 10 | Camionetas y jeeps | 7 | 2 |
| 11 | Automóviles | 7 | 2 |
| 12 | Microbuses, taxibuses, furgones y similares | 7 | 2 |
| 13 | Motos en general | 7 | 2 |
| 14 | Remolques, semirremolques y carros de arrastre | 7 | 2 |
| 15 | Maquinarias y equipos en general | 15 | 5 |
| 16 | Balanzas, hornos microondas, refrigeradores, conservadoras, vitrinas refrigeradas y cocinas | 9 | 3 |
| 17 | Equipos de aire y cámaras de refrigeración | 10 | 3 |
| 18 | Herramientas pesadas | 8 | 2 |
| 19 | Herramientas livianas | 3 | 1 |
| 20 | Letreros camineros y luminosos | 10 | 3 |
| 21 | Útiles de oficina (máquina de escribir, fotocopiadora) | 3 | 1 |
| 22 | Muebles y enseres | 7 | 2 |
| 23 | Sistemas computacionales, computadores, periféricos y similares (cajeros automáticos, cajas registradoras) | 6 | 2 |
| 24 | Estanques | 10 | 3 |
| 25 | Equipos médicos en general | 8 | 2 |
| 26 | Equipos de vigilancia, detección y control de incendios, alarmas | 7 | 2 |
| 27 | Envases en general | 6 | 2 |
| 28 | Equipo de audio y video | 6 | 2 |
| 29 | Material de audio y video | 5 | 1 |
| + | **Vehículos eléctricos o híbridos con recarga eléctrica exterior** (Res. Ex. 56/2021) | **3** | **1** |
| + | **Otros calificados como cero emisiones por resolución fundada del Ministerio de Energía** (Res. Ex. 56/2021) | **3** | **1** |

> ⚠️ La nómina genérica del SII incluye algunos ítems adicionales de detalle (p. ej. desgloses de maquinaria de construcción pesada) que **no se pudieron leer completos** en esta sesión. Antes de cerrar la tabla en el motor, revisar la página [1] ítem por ítem. Los 29 ítems anteriores sí fueron leídos directamente.

### 1.3 Nóminas por actividad — AGRICULTURA

[VERIFICADO] contra [1], salvo indicación.

| Bien | Normal | Acelerada |
|---|---:|---:|
| Tractores, segadoras, cultivadoras, fumigadoras, motobombas, pulverizadoras | 8 | 2 |
| Cosechadoras, arados, esparcidoras de abono y cal, máquinas de ordeñar | 11 | 3 |
| Esquiladoras mecánicas y maquinarias agrícolas no comprendidas en otros ítems | 11 | 3 |
| Vehículos de carga motorizados (camiones, trailers, acoplados) | 10 | 3 |
| Carretas, carretones, carretelas | 15 | 5 |
| Camiones de carga y camionetas de uso intensivo agrícola | 6 | 2 |
| Tuberías para agua potable en predios agrícolas | 18 | 6 |
| Construcciones de material sólido (silos, casas patronales, lagares) | 50 | 16 |
| Construcciones de adobe, madera o estructuras metálicas | 20 | 6 |
| Animales de trabajo | 8 | 2 |
| Reproductores (toros, carneros, verracos, potros) | 5 | 1 |
| Gallos y pavos reproductores | 3 | 1 |
| Viñedos (según variedad) | 11 a 23 | 3 a 7 |
| Nogales, paltos, ciruelos, manzanos, almendros | 18 | 6 |
| Limoneros | 12 | 4 |
| Duraznos | 10 | 3 |
| Otras plantaciones frutales | 13 | 4 |
| Olivos | 40 | 13 |
| Naranjos | 30 | 10 |
| Perales | 25 | 8 |
| Orégano | 9 | 3 |
| Alfalfa | 4 | 1 |
| Animales de lechería (vacas) | 7 | 2 |
| Gallinas | 3 | 1 |
| Ovejas | 5 | 1 |
| Yeguas | 12 | 4 |
| Porcinos de reproducción (hembras) | 6 | 2 |
| Conejos | 3 | 1 |
| Caprinos | 5 | 1 |
| Asnales | 5 | 1 |
| Postes y alambradas para viñas | 10 | 3 |
| Instalaciones anexas a tranques (bombas, estanques) | 10 | 3 |
| Canales de riego revestidos en concreto | 70 | 23 |
| Canales de riego con fierro pesado | 45 | 15 |
| Canales de riego con madera | 25 | 8 |
| Pozos con cemento u hormigón armado | 20 | 6 |
| Pozos con ladrillo | 15 | 5 |
| Bombas elevadoras de agua | 20 | 6 |
| Puentes de cemento | 75 | 25 |
| Puentes metálicos | 45 | 15 |
| Puentes de madera | 30 | 10 |

### 1.4 Otras nóminas por actividad (lectura parcial)

Valores leídos de la misma página [1]; **cobertura parcial**, marcar como pendiente de completar antes de cargarlos al motor.

| Actividad | Bien | Normal | Acelerada |
|---|---|---:|---:|
| Industria de la construcción | Maquinaria pesada (motoniveladoras, bulldozers, chancadoras) | 8 | 2 |
| Industria de la construcción | Bombas, perforadoras, soldadoras | 6 | 2 |
| Minería (industria extractiva) | Maquinarias pesadas en minas | 9 | 3 |
| Minería | Instalaciones | 5 | 1 |
| Minería | Tranques de relaves | 10 | 3 |
| Transporte marítimo | Naves de carga de acero | 18 | 6 |
| Transporte marítimo | Naves con casco de acero (uso general) | 36 | 12 |
| Transporte marítimo | Remolcadores de acero | 20 | 6 |
| Transporte terrestre | Tolvas y equipos de volteo | 9 | 3 |
| Transporte terrestre | Portacontenedores | 7 | 2 |
| Energía eléctrica | Equipos de generación | 10 | 3 |
| Energía eléctrica | Obras civiles (bocatomas, presas) | 50 | 16 |
| Energía eléctrica | Líneas de distribución | 20 | 6 |
| Telecomunicaciones | Equipos de conmutación | 10 | 3 |
| Telecomunicaciones | Cables aéreos y subterráneos | 20 | 6 |
| Telecomunicaciones | Antenas | 12 | 4 |

> **Importante para cadena de frío:** la Res. 43/2002 **no tiene una nómina específica de industria de alimentos, frigoríficos ni cámaras de frío**. Los activos de frío se clasifican en la nómina genérica: *"Equipos de aire y cámaras de refrigeración"* (10 / 3) y *"Balanzas, hornos microondas, refrigeradores, conservadoras, vitrinas refrigeradas y cocinas"* (9 / 3). [VERIFICADO]

---

## 2. Depreciación tributaria — art. 31 N° 5 y N° 5 bis LIR

### 2.1 Depreciación normal (art. 31 N° 5, inciso primero)

| Elemento | Regla | Etiqueta |
|---|---|---|
| Qué se deduce | "Una cuota anual de depreciación por los bienes físicos del activo inmovilizado a contar de su utilización en la empresa, calculada sobre el valor neto de los bienes a la fecha del balance respectivo" | [VERIFICADO] texto legal [5] |
| Método | Lineal sobre la vida útil fijada por el SII (Res. 43/2002) | [VERIFICADO] |
| Base de cálculo | Valor **actualizado por corrección monetaria** (art. 41 LIR) al cierre del ejercicio, neto de depreciaciones acumuladas | [VERIFICADO] [7] |
| Inicio | Desde la **utilización** del bien en la empresa (no desde la compra) | [VERIFICADO] |
| Proporcionalidad | En el primer ejercicio se computa por los **meses efectivos de uso** (`cuota anual × meses/12`). El SII lo ejemplifica en la Circular N° 31/2020 con "meses utilizados al 31.12" | [VERIFICADO] [8] |
| Terrenos | **No se deprecian** ("no está sujeto a desgaste, agotamiento o destrucción durante su uso, el que por lo demás no puede ser adquirido nuevo") | [VERIFICADO] [8] |
| Intangibles | No son bienes físicos → fuera del art. 31 N° 5 | [VERIFICADO] [8] |
| Activo realizable | Mercaderías, materias primas, productos en proceso: **no se deprecian** | [VERIFICADO] [8] |
| Vida útil especial | El contribuyente puede pedir al Director Regional una vida útil distinta en casos calificados; también existe depreciación por bienes que se han hecho inservibles antes del término de su vida útil (duplicando la cuota) | [SECUNDARIO] — verificar texto exacto |

### 2.2 Depreciación acelerada (art. 31 N° 5, incisos siguientes)

| Elemento | Regla | Etiqueta |
|---|---|---|
| Fórmula | Vida útil = **un tercio** de la fijada por el SII | [VERIFICADO] |
| Redondeo | Se **desprecian los valores decimales** (truncamiento hacia abajo), mínimo 1 año → `max(1, floor(normal/3))` | [VERIFICADO] por consistencia integral de la tabla oficial [1] |
| Requisito 1 | Bienes **nuevos adquiridos o importados**. Los **importados pueden ser usados** (la condición de "nuevo" no se exige a los importados) | [VERIFICADO] [8] |
| Requisito 2 | Vida útil normal **igual o superior a 3 años** | [VERIFICADO] [6] |
| Efecto en art. 14 | Para los registros empresariales / retiros, solo se considera la **depreciación normal**; la diferencia entre acelerada y normal se controla separadamente (genera renta afecta a impuestos finales) | [VERIFICADO] [8] |
| Abandono del régimen | El contribuyente puede volver al régimen normal en cualquier oportunidad, de forma definitiva | [SECUNDARIO] |

### 2.3 Art. 31 N° 5 bis — depreciación para empresas medianas y pequeñas

Introducido por la **Ley N° 20.780 (29.09.2014)**, aplicable a bienes adquiridos desde el **01.10.2014**; texto vigente tras la Ley N° 21.210.

| Tramo de ingresos (promedio anual del giro, 3 ejercicios anteriores al del inicio de utilización del bien) | Vida útil tributaria | Bienes elegibles | Etiqueta |
|---|---|---|---|
| **≤ 25.000 UF** | **1 año** (depreciación instantánea de hecho) | Bienes **nuevos o usados** | [VERIFICADO] [5][6] |
| **> 25.000 UF y ≤ 100.000 UF** | **1/10 de la vida útil normal**, despreciando decimales, **mínimo 1 año** → `max(1, floor(normal/10))` | Bienes **nuevos o importados** | [VERIFICADO] [5][6] |

- Si la empresa tiene **menos de 3 ejercicios** de existencia, el promedio se calcula sobre los ejercicios de existencia efectiva. [VERIFICADO]
- El régimen es **opcional**: el contribuyente elige entre N° 5 (normal/acelerada) y N° 5 bis. [VERIFICADO]

**Ejemplos de `floor(normal/10)`:** maquinaria general 15 → 1; galpón 20 → 2; edificio de hormigón 50 → 5; construcción de acero 80 → 8; computadores 6 → 1; camión 7 → 1.

### 2.4 Régimen Pro Pyme — depreciación instantánea e íntegra (art. 14 letra D) N° 3 LIR)

Texto literal de la Circular SII N° 62 de 2020 [9] [VERIFICADO]:

> "La Pyme depreciará sus activos físicos del activo inmovilizado de manera instantánea e íntegra en el mismo ejercicio comercial en que sean adquiridos o fabricados."
>
> "Para efectos de lo anterior, los activos físicos del activo inmovilizado deben encontrarse pagados, por cuanto, en el régimen Pro Pyme la determinación de la base imponible se basa en flujos de caja, de acuerdo a la letra (f) del N° 3 y el N° (iv) de la letra (a) del N° 8, ambos de la letra D) del artículo 14."

| Elemento | Regla | Etiqueta |
|---|---|---|
| Porcentaje | **100 % en el ejercicio de adquisición o fabricación** | [VERIFICADO] |
| Condición | El bien debe estar **efectivamente pagado** (régimen de base caja) | [VERIFICADO] |
| Exclusiones | Bienes que no pueden depreciarse conforme a la LIR (p. ej. **terrenos y activos intangibles**); su desembolso no es egreso del ejercicio, sino rebaja del ingreso neto al enajenarlos | [VERIFICADO] [9] |
| Interacción con art. 33 bis | Si procede el crédito por activo fijo del art. 33 bis, el monto imputado contra el IDPC constituye **menor gasto** para la base imponible | [VERIFICADO] [9] |
| Corrección monetaria | Los contribuyentes del art. 14 D) N° 3 **no están sujetos al sistema de corrección monetaria** ni reajustan sus registros de rentas empresariales | [VERIFICADO] Circular 5/2026 [7] |
| Tope en UF | **No existe** tope en UF para la depreciación instantánea Pro Pyme. Se descartó una afirmación secundaria que mencionaba un tope de 25.000 UF: no aparece en la Circular 62/2020 | [VERIFICADO] (descarte) |

### 2.5 Regímenes transitorios de depreciación instantánea — estado al 16.09.2026

| Norma | Bienes | Ventana de adquisición | Beneficio | ¿Vigente hoy? |
|---|---|---|---|---|
| **Art. vigésimo primero transitorio, Ley N° 21.210** (24.02.2020) | Físicos del activo inmovilizado, depreciables, **nuevos o importados** (los importados pueden ser usados), destinados a nuevos proyectos de inversión | **01.10.2019 a 31.12.2021**, ambas inclusive | **50 %** instantáneo e inmediato del valor de adquisición (art. 41 LIR) + **depreciación acelerada** (N° 5 o 5 bis) sobre el 50 % restante | **No**, ventana cerrada [VERIFICADO] [8] |
| **Art. vigésimo segundo transitorio, Ley N° 21.210** | Igual, pero instalados físicamente y usados en producción **exclusivamente en la Región de La Araucanía**, con permanencia mínima de **3 años** | 01.10.2019 a 31.12.2021 | **100 %** instantáneo e íntegro; se pierde retroactivamente si se incumple el plazo de 3 años | **No** [VERIFICADO] [8] |
| **Ley N° 21.256** (02.09.2020) | Activo inmovilizado nuevo o importado, todo el país | **01.06.2020 a 31.12.2022** | **100 %** instantáneo e íntegro, bien valorizado en **$1** | **No** [SECUNDARIO] [10] |
| **Ley N° 21.256** — intangibles | Derechos de propiedad industrial (Ley 19.039), propiedad intelectual (Ley 17.336) y nueva variedad vegetal (Ley 19.342) | 01.06.2020 a 31.12.2022 | Amortización **instantánea e íntegra**, valorizados en **1 peso** | **No** [VERIFICADO] (nota 31 de la Circular 62/2020) [9] |

> **Conclusión operativa:** al 16.09.2026 **no hay régimen transitorio de depreciación instantánea abierto** para nuevas adquisiciones. Los únicos regímenes acelerados permanentes son art. 31 N° 5 (1/3), art. 31 N° 5 bis (1 año o 1/10) y art. 14 D) N° 3 Pro Pyme (100 %). Ver también §8 sobre el proyecto de 2026.

### 2.6 Valor residual

| Regla | Detalle | Etiqueta |
|---|---|---|
| Valor residual tributario | El bien totalmente depreciado se mantiene en **$1** hasta su enajenación o baja. Es práctica establecida y la Ley 21.256 la explicitó ("los que quedarán valorados en 1 peso") | [VERIFICADO] para el caso de Ley 21.256 [9]; [SECUNDARIO] como regla general |
| Consecuencia | La depreciación del último año = `valor neto actualizado − 1` | [SECUNDARIO] |
| Contable (IFRS/NIC 16) | Se usa **valor residual estimado** distinto de $1 y **vida útil económica** propia de la empresa, revisados al menos anualmente | [SECUNDARIO] |

### 2.7 Diferencias tributaria vs. contable (resumen)

| Aspecto | Tributario (LIR) | Contable (NIC 16 / IFRS) |
|---|---|---|
| Vida útil | Tabla del SII (Res. 43/2002), rígida | Estimación propia de la entidad, revisable |
| Método | Lineal (normal o acelerada) | Lineal, decreciente o unidades de producción |
| Valor residual | $1 (tributario) | Valor residual estimado, revisable |
| Corrección monetaria | Obligatoria (art. 41), salvo Pro Pyme | No se aplica (moneda funcional, sin ajuste por inflación en Chile) |
| Componentes | Bien como unidad | **Componentización** obligatoria si partes significativas tienen vidas distintas |
| Deterioro | No existe el concepto | Test de deterioro (NIC 36) |
| Efecto | Estas diferencias generan **diferencias temporarias** → impuestos diferidos (NIC 12) | |

[SECUNDARIO] — resumen conceptual, no citar como norma.

---

## 3. Corrección monetaria (art. 41 LIR)

### 3.1 Quiénes la aplican

| Sujeto | ¿Aplica corrección monetaria? | Etiqueta |
|---|---|---|
| Contribuyentes de Primera Categoría que declaran **renta efectiva según contabilidad completa** (régimen general art. 14 A) | **Sí**, obligatorio | [VERIFICADO] [5][7] |
| **Pro Pyme general art. 14 D) N° 3** | **No**. "Los contribuyentes acogidos al régimen del artículo 14, letra D), N° 3, de la LIR, no deben reajustar sus registros tributarios de rentas empresariales, por cuanto no se encuentran sujetos al sistema de corrección monetaria" | [VERIFICADO] Circular 5/2026 [7] |
| **Pro Pyme transparente art. 14 D) N° 8** | No (base caja, sin CPT corregido) | [SECUNDARIO] |
| Renta presunta | No | [SECUNDARIO] |

### 3.2 Método y desfase del IPC

| Partida | Período de variación del IPC | Etiqueta |
|---|---|---|
| **Capital propio tributario inicial** | Desde el **último día del segundo mes anterior al de iniciación del ejercicio** hasta el **último día del mes anterior al del balance**. Para un ejercicio calendario: **30.11 del año anterior → 30.11 del año del balance** | [VERIFICADO] [5] |
| **Bienes físicos del activo inmovilizado existentes al inicio** (art. 41 N° 2) | Mismo porcentaje que el capital propio inicial | [VERIFICADO] [5] |
| **Bienes adquiridos durante el ejercicio** | Desde el **último día del mes anterior al de adquisición** hasta el **último día del mes anterior al del balance** | [VERIFICADO] [5] |
| **Regla de piso** | "Cuando el porcentaje de reajuste da como resultado un valor negativo, dicho valor no debe considerarse, igualándose a cero (0)", tanto para ejercicios cerrados al 31 de diciembre como para términos de giro y demás situaciones de reajustabilidad | [VERIFICADO] Circular 5/2026 [7] |
| Orden de cálculo | Primero se **actualiza** el valor neto del bien, y **sobre ese valor actualizado** se calcula la cuota de depreciación del ejercicio | [VERIFICADO] (ejemplos de la Circular 31/2020) [8] |

### 3.3 Factores oficiales publicados por el SII — AT 2026 (ejercicio 2025)

Fuente: **Circular SII N° 5, de 21.01.2026** (Ref. legal: arts. 41, 52 y 52 bis LIR) [7] [VERIFICADO].

**Reajuste del capital propio inicial, ejercicio 01.01.2025 – 31.12.2025: 3,4 %.**

**Porcentajes y factores de actualización directos (para actualizar al 31.12.2025):**

| Mes en que ocurrió el hecho | Porcentaje de reajuste | Factor de actualización directo |
|---|---:|---:|
| Enero 2025 | 3,6 % | **1,036** |
| Febrero 2025 | 2,6 % | **1,026** |
| Marzo 2025 | 2,2 % | **1,022** |
| Abril 2025 | 1,6 % | **1,016** |
| Mayo 2025 | 1,4 % | **1,014** |
| Junio 2025 | 1,2 % | **1,012** |
| Julio 2025 | 1,7 % | **1,017** |
| Agosto 2025 | 0,8 % | **1,008** |
| Septiembre 2025 | 0,7 % | **1,007** |
| Octubre 2025 | 0,3 % | **1,003** |
| Noviembre 2025 | 0,3 % | **1,003** |
| Diciembre 2025 | 0,0 % | **1,000** |

Otros datos de la misma circular, útiles para el motor [VERIFICADO]:

- Saldos de registros de rentas empresariales, registro FUR y excesos de retiros al 31.12.2024: reajuste **3,4 %** en el año comercial 2025.
- Costo de reposición de mercaderías nacionales al 31.12.2025: si solo hubo adquisiciones en el **primer semestre** de 2025, se reajusta **1,2 %**; si **no hubo adquisiciones** en 2025, valor de libros del ejercicio anterior reajustado **3,4 %**.
- Dólar EE.UU. al 31.12.2025: **$907,13** (variación anual **−8,96 %**; segundo semestre **−2,82 %**). Euro: **$1.066,58**. UTA a diciembre 2025: **$834.504**.

### 3.4 Porcentajes mensuales 2026 (término de giro y reajustabilidad intra-anual)

Tabla "Porcentajes de Actualización Corrección Monetaria (Término de Giro), Año 2026" del SII [11] [VERIFICADO]:

| Mes 2026 | Porcentaje |
|---|---:|
| Enero | 0,4 % |
| Febrero | 0,0 % |
| Marzo | 1,0 % |
| Abril | 1,3 % |
| Mayo | 0,2 % |
| Junio | 0,0 % |
| Julio | 0,1 % |
| Agosto | 0,6 % |
| Septiembre a diciembre | aún no publicados al 16.09.2026 |

> El SII publica estas tablas mes a mes; el motor debe **leerlas dinámicamente** o versionarlas por año tributario, no fijarlas en código.

---

## 4. Documentos tributarios electrónicos (DTE) y Registro de Compras y Ventas

### 4.1 Especificación vigente

| Dato | Valor |
|---|---|
| Documento | "Formato Documentos Tributarios Electrónicos" |
| Versión vigente | **2.5**, fecha **2026-02** (bitácora de cambios del **16/02/2026**) |
| URL | https://www.sii.cl/factura_electronica/factura_mercado/formato_dte_202602.pdf |
| Etiqueta | [VERIFICADO] [12] |

**Cambios del 16.02.2026 relevantes para logística** [VERIFICADO] [12]:
1. En "Indicador Tipo de traslado de bienes", el tipo N° 7 cambia de nombre: de *"Guía de devolución"* a *"Devolución de Mercaderías"*.
2. En la subsección **Transporte** se agregan los campos **Patente de Carro o remolque, Fecha de Salida, Hora de Salida y Fecha de Llegada**, según **Resolución Ex. N° 154 de 2025**. → *Esto abre la puerta a calcular alcance 3 de transporte propio directamente desde la guía de despacho electrónica.*
3. Se modifica la condición de uso de los campos de la guía de despacho: Patente, RUT transportista, RUT chofer, Nombre chofer, dirección destino.
4. En "Unidad de Medida" se elimina la condicionalidad para Indicador de tipo de Traslado = 8 y 9.
5. En "Datos de manejo de la madera" se agregan Georreferenciación de Destino, Rol Predio destino y Aviso Ejecución.

### 4.2 Tipos de DTE y códigos (campo `<TipoDTE>`)

Tabla del campo N° 2 "Tipo Documento Tributario Electrónico" del formato v2.5 [VERIFICADO] [12]:

| Código | Documento |
|---:|---|
| **33** | Factura Electrónica |
| **34** | Factura No Afecta o Exenta Electrónica |
| **43** | Liquidación-Factura Electrónica |
| **46** | Factura de Compra Electrónica |
| **52** | Guía de Despacho Electrónica |
| **56** | Nota de Débito Electrónica |
| **61** | Nota de Crédito Electrónica |
| **110** | Factura de Exportación |
| **111** | Nota de Débito de Exportación |
| **112** | Nota de Crédito de Exportación |

Códigos adicionales usados en el campo `<TpoDocRef>` (información de referencia) y en los libros [VERIFICADO] [12]:

| Código | Documento |
|---:|---|
| 30 | Factura (papel) |
| 32 | Factura de venta de bienes y servicios no afectos o exentos de IVA |
| 39 | Boleta Electrónica |
| 41 | Boleta No Afecta o Exenta Electrónica |
| 45 | Factura de Compra (papel) |
| 48 | Comprobante de pago electrónico |
| 50 | Guía de Despacho (papel) |
| 55 | Nota de Débito (papel) |
| 60 | Nota de Crédito (papel) |
| 801 / 802 / 803… | Documentos no tributarios (orden de compra, nota de pedido, etc.) — verificar nómina vigente |

> Las **boletas electrónicas (39 y 41)** se rigen por un **documento de formato distinto** ("Formato Boletas Electrónicas"), no por el formato DTE v2.5. [VERIFICADO] (por ausencia en la tabla del campo 2)

### 4.3 Campos clave del XML para extracción automática

Tags confirmados en el esquema del formato v2.5 [VERIFICADO] [12]:

| Zona | Tag XML | Contenido | Uso en ESG |
|---|---|---|---|
| Encabezado / IdDoc | `<TipoDTE>` | Código del documento | Clasificar compra/venta |
| | `<Folio>` | Folio autorizado por el SII (máx. 10 dígitos, NUM) | Clave primaria junto con RUT y tipo |
| | `<FchEmis>` | Fecha de emisión contable, formato **AAAA-MM-DD**, válida entre **2003-04-01 y 2050-12-31** | Período de reporte |
| | `<FchVenc>` | Fecha de vencimiento | — |
| | `<TipoDespacho>` | 1 = despacho por cuenta del receptor; 2 = por cuenta del emisor a instalaciones del cliente; 3 = por cuenta del emisor a otras instalaciones (p. ej. entrega en obra) | **Determina si el transporte es alcance 1 (flota propia) o alcance 3 (categoría 4/9)** |
| | `<IndNoRebaja>` | 1 = Nota de crédito sin derecho a descontar débito (art. 70 DL 825) | Limpieza de duplicados |
| Emisor | `<RUTEmisor>`, `<RznSoc>`, `<GiroEmis>`, `<Acteco>`, `<CdgSIISucur>` | RUT, razón social, giro, **código de actividad económica** y código de sucursal SII | `<Acteco>` es **la llave para mapear gasto → factor de emisión por sector (EEIO)** |
| Receptor | `<RUTRecep>`, `<RznSocRecep>` | RUT y razón social del receptor | Identificación de contraparte |
| Totales | `<MntNeto>`, `<MntExe>`, `<TasaIVA>`, `<IVA>`, `<MntTotal>`, `<MntBruto>`, `<ImptoReten>` | Neto, exento, tasa e importe de IVA, total, indicador de documento bruto, impuestos retenidos | Base monetaria del alcance 3 por gasto (usar **neto**, no total) |
| Detalle | `<NmbItem>`, `<CdgItem>` (`<TpoCodigo>`, `<VlrCodigo>`), `<QtyItem>`, `<UnmdItem>`, `<PrcItem>`, `<MontoItem>`, `<CodImpAdic>` | Nombre, código (permite **GTIN/EAN vía `TpoCodigo`**), cantidad (enteros con hasta 6 decimales), unidad de medida, precio unitario, monto y código de impuesto adicional | **Ruta preferida**: cantidad física × factor de emisión, mucho mejor que gasto × factor |
| Referencias | `<TpoDocRef>`, `<FolioRef>` | Documento referenciado | Enlazar guía de despacho ↔ factura |
| Transporte (guía 52) | Patente, RUT transportista, RUT chofer, nombre chofer, dirección destino, **Patente de Carro/remolque, Fecha y Hora de Salida, Fecha de Llegada** (Res. Ex. 154/2025) | Datos del viaje | **Insumo directo para tonelada-kilómetro** |
| Timbre | `<TED>` | Timbre electrónico SII | Validación |

> **Regla de oro para el motor:** priorizar `QtyItem × UnmdItem` (dato físico) sobre `MntNeto` (dato monetario). El gasto solo como *fallback*.

### 4.4 Registro de Compras y Ventas (RCV) — estructura oficial exportable

Fuentes oficiales del SII: *"Instrucciones de llenado de Información de Compras para Informar en el Registro de Compras"* y su equivalente de Ventas [13][14] [VERIFICADO].

**Reglas generales del archivo** [VERIFICADO] [13]:
- Formato **.csv separado por punto y coma (`;`)**; se acepta comprimido `.Gz`.
- Primera línea con encabezados de columna.
- Montos **sin comas ni separadores de miles, máximo 15 dígitos**; si se requieren decimales, el separador decimal es el **punto**.
- RUT: **solo cuerpo con guion y DV, sin puntos ni espacios**; DV "K" en **mayúscula**.
- Razón social: alfanumérico latino, **solo se consideran los primeros 40 caracteres**.
- El importador de libros acepta hasta **20.000 registros por archivo** (dividir en tramos si hay más) [VERIFICADO] [15].
- `(*)` = campo obligatorio.

#### Registro de COMPRAS — 28 campos

| N° | Nombre del campo | Nombre en el archivo | Obl. |
|---:|---|---|:--:|
| 1 | Tipo de Documento | `Tipo Doc` | * |
| 2 | Folio del Documento | `Folio` | * |
| 3 | RUT de la Contraparte | `Rut Contraparte` | * |
| 4 | Tasa de Impuesto | `Tasa Impuesto` | |
| 5 | Nombre o Razón Social | `Razón Social Contraparte` | * |
| 6 | Tipo de Impuesto (1=IVA, 2=Ley 18.211) | `Tipo Impuesto` | * |
| 7 | Fecha de emisión del Documento | `Fecha Emisión` | * |
| 8 | Monto Exento o No Gravado | `Monto Exento` | |
| 9 | Monto Neto | `Monto Neto` | |
| 10 | Monto IVA Recuperable | `Monto IVA (Recuperable)` | |
| 11 | Código IVA No Recuperable | `Cod IVA no Rec` | |
| 12 | Monto IVA No Recuperable | `Monto IVA no Rec` | |
| 13 | Monto IVA Uso Común | `IVA Uso Comun` | |
| 14 | Código Otro Impuesto o Retención | `Cod Otro Imp (Con Credito)` | |
| 15 | Tasa Otro Impuesto o Retención | `Tasa Otro Imp (Con Credito)` | |
| 16 | Monto Otro Impuesto o Retención (con crédito) | `Monto Otro Imp (Con Credito)` | |
| 17 | Monto Otro Impuesto (sin crédito) | `Monto Otro Imp Sin Credito` | |
| 18 | **Monto Neto Activo Fijo** | `Monto Activo Fijo` | |
| 19 | **Monto IVA Activo Fijo** | `Monto IVA Activo Fijo` | |
| 20 | Monto IVA No Retenido | `IVA no Retenido` | |
| 21 | Impuesto Cigarros Puros | `Tabacos – Puros` | |
| 22 | Impuesto Cigarrillos | `Tabacos – Cigarrillos` | |
| 23 | Impuesto Tabaco Elaborado | `Tabacos – Elaborados` | |
| 24 | Código de Sucursal SII | `Código sucursal SII` | |
| 25 | Número Interno (comprobante contable) | `Numero Interno` | |
| 26 | Notas de Débito/Crédito por Facturas de Compra | `Emisor/Receptor` | |
| 27 | Monto Total | `Monto Total` | * |
| 28 | **Tipo de Transacción de Compra** | `Tipo Transaccion` | |

**Códigos del campo 28 — Tipo de Transacción de Compra** [VERIFICADO] [13]:

| Valor | Código |
|---|---:|
| Compras del Giro | 1 |
| Compras en Supermercados o comercios similares | 2 |
| Adquisición de bienes raíces | 3 |
| **Compra de Activo Fijo** | **4** |
| Compras con IVA Uso Común | 5 |
| Compras sin Derecho a Crédito | 6 |

> **Uso doble para Agentes ESG:** el código **4** (y los campos 18-19 *Monto Activo Fijo* / *Monto IVA Activo Fijo*) permiten **detectar automáticamente las altas de activo fijo del ejercicio** y alimentar el módulo de depreciación. El código **1** (compras del giro) es la base natural del **alcance 3 por gasto**, y el **2** (supermercados) suele aislar gasto no productivo.

**Códigos del campo 11 — IVA No Recuperable** [VERIFICADO] [13]: 1 = compras destinadas a operaciones exentas o no gravadas; 2 = facturas de proveedores registradas fuera de plazo; 3 = gastos no necesarios para producir la renta; 4 = entregas gratuitas recibidas; 9 = otros.

**Códigos de documentos de compras** (campo 1) [VERIFICADO] [13]: 29 Factura de Inicio · 30 Factura · 32 Factura de Ventas y Servicios No Afectos o Exentos de IVA · 33 Factura Electrónica · 34 Factura No Afecta o Exenta Electrónica · 40 Liquidación Factura · 43 Liquidación Factura Electrónica · 45 Factura de Compra · 46 Factura de Compra Electrónica · 55 Nota de Débito · 56 Nota de Débito Electrónica · 60 Nota de Crédito · 61 Nota de Crédito Electrónica · 108 SRF Solicitud de Registro de Factura · 901 Factura de ventas a empresas del territorio preferencial · 904 Factura de Traspaso · 909 Facturas Venta Módulo ZF · 910 Solicitud Traslado Zona Franca (Z) · 911 Declaración de Ingreso a Zona Franca Primaria · 914 Declaración de Ingreso (DIN).

> El código **914 (DIN, Declaración de Ingreso)** identifica **importaciones**: es la puerta de entrada para el alcance 3 de bienes importados y para el transporte internacional.

#### Registro de VENTAS — 40 campos

| N° | Nombre del campo | Nombre en el archivo | Obl. |
|---:|---|---|:--:|
| 1 | Tipo de Documento | `Tipo Doc` | * |
| 2 | Folio del Documento | `Folio` | * |
| 3 | RUT del Cliente | `Rut Contraparte` | * |
| 4 | Tasa de Impuesto | `Tasa Impuesto` | * |
| 5 | Nombre o Razón Social | `Razón Social Contraparte` | * |
| 6 | Fecha Emisión del Documento | `Fecha Emisión` | * |
| 7 | Monto Exento o No Gravado | `Monto Exento` | |
| 8 | Monto Neto | `Monto Neto` | * |
| 9 | Monto IVA | `Monto IVA` | * |
| 10 | Monto IVA Fuera de Plazo | `IVA Fuera Plazo (Nota de Crédito)` | |
| 11 | Código Otro Impuesto o Retención | `Cod Otro Imp` | |
| 12 | Tasa Otro Impuesto o Retención | `Tasa Otro Imp` | |
| 13 | Monto Otro Impuesto o Retenciones | `Monto Otro Imp` | |
| 14 | Monto IVA Propio | `Monto IVA Propio` | |
| 15 | Monto IVA Terceros | `Monto IVA Terceros` | |
| 16 | Monto IVA Retenido Total | `IVA Retenido Total` | |
| 17 | Monto IVA Retenido Parcial | `IVA Retenido Parcial` | |
| 18 | Monto IVA No Retenido | `IVA No Retenido` | |
| 19 | Impuesto Zona Franca Ley 18.211 | `Ley 18211` | |
| 20 | Monto Crédito Especial Empresas Constructoras | *(ver fuente)* | |
| 21 | Tipo Documento Referencia | `Tipo Doc Referencia` | |
| 22 | Folio Documento Referencia | `Folio Documento Referencia` | |
| 23 | Monto Depósito por Envases | `Deposito por Envase` | |
| 24 | Monto No Facturable | `Monto No Facturable` | |
| 25 | Monto Período | `Monto Periodo` | |
| 26 | Monto Venta Pasaje Nacional | `Venta Pasaje Nacional` | |
| 27 | Monto Venta Pasaje Internacional | `Venta Pasaje Internacional` | |
| 28 | Número Identificación Receptor Extranjero | *(ver fuente)* | |
| 29 | Nacionalidad | `Nacionalidad` | |
| 30 | Indicador de Facturación / Servicio periódico | *(ver fuente)* | |
| 31 | Indicador Venta sin Costo | `Indicador sin Costo` | |
| 32 | RUT Liquidador emisor de Liquidación-Factura | *(ver fuente)* | |
| 33 | Monto Valor Neto Comisiones | `Valor Neto Comisiones` | |
| 34 | Monto Valor Comisiones Exentas | `Valor Comisiones Exentas` | |
| 35 | Monto Valor IVA Comisiones | `Valor IVA Comisiones` | |
| 36 | Código Sucursal SII | `Codigo sucursal SII` | |
| 37 | Número Interno | `Numero Interno` | |
| 38 | Notas de Débito/Crédito por Facturas de Compra | *(ver fuente)* | |
| 39 | Monto Total | `Monto Total` | * |
| 40 | **Tipo de Transacción de Venta** | `Tipo Transacción` | |

**Códigos del campo 40 — Tipo de Transacción de Venta** [VERIFICADO] [14]: 1 = Ventas del Giro · 2 = **Venta de Activo Fijo** · 3 = Venta de Bienes Raíces · 4 = Emisión de Nota de Crédito por Vale de Máquina Registradora.

> Los campos 20, 28, 30, 32 y 38 de ventas no se pudieron leer completos por problemas de extracción del PDF; **verificar sus nombres exactos en [14] antes de codificar el parser**. [NO VERIFICADO]

### 4.5 Recomendaciones de implementación

1. **Descarga**: el RCV se descarga desde el portal del SII con "Descargar Detalles" / "Exportar CSV"; se generan archivos separados para compras y ventas (registro y resumen). [SECUNDARIO]
2. **Encoding**: los CSV del SII vienen históricamente en **Latin-1 / Windows-1252**, no UTF-8. Probar `cp1252` con *fallback* a `utf-8-sig`. [NO VERIFICADO] — confirmar con un archivo real.
3. **Alcance 3 por gasto**: agrupar por `Rut Contraparte` → enriquecer con `<Acteco>` del emisor (desde el XML del DTE, no está en el RCV) → mapear a un factor EEIO. El RCV **no trae el código de actividad económica**, solo el RUT, así que el cruce exige consultar el DTE o un padrón de contribuyentes.
4. **Evitar doble conteo**: restar notas de crédito (56/61 en ventas; 60/61 en compras) y excluir `Tipo Transaccion = 3` (bienes raíces) y `= 4` (activo fijo) del gasto operacional — el activo fijo va a **categoría 2 (bienes de capital)** del alcance 3, no a la categoría 1.

---
