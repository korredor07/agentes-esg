# -*- coding: utf-8 -*-
"""Utilidades compartidas por las pruebas: rutas del motor y carpetas temporales."""

import os
import sys
import shutil
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTOR = os.path.join(RAIZ, ".claude", "motor")
if MOTOR not in sys.path:
    sys.path.insert(0, MOTOR)


class PruebaConCarpeta(unittest.TestCase):
    """Crea una carpeta temporal por prueba y la borra al terminar."""

    def setUp(self):
        self.carpeta = tempfile.mkdtemp(prefix="agentes-esg-")

    def tearDown(self):
        shutil.rmtree(self.carpeta, ignore_errors=True)

    def ruta(self, *partes):
        return os.path.join(self.carpeta, *partes)
