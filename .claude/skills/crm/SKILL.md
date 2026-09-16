---
name: crm
description: Llevar el seguimiento comercial de servicios ESG: prospectos, estados del embudo, bitácora y próxima acción. Úsala cuando quien trabaja aquí es una consultora o un equipo comercial que vende servicios de sostenibilidad y necesita ordenar sus clientes potenciales, saber a quién llamar hoy o revisar por qué se pierden las oportunidades.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Seguimiento comercial de servicios ESG

Para consultoras y equipos que **venden** servicios ESG: diagnósticos, huella de
carbono, reportes, acompañamiento en cumplimiento. No es para el cliente final
de la empresa; es para quien lo atiende.

**Ojo con una opción:** `--empresa` elige la empresa del espacio de trabajo (la
consultora). El prospecto se indica con `--prospecto`.

## El embudo

| Estado | Qué significa | Si lleva más de… hay que actuar |
|---|---|---|
| `nuevo` | Llegó el contacto y todavía no se le habla | 2 días |
| `contactado` | Ya se le escribió o llamó, sin reunión agendada | 5 días |
| `reunion` | Reunión hecha o agendada | 7 días |
| `propuesta` | Se envió propuesta con alcance y precio | 7 días |
| `negociacion` | Revisan condiciones, plazos o precio | 5 días |
| `ganado` | Aceptaron, el trabajo está contratado | — |
| `perdido` | Se cerró sin contrato | — |

```bash
python .claude/motor/esg.py crm registrar --prospecto "Viña Los Robles" --contacto "Marta Diaz" --sector Vitivinicola --tamano mediana --origen recomendacion --necesidad "un cliente europeo le pide la huella"
python .claude/motor/esg.py crm listar
python .claude/motor/esg.py crm mover --prospecto CRM-0001 --estado contactado --nota "llamada inicial, quedó de mandar el requerimiento del cliente"
python .claude/motor/esg.py crm siguiente
python .claude/motor/esg.py crm informe
```

Cada movimiento deja bitácora con la fecha y la nota. Esa bitácora es lo que
permite retomar una conversación tres semanas después sin partir de cero.

## Detectar la necesidad real detrás de lo que piden

Casi nadie pide lo que necesita. Piden lo que escucharon. La diferencia entre
una propuesta que se firma y una que se archiva suele estar acá.

**Lo que dicen y lo que suele haber detrás:**

| Lo que piden | Lo que puede haber detrás | Pregunta que lo aclara |
|---|---|---|
| «Queremos un reporte de sostenibilidad» | Un cliente o un banco les pidió algo concreto | ¿Quién se lo pidió y qué formato les indicó? |
| «Necesitamos ser carbono neutral» | Quieren usarlo en su comunicación | ¿Dónde piensan usar esa afirmación? |
| «Nos piden la huella» | Un comprador grande está armando su alcance 3 | ¿Les mandaron un cuestionario? ¿Lo puedo ver? |
| «Queremos certificarnos» | No saben qué certificación ni para qué | ¿Qué les pasaría si la tuvieran mañana? |
| «Hay que cumplir la ley» | Llegó una fiscalización o una carta | ¿Recibieron algún documento de la autoridad? |
| «El directorio lo pidió» | Alguien del directorio vio algo afuera | ¿Qué decisión quieren tomar con esa información? |

**Las tres preguntas que ordenan cualquier primera reunión:**

1. **¿Qué los llevó a buscar esto ahora?** Casi siempre hay un gatillo concreto:
   un correo de un cliente, una licitación, una multa de un competidor. Ese
   gatillo es la necesidad real.
2. **¿Qué pasa si no lo hacen?** Distingue lo urgente de lo que estaría bueno.
   Si la respuesta es «nada», no hay proyecto todavía.
3. **¿Quién decide y cuándo?** Sin eso, la propuesta se queda esperando en un
   escritorio.

Anota lo que descubras en `--necesidad`. Una necesidad bien escrita es específica:
«un cliente europeo les pidió datos para su CSRD y tienen plazo hasta marzo», no
«quieren sostenibilidad».

**Si lo que piden no es lo que necesitan, dilo antes de cotizar.** Ofrecer un
reporte completo a quien solo necesita responder un cuestionario de su cliente es
venderle de más, y se nota. Ofrecer un diagnóstico a quien tiene una fiscalización
encima es llegar tarde.

## Trabajar la lista cada día

```bash
python .claude/motor/esg.py crm siguiente
```

Ordena los prospectos activos por cuánto llevan sin movimiento y propone la
acción de cada uno. Los marcados `detenido` llevan más del triple del plazo
razonable de su estado.

Cómo usarlo en la conversación:

- **Toma los tres primeros, no la lista entera.** Una lista de 20 pendientes no
  se trabaja; tres sí.
- Para un prospecto detenido hace tiempo, la mejor acción suele ser preguntar
  derecho si sigue en pie o se cierra. Un «no» libera tiempo; un silencio, no.
- Al cerrar como `perdido`, el motor **exige la razón** en `--nota`. Es a
  propósito: sin esa razón no se aprende nada de la oportunidad perdida. Si la
  misma razón aparece tres veces en el informe, ahí hay algo que corregir.
- Después de cada llamada, mueve el estado o al menos deja una nota. Un CRM
  desactualizado miente y hace tomar malas decisiones.

## Privacidad: esto guarda datos de personas

Nombres, cargos, correos y teléfonos de personas reales.

- Todo queda en `empresas/<empresa>/seguimiento/crm.json`, **en este
  computador**. No se sube a internet, no se publica y no se comparte.
- **Guarda solo lo necesario** para el seguimiento comercial. No anotes datos
  sensibles (salud, opiniones políticas, situación familiar) ni comentarios
  sobre las personas que no te gustaría que leyeran.
- La nota de la bitácora describe **el estado del negocio**, no a la persona:
  «no ha respondido tres correos», no «es desordenado».
- **Borra el registro cuando la persona lo pida o cuando ya no haga falta.** En
  Chile, la Ley 21.719 de datos personales establece que los datos se recogen
  para un fin explícito y se conservan solo el tiempo necesario para cumplirlo;
  los derechos del titular incluyen pedir su supresión.
- Si vas a escribirle a alguien que nunca ha tenido contacto con la empresa,
  revisa de dónde salió ese dato antes de usarlo.
- Al mostrar el informe del embudo en una reunión, recuerda que trae nombres:
  no lo publiques ni lo envíes fuera del equipo comercial.

## Lo que no se hace

- **Nada de promesas.** No hay «garantía de cumplimiento», «certificación
  asegurada» ni ahorros prometidos antes de medir. Si la empresa vende eso, está
  vendiendo un riesgo.
- No inventes plazos normativos ni multas para apurar una decisión. Si hay un
  plazo real, muéstralo con su fuente (`cumplimiento`, `ley-karin`, `ley-rep`).
- No uses un diagnóstico gratuito como excusa para asustar. Los hallazgos se
  presentan con lo que son: brechas con su plazo y su responsable.
- No prometas un resultado que depende del cliente (que entregue datos, que su
  proveedor responda, que la autoridad se pronuncie).
- No registres a una persona en el CRM si te pidió que no la contacten.
