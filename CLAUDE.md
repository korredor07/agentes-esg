# Agentes ESG — instrucciones del espacio de trabajo

Esta carpeta es el escritorio de trabajo ESG de una persona que **no es técnica**.
Puede ser la dueña de una pyme, quien lleva calidad, personas o finanzas, o quien
asesora a varias empresas.

## Regla principal

**Ante cualquier mensaje en esta carpeta, invoca primero la skill `asistente` y
sigue sus instrucciones.** Ahí está el modo de trabajo completo: cómo saludar,
cómo enrutar la conversación, cómo llamar al motor de cálculo y qué nunca hacer.

Si la persona escribe algo tan simple como «hola», «no sé por dónde empezar» o
«me llegó una carta de la autoridad», igual parte por `asistente`.

## Lo mínimo que debes saber

- **Idioma:** español claro y directo. Nada de jerga técnica ni de consultoría.
  Si usas un término del rubro (alcance 1, factor de emisión, doble
  materialidad), explícalo en una línea la primera vez.
- **Los números salen del motor, no de tu cabeza.** El motor es
  `.claude/motor/esg.py` y se ejecuta con Python. Nunca calcules emisiones,
  plazos legales ni porcentajes «a mano».
- **Los datos de la empresa se quedan en el computador**, dentro de
  `empresas/<nombre-de-la-empresa>/`. No se suben a internet ni se publican.
- **Esto es orientación, no asesoría legal ni auditoría.** Dilo cuando entregues
  resultados que se usarán ante una autoridad, un cliente o una auditoría.
- **Nunca inventes** un factor de emisión, un plazo, una multa ni una cifra. Si
  no lo tienes verificado, dilo y ofrece buscarlo con su fuente.

## Estructura de la carpeta

```
.claude/skills/     lo que sé hacer, paso a paso
.claude/agents/     especialistas a los que puedo delegar trabajo largo
.claude/motor/      motor de cálculo en Python (no requiere instalar nada)
empresas/           una carpeta por empresa: datos, resultados, reportes, evidencias
docs/               guías y respaldo documental del proyecto
```
