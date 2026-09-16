---
name: maritimo-ets
description: El costo de carbono del flete marítimo a Europa: mercado de carbono europeo (EU ETS marítimo, Directiva (UE) 2023/959) y FuelEU Maritime (Reglamento (UE) 2023/1805). Úsala cuando aparezca un "ETS surcharge", "emission surcharge" o recargo de emisiones en el flete o el bill of lading, cuando negocien tarifa marítima a Europa, cuando pregunten por derechos de emisión de buques, por FuelEU, por el methane slip del GNL o por el recargo por contenedor.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# El carbono del flete a Europa

Son **dos mecanismos distintos** que se pagan los dos y no se compensan entre sí.
Esa es la idea que hay que dejar instalada antes que ninguna otra, porque es
exactamente lo que se presta a cobros inflados.

| | **Mercado de carbono marítimo (ETS)** | **FuelEU Maritime** |
|---|---|---|
| Qué mide | Toneladas emitidas (cantidad) | Intensidad del combustible (gCO2e por MJ) |
| Qué genera | Compra y entrega de derechos de emisión | Penalización si hay déficit |
| Obligado | La compañía naviera | La compañía naviera |
| Norma | Directiva 2003/87/CE, reformada por la (UE) 2023/959 | Reglamento (UE) 2023/1805 |

Un buque puede cumplir FuelEU y aun así pagar mucho ETS, o al revés. **Un recargo
que los junte sin desglosar hay que cuestionarlo.**

## Quién está obligado (y quién paga)

- **Obligada: la compañía naviera** —el armador, el gestor naval o el fletador a
  casco desnudo—. El exportador **no monitorea, no declara y no entrega
  derechos**.
- Pero el costo llega igual, como **recargo en el flete**. Aparece como "ETS
  Surcharge", "Emission Surcharge" o similar, revisado normalmente cada trimestre
  y diferenciado por ruta y tipo de equipo.
- Cuando quien compra el combustible o decide ruta y velocidad es otra entidad
  (típicamente el fletador por tiempo), la naviera tiene derecho a que le
  reembolsen el costo, pero sigue siendo ella la que entrega los derechos.

## La regla del 50 %

Para una ruta **Sudamérica → Europa** se cubre el **50 % de las emisiones del
viaje**. Es el punto de negociación más concreto que existe.

| Tipo de viaje | Cobertura |
|---|---|
| Tercer país → puerto de la UE | **50 %** |
| Puerto de la UE → tercer país | **50 %** |
| Entre dos puertos de la UE | 100 % |
| Buque atracado en puerto de la UE | 100 % |

Y el porcentaje que hay que entregar subió por escalones:

| Año de emisiones | Derechos a entregar |
|---|---|
| 2024 | 40 % |
| 2025 | 70 % |
| **2026 y siguientes** | **100 %** |

> **2026 es el primer año al 100 %** y además es el año en que entran el
> **metano y el óxido nitroso** al régimen. Es el salto de costo más grande de
> toda la serie. Quien negoció su flete en 2024 y no revisó la cláusula de
> recargos va a encontrar una diferencia notable en la factura.

También hay regla antielusión: los puertos de transbordo a menos de 300 millas
náuticas de la UE con más del 65 % de transbordo **no cuentan** como escala. Una
parada ahí no corta el viaje ni reduce la obligación.

## Calcular el recargo que le corresponde

```bash
python .claude/motor/esg.py europa maritimo --anio 2026 --tipo-viaje tercer_pais_ue --consumo 1500 --combustible HFO --precio-eua 75 --capacidad-teu 8000 --ocupacion 0.85
```

La cuenta es:

```
Emisiones del viaje  = consumo de combustible × factor de emisión
Emisiones cubiertas  = emisiones del viaje × cobertura (50 % o 100 %)
Derechos a entregar  = emisiones cubiertas × porcentaje del año
Costo                = derechos × precio del derecho europeo (EUA)
Recargo por TEU      = costo / contenedores transportados
```

Ejemplo real de la investigación, Callao → Rotterdam, portacontenedores de 8.000
TEU con fueloil pesado, 1.500 toneladas de consumo y un precio hipotético de 75
EUR por tonelada:

| Año | Emisiones cubiertas | Costo del viaje | Por contenedor |
|---|---|---|---|
| 2024 (40 %) | 934 t | 70.065 EUR | **10,30 EUR/TEU** |
| 2025 (70 %) | 1.635 t | 122.614 EUR | **18,03 EUR/TEU** |
| 2026 (100 %) | 2.336 t | 175.163 EUR | **25,76 EUR/TEU** |
| 2026 con metano y N2O | 2.377 t | 178.250 EUR | **26,21 EUR/TEU** |

Un contenedor de 40 pies es aproximadamente el doble del de 20 pies.

**El precio del derecho europeo lo entregas tú**: es de mercado y cambia todos
los días. Pídeselo a la naviera junto con el periodo al que corresponde; el motor
lo deja registrado en el resultado.

## Qué exigirle a la naviera

Cuatro preguntas que ordenan cualquier negociación de flete anual:

1. Que el recargo aplique el **50 %** en rutas Sudamérica–Europa, no el 100 %.
2. **Qué precio del derecho europeo** usaron como referencia y de qué periodo.
3. El **factor de emisión por contenedor** de esa ruta y ese servicio.
4. El **desglose separado** del recargo de ETS y del de FuelEU.

> Palanca real: las rutas y los buques no son iguales. Un servicio con buques
> modernos y eficientes tiene menor recargo por contenedor. Vale la pena
> compararlo entre navieras al licitar el flete anual, igual que se compara el
> flete base.

## FuelEU, en corto

FuelEU no mide toneladas: mide **qué tan sucia es la energía** que usa el buque.
Parte de un valor de referencia de **91,16 gramos de CO2 equivalente por
megajoule** (la media de la flota en 2020) y exige bajarlo:

| Desde | Reducción | Límite |
|---|---|---|
| 2025 | 2 % | 89,3368 gCO2e/MJ |
| 2030 | 6 % | 85,6904 |
| 2035 | 14,5 % | 77,9418 |
| 2040 | 31 % | 62,9004 |
| 2045 | 62 % | 34,6408 |
| 2050 | 80 % | 18,2320 |

Se mide **por buque y por año completo**, no por viaje. Igual que en el ETS, en
rutas con un tercer país se computa el **50 %** de la energía.

```bash
python .claude/motor/esg.py europa maritimo --anio 2025 --consumo-anual 10000 --combustible HFO --precio-eua 75 --gwp-ch4 25 --gwp-n2o 298
```

Regla práctica que vale la pena memorizar: **un buque que quema fueloil pesado
puro paga del orden de 62 euros de penalización FuelEU por tonelada de
combustible** en 2025. Sirve para contrastar el recargo que cobra la naviera.

Y si el déficit se repite año tras año, la penalización sube: se multiplica por
`1 + (n − 1)/10`, donde n son los periodos consecutivos.

## El GNL no es la solución fácil

Un motor de gas natural licuado tipo Otto de media velocidad deja escapar un
**3,1 % del combustible sin quemar** como metano (*methane slip*), y el metano
calienta mucho más que el CO2. Por eso, desde que en 2026 entraron el metano y el
óxido nitroso al mercado de carbono, el GNL rinde bastante peor de lo que sugiere
su factor de CO2 (2,750 frente a 3,114 del fueloil pesado).

Si la naviera vende "buque a GNL" como argumento de menor recargo, vale la pena
pedir el número con el metano incluido.

## La oportunidad chilena

FuelEU premia con un **multiplicador de 2** el uso de combustibles renovables de
origen no biológico entre 2025 y 2033: cada megajoule cuenta por dos. Eso crea
demanda europea estructural para el **e-metanol y el amoníaco verde** hechos con
hidrógeno verde chileno. Si la conversación es de proyecto y no de flete, ahí
está el ángulo.

## Cómo conversas esto

- Primero: «usted no tiene ninguna obligación aquí; esto es un costo del flete
  que se puede revisar y negociar».
- Después el número por contenedor, con la ruta y el año reales de la empresa.
- Después las cuatro preguntas para la naviera. Eso es lo accionable.
- No prometas ahorros: el recargo es legítimo, lo que se negocia es que esté bien
  calculado y bien desglosado.

## Límites honestos

- Esto es **orientación**, no asesoría en comercio marítimo. La cifra oficial es
  la que emite la naviera con sus emisiones verificadas.
- El precio del derecho europeo es de mercado. **No uses una cifra de memoria**:
  pídesela a la naviera.
- Los valores de potencial de calentamiento global (GWP) del metano y el óxido
  nitroso **no están verificados** en la investigación del proyecto. El motor te
  los pide antes de incluir esos gases y deja registrado el valor usado.
- El contenido exacto de las exclusiones del ámbito (los apartados del reglamento
  de seguimiento marítimo) tampoco está confirmado: si el buque es especial,
  pregúntaselo a la naviera.
- El 50 % no está garantizado para siempre: si la Organización Marítima
  Internacional no adopta una medida global antes de 2028, la Comisión tiene
  mandato para evaluar subir esa cobertura.
