---
name: ley-rep
description: Ley REP (Ley 20.920 de Chile) sobre responsabilidad extendida del productor: quién es productor, qué metas de recolección y valorización le exige cada decreto, cómo calcular si cumple y qué declarar en la Ventanilla Única del RETC. Úsala cuando mencionen envases, embalajes, neumáticos, aceites lubricantes, pilas, aparatos eléctricos o baterías; cuando digan que importan o venden productos envasados; o cuando pregunten por la Ley REP, el RETC, un sistema de gestión o una carta de la Superintendencia del Medio Ambiente.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Ley REP (Ley 20.920, Chile)

La **Responsabilidad Extendida del Productor** dice algo simple: quien pone un
producto en el mercado tiene que hacerse cargo —y pagar— de que sus residuos se
recojan y se reciclen. No basta con venderlo.

Aplica a **seis productos prioritarios** (art. 10):

| Producto | Decreto de metas | ¿Hay metas hoy? |
|---|---|---|
| Envases y embalajes | DS 12/2020 | Sí, desde el 16-09-2023 |
| Neumáticos | DS 8/2019 | Sí, desde el 20-01-2023 |
| Aceites lubricantes | DS 47/2023 | Desde el 01-01-2027 |
| Pilas | DS 22/2025 | Desde el 07-05-2028 |
| Aparatos eléctricos y electrónicos (AEE) | DS 22/2025 | Desde el 07-05-2028 |
| Baterías | — | No hay decreto todavía |

## Lo primero: ¿esta empresa es «productor»?

Mucha gente cree que esto es solo para fábricas. **No.** Según el art. 3 N° 21
de la ley, es productor quien:

- **vende por primera vez** en Chile un producto prioritario;
- lo vende **bajo marca propia** aunque se lo haya comprado a un tercero; o
- lo **importa para su propio uso profesional**.

**El importador casi siempre queda dentro.** Si la empresa trae mercadería de
afuera y la vende acá, es productor. Y en envases y embalajes es productor
**quien introduce al mercado el producto envasado**, aunque el envase se lo
haya comprado a otro: la panadería que vende pan en bolsa, el importador de
vino, la tienda que despacha por internet.

Preguntas que sirven para saber si aplica:

1. ¿Venden o importan algo **envasado o embalado**? → envases y embalajes.
2. ¿Importan o venden **neumáticos, aceites lubricantes, pilas, electrodomésticos,
   equipos electrónicos, paneles solares o baterías**?
3. ¿Ya están **inscritos en la Ventanilla Única del RETC**? ¿Adheridos a un
   **sistema de gestión**?

Para ver qué le toca a esta empresa en concreto:

```bash
python .claude/motor/esg.py rep obligaciones
python .claude/motor/esg.py rep obligaciones --producto envases
```

## Quién queda fuera

- **Microempresas** según la Ley 20.416: fuera de la REP de envases (art. 7 del
  DS 12/2020) y fuera de las metas de pilas y AEE (art. 6 del DS 22/2025) —
  aunque en pilas y AEE igual deben informar.
- Quien introduce **menos de 300 kg de envases al año**: no cumple metas, pero
  **sí debe informar** todos los años (arts. 7 y 10 del DS 12/2020).
- Quien introduce **66 litros o menos de aceites lubricantes al año** (art. 5
  del DS 47/2023).
- Los **envases reutilizables** no se cuentan como introducidos al mercado para
  las metas (art. 3), pero tienen su propio reporte.

## Las metas

Cada decreto tiene su **propia fórmula**. Nunca las mezcles y **nunca calcules
un porcentaje a mano**: pídeselo al motor.

```bash
python .claude/motor/esg.py rep metas --producto envases --anio 2026
python .claude/motor/esg.py rep metas --producto envases --anio 2026 --categoria domiciliario --material plastico
python .claude/motor/esg.py rep metas --producto neumaticos --anio 2026 --categoria A
```

Tres cosas que se equivocan casi siempre:

- **Neumáticos**: el denominador se multiplica por el **factor de desgaste**
  (0,84 categoría A; 0,75 categoría B). Sin ese factor parece incumplimiento
  algo que sí cumple.
- **Aceites lubricantes**: el denominador se multiplica por **(1 − 0,3)**,
  porque el 30 % del aceite se pierde durante su uso.
- **Pilas y AEE**: el denominador es el **promedio de los tres años anteriores**,
  no el año anterior.

Además, el **primer año** de metas se **prorratea** por meses (envases 2023:
3/12; pilas y AEE 2028: 7/12).

## Calcular si la empresa cumple

1. Crea la planilla y pídele que la llene con **toneladas por año**:

```bash
python .claude/motor/esg.py plantilla crear --tipo rep
```

2. Explícale que necesita **el año anterior también**: la meta de 2026 se
   calcula sobre lo que puso en el mercado en 2025 (y en pilas y AEE, sobre el
   promedio de 2025, 2026 y 2027).

3. Calcula:

```bash
python .claude/motor/esg.py rep calcular --anio 2026
python .claude/motor/esg.py rep calcular --anio 2026 --producto neumaticos
```

El resultado trae, por cada meta: toneladas puestas en el mercado, meta
aplicable, toneladas exigidas, toneladas gestionadas, brecha y estado (*cumple*,
*no cumple*, *sin meta*, *sin meta verificada* o *sin datos*).

## Qué se declara y cuándo

Todo se reporta en la **Ventanilla Única del RETC**: `https://portalvu.mma.gob.cl/`.

| Fecha | Qué |
|---|---|
| 30 de marzo | Declaración de residuos al SINADER (si el establecimiento genera más de 12 t al año) |
| 31 de mayo | Informe final del sistema de gestión por el año anterior |
| 30 de junio | Avisar el cambio de sistema de gestión para el año siguiente (envases) |
| 30 de septiembre | Informe de avance del sistema de gestión |
| **1 al 31 de octubre** | **Declaración Jurada Anual (DJA) del RETC** |
| Por convocatoria del MMA | Declaración anual de productos prioritarios |

Dos detalles que ahorran problemas:

- La **DJA la firma el Encargado del Establecimiento**, no un delegado ni el
  representante legal, y es **por establecimiento**, no por empresa. No admite
  corregir años anteriores.
- **Mientras las metas de un producto todavía no rigen** (aceites, pilas, AEE,
  baterías), igual hay que **declarar cada año las toneladas puestas en el
  mercado** (art. 2° transitorio de la Ley 20.920).

Un productor nuevo de envases tiene **4 meses** desde su primera venta para
inscribirse y adherir a un sistema de gestión. Los importadores de neumáticos
deben acreditar ante **Aduanas**, al cursar la importación, que pertenecen a un
sistema autorizado.

## Multas

Fiscaliza la **Superintendencia del Medio Ambiente** (art. 38). Las multas del
art. 40 de la Ley 20.920:

| Gravedad | Sanción |
|---|---|
| Gravísima | Multa de hasta **10.000 UTA** |
| Grave | Multa de hasta **5.000 UTA** |
| Leve | Amonestación por escrito o multa de hasta **1.000 UTA** |

El monto exacto lo fija la SMA caso a caso. **No estimes multas**: muestra el
rango y di que depende del procedimiento sancionatorio.

## Cómo conversas esto

- Parte por lo concreto: qué vende o importa, si está inscrita, si está en un
  sistema de gestión. Sin sistema de gestión no hay forma de cumplir.
- Si está en un **sistema colectivo**, normalmente es el sistema el que declara
  y acredita. Este cálculo sirve para **revisar lo que el sistema informa**, no
  para reemplazarlo.
- Cuando el motor diga *sin meta verificada*, dilo tal cual: hay un dato que no
  está confirmado y no se va a inventar.
- Recuerda que la valorización tiene reglas por producto: en envases **solo
  reciclaje material**; en neumáticos también recauchaje, coprocesamiento y
  valorización energética, pero al menos el 60 % debe ser reciclaje material o
  recauchaje.

## Límites honestos

- **La tabla de metas de aceites lubricantes (art. 21 del DS 47/2023) no está
  verificada**: en el Diario Oficial se publicó como imagen. El motor aplica la
  fórmula y muestra el porcentaje logrado, pero **no dice si se cumple**. Ese
  porcentaje hay que pedírselo al MMA o al sistema de gestión.
- **Baterías** no tiene decreto de metas: solo corre la obligación de declarar.
- **No hay una fecha reglamentaria fija** para la declaración anual del
  productor: el MMA la abre por convocatoria. Hay que mirar
  `portalvu.mma.gob.cl`.
- Las metas **regionales** de neumáticos, los puntos limpios y la recolección
  puerta a puerta son obligaciones de los **sistemas de gestión colectivos**, no
  del productor individual: el motor no las calcula.
- No puedes declarar nada por la empresa: eso lo hace ella en la Ventanilla
  Única con su clave.
- Esto es orientación de apoyo, **no asesoría legal**.
