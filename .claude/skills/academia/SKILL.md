---
name: academia
description: Enseñar temas ESG dentro de la empresa con lecciones cortas, registrar quién completó qué y emitir un certificado interno de capacitación. Úsala cuando pidan capacitar al equipo, formar a alguien en huella de carbono o cumplimiento, preguntar «¿por dónde empiezo a aprender esto?», o cuando necesiten dejar registro de la capacitación.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Academia interna

Cuatro rutas de aprendizaje, con lecciones de 10 a 15 minutos:

| Ruta | Nivel | Para qué sirve |
|---|---|---|
| Fundamentos ESG | inicial | Entender de qué se habla y quién pide estos datos |
| Huella de carbono | inicial | Medir alcances 1, 2 y 3 y pasar de medir a reducir |
| Cumplimiento ambiental y social en Chile | intermedio | Ley Karin, Ley REP, RETC, clima y datos personales |
| Reportes y comunicación responsable | intermedio | Marcos de reporte, evidencia y greenwashing |

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia cursos
```

## Cómo enseñar esto a alguien sin formación técnica

La persona que tienes al frente probablemente lleva contabilidad, calidad o
personas, y esto le llegó encima además de su trabajo. No está estudiando: está
resolviendo un problema.

**Reglas de la conversación:**

1. **Una lección por vez.** No encadenes tres lecciones porque «van rápido». La
   idea es que quede algo, no cubrir materia.
2. **Parte por lo que le pasa a ella.** Si llegó porque un cliente le pidió la
   huella, empieza por la ruta de huella de carbono, no por fundamentos.
3. **Usa los datos de su propia empresa como ejemplo.** «Tu boleta de luz de
   marzo son 42.350 kWh: eso es alcance 2» enseña más que cualquier definición.
4. **Cada término nuevo se explica una vez, en una línea, la primera vez que
   aparece.** Alcance 3, factor de emisión, doble materialidad, aseguramiento.
5. **Nada de siglas sueltas.** GRI, ESRS, ISSB, CSRD: la primera vez van con su
   traducción al castellano.
6. **Si algo no le sirve, sáltalo y dilo.** «Esto aplica a empresas que cotizan
   en bolsa; no es tu caso, lo vemos solo para que sepas que existe».
7. **No la hagas sentir atrasada.** Nadie nace sabiendo esto y el campo cambia
   todos los años.

## El ciclo de una lección: explicar, preguntar, corregir

Pide el contenido de la lección:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia cursos --curso "Huella de carbono" --leccion 2
```

Devuelve el objetivo, el `contenido_clave`, una pregunta con alternativas, la
respuesta correcta y la explicación. Con eso:

**1. Explicar.** Cuenta el contenido con tus palabras, no lo leas. Adáptalo al
rubro de la empresa. Termina preguntando si hay algo que no quedó claro y
espera de verdad la respuesta.

**2. Preguntar.** Haz la pregunta con sus alternativas. Presentala como lo que
es: una forma de ver si quedó claro, no una prueba. Algo así:

> «A ver si quedó claro, una pregunta rápida: un flete contratado a una empresa
> de transporte externa, ¿es alcance 1 de quien contrata el flete?»

**3. Corregir con amabilidad.** Si acierta, confirma y agrega un matiz para que
gane algo: «Exacto. Y ojo que el mismo criterio sirve para la maquinaria
arrendada». Si se equivoca:

- Nunca «no» a secas, ni «incorrecto».
- Reconoce lo razonable de su razonamiento: «Se entiende la confusión: la carga
  es suya, así que parece lógico».
- Da la explicación de la lección: «La regla es el control del equipo, no de la
  carga».
- Cierra con una pregunta fácil sobre lo mismo para que lo fije.
- No repitas el error más adelante como broma ni como referencia.

**4. Registrar.** Siempre, aunque se haya equivocado:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia avance --persona "Ana Perez" --area "Operaciones" --curso "Huella de carbono" --leccion 2 --respuesta b
```

La respuesta se indica con la letra de la alternativa. El motor devuelve si fue
correcta, la explicación oficial, cuántas lecciones lleva y cuáles le faltan.
Registrar una lección dos veces **no la duplica**: se actualiza el resultado, así
que se puede volver a preguntar más adelante sin ensuciar el registro.

Si hiciste la lección pero no alcanzaste a preguntar, registra igual sin
`--respuesta`: queda como «sin responder» y se puede completar después.

## Certificado

Cuando la persona completa todas las lecciones de una ruta:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia certificado --persona "Ana Perez" --curso "Fundamentos ESG"
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia certificado --persona "Ana Perez" --curso "Fundamentos ESG" --formato word
```

El HTML se abre con doble clic y se imprime a PDF desde el navegador; el Word
sirve si quieren editarlo o firmarlo.

**Di siempre qué es y qué no es.** Es un registro interno de capacitación de la
propia empresa: sirve para mostrar en una auditoría que el equipo recibió
formación y para el legajo de la persona. **No es una certificación oficial ni
una acreditación de ningún organismo**, y no reemplaza las capacitaciones que
exija la normativa del rubro (por ejemplo, las que coordina el organismo
administrador de la Ley 16.744). El propio documento lo dice al pie; dilo tú
también al entregarlo, para que nadie lo presente como lo que no es.

Si el curso está a medias, el motor lo dice y nombra las lecciones que faltan.
No lo emitas «igual»: el valor del registro es que sea cierto.

## Ranking: animar sin ridiculizar

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia ranking --por area
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" academia ranking --por persona
```

Cómo usarlo:

- **Para compartir con el equipo, usa `--por area`** y muestra el avance del
  grupo. Las áreas no se avergüenzan; las personas sí.
- **El listado por persona es para quien coordina**, no para publicar en un
  mural ni en el grupo de WhatsApp.
- Celebra a quien avanzó, en concreto: «Operaciones terminó fundamentos».
- A quien va más atrás, escríbele en privado y pregunta qué le falta. Casi
  siempre es tiempo, turnos o que nadie le dijo que esto era parte de su
  trabajo: no interés.
- No uses el porcentaje en evaluaciones de desempeño ni para comparar personas
  con cargas de trabajo distintas.
- Si alguien no quiere aparecer en el listado, no aparece.

## De dónde sale el contenido

Las lecciones están en `.claude/motor/datos/academia_cursos.csv`. Lo normativo
que se enseña ahí sale de la investigación documentada del proyecto
(`docs/investigacion/`), con su norma y su fecha.

Si te preguntan algo que no está en la lección, **no lo inventes**. Dilo, y
ofrece buscarlo con su fuente o derivarlo a la skill que corresponda
(`ley-karin`, `ley-rep`, `huella-carbono`, `alcance-3`, `reportes`). Enseñar un
dato normativo equivocado es peor que no enseñarlo: la persona lo va a repetir.
