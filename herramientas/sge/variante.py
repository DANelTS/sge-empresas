"""Variantes deterministas por alumno.

La semilla es (empresa, alumno). Con la misma pareja se obtienen siempre los
mismos números, nombres y documentos: eso permite corregir, repetir una demo y
comparar dos ejecuciones. La variante 00 es la canónica (la que usan las
pruebas automáticas del repositorio).
"""
from __future__ import annotations

import hashlib
import random

from . import nif
from .util import precio_comercial, redondear


def _semilla(empresa: str, alumno: int) -> int:
    texto = f"sge-empresas|{empresa}|{alumno:02d}".encode()
    return int.from_bytes(hashlib.sha256(texto).digest()[:8], "big")


class Variante:
    """Generador pseudoaleatorio estable para una pareja (empresa, alumno)."""

    def __init__(self, empresa: str, alumno: int):
        if not 0 <= alumno <= 99:
            raise ValueError("el número de alumno debe estar entre 0 y 99")
        self.empresa = empresa
        self.alumno = alumno
        self.rnd = random.Random(_semilla(empresa, alumno))
        self._contador_cif = 0

    # -- Identidad ---------------------------------------------------------
    @property
    def sufijo(self) -> str:
        """'— A07' o cadena vacía para la variante canónica 00."""
        return "" if self.alumno == 0 else f" — A{self.alumno:02d}"

    def nombre_empresa(self, nombre: str, forma: str) -> str:
        return f"{nombre} {forma}{self.sufijo}"

    def cif(self, letra: str) -> str:
        """CIF válido. La variante 00 usa el CIF del catálogo si se indica."""
        self._contador_cif += 1
        base = self.rnd.randrange(1_000_000, 9_999_999)
        return nif.cif(letra, f"{base:07d}")

    def iban(self, banco: str = "2100", sucursal: str = "4567") -> str:
        cuenta = f"{self.rnd.randrange(10**9, 10**10 - 1):010d}"
        return nif.iban_es(banco, sucursal, cuenta)

    def telefono(self, prefijo: str = "91") -> str:
        return f"{prefijo} {self.rnd.randrange(100, 999)} {self.rnd.randrange(10, 99)} {self.rnd.randrange(10, 99)}"

    def movil(self) -> str:
        return f"6{self.rnd.randrange(10, 99)} {self.rnd.randrange(100, 999)} {self.rnd.randrange(100, 999)}"

    def email_cliente(self, nombre: str) -> str:
        from .util import slug
        return f"{slug(nombre)[:30].strip('-')}@correo.example"

    # -- Precios -----------------------------------------------------------
    def variacion(self) -> float:
        """±10 % para precios y costes."""
        return 1 + self.rnd.uniform(-0.10, 0.10)

    def precio(self, base: float) -> float:
        return precio_comercial(base * self.variacion())

    def coste(self, base: float) -> float:
        return redondear(base * self.variacion())

    # -- Utilidades --------------------------------------------------------
    def elegir(self, secuencia):
        return self.rnd.choice(list(secuencia))

    def muestra(self, secuencia, n: int):
        secuencia = list(secuencia)
        return self.rnd.sample(secuencia, min(n, len(secuencia)))

    def entero(self, minimo: int, maximo: int) -> int:
        return self.rnd.randint(minimo, maximo)

    def proporcional(self, valor: float, minimo: float = 0.8, maximo: float = 1.2) -> float:
        return valor * self.rnd.uniform(minimo, maximo)
