---
name: cbam
description: CBAM, el arancel de carbono en frontera de la Unión Europea (Reglamento (UE) 2023/956, simplificado por el Reglamento (UE) 2025/2083). Úsala cuando exporten a Europa acero, hierro, aluminio, cemento, fertilizantes, hidrógeno o electricidad, cuando un importador europeo les pida las emisiones incorporadas o "embedded emissions", cuando mencionen el mecanismo de ajuste en frontera, los certificados CBAM o el declarante autorizado.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# CBAM: el arancel de carbono en frontera

Europa cobra por el carbono que trae dentro un producto importado, para
igualarlo con lo que paga una fábrica europea. Desde el **1 de enero de 2026**
está en régimen definitivo: ya no es solo informar, ahora se paga.

## Lo primero: quién hace qué

Esto hay que dejarlo clarísimo desde la primera frase, porque es donde más se
angustia la gente sin necesidad:

- **El obligado es el importador europeo** (o su representante aduanero
  indirecto). Él se registra como *declarante CBAM autorizado*, él declara, él
  compra y entrega los certificados, y él paga.
- **El exportador no se registra, no declara y no paga nada.**
- Lo único que tiene que hacer el exportador es **entregarle al importador las
  emisiones incorporadas** de lo que le vende.

Pero ese "único" vale dinero: si no llegan los datos, el importador usa **valores
por defecto**, que están fijados a propósito muy arriba —el Reglamento (UE)
2025/2083 los subió al nivel de los diez países exportadores con mayores
emisiones— y ese sobrecosto termina en el precio o en el cambio de proveedor.

## ¿Le aplica?

Solo seis sectores, ninguno más:

| Sector | Ejemplos |
|---|---|
| **Hierro y acero** | Barras, perfiles, tubos, manufacturas del capítulo 73 |
| **Aluminio** | Lingotes, perfiles, planchas, manufacturas |
| **Cemento** | Clínker, cemento Portland, cementos hidráulicos |
| **Fertilizantes** | Amoníaco, ácido nítrico, nitratos, abonos nitrogenados y NPK |
| **Hidrógeno** | Partida 2804 10 00 |
| **Electricidad** | Partida 2716 00 00 |

**Fuera del CBAM**: fruta, vino, harina de pescado, celulosa, agroindustria,
salmón, y también el **cobre**. Si exportan eso, el CBAM no los toca. Lo que sí
los toca es el recargo del flete (skill `maritimo-ets`).

> Ojo con el cobre: hoy no está en la lista, pero el reglamento prevé revisiones
> para extender el ámbito. No prometas que seguirá fuera para siempre.

## El umbral de 50 toneladas

El Reglamento (UE) 2025/2083 reemplazó la vieja exención de 150 euros por envío
por un umbral mucho más útil: **50 toneladas de masa neta acumuladas por
importador y año natural**.

Tres detalles que hay que decir siempre:

1. Es **acumulativo por año**, no por envío.
2. Es **del importador europeo**, no del exportador. Si ese importador junta
   compras de varios proveedores y pasa las 50 toneladas, **todas** sus
   importaciones entran al régimen, incluidas las de ustedes.
3. **Electricidad e hidrógeno no tienen umbral**: entran desde el primer kilo.

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" europa cbam --sector acero --cantidad 500 --see 1.80 --anio 2026 --precio-certificado 75 --masa-anual-importador 500
```

## Qué datos hay que reunir

Lo que el importador va a pedir, y de dónde sale:

| Dato | Dónde está |
|---|---|
| Instalación donde se produjo la mercancía | Identificación de la planta |
| **Emisiones directas** del proceso, del periodo de referencia | Consumo de combustibles y proceso de la planta |
| **Emisiones indirectas** (electricidad consumida) | Solo para cemento y fertilizantes |
| **Nivel de actividad**: toneladas producidas en ese periodo | Producción de la planta |
| **Precursores**: masa y emisiones de las materias primas ya procesadas | Proveedores de insumos |
| Precio del carbono ya pagado en el país de origen | Comprobantes de pago |

Regla que la gente confunde mucho, y está en el **Anexo II** del reglamento:

- **Hierro y acero, aluminio e hidrógeno**: se computan **solo emisiones
  directas**.
- **Cemento y fertilizantes**: se computan **directas e indirectas**.

Si faltan las indirectas de un cemento o un fertilizante, el motor **las pide**;
no las inventa, porque los valores por defecto del periodo definitivo no están
confirmados.

## Cómo se calcula

La fórmula es la del **Anexo IV del Reglamento (UE) 2023/956**:

```
Emisiones específicas (SEE) = (emisiones directas + indirectas + precursores) / toneladas producidas
Emisiones incorporadas      = toneladas del envío × SEE
Certificados a entregar     = emisiones incorporadas × (1 − factor CBAM del año) − carbono pagado en origen
Costo                       = certificados × precio del certificado
```

Con el SEE ya verificado por la planta:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" europa cbam --sector acero --cantidad 500 --see 1.80 --anio 2026 --precio-certificado 75
```

Con los datos brutos de la instalación:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" europa cbam --sector cemento --cantidad 200 --emisiones-directas 60000 --emisiones-indirectas 9000 --nivel-actividad 100000 --anio 2026 --precio-certificado 75
```

Con precursores (masa:emisiones por tonelada, separados por coma):

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" europa cbam --sector acero --cantidad 500 --emisiones-directas 700 --nivel-actividad 1000 --precursores "300:1.2, 80:0.4" --anio 2026 --precio-certificado 75
```

**El precio del certificado lo entregas tú.** Es de mercado y cambia todos los
días: en 2026 es la media trimestral del precio de subasta del derecho de emisión
europeo, y desde 2027 la media semanal. El motor nunca lo inventa y deja
registrado el que se usó, para que el cálculo sea auditable.

## La curva: por qué 2026 engaña

El factor CBAM refleja la asignación gratuita que todavía reciben las fábricas
europeas. Mientras exista, el importador paga solo la diferencia.

| Año | Se paga | Ejemplo: 500 t de acero a 1,80 t CO2e/t, a 75 EUR/t |
|---|---|---|
| 2026 | 2,5 % | 1.688 EUR — **3,38 EUR por tonelada** |
| 2027 | 5 % | 3.375 EUR |
| 2028 | 10 % | 6.750 EUR |
| 2029 | 22,5 % | 15.188 EUR |
| **2030** | **48,5 %** | 32.738 EUR — **65,48 EUR por tonelada** |
| 2034 | **100 %** | 67.500 EUR — **135 EUR por tonelada** |

> El costo se multiplica por **cuarenta** entre 2026 y 2034. Quien mire el CBAM
> hoy y diga «son tres euros por tonelada, no importa» está leyendo mal la curva.
> Lo que hay ahora es una ventana de cuatro años para descarbonizar y para montar
> el sistema de datos.

El motor entrega la curva completa en cada cálculo, y el informe HTML la dibuja:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" europa informe
```

## Qué pasa si no entregan datos

El importador usa valores por defecto. En el ejemplo de la investigación, un
acero con 1,80 t CO2e/t reales frente a un valor por defecto de 2,50 significa
**656 EUR más en 2026 y 26.250 EUR más en 2034** por el mismo envío de 500
toneladas. Y con el criterio nuevo de los diez países peores, la brecha será
mayor.

Por eso, para un productor chileno o peruano con electricidad de bajo factor de
emisión, **calcular y verificar las emisiones reales casi siempre conviene**.

## El carbono ya pagado en Chile

El artículo 9 permite descontar el precio del carbono **efectivamente pagado** en
el país de origen por esas mismas emisiones. Chile tiene impuesto verde a fuentes
fijas, así que la pregunta es muy relevante.

Pero aquí hay que ser honesto: **la mecánica exacta de la deducción se remite a
un acto de ejecución que la investigación no pudo verificar, y si el gravamen
chileno será reconocido tampoco está confirmado.** Perú no tiene a la fecha un
precio explícito del carbono equiparable.

El motor lo trata como parámetro abierto y marca el resultado como estimación:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" europa cbam --sector acero --cantidad 500 --see 1.80 --anio 2026 --precio-certificado 75 --precio-carbono-origen 6
```

Lo que sí puedes decir con seguridad: **guarden la documentación de pago
trazable hasta la instalación y hasta la tonelada**. Si el descuento se
confirma, sin esos papeles no sirve de nada.

## Fechas

| Qué | Cuándo |
|---|---|
| Periodo definitivo | Desde el **1 de enero de 2026** |
| Venta de certificados | Desde el **1 de febrero de 2027** |
| Primera declaración anual (año 2026) | **30 de septiembre de 2027** |
| Entrega de certificados | Antes del 30 de septiembre de cada año |

> **Durante 2026 no se compran certificados.** Las importaciones de 2026 se
> declaran y se pagan en 2027. Es un año completo de margen para montar el
> sistema de datos: dilo, porque baja la ansiedad y ordena el plan.

## Cómo conversas esto

- Primero la calma: «usted no declara ni paga; su cliente sí, y necesita sus
  datos».
- Después el número: calcula el envío real de la empresa, no un ejemplo. Que vea
  su costo.
- Después la curva: el problema no es 2026, es 2030.
- Y el cierre: qué datos hay que levantar y quién en la planta los tiene.

## Límites honestos

- Esto es **orientación**, no asesoría aduanera. El código arancelario exacto de
  cada producto lo confirma el agente de aduana: la investigación no transcribió
  el Anexo I completo a nivel de subpartida.
- Los **valores por defecto del periodo definitivo no están verificados**: el
  motor no puede estimar el escenario "sin datos del proveedor". Hay que pedirlos
  al importador o a la Comisión.
- La **deducción por carbono pagado en origen** es un parámetro abierto, no la
  fórmula oficial.
- El precio del certificado es de mercado: no inventes cifras ni uses una vieja.
- Para **electricidad** el cálculo tiene reglas propias que la investigación no
  verificó; el motor lo dice y no calcula.
