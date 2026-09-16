# Agentes ESG

Un equipo de agentes de inteligencia artificial, en español, que ayuda a
empresas y personas **sin conocimientos técnicos** a medir su huella de carbono,
cumplir la normativa ambiental, social y de gobernanza que les aplica, y
preparar reportes de sostenibilidad.

Funciona dentro de **Claude Code** (la aplicación de escritorio de Claude o la
terminal). Tú conversas en español; los agentes hacen el trabajo y te dejan los
archivos listos en tu computador.

---

## Qué necesitas

1. Un computador con **Windows, macOS o Linux**.
2. La aplicación **Claude** instalada, con una cuenta de pago (Pro o Max), que es
   la que incluye Claude Code: <https://claude.ai/download>
3. **Python 3** (gratis). Si no lo tienes, el asistente te ofrece instalarlo la
   primera vez; no necesitas saber usarlo.

## Cómo instalarlo (3 pasos, sin terminal)

1. **Descarga la carpeta**: en esta página de GitHub, botón verde **Code** →
   **Download ZIP**.
2. **Descomprime** el archivo donde quieras guardar tu trabajo (por ejemplo, en
   Documentos). Te quedará una carpeta llamada `agentes-esg`.
3. **Ábrela en Claude**: abre la aplicación Claude → pestaña **Code** → elige la
   carpeta `agentes-esg` → escribe **hola**.

Eso es todo. El asistente te saluda, revisa tu computador y te guía.

### Alternativa: instalarlo como plugin

Si usas Claude Code en la terminal y quieres tener los agentes disponibles en
cualquier carpeta:

```bash
claude plugin marketplace add korredor07/agentes-esg
claude plugin install esg@agentes-esg
```

Los comandos quedan como `/esg:inicio`, `/esg:ayuda`, etc.

## Qué puedes pedirle

Escribe con tus palabras. Por ejemplo:

- «Quiero medir la huella de carbono de mi empresa del año pasado.»
- «Me llegó una carta de la autoridad, ¿qué hago?»
- «Mi cliente europeo me pide datos de sostenibilidad.»
- «Necesito un reporte para una licitación.»
- «No sé por dónde empezar.»

Si no sabes qué pedir, escribe **ayuda** y te ofrece un menú por objetivos.

## Dónde quedan tus datos

Todo se guarda en tu computador, dentro de la carpeta `empresas/`:

```
empresas/mi-empresa/
├── empresa.json     perfil de la empresa
├── datos/           tus planillas y documentos
├── resultados/      resultados de los cálculos
├── reportes/        entregables en Word, Excel y HTML
├── evidencias/      respaldos con huella digital SHA-256
└── seguimiento/     brechas, casos y metas en curso
```

Nada se sube a internet ni se comparte con terceros. La carpeta `empresas/` está
excluida del repositorio (`.gitignore`), así que **no se publica** aunque uses
Git.

## Qué no hace

Para que tomes decisiones informadas, esto es lo que **no** puede hacer:

- No es asesoría legal ni una auditoría. Es orientación de apoyo.
- No firma electrónicamente ni emite sellos de tiempo acreditados. El registro de
  evidencias prueba integridad y orden, no identidad legal.
- No declara por ti ante ningún organismo. Prepara la información; el envío lo
  haces tú en el portal correspondiente.
- No inventa datos: si un factor de emisión, un plazo o una multa no están
  verificados, te lo dice en vez de rellenar el hueco.

## Cómo actualizarlo

- **Si lo descargaste como ZIP**: descarga la nueva versión y reemplaza la
  carpeta, conservando tu carpeta `empresas/`.
- **Si lo instalaste como plugin**: se actualiza solo; puedes forzarlo con
  `claude plugin marketplace update agentes-esg`.

## Para quien quiera revisar el código

- El motor de cálculo está en `.claude/motor/` (Python, solo biblioteca
  estándar: no instala dependencias).
- Las instrucciones de cada agente están en `.claude/skills/` y
  `.claude/agents/`, en texto plano legible.
- Pruebas: `python -m unittest discover -s tests -t tests`
- Los datos normativos y factores de emisión llevan fuente, año y licencia en
  `.claude/motor/datos/`.

## Licencia

Código bajo licencia MIT (ver [LICENSE](LICENSE)). Los datos normativos y
factores de emisión conservan la licencia de su fuente original, indicada en
cada archivo. Este proyecto no está afiliado a ningún organismo público ni a
ninguna plataforma comercial de gestión ESG.
