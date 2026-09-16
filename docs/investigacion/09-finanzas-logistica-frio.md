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

## 5. Logística — ISO 14083:2023 y GLEC Framework

> **Aviso de alcance:** el documento hermano `02-factores-alcance3-transporte-gasto.md` (§4) ya contiene la investigación detallada y verificada del GLEC Framework v3.2 y de ISO 14083:2023, leída del PDF oficial. Esta sección **no la repite**: aporta el resumen operativo para el motor, el contraste con una fuente independiente y un **ejemplo multimodal resuelto**. Para factores, licencias y tablas, ir a `02-…`.

### 5.1 Normas vigentes al 16.09.2026

| Documento | Versión vigente | Fecha | Etiqueta |
|---|---|---|---|
| **ISO 14083** — *Greenhouse gases — Quantification and reporting of greenhouse gas emissions arising from transport chain operations* | **ISO 14083:2023**, edición 1 (Stage 60.60) | Marzo 2023 | [VERIFICADO] vía doc 02 |
| Versión europea | **EN ISO 14083:2023** (adopciones nacionales UNE-EN, DIN EN, BS EN…) | 2023 | [SECUNDARIO] |
| ¿Enmienda o revisión 2024–2026? | **No se encontró evidencia** de enmienda publicada ni de una ISO 14083-2 | — | [NO VERIFICADO] — `iso.org` devuelve HTTP 403 a peticiones automatizadas; comprobar manualmente |
| **GLEC Framework** (Smart Freight Centre) | **v3.2** | **21 de octubre de 2025** | [VERIFICADO] vía doc 02 |
| Novedad principal de la v3.2 | Nuevo módulo anexo de **contaminantes atmosféricos** (NOx, SOx, PM10, PM2.5, black carbon) + actualización de factores de combustible | Oct 2025 | [SECUNDARIO] [16] |
| Próxima revisión GLEC | Esperada **2026–2028**, alineada con el ciclo de revisión de ISO 14083 (GWP AR6, perfiles operativos post-pandemia, combustibles bajos en carbono) | — | [NO VERIFICADO] |
| **CountEmissions EU** | Reglamento UE de método único de cálculo de emisiones de transporte de pasajeros y carga, basado en EN ISO 14083; acuerdo Consejo–Parlamento en **noviembre de 2025** | 2025 | [SECUNDARIO] — verificar número y fecha de publicación en el DOUE |

### 5.2 Vocabulario ISO 14083 (redacción propia)

Confirmado de forma independiente en la guía CLECAT sobre ISO 14083 [17] [SECUNDARIO], coherente con doc 02:

| Sigla | Qué es | Símbolo de fórmula |
|---|---|---|
| **TC** — Transport Chain | La cadena completa, de expedidor a destinatario | — |
| **TCE** — Transport Chain Element | Cada tramo de la cadena: la carga movida por **un solo vehículo**, o una operación de **hub** (distancia cero). Cada cambio de vehículo o paso por hub obliga a abrir un TCE nuevo | — |
| **TO** — Transport Operation | El uso concreto de un vehículo para llevar carga o pasajeros | — |
| **TOC** — Transport Operation Category | Agrupación de operaciones de transporte con características similares en un período (típicamente un año). Es el nivel al que se calcula la **intensidad**. Reemplaza el término "leg" de EN 16258 | — |
| **HO / HOC** — Hub Operation (Category) | Transferencia de carga o pasajeros en un nodo, y su agrupación por características | — |
| **Transport activity** | Actividad de transporte: masa × distancia, en **t·km** (o pax·km) | `T` |
| **Hub activity** | Rendimiento (throughput) del hub, en **toneladas** o pax, medido sobre lo que **sale** del hub | `H` |
| **Operation GHG emissions** | Emisiones por operar vehículos o hubs. **Reemplaza "Tank-to-Wheel (TTW)"** de EN 16258 | — |
| **Energy provision GHG emissions** | Emisiones de producir, almacenar, procesar y distribuir el vector energético (incluida la electricidad). **Reemplaza "Well-to-Tank (WTT)"** | — |
| **Total GHG emissions** | La suma de ambas. **Reemplaza "Well-to-Wheel (WTW)"** | `G` |
| **GHG emission intensity** | Emisiones por unidad de actividad (g CO2e/t·km o g CO2e/t) | `g` |
| **SFD** — Shortest Feasible Distance | Ruta practicable más corta según las opciones de infraestructura para ese tipo de vehículo | — |
| **GCD** — Great Circle Distance | Distancia geodésica entre dos puntos sobre la superficie terrestre | — |
| **DAF** — Distance Adjustment Factor | Corrección para homogeneizar el tipo de distancia del TCE con el usado para la intensidad del TOC | — |

> **Punto fino terminológico:** ISO 14083 abandonó formalmente WTT/TTW/WTW en favor de *energy provision / operation / total GHG emissions*, pero la industria (y el propio GLEC) sigue usando las siglas antiguas. El motor debería aceptar ambos vocabularios y **reportar con los términos ISO**.

### 5.3 Ecuaciones operativas

```
# 1. Actividad
T_TCE  = masa_carga_toneladas × distancia_actividad_km        # t·km
H_TCE  = toneladas de throughput saliente del hub             # t

# 2. Intensidad del TOC (se calcula "hacia atrás", desde el consumo real)
G_TOC  = Σ (energía_consumida_i × (EF_operacion_i + EF_provision_i))
g_TOC  = G_TOC / T_TOC                                        # g CO2e/t·km

# 3. Emisión del TCE
G_TCE(transporte) = T_TCE × g_TOC × DAF
G_TCE(hub)        = H_TCE × g_HOC

# 4. Emisión de la cadena
G_TC = Σ G_TCE          # transporte + hubs

# 5. Intensidad de la cadena
g_TC = G_TC / T_TC
```

- El **DAF entra solo** cuando el tipo de distancia del TCE difiere del usado para calcular `g_TOC`; si ambos usan SFD, `DAF = 1`. [VERIFICADO]
- El *empty running* y los trayectos en vacío **ya están dentro del TOC**: la intensidad se calcula sobre la energía total del período (cargado + vacío) dividida por la actividad **cargada**. Si el dato de combustible cubre solo los trayectos cargados, hay que **añadir** la porción correspondiente a los vacíos. [VERIFICADO vía doc 02]
- **Asignación**: se evita siempre que se pueda desagregando más los datos; cuando es inevitable, la base de reparto es la **cuota de t·km directas** de cada envío sobre el total del TCE. [VERIFICADO vía doc 02]

### 5.4 Distancias y factores de ajuste

Tabla 3 de la guía CLECAT, que cita expresamente a ISO 14083 como fuente [17] [SECUNDARIO]:

| Modo | Tipo de distancia a usar | DAF | Equivalencia partiendo de distancia real |
|---|---|---:|---|
| **Aéreo** | **GCD** (obligatorio) | — | **GCD + 95 km** |
| **Carretera** | SFD | **1,05** | SFD + 5 % |
| **Marítimo** | SFD | **1,15** | SFD + 15 % |
| Ferrocarril, vías navegables interiores, tuberías, teleféricos | SFD | **No se requiere** | La red física fija la ruta; se asume distancia real ≈ SFD |

> **Coincide exactamente** con lo leído del GLEC v3.2 en doc 02 (+5 % carretera, +15 % marítimo, +95 km aéreo). Dos fuentes independientes → fiabilidad alta.

Reglas adicionales confirmadas [17] [SECUNDARIO]:
- **No se pueden mezclar** GCD y SFD dentro de una misma cadena; hay que declarar cuál se usó.
- El aéreo **siempre** usa GCD, y **cada escala es un TCE distinto**.
- En **rondas de recogida y entrega** se usa igualmente GCD o SFD entre cada punto de carga y descarga: es una distancia ficticia cuyo único propósito es **repartir** las emisiones reales de la ronda entre los envíos, vía t·km.
- La **distancia de la intensidad** y la **distancia de la actividad** deben ser siempre del mismo tipo, o el resultado está sesgado.

### 5.5 Masa, factor de carga y viajes vacíos

| Parámetro | Regla | Etiqueta |
|---|---|---|
| Masa del envío | Masa real de la mercancía **incluido el embalaje original del expedidor**, **excluido** el embalaje de transporte del transportista (palés, contenedores) | [VERIFICADO] |
| Contenedores/palés vacíos transportados como fin del viaje | Cuentan como carga; su tara es la masa del flete | [VERIFICADO] vía doc 02 |
| TEU sin peso conocido | **10 t/TEU** por defecto (6 t/TEU carga ligera; 14,5 t/TEU carga pesada) | [VERIFICADO] vía doc 02 |
| **Load factor** | Masa transportada / capacidad legal de carga del vehículo. Es el principal determinante de g CO2e/t·km | [VERIFICADO] |
| **Empty running** | % de recorrido sin carga sobre el total de operaciones | [VERIFICADO] |
| Uplift temperatura controlada | GLEC aplica un **uplift del 12 %** al ferrocarril refrigerado, extrapolado del uplift de carretera por falta de datos específicos | [VERIFICADO] vía doc 02 |

### 5.6 ¿Se pueden redistribuir los valores por defecto de GLEC? — **NO**

| Fuente | Licencia | ¿Redistribuible en repo open source? |
|---|---|---|
| **GLEC Framework v3.2** (Smart Freight Centre) | Efectivamente *NonCommercial*; exige **permiso previo por escrito** de SFC para cualquier uso comercial. Descarga gratuita ≠ licencia libre | **NO** [VERIFICADO vía doc 02] |
| Metodología ISO 14083 / GLEC (algoritmos, TCE/TOC/HOC, DAF, allocation) | Los métodos no son objeto de copyright | **Sí**, reimplementada con redacción propia |
| **ISO 14083:2023** (texto de la norma) | Copyright ISO, venta por catálogo | **NO** — solo se puede citar y resumir |

**Alternativas públicas y redistribuibles** (detalle y cifras en doc 02):

| Fuente | Licencia | Cobertura |
|---|---|---|
| **UK DESNZ — GHG Conversion Factors 2026** | Open Government Licence v3.0 (permite uso comercial con atribución) | HGV, furgonetas, rail, marítimo por tipo/tamaño de buque, aéreo, WTT y TTW por t·km |
| **ADEME — Base Empreinte / Base Carbone** | Licence Ouverte (Etalab) | Transporte francés y europeo |
| **US EPA — SmartWay** y factores por gasto | Dominio público (17 U.S.C. § 105) | Carretera y ferrocarril de EE. UU. |
| **EcoTransIT World** (parte pública) | Consultar términos por caso | Multimodal internacional |
| **CountEmissions EU** (futuro) | Se prevé **base de valores por defecto pública y gratuita** alineada con EN ISO 14083 | UE — poner en vigilancia |

> **Regla para el repositorio:** no versionar ningún valor GLEC. Implementar la metodología, alimentarla con DESNZ/ADEME/EPA, y ofrecer un *adaptador opcional* para que el usuario cargue su propio fichero GLEC bajo su propia licencia. Añadir un test que verifique la ausencia de valores GLEC en los datos versionados.

### 5.7 Ejemplo resuelto — envío multimodal camión + barco

Ver el desarrollo numérico completo en **§8.4 "Fórmulas y métodos"**.

---

## 6. Cadena de frío

### 6.1 Temperatura cinética media (MKT)

**Norma de referencia:** USP General Chapter **⟨1079.2⟩ *Mean Kinetic Temperature in the Evaluation of Temperature Excursions During Storage and Transportation of Drug Products***. [SECUNDARIO] [18] — `usp.org` y `uspnf.com` devuelven HTTP 403 a peticiones automatizadas; la ecuación y los valores se obtuvieron de resultados de búsqueda que citan el capítulo, y coinciden con la formulación original de **Haynes (1971)** y con ICH Q1A(R2).

**Ecuación** (derivada de Arrhenius):

```
        ΔH / R
MKT = ─────────────────────────────────────────────────
       − ln[ ( e^(−ΔH/(R·T₁)) + … + e^(−ΔH/(R·Tₙ)) ) / n ]
```

| Símbolo | Significado | Valor por defecto | Unidad |
|---|---|---|---|
| `ΔH` | Entalpía (calor) de activación. Se usa el valor por defecto **salvo que haya información experimental más precisa** del producto | **83,144** | kJ/mol |
| `R` | Constante universal de los gases | **8,3144 × 10⁻³** (USP) · CODATA 2019: 8,314 462 618 × 10⁻³ | kJ/(mol·K) |
| `n` | Número total de temperaturas registradas en el período de observación | — | — |
| `Tᵢ` | Temperatura de cada período, **en kelvin** | — | K |
| `MKT` | Resultado, convertible a °C restando 273,15 | — | K → °C |

> **Detalle de implementación que ahorra errores:** con los valores por defecto de USP, `ΔH/R = 83,144 / 0,0083144 = 10 000 K` **exactamente**. Conviene documentar esa constante en el código. Si se usa la R de CODATA 2019 el cociente es 9 999,92 K y el resultado cambia en menos de 0,0001 °C — irrelevante en la práctica, pero hay que declarar cuál se usa.
>
> **Riesgo numérico:** `e^(−10000/T)` con T ≈ 280 K vale ≈ e⁻³⁵·⁷ ≈ 3 × 10⁻¹⁶. Está dentro del rango de `float64`, pero para series largas o temperaturas muy bajas conviene usar **log-sum-exp** en vez de sumar exponenciales directamente.
>
> **MKT ≥ media aritmética siempre** (desigualdad de Jensen sobre una función convexa). Si el motor devuelve una MKT menor que la media, hay un error.

### 6.2 Casos de prueba resueltos (fixtures para el motor)

Calculados con `ΔH = 83,144 kJ/mol`, `R = 8,3144×10⁻³ kJ/(mol·K)`, temperaturas en °C convertidas a K con +273,15.

| Caso | Serie de temperaturas (°C) | n | Media aritmética (°C) | **MKT (°C)** | Δ (MKT − media) |
|---|---|---:|---:|---:|---:|
| **A** — Bodega a temperatura ambiente, 12 medias mensuales | 18,0 · 19,5 · 22,0 · 24,0 · 26,0 · 29,0 · 31,0 · 30,0 · 27,0 · 23,0 · 20,0 · 18,5 | 12 | 24,000000 | **25,017245** | +1,017245 |
| **B** — Cadena de frío 2–8 °C con excursión | 4,0 · 4,5 · 5,0 · 5,2 · 4,8 · 6,0 · 12,0 · 14,0 · 9,0 · 5,5 · 4,2 · 4,0 | 12 | 6,516667 | **7,227880** | +0,711213 |
| **C** — Serie didáctica de tres puntos | 20,0 · 25,0 · 30,0 | 3 | 25,000000 | **25,858208** | +0,858208 |

**Lectura del caso A:** la media aritmética (24,0 °C) sugeriría cumplimiento holgado de un límite de 25 °C, pero la **MKT es 25,02 °C**, es decir, **incumple**. Este es exactamente el motivo por el que existe la MKT y por el que el motor no debe usar promedios simples.

**Lectura del caso B:** una excursión de dos lecturas a 12 y 14 °C eleva la MKT a 7,23 °C, todavía por debajo de 8 °C. Ilustra que una excursión acotada puede ser tolerable según MKT — pero **eso no sustituye** la evaluación de estabilidad del producto ni las reglas de duración máxima de la excursión.

**Sensibilidad a `ΔH`** (serie B): con 60 kJ/mol → 7,00 °C; con 83,144 → 7,23 °C; con 100 → 7,40 °C. La MKT **crece con `ΔH`**: usar un valor de activación menor al real subestima el daño térmico.

**Reglas de uso** [SECUNDARIO]:
- La MKT se calcula sobre **todas** las lecturas del período, a intervalos **regulares**; mezclar intervalos desiguales sin ponderar sesga el resultado (si los intervalos son desiguales, ponderar por duración).
- La MKT **no reemplaza** los límites absolutos: una excursión puede violar un límite máximo aunque la MKT cumpla.
- La MKT se usa para el **almacenamiento acumulado**, no para juzgar un pico instantáneo.

### 6.3 Condiciones de almacenamiento — definiciones USP ⟨659⟩

[SECUNDARIO] — `usp.org`/`uspnf.com` inaccesibles automáticamente; valores obtenidos de resúmenes que citan el capítulo. **Verificar contra el texto oficial antes de codificar.**

| Condición | Rango | Excursiones permitidas |
|---|---|---|
| **Freezer** (congelador) | −25 °C a −10 °C | — |
| **Cold** (frío) | No más de 8 °C | — |
| **Refrigerator** (refrigerador) | **2 °C a 8 °C** | — |
| **Controlled Cold Temperature** (frío controlado) | 2 °C a 8 °C | Hasta **15 °C**, siempre que la excursión no supere 24 h y la **MKT no exceda 8 °C** |
| **Cool** (fresco) | 8 °C a 15 °C | — |
| **Controlled Room Temperature (CRT)** — definición histórica | **20 °C a 25 °C** | Excursiones entre **15 °C y 30 °C** permitidas en farmacias, hospitales, bodegas y durante el transporte, **siempre que la MKT no exceda 25 °C**. Picos transitorios hasta **40 °C** admisibles si **no superan 24 h**. Por encima de 40 °C, solo si el fabricante lo instruye |
| **Warm** | 30 °C a 40 °C | — |
| **Excessive heat** | Por encima de 40 °C | — |

> ⚠️ **Cambio en curso [NO VERIFICADO]:** USP propuso en *Pharmacopeial Forum* **PF 52(4)** redefinir la CRT como **15 °C a 25 °C** (bajando el límite inferior de 20 a 15 °C), alineándose con JP, Ph. Eur. y OMS, y manteniendo la MKT para evaluar excursiones sobre 25 °C. Circula una fecha de **1 de julio de 2026** asociada a un borrador revisado del capítulo ⟨659⟩, pero **no se pudo confirmar si ya es texto oficial o sigue siendo propuesta**. El motor debe **parametrizar** el rango CRT, no fijarlo en código.

### 6.4 Excursiones de temperatura — definición operativa

| Concepto | Definición operativa para el motor | Etiqueta |
|---|---|---|
| **Excursión** | Desviación de la temperatura fuera del rango de almacenamiento etiquetado del producto, durante un período acotado | [SECUNDARIO] |
| Parámetros que hay que registrar | (1) temperatura máxima/mínima alcanzada; (2) **duración acumulada** fuera de rango; (3) número de excursiones; (4) MKT del período completo | [SECUNDARIO] |
| Criterio de aceptación típico | Combinación de: MKT dentro del límite **Y** duración de la excursión dentro del tolerado **Y** ausencia de picos sobre el máximo absoluto | [SECUNDARIO] |
| Decisión final | La aceptación o rechazo la determina el **titular del registro sanitario** con sus datos de estabilidad, no el software | [SECUNDARIO] |

### 6.5 Vida útil dinámica (dynamic shelf life)

Enfoques usados para reemplazar la fecha de vencimiento fija por una vida útil que consume el historial térmico real. [SECUNDARIO] — resumen conceptual, **sin valores por defecto verificados**.

| Enfoque | Idea | Parámetros que exige |
|---|---|---|
| **Arrhenius / MKT acumulada** | La degradación depende de la temperatura según Arrhenius; se acumula "daño térmico" y se descuenta de la vida útil nominal | `Ea` del deterioro del producto (**no** el 83,144 por defecto: ese es para evaluar excursiones, no para modelar un producto concreto) |
| **Q₁₀** | Regla empírica: la velocidad de deterioro se multiplica por `Q₁₀` por cada +10 °C. `vida_útil(T) = vida_útil(T_ref) · Q₁₀^((T_ref − T)/10)` | `Q₁₀` del producto (típicamente 2–3 en alimentos, pero **específico del producto**) |
| **Modelos microbiológicos predictivos** | Crecimiento de patógenos/alterantes en función de T, pH y a_w (Baranyi–Roberts, Gompertz modificado, raíz cuadrada de Ratkowsky) | Parámetros cinéticos por microorganismo y matriz |
| **TTI — Time-Temperature Indicators** | Etiquetas físico-químicas o enzimáticas cuya respuesta integra tiempo y temperatura; se calibran para imitar la cinética del producto | Calibración TTI ↔ producto |

> **Recomendación para Agentes ESG:** implementar MKT y Q₁₀ como *utilidades* con parámetros que aporta el usuario, y **rechazar explícitamente** dar valores por defecto de `Ea` o `Q₁₀` por producto. Un valor inventado aquí puede liberar producto no apto.

### 6.6 Chile — Reglamento Sanitario de los Alimentos (DS 977/96 MINSAL)

Texto consolidado a **mayo de 2024** [19]. Todas las citas son literales del reglamento (normativa pública). [VERIFICADO]

| Artículo | Materia | Temperatura |
|---|---|---|
| **67** | Almacenamiento y transporte de productos terminados | "condiciones adecuadas de temperatura y humedad que garantice su aptitud para el consumo humano" |
| **68** | **Transporte de alimentos perecibles que requieren frío** (fresco, enfriado y/o congelado) | Solo en vehículos **con carrocería cerrada**, con equipos capaces de mantener la temperatura requerida, **provistos de termómetros que permitan su lectura desde el exterior**. Requiere **autorización sanitaria** válida por **3 años** |
| **186** | Definición de alimento congelado | Proceso térmico hasta que el producto alcance **−18 °C en el centro térmico**. Rotulación obligatoria "PRODUCTO CONGELADO" (salvo helados del art. 243) |
| **187** | Precocidos destinados a congelación rápida | Si no se pueden enfriar de inmediato, conservar a **más de 60 °C** medidos en el punto más frío del producto hasta poder enfriar y congelar |
| **188** | Reenvasado de congelados | Sala con dispositivo que mantenga temperatura **no superior a 8 °C** y registro permanente |
| **189** | Almacenamiento de congelados | Cámaras frigoríficas a **−18 °C o inferior**, con mínima fluctuación y **registro continuo** de temperatura |
| **190** | **Transporte interurbano de congelados** | Equipos capaces de mantener el producto a **−18 °C o más baja**; termómetros legibles desde el exterior y **dispositivos de registro durante el transporte**. Se tolera aumento hasta **−15 °C**, que debe reducirse rápidamente |
| **191** | **Transporte local de congelados** a minoristas | Todo aumento sobre −18 °C debe durar el mínimo tiempo y **en ningún caso superar −12 °C** |
| **192** | Venta de congelados | Vitrinas congeladoras capaces de mantener **−18 °C**, con termómetros. Se tolera por períodos breves un aumento que **no sobrepase −12 °C**. Reglas de descongelación y rotulado "PRODUCTO DESCONGELADO. NO VOLVER A CONGELAR" |
| **286** | Aves faenadas, trozadas, menudencias y despojos | Enfriados a **2 °C como máximo**; en punto de venta, hasta **6 °C** medidos en el interior de la masa muscular |
| **287** | Aves refrigeradas | Entre **4 °C y −18 °C** |
| **288** | Aves congeladas | **−18 °C como máxima**, medida en el centro de la masa muscular |
| **302** | Cecinas crudas frescas, acidificadas y cocidas | Refrigeración **0 – 6 °C** tras elaboración y en locales de expendio. Cecinas maduradas: lugar fresco y seco, **máximo 12 °C** |
| **303** | Transporte y distribución de cecinas | Vehículos autorizados, refrigeración **entre 0 y 6 °C** |
| **466** | **Comidas y platos preparados** | Calientes: recipientes térmicos a temperatura **uniforme y permanente de 65 °C**. Fríos: conservación y transporte a **máximo 5 °C**. Aplica también a la distribución de alimentos en todo tipo de transporte de pasajeros |
| Art. 4° (ferias libres), letra d) | Pescados, mariscos, carnes y subproductos en ferias | Sistema de frío que mantenga **0 °C – 5 °C** durante toda la jornada |
| Art. 4° letra f) | Quesos y cecinas en puestos de venta | Refrigeración **máximo 5 °C**; cecinas crudas maduradas sin refrigeración en lugar seco y fresco, **máximo 12 °C** |

> **Observación para el motor:** el RSA **no** define un único rango de "refrigeración": fija temperaturas **por tipo de producto** (0–5 °C, 0–6 °C, 2 °C, 4 °C, 5 °C, 8 °C, 12 °C). Modelar como **tabla producto → rango**, nunca como constante global. El único valor realmente transversal es **−18 °C para congelados**, con tolerancias de **−15 °C** (transporte interurbano) y **−12 °C** (transporte local y exhibición).

### 6.7 Chile — Medicamentos: reglas del ISP y MINSAL

| Norma | Contenido | Aprobación / vigencia | Etiqueta |
|---|---|---|---|
| **Norma Técnica N° 208** — *Almacenamiento y Transporte de Medicamentos Refrigerados y Congelados* | Requisitos técnicos para medicamentos que necesitan **cadena de frío**: cámaras de frío, refrigeradores, congeladores, vehículos de transporte, contenedores fríos y termos. Consta de **20 páginas** | **Decreto Exento N° 48 de 17.09.2019** (MINSAL, Subsecretaría de Salud Pública), publicado el **30.09.2019**. Modificado por **Decreto Exento N° 49**, publicado el **21.09.2020**. **Entró en vigencia 12 meses después de su publicación** | [VERIFICADO] [20] |
| Ámbito de la NT 208 | Aplica a establecimientos sanitariamente autorizados de **almacenamiento y distribución**: laboratorios farmacéuticos, droguerías, depósitos de productos farmacéuticos de uso humano, **depósitos de vacunas e inmunoglobulinas**. **NO aplica a farmacias, botiquines ni recetarios magistrales** | Vigente | [VERIFICADO] [20] |
| Rango de cadena de frío de la NT 208 | Refrigerados: **5 °C ± 3 °C**, es decir **+2 °C a +8 °C** | Vigente | [SECUNDARIO] — no se pudo leer el texto de la norma; confirmar en el PDF de MINSAL |
| Rango de congelados de la NT 208 | No confirmado | — | **[NO VERIFICADO]** |
| **Norma Técnica N° 147** — Buenas Prácticas de Almacenamiento y Distribución (BPAD) de productos farmacéuticos | Norma general de almacenamiento y distribución; la NT 208 la complementa | Vigente | [VERIFICADO] (referenciada en el Decreto Ex. 48) [20] |
| **Norma Técnica N° 127** — Buenas Prácticas de Manufactura (BPM), anexos 4 y 5 | Condiciones generales de almacenamiento en manufactura | Vigente | [VERIFICADO] (referenciada) [20] |
| **Resolución N° 399/2020** (ISP) | Aprueba la **guía de inspección** de BPAD | Vigente | [SECUNDARIO] |
| Marco reglamentario superior | **DS N° 3 de 2010** (Reglamento del Sistema Nacional de Control de Productos Farmacéuticos de Uso Humano) y **DS N° 466 de 1984** (Reglamento de Farmacias, Droguerías, Almacenes Farmacéuticos, Botiquines y Depósitos) | Vigente | [VERIFICADO] (citados en el Decreto Ex. 48) [20] |
| Alineación internacional | La NT 208 se desarrolló conforme a las directrices de **OMS**, en particular las *Good Distribution Practices* del **TRS 992, Anexo 5** | — | [SECUNDARIO] |
| Fiscalización | El **ISP** vigila el cumplimiento; promueve autoevaluación con checklist y levanta actas de infracción | Vigente | [SECUNDARIO] [21] |

---

## 7. Trazabilidad y retiros de mercado

### 7.1 Modelo de datos GS1 para lotes

**Estado de los estándares** [SECUNDARIO] [22]:

| Estándar | Versión / estado | Para qué sirve |
|---|---|---|
| **GS1 General Specifications** | **Release 26**, ratificada en **enero de 2026** | Define claves de identificación, atributos de datos y códigos de barras |
| **EPCIS & CBV** | **2.0** | Modelo de eventos de la cadena de suministro (qué, cuándo, dónde, por qué) e intercambio de datos de trazabilidad. Acepta un subconjunto acotado de URIs GS1 Digital Link |
| **GS1 Digital Link** | Vigente (verificar número de versión exacto) | Convierte el identificador en una URL web resoluble |
| **GS1 Global Traceability Standard (GTS)** | Vigente | Marco de procesos de trazabilidad end-to-end |
| **GDSN** | Vigente | Sincronización de datos maestros de producto |

**Claves de identificación GS1 (las cuatro que importan para lotes)**

| Clave | Qué identifica | AI |
|---|---|---|
| **GTIN** | El artículo comercial (producto + presentación) | `01` |
| **SSCC** | La **unidad logística** (pallet, caja consolidada) — es la clave del movimiento físico | `00` |
| **GLN** | La **parte** (empresa) y la **ubicación** física | `414` (ubicación), `410`–`417` (roles) |
| **GTIN + lote** o **GTIN + serie** | La **instancia trazable**: GTIN + `10` (lote) o GTIN + `21` (serie) | `01`+`10` / `01`+`21` |

**Application Identifiers verificados** contra la referencia oficial de GS1 (fichero `GS1_Application_Identifiers`, v1.2, última modificación **26 de enero de 2026**) [VERIFICADO] [23]:

| AI | Título GS1 | Formato | Uso en el modelo de lotes |
|---:|---|---|---|
| `00` | SSCC | N2+N18 | Clave de la unidad logística |
| `01` | GTIN | N2+N14 | Clave del producto |
| `02` | CONTENT | N2+N14 | GTIN del contenido de una unidad logística |
| `10` | BATCH/LOT | N2+X..20 | **Número de lote** — longitud variable hasta 20 caracteres alfanuméricos |
| `11` | PROD DATE | N2+N6 | Fecha de producción (AAMMDD) |
| `13` | PACK DATE | N2+N6 | Fecha de envasado |
| `15` | BEST BEFORE / BEST BY | N2+N6 | Consumo preferente |
| `16` | SELL BY | N2+N6 | Fecha límite de venta |
| `17` | USE BY / EXPIRY | N2+N6 | **Fecha de vencimiento** |
| `21` | SERIAL | N2+X..20 | Número de serie (unidad individual) |
| `30` | VAR. COUNT | N2+N..8 | Cantidad variable |
| `3103` | NET WEIGHT (kg) | N4+N6 | **Peso neto en kg con 3 decimales** — clave para t·km |

> **AIs adicionales muy usados en logística y frío** (`37` COUNT, `400`/`401` referencias de pedido y envío, `410`–`417` GLN por rol, `422` país de origen, `7003` fecha y hora de vencimiento, `7006`–`7007` fechas de primera congelación y de sacrificio, `8003`/`8006`/`8018`/`8026` GRAI/ITIP/GSRN): **[NO VERIFICADO]** — no se pudieron leer del fichero oficial en esta sesión. Confirmar en `ref.gs1.org/ai/` antes de codificar el parser.

**Modelo de datos mínimo recomendado para el motor** (redacción propia a partir de lo anterior):

```
Producto      : gtin (14)                         # AI 01
Lote          : gtin + batch_lot (≤20 alfanum)    # AI 01 + 10
Instancia     : gtin + serial                     # AI 01 + 21   (opcional)
Unidad logíst.: sscc (18)                         # AI 00
Fechas        : prod_date, pack_date, best_before, use_by   # AI 11,13,15,17
Peso neto     : net_weight_kg (3 decimales)       # AI 3103
Ubicaciones   : gln_origen, gln_destino           # AI 410/414/415/417
Evento EPCIS  : what (epc/quantity) · when (eventTime, recordTime, tz)
                where (readPoint, bizLocation) · why (bizStep, disposition)
```

Cuatro reglas que evitan los errores típicos [SECUNDARIO]:
1. **El lote solo es trazable si viaja pegado al GTIN.** Un `batch_lot` sin GTIN no identifica nada: dos fabricantes pueden usar el mismo texto de lote.
2. **El SSCC es lo que realmente se mueve.** Los eventos de transporte se registran sobre SSCC; el vínculo SSCC → (GTIN, lote, cantidad) es el que permite un retiro quirúrgico.
3. **Las fechas GS1 son AAMMDD** (6 dígitos, sin siglo explícito). Hay que definir la ventana de siglo en el parser (regla habitual: ±50 años respecto del año actual) y aceptar `DD = 00` como "fin de mes", que GS1 permite.
4. **Cada eslabón debe conservar "un paso atrás, un paso adelante"**: de quién recibió cada lote y a quién lo entregó. Ese es el mínimo legal en Chile y la UE, y el mínimo funcional para un recall.

### 7.2 Chile — Alimentos: trazabilidad y alerta

**Base reglamentaria de los registros (RSA, DS 977/96)** [VERIFICADO] [19]:

> **Artículo 66.-** "Deberán existir registros de producción, distribución y control de los alimentos y materias primas y conservarse, como mínimo, durante **90 días posteriores a la fecha de vencimiento o plazo de duración del producto**. Los alimentos de duración indefinida deberán mantener el registro, al menos, **durante tres años**. En el registro deberá identificarse la procedencia del alimento y/o materia prima […]"

(Artículo reemplazado por el N° 3 del art. 1° del **Decreto 60/18** del Ministerio de Salud, D.O. 07.07.2018.)

**Definición de lote (RSA)**: "Cantidad determinada de un alimento producido en condiciones esencialmente [iguales]" — numeral 21 del artículo de definiciones. [VERIFICADO] [19]

> ⚠️ El RSA **no contiene artículos específicos de "retiro de producto" ni de "alerta alimentaria"**: se buscó "retiro", "alerta", "trazabilidad" y "rastreabilidad" en el texto consolidado a mayo de 2024 y no aparecen con ese sentido. Las facultades de retiro derivan del **Código Sanitario** y de la Ley N° 19.937 sobre Autoridad Sanitaria, y se operan vía **SEREMI de Salud**. [VERIFICADO por ausencia + SECUNDARIO]

**RIAL — Red de Información y Alertas Alimentarias (ACHIPIA)** [VERIFICADO] [24]

| Aspecto | Detalle |
|---|---|
| Documento | *Procedimiento de Gestión de la Red de Información y Alertas Alimentarias (RIAL)*, **versión 11-12-2013** — el procedimiento publicado más reciente que se encontró |
| Mandato legal | **DS N° 162 de 06.12.2010** (MINSEGPRES), que modifica el **DS N° 83 de 21.10.2005**: encarga a ACHIPIA proponer un sistema de información y alertas alimentarias. Todos los servicios del Estado están obligados a entregar la información que ACHIPIA les solicite oficialmente |
| Servicios participantes | ACHIPIA + **SAG, SERNAPESCA, DIRECON, MINSAL, SUBPESCA y ODEPA**, mediante **puntos de contacto** designados |
| Definición de evento | "Aquella situación en la cual se verifica la presencia de un peligro en un alimento para consumo humano o para consumo animal, cuando éste transgrede la normativa nacional o de un mercado de destino" |

**Clasificación de eventos RIAL** — el criterio es la **disponibilidad del alimento para el consumidor final** [VERIFICADO] [24]:

| Tipo | Cuándo aplica | Acción |
|---|---|---|
| **Alerta** | Peligro detectado en un alimento **presente en el mercado** (disponible para la venta al público) nacional, o en un producto chileno en el mercado internacional. *No* se considera presente en el mercado si no ha salido del establecimiento elaborador, sigue bajo su control o está en tránsito al mercado de destino | Los servicios competentes actúan **de forma inmediata** |
| **Información** | Peligro detectado en alimento nacional o importado **que no está presente en el mercado** | Los servicios evalúan la adopción de medidas |
| **Rechazo** | (a) Alimento elaborado en un tercer país cuyo ingreso a Chile fue rechazado por la autoridad sanitaria; (b) alimento chileno con peligro informado por la autoridad del país de destino que notifica prohibición de ingreso. **No se incluyen los rechazos por etiquetado** | Actuación de las autoridades nacionales con medidas preventivas y correctivas |

**Retiro (recall) de alimentos** [SECUNDARIO] [25]: es el procedimiento por el cual una instalación de alimentos retira un producto del mercado cuando tiene certeza o sospecha de que incumple las exigencias reglamentarias, está produciendo o puede producir problemas de salud, o transgrede los estándares de calidad declarados. ACHIPIA, MINSAL y el Ministerio de Agricultura desarrollaron un **Manual de Buenas Prácticas de Recall dirigido a la industria de alimentos**, de descarga gratuita. La clasificación por clases (I = riesgo grave para la salud, II = riesgo moderado, III = incumplimiento sin riesgo apreciable, p. ej. problemas de etiquetado o de calidad declarada) aparece en ese manual. **[NO VERIFICADO]** el detalle de plazos y alcance de cada clase — leer el manual antes de programarlo.

**En la práctica (caso Listeria, octubre de 2024)** [SECUNDARIO]: MINSAL notificó alerta alimentaria tras análisis de los laboratorios de las SEREMI de Salud (Región Metropolitana y Los Lagos), ordenó el **retiro inmediato**, fiscalizó puntos de venta, abrió sumarios sanitarios, aplicó prohibición sobre líneas de producción y reforzó la vigilancia. Es el flujo real a modelar: *hallazgo de laboratorio → notificación RIAL → alerta pública MINSAL → orden de retiro → fiscalización → medidas sobre el establecimiento*.

### 7.3 Chile — Productos farmacéuticos: retiro de mercado (ISP/ANAMED)

Fuente: *Instructivo para notificar retiros del mercado de productos farmacéuticos*, **ANAMED — Subdepartamento de Inspecciones**, ISP [VERIFICADO] [26].

| Elemento | Regla |
|---|---|
| **Base legal** | **Artículo 71° N° 3 del DS N° 3 de 2010** (Reglamento del Sistema Nacional de Control de Productos Farmacéuticos de Uso Humano, MINSAL). También se invocan el art. 60 del mismo decreto, la **NT N° 127** (BPM, aprobada por Decreto Exento N° 159 de 2013) y la **NT N° 147** (BPAD, aprobada por Decreto Exento N° 57 de 2013) [SECUNDARIO para los números de decreto] |
| **Quién notifica** | El **titular del registro sanitario farmacéutico** |
| **Plazo** | "**De manera inmediata a su inicio**" |
| **Cómo** | Completar el *Formulario Notificación de Retiro del Mercado Productos Farmacéuticos* (web del ISP) y presentarlo en **oficina de partes** del ISP |
| **Adjuntos obligatorios** | (1) **Registro de distribución** de los lotes que se retirarán; (2) **investigación del defecto de calidad**, incluyendo las medidas adoptadas |
| **Motivo** | Defecto de calidad **sospechado o confirmado** |
| **Alcance obligatorio de la empresa** | Sistema de gestión de calidad para retiros; estrategia de retiro rápido y efectivo; procedimientos escritos que permitan iniciar en **el nivel de la cadena de distribución donde esté el producto**; personal responsable de ejecución y coordinación; **área segregada y segura** para almacenar lo retirado |
| **Registros de distribución** | Deben estar **rápidamente disponibles** para la persona autorizada y para la autoridad reguladora, con información suficiente sobre mayoristas y clientes abastecidos directamente (incluidos, en exportación, quienes recibieron muestras para pruebas clínicas y médicas) |
| **Seguimiento** | El progreso debe ser **monitoreado y registrado** |
| **Informe final** | Reporte final con **conciliación entre cantidades entregadas y devueltas**, entregado a ANAMED (Subdepartamento de Inspecciones) |
| **Destino del producto** | **Todos los productos retirados deben ser destruidos e inutilizados**, mediante vías y empresas autorizadas |
| **Prueba de destrucción** | Documentos de respaldo: **acta notarial y guía de despacho** que individualice producto, series, lotes y cantidades |
| **Mejora continua** | La **efectividad de la estrategia de retiro debe controlarse y evaluarse periódicamente** (mock recalls) |
| **Ámbito** | Todos los establecimientos que fabriquen, importen, distribuyan y comercialicen productos **farmacéuticos o cosméticos** en Chile |
| **Transparencia** | El ISP publica un **"Listado de Productos Retirados del Mercado"** en su sitio web |

> **Implicación de diseño para Agentes ESG:** el informe final exige **conciliar unidades entregadas vs. devueltas**. Eso obliga a que el modelo de datos guarde cantidad por (GTIN, lote, destinatario) en cada despacho, no solo el total. Si el sistema no lo registra al despachar, el recall no se puede cerrar.

---
