# Fase 1 — Fundaciones: Plan de implementación

> Ejecutable tarea por tarea. Casillas `- [ ]` para seguimiento.

**Meta:** dejar funcionando el esqueleto instalable (carpeta + plugin), el motor de cálculo con su núcleo probado, y las cuatro skills de entrada (`asistente`, `inicio`, `ayuda`, `preparar-equipo`).

**Arquitectura:** un repositorio que sirve como carpeta de trabajo (se abre en Claude Desktop y carga `CLAUDE.md`, `.claude/agents`, `.claude/skills`) y como plugin (`.claude-plugin/plugin.json` apunta a esas mismas rutas). Todo cálculo ocurre en `.claude/motor` (Python, solo biblioteca estándar) con contrato JSON.

**Tecnologías:** Python 3.9+ (stdlib), Markdown, JSON, unittest.

---

## Decisiones cerradas por el spike de validación

- `plugin.json`: `skills` acepta ruta de directorio como texto (`"./.claude/skills"`). `agents` **NO** acepta directorios: debe ser un arreglo con cada archivo `.md` (`["./.claude/agents/agente-carbono.md", ...]`). Validado con `claude plugin validate`.
- `${CLAUDE_SKILL_DIR}` se sustituye tanto en skills de proyecto como de plugin (docs oficiales), y también dentro de `allowed-tools`. Es la ruta que usan las skills para llamar al motor: `${CLAUDE_SKILL_DIR}/../../motor/esg.py`.
- No se pueden correr pruebas de extremo a extremo con `claude -p` en esta máquina (la sesión OAuth del CLI está vencida). Sustituto: un subagente hace de "usuario no técnico" siguiendo las instrucciones del repositorio.

## Estructura de archivos de la fase

| Archivo | Responsabilidad |
|---|---|
| `.claude/motor/esg.py` | Única entrada del motor: enruta `<módulo> <acción>` y emite JSON |
| `.claude/motor/nucleo/salida.py` | Contrato JSON de salida, errores en español, códigos de salida |
| `.claude/motor/nucleo/excel.py` | Leer y escribir `.xlsx` sin dependencias |
| `.claude/motor/nucleo/informe.py` | Informe HTML autocontenido con gráficos SVG |
| `.claude/motor/nucleo/word.py` | Escribir `.docx` desde bloques simples |
| `.claude/motor/nucleo/espacio.py` | Carpeta de empresa, `empresa.json`, rutas y validación |
| `.claude/motor/nucleo/evidencias.py` | Cadena de hashes SHA-256 y verificación |
| `.claude/motor/nucleo/unidades.py` | Conversión de unidades (energía, volumen, masa, distancia) |
| `.claude/motor/nucleo/fechas.py` | Días hábiles y plazos (feriados se cargan desde CSV) |
| `.claude/motor/plantillas/definiciones.py` | Definición de cada plantilla Excel (columnas, ejemplos, ayuda) |
| `.claude-plugin/plugin.json`, `marketplace.json` | Instalación como plugin |
| `CLAUDE.md`, `.claude/settings.json` | Activación del Asistente ESG y permisos del motor |
| `.claude/skills/{asistente,inicio,ayuda,preparar-equipo}/SKILL.md` | Entrada conversacional |
| `tests/test_*.py` | Pruebas unitarias (unittest, stdlib) |

## Contrato del motor

```
python esg.py <módulo> <acción> [--empresa RUTA] [--entrada ARCHIVO] [--salida ARCHIVO] [opciones]
```
- Éxito: imprime `{"ok": true, "resultado": {...}, "advertencias": [...], "fuentes": [...]}` y sale con 0.
- Error: imprime `{"ok": false, "error": "...", "sugerencia": "...", "detalle": {...}}` y sale con 1.
- Todos los mensajes en español, sin tecnicismos: los lee una persona a través del agente.

## Tareas

- [ ] **T1 — Esqueleto del repositorio**: `.gitignore` (excluye `empresas/*` salvo `empresas/ejemplo-*`), `LICENSE` (MIT), `.claude-plugin/plugin.json` y `marketplace.json` válidos, `.claude/settings.json` con permisos del motor. Verificación: `claude plugin validate .` pasa.
- [ ] **T2 — Contrato de salida y CLI**: `nucleo/salida.py` (`exito`, `error`, `Problema`) y `esg.py` con enrutador, `--ayuda` y módulo `version`. Pruebas: salida JSON válida, error con código 1, módulo inexistente sugiere módulos disponibles.
- [ ] **T3 — Excel**: `nucleo/excel.py` con `leer_xlsx(ruta) -> {hoja: [filas]}`, `escribir_xlsx(ruta, hojas)` (encabezados en negrita, anchos, formato de números y fechas), `leer_tabla(ruta, hoja)` -> lista de diccionarios normalizando encabezados. Pruebas: ida y vuelta, cadenas compartidas, números, fechas, celdas vacías, hoja inexistente, archivo corrupto.
- [ ] **T4 — Informe HTML**: `nucleo/informe.py` con `render(titulo, bloques, marca)`: bloques `kpi`, `tabla`, `texto`, `lista`, `barras`, `lineas`, `dona`, `semaforo`, `nota`. Autocontenido, imprimible a PDF, colores de marca configurables. Pruebas: HTML sin recursos externos, escape de caracteres, SVG con datos correctos.
- [ ] **T5 — Word**: `nucleo/word.py` con `escribir_docx(ruta, bloques)` (título, subtítulos, párrafos, viñetas, tablas, salto de página). Pruebas: el archivo es un zip válido con `word/document.xml` y contiene los textos.
- [ ] **T6 — Unidades**: `nucleo/unidades.py` con `convertir(valor, desde, hacia)` para energía (kWh, MWh, GJ, TJ, kcal), volumen (L, m3, gal), masa (kg, t, lb), distancia (km, mi, m) y `normalizar_unidad(texto)` que acepta variantes en español. Pruebas: conversiones conocidas, unidad desconocida da error claro.
- [ ] **T7 — Espacio de trabajo**: `nucleo/espacio.py` con `crear_empresa(datos)`, `cargar_empresa(ruta)`, `listar_empresas(raiz)`, `ruta_de(empresa, tipo)`; esquema de `empresa.json` (nombre, país, sector, tamaño, año base, marcos, sitios, entidades, marca) con validación y mensajes en español. Pruebas: creación de estructura, validación de campos obligatorios, empresa inexistente.
- [ ] **T8 — Evidencias**: `nucleo/evidencias.py` con `registrar(empresa, archivo, descripcion)` (SHA-256 + hash del registro anterior en `evidencias/registro.jsonl`) y `verificar(empresa)` (detecta archivo alterado, ausente o cadena rota). Pruebas: cadena válida, alteración detectada, archivo faltante.
- [ ] **T9 — Plantillas Excel**: `plantillas/definiciones.py` + acción `plantilla crear --tipo <t> --empresa <ruta>`; incluye en esta fase `sitios` y `personas`; cada plantilla trae hoja de instrucciones y ejemplos. Pruebas: genera archivo legible por `leer_tabla`, tipo desconocido lista los disponibles.
- [ ] **T10 — Fechas**: `nucleo/fechas.py` con `dias_habiles(desde, cantidad, feriados)`, `plazo(desde, cantidad, tipo)` (hábiles o corridos), `cargar_feriados(csv)`. Pruebas: fin de semana, feriado, plazo en días corridos. (El CSV de feriados de Chile llega con la investigación, Fase 3.)
- [ ] **T11 — Activación conversacional**: `CLAUDE.md` + skills `asistente` (orquestador), `inicio` (alta de empresa en ~8 preguntas), `ayuda` (menú por objetivos), `preparar-equipo` (detecta Python e instala si falta). Verificación: `claude plugin validate .` sigue pasando y un subagente que hace de usuario no técnico completa el alta de una empresa siguiendo solo estas instrucciones.
- [ ] **T12 — Cierre de fase**: `python -m unittest discover -s tests -v` en verde, README mínimo con los tres caminos de instalación, commit y etiqueta interna de fase.

## Verificación de la fase

1. `python -m unittest discover -s tests -v` sin fallos.
2. `claude plugin validate .` sin errores.
3. Un subagente en modo "usuario no técnico" crea la empresa de ejemplo y genera una plantilla, usando solo el repositorio.
