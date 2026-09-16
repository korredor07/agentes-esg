---
name: social-personas
description: Indicadores sociales de la empresa: dotación, rotación, brecha salarial, accidentes, capacitación e inclusión laboral. Úsala cuando pidan datos de personas para un reporte, cuando pregunten por la brecha salarial o la accidentabilidad, o cuando haya que preparar la parte social de una memoria o de un cuestionario de cliente.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Indicadores sociales

La parte social de un reporte se arma con datos que la empresa ya tiene en
remuneraciones y en prevención de riesgos: cuántas personas trabajan, quiénes
entran y salen, cuánto ganan, cuánto se capacitan y cuántos accidentes hubo.

## 1. Cargar los datos

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" plantilla crear --tipo personas
```

Una fila por **grupo**, no por persona: sitio, categoría, género, tipo de
contrato, jornada y cuántas personas hay en esa combinación. Así se obtienen los
indicadores sin manejar datos individuales, que es lo correcto en privacidad.

Dile de dónde sacar cada dato:

| Dato | Dónde está |
|---|---|
| Dotación, contrataciones y salidas | Planilla de remuneraciones o sistema de personal |
| Remuneración promedio por grupo | Planilla de remuneraciones (promedio, nunca sueldos individuales) |
| Horas de capacitación | Registros de capacitación |
| Accidentes y días perdidos | Registros del organismo administrador (mutualidad) |
| Horas trabajadas | Control de asistencia |
| Personas con discapacidad | Registro interno (Ley 21.015 en Chile) |

## 2. Calcular

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" social calcular --periodo 2025
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" social informe --periodo 2025
```

## 3. Qué significa cada número

- **Rotación**: desvinculaciones sobre la dotación. Alta rotación encarece y
  desgasta; es de los indicadores que más miran los clientes grandes.
- **Brecha salarial**: cuánto menos gana en promedio un grupo respecto de otro
  **en la misma categoría**. Comparar el promedio general de mujeres con el de
  hombres sin separar por cargo produce cifras engañosas: dilo si la empresa
  quiere publicar el dato.
- **Accidentabilidad**: accidentes sobre la dotación. La cifra oficial la emite
  la mutualidad; esta sirve para gestión interna.
- **Tasa por 200.000 horas**: la convención internacional para comparar entre
  empresas de distinto tamaño.
- **Capacitación por persona**: horas totales divididas por la dotación.
- **Inclusión (Chile)**: desde 100 trabajadores hay que cumplir la cuota del 1 %
  y comunicarlo anualmente a la Dirección del Trabajo.

## Cuidados importantes

- **Nunca pidas ni guardes datos individuales** de salud, licencias, sueldos
  nominativos o denuncias en esta planilla. Todo agregado por grupo.
- Si la empresa tiene pocas personas en una categoría, un promedio puede
  identificar a alguien: agrupa más o no publiques ese corte.
- Los datos de personas son sensibles: se quedan en el computador y solo se
  comparten de forma agregada.
- Si aparece un accidente grave o una situación de acoso, eso no es un
  indicador: es un caso que tiene su propio procedimiento y plazos (skill
  `ley-karin` en Chile).
