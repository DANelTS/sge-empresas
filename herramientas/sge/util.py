"""Utilidades comunes: redondeos comerciales, texto y escritura de CSV."""
from __future__ import annotations

import csv
import pathlib
import unicodedata
from decimal import ROUND_HALF_UP, Decimal

# Terminaciones "de tienda": un precio de catálogo casi nunca acaba en ,37.
TERMINACIONES = ("00", "50", "95", "99", "90", "49")


def a_decimal(valor) -> Decimal:
    return Decimal(str(valor))


def redondear(valor, decimales: int = 2) -> float:
    """Redondeo comercial (mitad hacia arriba), no el de Python."""
    cuantia = Decimal(1).scaleb(-decimales)
    return float(a_decimal(valor).quantize(cuantia, rounding=ROUND_HALF_UP))


def precio_comercial(valor, terminaciones=TERMINACIONES) -> float:
    """Ajusta un importe a la terminación comercial más cercana.

    Sirve para que los precios del catálogo parezcan de verdad: 14,50 / 8,95 /
    12,99 en lugar de 14,37. Se usa solo con precios de venta y de coste.
    """
    valor = round(float(valor), 2)
    if valor < 0.5:
        return redondear(valor)
    entero = int(valor)
    candidatos = []
    for t in terminaciones:
        decimales = int(t) / 100
        for e in (entero - 1, entero, entero + 1):
            if e >= 0:
                candidatos.append(round(e + decimales, 2))
    return min(candidatos, key=lambda c: (abs(c - valor), c))


def slug(texto: str) -> str:
    """'Café con Leche' -> 'cafe-con-leche' (para ids y correos)."""
    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    limpio = [c.lower() if c.isalnum() else "-" for c in sin_acentos]
    return "-".join(filter(None, "".join(limpio).split("-")))


def escribir_csv(ruta: pathlib.Path, columnas: list[str], filas: list[dict]) -> None:
    """Escribe un CSV UTF-8 (sin BOM, con LF) listo para el importador de Odoo."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore", lineterminator="\n")
        escritor.writeheader()
        for fila in filas:
            escritor.writerow(fila)


def escribir_texto(ruta: pathlib.Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto if texto.endswith("\n") else texto + "\n", encoding="utf-8")


def euros(valor) -> str:
    """1234.5 -> '1.234,50 €' (formato español)."""
    texto = f"{float(valor):,.2f}"
    return texto.replace(",", "\0").replace(".", ",").replace("\0", ".") + " €"
