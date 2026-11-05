"""Planificación del histórico de una variante (sin hablar con Odoo).

Con el catálogo, la variante y los datos maestros ya generados, este módulo
decide **qué documentos** forman el histórico de la empresa entre agosto y
octubre de 2026: qué se compró, qué se vendió, cuándo se entregó, cuándo se
facturó y cuánto se cobró.

Es determinista: con la misma pareja (empresa, alumno) sale siempre el mismo
plan. Y es autosuficiente: calcula también el stock inicial necesario para que
ninguna entrega se quede sin existencias.

`cargar_historico.py` es quien convierte este plan en pedidos, albaranes,
facturas y cobros reales en Odoo.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import random
from dataclasses import dataclass, field

from .catalogo import Empresa
from .maestros import Maestros

# Reparto de meses: en agosto media hostelería de Madrid está de vacaciones.
PESO_MES = {8: 0.7, 9: 1.3, 10: 1.1}

# Peso por segmento de cliente: las cafeterías compran poco y a menudo; el
# distribuidor compra mucho y de vez en cuando.
PESO_SEGMENTO = {
    "Cafetería": 3.0, "Restaurante": 2.0, "Hotel": 1.0, "Distribuidor": 1.2,
    "Tienda de café": 1.0, "Particular": 1.0,
}


@dataclass
class Linea:
    ref: str
    cantidad: float
    precio: float          # precio unitario ya con el descuento aplicado
    descuento: float = 0.0


@dataclass
class Venta:
    fecha: dt.date
    cliente: str           # clave CLI-xx
    lineas: list[Linea]
    entrega: dt.date
    factura: bool = True
    fecha_factura: dt.date | None = None
    cobro: str = "total"   # total | parcial | nada
    fecha_cobro: dt.date | None = None


@dataclass
class Compra:
    fecha: dt.date
    proveedor: str         # clave PRV-xx
    lineas: list[Linea]
    recepcion: dt.date
    factura: bool = True
    fecha_factura: dt.date | None = None
    pago: str = "total"    # total | parcial | nada
    fecha_pago: dt.date | None = None


@dataclass
class Plan:
    desde: dt.date
    hasta: dt.date
    stock_inicial: dict[str, float] = field(default_factory=dict)
    compras: list[Compra] = field(default_factory=list)
    ventas: list[Venta] = field(default_factory=list)

    def resumen(self) -> str:
        previsto = sum(
            l.cantidad * l.precio for v in self.ventas for l in v.lineas if l.precio
        )
        return (
            f"{len(self.ventas)} pedidos de venta y {len(self.compras)} compras "
            f"entre {self.desde:%d/%m/%Y} y {self.hasta:%d/%m/%Y} "
            f"(≈ {previsto:,.0f} € de venta prevista)"
        ).replace(",", ".")


def _rnd(empresa: str, alumno: int) -> random.Random:
    texto = f"sge-historico|{empresa}|{alumno:02d}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(texto).digest()[:8], "big"))


def _fecha(rnd: random.Random, desde: dt.date, hasta: dt.date) -> dt.date:
    dias = (hasta - desde).days
    return desde + dt.timedelta(days=rnd.randint(0, dias))


def _fecha_ponderada(rnd: random.Random, desde: dt.date, hasta: dt.date) -> dt.date:
    """Fecha con más peso en septiembre y octubre que en agosto."""
    while True:
        fecha = _fecha(rnd, desde, hasta)
        if rnd.random() < PESO_MES.get(fecha.month, 1.0) / 1.3:
            return fecha


def _cantidad(rnd: random.Random, producto: dict) -> int:
    """Cuanto más barato es el producto, más unidades se piden."""
    if producto["tipo"] == "servicio":
        return 1
    precio = producto["pvp"] or 10
    if precio <= 0:
        return 1
    tope = max(1, min(24, int(320 / precio)))
    return rnd.randint(max(1, tope // 3), tope)


def _lineas_venta(rnd: random.Random, m: Maestros, descuento: float) -> list[Linea]:
    vendibles = [p for p in m.productos if p["venta"] and p["pvp"] > 0]
    cafes = [p for p in vendibles if p["categoria"] in ("CAFE-TUESTE",)]
    otros = [p for p in vendibles if p["categoria"] not in ("CAFE-TUESTE",)]
    elegidos: list[dict] = []
    # La base del pedido es café; a veces se añade menaje o un servicio.
    for _ in range(rnd.choice([1, 1, 2, 2, 3])):
        elegidos.append(rnd.choice(cafes or vendibles))
    if otros and rnd.random() < 0.18:
        elegidos.append(rnd.choice(otros))

    lineas, vistos = [], set()
    for p in elegidos:
        if p["ref"] in vistos:
            continue
        vistos.add(p["ref"])
        precio = round(p["pvp"] * (1 - descuento / 100), 2)
        lineas.append(Linea(ref=p["ref"], cantidad=_cantidad(rnd, p),
                            precio=precio, descuento=descuento))
    return lineas


def planificar(e: Empresa, m: Maestros, alumno: int) -> Plan:
    rnd = _rnd(e.clave, alumno)
    parametros = e.catalogo.get("historico", {})
    desde = dt.date.fromisoformat(str(parametros.get("desde", "2026-08-01")))
    hasta = dt.date.fromisoformat(str(parametros.get("hasta", "2026-10-31")))
    n_ventas = int(parametros.get("ventas", 72))
    n_compras = int(parametros.get("compras", 18))

    plan = Plan(desde=desde, hasta=hasta)

    # ---- Compras: se compra materia prima y consumibles ------------------
    comprables = [p for p in m.productos if p["compra"] and p["proveedor"]]
    # Solo se compra a quien sirve producto: la mensajería factura portes, no
    # género, y no debe recibir pedidos de compra.
    con_compra = [
        p for p in m.proveedores
        if any(x["proveedor"] == p["clave"] for x in comprables)
    ] or m.proveedores
    # La materia prima se compra mucho más a menudo que el menaje.
    pesos = [4.0 if "VERDE" in p["clave"] else 1.0 for p in con_compra]
    for _ in range(n_compras):
        proveedor = rnd.choices(con_compra, weights=pesos, k=1)[0]["clave"]
        del_proveedor = [p for p in comprables if p["proveedor"] == proveedor] or comprables
        lineas = []
        for p in rnd.sample(del_proveedor, min(len(del_proveedor), rnd.choice([1, 1, 2]))):
            cantidad = 1 if p["coste"] > 200 else rnd.randint(2, 8)
            lineas.append(Linea(ref=p["ref"], cantidad=cantidad, precio=p["coste"]))
        fecha = _fecha(rnd, desde - dt.timedelta(days=20), hasta)
        recepcion = fecha + dt.timedelta(days=rnd.randint(2, 8))
        fecha_factura = recepcion + dt.timedelta(days=rnd.randint(0, 4))
        pago = "nada" if rnd.random() < 0.12 else ("parcial" if rnd.random() < 0.08 else "total")
        plan.compras.append(Compra(
            fecha=fecha, proveedor=proveedor, lineas=lineas, recepcion=recepcion,
            fecha_factura=fecha_factura, pago=pago,
            fecha_pago=fecha_factura + dt.timedelta(days=rnd.randint(10, 45)),
        ))

    # ---- Ventas ----------------------------------------------------------
    tarifas = {t["clave"]: t["descuento"] for t in m.tarifas}
    for _ in range(n_ventas):
        cliente = _elegir_cliente(rnd, m)
        fecha = _fecha_ponderada(rnd, desde, hasta)
        lineas = _lineas_venta(rnd, m, tarifas.get(cliente.get("tarifa"), 0))
        if not lineas:
            continue
        entrega = fecha + dt.timedelta(days=rnd.choice([0, 1, 1, 2, 3]))
        fecha_factura = entrega + dt.timedelta(days=rnd.choice([0, 0, 1, 2, 5]))
        azar = rnd.random()
        if azar < 0.08:
            cobro = "nada"
        elif azar < 0.18:
            cobro = "parcial"
        else:
            cobro = "total"
        plan.ventas.append(Venta(
            fecha=fecha, cliente=cliente["clave"], lineas=lineas, entrega=entrega,
            fecha_factura=fecha_factura, cobro=cobro,
            fecha_cobro=fecha_factura + dt.timedelta(days=rnd.randint(8, 52)),
        ))

    plan.compras.sort(key=lambda c: c.fecha)
    plan.ventas.sort(key=lambda v: v.fecha)
    plan.stock_inicial = _stock_inicial(m, plan)
    return plan


def _elegir_cliente(rnd: random.Random, m: Maestros) -> dict:
    pesos = [PESO_SEGMENTO.get(c.get("segmento"), 1.0) for c in m.clientes]
    total = sum(pesos)
    r = rnd.uniform(0, total)
    acumulado = 0.0
    for cliente, peso in zip(m.clientes, pesos):
        acumulado += peso
        if r <= acumulado:
            return cliente
    return m.clientes[-1]


def _stock_inicial(m: Maestros, plan: Plan) -> dict[str, float]:
    """Existencias al 31/07/2026 que garantizan que no se vende lo que no hay.

    Se simula el saldo producto a producto en orden cronológico y se toma el
    punto más bajo: el stock inicial debe cubrir ese hueco más un margen.
    """
    movimientos: dict[str, list[tuple[dt.date, float]]] = {p["ref"]: [] for p in m.productos}
    for c in plan.compras:
        for l in c.lineas:
            movimientos.setdefault(l.ref, []).append((c.recepcion, +l.cantidad))
    for v in plan.ventas:
        for l in v.lineas:
            movimientos.setdefault(l.ref, []).append((v.entrega, -l.cantidad))

    stock = {}
    for p in m.productos:
        ref = p["ref"]
        saldo = 0.0
        minimo = 0.0
        salido = 0.0
        for _, delta in sorted(movimientos.get(ref, [])):
            saldo += delta
            if delta < 0:
                salido += -delta
            minimo = min(minimo, saldo)
        # Colchón proporcional a lo que se vende de verdad: 25 % de las salidas
        # del trimestre, con un mínimo de 2 y un techo de 24. Así una bici de
        # 3.000 € no acumula 22 unidades en el almacén.
        margen = max(2, min(24, int(salido * 0.25) + 2))
        stock[ref] = round(max(0.0, -minimo) + margen, 2)
    return stock
