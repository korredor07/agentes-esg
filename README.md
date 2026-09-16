# Agentes ESG

Un equipo de agentes de inteligencia artificial, en español, que ayuda a
empresas y personas **sin conocimientos técnicos** a medir su huella de
carbono, cumplir la normativa ambiental, social y de gobernanza que les aplica,
y preparar reportes de sostenibilidad.

Funciona dentro de **Claude Code** (la aplicación de escritorio de Claude o la
terminal). Tú conversas en español; los agentes hacen el trabajo y te dejan los
archivos listos en tu computador.

> Es software libre, hecho sobre normas y estándares públicos. No está afiliado
> a ningún organismo ni a ninguna plataforma comercial.

---

## Cómo instalarlo (3 pasos, sin terminal)

1. **Descarga la carpeta**: botón verde **Code** → **Download ZIP**.
2. **Descomprime** el archivo donde quieras guardar tu trabajo (por ejemplo, en
   Documentos). Te quedará una carpeta llamada `agentes-esg`.
3. **Ábrela en Claude**: abre la aplicación Claude → pestaña **Code** → elige la
   carpeta `agentes-esg` → escribe **hola**.

El asistente te saluda, revisa tu computador y te guía desde ahí.

Necesitas: un computador con Windows, macOS o Linux; la aplicación **Claude**
con cuenta de pago (<https://claude.ai/download>); y **Python 3**, que el
asistente te ofrece instalar la primera vez si no lo tienes.

### Alternativa: instalarlo como plugin

Si usas Claude Code en la terminal y quieres los agentes en cualquier carpeta:

```bash
claude plugin marketplace add korredor07/agentes-esg
claude plugin install esg@agentes-esg
```

Los comandos quedan como `/esg:inicio`, `/esg:huella-carbono`, etc.

---

## Qué sabe hacer

Escribe con tus palabras: «quiero medir mi huella», «¿qué leyes me aplican?»,
«me llegó una denuncia», «necesito un reporte para una licitación». Si no sabes
qué pedir, escribe **ayuda**.

### Medir y reducir

- **Huella de carbono** (alcances 1, 2 y 3) con factores oficiales de Chile,
  Perú y referencias internacionales, cada uno con su fuente y su año.
- **Cadena de valor**: compras, fletes, viajes, residuos y agua, por actividad
  o por gasto, con análisis de dónde está el grueso del impacto.
- **Metas de reducción**: trayectoria año a año, revisión de criterios y
  probabilidad real de cumplirlas (simulación de Monte Carlo).
- **Plan de descarbonización**: qué medidas conviene hacer primero y cuánto
  cuesta cada tonelada evitada (curva MACC).

### Cumplir

- **Qué normativa te aplica** en Chile, Perú y para exportar a la Unión Europea,
  con plazos y riesgos.
- **Calendario de obligaciones** del año, con avisos de lo que está abierto o
  por vencer.
- **Ley Karin** (Chile): plazos legales exactos de una denuncia, protocolo de
  prevención y documentos.
- **Ley REP**: metas por producto prioritario, material y año, con la fórmula
  de cada decreto.
- **Declaraciones ambientales** (RETC, residuos, emisiones, residuos peligrosos).
- **Gobernanza y protección de datos personales**.

### Reportar y respaldar

- **Reportes de sostenibilidad**: GRI, NIIF S1/S2, norma de la CMF y el estándar
  voluntario europeo para pymes, con índice de contenidos y borrador en Word.
- **Doble materialidad**, preparación para **verificación externa** y revisión
  **anti-greenwashing** antes de publicar.
- **Indicadores sociales**: dotación, rotación, brecha salarial, accidentes,
  capacitación e inclusión.
- **Bóveda de evidencias** con huella digital SHA-256 verificable.
- **Tablero** y **diagnóstico ESG** con brechas priorizadas por riesgo.

### Exportar a Europa

- **CSRD y el estándar voluntario para pymes**: qué te puede pedir un cliente
  europeo y hasta dónde llega su derecho a pedirlo.
- **CBAM**, el arancel de carbono en frontera para acero, aluminio, cemento y
  fertilizantes.
- **EUDR**, productos libres de deforestación (soya, cacao, café, madera, carne).
- **Mercado de carbono marítimo** y FuelEU: cuánto le suma al flete a Europa.

### Sectoriales

- **Minería**: depósitos de relaves, ventilación de minas subterráneas,
  exposición ocupacional, ruido y cierre de faenas.
- **Agua**: consumo, indicadores GRI 303 y huella de escasez hídrica.
- **Transporte de carga**: emisiones de un envío tramo por tramo según ISO
  14083, y comparación entre camión, tren, barco y avión.
- **Cadena de frío**: temperatura cinética media, excursiones fuera de rango y
  las temperaturas que exige el Reglamento Sanitario de los Alimentos.
- **Activos fijos**: vida útil según la tabla del SII, depreciación y
  corrección monetaria, para planificar el recambio de equipos.
- Y además **proveedores**, **academia interna** y **seguimiento comercial**.

Para ver el detalle y la comparación con una plataforma comercial:
[docs/equivalencias.md](docs/equivalencias.md).

---

## Dónde quedan tus datos

Todo se guarda en tu computador, dentro de `empresas/`:

```
empresas/mi-empresa/
├── empresa.json     perfil de la empresa
├── datos/           tus planillas y documentos
├── resultados/      resultados de los cálculos
├── reportes/        entregables en Word, Excel y HTML
├── evidencias/      respaldos con huella digital
└── seguimiento/     brechas, casos y metas en curso
```

Nada se sube a internet. La carpeta `empresas/` está excluida del repositorio,
así que **no se publica** aunque uses Git.

Hay una empresa ficticia de ejemplo (`empresas/ejemplo-alimentos-del-sur`) con
datos inventados, para que veas cómo se ve todo antes de cargar lo tuyo.

---

## Qué no hace

- No es asesoría legal ni una auditoría: es orientación de apoyo.
- No firma electrónicamente ni emite sellos de tiempo acreditados. El registro
  de evidencias prueba integridad y orden, no identidad legal.
- No declara por ti ante ningún organismo: prepara la información, el envío lo
  haces tú en el portal correspondiente.
- No inventa datos. Si un factor, un plazo o una multa no están verificados, te
  lo dice en vez de rellenar el hueco.

---

## Guías

- [Guía de uso paso a paso](docs/guia-de-uso.md) — para empezar.
- [Equivalencias con plataformas comerciales](docs/equivalencias.md) — qué
  cubre y qué no.
- [Investigación normativa](docs/investigacion/) — de dónde sale cada dato, con
  sus fuentes y su fecha de verificación.

## Para quien quiera revisar el código

- Motor de cálculo en `.claude/motor/` (Python, **solo biblioteca estándar**:
  no instala dependencias).
- Instrucciones de cada agente en `.claude/skills/` y `.claude/agents/`, en
  texto plano legible.
- Pruebas: `python -m unittest discover -s tests -t tests`
- Validación del plugin: `claude plugin validate .`
- Los factores de emisión y datos normativos están en
  `.claude/motor/datos/`, cada fila con su fuente, año, licencia y fecha de
  verificación.

## Cómo actualizarlo

- **Si lo descargaste como ZIP**: descarga la nueva versión y reemplaza la
  carpeta, conservando tu carpeta `empresas/`.
- **Si lo instalaste como plugin**: se actualiza solo; puedes forzarlo con
  `claude plugin marketplace update agentes-esg`.

## Licencia

Código bajo licencia MIT (ver [LICENSE](LICENSE)). Los datos normativos y
factores de emisión conservan la licencia de su fuente original, indicada en
cada archivo.
