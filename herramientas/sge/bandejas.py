"""Bandeja de sucesos de la sesión S17: altas manuales.

En S17 el alumno importa los maestros por CSV, pero dos productos y un proveedor
se dan de alta **a mano**, con el formulario, como se hace en una empresa cuando
aparece algo nuevo. Esos datos no pueden estar en los CSV (si estuvieran, no
habría nada que teclear), así que viven en el bloque `altas_manuales` del
catálogo del sector.

Si un sector no tiene ese bloque, este módulo deriva dos "formatos especiales" a
partir de su propio catálogo, para que la bandeja nunca salga vacía.
"""
from __future__ import annotations

import pathlib

from . import nif as nif_es
from .catalogo import Empresa
from .maestros import Maestros
from .util import escribir_texto, euros
from .variante import Variante


def _productos_para_alta(e: Empresa, v: Variante, m: Maestros) -> list[dict]:
    bloque = (e.catalogo.get("altas_manuales") or {}).get("productos")
    if bloque:
        salida = []
        for p in bloque:
            categoria = e.categoria(p["categoria"])
            salida.append({
                "ref": p["ref"],
                "nombre": p["nombre"],
                "categoria": categoria["nombre"],
                "iva": p.get("iva_venta", categoria.get("iva_venta")),
                "iva_compra": p.get("iva_compra", categoria.get("iva_compra")),
                "coste": v.coste(p["coste"]),
                "pvp": v.precio(p["pvp"]),
                "tipo": p.get("tipo", "almacenable"),
                "proveedor": p.get("proveedor"),
                "minimo": p.get("minimo"),
                "maximo": p.get("maximo"),
            })
        return salida

    # Sin bloque propio: dos formatos nuevos a partir de los productos que ya hay.
    candidatos = [p for p in m.productos if p["tipo"] == "almacenable" and p["venta"]]
    vistos, elegidos = set(), []
    for p in candidatos:
        if p["categoria"] in vistos:
            continue
        vistos.add(p["categoria"])
        elegidos.append(p)
        if len(elegidos) == 2:
            break
    return [
        {
            "ref": f"{p['ref'].split('-')[0]}-9{i}",
            "nombre": f"{p['nombre']} — formato especial",
            "categoria": p["categoria_nombre"],
            "iva": p["iva_venta"],
            "iva_compra": p["iva_compra"],
            "coste": round(p["coste"] * 2.2, 2),
            "pvp": round(p["pvp"] * 2.3, 2),
            "tipo": "almacenable",
            "proveedor": p["proveedor"],
            "minimo": 4,
            "maximo": 20,
        }
        for i, p in enumerate(elegidos, start=1)
    ]


def escribir(destino: pathlib.Path, e: Empresa, m: Maestros, v: Variante) -> pathlib.Path:
    productos = _productos_para_alta(e, v, m)
    proveedores = (e.catalogo.get("altas_manuales") or {}).get("proveedores", [])

    lineas = [
        "# Bandeja de la S17 · Altas a mano",
        "",
        "Los CSV te dan el volumen. Estas tres fichas se dan de alta **con el",
        "formulario**, una por una, como cuando en una empresa aparece un producto",
        "nuevo o un proveedor con el que no se había trabajado.",
        "",
        "Copia los datos tal cual: si cambias un precio o una referencia, la",
        "comprobación automática no cuadrará.",
        "",
        "## Productos",
        "",
    ]
    for i, p in enumerate(productos, start=1):
        lineas += [
            f"### Alta {i} · {p['nombre']}",
            "",
            "| Campo del formulario | Valor |",
            "|---|---|",
            f"| Nombre | {p['nombre']} |",
            f"| Referencia interna | `{p['ref']}` |",
            f"| Categoría de producto | {p['categoria']} |",
            f"| Tipo de producto | {'Servicio' if p['tipo'] == 'servicio' else 'Mercancía'} |",
            f"| Rastrear inventario | {'No' if p['tipo'] == 'servicio' else 'Sí'} |",
            f"| Precio de venta | {euros(p['pvp'])} |",
            f"| Coste | {euros(p['coste'])} |",
            f"| Impuesto de ventas | {p['iva']} % (en Odoo se llama «{p['iva']}% B» si es mercancía) |",
            f"| Impuesto de compras | {p['iva_compra']} % |",
        ]
        if p.get("proveedor"):
            nombre_prov = e.proveedor(p["proveedor"])["nombre"]
            lineas.append(f"| Proveedor | {nombre_prov} |")
        if p.get("minimo"):
            lineas.append(f"| Regla de reabastecimiento | mínimo {p['minimo']}, máximo {p['maximo']} |")
        lineas += [
            "",
            "Ruta: **Ventas → Productos → Productos → Nuevo**.",
            "",
        ]

    if proveedores:
        lineas += ["## Proveedor", ""]
        for prov in proveedores:
            # El NIF del proveedor se genera si el del catálogo no es válido:
            # Odoo lo comprueba y rechazaría el alta.
            documento = prov.get("nif", "")
            if not nif_es.valido(documento):
                letra = documento[0].upper() if documento and documento[0].isalpha() else "B"
                documento = nif_es.cif(letra, f"{v.entero(1_000_000, 9_999_999):07d}")
            lineas += [
                f"### {prov['nombre']}",
                "",
                "| Campo del formulario | Valor |",
                "|---|---|",
                f"| Nombre | {prov['nombre']} |",
                f"| Es una compañía | Sí |",
                f"| NIF | `{documento}` |",
                f"| Dirección | {prov['calle']} |",
                f"| C.P. / Ciudad | {prov['cp']} — {prov['poblacion']} |",
                f"| Provincia | {prov['provincia']} |",
                f"| País | España |",
                f"| Teléfono | {prov['telefono']} |",
                f"| Correo electrónico | {prov['email']} |",
                f"| Condiciones de pago de proveedor | {prov['cond_pago']} |",
                "",
                "Ruta: **Contactos → Nuevo**, marcando *Es una compañía*.",
                "",
            ]

    lineas += [
        "## Cuando termines",
        "",
        "1. Comprueba que los dos productos aparecen en la lista con su referencia.",
        "2. Ejecuta `cargar_historico.py`: es quien les pone el IVA definitivo y",
        "   quien carga el stock y el histórico.",
        "3. Ejecuta `verificar.py`. Tiene que salir en verde.",
        "",
    ]

    ruta = destino / "bandejas" / "s17-altas.md"
    escribir_texto(ruta, "\n".join(lineas))
    return ruta
