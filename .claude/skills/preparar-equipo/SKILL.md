---
name: preparar-equipo
description: Dejar el computador listo para usar los Agentes ESG. Úsala cuando el motor de cálculo no responde, aparece "python no se reconoce", "command not found", se abre la tienda de aplicaciones al ejecutar python, o la persona instala esto por primera vez.
allowed-tools: Bash(python *), Bash(py *), Bash(python3 *), Bash(winget *), PowerShell(python *), PowerShell(py *), PowerShell(python3 *), PowerShell(winget *)
---

# Preparar el computador

El motor de cálculo necesita **Python 3.9 o superior**. No hace falta instalar
nada más: ninguna librería, ninguna cuenta, ningún servicio.

## 1. Buscar Python

Prueba en este orden y quédate con el primero que responda «Python 3.x»:

```bash
python --version
py --version
python3 --version
```

Advertencia en Windows: si `python --version` no imprime nada, imprime un
mensaje sobre la Microsoft Store o abre la tienda, **no cuenta como instalado**.

Si encontraste uno, confirma que el motor funciona y termina:

```bash
python .claude/motor/esg.py version mostrar
```

## 2. Si no está instalado

Explica primero, en una línea, qué vas a hacer y pide permiso:
«Necesito instalar Python, que es el programa que hace los cálculos. Es gratis,
oficial y no toca tus archivos. ¿Lo instalo?»

**Windows** (con permiso de la persona):

```bash
winget install --exact --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
```

Después de instalar hay que **cerrar y volver a abrir Claude** para que el
computador reconozca el comando nuevo. Dilo antes de que la persona se asuste.

**macOS:** pide que abra la aplicación Terminal y ejecute `xcode-select --install`
(instala herramientas de Apple, incluye Python 3), o que descargue el instalador
oficial desde python.org. Explícale que son unos minutos y que al terminar
vuelva contigo.

**Linux:** `sudo apt install python3` (Debian/Ubuntu) o el equivalente de su
distribución, desde su terminal.

Si la persona prefiere no instalar nada: dile con honestidad que sin Python
puedes conversar y orientar, pero **no** puedes calcular huellas, plazos ni
generar reportes confiables, porque no vas a inventar números.

## 3. Verificar

```bash
python .claude/motor/esg.py revision sistema
```

Revisa la versión de Python, que estén los archivos de factores y feriados, que
el cálculo de prueba dé el resultado correcto y que se puedan guardar archivos
en la carpeta. Si todo sale «ok», avísale que ya está listo y retoma lo que
estaban haciendo. Si algo falla, el propio resultado dice qué hacer.

## 4. Si algo falla

- «No se reconoce el comando»: Python no quedó en el PATH. Reinstala marcando
  la casilla «Add Python to PATH», o usa `py` en Windows.
- Se abre la Microsoft Store: la persona tiene el acceso directo, no Python.
  Instálalo con `winget` como arriba.
- Permisos denegados: pide que ejecute la instalación como administrador o que
  use el instalador oficial de python.org.
- Antivirus corporativo bloquea: no insistas; dile que hable con su área de
  informática y muéstrale qué se instalaría y para qué.
