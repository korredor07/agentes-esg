---
name: consultar-datos
description: Responder preguntas sobre los datos cargados de la empresa y revisar si hay datos raros o meses faltantes. Úsala cuando pregunten cuánto consumieron, cuánto gastaron, qué mes fue peor, cuánto subió algo, si falta información, o pidan revisar la calidad de los datos antes de calcular.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Consultar los datos de la empresa

Las respuestas salen **de los archivos**, nunca de tu memoria ni de una
estimación tuya.

## Qué hay cargado

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" datos resumen
```

Muestra los archivos, sus hojas, cuántas filas tienen y cuándo se actualizaron,
además de los resultados y reportes ya generados.

## Leer una planilla

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" datos leer --archivo consumos.xlsx
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" datos leer --archivo alcance3.xlsx --hoja "Alcance 3" --limite 50
```

Con esas filas puedes responder preguntas como «¿cuánta electricidad usamos en
marzo?» o «¿cuál sitio consume más diésel?». Suma y compara **con cuidado**: si
la operación es grande, pide el cálculo al motor (`huella calcular`) en vez de
sumar decenas de filas a mano.

Los resultados ya calculados están en `resultados/huella_*.json`: ahí tienes
totales por alcance, por sitio, por recurso y por periodo, listos para citar.

## Revisar si los datos tienen sentido

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" datos anomalias
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" datos anomalias --umbral 80
```

Detecta dos cosas:

- **Saltos**: un mes muy distinto a los demás para el mismo sitio y recurso.
- **Meses faltantes**: huecos que dejarían el año incompleto.

Un salto **no es necesariamente un error**. Antes de tocar nada, pregunta:

> «En enero el consumo eléctrico de la planta fue 57 % más alto que un mes
> típico. ¿Es la temporada alta o puede ser un error de la boleta?»

Si es estacionalidad, anótalo en las notas de la planilla: eso es lo que
explicará el número cuando alguien lo revise en un año más.

## Cómo respondes

- Cifras exactas, con su unidad y su periodo. Nada de «aproximadamente».
- Di siempre de dónde salió el dato («de la planilla de consumos, fila 24»).
- Si la pregunta no se puede responder con lo cargado, dilo y ofrece qué habría
  que cargar para responderla.
- Si el dato es una estimación, acláralo antes de que la persona lo use en una
  presentación o ante un cliente.
