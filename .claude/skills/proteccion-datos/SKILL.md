---
name: proteccion-datos
description: Protección de datos personales para empresas, sobre todo la Ley 21.719 de Chile y su entrada en vigencia. Úsala cuando pregunten qué pueden hacer con los datos de sus trabajadores o clientes, por la nueva ley de datos personales, por la política de privacidad, por el consentimiento, por cámaras o reloj con huella, por bases de correos para marketing, o cuando haya una filtración, un correo enviado con todos los destinatarios a la vista, o alguien que pide que borren sus datos.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Protección de datos personales (Ley 21.719, Chile)

## Lo primero que hay que decir

La **Ley 21.719** —que regula el tratamiento de datos personales y crea la
**Agencia de Protección de Datos Personales**— se **publicó el 13 de diciembre
de 2024**. Su disposición transitoria primera dice que entra en vigencia **el
primer día del mes 24 posterior a la publicación**, lo que da el **1 de
diciembre de 2026**.

> La **regla de cómputo está verificada en el texto legal**; la fecha de
> calendario es el resultado de aplicarla. Dilo así si alguien necesita la fecha
> para una decisión formal.

Dos cosas que quitan pánico y dan urgencia a la vez:

- **No es un régimen nuevo desde cero**: Chile ya tenía la Ley 19.628. Lo que
  cambia es que ahora hay una **Agencia con poder para fiscalizar y multar**, y
  un **Registro Nacional de Sanciones** que hace pública la sanción.
- Hay una ventana de aterrizaje: durante los **primeros 12 meses** de vigencia,
  las **empresas de menor tamaño** (según la Ley 20.416) pueden recibir
  **amonestación escrita en lugar de sanción** (transitoria sexta). Es tiempo
  para ordenarse, no una exención.

Sobre multas, si preguntan: la ley distingue infracciones **leves (hasta 400
UTM)**, **graves (400 a 2.000 UTM)** y **muy graves (2.000 a 10.000 UTM, o hasta
el 3% de los ingresos anuales si ese monto es mayor)**. La **base exacta de ese
3%** —ingresos totales o solo de la línea de negocio infractora— **hay que
contrastarla con el texto final**: no la afirmes.

## Regla de privacidad de esta skill

El motor **no pide ni guarda datos personales reales**. Solo guarda la
**descripción de los tratamientos**: qué categorías de datos, para qué, quién
accede, dónde están, cuánto duran. Si la persona te dicta un correo, un RUT o un
nombre, **no lo guardes**: reemplázalo por la categoría («correo de contacto de
clientes»). El motor además rechaza lo que parezca un dato real y explica por
qué.

Dilo en voz alta la primera vez: «no necesito ver ningún dato de sus
trabajadores ni de sus clientes para esto».

## Las obligaciones de una empresa común

Una pyme que tiene trabajadores, clientes y proveedores ya está tratando datos
personales. Estas son las obligaciones que le van a llegar:

| Obligación | Qué significa en la práctica |
|---|---|
| **Tener una base de licitud para cada uso** | Poder responder «¿por qué puedo usar este dato?»: la persona autorizó (consentimiento), hay un contrato, lo exige una ley, o hay un interés legítimo que se puede justificar. |
| **Registro de actividades de tratamiento** | Es **obligatorio**. La lista de todos los usos de datos, con responsable, operaciones, categorías de datos y de personas, finalidades, destinatarios, plazo de conservación y medidas de seguridad. Debe estar disponible para la Agencia. |
| **Deber de información** | Una política de tratamiento **permanentemente disponible**, con fecha y versión. |
| **Seguridad** | Medidas técnicas y organizativas acordes al riesgo: control de accesos, claves, respaldos, cifrado, y verificar cada cierto tiempo que funcionan. |
| **Responder derechos** | Acceso, rectificación, supresión, oposición, portabilidad y bloqueo. Gratuitos. El acceso es gratuito al menos una vez por trimestre. El **bloqueo temporal tiene plazo de respuesta de 2 días hábiles**. |
| **Notificar vulneraciones** | Registrar la filtración y notificarla sin dilaciones indebidas (ver más abajo). |
| **Evaluación de impacto** | Obligatoria en cuatro casos de alto riesgo (ver más abajo). |
| **Transferencias fuera del país** | Informarlas y respaldarlas con una garantía: cláusulas contractuales tipo, normas corporativas vinculantes, consentimiento informado, cifrado o seudonimización. |

Sobre el **consentimiento**: debe ser libre, informado, específico, previo e
inequívoco, y **revocable en cualquier momento sin explicar por qué**. La ley
**presume que no es libre** cuando se pide dentro de un contrato para el que no
era necesario. Traducción: la cláusula escondida en el contrato de trabajo que
autoriza «todo uso» no sirve.

Sobre el **delegado de protección de datos**: la figura existe, pero **los
criterios exactos que obligan a designarlo en el sector privado no están
confirmados** en la investigación de este proyecto. No le digas a nadie que está
o que no está obligado: dile que **hay que confirmarlo** en el texto vigente y en
las instrucciones de la Agencia.

Lo que sí conviene mencionar: la ley permite adoptar un **modelo de prevención de
infracciones certificado** (políticas, evaluación periódica de riesgos,
protección desde el diseño y por defecto, capacitación y auditorías). Su adopción
**genera presunción de cumplimiento** y puede **atenuar o incluso exonerar** de
sanciones.

## Datos sensibles: por qué importan tanto en personas

Son **datos sensibles** los que revelan origen étnico o racial, afiliación
política, sindical o gremial, **situación socioeconómica**, convicciones
ideológicas o filosóficas, creencias religiosas, **datos de salud**, perfil
biológico, **datos biométricos**, vida sexual, orientación sexual e identidad de
género.

Ojo con dos particularidades chilenas:

- La **situación socioeconómica es dato sensible** en Chile. Es una diferencia
  relevante frente a Europa y toma por sorpresa a mucha gente.
- El **reloj con huella o reconocimiento facial** para marcar asistencia trata
  **datos biométricos**: requiere consentimiento e información sobre el sistema,
  la finalidad específica, el período de uso y cómo se ejercen los derechos.

Por eso **recursos humanos es el área más expuesta** de cualquier empresa:
licencias médicas y estados de salud, afiliación sindical, descuentos y
cargas familiares, resultados de exámenes preocupacionales, el reloj biométrico,
y el canal de denuncias. Como norma general, los datos sensibles requieren
**consentimiento expreso**, con excepciones acotadas —entre ellas el **ejercicio
de derechos laborales**—; los de salud tienen además reglas propias.

Preguntas concretas que sirven para abrir el tema con una pyme:

- «¿Dónde guardan las licencias médicas y quién puede abrir esa carpeta?»
- «¿El reloj para marcar asistencia usa huella o cara?»
- «Los currículums de quienes postularon y no quedaron, ¿siguen guardados?»
- «¿Alguien de fuera de la empresa ve las liquidaciones de sueldo?»

## Cómo trabajas esto

### 1. Armar el inventario

```bash
python .claude/motor/esg.py datos_personales inventario --empresa mi-empresa
```

Entrega la guía, las preguntas en lenguaje cotidiano y la lista de tratamientos
que **siempre se olvidan** (postulantes, cámaras, canal de denuncias, respaldos,
base de correos de marketing).

Recorre **área por área**, no todo de una vez. Empieza por personas.

### 2. Registrar cada tratamiento

```bash
python .claude/motor/esg.py datos_personales registrar --nombre "Ficha de trabajadores" --area Personas --titulares "trabajadores y postulantes" --categorias-datos "identificación, contacto, contrato, licencias médicas" --finalidad "administrar la relación laboral" --base-licitud contrato --destinatarios "jefatura de personas y contadora externa" --donde-se-guarda "carpeta del servidor" --conservacion "mientras dure el contrato y el plazo legal posterior" --sale-del-pais no --datos-sensibles si
```

Bases de licitud válidas: `consentimiento`, `contrato`, `obligacion_legal`,
`interes_legitimo`, `obligaciones_economicas`, `defensa_derechos`.

Marcas opcionales que activan las alertas de alto riesgo: `--datos-sensibles`,
`--masivo`, `--perfilado`, `--videovigilancia`, `--sale-del-pais`.

Se puede volver a llamar con el **mismo nombre** para completar lo que falte.

### 3. Evaluar qué falta

```bash
python .claude/motor/esg.py datos_personales evaluar --deber-informacion no_cumple --seguridad parcial
```

Revisa qué tratamientos exigirían **evaluación de impacto** y en qué está la
empresa respecto de las cuatro obligaciones transversales: deber de información,
seguridad, respuesta a derechos y notificación de vulneraciones.

La **evaluación de impacto es obligatoria** cuando el tratamiento:

1. evalúa de forma sistemática a las personas con decisiones automatizadas que
   tienen efectos jurídicos o similares;
2. es masivo o a gran escala;
3. observa o monitorea sistemáticamente una **zona de acceso público**; o
4. trata **datos sensibles** amparándose en alguna excepción al consentimiento.

### 4. Entregar los borradores

```bash
python .claude/motor/esg.py datos_personales documento --tipo politica-privacidad
python .claude/motor/esg.py datos_personales documento --tipo registro-actividades
python .claude/motor/esg.py datos_personales documento --tipo procedimiento-derechos
python .claude/motor/esg.py datos_personales informe
```

Los documentos son **borradores con la estructura exigida**, con lo propio de la
empresa entre corchetes. No son documentos listos para publicar ni para firmar:
el paso siguiente es completarlos y revisarlos con la asesoría jurídica.

El registro de actividades se genera **con lo que ya esté registrado** en el
inventario, así que conviene dejarlo para el final.

## Si hay una filtración

Esto es urgente y va antes que cualquier otra cosa. El orden:

1. **Contener**: cortar el acceso, cambiar claves, aislar el equipo o el
   sistema. Primero se detiene la hemorragia.
2. **Registrar**: la ley obliga a dejar registro de la vulneración con su
   naturaleza, sus efectos, las categorías de datos, el **número aproximado de
   personas afectadas** y las medidas de gestión adoptadas.
3. **Notificar** por los medios más expeditos posibles y **"sin dilaciones
   indebidas"**. **La ley chilena no fija un plazo en horas.** No inventes uno.
4. **Avisar a las personas afectadas** —esto es obligatorio— cuando la
   vulneración afecta **datos sensibles**, **datos de menores de 14 años** o
   **datos financieros y bancarios**. En lenguaje claro y sencillo, diciendo qué
   datos se vieron afectados, qué consecuencias puede tener y qué se está
   haciendo. Si es imposible contactar a cada persona, mediante aviso en un
   medio de comunicación masivo de alcance nacional.
5. **Dejar constancia de todo**: es lo que después acredita que se actuó.

Casos cotidianos que también son vulneraciones y la gente no reconoce como
tales: el correo masivo enviado con todos los destinatarios visibles en el
campo "Para", la planilla de sueldos compartida por error, el notebook robado
sin cifrar, la carpeta de red abierta a toda la empresa.

**Involucra desde el primer minuto a la asesoría jurídica.** Tú ordenas el
procedimiento; no redactas la comunicación oficial a la autoridad.

## Perú y Europa, en corto

**Perú.** Rige la **Ley 29733** con el Reglamento aprobado por el **DS
016-2024-JUS**, publicado el 30 de noviembre de 2024 y vigente a los 120 días
calendario de su publicación. Tres diferencias que importan:

- **Plazo duro de 48 horas** para notificar un incidente de seguridad a la
  Autoridad Nacional y a la persona afectada (con explicación de los motivos si
  se excede). Chile, en cambio, dice «sin dilaciones indebidas».
- **Oficial de Datos Personales** obligatorio en ciertos casos, con un
  **cronograma escalonado por tamaño**: empresas con ventas sobre 2.300 UIT
  primero, luego medianas, pequeñas y microempresas. Sus datos de contacto se
  publican y se comunican a la autoridad dentro de los 15 días siguientes a la
  designación.
- **Inscripción de los bancos de datos** en el Registro Nacional de Protección de
  Datos Personales, y comunicación del flujo transfronterizo.

Los **montos de las multas peruanas** (art. 39 de la Ley 29733, en UIT) **no
están verificados** en la investigación de este proyecto. **No des cifras**: di
que hay que confirmarlas en la norma vigente y con el valor de la UIT del año.

**Europa.** El reglamento europeo de protección de datos (RGPD) **no está
cubierto** por la investigación de este proyecto. Lo único que esta anota es que,
a diferencia de Chile, el RGPD sí fija un plazo en horas para notificar. Si la
empresa trata datos de personas que están en la Unión Europea —por venta directa,
por una filial o por una casa matriz—, dile que **eso se revisa con asesoría
especializada** y no improvises el detalle.

## Límites honestos

- Esto es **orientación de gestión, no asesoría legal**.
- La **numeración de los artículos** puede moverse: la Ley 21.719 opera
  insertando artículos en la Ley 19.628, y conviene contrastarla con el texto
  refundido una vez vigente.
- El **umbral de 250 trabajadores** para simplificar el registro de actividades
  conviene contrastarlo con el texto final.
- Los **criterios del delegado de protección de datos** en el sector privado
  están sin confirmar.
- No revises ni pidas ver los datos de la empresa para "diagnosticar". Con la
  descripción del tratamiento basta, y es lo correcto.
