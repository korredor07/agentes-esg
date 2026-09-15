# Agentes ESG — Diseño (spec)

Fecha: 2026-09-15 · Estado: borrador para aprobación

## 1. Propósito

Llevar a Claude Code las capacidades de una plataforma SaaS ESG completa —huella de carbono, reportería, cumplimiento regulatorio de Chile, Perú y la Unión Europea, y módulos sectoriales— como un equipo de agentes de IA que cualquier persona sin conocimientos técnicos pueda descargar gratis y usar conversando en español.

### Criterios de éxito

1. Una persona no técnica con Claude Desktop puede: descargar la carpeta → abrirla en la pestaña Code → escribir «hola» → registrar su empresa → subir un Excel o PDF de facturas → recibir su huella de carbono y un reporte, sin usar la terminal ni editar código.
2. Cada dominio de la plataforma de referencia tiene su equivalente (§5).
3. Todo número sale de un motor de cálculo determinista con pruebas automáticas; el modelo nunca «calcula de memoria».
4. Cada factor de emisión, umbral y plazo legal lleva fuente, año y fecha de verificación.
5. También se instala como plugin de Claude Code desde GitHub.
6. Pasan: `claude plugin validate`, las pruebas unitarias del motor y una prueba de extremo a extremo con la empresa de ejemplo.

### Fuera de alcance (y qué se ofrece a cambio)

| De la plataforma | Por qué no | Alternativa |
|---|---|---|
| Firma Electrónica Avanzada y sellos de tiempo acreditados (RFC 3161) | Requieren entidad certificadora | Registro de evidencias con cadena de hashes SHA-256 verificable localmente |
| Conexión directa a SII, Ventanilla Única/RETC, SISREP, portal de la DT, ERPs, sensores IoT | Requieren credenciales o convenios | El agente prepara archivos listos para carga manual; importa Excel, CSV y PDF |
| Multiusuario con roles y alertas en tiempo real | Es un producto web | Carpeta local compartible (OneDrive/Drive); revisiones a pedido o programadas |
| Base propietaria de ~50.000 factores de emisión | Licencia privada | Factores públicos con licencia de redistribución + búsqueda web con fuente |
| Marketplace de instructores con pagos | Requiere pasarela de pago | Academia local con cursos, cuestionarios y certificados |
| Código, marca, textos o API de terceros | Propiedad intelectual ajena | Todo se construye desde normas y estándares públicos |

## 2. Enfoques evaluados

**A. Híbrido: carpeta de trabajo + plugin (elegido).** El mismo repositorio funciona (1) descargado y abierto como carpeta en Claude Desktop —se carga solo: instrucciones del asistente, agentes y skills— y (2) instalado como plugin por usuarios técnicos. Una sola fuente de verdad: `plugin.json` apunta a `.claude/skills` y `.claude/agents`.

- A favor: cero instalación para no técnicos; actualizaciones automáticas para quien use el plugin.
- Riesgo: hay que validar temprano que el plugin acepte rutas dentro de `.claude/` (plan B: script de sincronización hacia `skills/` y `agents/` en la raíz).

**B. Solo plugin.** Limpio y con actualizaciones, pero agregar un marketplace no está en la interfaz de Claude Desktop (el usuario tendría que escribir comandos) y un plugin no puede traer `CLAUDE.md` (la personalidad del asistente).

**C. Solo carpeta.** Lo más simple, pero sin actualizaciones y solo funciona dentro de esa carpeta.

## 3. Arquitectura

```
Persona usuaria (español, lenguaje natural)
        │
        ▼
Asistente ESG — hilo principal
  · modo carpeta: CLAUDE.md importa la skill `asistente`
  · modo plugin:  skill /esg:asistente
  · entiende la necesidad, pide lo que falta y deriva
        │
   ┌────┴────────────────────────────┐
   ▼                                 ▼
Skills (flujos guiados,         Agentes de dominio (trabajo largo
interactivos)                   en contexto aislado; devuelven resumen)
   │                                 │
   └───────────────┬─────────────────┘
                   ▼
      Motor de cálculo (Python, solo biblioteca estándar)
                   │
                   ▼
      empresas/<empresa>/  datos · resultados · reportes · evidencias · seguimiento
```

Reglas de diseño:

- **Skills** = cómo se hace algo: procedimiento, referencias normativas y llamadas al motor. Se usan en la conversación y pueden hacer preguntas.
- **Agentes** = quién lo hace cuando el trabajo es largo (procesar 12 meses de facturas, redactar un reporte GRI completo). No conversan con la persona usuaria: el asistente reúne antes los datos que falten y el agente devuelve un resumen y archivos.
- **Motor** = única fuente de números. Entrada y salida JSON; errores en español con sugerencia.
- **Datos de la empresa** = siempre en la carpeta local de la persona usuaria.

## 4. Estructura del repositorio

```
agentes-esg/
├── README.md                  Guía paso a paso para no técnicos
├── CLAUDE.md                  Activa al Asistente ESG (importa la skill asistente)
├── LICENSE                    MIT (código); licencias de datos en .claude/motor/datos/LICENCIAS.md
├── .gitignore                 Excluye empresas/* salvo la empresa de ejemplo
├── .claude-plugin/
│   ├── marketplace.json       Catálogo "agentes-esg" con el plugin "esg" (source "./")
│   └── plugin.json            name "esg"; skills → ./.claude/skills; agents → ./.claude/agents
├── .claude/
│   ├── settings.json          Pre-aprueba solo la ejecución del motor
│   ├── agents/                15 agentes (§5)
│   ├── skills/                38 skills: SKILL.md + referencias/*.md
│   └── motor/
│       ├── esg.py             Punto de entrada único: python esg.py <módulo> <acción>
│       ├── nucleo/            excel, word, html, espacio de trabajo, evidencias, fechas
│       ├── calculos/          carbono, metas, macc, agua, glec, frio, rep, karin, mineria,
│       │                      maritimo, cbam, activos, puntaje
│       └── datos/             CSV normativos con columnas de fuente, año, licencia y verificación
├── empresas/
│   └── ejemplo-alimentos-del-sur/   Empresa ficticia con datos de muestra
├── docs/                      Mapeo de módulos, guía de uso, specs y planes
└── tests/                     unittest + prueba de extremo a extremo
```

## 5. Mapeo de dominios → agentes → skills

| Dominio de la plataforma de referencia | Agente | Skills |
|---|---|---|
| Plataforma: bienvenida, perfil de empresa, sitios y entidades legales, ayuda, buscador | Asistente ESG (hilo principal) | `asistente`, `inicio`, `ayuda`, `preparar-equipo` |
| Plataforma: salud ESG, puntaje E/S/G, escáner de brechas priorizadas, diagnóstico inicial, tablero | `agente-auditor` | `diagnostico-esg`, `tablero` |
| Plataforma: carga de datos, factura → KPI, consultas en lenguaje natural, anomalías y patrones | `agente-datos` | `cargar-datos`, `consultar-datos` |
| Plataforma: bóveda de evidencias, trazabilidad, aseguramiento ISAE 3000 / ISSA 5000 | `agente-auditor` | `evidencias`, `aseguramiento` |
| ESG ambiental: Alcance 1-2-3, factores de emisión, cierre mensual, certificados de energía renovable, metas net zero (trayectoria SBTi y Monte Carlo), curva MACC | `agente-carbono` | `huella-carbono`, `alcance-3`, `metas-net-zero`, `plan-descarbonizacion` |
| ESG reportería: GRI, SASB, TCFD, NIIF S1/S2, NCG 519 de la CMF, multi-marco, doble materialidad, marca corporativa | `agente-reportes` | `reportes`, `doble-materialidad` |
| ESG social y gobernanza: personas, gobernanza corporativa, Ley 21.595, protección de datos (Ley 21.719: RAT y EIPD) | `agente-cumplimiento` | `social-personas`, `gobernanza`, `proteccion-datos` |
| Cumplimiento: aplicabilidad y brechas, radar regulatorio, anti-greenwashing | `agente-cumplimiento` + `agente-investigador` | `brechas-cumplimiento`, `radar-normativo`, `greenwashing` |
| Ley REP y RETC | `agente-cumplimiento` | `ley-rep`, `retc` |
| Ley Karin | `agente-ley-karin` | `ley-karin` |
| Agua | `agente-agua` | `huella-hidrica` |
| Logística: GLEC / ISO 14083, cadena de frío (MKT), lotes y retiros de mercado | `agente-logistica` | `logistica-glec`, `cadena-frio` |
| Minería: GISTM, relaves, exposición ocupacional, ventilación, cierre de faenas | `agente-mineria` | `mineria` |
| Unión Europea: CSRD/ESRS, VSME, CSDDD, Taxonomía, EINF, sanciones, CBAM, ETS marítimo y FuelEU, EUDR | `agente-union-europea` | `union-europea`, `cbam`, `maritimo-ets`, `eudr` |
| Finanzas y tesorería: activos fijos, depreciación SII, corrección monetaria, facturas, conciliación bancaria | `agente-finanzas` | `activos-fijos`, `facturas-conciliacion` |
| Red de proveedores | `agente-proveedores` | `proveedores` |
| CRM | `agente-crm` | `crm` |
| Academia | `agente-academia` | `academia` |
| Perú (transversal) | todos | Referencias por país dentro de cada skill + `brechas-cumplimiento` |

Totales: 15 agentes y 38 skills.

## 6. Motor de cálculo

- Python 3.9 o superior, solo biblioteca estándar (sin `pip install`).
- Contrato: `python esg.py <módulo> <acción> [--entrada archivo] [--empresa carpeta] [--salida archivo]` → imprime JSON `{"ok": true, "resultado": …, "advertencias": […], "fuentes": […]}`. En error: `{"ok": false, "error": "…", "sugerencia": "…"}` y código de salida 1.
- Núcleo propio: lector y escritor de Excel (.xlsx), escritor de Word (.docx), generador HTML autocontenido con gráficos SVG (imprimible a PDF desde el navegador), fechas y días hábiles de Chile.

| Módulo | Qué calcula |
|---|---|
| carbono | Alcance 1 (combustión fija y móvil, refrigerantes), Alcance 2 (ubicación y mercado), Alcance 3 por actividad y por gasto, calidad de dato, intensidades |
| metas | Trayectoria lineal SBTi, probabilidad de cumplimiento por Monte Carlo, escenarios what-if |
| macc | Costo por tCO₂e evitada y curva MACC |
| agua | Extracción, descarga y consumo; huella de escasez AWARE |
| glec | Emisiones de transporte pozo-a-rueda por tramo y modo |
| frio | Temperatura cinética media (MKT), excursiones, vida útil dinámica |
| rep | Toneladas puestas en el mercado frente a metas por material y año |
| karin | Plazos legales en días hábiles o corridos y alertas de vencimiento |
| mineria | Revancha y factor de seguridad de relaves, ventilación, exposición química |
| maritimo | Obligación EU ETS, recargo por contenedor, balance FuelEU y penalidad |
| cbam | Emisiones incorporadas y costo estimado de certificados |
| activos | Depreciación normal y acelerada (vida útil SII), corrección monetaria, bajas y ventas |
| puntaje | Puntaje E/S/G, brechas priorizadas por riesgo, % listo para auditoría |
| evidencias | Registro y verificación de cadena de hashes SHA-256 |

Cada módulo tiene pruebas con valores de referencia publicados por la fuente cuando existen.

## 7. Datos normativos y factores

- Archivos CSV con columnas `fuente`, `url`, `anio`, `licencia` y `verificado_el`.
- Solo fuentes redistribuibles o hechos normativos públicos: IPCC 2006 (factores por defecto), DESNZ/DEFRA (Open Government Licence v3), Ministerio de Energía de Chile (factor del SEN), MINAM Perú, EPA (factores de cadena de suministro, dominio público), IPCC AR5/AR6 (potenciales de calentamiento), tabla de vida útil del SII, decretos de metas REP, feriados legales de Chile.
- Cada valor lo verifica un subagente investigador en la fuente oficial vigente. Si no se puede verificar, no entra y la skill explica cómo obtenerlo.
- `radar-normativo` permite revalidar valores y plazos en la web cuando la persona usuaria lo pida.

## 8. Experiencia para personas no técnicas

- Primer uso: «hola» → saludo breve → verifica Python (si falta, lo instala con permiso) → registra la empresa con unas 8 preguntas simples → crea plantillas Excel → indica qué normas le aplican y los 3 primeros pasos.
- Lenguaje: español claro, frases cortas, términos explicados la primera vez. Nunca se pide editar JSON ni usar la terminal.
- Cada entrega: resumen de 3 a 5 líneas + archivo abrible (Word, Excel o HTML) en `empresas/<empresa>/reportes/`.
- `ayuda` muestra un menú por objetivos («quiero saber mi huella», «me llegó una denuncia Ley Karin», «exporto a Europa»).
- Avisos permanentes: es orientación, no asesoría legal; los datos no salen del computador; los datos sensibles (Ley Karin, personas) nunca se suben a GitHub (`.gitignore`).

## 9. Errores y casos límite

- Columnas o unidades faltantes → el motor dice exactamente qué falta y en qué fila.
- Sin factor de emisión aplicable → no se inventa: se informa y se ofrece una búsqueda con fuente.
- Datos incompletos → se calcula con lo disponible, se marca la calidad (estimado, reportado, verificado) y se registra como brecha.
- Sin Python → skill `preparar-equipo`; como último recurso, cálculo mostrado paso a paso y marcado «no verificado por el motor».
- Plazos de Ley Karin vencidos o por vencer → alerta destacada al abrir la empresa.

## 10. Verificación

1. Pruebas unitarias del motor (`python -m unittest`), incluidas pruebas contra ejemplos publicados por las fuentes.
2. `claude plugin validate .`
3. Prueba de extremo a extremo sin intervención (`claude -p`) con la empresa de ejemplo: huella, diagnóstico y reporte generados.
4. Revisión cruzada de skills y agentes (rutas, consistencia, español simple) por subagentes revisores.
5. Prueba de instalación en ambos modos: carpeta y plugin desde un marketplace local.

## 11. Publicación

- Repositorio nuevo y público `github.com/korredor07/agentes-esg`, independiente de otros proyectos. Carpeta local `D:\Programas Data\Claude Code\agentes-esg\`, excluida del repositorio padre mediante `.git/info/exclude` (sin modificar sus archivos versionados).
- Versión v1.0.0 con ZIP descargable desde Releases.
- El repositorio público no incluye los documentos de análisis de la plataforma de referencia ni nombres de marca de terceros.
- Se pide confirmación explícita antes de subir.

## 12. Fases

1. **Fundaciones:** estructura, plugin y marketplace, núcleo del motor, `asistente`, `inicio`, `ayuda`, `preparar-equipo`; validación temprana del modo híbrido.
2. **Núcleo ESG:** carbono 1-2-3 con factores verificados, carga y consulta de datos, diagnóstico, tablero, reportes, metas y MACC, evidencias.
3. **Chile:** Ley Karin, Ley REP, RETC, gobernanza, social, protección de datos, brechas y radar.
4. **Sectoriales y UE:** agua, logística y frío, minería, UE/CBAM/marítimo/EUDR, finanzas, proveedores, CRM, academia, greenwashing, aseguramiento, doble materialidad.
5. **Cierre:** empresa de ejemplo completa, prueba de extremo a extremo, README, versión y publicación.
