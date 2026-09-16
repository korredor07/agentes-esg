---
name: brechas-cumplimiento
description: Identificar qué normativa ambiental, social y de gobernanza le aplica a la empresa, con sus plazos y riesgos, y qué le falta para cumplir. Úsala cuando pregunten qué leyes les aplican, si están cumpliendo, qué arriesgan, cuando les llegó una carta o fiscalización, o cuando un cliente les exige algo y no saben si corresponde.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Qué normas le aplican y qué falta

La pregunta más común de una pyme es «¿esto me aplica a mí?». Se responde con
el perfil de la empresa y unas pocas preguntas concretas.

## 1. Preguntar lo justo

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" cumplimiento preguntas
```

Son preguntas de sí o no, en lenguaje cotidiano. **Hazlas de a una** y acepta
«no sé» como respuesta válida (queda pendiente y se retoma después).

Guarda cada respuesta apenas la recibas:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" cumplimiento responder --clave pone_productos_prioritarios --respuesta si
```

Cómo traducir las preguntas al lenguaje de la persona:

| Pregunta técnica | Cómo preguntarla |
|---|---|
| ¿Pone productos prioritarios en el mercado? | «¿Venden algo envasado, importan productos, o venden neumáticos, aceites, aparatos eléctricos o pilas?» |
| ¿Tiene fuentes fijas? | «¿Tienen caldera, horno o generador?» |
| ¿Descarga riles? | «¿El agua del proceso se va a un río, al mar o al alcantarillado?» |
| ¿Supervisada por la CMF? | «¿La empresa está en la bolsa o es sociedad anónima abierta?» |
| ¿Exporta bienes CBAM? | «¿Le venden a Europa acero, aluminio, cemento, fertilizantes o hidrógeno?» |

## 2. Revisar

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" cumplimiento revisar
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" cumplimiento informe
```

Entrega tres grupos:

- **Le aplican**: con lo que exige cada norma, sus plazos y qué arriesga.
- **Por confirmar**: falta un dato para decidir. Pregúntalo.
- **No le aplican**: sirve para tranquilizar y para acotar el trabajo.

## 3. Cómo se lo presentas

Empieza por lo de **riesgo alto** y máximo tres normas por vez. Para cada una:

1. Qué es, en una frase sin jerga.
2. Por qué le aplica a **su** empresa (usa el motivo que entrega el motor).
3. Qué hay que tener (lo concreto, no la teoría).
4. Cuál es el siguiente paso, con la skill que corresponde.

Ejemplo de tono:

> «La Ley Karin le aplica porque tiene trabajadores: toda empresa en Chile debe
> tener un protocolo de prevención escrito y entregado al personal. Si llega una
> denuncia, los plazos son cortos y perentorios. ¿Quiere que preparemos el
> protocolo?»

## 4. Dejar constancia y seguimiento

Las brechas que se confirmen conviene registrarlas en el diagnóstico (skill
`diagnostico-esg`) con responsable y fecha: así aparecen en el tablero y no se
pierden.

## Límites que debes decir siempre

- Esto es **orientación**, no asesoría legal. La revisión final la hace un
  abogado o la asesoría de la empresa.
- La lista cubre las normas más frecuentes de Chile, Perú y las exigencias
  europeas para exportadores; **no es exhaustiva**. Sectores regulados (minería,
  salud, alimentos, financiero, transporte) tienen normativa adicional propia.
- Los montos de multas dependen del caso y del tamaño de la empresa: no
  inventes cifras exactas.
- Si la empresa ya recibió una notificación o fiscalización, lo urgente es
  responderla dentro de plazo: eso va antes que cualquier diagnóstico.
