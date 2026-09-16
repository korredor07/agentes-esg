# Qué hace Agentes ESG frente a una plataforma ESG comercial

Las plataformas de gestión ESG del mercado organizan su oferta en dominios:
huella de carbono, cumplimiento regulatorio, reportería, agua, logística,
minería, personas, proveedores, academia y administración. Esta tabla muestra
cómo se resuelve cada dominio aquí, qué está listo y qué **no se puede
replicar** con una herramienta local, con su alternativa honesta.

Estado: ✅ listo · 🚧 en construcción · ⛔ no replicable (con alternativa)

## Núcleo de la plataforma

| Capacidad típica | Aquí | Estado |
|---|---|---|
| Alta de empresa, sitios y entidades legales | Skill `inicio` + `empresa.json` en la carpeta de la empresa | ✅ |
| Asistente de IA que guía y responde | El propio Claude con la skill `asistente` y 13 agentes especialistas | ✅ |
| Tablero con indicadores y estado general | Skill `tablero` → HTML imprimible a PDF | ✅ |
| Escáner de salud ESG con brechas priorizadas | Skill `diagnostico-esg`: puntaje E/S/G, brechas por riesgo y seguimiento | ✅ |
| Carga de datos desde archivos y documentos | Skill `cargar-datos`: Excel, CSV, PDF y fotos leídos por el agente | ✅ |
| Consultas en lenguaje natural sobre los datos | Skill `consultar-datos` + detección de datos raros y meses faltantes | ✅ |
| Trazabilidad y bóveda de evidencias | Skill `evidencias`: cadena de huellas SHA-256 verificable | ✅ |
| Buscador de acciones rápidas, atajos de teclado | No aplica: aquí se pide en lenguaje natural | — |
| Multiusuario con roles y permisos | Carpeta local compartible por OneDrive o Drive | ⛔ |
| Alertas en tiempo real | Alertas al abrir la empresa y tareas programadas opcionales | ⛔ |

## Ambiental

| Capacidad típica | Aquí | Estado |
|---|---|---|
| Huella de carbono alcances 1 y 2 | Skill `huella-carbono` con factores oficiales de Chile y Perú | ✅ |
| Alcance 3 con las 15 categorías | Skill `alcance-3`: por actividad y por gasto, con análisis de dónde está el grueso | ✅ |
| Catálogo de factores de emisión | 108 factores de emisión más densidades, transporte ISO 14083, AWARE y vida útil del SII, todos con fuente, año y licencia | ✅ |
| Metas y trayectoria de reducción | Skill `metas-net-zero`: trayectoria lineal, criterios y Monte Carlo | ✅ |
| Curva de costos de abatimiento (MACC) | Skill `plan-descarbonizacion` | ✅ |
| Huella hídrica (ISO 14046) | Skill `huella-hidrica`: GRI 303, huella de escasez con factores AWARE | ✅ |
| Ley REP: metas por producto y material | Skill `ley-rep` con las metas de cada decreto | ✅ |
| RETC y declaraciones ambientales | Skill `retc` con el calendario de plazos | ✅ |
| Minería: relaves, ventilación, exposición | Skill `mineria`: DS 248, DS 132 y límites del DS 594 | ✅ |
| Logística: emisiones de transporte | Skill `logistica-glec`: ISO 14083 tramo por tramo, con puertos | ✅ |
| Cadena de frío: temperatura y excursiones | Skill `cadena-frio`: temperatura cinética media y límites del RSA | ✅ |
| Base propietaria de decenas de miles de factores | Factores públicos verificados + búsqueda con fuente cuando falta uno | ⛔ |

## Social y gobernanza

| Capacidad típica | Aquí | Estado |
|---|---|---|
| Ley Karin: protocolo, casos y plazos | Skill `ley-karin` con plazos legales y feriados de Chile | ✅ |
| Indicadores de personas | Skill `social-personas`: dotación, rotación, brecha salarial, accidentes, inclusión | ✅ |
| Gobernanza y modelo de prevención de delitos | Skill `gobernanza`: Ley 20.393 y NCG de la CMF | ✅ |
| Protección de datos personales | Skill `proteccion-datos`: Ley 21.719 y documentos base | ✅ |
| Canal de denuncias anónimo con formulario web | Se entrega el procedimiento y los documentos; el canal lo opera la empresa | ⛔ |

## Cumplimiento y reportería

| Capacidad típica | Aquí | Estado |
|---|---|---|
| Qué normativa le aplica a la empresa | Skill `brechas-cumplimiento`: Chile, Perú y exigencias europeas | ✅ |
| Radar de cambios normativos | Agente `agente-investigador` verifica en fuentes oficiales | ✅ |
| Reportes GRI, NIIF S1/S2, norma CMF, VSME | Skill `reportes`: cobertura, índice y borrador en Word | ✅ |
| Doble materialidad | Skill `doble-materialidad` con matriz y priorización | ✅ |
| Preparación para verificación externa | Skill `aseguramiento`: qué pedirá el verificador y qué falta | ✅ |
| Revisión anti-greenwashing | Skill `greenwashing`: revisa la frase antes de publicarla | ✅ |
| Unión Europea: CSRD, CBAM, EUDR, marítimo | Skills `union-europea`, `cbam`, `eudr`, `maritimo-ets` | ✅ |
| Reportes en formato electrónico regulatorio (iXBRL) | No incluido: se entrega el contenido en Word para su carga | ⛔ |
| Envío automático a organismos (SII, RETC, DT) | Se preparan los archivos; el envío lo hace la empresa en el portal | ⛔ |
| Firma electrónica avanzada y sellado de tiempo acreditado | Cadena de hashes SHA-256 verificable localmente | ⛔ |

## Gestión

| Capacidad típica | Aquí | Estado |
|---|---|---|
| Red de proveedores y solicitud de datos | Skill `proveedores`: cuestionario, carta y priorización | ✅ |
| Academia y formación interna | Skill `academia` con registro y certificado interno | ✅ |
| CRM comercial | Skill `crm`: embudo, bitácora y próxima acción | ✅ |
| Activos fijos y depreciación tributaria | Skill `activos-fijos`: tabla del SII, depreciación y corrección monetaria | ✅ |
| Integraciones con ERP, sensores y cloud | Importación desde Excel, CSV y documentos | ⛔ |

## Lo que esta herramienta hace mejor

- **No hay suscripción ni límite de usuarios**: es un repositorio que se
  descarga.
- **Los datos no salen del computador** de la empresa.
- **Todo es auditable**: los factores, las fórmulas y las instrucciones de cada
  agente están en texto plano y se pueden revisar.
- **Explica en vez de mostrar**: el resultado viene con su método, sus supuestos
  y lo que falta, no solo con un número en un tablero.

## Lo que una plataforma comercial hace mejor

- Operación multiusuario con roles, historial y auditoría de accesos.
- Integraciones automáticas con sistemas de la empresa y sensores.
- Soporte contractual, acuerdos de nivel de servicio y responsabilidad legal.
- Bases de datos propietarias de factores de emisión con cobertura más amplia.

Elegir una u otra depende del tamaño y de la exigencia: para muchas pymes, esto
alcanza y sobra; para una empresa grande con obligación regulatoria y auditoría
anual, esto es un complemento, no un reemplazo.
