# -*- coding: utf-8 -*-
"""El paquete tiene que ser coherente consigo mismo.

Una skill que manda a otra que no existe, o un comando documentado que el motor
no tiene, dejan a la persona en un callejon sin salida. Estas pruebas revisan
todas esas referencias de una vez (hallazgo H12 de docs/prueba-de-uso.md).
"""

import io
import json
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(RAIZ, ".claude", "skills")
AGENTES = os.path.join(RAIZ, ".claude", "agents")
MOTOR = os.path.join(RAIZ, ".claude", "motor")
PLUGIN = os.path.join(RAIZ, ".claude-plugin", "plugin.json")

# Nombres entre comillas invertidas que no son referencias a skills ni a agentes.
NO_SON_REFERENCIAS = {
    "reporte", "huella", "empresa", "datos", "evidencia", "plantilla", "meta",
    "diagnostico", "tablero", "karin", "cumplimiento", "calendario", "social",
    "revision", "rep", "materialidad", "gobernanza", "datos_personales",
    "proveedores_motor", "academia", "crm", "version", "agua", "europa",
    "mineria", "activos",
}


def _leer(ruta):
    with io.open(ruta, encoding="utf-8") as archivo:
        return archivo.read()


def _frontmatter(texto):
    if not texto.startswith("---"):
        return {}
    fin = texto.find("\n---", 3)
    campos = {}
    for linea in texto[3:fin].splitlines():
        if ":" in linea and not linea.startswith(" "):
            clave, valor = linea.split(":", 1)
            campos[clave.strip()] = valor.strip()
    return campos


def _skills():
    return sorted(n for n in os.listdir(SKILLS)
                  if os.path.isfile(os.path.join(SKILLS, n, "SKILL.md")))


def _agentes():
    return sorted(n[:-3] for n in os.listdir(AGENTES) if n.endswith(".md"))


def _documentos():
    """Cada archivo .md del paquete con su ruta relativa."""
    documentos = []
    for nombre in _skills():
        ruta = os.path.join(SKILLS, nombre, "SKILL.md")
        documentos.append((".claude/skills/%s/SKILL.md" % nombre, _leer(ruta)))
    for nombre in _agentes():
        ruta = os.path.join(AGENTES, nombre + ".md")
        documentos.append((".claude/agents/%s.md" % nombre, _leer(ruta)))
    documentos.append(("CLAUDE.md", _leer(os.path.join(RAIZ, "CLAUDE.md"))))
    return documentos


def _acciones_del_motor():
    """Acciones que realmente existen, leidas del motor."""
    import sys
    if MOTOR not in sys.path:
        sys.path.insert(0, MOTOR)
    import importlib
    catalogo = {}
    for archivo in sorted(os.listdir(os.path.join(MOTOR, "modulos"))):
        if archivo.endswith(".py") and not archivo.startswith("_"):
            nombre = archivo[:-3]
            modulo = importlib.import_module("modulos.%s" % nombre)
            catalogo[nombre] = set(getattr(modulo, "ACCIONES", {}))
    return catalogo


class PruebaSkills(unittest.TestCase):

    def test_cada_skill_tiene_nombre_y_descripcion(self):
        for nombre in _skills():
            campos = _frontmatter(_leer(os.path.join(SKILLS, nombre, "SKILL.md")))
            self.assertEqual(campos.get("name"), nombre,
                             "La skill %s declara name «%s»." % (nombre, campos.get("name")))
            self.assertTrue(campos.get("description"), "La skill %s no tiene description." % nombre)
            self.assertGreater(len(campos["description"]), 60,
                               "La descripcion de %s es muy corta para decidir cuando usarla." % nombre)

    def test_las_skills_declaran_las_herramientas_que_usan(self):
        for nombre in _skills():
            texto = _leer(os.path.join(SKILLS, nombre, "SKILL.md"))
            if "python .claude/motor/esg.py" not in texto:
                continue
            permitidas = _frontmatter(texto).get("allowed-tools", "")
            self.assertIn("PowerShell(python", permitidas,
                          "La skill %s corre el motor pero no permite PowerShell (Windows)." % nombre)
            self.assertIn("Bash(python", permitidas,
                          "La skill %s corre el motor pero no permite Bash." % nombre)

    def test_ninguna_skill_usa_una_variable_que_no_existe_en_windows(self):
        culpables = [n for n in _skills()
                     if "${CLAUDE_SKILL_DIR}" in _leer(os.path.join(SKILLS, n, "SKILL.md"))]
        self.assertFalse(culpables, "Usan ${CLAUDE_SKILL_DIR}, que PowerShell no expande: %s."
                         % ", ".join(culpables))


class PruebaAgentes(unittest.TestCase):

    def test_todos_los_agentes_estan_en_el_plugin(self):
        declarados = json.loads(_leer(PLUGIN))["agents"]
        en_disco = {"./.claude/agents/%s.md" % n for n in _agentes()}
        faltan = en_disco - set(declarados)
        self.assertFalse(faltan, "Agentes sin registrar en plugin.json: %s." % sorted(faltan))

    def test_el_plugin_no_declara_agentes_inexistentes(self):
        for relativa in json.loads(_leer(PLUGIN))["agents"]:
            ruta = os.path.join(RAIZ, relativa.replace("./", "").replace("/", os.sep))
            self.assertTrue(os.path.isfile(ruta), "plugin.json declara %s y no existe." % relativa)

    def test_cada_agente_tiene_nombre_y_descripcion(self):
        for nombre in _agentes():
            campos = _frontmatter(_leer(os.path.join(AGENTES, nombre + ".md")))
            self.assertEqual(campos.get("name"), nombre)
            self.assertTrue(campos.get("description"), "El agente %s no tiene description." % nombre)


class PruebaReferencias(unittest.TestCase):
    """Ninguna skill puede mandar a otra que no existe."""

    def test_las_skills_mencionadas_existen(self):
        conocidos = set(_skills()) | set(_agentes()) | NO_SON_REFERENCIAS
        rotas = []
        for ruta, texto in _documentos():
            for mencion in re.findall(r"(?:skill|agente|skills|agentes)\s+`([a-z0-9-]+)`", texto):
                if mencion not in conocidos:
                    rotas.append("%s -> `%s`" % (ruta, mencion))
        self.assertFalse(rotas, "Referencias rotas: %s." % "; ".join(sorted(set(rotas))))

    def test_los_comandos_documentados_existen_en_el_motor(self):
        catalogo = _acciones_del_motor()
        rotos = []
        for ruta, texto in _documentos():
            for modulo, accion in re.findall(
                    r"python \.claude/motor/esg\.py\s+([a-z_]+)\s+([a-z_-]+)", texto):
                if modulo not in catalogo:
                    rotos.append("%s -> modulo «%s» no existe" % (ruta, modulo))
                elif accion not in catalogo[modulo]:
                    rotos.append("%s -> «%s %s» no existe (hay: %s)"
                                 % (ruta, modulo, accion, ", ".join(sorted(catalogo[modulo]))))
        self.assertFalse(rotos, "Comandos documentados que el motor no tiene: %s."
                         % "; ".join(sorted(set(rotos))))

    def test_los_archivos_de_datos_mencionados_existen(self):
        faltan = []
        for ruta, texto in _documentos():
            for archivo in re.findall(r"`\.claude/motor/datos/([a-z0-9_]+\.csv)`", texto):
                if not os.path.isfile(os.path.join(MOTOR, "datos", archivo)):
                    faltan.append("%s -> %s" % (ruta, archivo))
        self.assertFalse(faltan, "Archivos de datos mencionados que no existen: %s." % "; ".join(faltan))


class PruebaCatalogo(unittest.TestCase):
    """El catalogo que lee el asistente tiene que estar al dia.

    Si una capacidad no aparece aqui, el asistente no la va a ofrecer nunca:
    es como si no existiera (hallazgo H1 de docs/prueba-de-uso.md).
    """

    CATALOGO = os.path.join(SKILLS, "asistente", "catalogo.md")

    def test_el_catalogo_lista_todas_las_skills(self):
        texto = _leer(self.CATALOGO)
        # El asistente y el propio menu de ayuda no se ofrecen a si mismos.
        faltan = [n for n in _skills() if "`%s`" % n not in texto and n not in ("asistente",)]
        self.assertFalse(faltan, "Skills que faltan en el catalogo del asistente: %s." % ", ".join(faltan))

    def test_el_catalogo_lista_todos_los_agentes(self):
        texto = _leer(self.CATALOGO)
        faltan = [n for n in _agentes() if "`%s`" % n not in texto]
        self.assertFalse(faltan, "Agentes que faltan en el catalogo del asistente: %s." % ", ".join(faltan))

    def test_el_catalogo_no_ofrece_cosas_que_no_existen(self):
        texto = _leer(self.CATALOGO)
        conocidos = set(_skills()) | set(_agentes())
        inventadas = [m for m in re.findall(r"\| `([a-z0-9-]+)` \|$", texto, re.MULTILINE)
                      if m not in conocidos]
        self.assertFalse(inventadas, "El catalogo ofrece capacidades inexistentes: %s."
                         % ", ".join(sorted(set(inventadas))))


if __name__ == "__main__":
    unittest.main()
