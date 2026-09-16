---
name: retc
description: Declaraciones ambientales de Chile: RETC, residuos, emisiones de fuentes fijas, residuos peligrosos, descargas líquidas e impuesto verde, con el calendario de plazos del año. Úsala cuando pregunten qué tienen que declarar, cuándo, cuando les llegue un requerimiento de la autoridad ambiental, o cuando quieran saber si están registrados donde corresponde.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Declaraciones ambientales (Chile)

Casi todas las multas ambientales de una pyme no vienen por contaminar: vienen
por **no declarar a tiempo**. Esta skill ordena qué le toca a la empresa y
cuándo.

## 1. Saber qué le aplica

Si aún no está hecho, primero la skill `brechas-cumplimiento`: sus preguntas
(si tienen caldera, si generan residuos industriales, si descargan riles, si
ponen productos en el mercado) son las que activan cada declaración.

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" calendario proximas
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" calendario informe
```

Estados que devuelve: **urgente** (vence en una semana o menos), **abierto**
(la ventana está abierta ahora), **se acerca** (dentro de 45 días),
**programado**, **por abrir** y **cerrado este año**.

## 2. Las declaraciones más comunes

| Qué | Cuándo | Quién |
|---|---|---|
| Declaración de emisiones de fuentes fijas | 1 de enero al 30 de abril | Establecimientos con calderas, hornos o generadores afectos |
| Declaración anual de residuos generados | hasta el 30 de marzo | Quien genera más de 12 toneladas al año |
| Declaración de Desempeño Ambiental y Empresarial | 1 al 30 de junio | Establecimientos registrados |
| Declaración Jurada Anual del RETC | 1 al 31 de octubre | Encargado de cada establecimiento registrado |
| Residuos peligrosos (SIDREP) | por operación | Generadores de residuos peligrosos |
| Autocontrol de residuos líquidos | mensual | Establecimientos con descarga regulada |

Todo se hace en la **Ventanilla Única del RETC**, con la clave del
establecimiento. Si la empresa no está registrada, ese es el primer paso.

## 3. Cómo acompañas

- Empieza por lo que está **abierto o urgente**, no por explicar el sistema
  completo.
- Para cada declaración: qué datos hay que reunir, de dónde salen (registros de
  compra de combustible, guías de retiro de residuos, informes del laboratorio)
  y quién los tiene en la empresa.
- Ayuda a armar la planilla con esos datos; el envío lo hace la empresa con su
  clave en el portal. **Tú no puedes declarar por ella.**
- Cuando el dato ya esté listo, respáldalo con la skill `evidencias`: si hay
  fiscalización, lo que importa es poder mostrar de dónde salió cada cifra.

## 4. Impuesto verde

Aplica a establecimientos cuyas fuentes fijas superan los umbrales de material
particulado o de dióxido de carbono. Si la empresa cree estar cerca del umbral,
lo primero es cuantificar las emisiones de esas fuentes; el cálculo de la
huella ayuda, pero la declaración usa la metodología que exige la autoridad.

## Cuidados

- **Las fechas pueden cambiar** cada año por resolución o convocatoria del
  organismo: confírmalas en el portal antes de planificar.
- No inventes umbrales ni montos de multa. Si no está verificado en los
  antecedentes del proyecto, dilo y ofrece verificarlo con el agente
  investigador.
- Si la empresa ya recibió un requerimiento o una formulación de cargos, eso
  tiene plazos propios y muy cortos: lo primero es leer el documento y
  contactar a su asesoría.
