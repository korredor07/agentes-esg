---
name: tablero
description: Generar el tablero ESG en una página: huella, puntaje, brechas por cerrar, plazos que vencen y estado de los datos. Úsala cuando pidan un resumen general, una vista para la gerencia o el directorio, un estado de avance, o cuando alguien pregunte "cómo vamos".
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Tablero ESG

Una sola página con todo lo importante, para mirar antes de una reunión.

```bash
python .claude/motor/esg.py tablero generar
```

Queda en `reportes/tablero.html`. Se abre con doble clic; para enviarlo, se
imprime a PDF desde el navegador (Ctrl+P → Guardar como PDF).

## Qué muestra

- Puntaje ESG y nivel de madurez.
- Huella de carbono del último cálculo y su reparto por alcance.
- Brechas por cerrar, con las cinco más urgentes y qué hacer en cada una.
- Plazos que vencen (los dejan los módulos de cumplimiento).
- Estado de los respaldos y de las planillas: qué está cargado y qué falta.

## Cómo lo presentas

Después de generarlo, resume en voz propia lo que verá, en tres o cuatro frases:

> «El tablero quedó listo. En resumen: la huella 2025 fue de 1.566 toneladas, el
> 79 % viene de la cadena de valor; el puntaje ESG está en 32 de 100 porque
> faltan varias cosas del lado social y de gobernanza; y lo más urgente es el
> protocolo de la Ley Karin. ¿Lo revisamos por ahí?»

## Cuándo conviene generarlo

- Después de calcular la huella o de responder el diagnóstico.
- Antes de una reunión de gerencia, directorio o comité.
- Cuando un cliente o un banco pide "el estado de sostenibilidad".
- Una vez al mes, si quieren seguimiento (se puede dejar como rutina).

Si todavía no hay huella calculada, el tablero lo dice y sugiere ese primer
paso: no lo escondas, es información útil.
