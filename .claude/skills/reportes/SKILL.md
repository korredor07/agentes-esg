---
name: reportes
description: Preparar un reporte o memoria de sostenibilidad con un marco reconocido (GRI, NIIF S1/S2, NCG 461/519 de la CMF, ESRS, VSME). Úsala cuando pidan hacer un reporte de sostenibilidad, una memoria anual integrada, responder el cuestionario de un cliente o un banco, saber qué exige cada estándar, o cuando quieran comunicar logros ambientales sin caer en greenwashing.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Reportes de sostenibilidad

Un reporte de sostenibilidad es **contar de forma ordenada lo que la empresa ya
hace y ya mide**, siguiendo la estructura que pide quien va a leerlo. El motor
sabe qué contenidos exige cada marco, revisa cuáles se pueden llenar con los
datos que ya están en la carpeta y arma el borrador. **Lo que falta lo escribe
la empresa: eso no se inventa.**

Antes de partir, asegúrate de que exista la huella de carbono (skill
`huella-carbono`) y, si se puede, el diagnóstico (skill `diagnostico-esg`): son
los dos que más contenidos llenan solos.

## Elegir el marco: es la primera decisión

Pregunta **quién va a leer el reporte**. Esa respuesta decide el marco:

| Si quien lo pide es… | Usa | Por qué |
|---|---|---|
| Clientes, comunidad, trabajadores, público general | **GRI** | Mira el impacto de la empresa sobre las personas y el ambiente. Es el estándar voluntario más usado del mundo. |
| Inversionistas, bancos, aseguradoras, reguladores de valores | **NIIF S1 + NIIF S2** | Miran cómo la sostenibilidad afecta la plata de la empresa. S2 es la parte climática y se usa junto con S1. |
| La CMF de Chile (sociedad anónima abierta, banco, aseguradora, AGF, bolsa, emisor inscrito) | **NCG 461** y **NCG 519** | La memoria anual integrada. La NCG 519 no reemplaza a la 461: la modifica y suma NIIF S1/S2. |
| Un cliente europeo grande, una matriz europea o un banco de la UE | **VSME** (pyme) o **ESRS** (si está en el ámbito de la CSRD) | El VSME es la vía corta para responder cuestionarios; el ESRS es la norma completa europea. |

Cosas que conviene decir en palabras simples:

- **GRI** pregunta «qué efectos genera la empresa». **NIIF S1/S2** preguntan
  «qué le puede pasar a la empresa». **ESRS** pregunta las dos (eso es la
  *doble materialidad*).
- **GRI** se puede reportar «de conformidad con» (nueve requisitos, es el
  reporte completo) o «con referencia a» (tres requisitos). Para una pyme que
  parte, «con referencia a» es un primer paso honesto y mucho más barato.
- **En Chile**, la NCG 519 obliga a reportar bajo NIIF S1 y S2, y la **NCG 572
  de julio de 2026 corrió el plazo un año**: el primer reporte obligatorio es
  sobre el **ejercicio 2027**, publicado en 2028. Se puede adoptar antes de
  forma voluntaria, declarándolo de manera expresa.
- **El VSME no exige verificación de un tercero**: basta la autodeclaración de
  la pyme. Reportar el módulo básico (B1 a B11) es requisito para reportar el
  comprehensivo (C1 a C9).
- En la UE el umbral de la CSRD subió a más de **1.000 empleados y 450 millones
  de euros**. Una pyme de Chile o Perú casi nunca queda obligada: lo que sí le
  llega es el **cuestionario de su cliente europeo**, y para eso está el VSME.

Se puede usar más de un marco: comparten los mismos datos de base.

## Paso a paso con el motor

**1. Muestra los marcos y ayúdale a elegir.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte marcos
```

Para ver todo lo que exige uno en particular:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte marcos --marco "NIIF S2"
```

**2. Revisa qué puede reportar hoy.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte cobertura --marco GRI --periodo 2025
```

Lee la carpeta de la empresa (`resultados/huella_*.json`, `datos/personas.xlsx`,
`datos/consumos.xlsx`, `datos/alcance3.xlsx`, `datos/sitios.xlsx`,
`seguimiento/diagnostico.json` y `seguimiento/metas.json`) y devuelve tres
cosas: el porcentaje de cobertura, lo que ya se puede reportar y lo que falta.

Explícaselo así, sin tecnicismos:

1. «De los N contenidos que pide GRI, hoy puedes responder X con datos que ya
   tienes.»
2. «Estos tres datos son los que más te desbloquean» (viene en
   `datos_que_mas_suman`).
3. «El resto son textos que tienes que escribir tú: ningún cálculo los puede
   inventar.»

Un porcentaje bajo en la primera vuelta es **normal**. No lo dramatices.

**3. Genera el índice de contenidos.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte indice --marco GRI
```

Deja un HTML en `reportes/` que marca cada contenido como **cubierto**
(el dato ya está), **parcial** (falta una parte) o **pendiente** (falta el dato
o falta escribirlo). Sirve para repartir tareas dentro de la empresa y, en GRI,
es el punto de partida del índice de contenidos que exige el estándar.

**4. Genera el borrador en Word.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte borrador --marco GRI --periodo 2025
```

Queda en `reportes/` como `.docx`: se abre en Word y se edita. Las cifras que
existen ya vienen puestas; **lo que está entre corchetes lo escribe la empresa**.

Si el borrador queda muy largo (GRI tiene muchos contenidos temáticos), acótalo:

```bash
# solo lo que se reporta siempre (universales)
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte borrador --marco GRI --solo-obligatorios

# solo los temas materiales que eligió la empresa
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" reporte borrador --marco GRI --temas 302,305,403,405
```

**5. Acompáñala a completarlo.** No le entregues el archivo y te vayas. Toma los
corchetes de a tres o cuatro, pregúntale en lenguaje cotidiano y ofrécele
redactar tú el texto con lo que te cuente. Si no sabe algo, se deja pendiente y
se anota como brecha: **es mejor una omisión explicada que un dato inventado**.

**6. Respalda las cifras** antes de que el reporte salga de la empresa:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia registrar --archivo datos/consumos.xlsx --descripcion "Consumos 2025 del reporte"
```

## Greenwashing: lo que no se puede decir

Esta es la parte donde una empresa honesta se mete en problemas por escribir de
más. Decir de más hoy es un **riesgo legal**, no solo de reputación.

**Unión Europea — Directiva (UE) 2024/825, aplicable desde el 27 de septiembre
de 2026.** Prohíbe *en toda circunstancia*, entre otras:

- **Alegaciones genéricas** («ecológico», «verde», «respetuoso con el medio
  ambiente») cuando no hay un desempeño ambiental excelente y reconocido que las
  respalde.
- Alegar sobre **todo el producto o toda la empresa** cuando la evidencia cubre
  solo un aspecto, una planta o una línea.
- Afirmar impacto **neutro, reducido o positivo en emisiones basándose solo en
  compensación** (comprar bonos de carbono).
- Exhibir **sellos de sostenibilidad** que no se apoyan en un sistema de
  certificación ni fueron establecidos por una autoridad pública.
- Presentar como mérito algo que **la ley ya obliga** a hacer.

Además, evaluadas caso a caso: las **promesas a futuro** (tipo «seremos neutros
en 2030») solo se sostienen si hay compromisos claros y públicos, un **plan de
implementación detallado y realista** y **verificación periódica de un tercero
experto independiente**; y las **comparaciones** obligan a publicar el método,
qué se comparó y cómo se mantiene al día.

**Chile — Ley 19.496 del consumidor.** No hace falta una ley nueva: la
publicidad falsa o engañosa se sanciona con hasta **1.500 UTM**, y hasta
**2.250 UTM** cuando incide sobre la salud, la seguridad o **el medio ambiente**
(artículo 24). Ese es el argumento más fuerte para pedirle a una empresa chilena
que fundamente lo que publica.

**Checklist de seis puntos** (viene del Green Claims Code de la autoridad de
competencia británica y es el más fácil de explicar): la afirmación debe ser
veraz y exacta, clara y sin ambigüedad, no omitir información importante, hacer
comparaciones justas, considerar el ciclo de vida completo y estar fundamentada
en evidencia actualizada.

**Cómo traducirlo en la práctica**, cuando la persona quiera escribir algo:

| En vez de… | Escribe… |
|---|---|
| «Somos una empresa sostenible» | «Redujimos 12% nuestras emisiones entre 2024 y 2025, medidas según GHG Protocol» |
| «Producto ecológico» | «Envase con 40% de material reciclado, verificado con la factura del proveedor» |
| «Carbono neutral» (con bonos) | «Medimos nuestra huella, redujimos X toneladas y compensamos el resto con créditos de [proyecto]» |
| «Seremos neutros en 2030» | Solo si hay plan con hitos, responsable y verificación externa; si no, no se publica |

Cuando revises un texto de la empresa, señala la frase exacta y ofrece la
alternativa medible. No la asustes: la salida casi siempre es decir menos y
mostrar el dato.

## Lo que el motor NO trae, y por qué

Dilo si preguntan. La investigación de respaldo dejó estos puntos sin verificar
y **no se incluyeron para no inventar**:

- **Métricas y códigos de SASB por industria** (los que usa el Apéndice B de
  NIIF S2). Hay que tomarlos del estándar de la industria, y además su uso
  dentro de un producto requiere licencia de la Fundación IFRS.
- **Los títulos de GRI 304** (biodiversidad 2016), que además fue sustituido por
  GRI 101: Biodiversity 2024.
- **Los códigos individuales de las divulgaciones de GRI 2** más allá de 2-1 a
  2-5. El motor las agrupa por sección y lo dice en sus notas: toma los códigos
  exactos del estándar oficial.
- **Perú**: la oficialización de NIIF S1 y S2 por el Consejo Normativo de
  Contabilidad y la obligatoriedad desde 2029 para empresas con ingresos sobre
  2.300 UIT son datos de fuente secundaria. No los afirmes como seguros.
- **La Directiva europea de Alegaciones Ecológicas** (*Green Claims*) **no está
  en vigor**: el procedimiento figura «en curso». No digas que fue aprobada ni
  que fue retirada. Lo aplicable es la Directiva (UE) 2024/825.
- **ISO 14021 e ISO 14068-1** (autodeclaraciones y carbono neutralidad): no se
  pudieron verificar en la fuente oficial. Ojo además con esto: una
  certificación de «carbono neutral» **no protege** frente a la prohibición
  europea si la neutralidad descansa en compensaciones.
- **Guías del SERNAC sobre alegaciones ambientales**: no se encontró ninguna. No
  afirmes que existen.

Si la empresa necesita alguno de estos puntos, ofrécele buscarlo en la fuente
oficial con el agente `agente-investigador` antes de usarlo.

## La advertencia que siempre va

**El borrador no es un reporte final ni una verificación.** Es un punto de
partida armado con los datos de esta carpeta. Antes de publicarlo hay que
completarlo, revisarlo con quien corresponda en la empresa y respaldar cada
cifra con su evidencia. Si el reporte se va a presentar a un regulador, a una
auditoría o a un cliente que lo va a auditar, los datos deben verificarse y el
texto lo debe aprobar quien responde legalmente por él.

## Cierre

Termina siempre diciendo: qué marco se usó, qué porcentaje quedó cubierto con
datos reales, dónde quedó el archivo, qué le falta a la empresa por escribir y
cuál es el siguiente paso concreto.
