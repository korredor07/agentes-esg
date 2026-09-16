---
name: greenwashing
description: Revisar afirmaciones ambientales antes de publicarlas, para que no sean engañosas ni sancionables. Úsala cuando quieran poner «ecológico», «sustentable», «carbono neutral», «biodegradable» o un sello en una etiqueta, web, catálogo, licitación o publicación; cuando preparen una campaña o un anuncio de una meta climática; o cuando pregunten qué se puede decir y qué no.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Revisar una afirmación ambiental antes de publicarla

La regla que ordena todo: **si no lo puedes demostrar con un documento, no lo
publiques**. No es una cuestión de imagen; hoy es riesgo de multa y de contrato.

## 1. Por qué importa ahora

**Unión Europea.** La Directiva (UE) 2024/825 (de 28 de febrero de 2024, publicada
el 6 de marzo de 2024) modificó las reglas de prácticas comerciales desleales.
Su plazo de transposición fue el **27 de marzo de 2026** y **se aplica desde el
27 de septiembre de 2026**. [VERIFICADO] Afecta a la empresa si vende a la UE,
si su etiqueta o su web llegan a un consumidor europeo, o si su cliente europeo
le traspasa la exigencia.

**Chile.** No hace falta una ley nueva: la **Ley N° 19.496** de protección de
los derechos de los consumidores **ya sanciona hoy** la publicidad falsa o
engañosa. Según su artículo 24 [VERIFICADO]:

| Situación | Multa máxima |
|---|---|
| Infracción general | 300 UTM |
| Publicidad falsa o engañosa difundida por medios de comunicación social, respecto de los elementos del artículo 28 | 1.500 UTM |
| **Si esa publicidad incide sobre la salud, la seguridad o el medio ambiente** | **2.250 UTM** |

Una afirmación ambiental falsa cae justo en el tramo agravado. Además, las
condiciones objetivas que se comunican en la publicidad **se entienden
incorporadas al contrato**: lo que se promete pasa a ser exigible por el
consumidor. (UTM es una unidad que se reajusta cada mes; **no conviertas a pesos
ni estimes montos**.)

> **[NO VERIFICADO]** en la investigación del proyecto: el texto literal de los
> artículos 28 y 28 A, y la existencia de guías o pronunciamientos del SERNAC
> específicos sobre alegaciones ambientales. **No afirmes que existe una guía
> del SERNAC sobre greenwashing.**

> **[NO VERIFICADO]** para **Perú**: este proyecto todavía no tiene verificadas
> las reglas peruanas de publicidad y protección al consumidor. Di que el
> criterio técnico de esta skill igual sirve, pero que la base legal peruana hay
> que confirmarla antes de citarla.

**Directiva europea de alegaciones ecológicas (Green Claims):** su tramitación
figura **«en curso»**, en primera lectura. **No digas que fue aprobada ni que
fue retirada.** La norma que aplica hoy en la UE es la Directiva 2024/825
traspuesta a la ley de cada país.

## 2. Afirmaciones que están prohibidas en toda circunstancia (UE)

Estas no admiten matices ni «depende del caso»: la directiva las prohíbe
siempre. [VERIFICADO]

| Práctica | En palabras simples |
|---|---|
| Alegación **genérica** | Decir «ecológico», «verde», «respetuoso con el medio ambiente» sin poder demostrar un desempeño ambiental excelente y reconocido |
| Alegación sobre **todo** cuando cubre una **parte** | Decir que el producto o la empresa es sostenible cuando la evidencia cubre solo un componente, una planta o una línea |
| **Neutralidad basada solo en compensación** | Afirmar impacto climático neutro, reducido o positivo apoyándose exclusivamente en compra de créditos |
| **Sello sin sistema detrás** | Mostrar una etiqueta de sostenibilidad que no se basa en un sistema de certificación ni fue establecida por una autoridad pública |
| **Vender una obligación legal** como ventaja | Presentar como rasgo distintivo algo que la ley exige a todos los productos de esa categoría |

Y se evalúan **caso a caso** como engañosas:

- **Promesas a futuro** («seremos neutrales en 2030»): solo se admiten si se
  apoyan en compromisos claros, objetivos, **públicos** y verificables, con un
  **plan de implementación detallado y realista** y **verificación periódica por
  un tercero experto independiente**.
- **Comparaciones**: hay que informar el método de comparación, qué productos se
  comparan y de qué proveedores, y cómo se mantiene actualizada esa información.
- **Beneficios irrelevantes**: publicitar una ventaja que no se deriva de
  ninguna característica real del producto o del negocio.
- Engañar sobre **características ambientales, durabilidad, reparabilidad o
  reciclabilidad** cuenta como engaño sobre una característica principal.

## 3. Criterios técnicos de las autodeclaraciones ambientales

La familia ISO de etiquetado ambiental (autodeclaraciones, tipo II) plantea que
una declaración debe ser **exacta, verificable, pertinente y no engañosa**, debe
ser **específica** sobre a qué se refiere (producto, envase, componente o
servicio), no debe basarse en la ausencia de una sustancia que el producto nunca
contuvo o que ya está prohibida, y debe poder sustentarse con evidencia
**disponible antes** de hacerse pública.

> **[NO VERIFICADO]**: el contenido de las normas ISO no pudo confirmarse en la
> fuente oficial durante la investigación del proyecto. Úsalo como criterio
> técnico de sentido común y **no cites números de norma ni ediciones como si
> fueran verificados**.

Los mismos criterios, en forma de preguntas, funcionan como lista universal:
¿es veraz y exacta?, ¿es clara y sin ambigüedad?, ¿omite algo importante?, ¿la
comparación es justa?, ¿considera todo el ciclo de vida?, ¿está fundamentada?

## 4. En vez de decir X, di Y

| En vez de decir | Di | Por qué |
|---|---|---|
| «Producto ecológico» | «Envase con 60 % de material reciclado, medido en 2025» | Genérico prohibido; lo específico y medido sí se puede |
| «Amigable con el medio ambiente» | «Usamos 30 % menos agua por unidad que en 2023» | Vago y no demostrable |
| «Empresa carbono neutral» (comprando créditos) | «Redujimos 18 % nuestras emisiones entre 2023 y 2025 y compensamos las 400 tCO2e restantes con créditos de [proyecto]» | La neutralidad basada solo en compensación está prohibida |
| «100 % reciclable» | «La botella es reciclable donde exista recolección de PET; la tapa y la etiqueta no lo son» | La afirmación cubría todo y la evidencia cubría una parte |
| «Seremos neutrales en 2030» | «Meta: reducir 42 % los alcances 1 y 2 al 2030 respecto de 2025. Plan y avance publicados en [dirección], revisados anualmente por un tercero» | Promesa a futuro sin plan público ni verificación |
| «Sin químicos» | «Sin [sustancia concreta] añadida» | Todo producto tiene química; la frase no significa nada |
| «Libre de plomo» (cuando la ley ya lo prohíbe) | No decirlo, o «cumple la normativa que prohíbe el plomo en este uso» | Vender como ventaja una obligación legal |
| «Biodegradable» | «Se degrada en condiciones de compostaje industrial en X meses, según [ensayo y fecha]» | Sin condiciones ni plazo, induce a error |
| Sello propio con una hoja verde | Retirarlo, o mostrar la certificación real con su emisor y su esquema | Sello sin sistema de certificación detrás |
| «El más sustentable del mercado» | «Nuestro consumo de agua por unidad es 30 % menor que el promedio del rubro según [estudio, año y método]» | Comparación sin método ni base publicada |
| «Comprometidos con el planeta» | Nada, o una acción concreta con su cifra | Beneficio irrelevante, no se deriva de nada real |
| «Producto sustentable» | «Producto elaborado con energía 100 % renovable certificada en la planta de [lugar]» | Genérico prohibido; lo acotado y respaldado sí |

Regla para reescribir: **dato + alcance + periodo + fuente**. Si falta una de
las cuatro, la frase todavía no se puede publicar.

## 5. Procedimiento para revisar un texto de marketing

1. **Pide el texto completo y dónde se va a publicar**: etiqueta, web, catálogo,
   licitación, redes sociales. Y si llega a la Unión Europea.
2. **Subraya cada afirmación ambiental o social por separado.** Una frase puede
   tener tres.
3. **Clasifica cada una**: genérica, específica, promesa a futuro, comparación,
   sello o neutralidad climática.
4. **Pide la evidencia de cada una, por su nombre**: el ensayo, la factura, el
   certificado, el cálculo. Si no existe el documento, la afirmación sale. No
   hay término medio.
5. **Compara alcance de la afirmación con alcance de la evidencia.** Si la
   evidencia es de una planta y la frase habla de la empresa, acota la frase.
6. **Descarta lo que es obligación legal** y lo que es un beneficio irrelevante.
7. **Si es una promesa a futuro**, exige plan publicado, hitos y verificación
   independiente periódica. Si no los hay, no se anuncia todavía.
8. **Si es una comparación**, exige método, qué se compara y cómo se actualiza.
9. **Busca lo que se está callando**: un impacto negativo importante que el
   lector consideraría al comprar. Si lo hay, se menciona o no se publica.
10. **Reescribe** con dato, alcance, periodo y fuente, y entrega un semáforo:

| Semáforo | Qué significa |
|---|---|
| Verde | Se puede publicar tal como quedó |
| Amarillo | Se publica solo con la reformulación propuesta |
| Rojo | No se publica: falta evidencia o está prohibida |

11. **Deja el respaldo guardado** antes de publicar:

```bash
python .claude/motor/esg.py evidencia registrar --archivo datos/respaldo-afirmacion-envase.pdf --descripcion "Certificado de contenido reciclado del envase, 2025" --responsable "Nombre de quien lo aprueba"
```

## 6. Los dos casos que más aparecen

**«Queremos poner carbono neutral».** El orden correcto es medir, reducir y solo
al final compensar lo que queda, con créditos de calidad; la compensación es
para el remanente, no un reemplazo de la reducción. Y hay que ser explícito: una
certificación de neutralidad **no protege** frente a la prohibición europea si
la reducción real fue marginal y la neutralidad descansa en créditos comprados.

```bash
python .claude/motor/esg.py huella calcular
python .claude/motor/esg.py meta validar
```

**«Queremos anunciar nuestra meta».** Antes de publicarla, revisa con la skill
`metas-net-zero` que tenga año base, alcance cubierto, metodología, supuestos y
plan. Si la probabilidad de cumplirla es baja, dilo internamente antes de que se
anuncie:

```bash
python .claude/motor/esg.py meta probabilidad
```

## Cuidados

- **Esto es orientación, no asesoría legal.** Una campaña grande o una etiqueta
  que va a la UE se revisa además con un abogado.
- **No inventes artículos, fechas ni montos.** Lo que no está verificado en la
  investigación del proyecto, se dice que no está verificado.
- No conviertas UTM a pesos: el valor cambia cada mes.
- Sé firme pero no moralista: el objetivo es que puedan comunicar lo bueno que
  sí hicieron, **con respaldo**. Casi siempre hay una frase honesta y vendible
  esperando debajo de la exagerada.
- Si la empresa ya publicó algo indefendible, lo primero es **corregirlo o
  bajarlo**, y dejar registro de cuándo se corrigió.
