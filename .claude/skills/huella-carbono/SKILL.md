---
name: huella-carbono
description: Calcular la huella de carbono de la empresa (alcances 1 y 2) y generar el informe. Úsala cuando pidan medir emisiones, huella de carbono, CO2, inventario de gases de efecto invernadero, cuando un cliente o banco les pida esa cifra, o cuando quieran saber cuánto contamina la empresa.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Huella de carbono (alcances 1 y 2)

Medir es sumar dos cosas: **cuánta energía o combustible usó la empresa** y
**cuánto CO2 equivale cada unidad** (el factor de emisión). El motor hace la
multiplicación con factores oficiales; tú acompañas a la persona a reunir los
datos y le explicas el resultado.

Para la cadena de valor (compras, fletes, viajes, residuos) usa la skill
`alcance-3`.

## Explicaciones que debes tener a mano

- **Alcance 1**: lo que la empresa quema o fuga ella misma — combustible de
  camiones y maquinaria, gas o leña de calderas, recargas de refrigerante.
- **Alcance 2**: la electricidad (o vapor) que compra.
- **tCO2e**: toneladas de CO2 equivalente; junta todos los gases en una sola cifra.
- **Factor de emisión**: cuánto CO2e genera una unidad (por ejemplo, 1 kWh de la
  red chilena). Cambia por país y por año.

## Paso a paso

**1. Confirma la empresa y el periodo.** Normalmente el año calendario anterior.

**2. Revisa si ya hay datos.**

```bash
python .claude/motor/esg.py empresa ver
```

Si no existe `datos/consumos.xlsx`, créalo y explícale qué llenar:

```bash
python .claude/motor/esg.py plantilla crear --tipo consumos
```

**3. Ayúdale a reunir los datos.** Lo mínimo para un año creíble:

| Dato | Dónde lo encuentra |
|---|---|
| Electricidad (kWh por mes) | Boletas de la eléctrica; el total anual también sirve |
| Combustible de vehículos y maquinaria (litros) | Facturas de la estación de servicio o control interno |
| Gas, leña o petróleo de calderas | Facturas del proveedor |
| Recargas de refrigerante (kg y tipo) | Informe del servicio técnico de climatización |

Si tiene las boletas en PDF o fotos, **léelas tú y llena la planilla por ella**:
es la forma más rápida y evita errores de tipeo. Confirma con la persona los
valores que extrajiste antes de guardarlos. Para el detalle de la carga usa la
skill `cargar-datos`.

**4. Calcula.**

```bash
python .claude/motor/esg.py huella calcular --periodo 2025
```

Lee con atención `advertencias` y `problemas`:

- «Asumí uso estacionario…» → pregúntale si ese combustible es de vehículos.
- «Para X usé el factor de otro año» → normal cuando el factor oficial del año
  todavía no se publica; menciónalo en el informe.
- Filas con problema → dile exactamente qué fila y qué corregir.

**5. Explícale el resultado en palabras simples.** Di, en este orden:

1. El total en toneladas de CO2e del periodo.
2. Cuánto es alcance 1 y cuánto alcance 2.
3. Las tres mayores fuentes (de ahí saldrán las acciones de reducción).
4. La calidad de los datos: cuánto es medido y cuánto estimado.
5. Qué falta para que la cifra sea sólida.

No inventes comparaciones («equivale a X autos») a menos que puedas justificar
la conversión con una fuente.

**6. Genera el informe.**

```bash
python .claude/motor/esg.py huella reporte --periodo 2025
```

Queda en `reportes/` como archivo HTML: se abre con doble clic y se imprime a
PDF desde el navegador (Ctrl+P). Dile dónde quedó.

**7. Respalda la evidencia** (importante si el número se usará ante terceros):

```bash
python .claude/motor/esg.py evidencia registrar --archivo datos/consumos.xlsx --descripcion "Consumos 2025"
```

**8. Propón el siguiente paso**, según lo que la empresa necesite: estimar el
alcance 3 (`alcance-3`), fijar una meta (`metas-net-zero`), armar un plan de
reducción (`plan-descarbonizacion`) o preparar un reporte formal (`reportes`).

## Detalles que hacen la diferencia

- **Electricidad**: el motor usa el factor de la red del país por año (alcance 2
  «por ubicación»). Si la empresa compró certificados de energía renovable
  (I-REC), se puede reportar además un alcance 2 «por mercado»; para eso hacen
  falta los certificados, y sin ellos no se descuenta nada aunque el contrato
  diga «energía verde».
- **Leña y biomasa**: el CO2 biogénico se informa aparte, no dentro del alcance 1.
  Hoy el motor no trae factor oficial chileno de leña: si la empresa usa leña,
  dilo y regístralo como brecha en vez de inventar un valor.
- **Meses vs año**: cargar mes a mes permite ver estacionalidad y detectar
  errores; si solo tiene el total del año, también sirve.
- **Sitios**: usa el mismo nombre de sitio en todas las planillas, así el informe
  muestra bien de dónde vienen las emisiones.
- **No cambies factores a mano.** Si falta uno, regístralo como brecha y ofrece
  buscarlo en la fuente oficial con el agente `agente-investigador`.
- **Consulta el catálogo antes de adivinar un nombre.** El motor solo reconoce
  los nombres que tiene registrados:

  ```bash
  python .claude/motor/esg.py huella factores --recurso leña
  ```

  Busca por nombre y, si no hay, por la descripción del factor. Acepta también
  `--uso` (`estacionaria`, `movil`, `gasto`, `carga`, `pasajeros`, `residuos`,
  `fugitiva`, `electricidad`, `agua`, `alojamiento`), `--alcance` y `--pais`.
  Cada resultado trae fuente, año, unidad y qué cubre. Si el nombre no existe,
  el error te devuelve los parecidos: muéstraselos a la persona y que ella elija,
  no decidas tú.

## Cierre

Termina siempre diciendo: qué se obtuvo, dónde quedó el archivo, qué tan sólido
es el dato y cuál es el siguiente paso. Y recuerda que es un apoyo de gestión:
para una declaración oficial o una auditoría, los datos deben verificarse.
