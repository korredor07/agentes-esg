---
name: doble-materialidad
description: Decidir qué asuntos ESG son importantes para la empresa, mirando por un lado lo que la empresa le hace al mundo y por otro lo que el mundo le puede hacer a la empresa. Úsala cuando pregunten qué temas reportar, qué priorizar, cuando un cliente europeo o un banco pida un análisis de materialidad o una matriz, cuando preparen un reporte de sostenibilidad, o cuando no sepan por dónde empezar y necesiten acotar el trabajo.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Doble materialidad

Sirve para responder una sola pregunta: **¿de todo lo que existe en
sostenibilidad, qué le importa de verdad a esta empresa?** Sin esto, una pyme
termina midiendo cosas que no le mueven la aguja y dejando fuera lo que sí.

## 1. Qué es, en dos preguntas

| Mirada | La pregunta | Ejemplo en una planta de alimentos |
|---|---|---|
| **De adentro hacia afuera** (materialidad de impacto) | ¿Qué le hace la empresa al mundo, con su operación y su cadena? | El agua que saca de una cuenca con escasez |
| **De afuera hacia adentro** (materialidad financiera) | ¿Qué del mundo puede afectar la plata de la empresa? | Que le restrinjan el agua y tenga que parar la planta |

Reglas que tienes que saber decir de memoria:

- Un asunto es material si lo es **por cualquiera de las dos vías**: basta con
  una. No se necesitan las dos.
- Hay que mirar **toda la cadena de valor**, no solo lo que pasa dentro del
  cerco: proveedores, transporte, uso del producto.
- Las dos miradas están conectadas: **el impacto de hoy es el riesgo financiero
  de mañana** (por regulación, por reputación, por un cliente que se va).

Contraste rápido, por si preguntan por marcos:

| Marco | Qué materialidad mira |
|---|---|
| GRI | Solo la de impacto |
| NIIF S1 / S2 (ISSB) | Solo la financiera |
| ESRS (Unión Europea) | **Las dos** |

## 2. Por qué la piden los marcos europeos

La doble materialidad es la regla que decide **qué** reporta una empresa bajo
las normas europeas de sostenibilidad (ESRS). El resultado determina qué normas
temáticas se aplican; las divulgaciones generales se reportan siempre, salga lo
que salga de la evaluación.

Lo que le importa a una empresa de Chile o Perú:

- La directiva europea de reporte fue **acotada en 2026** (Directiva (UE)
  2026/470, «Ómnibus I»): quedan en ámbito las empresas que superan
  **450 millones de euros de facturación y 1.000 empleados**, para ejercicios
  que empiecen desde el **1 de enero de 2027**. Tu empresa casi con seguridad
  **no** está obligada.
- Pero sí le llega **por rebote**: su cliente europeo que sí está obligado le va
  a pedir datos. Esa misma reforma creó un **tope**: a una empresa de menos de
  1.000 empleados no se le puede exigir más de lo que pide la norma voluntaria
  para pymes (VSME), y tiene derecho a rechazar lo que exceda ese tope.
- Hacer la materialidad **antes** de que llegue el cuestionario cambia la
  conversación: se responde lo que corresponde y se deja fuera el resto con
  argumento.

Dilo así: «esto no es una obligación tuya, es la forma de contestarle a tu
cliente sin terminar haciendo el trabajo de una multinacional».

## 3. Paso a paso con el motor

### Proponer la lista

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" materialidad asuntos
```

Entrega los asuntos comunes más los propios del rubro de la empresa (los detecta
del sector del perfil). **No la leas entera de corrido.** Muéstrala agrupada por
tema (ambiental, social, gobernanza) y haz dos preguntas:

> «¿Hay algo aquí que no tenga nada que ver con ustedes?»
> «¿Falta algo que a ustedes les quite el sueño y no esté en la lista?»

Lo que agreguen se registra igual, con su nombre tal cual lo dijeron.

### Evaluar de a un asunto

Seis preguntas por asunto. Tradúcelas así:

| Criterio | Cómo preguntarlo | 1 | 5 |
|---|---|---|---|
| Escala | «Cuando pasa, ¿qué tan grave es?» | Apenas se nota | Daño grave a la salud, al ambiente o a los derechos de alguien |
| Alcance | «¿A cuánta gente o a qué superficie alcanza?» | A unos pocos | A toda la comunidad o al territorio |
| Irremediabilidad | «Si pasa, ¿se puede reparar?» | Se arregla rápido | No tiene vuelta atrás |
| Probabilidad del impacto | «¿Cada cuánto ocurre?» | Sería muy raro | Ya está pasando |
| Magnitud financiera | «Si se les viene encima, ¿cuánta plata está en juego?» | No mueve la aguja | Pone en riesgo el negocio |
| Probabilidad financiera | «¿Qué tan probable es que eso pase en los próximos años?» | Muy poco probable | Prácticamente seguro |

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" materialidad registrar --asunto agua --escala 5 --alcance 4 --irremediabilidad 4 --probabilidad-impacto 5 --magnitud-financiera 4 --probabilidad-financiera 4 --nota "La planta está en zona declarada de escasez hídrica"
```

Se puede registrar en dos tandas (primero el impacto, después lo financiero):
el asunto queda pendiente hasta que estén las seis notas y **no se rellena con
supuestos**. Si el asunto ya está ocurriendo hoy, la probabilidad es 5.

### Calcular y mirar el resultado

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" materialidad evaluar
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" materialidad evaluar --umbral 3,5
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" materialidad informe
```

El informe deja `reportes/doble-materialidad.html` con la matriz dibujada, la
tabla ordenada y la lista de asuntos materiales.

## 4. La consulta a los grupos de interés

Una matriz hecha entre dos personas en una oficina no resiste ninguna revisión.
Hay que preguntarle a quienes están afectados. Para una pyme esto es **modesto y
factible**, no un estudio de mercado:

1. **Lista quiénes son**: trabajadores, clientes, proveedores clave, vecinos,
   banco, autoridad local. Cinco o seis grupos bastan.
2. **Elige a poca gente pero bien elegida**: 3 a 5 personas por grupo, las que
   tengan algo real que decir.
3. **Pregunta poco y concreto**: «de esta lista, ¿cuáles son los tres temas que
   más les afectan a ustedes?» y «¿hay algo que nos falta ver?». Una reunión de
   media hora o un formulario de diez líneas.
4. **Anota quién dijo qué y cuándo**. Eso es la evidencia de la consulta.
5. **Vuelve a contarles el resultado.** Es lo que hace que la próxima vez
   contesten.

Deja el respaldo guardado:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia registrar --archivo datos/consulta-grupos-interes.xlsx --descripcion "Respuestas de la consulta de materialidad 2026" --responsable "Nombre de quien la hizo"
```

Un verificador externo va a pedir exactamente esto: método usado, a quién se
consultó, con qué evidencia, qué umbral se aplicó y quién aprobó el resultado.

## 5. Cómo se calcula (dilo si preguntan)

Las dos escalas van de 1 a 5:

- **Impacto**: la gravedad es el promedio de escala, alcance e
  irremediabilidad; el puntaje es 70 % gravedad más 30 % probabilidad. En los
  asuntos de derechos humanos **la gravedad manda**: el puntaje nunca baja de
  ella aunque la probabilidad sea baja.
- **Financiero**: magnitud por probabilidad, devuelto a la escala de 1 a 5 con
  la raíz cuadrada.
- **Material** es el asunto que llega al umbral en cualquiera de los dos ejes.

El umbral por defecto es 3,0, **pero es una decisión de la empresa**, no del
motor ni del estándar: lo que se exige es tener un método explicado y usarlo
igual todos los años. Si salen quince asuntos materiales, el umbral está
demasiado bajo para el tamaño del equipo; súbelo y déjalo escrito.

## 6. Qué se hace después con el resultado

Los asuntos materiales son la agenda de trabajo del año:

| Si salió material… | Sigue con la skill |
|---|---|
| Cambio climático o energía | `huella-carbono`, después `metas-net-zero` |
| Cualquier asunto con obligación legal detrás | `brechas-cumplimiento` |
| Acoso o violencia laboral (en Chile) | `ley-karin` |
| Lo que la empresa va a comunicar en público | `greenwashing` |
| Todo lo que haya que respaldar ante un tercero | `evidencias`, `aseguramiento` |

## Cuidados

- **No es asesoría legal ni un dictamen.** Es una decisión de gestión de la
  empresa, ordenada con un método.
- **No pongas tú las notas.** Si la persona duda, deja el asunto pendiente y
  vuelve a preguntarlo; un asunto sin evaluar es mejor que uno inventado.
- Si un asunto toca **derechos humanos** (acoso, trabajo en la cadena,
  comunidades, seguridad), avisa que ahí la gravedad pesa más que la
  probabilidad: no se descarta porque «casi nunca pasa».
- La matriz **se revisa al menos una vez al año** y cada vez que cambie algo
  grande: una planta nueva, un mercado nuevo, un accidente, una ley nueva.
- No presentes la matriz como resultado del motor: preséntala como **la
  decisión de la empresa**, que el motor solo ordenó y dibujó.
