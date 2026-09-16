---
name: union-europea
description: Qué le exige Europa a un exportador de Chile o Perú: lo que puede pedirle un cliente europeo (CSRD y el tope VSME), el arancel de carbono CBAM, el recargo del flete marítimo y el reglamento de deforestación. Úsala cuando mencionen que exportan a Europa, que un cliente europeo les mandó un cuestionario de sostenibilidad, que les hablaron de CBAM, CSRD, VSME, CSDDD, EUDR o taxonomía, o cuando pregunten si les afecta alguna norma europea.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Lo que Europa le pide a un exportador latinoamericano

Lo primero, y es la mejor noticia que puedes dar: **ninguna de estas normas
obliga directamente a una empresa chilena o peruana**. Todas obligan a alguien
en Europa —el importador, el cliente, la naviera— y ese alguien traslada la
exigencia aguas arriba.

Eso cambia la conversación por completo. No hay que "inscribirse" en nada ni
"declarar" ante una autoridad europea. Hay que **tener los datos listos cuando
el cliente los pida**, porque si no llegan, el europeo usa valores por defecto
que siempre salen más caros, o cambia de proveedor.

## 1. Empieza por el mapa

```bash
python .claude/motor/esg.py europa aplica
```

Entrega seis mecanismos con semáforo: le aplica, hay que confirmarlo, o queda
fuera. Si algo queda en «revisar», pregunta lo que falte —de a una pregunta— y
guárdalo:

```bash
python .claude/motor/esg.py europa aplica --exporta-bienes-cbam si --envia-por-mar si
```

Preguntas que resuelven casi todo:

| Pregunta técnica | Cómo preguntarla |
|---|---|
| ¿Exporta bienes CBAM? | «¿Le venden a Europa acero, aluminio, cemento, fertilizantes o hidrógeno?» |
| ¿Exporta materias primas EUDR? | «¿Le venden a Europa café, cacao, madera, soya, palma, caucho o cuero?» |
| ¿Envía por mar? | «¿La carga viaja a Europa en barco?» |
| ¿Tiene filial en la UE? | «¿Tienen oficina o empresa propia en Europa, o venden a través de un importador?» |

Vender a un intermediario **no** los salva: la exigencia baja igual por la
cadena.

## 2. Lo que sí le va a llegar: el cuestionario del cliente

El cliente europeo grande está obligado a reportar sostenibilidad (**CSRD**) y a
hacer diligencia debida (**CSDDD**). Para eso pide datos a sus proveedores. Esa
es, con diferencia, la vía por la que Europa llega a una pyme de la región.

Qué cambió en 2026, y conviene decirlo porque casi toda la información que hay
dando vueltas está desactualizada:

- La **Directiva (UE) 2026/470** ("Ómnibus I", de 24 de febrero de 2026) subió el
  umbral de la CSRD a **más de 450 millones de euros de facturación Y más de
  1.000 empleados**, los dos a la vez. Muchos clientes europeos medianos que el
  año pasado pedían datos **ya no están obligados**.
- La misma directiva subió la CSDDD a **5.000 empleados y 1.500 millones de
  euros**, y su aplicación quedó para el **26 de julio de 2029**.
- Los clientes que **sí** quedan obligados son los grandes compradores, y su
  exigencia va a ser más estructurada y más difícil de esquivar.

## 3. El tope VSME: el techo de lo que pueden exigirle

Esta es la novedad más útil para una pyme proveedora, y hay que explicarla bien
porque se presta a malentendidos.

La Directiva 2026/470 creó las **"empresas protegidas"**: las que no superan una
media de **1.000 empleados**. Un cliente sujeto a CSRD **no puede exigirles**
información que exceda los límites del estándar voluntario **VSME**, y la
empresa protegida **puede negarse** a entregar lo que se pase de ahí.

Cómo se lo cuentas a la persona:

> «Su cliente puede pedirle lo que está en el estándar VSME. Si le manda un
> cuestionario de 300 preguntas con desgloses que ni siquiera lleva, usted tiene
> argumento para acotarlo.»

Y de inmediato los dos matices honestos, porque si no, genera falsas
expectativas:

1. **Es un techo regulatorio, no contractual.** Limita lo que el cliente puede
   exigir *por obligación legal*. Lo que se pacte en el contrato es otra cosa, y
   si el contrato ya está firmado, manda el contrato.
2. **Si el proveedor no está domiciliado en la Unión Europea, que pueda invocar
   ese derecho de negativa no está confirmado.** Depende de la transposición
   nacional y de la ley aplicable al contrato. Úsalo para negociar, no como
   escudo legal.

La estrategia práctica es siempre la misma: **preparar el paquete VSME como
posición por defecto** y negociar cualquier exceso. Ese mismo paquete sirve para
todos los clientes a la vez, y además es la base de CBAM, de los cuestionarios
de banca y de la debida diligencia.

Qué contiene ese paquete, en la práctica:

- Huella de carbono de **alcance 1 y 2**, con respaldo (skill `huella-carbono`).
- Alcance 3 solo en las categorías que el cliente considere materiales:
  típicamente transporte y bienes comprados (skill `alcance-3`).
- Datos básicos de personas: dotación, rotación, accidentabilidad, brecha
  salarial (skill `social-personas`).
- Políticas de gobernanza: ética, canal de denuncias, proveedores.

## 4. Cuándo derivar a otra skill

| Si aparece esto | Deriva a |
|---|---|
| Exportan acero, aluminio, cemento, fertilizantes, hidrógeno o electricidad | `cbam` |
| Les llegó un "ETS surcharge" o "recargo de emisiones" en el flete | `maritimo-ets` |
| Exportan café, cacao, madera, soya, palma, caucho o cuero | `eudr` |
| Piden la huella de carbono | `huella-carbono` |
| Piden datos sociales | `social-personas` |
| Quieren saber qué normas chilenas o peruanas les aplican | `brechas-cumplimiento` |

Para dejar todo en un documento que puedan mandarle al cliente o al directorio:

```bash
python .claude/motor/esg.py europa informe
```

## 5. Taxonomía de la UE, en dos frases

Aparece mucho en conversaciones de financiamiento. **No impone obligaciones a
una empresa no europea**: su efecto es que los fondos y bancos europeos la usan
como referencia para calificar inversiones. Para un proyecto latinoamericano
(hidrógeno verde, transmisión, forestal, minería), el filtro que suele fallar no
son los criterios técnicos sino las **garantías mínimas** —relaciones laborales,
consulta indígena, cadena de suministro— y el **DNSH de agua y biodiversidad**.
Ahí conviene concentrar la evidencia.

## 6. España: ojo con esto

Si el cliente es español y es mediano, puede seguir obligado por la **Ley
11/2018** de información no financiera, que alcanza desde **250 trabajadores** —
mucho más abajo que la CSRD. Y **ahí el tope VSME no lo ampara**, porque ese tope
vive dentro del régimen de la CSRD.

Si España ya transpuso la CSRD y qué pasa con la Ley 11/2018 **no está
confirmado** en la investigación del proyecto. Cuando el cliente sea español,
pregúntale directamente **bajo qué norma** está pidiendo los datos. Es una
pregunta legítima y ordena toda la conversación.

## Cómo conversas esto

- Empieza por lo que **no** aplica. Quita miedo y acota el trabajo.
- Nunca digas "usted está obligado a" si la obligación es del cliente europeo.
  Di «su cliente está obligado y se lo va a pedir a usted».
- Una norma por vez, y siempre con el «para qué le sirve»: un dato que sirve
  para el cliente europeo sirve también para el banco y para la licitación.
- Si preguntan por multas europeas: a ellos no los multa nadie en Europa. Lo que
  arriesgan es **perder al cliente**, que suele doler antes y más.

## Límites honestos

- Esto es **orientación**, no asesoría legal ni aduanera. La revisión final la
  hace un abogado, el agente de aduana o la asesoría del cliente.
- Los reglamentos europeos cambiaron mucho entre 2025 y 2026. Si encuentras
  material que cite umbrales de 250 empleados para la CSRD o el 5 % de sanción
  de la CSDDD, **está desactualizado**.
- Hay puntos que la investigación del proyecto no pudo confirmar contra el texto
  oficial (el umbral de la sucursal europea, el alcance del tope VSME fuera de
  la UE, el estado de la transposición española). El motor los marca como no
  confirmados y los muestra en el informe. No los des por ciertos.
