---
name: ley-karin
description: Ley Karin (Ley 21.643 de Chile) sobre acoso sexual, acoso laboral y violencia en el trabajo: qué hacer ante una denuncia, plazos legales exactos, protocolo de prevención y documentos. Úsala cuando mencionen una denuncia de acoso o maltrato, un problema entre trabajadores, la Dirección del Trabajo, el protocolo de prevención, o pregunten qué exige la Ley Karin.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Ley Karin (Ley 21.643, Chile)

Obliga a **todo empleador** en Chile —sin importar su tamaño— a tener un
protocolo de prevención y a investigar las denuncias de acoso sexual, acoso
laboral y violencia en el trabajo con **plazos perentorios**.

## Lo primero: ¿hay una denuncia en curso?

Si la respuesta es sí, **esto es urgente y va antes que cualquier otra cosa**.
Actúa en este orden:

1. **Pregunta la fecha exacta en que la empresa recibió la denuncia.** De ahí
   salen todos los plazos.
2. Dile que hay una obligación **inmediata**: adoptar medidas de resguardo
   (separar espacios físicos, cambiar turnos, ofrecer atención psicológica a
   través de la mutual). No pueden perjudicar a quien denuncia.
3. **Pregunta dos cosas que deciden si la empresa puede investigar o tiene que
   derivar a la Dirección del Trabajo:**
   - ¿El reglamento interno ya tiene el procedimiento de la Ley Karin? Si no
     está actualizado, la denuncia **se deriva de inmediato** a la DT (DS 21,
     art. primero transitorio inc. 3°).
   - ¿La persona denunciada es gerente, administrador o representa al
     empleador? Si es así, **siempre** se deriva (art. 12 inc. 5° DS 21).
4. Registra el caso con esas respuestas y muéstrale el calendario completo:

```bash
python .claude/motor/esg.py karin crear --fecha-denuncia 15-09-2026 --tipo "acoso laboral" --sitio "Planta" --denunciante "A.P." --denunciado "M.R." --resumen "Descripción breve" --reglamento-actualizado no --contra-representante no
```

Si el motor responde `derivacion_obligatoria: true`, eso va **primero** en tu
respuesta, antes que cualquier plazo: la empresa no puede investigar
internamente. Registra la derivación con `--via derivada` y, cuando la DT emita
el certificado de recepción, anótalo: desde esa fecha corren los 30 días de
investigación (art. 17 DS 21).

```bash
python .claude/motor/esg.py karin evento --caso KARIN-2026-001 --hito recepcion_dt --fecha 2026-09-03
```

4. Dile que **involucre desde ya a su asesoría jurídica y al organismo
   administrador de la Ley 16.744** (ACHS, Mutual, IST o ISL). Tú acompañas y
   ordenas los plazos; no reemplazas a un abogado.

**Usa iniciales o un código, nunca nombres completos**, salvo que sea
imprescindible: son datos sensibles y quedan guardados en el computador.

## Los plazos (esto es lo que más se equivoca)

Todos los plazos son en **días hábiles** —y son inhábiles sábados, domingos y
festivos (art. 1° del DS N° 21 de 2024)— **salvo uno**: la aplicación de medidas
y sanciones, que es de **15 días corridos** (art. 19 DS 21). Muchas guías dicen
"hábiles" y está mal.

| Hito | Plazo |
|---|---|
| Medidas de resguardo | Inmediato |
| Informar a la Dirección del Trabajo el inicio de la investigación, o derivarle la denuncia | 3 días hábiles |
| Designar a la persona investigadora e informarlo por escrito | 3 días hábiles |
| Concluir la investigación | 30 días hábiles |
| Remitir el informe a la Dirección del Trabajo | 2 días hábiles |
| Pronunciamiento de la Dirección del Trabajo | 30 días hábiles |
| Aplicar medidas y sanciones e informar a las partes | **15 días corridos** |

Los plazos **no se suspenden** por vacaciones ni licencia médica de los
involucrados (dictamen DT ORD. N° 386/10 de 2025).

Para ver el calendario de un caso, con feriados chilenos ya descontados:

```bash
python .claude/motor/esg.py karin ver --caso KARIN-2026-001
```

Cuando algo se cumple, regístralo: el resto del calendario se recalcula solo.

```bash
python .claude/motor/esg.py karin evento --caso KARIN-2026-001 --hito informar_dt --fecha 17-09-2026
```

Hitos válidos: `medidas_resguardo`, `informar_dt`, `designar_investigador`,
`conclusion_investigacion`, `remision_informe`, `pronunciamiento_dt`,
`aplicar_medidas`.

Para dejar los vencimientos visibles en el tablero:

```bash
python .claude/motor/esg.py karin alertas
```

## Si no hay denuncia: prevención

Toda empresa debe tener el **protocolo de prevención** (art. 211-A del Código
del Trabajo), elaborado con apoyo del organismo administrador de la Ley 16.744,
con cinco contenidos mínimos: evaluación de riesgos psicosociales con
perspectiva de género, medidas de prevención con objetivos medibles,
información y capacitación, medidas de prevención propias del giro, y resguardo
de la privacidad y la honra.

```bash
python .claude/motor/esg.py karin documento --tipo protocolo
python .claude/motor/esg.py karin documento --tipo informe
```

Entrega un borrador en Word con la estructura exigida. Deja claro que **es un
punto de partida**: hay que completarlo con la realidad de la empresa y
revisarlo con la mutual y la asesoría jurídica.

Dónde va el protocolo, según el tamaño:

- **10 o más trabajadores permanentes**: dentro del Reglamento Interno de Orden,
  Higiene y Seguridad. Copia al Ministerio de Salud y a la Dirección del Trabajo
  dentro de los 5 días siguientes a su vigencia.
- **Menos de 10**: se entrega por escrito al firmar el contrato y se incorpora
  al reglamento del art. 67 de la Ley 16.744.

Además: informar los canales de denuncia **cada seis meses** a todo el personal.

## Cómo conversas esto

- Con cuidado. Puede haber una persona afectada esperando una respuesta.
- Sin prometer resultados («esto se resuelve así» no; «la ley exige esto y estos
  son los plazos» sí).
- Sin opinar sobre la culpabilidad de nadie: tu rol es el procedimiento.
- Recuérdale la reserva: la investigación es confidencial y no puede haber
  represalias contra quien denuncia o declara.
- Si preguntan por multas: existen y dependen del tamaño de la empresa; el monto
  exacto lo determina la Dirección del Trabajo según el caso.

## Límites honestos

- No puedes presentar nada ante la Dirección del Trabajo: eso lo hace la
  empresa por sus canales oficiales.
- No sustituyes al investigador ni a la asesoría legal.
- El día inicial del cómputo se asume como el día siguiente al hecho (regla
  supletoria del art. 25 de la Ley 19.880). Si un plazo queda al límite, que lo
  confirme la asesoría jurídica.
