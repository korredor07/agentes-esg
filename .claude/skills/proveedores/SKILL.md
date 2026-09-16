---
name: proveedores
description: Pedir datos ambientales y laborales a los proveedores de la empresa, registrar lo que responden y priorizar a quién perseguir. Úsala cuando hablen de cadena de suministro, de pedir la huella a un proveedor, de un cuestionario para proveedores, de reemplazar estimaciones del alcance 3 por datos reales, o cuando un proveedor no responde.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Proveedores: pedir datos sin abrumar

En la mayoría de las empresas, la parte más grande de la huella está en lo que
compran. Ese dato no lo tiene la empresa: lo tienen sus proveedores. Este
módulo sirve para pedírselo de una forma que sí funcione.

**La regla que ordena todo:** no hay que pedirle datos a todos los proveedores.
Hay que pedírselos a los pocos que explican la mayor parte del impacto.

## Antes de escribir a nadie: prioriza

Una pyme puede tener 200 proveedores y que 8 expliquen el 80 % de sus compras.
Escribirle a los 200 significa tres cosas: mucho trabajo, tasas de respuesta
bajísimas y proveedores molestos. Escribirle a los 8 es una tarde de trabajo.

1. Carga la lista con lo que ya se sabe: nombre, categoría de compra y **gasto
   anual**. El gasto es el mejor sustituto cuando todavía no hay emisiones
   calculadas.

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" proveedores registrar --nombre "Envases del Sur" --categoria envases --gasto-anual 18000000 --contacto "Luis Soto"
```

2. Pide el orden de trabajo:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" proveedores evaluar
```

El resultado marca con `explica_80_pct` a los que están dentro del 80 % del
impacto y pone arriba a los grandes que **todavía no entregan datos**. Esa
lista, y no otra, es a quien hay que escribir esta semana.

3. Muéstrale a la persona los tres primeros y dile por qué son esos. Si alguien
   quiere «mandar el cuestionario a todos», explícale el costo: cada envío
   consume paciencia del proveedor, y esa paciencia conviene gastarla donde
   mueve el número.

## Cómo pedirlo para que respondan

Genera los dos documentos y revísalos con la persona antes de enviarlos:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" proveedores carta --proveedor "Envases del Sur" --plazo 30-10-2026 --responsable "Ana Rojas" --correo ana@empresa.cl
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" proveedores cuestionario --proveedor "Envases del Sur" --plazo 30-10-2026 --responsable "Ana Rojas" --correo ana@empresa.cl
```

Lo que hace la diferencia entre un cuestionario contestado y uno ignorado:

- **Decir para qué es.** «Un cliente nos pide las emisiones de nuestra cadena y
  hoy las estamos estimando con promedios que no reflejan lo que ustedes hacen».
- **Ser corto.** Si toma más de 20 minutos, no se contesta.
- **Permitir el "no lo tengo".** Una respuesta honesta e incompleta vale más que
  un número inventado, y hay que decírselo explícitamente.
- **Aceptar el formato que ya tengan.** Si mandan su propio informe o una
  planilla distinta, sirve. No los hagas rehacer el trabajo.
- **Poner una fecha concreta**, no «a la brevedad».
- **Ofrecer ayuda.** Un llamado de 15 minutos completando el cuestionario juntos
  resuelve más que tres correos de recordatorio.
- **No amenazar.** Condicionar la relación comercial al resultado hace que
  inventen números. Se condiciona a que haya respuesta, no a que sea buena.

## Registrar lo que llega

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" proveedores registrar --nombre "Envases del Sur" --entrego si --huella-declarada 0,85 --unidad "kg CO2e por kg" --calidad reportado --certificaciones "ISO 14001, ISO 9001"
```

Dos cosas que nunca deben faltar:

- **La unidad.** «0,85» no significa nada. «0,85 kg CO2e por kilo de envase» sí.
  Si no viene la unidad, pregúntala antes de guardar.
- **La calidad del dato**: `estimado` (lo calcularon ellos con un supuesto),
  `reportado` (viene de sus facturas o medidores) o `verificado` (lo revisó un
  tercero independiente). De eso depende cuánto se puede afirmar después.

Anota también el año del dato. Una huella de 2021 usada como si fuera de 2025 es
un error que un auditor detecta de inmediato.

## Reemplazar estimaciones por datos primarios en el alcance 3

El alcance 3 casi siempre parte estimado por gasto: se multiplica lo que se
gastó en una categoría por un factor promedio. Sirve para saber **dónde está el
bulto**, no para fijar metas ni para prometer reducciones.

El camino de mejora, categoría por categoría:

1. Calcula el alcance 3 como esté (ver skill `alcance-3`).
2. Mira qué categorías explican la mayor parte.
3. Solo en esas, cambia el método: pide al proveedor su huella por unidad y
   multiplícala por las unidades compradas, en vez de usar el factor por gasto.
4. Deja escrito el cambio de método en el informe. Si la huella baja porque
   cambió el método y no porque bajaron las emisiones, **hay que decirlo**: no
   es una reducción.
5. Para el resto de las categorías, la estimación se queda como está. Es
   suficiente y está bien declararlo así.

Regla dura: **un dato primario reemplaza a una estimación solo si es comparable**
(misma unidad, mismo período, mismo alcance de lo que incluye). Si el proveedor
entrega solo su alcance 1 y 2, eso no es la huella completa del producto; anótalo
como supuesto.

## Cuando un proveedor no responde

No es personal y no siempre es desinterés: muchas veces no tienen el dato ni a
quién preguntarle. El orden que funciona:

1. **Recordatorio a los 10 días**, corto y por el mismo canal.
2. **Llamado telefónico.** Ahí se sabe si el problema es tiempo, si no entienden
   qué se les pide o si no tienen el dato. Cada caso se resuelve distinto.
3. **Ofrecer completar el cuestionario juntos** en una llamada.
4. **Bajar la exigencia**: si no tienen la huella, pedir solo el consumo de
   electricidad y de combustible por unidad. Con eso se puede estimar y se les
   devuelve el cálculo, que a ellos también les sirve.
5. **Si después de todo eso no hay respuesta**: se deja anotado como «sin datos»,
   se sigue con la estimación por gasto y se declara en el informe qué parte de
   la cadena quedó estimada. Eso es una respuesta legítima y transparente.
6. Solo si es un proveedor grande y estratégico vale la pena escalar la
   conversación a quien lleva la relación comercial.

Lo que **no** hay que hacer: inventar el dato, copiar el de otro proveedor
parecido sin decirlo, o presentar una estimación como si fuera un dato entregado
por el proveedor.

## Informe y seguimiento

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" proveedores informe
```

Entrega una página HTML con quién pesa más, quién entregó datos (verde) y quién
no (rojo), y qué parte del impacto ya está cubierta con datos propios. Es el
documento para mostrar en una reunión de gerencia: deja claro que el trabajo
pendiente está acotado a unos pocos nombres.

Buena meta para el primer año: **cubrir con datos primarios el 50 % del impacto**,
no el 100 % de los proveedores.

## Privacidad

Los nombres, correos y teléfonos de los contactos son **datos de personas**.

- Se quedan en `empresas/<empresa>/seguimiento/proveedores.json`, en este
  computador. No se publican ni se suben a internet.
- Guarda solo lo necesario para la gestión: nombre, cargo y un canal de contacto.
  No anotes datos personales que no se usen.
- No publiques el nombre de un proveedor junto con su huella sin su acuerdo
  previo, y no compartas su dato con otras empresas de su rubro. Eso está dicho
  en la carta que se les envía: hay que cumplirlo.
- Si un proveedor pide que se borren sus datos de contacto, bórralos.

## Lo que nunca se hace

- Prometerle a un proveedor que «esto lo va a ayudar a vender más». No lo sabes.
- Afirmar que la ley lo obliga a responder si no es cierto para su caso.
- Usar el dato de un proveedor para un informe público sin avisarle.
- Cambiar un número que entregó el proveedor porque «se ve raro»: si se ve raro,
  se pregunta.
