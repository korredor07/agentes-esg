# Guía de uso

Para personas que **no** trabajan en tecnología. Si algo de esta guía no se
entiende, escríbeselo al asistente: está hecho para explicar.

## 1. Lo que necesitas la primera vez

1. **Claude instalado** en tu computador (Windows, Mac o Linux), con cuenta de
   pago: <https://claude.ai/download>
2. **La carpeta de Agentes ESG** descargada y descomprimida.
3. **Python**: si no lo tienes, el asistente te ofrece instalarlo en el primer
   uso. Es gratis, oficial y no toca tus archivos.

Abre Claude → pestaña **Code** → elige la carpeta `agentes-esg` → escribe
**hola**. Eso es todo.

## 2. Lo primero: registrar tu empresa

El asistente te hará unas ocho preguntas simples (nombre, país, a qué se
dedican, cuántas personas trabajan, cuántos locales tienen, por qué necesitas
esto, desde qué año quieres medir). Se demora unos diez minutos.

Con eso queda creada tu carpeta:

```
empresas/mi-empresa/
├── datos/           tus planillas y documentos
├── resultados/      los cálculos
├── reportes/        lo que puedes enviar o imprimir
├── evidencias/      los respaldos
└── seguimiento/     lo que está en curso
```

## 3. Los caminos más comunes

### «Un cliente me pide la huella de carbono»

1. Dile al asistente: **«quiero medir la huella de carbono del año pasado»**.
2. Él crea una planilla Excel y te dice exactamente qué llenar.
3. Si tienes las boletas de luz y las facturas de combustible en PDF o foto,
   **pásaselas**: él las lee y llena la planilla por ti.
4. Te entrega el total en toneladas de CO₂ y un informe listo para enviar.

Lo que necesitas juntar: boletas de electricidad del año, litros de combustible
(vehículos, calderas, generadores), gas, y si hubo recargas de refrigerante.

### «Me llegó algo de la autoridad» o «no sé qué leyes me aplican»

Dile: **«¿qué normas le aplican a mi empresa?»**. Te hará preguntas de sí o no
(si venden productos envasados, si tienen caldera, si exportan) y te dirá qué
le aplica, con qué plazos y qué arriesga.

Si lo que llegó tiene plazo, dilo de inmediato: eso se atiende primero.

### «Me llegó una denuncia de acoso» (Chile)

Dile la fecha exacta en que la empresa recibió la denuncia. El asistente
calcula todos los plazos legales, te dice qué hay que hacer hoy y prepara los
documentos. **Involucra desde el primer día a tu asesoría jurídica y a tu
mutual**: el asistente ordena el proceso, no reemplaza a un abogado.

### «Necesito un reporte para una licitación o un banco»

Dile **«necesito un reporte de sostenibilidad»** y para quién es. Si faltan
datos, te dirá cuáles y en qué orden conviene conseguirlos.

### «Quiero saber cómo estamos en general»

Dile **«hazme un diagnóstico»**. Obtienes un puntaje, las brechas ordenadas por
riesgo y los tres primeros pasos concretos.

## 4. Cómo conversar con el asistente

- Escribe como le escribirías a una persona: «no entiendo qué me piden», «¿esto
  es caro?», «explícamelo más simple».
- Si te pierdes, escribe **ayuda**.
- Si algo salió mal, cuéntaselo: «esto no me cuadra, el mes de marzo se ve muy
  alto».
- Puedes cerrar y volver mañana: todo queda guardado en tu carpeta.

## 5. Dónde queda todo

Los archivos que puedes abrir y enviar están en `empresas/tu-empresa/reportes/`:

- Los **.html** se abren con doble clic en el navegador. Para enviarlos por
  correo, ábrelos y usa Ctrl+P → «Guardar como PDF».
- Los **.docx** se abren en Word y se pueden editar.
- Los **.xlsx** se abren en Excel.

## 6. Cuidados

- **Tus datos son tuyos**: se quedan en tu computador. No se suben a internet.
- **Haz copias de seguridad** de la carpeta `empresas/` (en un disco externo o
  en tu nube habitual). Si pierdes el computador, pierdes los datos.
- **Datos de personas**: sueldos, licencias y denuncias son sensibles. Guarda
  solo lo necesario y no compartas la carpeta completa.
- **Esto es orientación, no asesoría legal ni una auditoría.** Antes de
  presentar algo ante una autoridad, un cliente exigente o un auditor, que lo
  revise un profesional.
- Si el asistente dice que no tiene un dato verificado, **créele**: es
  preferible a un número inventado.

## 7. Preguntas frecuentes

**¿Tengo que saber de computación?** No. Solo conversar y, a lo más, llenar una
planilla de Excel.

**¿Sirve si soy una empresa chica?** Sí. De hecho está pensado para eso.

**¿Y si mis datos están incompletos?** Se calcula con lo que hay, se marca como
estimación y se anota qué falta. Eso es lo correcto; inventar no.

**¿Puedo usarlo para varias empresas?** Sí: cada una tiene su carpeta dentro de
`empresas/`. Al empezar dile con cuál trabajan hoy.

**¿Esto reemplaza a mi consultora?** No. Hace el trabajo repetitivo de medir,
ordenar y documentar. El criterio profesional y la firma de un especialista
siguen siendo necesarios cuando hay una obligación formal.

**¿Cómo lo actualizo?** Si lo bajaste como ZIP, descarga la versión nueva y
reemplaza la carpeta, conservando tu carpeta `empresas/`.
