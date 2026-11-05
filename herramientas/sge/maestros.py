"""Construcción de los datos maestros de una variante.

Entra el catálogo del sector + el número de alumno; salen las listas de
categorías, productos, proveedores, clientes y tarifas ya con los números,
nombres y documentos de esa variante.

Reglas de variación (las del plan de trabajo):
- cambian precios y costes (±10 %, con terminación comercial), el stock
  inicial, los NIF, el IBAN, los teléfonos, las direcciones y los nombres de
  los clientes (de la bolsa de nombres);
- no cambian las referencias de producto, la estructura del catálogo ni el
  tipo de preguntas.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import nif
from .catalogo import Empresa
from .util import redondear
from .variante import Variante

LETRA_POR_FORMA = {
    "S.L.": "B", "S.L.U.": "B", "S.A.": "A", "S.A.U.": "A",
    "S. Coop.": "F", "S. Coop. Mad.": "F", "S.C.": "E", "C.B.": "E",
    "Sociedad Civil": "E", "Asociación": "G", "Fundación": "G",
    "Ayuntamiento": "P", "Organismo autónomo": "S",
}


@dataclass
class Maestros:
    empresa: dict
    categorias: list[dict] = field(default_factory=list)
    productos: list[dict] = field(default_factory=list)
    proveedores: list[dict] = field(default_factory=list)
    clientes: list[dict] = field(default_factory=list)
    tarifas: list[dict] = field(default_factory=list)


def codigo_barras(v: Variante, prefijo: str = "20") -> str:
    """EAN-13 con dígito de control válido y prefijo de uso interno (20-29)."""
    cuerpo = prefijo + "".join(str(v.entero(0, 9)) for _ in range(10))
    suma = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(cuerpo))
    control = (10 - suma % 10) % 10
    return f"{cuerpo}{control}"


def _direccion(v: Variante, e: Empresa, usadas: set[str]) -> dict:
    """Calle, número, CP y población coherentes entre sí."""
    for _ in range(200):
        poblacion = v.elegir(e.nombres["poblaciones"])
        calle = v.elegir(e.nombres["calles"])
        numero = v.entero(1, 120)
        piso = v.elegir(["", " 1.º A", " 2.º B", " 3.º C", " bajo", " local"])
        linea = f"{calle}, {numero}{piso}"
        if linea not in usadas:
            usadas.add(linea)
            return {
                "calle": linea,
                "cp": str(poblacion["cp"]),
                "poblacion": poblacion["poblacion"],
                "provincia": poblacion["provincia"],
            }
    raise RuntimeError("no quedan direcciones libres en la bolsa del sector")


def construir(e: Empresa, v: Variante) -> Maestros:
    datos = e.datos
    letra = datos["letra_cif"]

    empresa = {
        "nombre": v.nombre_empresa(datos["nombre"], datos["forma_juridica"]),
        "nombre_corto": datos["nombre"],
        "cif": nif.cif(letra, f"{v.entero(1_000_000, 9_999_999):07d}"),
        "domicilio": datos["domicilio"],
        "cp": str(datos["cp"]),
        "poblacion": datos["poblacion"],
        "provincia": datos["provincia"],
        "telefono": datos["telefono"],
        "email": datos["email"],
        "web": datos["web"],
        "iban": v.iban(datos.get("banco", "2100"), datos.get("sucursal", "4567")),
        "cond_pago_ventas": datos["cond_pago_ventas"],
        "cond_pago_compras": datos["cond_pago_compras"],
    }

    # -- Categorías --------------------------------------------------------
    categorias = [
        {
            "clave": c["clave"],
            "id": f"cat-{c['clave']}",
            "nombre": c["nombre"],
            "iva_venta": c.get("iva_venta"),
            "iva_compra": c.get("iva_compra"),
        }
        for c in e.categorias
    ]

    # -- Tarifas -----------------------------------------------------------
    tarifas = [
        {"clave": t["clave"], "id": f"tar-{t['clave']}", "nombre": t["nombre"], "descuento": t.get("descuento", 0)}
        for t in e.tarifas
    ]

    # -- Proveedores -------------------------------------------------------
    proveedores = []
    usadas: set[str] = set()
    for i, p in enumerate(e.proveedores, start=1):
        direccion = {
            "calle": p.get("calle"),
            "cp": str(p.get("cp", "")),
            "poblacion": p.get("poblacion"),
            "provincia": p.get("provincia"),
        }
        if not all(direccion.values()):
            direccion = _direccion(v, e, usadas)
        letra_p = p.get("letra_cif", LETRA_POR_FORMA.get(p.get("forma_juridica", "S.L."), "B"))
        proveedores.append({
            "clave": p["clave"],
            "id": f"prv-{i:02d}",
            "nombre": p["nombre"],
            "es_empresa": True,
            "nif": nif.cif(letra_p, f"{v.entero(1_000_000, 9_999_999):07d}"),
            "actividad": p.get("actividad", ""),
            "cond_pago": p.get("cond_pago", datos["cond_pago_compras"]),
            "telefono": v.telefono(v.elegir(["91", "96", "95", "93", "94"])),
            "email": f"pedidos@{p.get('dominio', 'proveedor.example')}",
            **direccion,
        })

    # -- Productos ---------------------------------------------------------
    productos = []
    for p in e.productos:
        categoria = e.categoria(p["categoria"])
        tipo = p.get("tipo", "almacenable")
        productos.append({
            "ref": p["ref"],
            "id": f"prod-{p['ref']}",
            "nombre": p["nombre"],
            "categoria": categoria["clave"],
            "categoria_nombre": categoria["nombre"],
            "iva_venta": p.get("iva_venta", categoria.get("iva_venta")),
            "iva_compra": p.get("iva_compra", categoria.get("iva_compra")),
            "pvp": v.precio(p["pvp"]),
            "coste": v.coste(p["coste"]),
            "tipo": "servicio" if tipo == "servicio" else "almacenable",
            "proveedor": p.get("proveedor"),
            "minimo": p.get("minimo"),
            "maximo": p.get("maximo"),
            "compra": p.get("compra", tipo != "servicio"),
            "venta": p.get("venta", True),
            "barcode": codigo_barras(v) if tipo != "servicio" else "",
        })

    # -- Clientes ----------------------------------------------------------
    bolsa = list(e.nombres["clientes"]["empresas"]) + list(e.nombres["clientes"]["particulares"])
    v.rnd.shuffle(bolsa)
    if len(bolsa) < len(e.clientes):
        raise ValueError(
            f"{e.clave}: hay {len(e.clientes)} clientes en el catálogo y solo "
            f"{len(bolsa)} nombres en nombres.yaml"
        )

    clientes = []
    for i, (c, nombre) in enumerate(zip(e.clientes, bolsa), start=1):
        particular = c.get("tipo") == "particular"
        if particular:
            documento = nif.dni(v.entero(10_000_000, 79_999_999))
        else:
            forma = c.get("forma_juridica", "S.L.")
            documento = nif.cif(LETRA_POR_FORMA.get(forma, "B"), f"{v.entero(1_000_000, 9_999_999):07d}")
        direccion = _direccion(v, e, usadas)
        clientes.append({
            "clave": c["clave"],
            "id": f"cli-{i:02d}",
            "ref": f"CLI-{i:02d}",
            "nombre": nombre,
            "es_empresa": not particular,
            "nif": documento,
            "tarifa": c.get("tarifa"),
            "cond_pago": c.get("cond_pago", "30 días" if not particular else "Pago inmediato"),
            "segmento": c.get("segmento", ""),
            "telefono": v.telefono(v.elegir(["91", "91", "91", "91", "96", "95"])) if not particular else v.movil(),
            "email": v.email_cliente(nombre),
            "comentario": c.get("comentario", ""),
            **direccion,
        })

    return Maestros(
        empresa=empresa,
        categorias=categorias,
        productos=productos,
        proveedores=proveedores,
        clientes=clientes,
        tarifas=tarifas,
    )
