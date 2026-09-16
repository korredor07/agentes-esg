---
name: cargar-datos
description: Cargar los datos de la empresa al espacio de trabajo desde boletas, facturas, fotos, PDF, planillas Excel o exportaciones del sistema contable. Úsala cuando la persona diga que tiene boletas de luz, facturas de combustible, planillas sueltas, un export del ERP, o pregunte cómo meter sus datos.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Cargar datos

La regla: **la persona no debería tipear nada que tú puedas leer por ella**.

## Formas de cargar, de la más cómoda a la menos

**1. Ella te pasa los documentos y tú llenas la planilla.**
Boletas de luz, facturas de combustible, fotos del medidor, un PDF del banco:
léelos, extrae los datos y escribe la planilla. Es lo más rápido y lo más
seguro. Siempre muéstrale un resumen de lo que extrajiste **antes** de guardar:

> «De las 12 boletas leí: enero 42.350 kWh, febrero 39.980 kWh… ¿Lo dejo así?»

**2. Ella llena la plantilla Excel.**

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" plantilla listar
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" plantilla crear --tipo consumos
```

Explícale: una fila por dato, no cambiar los títulos de las columnas, borrar las
filas de ejemplo, guardar el archivo en `datos/` y avisarte.

**3. Ella te dicta los números en la conversación.** Perfecto para empezar:
anótalos tú en la planilla y sigue.

**4. Exportación del sistema contable o del ERP.** Si trae un archivo con las
compras del año, se puede usar para el alcance 3 por gasto. En Chile, el
«Registro de Compras y Ventas» del SII sirve: agrupa por tipo de proveedor y
convierte a dólares (ver skill `alcance-3`).

## Dónde va cada archivo

```
empresas/<empresa>/datos/        planillas y documentos de respaldo
```

Guarda los PDF y fotos originales ahí también: son la evidencia del dato.

## Calidad del dato: no es un detalle

Cada fila lleva una etiqueta y cambia cuánto vale el número:

| Etiqueta | Cuándo | Ejemplo |
|---|---|---|
| verificado | Un tercero lo revisó o auditó | Consumo auditado por la certificadora |
| reportado | Viene de una boleta, medidor o factura | kWh de la boleta de la eléctrica |
| estimado | Lo calculó la empresa o tú | Litros estimados por horas de uso |

Si estimaste algo, **dilo y anota el supuesto en la columna de notas**. En una
auditoría, un supuesto escrito vale; uno olvidado no.

## Revisar antes de calcular

Después de cargar, corre el cálculo: el motor avisa fila por fila lo que falta o
no cuadra. Traduce cada problema a una instrucción concreta:

- «Falta la unidad en la fila 14» → «En la fila 14 falta decir si son litros o
  kilos; ¿me confirmas?»
- «No tengo un factor de emisión para X» → ofrece buscarlo con fuente oficial.
- Valores raros (un mes con el triple que los demás) → pregúntale antes de
  seguir; suele ser un error de tipeo o un dato acumulado.

## Respaldar la evidencia

Cuando el dato ya está bueno, deja la huella digital del archivo:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia registrar --archivo datos/consumos.xlsx --descripcion "Consumos 2025 con boletas"
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia verificar
```

Eso permite demostrar más adelante que el archivo no cambió. No reemplaza una
firma electrónica avanzada ni un sellado de tiempo acreditado: dilo así.

## Cuidados

- **Datos de personas** (remuneraciones, licencias, denuncias): quédate solo con
  lo necesario, nunca los publiques y recuerda que la carpeta `empresas/` no se
  sube a internet.
- **No borres ni sobrescribas** un archivo de la persona sin preguntar.
- Si un documento está borroso o incompleto, dilo en vez de adivinar.
