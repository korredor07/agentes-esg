---
name: aseguramiento
description: Preparar a la empresa para que un tercero verifique su información de sostenibilidad. Úsala cuando pidan una verificación o auditoría externa, cuando un cliente, banco o casa matriz exija datos «verificados» o «asegurados», cuando pregunten por ISSA 5000, ISAE 3000, aseguramiento limitado o razonable, o cuando haya que armar el expediente que respalda las cifras de un reporte.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *)
---

# Prepararse para una verificación externa

Una verificación no revisa si la empresa es sostenible: revisa si **lo que dice
es cierto y se puede demostrar**. Casi todos los problemas de una primera
verificación no son de cálculo, son de respaldo: el número existe, pero nadie
puede llegar desde el número hasta el documento que lo origina.

Esta skill prepara ese camino. **Nosotros no verificamos nada**: eso lo hace un
tercero independiente, con su propio contrato y su propio costo.

## 1. Los dos niveles: limitado y razonable

| | **Limitado** | **Razonable** |
|---|---|---|
| Qué dice el informe | Una conclusión **en negativo**: «no encontramos nada que nos haga pensar que la información esté mal preparada» | Una **opinión positiva**: «en nuestra opinión, la información está preparada conforme al marco, en todo lo material» |
| Nivel de seguridad | Significativo, pero **sustancialmente menor** | Alto (nunca absoluto) |
| Qué hace el verificador | Procedimientos acotados | Pruebas de controles, muestreo, recálculos |
| Costo y esfuerzo | Menor | Bastante mayor |

*(Definiciones de ISAE 3000 revisada — [VERIFICADO] en la investigación del
proyecto.)*

**Cuál elegir:** casi todas las empresas de Chile, Perú y la UE parten con
**limitado**, y es lo razonable. El salto a razonable no se trata de que el
número final esté bien: exige que los **controles internos** sobre los datos ESG
sean auditables. Si la empresa aún llena planillas a mano, el salto es
prematuro.

## 2. Qué normas existen

| Norma | De qué trata | Vigencia |
|---|---|---|
| **ISAE 3000 (Revisada)** | Encargos de aseguramiento distintos de la auditoría de información financiera histórica. Ha sido la norma de referencia para verificar reportes de sostenibilidad | Encargos cuyo informe lleve fecha del **15 de diciembre de 2015** en adelante |
| **ISAE 3410** | Encargos de aseguramiento sobre declaraciones de gases de efecto invernadero | Se **retira el 15 de diciembre de 2026**, cuando entra en vigor ISSA 5000 |
| **ISSA 5000** | Requisitos generales para encargos de aseguramiento de sostenibilidad. Publicada el **12 de noviembre de 2024** | Periodos que **comiencen el 15 de diciembre de 2026 o después**; la adopción anticipada está permitida y se fomenta |
| **IESSA** (IESBA) | Normas de ética para quien hace aseguramiento de sostenibilidad | Misma fecha, en las jurisdicciones que las adopten |

Todo lo anterior está **[VERIFICADO]** en
`docs/investigacion/06-marcos-reporte-metas-greenwashing.md`.

Lo que conviene saber de **ISSA 5000**:

- Es una norma **completa y autónoma**, sirve para cualquier encargo de
  aseguramiento de sostenibilidad.
- **No depende de la profesión** de quien verifica: la pueden aplicar auditores
  y también proveedores no contables.
- **No depende del marco** usado para reportar: sirve para GRI, ESRS, NIIF S1/S2
  u otro.
- Cubre **los dos niveles** (limitado y razonable) y tanto encargos obligatorios
  como voluntarios.

> **[NO VERIFICADO]**: que ISAE 3000 revisada siga usándose para materias
> distintas de sostenibilidad una vez vigente ISSA 5000. No lo afirmes; si la
> persona necesita esa precisión, que la confirme con su verificador.

**En la Unión Europea:** la Directiva (UE) 2026/470 aplazó al **1 de julio de
2027** la adopción por la Comisión de normas de **aseguramiento limitado**, y
**eliminó** el mandato de adoptar normas de aseguramiento razonable. Hasta
entonces rigen las normas nacionales de cada país. [VERIFICADO]

## 3. La regla de oro de la evidencia: ALCOA+

Es un marco de integridad de datos que viene de la industria farmacéutica y se
usa como buena práctica en sostenibilidad. **No es un requisito de ISSA 5000 ni
de las normas europeas**: preséntalo como recomendación, nunca como obligación.

| Principio | Traducido al expediente ESG |
|---|---|
| **Atribuible** | Cada dato tiene responsable con nombre y fecha |
| **Legible** | Nada de fotos borrosas ni PDF escaneados ilegibles; nombres de archivo ordenados |
| **Contemporáneo** | Las lecturas se cargan en el mes que ocurren, no reconstruidas en diciembre |
| **Original** | Se guarda la boleta del proveedor, no la planilla intermedia |
| **Exacto** | Unidades, conversiones y factores revisados; los errores se corrigen dejando rastro |
| **Completo** | Todos los meses y todas las sedes; lo excluido se justifica |
| **Consistente** | La misma metodología año a año; los cambios se documentan |
| **Duradero** | Almacenamiento estable, no el correo de una sola persona |
| **Disponible** | El verificador llega del número del reporte al documento fuente en pocos pasos |

La bóveda de evidencias del motor cubre la parte mecánica de esto:

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia registrar --archivo datos/consumos-2025.xlsx --descripcion "Consumos de energía 2025, cerrados" --responsable "Ana Pérez"
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia verificar
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" evidencia listar
```

Recuerda el límite: la huella digital prueba que el archivo **no cambió** y en
qué orden se registró; **no** prueba identidad ni fecha ante un tercero. Para
eso hace falta firma electrónica avanzada o sellado de tiempo acreditado.

## 4. Qué contiene un expediente listo para auditoría

Once carpetas. Es una síntesis del proyecto a partir de los requisitos de las
normas de aseguramiento y de los principios de verificabilidad y exactitud de
los marcos de reporte: úsala como guía de trabajo, no la presentes como un
listado oficial de ninguna norma.

| # | Bloque | Qué va adentro |
|---|---|---|
| 1 | **Gobernanza del reporte** | Quién aprueba el informe, acta del directorio o de la gerencia, quién hace qué por indicador |
| 2 | **Alcance y límites** | Qué entidades y sitios entran y cuáles no, y por qué; cómo se consolidan las emisiones (control operacional o financiero) |
| 3 | **Materialidad** | Método, a qué grupos de interés se consultó, evidencia de la consulta, umbral usado, matriz y acta de aprobación |
| 4 | **Ficha por indicador** | Definición, unidad, fórmula, de dónde sale el dato, responsable, frecuencia, controles, factores de emisión con versión y fuente, supuestos |
| 5 | **Trazabilidad** | La cadena completa: documento fuente → planilla → suma → cifra publicada. Cada salto reproducible |
| 6 | **Reexpresiones** | Cifras del año anterior que se corrigieron, por qué, cuánto cambió y quién lo aprobó |
| 7 | **Estimaciones** | Qué se estimó, con qué técnica, con qué supuestos y qué tan incierto es |
| 8 | **Metas** | Año base, alcance cubierto, metodología, validación externa si la hay, cómo se calcula el avance |
| 9 | **Aseguramiento** | Alcance del encargo, norma aplicada, nivel, independencia del verificador, carta de encargo, hallazgos y cómo se cerraron |
| 10 | **Índice y correspondencias** | Dónde está cada dato y cómo se corresponde entre marcos |
| 11 | **Control de versiones** | Registro de cambios del informe y de los archivos de cálculo; la versión publicada se congela |

## 5. Lista de verificación previa

Recórrela con la persona antes de contratar a nadie. Si hay más de tres «no»,
conviene postergar el encargo un ciclo: contratar una verificación sin expediente
es pagar por una lista de hallazgos.

```bash
python "${CLAUDE_SKILL_DIR}/../../motor/esg.py" diagnostico evaluar
```

El diagnóstico entrega el indicador **«listo para auditoría»**: el porcentaje de
datos que están respaldados y no estimados. Úsalo como punto de partida.

1. ¿Cada cifra del reporte tiene detrás un archivo registrado en la bóveda?
2. ¿La verificación de la cadena de evidencias pasa sin problemas?
3. ¿Los datos vienen de boletas, facturas o lecturas, y no de estimaciones? ¿Se
   sabe qué porcentaje es estimado?
4. ¿Están **todos** los meses y **todas** las sedes? ¿Lo excluido está
   justificado por escrito?
5. ¿Los factores de emisión usados tienen fuente y versión anotadas?
6. ¿Hay una persona responsable por cada indicador, con nombre?
7. ¿El ejercicio de materialidad está documentado y aprobado?
8. ¿Las cifras del año anterior que cambiaron están explicadas?
9. ¿Alguien externo al equipo revisó los cálculos antes de publicarlos?
10. ¿Está claro **quién aprueba** el reporte y quedó por escrito?

## 6. Cómo acompañar la conversación

- Pregunta primero **quién está pidiendo la verificación y para qué**: no es lo
  mismo un requisito de la casa matriz que un cliente que pide «datos
  verificados» sin saber qué significa. A veces basta con evidencia ordenada y
  no hace falta contratar a nadie.
- Advierte el orden correcto: **primero el expediente, después el verificador**.
- Los honorarios y los plazos los define el verificador; **no estimes costos**.
- Cuando el verificador entregue hallazgos, trátalos como brechas: se registran
  y se cierran con la skill `diagnostico-esg`.

## Cuidados

- **No prometas que la empresa pasará la verificación.** Preparar bien reduce
  hallazgos; no los elimina.
- **No inventes requisitos ni fechas.** Si algo no está en la investigación del
  proyecto, dilo y ofrece buscarlo con su fuente.
- ALCOA+ y el expediente de once bloques son **buenas prácticas**, no artículos
  de una norma. Dilo cuando los presentes.
- Un dato corregido no es un fraude: lo grave es corregirlo **sin dejar rastro**.
