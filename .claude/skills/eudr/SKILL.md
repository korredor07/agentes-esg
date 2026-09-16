---
name: eudr
description: EUDR, el reglamento europeo de productos libres de deforestación (Reglamento (UE) 2023/1115, aplazado y simplificado por el Reglamento (UE) 2025/2650). Úsala cuando exporten a Europa café, cacao, madera, celulosa, muebles, soya, aceite de palma, caucho, neumáticos, ganado o cuero, cuando les pidan geolocalización de predios o parcelas, declaración de diligencia debida, número de referencia de TRACES, o cuando mencionen deforestación, trazabilidad de origen o la fecha de corte de 2020.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# EUDR: productos libres de deforestación

Europa no deja entrar siete materias primas —ni lo que se hace con ellas— si
vienen de tierra deforestada después del **31 de diciembre de 2020**.

## ¿Le aplica?

Siete materias primas y sus derivados:

**ganado bovino** (y cuero), **cacao** (y chocolate), **café**, **palma
aceitera**, **caucho** (y neumáticos), **soya** y **madera** (y muebles,
tableros, pasta y papel).

Fuera del reglamento: fruta, uva, vino, pesca, cobre, harina de pescado.

```bash
python .claude/motor/esg.py europa eudr --producto cafe --pais PE --tamano-operador grande
```

## Los tres requisitos, que son acumulativos

Un producto solo entra a Europa si cumple **los tres** (artículo 3):

1. Está **libre de deforestación**: la tierra no fue deforestada después del
   **31 de diciembre de 2020**.
2. Se produjo **conforme a la legislación del país de producción**: uso del
   suelo, ambiental, laboral, derechos de terceros, tributaria.
3. Está amparado por una **declaración de diligencia debida** del operador
   europeo.

> El punto 1 sorprende a mucha gente: **da igual si la deforestación fue legal en
> el país**. La fecha de corte es absoluta. Si el predio se habilitó en 2022 con
> todos los permisos al día, ese café no entra a Europa.

## Chile tiene una ventaja concreta; Perú no

El **Reglamento de Ejecución (UE) 2025/1093**, de 22 de mayo de 2025, clasificó
los países por riesgo:

| País | Categoría | Qué significa |
|---|---|---|
| **Chile** | **Riesgo bajo** | **Diligencia debida simplificada**: basta con recopilar y conservar la información del artículo 9. No hay que hacer la evaluación (art. 10) ni la mitigación del riesgo (art. 11). Además, menos controles |
| **Perú** | Riesgo estándar | **Diligencia debida completa**: artículos 9, 10 y 11 |
| Brasil, Colombia | Riesgo estándar | Igual que Perú |
| Bielorrusia, Corea del Norte, Myanmar, Rusia | Riesgo alto | Escrutinio máximo |

Los países que no figuran en ninguna de las dos listas quedan en riesgo estándar.

Para un exportador **chileno de madera o celulosa** esto es un argumento
comercial real frente a competidores de riesgo estándar. Vale la pena decírselo:
**es una ventaja, no solo un requisito**. Pero la geolocalización y la prueba de
legalidad se siguen exigiendo.

Para **Perú** —café, cacao y madera— la diligencia es completa. El reto operativo
no es legal, es de terreno: **georreferenciar miles de parcelas pequeñas** en
cadenas minifundistas.

## Qué información hay que reunir

El motor entrega la lista separada en dos, porque así se levanta en la práctica:
unas cosas son por lote de exportación y otras por predio.

**Por predio** (se levanta una vez y se reutiliza):

| Dato | Detalle |
|---|---|
| **Geolocalización** | Coordenadas de latitud y longitud de **todas** las parcelas donde se produjo |
| **Libre de deforestación** | Prueba de que no hubo deforestación después del 31-12-2020: imágenes satelitales, títulos, estudios, certificaciones |
| **Legalidad** | Prueba de cumplimiento de la legislación del país de producción |

**Por lote de exportación** (cambia en cada envío):

| Dato | Detalle |
|---|---|
| Descripción | Producto y materias primas que contiene |
| **Cantidad** | En kilogramos |
| País de producción | De cada materia prima |
| Proveedor | Nombre, dirección y correo |
| Comprador | A quién se le vendió |

Todo se conserva **cinco años** (artículo 9).

Para el **ganado bovino** hay un requisito extra: los datos de **todos los
establecimientos donde estuvo el animal**, no solo el último.

## Cómo organizarlo sin morir en el intento

Esto es lo que más ayuda a una cooperativa o a un exportador con muchos
proveedores:

1. **Una planilla por predio**: código del predio, productor, superficie,
   coordenadas y evidencia de no deforestación. Se levanta una vez y se
   actualiza.
2. **Una planilla por lote**: kilos, predios de origen, proveedor, comprador y
   número de referencia de la declaración europea.
3. **Contratos con los proveedores** que obliguen a entregar coordenadas y
   pruebas. Sin eso, el lote no se puede declarar y queda fuera del envío.
4. **Empezar por los predios que concentran volumen**. No hay que tener el 100 %
   el primer día; hay que tener trazado lo que efectivamente se va a exportar.

## Quién declara

El **operador europeo** que pone el producto en el mercado presenta la
declaración de diligencia debida por el sistema de información **TRACES**, antes
de comercializar. Esa declaración genera un **número de referencia** que acompaña
al producto en la cadena.

**El exportador no declara.** Entrega la información y las pruebas. Pero sin
ellas el operador europeo no puede declarar, y sin declaración el producto no
entra.

## Fechas

| Quién importa | Desde cuándo |
|---|---|
| Grandes y medianas empresas | **30 de diciembre de 2026** |
| Micro y pequeñas empresas | **30 de junio de 2027** |
| Micro y pequeñas ya cubiertas por el reglamento anterior de la madera | 30 de diciembre de 2026 |

> Estas fechas vienen de la página oficial de la Comisión Europea y **no se
> pudieron confirmar contra el articulado** del texto consolidado tras el
> Reglamento (UE) 2025/2650. Sirven para planificar; para discutir un plazo, que
> el cliente europeo confirme la suya.

El EUDR ya se aplazó dos veces. No prometas que no volverá a moverse, pero
tampoco recomiendes esperar: levantar la geolocalización de cientos de predios
toma meses y no se improvisa.

## Qué arriesga el cliente europeo

Y por eso te lo va a exigir a ti:

- Multa de **al menos el 4 % de su facturación anual en toda la Unión Europea**.
- Decomiso de los productos y de los ingresos.
- Exclusión de contratación pública y de financiamiento público.
- Prohibición temporal de comercializar, si la infracción es grave o reiterada.

## Cómo conversas esto

- Empieza por si le aplica o no: seis de cada diez veces la respuesta es «no,
  usted exporta fruta» y ahí termina la conversación.
- Si es chileno y es madera: **la ventaja primero**. Riesgo bajo, diligencia
  simplificada, argumento de venta.
- Si es peruano y es café o cacao: directo al problema real, que es levantar
  coordenadas en muchos predios pequeños, y a cómo priorizar por volumen.
- Nunca digas «basta con un certificado». Ninguna certificación reemplaza la
  geolocalización ni la prueba de no deforestación; a lo más sirve como evidencia
  de apoyo.

## Límites honestos

- Esto es **orientación**, no asesoría legal. Quien decide qué acepta es el
  operador europeo que firma la declaración.
- El **formato exacto de la geolocalización** —cuántos decimales, punto o
  polígono según el tamaño del predio— **no está confirmado** tras las reformas
  de 2024 y 2025. Antes de mandar gente a terreno con GPS, pide al cliente
  europeo el formato que exige su sistema. Levantar mal los datos y repetirlo es
  caro.
- El contenido concreto de las simplificaciones del Reglamento (UE) 2025/2650
  tampoco está verificado.
- Los porcentajes de control de las autoridades europeas por categoría de riesgo
  no están confirmados: no cites cifras de probabilidad de inspección.
