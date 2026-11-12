#!/usr/bin/env python3
"""cargar_historico.py — carga en Odoo el histórico de una variante.

Qué hace, en este orden:

1. Regenera en memoria la variante (misma semilla que `generar.py`, mismos datos).
2. Comprueba que los datos maestros están importados (productos, clientes y
   proveedores). Si falta algo, dice exactamente qué falta.
3. Asigna a cada producto su IVA de venta y de compra.
4. Fija el stock inicial al 31/07/2026 con un ajuste de inventario.
5. Crea las compras (pedido → recepción → factura → pago).
6. Crea las ventas (pedido → albarán → factura → cobro).
7. Deja una marca para no duplicar nada si se ejecuta dos veces.

Uso:

    docker compose run --rm herramientas cargar_historico.py --empresa cerveceria --alumno 07
    docker compose run --rm herramientas cargar_historico.py --empresa cerveceria --alumno 07 --seco

`--seco` no toca la base de datos: solo enseña el plan que aplicaría.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys

from odoo_api import ErrorOdoo, Odoo
from sge import catalogo, historico, maestros
from sge.variante import Variante

RAIZ = pathlib.Path(__file__).resolve().parents[1]
CLAVE_MARCA = "sge.historico"


# ---------------------------------------------------------------------------
# Utilidades de Odoo
# ---------------------------------------------------------------------------
def _productos_odoo(api: Odoo) -> dict[str, dict]:
    """ref interna -> {tmpl, variante, nombre, tipo}"""
    registros = api.buscar(
        "product.product",
        [["default_code", "!=", False], ["active", "in", [True, False]]],
        ["default_code", "product_tmpl_id", "name", "type", "is_storable"],
    )
    return {
        r["default_code"]: {
            "variante": r["id"],
            "plantilla": r["product_tmpl_id"][0],
            "nombre": r["name"],
            "tipo": r["type"],
            # En la 19 un almacenable es type='consu' con is_storable=True.
            "almacenable": bool(r.get("is_storable")),
        }
        for r in registros
    }


def _contactos_odoo(api: Odoo) -> dict[str, int]:
    registros = api.buscar("res.partner", [["ref", "!=", False]], ["ref"])
    return {r["ref"]: r["id"] for r in registros}


def _impuesto(api: Odoo, porcentaje: float, uso: str, servicio: bool, empresa: int) -> int:
    """Localiza el impuesto español por importe y tipo, nunca por id fijo.

    En la localización española hay dos impuestos con el mismo nombre para cada
    tipo («21% B» bienes y «21% S» servicios), así que además del importe hay
    que mirar la terminación del nombre.
    """
    candidatos = api.buscar(
        "account.tax",
        [
            ["amount", "=", porcentaje],
            ["type_tax_use", "=", uso],
            ["company_id", "=", empresa],
        ],
        ["name", "amount", "type_tax_use"],
    )
    if not candidatos:
        raise ErrorOdoo(
            f"no hay impuesto del {porcentaje:g} % de {uso} en la compañía. "
            "¿Está instalada la localización española (país España antes de Facturación)?"
        )
    if len(candidatos) == 1:
        return candidatos[0]["id"]
    sufijo = "s" if servicio else "b"
    for c in candidatos:
        nombre = (c["name"] or "").strip().lower()
        if nombre.endswith(f"% {sufijo}") or nombre.endswith(f"% {sufijo} "):
            return c["id"]
    # Alternativa: en inglés los bienes son «G» (goods).
    if not servicio:
        for c in candidatos:
            if (c["name"] or "").strip().lower().endswith("% g"):
                return c["id"]
    return candidatos[0]["id"]


def _marcar_movimientos(api: Odoo, producto_ids: list[int], fecha: str,
                        desde_id: int) -> None:
    """Pone fecha del pasado a los movimientos de stock recién creados."""
    movimientos = api.buscar(
        "stock.move",
        [["id", ">", desde_id], ["product_id", "in", producto_ids], ["state", "=", "done"]],
        ["date"],
    )
    for m in movimientos:
        api.escribir("stock.move", m["id"], {"date": fecha})


def _stock_inicial(api: Odoo, plan: historico.Plan, productos: dict[str, dict],
                   empresa: int) -> None:
    ubicacion = api.buscar("stock.location", [["usage", "=", "internal"]], ["name"], limite=1)
    if not ubicacion:
        raise ErrorOdoo("no hay ninguna ubicación interna: ¿está instalado Inventario?")
    ubicacion_id = ubicacion[0]["id"]
    ultimo_movimiento = api.llamar("stock.move", "search", [[]], {"order": "id desc", "limit": 1})

    for ref, cantidad in plan.stock_inicial.items():
        if cantidad <= 0:
            continue
        producto = productos.get(ref)
        if not producto or not producto["almacenable"]:
            continue
        dominio = [
            ["product_id", "=", producto["variante"]],
            ["location_id", "=", ubicacion_id],
        ]
        quant = api.buscar("stock.quant", dominio, ["quantity"], limite=1)
        if quant:
            api.escribir("stock.quant", quant[0]["id"], {"inventory_quantity": cantidad})
            api.ejecutar("stock.quant", "action_apply_inventory", [quant[0]["id"]])
        else:
            quant_id = api.crear("stock.quant", {
                "product_id": producto["variante"],
                "location_id": ubicacion_id,
                "inventory_quantity": cantidad,
            })
            api.ejecutar("stock.quant", "action_apply_inventory", [quant_id])

    _marcar_movimientos(api, [p["variante"] for p in productos.values()],
                        "2026-07-30 09:00:00",
                        ultimo_movimiento[0] if ultimo_movimiento else 0)


def _reglas_reabastecimiento(api: Odoo, m) -> None:
    """Crea las reglas de mínimo/máximo del catálogo (las que usa el planificador).

    Sin ellas, la pantalla de Abastecimiento no propone nada y el ejercicio de la
    S19 no se puede hacer. Se crean una sola vez: si ya existe la regla para ese
    producto y ubicación, no se duplica.
    """
    ubicacion = api.buscar("stock.location", [["usage", "=", "internal"]], ["name"], limite=1)
    if not ubicacion:
        return
    ubicacion_id = ubicacion[0]["id"]
    for p in m.productos:
        if not p.get("minimo") or p["tipo"] == "servicio":
            continue
        producto = api.buscar("product.product", [["default_code", "=", p["ref"]]],
                              ["id"], limite=1)
        if not producto:
            continue
        existente = api.buscar_ids("stock.warehouse.orderpoint", [
            ["product_id", "=", producto[0]["id"]],
            ["location_id", "=", ubicacion_id],
        ], limite=1)
        if existente:
            continue
        api.crear("stock.warehouse.orderpoint", {
            "product_id": producto[0]["id"],
            "location_id": ubicacion_id,
            "product_min_qty": p["minimo"],
            "product_max_qty": p.get("maximo") or (p["minimo"] * 3),
            # "manual": la regla solo *propone*. Con "auto", el planificador
            # diario crea los borradores de compra por su cuenta y el alumno se
            # encuentra pedidos que no ha hecho. En el aula interesa ver la
            # propuesta y decidir.
            "trigger": "manual",
        })


def _proveedores_producto(api: Odoo, m, productos: dict, contactos: dict,
                          verboso: bool = True) -> int:
    """Crea la ficha de proveedor (product.supplierinfo) de cada producto.

    Sin ella Odoo no sabe a quién comprar: el producto sale como «sin
    proveedor» en Inventario y la regla de reabastecimiento no propone nada.
    Es idempotente: si la ficha ya existe para ese producto y proveedor, no se
    toca.
    """
    plazo = {p["clave"]: 5 + (i % 5) for i, p in enumerate(m.proveedores)}
    creadas = 0
    for p in m.productos:
        clave = p.get("proveedor")
        if not clave or not p.get("compra", True) or p["tipo"] == "servicio":
            continue
        socio = contactos.get(clave)
        plantilla = productos.get(p["ref"], {}).get("plantilla")
        if not socio or not plantilla:
            continue
        ya = api.buscar_ids("product.supplierinfo",
                            [["product_tmpl_id", "=", plantilla], ["partner_id", "=", socio]],
                            limite=1)
        if ya:
            continue
        api.crear("product.supplierinfo", {
            "product_tmpl_id": plantilla,
            "partner_id": socio,
            "price": p["coste"],
            "delay": plazo.get(clave, 7),
            "min_qty": 1,
        })
        creadas += 1
    if verboso:
        print(f"  proveedor asignado a {creadas} productos")
    return creadas


def _validar_albaran(api: Odoo, picking_id: int, fecha: str) -> None:
    """Cantidades completas, validar y volver a poner la fecha histórica."""
    movimientos = api.buscar("stock.move", [["picking_id", "=", picking_id]],
                             ["product_uom_qty"])
    for m in movimientos:
        api.escribir("stock.move", m["id"], {"quantity": m["product_uom_qty"], "picked": True})
    # skip_sms: la 19 pide confirmar las entregas por SMS al cliente si el
    # contacto tiene teléfono. En el aula no hay pasarela de SMS: se salta.
    resultado = api.ejecutar("stock.picking", "button_validate", [picking_id],
                             contexto={"skip_sms": True})
    if isinstance(resultado, dict) and resultado.get("res_model"):
        raise ErrorOdoo(f"la validación del albarán {picking_id} pide el asistente "
                        f"{resultado['res_model']} (¿cantidades incompletas?)")
    api.escribir("stock.picking", picking_id, {"date_done": fecha})
    movimientos = api.buscar("stock.move", [["picking_id", "=", picking_id]], ["id"])
    ids = [m["id"] for m in movimientos]
    if ids:
        api.escribir("stock.move", ids, {"date": fecha})


def _cobrar(api: Odoo, factura_id: int, fecha: str, importe: float | None = None) -> None:
    contexto = {"active_model": "account.move", "active_ids": [factura_id],
                "active_id": factura_id}
    valores = {"payment_date": fecha}
    if importe is not None:
        valores["amount"] = importe
    asistente = api.llamar(
        "account.payment.register", "create", [valores], {"context": contexto}
    )
    if isinstance(asistente, list):
        asistente = asistente[0]
    api.ejecutar("account.payment.register", "action_create_payments", [asistente],
                 contexto=contexto)


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def cargar(api: Odoo, e: catalogo.Empresa, m: maestros.Maestros, plan: historico.Plan,
           verboso: bool = True) -> dict:
    empresa = api.buscar("res.company", [], ["name"], limite=1)[0]
    productos = _productos_odoo(api)
    contactos = _contactos_odoo(api)

    # Los productos de alta manual (S17) no vienen en los CSV: si el alumno los
    # ha creado, también hay que ponerles el IVA.
    manuales = (e.catalogo.get("altas_manuales") or {}).get("productos", [])
    for p in manuales:
        categoria = e.categoria(p["categoria"])
        m.productos.append({
            "ref": p["ref"],
            "nombre": p["nombre"],
            "categoria": p["categoria"],
            "categoria_nombre": categoria["nombre"],
            "iva_venta": p.get("iva_venta", categoria.get("iva_venta")),
            "iva_compra": p.get("iva_compra", categoria.get("iva_compra")),
            "pvp": p["pvp"],
            "coste": p["coste"],
            "tipo": p.get("tipo", "almacenable"),
            "proveedor": p.get("proveedor"),
            "minimo": p.get("minimo"),
            "maximo": p.get("maximo"),
            "compra": p.get("compra", p.get("tipo", "almacenable") != "servicio"),
            "venta": True,
            "barcode": "",
        })

    faltan = [p["ref"] for p in m.productos if p["ref"] not in productos]
    refs_manuales = {p["ref"] for p in manuales}
    faltan_obligatorios = [r for r in faltan if r not in refs_manuales]
    if faltan_obligatorios:
        raise ErrorOdoo(
            "faltan productos en Odoo: " + ", ".join(faltan_obligatorios[:10]) +
            ("…" if len(faltan_obligatorios) > 10 else "") +
            "\nImporta los CSV de maestros en el orden que indica LEEME.md."
        )
    if faltan:
        print("  aviso: no están los productos de alta manual (" +
              ", ".join(faltan) + "); se cargan igualmente el resto.")
    faltan = [c["ref"] for c in m.clientes if c["ref"] not in contactos]
    if faltan:
        raise ErrorOdoo("faltan clientes en Odoo: " + ", ".join(faltan[:10]))
    faltan = [p["clave"] for p in m.proveedores if p["clave"] not in contactos]
    if faltan:
        raise ErrorOdoo("faltan proveedores en Odoo: " + ", ".join(faltan))

    # ---- 1. Impuestos de los productos ----------------------------------
    if verboso:
        print("Asignando impuestos a los productos…")
    for p in m.productos:
        if p["ref"] not in productos:
            continue
        venta = p["iva_venta"]
        compra = p["iva_compra"]
        valores = {}
        if venta is not None:
            valores["taxes_id"] = [(6, 0, [_impuesto(api, venta, "sale", p["tipo"] == "servicio",
                                                     empresa["id"])])]
        if compra is not None and p["compra"]:
            valores["supplier_taxes_id"] = [(6, 0, [_impuesto(api, compra, "purchase",
                                                              p["tipo"] == "servicio",
                                                              empresa["id"])])]
        if valores:
            api.escribir("product.template", productos[p["ref"]]["plantilla"], valores)

    # ---- 1b. Ficha de proveedor de cada producto -------------------------
    if verboso:
        print("Asignando proveedor a los productos…")
    _proveedores_producto(api, m, productos, contactos, verboso)

    # ---- 2. Stock inicial ------------------------------------------------
    if verboso:
        print("Fijando el stock inicial al 30/07/2026…")
    _stock_inicial(api, plan, productos, empresa["id"])
    _reglas_reabastecimiento(api, m)

    # ---- 3. Compras ------------------------------------------------------
    if verboso:
        print(f"Creando {len(plan.compras)} compras…")
    for i, compra in enumerate(plan.compras, start=1):
        lineas = [
            (0, 0, {
                "product_id": productos[l.ref]["variante"],
                "product_qty": l.cantidad,
                "price_unit": l.precio,
                "name": productos[l.ref]["nombre"],
                "date_planned": str(compra.recepcion),
            })
            for l in compra.lineas
        ]
        pedido = api.crear("purchase.order", {
            "partner_id": contactos[compra.proveedor],
            "date_order": f"{compra.fecha} 09:00:00",
            "order_line": lineas,
        })
        api.ejecutar("purchase.order", "button_confirm", [pedido])
        api.escribir("purchase.order", pedido, {"date_order": f"{compra.fecha} 09:00:00"})
        albaranes = api.buscar_ids("stock.picking", [["origin", "=", api.leer("purchase.order", [pedido], ["name"])[0]["name"]]])
        for albaran in albaranes:
            _validar_albaran(api, albaran, f"{compra.recepcion} 10:00:00")
        if compra.factura:
            accion = api.ejecutar("purchase.order", "action_create_invoice", [pedido])
            facturas = api.buscar_ids("account.move", [["invoice_origin", "=", api.leer("purchase.order", [pedido], ["name"])[0]["name"]]])
            if facturas:
                factura = facturas[0]
                api.escribir("account.move", factura, {"invoice_date": str(compra.fecha_factura)})
                api.ejecutar("account.move", "action_post", [factura])
                if compra.pago in ("total", "parcial"):
                    total = api.leer("account.move", [factura], ["amount_total"])[0]["amount_total"]
                    importe = total if compra.pago == "total" else round(total * 0.5, 2)
                    _cobrar(api, factura, f"{compra.fecha_pago} 12:00:00", importe)
        if verboso and i % 5 == 0:
            print(f"  … {i}/{len(plan.compras)}")

    # ---- 4. Ventas -------------------------------------------------------
    if verboso:
        print(f"Creando {len(plan.ventas)} ventas…")
    tarifas = {t["nombre"]: None for t in m.tarifas}
    tarifa_odoo = {}
    for nombre in tarifas:
        encontradas = api.buscar_ids("product.pricelist", [["name", "=", nombre]], limite=1)
        if encontradas:
            tarifa_odoo[nombre] = encontradas[0]
    nombre_tarifa = {t["clave"]: t["nombre"] for t in m.tarifas}

    # ---- 3b. Reglas de tarifa -------------------------------------------
    # La pestaña «Reglas» de una lista de precios es una lista incrustada: no
    # tiene botón «Importar», así que el CSV de reglas no se puede cargar desde
    # la interfaz. Las crea este script (una regla global por lista) y
    # verificar.py comprueba que están.
    for tarifa in m.tarifas:
        if not tarifa.get("descuento"):
            continue
        lista = tarifa_odoo.get(tarifa["nombre"])
        if not lista:
            continue
        ya = api.buscar_ids("product.pricelist.item",
                            [["pricelist_id", "=", lista], ["applied_on", "=", "3_global"]],
                            limite=1)
        if not ya:
            api.crear("product.pricelist.item", {
                "pricelist_id": lista,
                "applied_on": "3_global",
                "compute_price": "percentage",
                "percent_price": tarifa["descuento"],
                "min_quantity": 0,
            })

    for i, venta in enumerate(plan.ventas, start=1):
        cliente = next(c for c in m.clientes if c["clave"] == venta.cliente)
        valores = {
            "partner_id": contactos[cliente["ref"]],
            "date_order": f"{venta.fecha} 09:00:00",
            "order_line": [
                (0, 0, {
                    "product_id": productos[l.ref]["variante"],
                    "product_uom_qty": l.cantidad,
                    "price_unit": l.precio,
                })
                for l in venta.lineas
            ],
        }
        if cliente.get("tarifa") and tarifa_odoo.get(nombre_tarifa.get(cliente["tarifa"])):
            valores["pricelist_id"] = tarifa_odoo[nombre_tarifa[cliente["tarifa"]]]
        pedido = api.crear("sale.order", valores)
        api.ejecutar("sale.order", "action_confirm", [pedido])
        api.escribir("sale.order", pedido, {"date_order": f"{venta.fecha} 09:00:00"})

        albaranes = api.buscar_ids("stock.picking", [["sale_id", "=", pedido]])
        for albaran in albaranes:
            _validar_albaran(api, albaran, f"{venta.entrega} 10:00:00")

        if venta.factura:
            contexto = {"active_model": "sale.order", "active_ids": [pedido], "active_id": pedido}
            asistente = api.llamar(
                "sale.advance.payment.inv", "create",
                [{"advance_payment_method": "delivered"}], {"context": contexto},
            )
            if isinstance(asistente, list):
                asistente = asistente[0]
            api.ejecutar("sale.advance.payment.inv", "create_invoices", [asistente],
                         contexto=contexto)
            facturas = api.buscar_ids("account.move", [["invoice_origin", "=",
                                                        api.leer("sale.order", [pedido], ["name"])[0]["name"]]])
            if facturas:
                factura = facturas[0]
                api.escribir("account.move", factura, {"invoice_date": str(venta.fecha_factura)})
                api.ejecutar("account.move", "action_post", [factura])
                if venta.cobro in ("total", "parcial"):
                    total = api.leer("account.move", [factura], ["amount_total"])[0]["amount_total"]
                    importe = total if venta.cobro == "total" else round(total * 0.5, 2)
                    _cobrar(api, factura, f"{venta.fecha_cobro} 12:00:00", importe)
        if verboso and i % 10 == 0:
            print(f"  … {i}/{len(plan.ventas)}")

    return {"ventas": len(plan.ventas), "compras": len(plan.compras)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--empresa", required=True)
    p.add_argument("--alumno", required=True, type=int)
    p.add_argument("--seco", action="store_true", help="solo enseña el plan, no escribe")
    p.add_argument("--forzar", action="store_true", help="carga aunque ya haya histórico")
    p.add_argument("--solo-proveedores", action="store_true",
                   help="repara las fichas de proveedor de los productos y sale")
    p.add_argument("--url", default=os.environ.get("ODOO_URL", "http://odoo:8069"))
    p.add_argument("--bd", default=os.environ.get("ODOO_BD", "empresa"))
    p.add_argument("--usuario", default=os.environ.get("ODOO_USUARIO", "admin"))
    p.add_argument("--clave", default=os.environ.get("ODOO_CLAVE", "admin"))
    p.add_argument("--transporte", default=os.environ.get("ODOO_API", "xmlrpc"),
                   choices=["xmlrpc", "json2"])
    args = p.parse_args(argv)

    e = catalogo.cargar(args.empresa)
    v = Variante(args.empresa, args.alumno)
    m = maestros.construir(e, v)
    plan = historico.planificar(e, m, args.alumno)

    print(f"Empresa: {m.empresa['nombre']}")
    print(f"Plan:    {plan.resumen()}")

    if args.seco:
        for c in plan.compras[:5]:
            print(f"  compra  {c.fecha} {c.proveedor} {len(c.lineas)} líneas pago={c.pago}")
        for vv in plan.ventas[:5]:
            print(f"  venta   {vv.fecha} {vv.cliente} {len(vv.lineas)} líneas cobro={vv.cobro}")
        print("  stock inicial:", {k: v_ for k, v_ in list(plan.stock_inicial.items())[:6]}, "…")
        print("Modo seco: no se ha escrito nada en la base de datos.")
        return 0

    api = Odoo(args.url, args.bd, args.usuario, args.clave, args.transporte)
    try:
        api.conectar()
    except ErrorOdoo as exc:
        print(f"No se puede conectar con Odoo en {args.url}: {exc}", file=sys.stderr)
        return 1
    print(f"Conectado a {args.url} (base {args.bd}, {api.version()})")

    if args.solo_proveedores:
        # Reparación: asigna el proveedor del catálogo a los productos que no lo
        # tengan. No toca nada más. Sirve cuando en Inventario aparecen
        # productos «sin proveedor» y la regla de reabastecimiento no propone
        # compras.
        try:
            productos = _productos_odoo(api)
            contactos = _contactos_odoo(api)
            creadas = _proveedores_producto(api, m, productos, contactos)
        except ErrorOdoo as exc:
            print(f"\nERROR: {exc}", file=sys.stderr)
            return 1
        print(f"\nFichas de proveedor creadas: {creadas}.")
        return 0

    marca = api.buscar("ir.config_parameter", [["key", "=", CLAVE_MARCA]], ["value"], limite=1)
    if marca and not args.forzar:
        print("\nAVISO: esta base ya tiene un histórico cargado por este script:")
        print(" ", marca[0]["value"])
        print("Si quieres volver a cargarlo, restaura una copia de seguridad o usa --forzar.")
        return 2

    try:
        resultado = cargar(api, e, m, plan)
    except ErrorOdoo as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1

    api.crear("ir.config_parameter", {
        "key": CLAVE_MARCA,
        "value": json.dumps({
            "empresa": args.empresa, "alumno": args.alumno,
            "fecha": dt.datetime.now().isoformat(timespec="seconds"),
            **resultado,
        }, ensure_ascii=False),
    })
    print(f"\nHistórico cargado: {resultado['ventas']} ventas y {resultado['compras']} compras.")
    print("Ejecuta ahora verificar.py para comprobar que todo cuadra.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
