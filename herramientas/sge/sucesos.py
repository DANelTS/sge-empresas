"""Bandejas de sucesos: de plantilla YAML a texto para el alumno.

Una bandeja es una colección de mensajes —correos, llamadas, notas de dirección—
que el alumno tiene que resolver en Odoo. La plantilla vive en
`empresas/<sector>/sucesos/<sesion>.yaml` y aquí se convierte en un Markdown con
los nombres y precios de **su** variante ya resueltos.

Marcas que se pueden usar en el texto:

    {{cliente:CLI-03}}                nombre del cliente
    {{producto:TOS-013}}              nombre del producto
    {{ref:TOS-013}}                   referencia interna
    {{precio:TOS-013}}                precio de tarifa, sin IVA
    {{precio_tarifa:CLI-03:TOS-013}}  precio con el descuento de su tarifa
    {{proveedor:PRV-MALTA}}           nombre del proveedor
    {{empresa}} / {{alumno}}

El bloque `operaciones` de la plantilla **no** se imprime: es la pista para el
solucionario del profesor y para el resolvedor del repositorio privado.
"""
from __future__ import annotations

import pathlib
import re

import yaml

from .catalogo import Empresa
from .maestros import Maestros
from .util import escribir_texto, euros

PATRON = re.compile(r"\{\{\s*([a-z_]+)(?::([A-Za-z0-9_\-]+))?(?::([A-Za-z0-9_\-]+))?\s*\}\}")

MEDIOS = {
    "correo": "Correo electrónico",
    "llamada": "Llamada telefónica",
    "nota": "Nota interna",
    "visita": "Visita concertada",
}


class ErrorSuceso(ValueError):
    pass


def _buscar(coleccion, clave, campo, etiqueta):
    for elemento in coleccion:
        if elemento[campo] == clave:
            return elemento
    raise ErrorSuceso(f"{etiqueta} desconocido en la plantilla: {clave}")


def _descuento(m: Maestros, clave: str | None) -> float:
    for t in m.tarifas:
        if t["clave"] == clave:
            return t["descuento"]
    return 0.0


def _resolver(marca: str, a: str | None, b: str | None, m: Maestros) -> str:
    if marca == "empresa":
        return m.empresa["nombre"]
    if marca == "alumno":
        return a or ""
    if marca == "cliente":
        return _buscar(m.clientes, a, "clave", "cliente")["nombre"]
    if marca == "proveedor":
        return _buscar(m.proveedores, a, "clave", "proveedor")["nombre"]
    if marca == "producto":
        return _buscar(m.productos, a, "ref", "producto")["nombre"]
    if marca == "ref":
        return _buscar(m.productos, a, "ref", "producto")["ref"]
    if marca == "precio":
        return euros(_buscar(m.productos, a, "ref", "producto")["pvp"])
    if marca == "precio_tarifa":
        cliente = _buscar(m.clientes, a, "clave", "cliente")
        producto = _buscar(m.productos, b, "ref", "producto")
        descuento = _descuento(m, cliente.get("tarifa"))
        return euros(round(producto["pvp"] * (1 - descuento / 100), 2))
    raise ErrorSuceso(f"marca desconocida en la plantilla: {{{{{marca}}}}}")


def renderizar(texto: str, m: Maestros) -> str:
    return PATRON.sub(
        lambda c: _resolver(c.group(1), c.group(2), c.group(3), m), texto
    )


def escribir_en(destino: pathlib.Path, a: Empresa, m: Maestros, sesion: str) -> pathlib.Path | None:
    """Genera `bandejas/<sesion>.md` en la carpeta de la variante, si hay plantilla."""
    plantilla = a.carpeta / "sucesos" / f"{sesion}.yaml"
    if not plantilla.is_file():
        return None
    datos = yaml.safe_load(plantilla.read_text(encoding="utf-8"))
    sucesos = datos.get("sucesos") or []
    if not sucesos:
        raise ErrorSuceso(f"{plantilla}: no hay sucesos")

    partes = [f"# Bandeja · {datos.get('titulo', sesion)}", ""]
    intro = (datos.get("intro") or "").strip()
    if intro:
        partes += [renderizar(intro, m), ""]
    partes += [
        f"**Empresa:** {m.empresa['nombre']}  ",
        f"**Sucesos:** {len(sucesos)}",
        "",
        "Cada suceso es un mensaje real: un correo, una llamada anotada o una nota",
        "de dirección. Léelo entero antes de tocar Odoo y decide **qué documento**",
        "hay que crear o modificar. Los datos exactos (referencias, precios) están",
        "en tu catálogo: `maestros/4-productos.csv`.",
        "",
        "---",
        "",
    ]

    for i, s in enumerate(sucesos, start=1):
        medio = MEDIOS.get(s.get("medio", "correo"), "Mensaje")
        cabecera = f"## {i}. {medio}"
        cuando = " ".join(x for x in (s.get("dia"), s.get("hora")) if x)
        if cuando:
            cabecera += f" · {cuando}"
        partes += [cabecera, ""]
        if s.get("de"):
            partes.append(f"**De:** {renderizar(s['de'], m)}")
        if s.get("asunto"):
            partes.append(f"**Asunto:** {renderizar(s['asunto'], m)}")
        if s.get("de") or s.get("asunto"):
            partes.append("")
        partes += [renderizar(s["texto"].strip(), m), ""]
        if s.get("incidencia"):
            partes += [
                "> **Aquí hay algo que no es de recibo.** No lo resuelvas «como",
                "> siempre»: piensa qué documento hay que emitir y por qué.",
                "",
            ]
        partes += ["---", ""]

    comprobacion = datos.get("comprobacion") or []
    if comprobacion:
        partes += ["## Comprueba tu trabajo", ""]
        partes += [f"- [ ] {renderizar(l, m)}" for l in comprobacion]
        partes.append("")

    ruta = destino / "bandejas" / f"{sesion}.md"
    escribir_texto(ruta, "\n".join(partes))
    return ruta
