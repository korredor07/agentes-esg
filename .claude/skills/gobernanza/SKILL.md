---
name: gobernanza
description: Modelo de prevención de delitos y gobierno corporativo en Chile (Ley 20.393 reformada por la Ley 21.595 de delitos económicos, y NCG 461/519 de la CMF). Úsala cuando pregunten por el modelo de prevención de delitos, compliance, canal de denuncias, código de ética, conflictos de interés, responsabilidad penal de la empresa, encargado de prevención, o cuando un cliente grande, un banco o una licitación les pida "su programa de cumplimiento".
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Modelo de prevención de delitos y gobierno corporativo

## Explícalo así la primera vez

> «En Chile, una empresa —no solo sus dueños o gerentes— puede ser condenada
> penalmente por delitos cometidos en el marco de su actividad. La defensa
> central es tener un **modelo de prevención de delitos**: un conjunto de reglas
> escritas, un canal para denunciar, alguien a cargo y evidencia de que eso se
> usa de verdad.»

Lo que cambió con la **Ley 21.595 de Delitos Económicos** (publicada el 17 de
agosto de 2023), que reescribió la **Ley 20.393**:

- **Se amplió muchísimo la lista de delitos** por los que responde la empresa,
  incluidos los **delitos ambientales** que la misma ley incorporó al Código
  Penal (vertimientos sin evaluación ambiental, incumplir normas de emisión,
  afectación grave de humedales y áreas protegidas).
- **Ya no se exige** que el delito se haya cometido "en interés o provecho" de
  la empresa. Hoy basta que lo cometa alguien con un cargo, función o posición
  en ella —o que gestione asuntos suyos ante terceros— **y** que el hecho se
  haya visto favorecido o facilitado por **la falta de implementación efectiva**
  de un modelo adecuado.
- **No hay umbral de tamaño.** El artículo 2° alcanza a toda persona jurídica de
  derecho privado. Una SpA de ocho personas está incluida.

> **Dato que debes advertir siempre:** la **fecha exacta en que entraron en
> vigencia** las modificaciones de la Ley 21.595 a la Ley 20.393 **no está
> confirmada en fuente oficial** en la investigación de este proyecto. Circula
> el 1 de septiembre de 2024, pero viene de fuentes secundarias. Si la fecha
> importa para el caso (por ejemplo, para saber si un hecho de 2024 queda
> cubierto), dile que **eso lo tiene que confirmar su asesoría jurídica leyendo
> el artículo transitorio**. No la afirmes tú.

## Lo que la ley pide que tenga el modelo (art. 4° de la Ley 20.393)

Son cuatro piezas, y conviene nombrarlas siempre en este orden:

1. **Identificar los riesgos**: qué actividades o procesos de *esta* empresa
   implican riesgo de conducta delictiva.
2. **Protocolos y procedimientos** para prevenir y detectar, que incluyan
   **canales seguros de denuncia** y **sanciones internas** para quien incumpla.
3. **Uno o más responsables** de aplicar esos protocolos, con **independencia**,
   facultades efectivas de dirección y supervisión, **acceso directo a la
   administración** y **recursos y medios** suficientes.
4. **Evaluaciones periódicas por terceros independientes** y un mecanismo de
   actualización.

Y la frase que lo cambia todo para una pyme: la ley exige esto **"en la medida
exigible a su objeto social, giro, tamaño, complejidad, recursos y a las
actividades que desarrolle"**. Es proporcional. Una pyme no necesita el mismo
despliegue que un banco, pero sí necesita dejar escrito **por qué ese alcance es
el exigible a su realidad**.

## Cómo trabajas esto

### 1. Revisar dónde está parada la empresa

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" gobernanza revisar --empresa mi-empresa
```

Devuelve el cuestionario guiado (19 preguntas repartidas en políticas, canal de
denuncias, encargado, capacitación, supervisión y gobierno corporativo), el
avance por bloque y las brechas ordenadas por riesgo.

**Haz las preguntas de a una y con las palabras de la persona.** El motor
entrega la versión conversacional en `preguntas_pendientes` → `pregunta`.
Ejemplos de cómo suenan:

| Lo técnico | Cómo se pregunta |
|---|---|
| Identificación de riesgos delictivos | «¿Han revisado alguna vez en qué parte del negocio alguien podría hacer algo indebido: compras, permisos, residuos, pagos?» |
| Canal seguro de denuncias | «Si alguien quiere denunciar algo sin que se sepa quién fue, ¿por dónde lo hace?» |
| Encargado de prevención | «¿Hay alguien con nombre y apellido a cargo de que esto funcione?» |
| Evaluación por tercero independiente | «¿Alguien de afuera lo ha revisado, aunque sea su contador o su abogado?» |

Guarda cada respuesta apenas la recibas:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" gobernanza responder --pregunta canal-denuncias --estado parcial --nota "Existe un correo pero nadie lo sabe"
```

Estados válidos: `cumple`, `parcial`, `no_cumple`, `no_aplica`. **`parcial` es la
respuesta más común y más honesta**: existe algo, pero sin difundir, sin firmar o
sin registro. Acepta «no sé» dejando la pregunta sin responder.

Las dos preguntas de la CMF (`memoria-cmf` y `seleccion-directores`) solo aplican
a entidades supervisadas. Si la empresa no lo es, respóndelas `no_aplica` y
sigue.

### 2. Entregar los borradores

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" gobernanza documento --tipo codigo-etica
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" gobernanza documento --tipo politica-canal-denuncias
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" gobernanza documento --tipo matriz-riesgos-delitos
```

Son **borradores con la estructura que pide la ley**, con todo lo propio de la
empresa entre corchetes. Dilo con esas palabras: no son documentos listos para
firmar, y el paso siguiente es completarlos y revisarlos con la asesoría
jurídica.

### 3. Dejar el informe

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" gobernanza informe
```

HTML que se abre con doble clic y se imprime a PDF (Ctrl+P).

## Una pyme puede hacer esto sin gastar una fortuna

Cuando pregunten «¿esto no es carísimo?», la respuesta honesta es que **el costo
está en el tiempo, no en la consultoría**. Un camino realista, en orden:

1. **Una reunión de dos horas** con quien conoce la operación para llenar la
   matriz de riesgos. Se parte por los tres procesos donde de verdad podría
   pasar algo: compras y pagos, permisos y trámites ante la autoridad, y manejo
   de residuos o emisiones.
2. **Código de ética corto**, de dos o tres páginas, entregado con firma de
   recepción. Un código de 40 páginas que nadie lee no acredita nada.
3. **Canal de denuncias barato**: un correo dedicado con acceso restringido a
   una o dos personas basta. Lo caro no es la herramienta: es que nadie sepa que
   existe. Difúndelo en la inducción y una vez al año.
4. **Encargado de prevención con dedicación parcial**. Puede ser quien lleva
   administración o finanzas, siempre que quede por escrito que **reporta
   directo** a la gerencia o al directorio y que tiene horas asignadas. Ojo con
   el conflicto: no conviene que sea la misma persona que decide las compras.
5. **Sanciones internas en el reglamento interno** y en los contratos. Es un
   párrafo, no un proyecto.
6. **Evaluación por un tercero proporcional**: el contador externo o el abogado
   de la empresa revisando una vez al año, con un informe de dos páginas
   fechado, cumple la lógica del art. 4° N°4 para una empresa pequeña.
7. **Evidencia**: actas, listas de asistencia firmadas, correos. La ley no pide
   tener el documento, pide que el modelo esté **implementado de manera
   efectiva**. Registra los respaldos con la skill `evidencias`.

Insiste en un punto: **un modelo escrito y guardado en un cajón es peor que
nada**, porque muestra que se conocía el riesgo y no se hizo seguimiento.

## Si la empresa es supervisada por la CMF

Aplica además la **NCG 461** (12 de noviembre de 2021), que convirtió la Memoria
Anual en un reporte integrado. Entre sus ocho áreas de contenido está
**gobierno corporativo**: composición y diversidad del directorio, comités,
política de selección de directores, gestión de riesgos, y ética y cumplimiento.

La **NCG 519** (29 de octubre de 2024) agregó dos divulgaciones: la **política de
cuota de género en el directorio** y la descripción del **proceso de selección de
directores**. También adoptó los estándares **NIIF S1 y S2**, cuyo plazo fue
ampliado un año por la **NCG 572** (27 de julio de 2026): el primer ejercicio
obligatorio es **2027, reportado en 2028**, con invitación a reportar de forma
voluntaria el ejercicio 2026 durante 2027.

Quedan fuera del reporte integrado completo las entidades cuyo **promedio de
activos consolidados de los dos últimos ejercicios sea inferior a UF 1.000.000**;
esas presentan un reporte simplificado.

Para el detalle del reporte en sí, deriva a la skill `reportes`.

## Cómo conversas esto

- **No asustes.** La reacción típica es «¿me pueden meter preso?». Aclara que
  esto es responsabilidad **de la empresa** (multas, inhabilidades para
  contratar con el Estado, pérdida de beneficios fiscales y, en casos graves,
  disolución), distinta de la responsabilidad personal de quien comete el
  delito.
- **No cuantifiques.** Las multas se expresan en días-multa con rangos legales;
  el monto concreto lo fija un tribunal. No inventes cifras ni ejemplos
  numéricos.
- **Conecta con lo que ya hicieron.** Si tienen protocolo de Ley Karin, ya
  tienen media política de canal de denuncias. Si tienen matriz de riesgos
  ambientales, ya tienen parte de la matriz de delitos.
- **Aterriza el beneficio inmediato**: los clientes grandes, los bancos y las
  licitaciones piden el código de ética y el canal de denuncias. Esto sirve para
  vender, no solo para defenderse.

## Límites honestos

- Esto es **orientación de gestión, no asesoría legal** y **no certifica** el
  modelo. La revisión final la hace un abogado.
- El motor **no evalúa si el modelo es "adecuado"** en el sentido del art. 4°:
  eso lo determina un tribunal caso a caso. Lo que mide es cuánto de la
  estructura exigida está hecho y documentado.
- La **fecha de entrada en vigencia de la Ley 21.595 está sin verificar**: dilo
  cada vez que aparezca.
- El listado de delitos es extenso y no está reproducido aquí. Si preguntan por
  un delito específico, di que hay que revisar el catálogo de los arts. 1° a 4°
  de la Ley 21.595 con la asesoría jurídica, en vez de improvisar.
- Para **Perú y otros países** existe legislación propia sobre responsabilidad
  de las personas jurídicas que **no está verificada en este proyecto**. Si la
  empresa no es chilena, dilo y recomienda asesoría local.
