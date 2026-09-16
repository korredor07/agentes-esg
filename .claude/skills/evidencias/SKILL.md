---
name: evidencias
description: Respaldar documentos con huella digital SHA-256 y verificar que no hayan cambiado. Úsala cuando pidan trazabilidad, respaldo de datos, prepararse para una auditoría o una verificación, demostrar que un archivo no fue alterado, o cuando el dato vaya a usarse ante un cliente, un banco o una autoridad.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Bóveda de evidencias

Cada archivo que respaldas queda anotado con su **huella digital** (SHA-256) y
enlazado al anterior, formando una cadena. Si alguien cambia un archivo, borra
una anotación o altera el orden, la verificación lo detecta.

## Qué prueba y qué no

- **Sí prueba**: que el archivo es idéntico al que se registró y en qué orden se
  registraron las cosas.
- **No prueba**: quién lo firmó ni en qué fecha exacta ante un tercero. Para eso
  se necesita firma electrónica avanzada o un sellado de tiempo acreditado, que
  esto **no reemplaza**. Dilo cada vez que entregues un informe de evidencias.

## Registrar

```bash
python .claude/motor/esg.py evidencia registrar --archivo datos/consumos.xlsx --descripcion "Consumos de energía 2025" --responsable "Ana Pérez"
```

Qué conviene registrar:

- Las planillas con los datos del periodo, una vez cerradas.
- Boletas, facturas e informes de laboratorio que respaldan esas cifras.
- Los reportes finales que se entregaron a un tercero.
- Actas, protocolos y comunicaciones con plazo legal.

Registra **después** de cerrar el dato, no mientras lo están editando: cada
cambio posterior aparecerá como archivo modificado.

## Verificar

```bash
python .claude/motor/esg.py evidencia verificar
python .claude/motor/esg.py evidencia listar
```

Si algo falla, traduce el problema:

| Problema | Qué pasó | Qué hacer |
|---|---|---|
| archivo_modificado | El archivo cambió después de registrarse | Ver qué cambió y registrar la nueva versión explicando por qué |
| archivo_faltante | Ya no está donde estaba | Buscarlo o recuperarlo de una copia |
| registro_alterado | Alguien editó el registro a mano | No editar `registro.jsonl`; revisar quién tuvo acceso |
| cadena_rota | Falta una anotación o cambió el orden | Igual que el anterior |

Un archivo modificado **no es fraude**: casi siempre es que corrigieron un dato.
Lo importante es dejar la explicación por escrito y registrar la nueva versión.

## Antes de una auditoría

1. Verifica la cadena completa.
2. Revisa que cada cifra del reporte tenga su respaldo registrado.
3. Anota los supuestos usados donde no hubo dato medido.
4. Deja los archivos originales en `datos/`, no solo los resúmenes.

Eso es, en la práctica, lo que pide un verificador: poder llegar desde el número
del reporte hasta el documento que lo origina.
