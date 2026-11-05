"""Carga y validación de los ficheros de definición de una empresa.

Cada sector vive en `empresas/<clave>/` y tiene dos ficheros:

- `catalogo.yaml`: la empresa, sus categorías, productos, proveedores, clientes
  y tarifas. Es la definición "canónica"; el generador la convierte en la
  variante de cada alumno.
- `nombres.yaml`: bolsas de nombres, calles y poblaciones con las que el
  generador construye direcciones verosímiles y distintas por alumno.

Este módulo solo lee y comprueba; no genera nada.
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Any

import yaml

RAIZ = pathlib.Path(__file__).resolve().parents[2]
EMPRESAS = RAIZ / "empresas"

TIPOS_PRODUCTO = {"almacenable", "servicio"}


class ErrorCatalogo(ValueError):
    """Error de contenido en un fichero de empresa, con mensaje para el docente."""


@dataclass
class Empresa:
    clave: str
    carpeta: pathlib.Path
    catalogo: dict[str, Any]
    nombres: dict[str, Any]

    # Atajos cómodos
    @property
    def datos(self) -> dict[str, Any]:
        return self.catalogo["empresa"]

    @property
    def nombre(self) -> str:
        return self.datos["nombre"]

    @property
    def categorias(self) -> list[dict]:
        return self.catalogo["categorias"]

    @property
    def productos(self) -> list[dict]:
        return self.catalogo["productos"]

    @property
    def proveedores(self) -> list[dict]:
        return self.catalogo["proveedores"]

    @property
    def clientes(self) -> list[dict]:
        return self.catalogo["clientes"]

    @property
    def tarifas(self) -> list[dict]:
        return self.catalogo.get("tarifas", [])

    def categoria(self, clave: str) -> dict:
        for c in self.categorias:
            if c["clave"] == clave:
                return c
        raise ErrorCatalogo(f"{self.clave}: categoría desconocida {clave!r}")

    def producto(self, ref: str) -> dict:
        for p in self.productos:
            if p["ref"] == ref:
                return p
        raise ErrorCatalogo(f"{self.clave}: producto desconocido {ref!r}")

    def proveedor(self, clave: str) -> dict:
        for p in self.proveedores:
            if p["clave"] == clave:
                return p
        raise ErrorCatalogo(f"{self.clave}: proveedor desconocido {clave!r}")

    def cliente(self, clave: str) -> dict:
        for c in self.clientes:
            if c["clave"] == clave:
                return c
        raise ErrorCatalogo(f"{self.clave}: cliente desconocido {clave!r}")


def sectores() -> list[str]:
    """Claves de las empresas disponibles (carpetas con catalogo.yaml)."""
    if not EMPRESAS.is_dir():
        return []
    return sorted(
        p.name for p in EMPRESAS.iterdir()
        if p.is_dir() and (p / "catalogo.yaml").is_file()
    )


def cargar(clave: str) -> Empresa:
    carpeta = EMPRESAS / clave
    if not (carpeta / "catalogo.yaml").is_file():
        raise ErrorCatalogo(
            f"No existe la empresa {clave!r}. Disponibles: {', '.join(sectores()) or 'ninguna'}"
        )
    catalogo = yaml.safe_load((carpeta / "catalogo.yaml").read_text(encoding="utf-8"))
    nombres = yaml.safe_load((carpeta / "nombres.yaml").read_text(encoding="utf-8"))
    empresa = Empresa(clave=clave, carpeta=carpeta, catalogo=catalogo, nombres=nombres)
    validar(empresa)
    return empresa


def validar(e: Empresa) -> None:
    """Comprobaciones que evitan errores silenciosos al generar."""
    faltan = [
        campo for campo in (
            "nombre", "forma_juridica", "letra_cif", "domicilio", "cp", "poblacion",
            "provincia", "telefono", "email", "cond_pago_ventas",
            "cond_pago_compras",
        )
        if campo not in e.datos
    ]
    if faltan:
        raise ErrorCatalogo(f"{e.clave}: faltan datos de empresa: {', '.join(faltan)}")

    if not e.categorias:
        raise ErrorCatalogo(f"{e.clave}: no hay categorías")
    if not e.productos:
        raise ErrorCatalogo(f"{e.clave}: no hay productos")

    claves_cat = [c["clave"] for c in e.categorias]
    if len(set(claves_cat)) != len(claves_cat):
        raise ErrorCatalogo(f"{e.clave}: claves de categoría repetidas")

    refs = [p["ref"] for p in e.productos]
    if len(set(refs)) != len(refs):
        raise ErrorCatalogo(f"{e.clave}: referencias de producto repetidas")

    claves_prov = [p["clave"] for p in e.proveedores]
    claves_cli = [c["clave"] for c in e.clientes]
    if len(set(claves_prov)) != len(claves_prov):
        raise ErrorCatalogo(f"{e.clave}: claves de proveedor repetidas")
    if len(set(claves_cli)) != len(claves_cli):
        raise ErrorCatalogo(f"{e.clave}: claves de cliente repetidas")

    for p in e.productos:
        if p.get("tipo", "almacenable") not in TIPOS_PRODUCTO:
            raise ErrorCatalogo(f"{e.clave}/{p['ref']}: tipo {p.get('tipo')!r} no válido")
        e.categoria(p["categoria"])          # lanza si no existe
        if p.get("proveedor"):
            e.proveedor(p["proveedor"])      # lanza si no existe
        for campo in ("nombre", "coste", "pvp"):
            if campo not in p:
                raise ErrorCatalogo(f"{e.clave}/{p['ref']}: falta {campo!r}")

    for c in e.clientes:
        if c.get("tarifa") and not any(t["clave"] == c["tarifa"] for t in e.tarifas):
            raise ErrorCatalogo(f"{e.clave}/{c['clave']}: tarifa desconocida {c['tarifa']!r}")

    for seccion in ("clientes", "poblaciones", "calles"):
        if not e.nombres.get(seccion):
            raise ErrorCatalogo(f"{e.clave}/nombres.yaml: falta la sección {seccion!r}")
