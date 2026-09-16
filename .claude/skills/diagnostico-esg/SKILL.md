---
name: diagnostico-esg
description: Diagnóstico ESG de la empresa: puntaje de madurez, brechas priorizadas por riesgo y plan de cierre. Úsala cuando pregunten cómo están en sostenibilidad, qué les falta, por dónde partir, cuando quieran una radiografía general o preparar una revisión de un cliente, banco o auditoría.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Diagnóstico ESG

Responde tres preguntas: **cómo estamos**, **qué nos falta** y **por dónde
partir**. Mitad se calcula solo con los datos de la carpeta; la otra mitad la
respondes tú conversando con la persona.

## 1. Primera evaluación

```bash
python .claude/motor/esg.py diagnostico evaluar
```

Devuelve el puntaje general, el de cada dimensión (ambiental, social,
gobernanza), el porcentaje «listo para auditoría» y las brechas ordenadas por
riesgo. Preséntalo en **cuatro líneas**, sin tecnicismos, y dile de inmediato
que el puntaje **no es una calificación de mercado ni una certificación**: es
una autoevaluación con lo que hay en la carpeta.

## 2. Completar lo que falta preguntando

```bash
python .claude/motor/esg.py diagnostico preguntas
```

Trae los indicadores sin responder, ordenados por importancia. **Pregunta de a
uno**, traduciendo a lenguaje cotidiano y ofreciendo las opciones:

> «¿Tienen un protocolo escrito para prevenir el acoso laboral, entregado a los
> trabajadores? Puede ser: sí lo tenemos, lo tenemos a medias, no lo tenemos, o
> no sé.»

Traducción de las respuestas: sí → `cumple`; a medias o desactualizado →
`parcial`; no → `no_cumple`; no corresponde al giro → `no_aplica`. Si dice «no
sé», déjalo sin responder y anótalo como algo por averiguar.

Guarda cada respuesta apenas la recibas:

```bash
python .claude/motor/esg.py diagnostico responder --indicador soc-canal --estado no_cumple --nota "Nunca se implementó"
```

El identificador (`soc-canal`, `amb-huella`, …) sale de la lista que devuelve
`diagnostico evaluar`: **no lo inventes**. La lista ya viene filtrada por el
país de la empresa, así que a una empresa peruana no le aparecen indicadores
que solo existen en Chile (como `soc-karin`, de la Ley Karin).

No hagas todas las preguntas de una vez. Tres o cuatro por conversación es
suficiente; el diagnóstico se puede retomar cuando quieran.

## 3. Priorizar y comprometer

Después de responder, vuelve a evaluar y muestra **las tres brechas más
urgentes**, con esta estructura para cada una:

1. Qué falta (en una línea).
2. Por qué importa (riesgo concreto: multa, pérdida de cliente, accidente).
3. Qué hacer primero (un paso, no un proyecto).

Si la persona se compromete con alguna, regístralo:

```bash
python .claude/motor/esg.py diagnostico brecha --indicador soc-canal --seguimiento reconocida --responsable "Jefa de personas" --fecha-compromiso 2026-11-30
```

Estados de seguimiento: `abierta`, `reconocida` (la vio y la asumió),
`pospuesta` (decidió dejarla para después, con razón anotada), `resuelta`.

## 4. Informe

```bash
python .claude/motor/esg.py diagnostico informe
```

Deja `reportes/diagnostico-esg.html`: sirve para mostrar a la gerencia o al
directorio. Para una vista más general, usa la skill `tablero`.

## Cómo se calcula (dilo si preguntan)

Cada indicador tiene un peso (1 a 3) y un estado. Cumple suma todo su peso,
parcial la mitad, no cumple o sin datos no suman; los que no aplican salen del
cálculo. El puntaje de cada dimensión es el porcentaje logrado y el general es
el promedio de las tres. La prioridad de una brecha es su peso por el tipo de
riesgo: legal 3, reputacional 2, gestión 1.

## Cuidados

- No dramatices ni minimices: un puntaje bajo en una empresa que recién parte es
  **normal**, y así hay que decirlo.
- No prometas que cerrar brechas evita multas: reduce riesgo, no lo elimina.
- Si detectas algo con plazo legal encima (una denuncia de acoso, una
  declaración vencida), **eso pasa al frente de la fila** y se trata con la
  skill correspondiente ese mismo día.
