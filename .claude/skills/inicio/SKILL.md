---
name: inicio
description: Registrar una empresa nueva en el espacio de trabajo ESG. Úsala cuando la persona empieza de cero, dice que quiere configurar su empresa, medir su huella por primera vez o cuando no hay ninguna empresa registrada.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Registrar una empresa

Objetivo: en menos de 10 minutos dejar lista la carpeta de la empresa, con lo
justo para empezar a trabajar. Nada de formularios largos.

## Antes de preguntar

Comprueba que el motor responde:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" empresa listar
```

Si falla por falta de Python, usa la skill `preparar-equipo` y vuelve aquí.
Si ya existe una empresa con ese nombre, no la dupliques: ábrela y sigue.

## Las preguntas (una a la vez)

Hazlas en este orden, en lenguaje cotidiano. Si la persona no sabe algo,
acéptalo vacío y sigue: se puede completar después.

1. **¿Cómo se llama la empresa?** (el nombre con el que la conocen)
2. **¿En qué país está la operación principal?** (Chile, Perú, España…)
3. **¿A qué se dedican?** En una frase. Ej: «hacemos conservas de fruta».
4. **¿Cuántas personas trabajan ahí?** Un número aproximado basta.
5. **¿Cuántos lugares tienen?** Oficinas, plantas, bodegas, campos, tiendas.
   Si es más de uno, anota los nombres.
6. **¿Por qué necesitas esto ahora?** Esta es la pregunta más importante:
   - «Un cliente me lo pide» → prioriza huella de carbono y datos por producto.
   - «Exportamos a Europa» → prioriza requisitos europeos y trazabilidad.
   - «Me llegó algo de la autoridad» → prioriza esa obligación puntual.
   - «Queremos ordenarnos / medir» → prioriza diagnóstico y huella.
   - «Vamos a postular a un fondo o licitación» → prioriza reporte presentable.
7. **¿Desde qué año quieres medir?** (año base; normalmente el año pasado)
8. **¿Venden a la Unión Europea, directo o a través de otro?** (sí/no)
9. *(Opcional)* **¿Ventas anuales aproximadas?** Sirve para comparar y para
   saber si le aplican ciertas normas. Si prefiere no decirlo, se salta.

## Crear la empresa

Arma un archivo JSON temporal con lo recogido y créala:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" empresa crear --datos perfil.json
```

`perfil.json` acepta: `nombre`, `razon_social`, `identificador_tributario`,
`pais` (CL, PE, ES…), `sector`, `tamano` (micro, pequena, mediana, grande),
`trabajadores`, `ingresos_anuales`, `moneda`, `anio_base`, `periodo_actual`,
`marcos` (lista), `exporta_a_ue` (true/false), `sitios` (lista de objetos con
`nombre`, `tipo`, `comuna`, `region`, `pais`), `notas`.

Criterio para `tamano` cuando la persona no lo sabe: micro hasta 9 personas,
pequeña 10–49, mediana 50–199, grande 200 o más. Dile qué asumiste.

Borra el JSON temporal después de crear la empresa.

## Dejar el terreno listo

1. Si hay más de un sitio, crea la planilla de sitios y explícale que la llene:
   ```bash
   python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" plantilla crear --tipo sitios
   ```
2. Resume en 5 líneas lo que quedó registrado y **dónde** quedó la carpeta.
3. Propón exactamente **tres** próximos pasos, ordenados por lo que la persona
   respondió en la pregunta 6. Por ejemplo:
   - «Calcular la huella de carbono del año pasado» (skill `huella-carbono`).
   - «Revisar qué normas te aplican hoy» (skill `brechas-cumplimiento`).
   - «Ver el estado general de la empresa» (skill `diagnostico-esg`).
   Ofrece empezar por uno ahora mismo.

## Cuidados

- No pidas datos personales de trabajadores en esta etapa. No hacen falta.
- No prometas certificaciones ni resultados regulatorios.
- Si la persona se agobia, ofrece registrar solo el nombre y el país, y
  completar el resto más adelante: eso es suficiente para empezar.
