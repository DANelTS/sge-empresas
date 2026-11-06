#!/usr/bin/env python3
"""verificar.py — comprueba que tu base de datos está como debe estar.

No arregla nada: mira y te dice qué falta o qué está mal, con la pista para
arreglarlo. Se ejecuta después de importar los maestros y de cargar el
histórico, y también sirve para comprobar antes de entregar.

    docker compose run --rm herramientas verificar.py --empresa cerveceria --alumno 07

Devuelve 0 si todo está en verde y 1 si algo falla (útil para automatizar).
"""
from __future__ import annotations

import argparse
import os
import sys

from odoo_api import ErrorOdoo, Odoo
from sge import catalogo, maestros
from sge.variante import Variante

VERDE = "\033[32m✔\033[0m"
ROJO = "\033[31m✖\033[0m"
AMBAR = "\033[33m•\033[0m"


class Informe:
    def __init__(self):
        self.fallos = 0
        self.avisos = 0

    def bien(self, texto: str, detalle: str = "") -> None:
        print(f"  {VERDE} {texto}" + (f" — {detalle}" if detalle else ""))

    def mal(self, texto: str, pista: str = "") -> None:
        self.fallos += 1
        print(f"  {ROJO} {texto}")
        if pista:
            print(f"      → {pista}")

    def ojo(self, texto: str, pista: str = "") -> None:
        self.avisos += 1
        print(f"  {AMBAR} {texto}" + (f"\n      → {pista}" if pista else ""))

    def titulo(self, texto: str) -> None:
        print(f"\n{texto}")


def comprobar_modulos(api: Odoo, inf: Informe) -> None:
    inf.titulo("Aplicaciones instaladas")
    necesarias = ["crm", "sale_management", "purchase", "stock", "account", "l10n_es"]
    estados = api.buscar("ir.module.module", [["name", "in", necesarias]], ["name", "state"])
    mapa = {m["name"]: m["state"] for m in estados}
    for modulo in necesarias:
        estado = mapa.get(modulo)
        if estado == "installed":
            inf.bien(modulo)
        else:
            inf.mal(f"{modulo} no está instalado", f"Aplicaciones → busca «{modulo}» → Instalar")


def comprobar_compania(api: Odoo, inf: Informe, m: maestros.Maestros) -> None:
    inf.titulo("Compañía")
    empresa = api.buscar("res.company", [], ["name", "currency_id", "chart_template", "vat"])[0]
    esperado = m.empresa
    if empresa["name"] == esperado["nombre"]:
        inf.bien("nombre", empresa["name"])
    else:
        inf.mal(f"el nombre es «{empresa['name']}» y debería ser «{esperado['nombre']}»",
                "Ajustes → Compañías")
    if empresa["currency_id"] and empresa["currency_id"][1] == "EUR":
        inf.bien("moneda EUR")
    else:
        inf.mal(f"la moneda es {empresa['currency_id'][1] if empresa['currency_id'] else 'ninguna'}",
                "Se instaló Facturación antes de poner el país: hay que rehacer la base (guía S16)")
    if (empresa.get("chart_template") or "").startswith("es"):
        inf.bien("plan contable español", empresa["chart_template"])
    else:
        inf.mal(f"el plan contable es «{empresa.get('chart_template')}»",
                "Falta la localización española: país España + instalar Facturación")
    vat = (empresa.get("vat") or "").replace("ES", "", 1)
    if vat == esperado["cif"]:
        inf.bien("NIF de la compañía", vat)
    else:
        inf.mal(f"el NIF es «{vat or 'vacío'}» y debería ser «{esperado['cif']}»",
                "Copia el NIF desde datos-empresa.md (sin espacios)")


def comprobar_impuestos(api: Odoo, inf: Informe, m: maestros.Maestros) -> None:
    inf.titulo("Impuestos españoles")
    empresa = api.buscar("res.company", [], ["id"])[0]["id"]
    impuestos = api.buscar("account.tax",
                           [["company_id", "=", empresa], ["type_tax_use", "=", "sale"]],
                           ["name", "amount"])
    for porcentaje in (21, 10, 4):
        encontrados = [t for t in impuestos if abs(t["amount"] - porcentaje) < 0.01]
        if encontrados:
            inf.bien(f"existe el {porcentaje} % de venta",
                     ", ".join(t["name"] for t in encontrados[:4]))
        else:
            inf.mal(f"no hay ningún impuesto de venta del {porcentaje} %",
                    "Facturación → Configuración → Contabilidad → Impuestos")


def comprobar_maestros(api: Odoo, inf: Informe, m: maestros.Maestros, e) -> None:
    inf.titulo("Datos maestros")
    productos = api.buscar("product.product", [["default_code", "!=", False]],
                           ["default_code", "taxes_id", "supplier_taxes_id", "type"])
    por_ref = {p["default_code"]: p for p in productos}
    faltan = [p["ref"] for p in m.productos if p["ref"] not in por_ref]
    if faltan:
        inf.mal(f"faltan {len(faltan)} productos: {', '.join(faltan[:8])}",
                "Importa 4-productos.csv (Ventas → Productos → Importar)")
    else:
        inf.bien(f"están los {len(m.productos)} productos")

    # Impuestos por producto
    malos = []
    for p in m.productos:
        odoo = por_ref.get(p["ref"])
        if not odoo:
            continue
        if not odoo["taxes_id"]:
            malos.append(f"{p['ref']} sin IVA de venta")
            continue
        if p["compra"] and not odoo["supplier_taxes_id"]:
            malos.append(f"{p['ref']} sin IVA de compra")
    if malos:
        inf.mal(f"{len(malos)} productos sin impuesto: {', '.join(malos[:6])}",
                "Ejecuta cargar_historico.py: es quien asigna los impuestos")
    else:
        inf.bien("todos los productos tienen IVA de venta y de compra")

    contactos = api.buscar("res.partner", [["ref", "!=", False]], ["ref", "vat", "property_payment_term_id"])
    refs = {c["ref"] for c in contactos}
    faltan_cli = [c["ref"] for c in m.clientes if c["ref"] not in refs]
    faltan_prv = [p["clave"] for p in m.proveedores if p["clave"] not in refs]
    if faltan_cli:
        inf.mal(f"faltan {len(faltan_cli)} clientes: {', '.join(faltan_cli[:8])}",
                "Importa 6-clientes.csv")
    else:
        inf.bien(f"están los {len(m.clientes)} clientes")
    if faltan_prv:
        inf.mal(f"faltan {len(faltan_prv)} proveedores: {', '.join(faltan_prv[:8])}",
                "Importa 5-proveedores.csv")
    else:
        inf.bien(f"están los {len(m.proveedores)} proveedores")

    # Altas manuales de la S17: no vienen en los CSV, las teclea el alumno.
    manuales = (e.catalogo.get("altas_manuales") or {}).get("productos", [])
    if manuales:
        sin_alta = [p["ref"] for p in manuales if p["ref"] not in por_ref]
        if sin_alta:
            inf.ojo(f"no están los productos de alta manual: {', '.join(sin_alta)}",
                    "Bandeja s17-altas.md: se crean a mano con el formulario")
        else:
            inf.bien(f"están los {len(manuales)} productos de alta manual")


def comprobar_tarifas(api: Odoo, inf: Informe, m: maestros.Maestros) -> None:
    """Listas de precios con su regla, y el ajuste que las hace visibles."""
    inf.titulo("Listas de precios")
    con_descuento = [t for t in m.tarifas if t.get("descuento")]
    if not con_descuento:
        inf.bien("esta empresa no usa tarifas")
        return

    reglas = api.buscar("product.pricelist.item",
                        [["applied_on", "=", "3_global"]],
                        ["pricelist_id", "percent_price"])
    por_lista = {}
    for r in reglas:
        if r["pricelist_id"]:
            por_lista[r["pricelist_id"][0]] = r["percent_price"]

    for t in con_descuento:
        ids = api.buscar_ids("product.pricelist", [["name", "=", t["nombre"]]], limite=1)
        if not ids:
            inf.mal(f"falta la lista «{t['nombre']}»",
                    "impórtala con maestros/2-tarifas.csv (Ventas → Productos → Listas de precios)")
            continue
        if ids[0] not in por_lista:
            inf.mal(f"la lista «{t['nombre']}» no tiene regla de descuento",
                    "la crea cargar_historico.py; si no la ves, vuelve a ejecutarlo")
            continue
        if abs((por_lista[ids[0]] or 0) - t["descuento"]) > 0.01:
            inf.mal(f"«{t['nombre']}» descuenta {por_lista[ids[0]]} % y debería {t['descuento']} %",
                    "revisa la regla en la pestaña Reglas de la lista")
        else:
            inf.bien(f"«{t['nombre']}» con regla del {t['descuento']} %")

    # El ajuste de listas de precios: si está apagado, el menú no aparece y la
    # columna de tarifa del cliente no se puede importar.
    # El ajuste no añade usuarios al grupo: lo hace heredar del grupo «Usuario
    # interno», que es el que tiene todo el mundo. Por eso no basta con mirar
    # quién está en el grupo.
    xmlid = api.buscar("ir.model.data",
                       [["module", "=", "product"], ["name", "=", "group_product_pricelist"]],
                       ["res_id"], limite=1)
    interno = api.buscar("ir.model.data",
                         [["module", "=", "base"], ["name", "=", "group_user"]],
                         ["res_id"], limite=1)
    activo = False
    if xmlid and interno:
        heredados = api.buscar("res.groups", [["id", "=", interno[0]["res_id"]]],
                               ["implied_ids"], limite=1)
        activo = xmlid[0]["res_id"] in (heredados[0]["implied_ids"] if heredados else [])
        if not activo:
            grupo = api.buscar("res.groups", [["id", "=", xmlid[0]["res_id"]]],
                               ["user_ids"], limite=1)
            activo = bool(grupo and grupo[0]["user_ids"])
    if not activo:
        inf.ojo("las listas de precios están desactivadas en Ajustes",
                "Ajustes → Ventas → Precios → Listas de precios")


def comprobar_stock(api: Odoo, inf: Informe) -> None:
    inf.titulo("Inventario")
    quants = api.buscar("stock.quant", [["location_id.usage", "=", "internal"]],
                        ["product_id", "quantity"])
    negativos = [q["product_id"][1] for q in quants if q["quantity"] < 0]
    if negativos:
        inf.mal(f"hay {len(negativos)} productos con stock negativo: {', '.join(negativos[:5])}",
                "Revisa las entregas: se ha vendido más de lo que había")
    else:
        inf.bien("ningún producto con stock negativo")
    reglas = api.buscar_ids("stock.warehouse.orderpoint", [["active", "=", True]])
    if reglas:
        inf.bien(f"{len(reglas)} reglas de reabastecimiento (mínimo/máximo)")
    else:
        inf.ojo("no hay reglas de reabastecimiento",
                "Las crea cargar_historico.py; sin ellas el planificador no propone compras (S19)")

    con_stock = sum(1 for q in quants if q["quantity"] > 0)
    if con_stock:
        inf.bien(f"{con_stock} productos con existencias")
    else:
        inf.ojo("no hay existencias en el almacén",
                "Falta cargar el stock inicial: cargar_historico.py")


def comprobar_historico(api: Odoo, inf: Informe) -> None:
    inf.titulo("Histórico")
    marca = api.buscar("ir.config_parameter", [["key", "=", "sge.historico"]], ["value"], limite=1)
    if not marca:
        inf.ojo("el histórico todavía no está cargado",
                "docker compose run --rm herramientas cargar_historico.py --empresa ... --alumno ...")
        return
    facturas = api.buscar("account.move",
                          [["move_type", "=", "out_invoice"], ["state", "=", "posted"]],
                          ["payment_state", "amount_total", "amount_residual", "invoice_date"])
    pedidos = api.buscar_ids("sale.order", [["state", "not in", ["draft", "cancel"]]])
    compras = api.buscar_ids("purchase.order", [["state", "not in", ["draft", "cancel"]]])
    if facturas:
        total = sum(f["amount_total"] for f in facturas)
        pendiente = sum(f["amount_residual"] for f in facturas)
        inf.bien(f"{len(pedidos)} pedidos de venta confirmados")
        inf.bien(f"{len(compras)} pedidos de compra confirmados")
        inf.bien(f"{len(facturas)} facturas emitidas", f"{total:,.2f} €".replace(",", "."))
        vencidas = [f for f in facturas if f["payment_state"] in ("not_paid", "partial")]
        if vencidas:
            inf.bien(f"{len(vencidas)} facturas pendientes de cobro",
                     f"{pendiente:,.2f} €".replace(",", "."))
        else:
            inf.ojo("no hay ninguna factura pendiente de cobro; el histórico debería tener morosos")
        fechas = [f["invoice_date"] for f in facturas if f["invoice_date"]]
        if fechas and min(fechas) < "2026-08-01":
            inf.ojo(f"hay facturas anteriores a agosto de 2026: {min(fechas)}")
    else:
        inf.mal("la marca de histórico existe pero no hay facturas de venta",
                "Restaura una copia y vuelve a cargar")


def comprobar_usuarios(api: Odoo, inf: Informe) -> None:
    inf.titulo("Usuarios")
    usuarios = api.buscar("res.users", [["share", "=", False], ["active", "=", True]],
                          ["name", "login", "group_ids"])
    if len(usuarios) >= 2:
        inf.bien(f"{len(usuarios)} usuarios internos", ", ".join(u["login"] for u in usuarios[:5]))
    else:
        inf.ojo("solo hay un usuario interno",
                "Ajustes → Usuarios → Nuevo: crea «Comercial» y «Almacén» (guía S16)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--empresa", required=True)
    p.add_argument("--alumno", required=True, type=int)
    p.add_argument("--url", default=os.environ.get("ODOO_URL", "http://odoo:8069"))
    p.add_argument("--bd", default=os.environ.get("ODOO_BD", "empresa"))
    p.add_argument("--usuario", default=os.environ.get("ODOO_USUARIO", "admin"))
    p.add_argument("--clave", default=os.environ.get("ODOO_CLAVE", "admin"))
    p.add_argument("--transporte", default=os.environ.get("ODOO_API", "xmlrpc"))
    args = p.parse_args(argv)

    e = catalogo.cargar(args.empresa)
    v = Variante(args.empresa, args.alumno)
    m = maestros.construir(e, v)

    api = Odoo(args.url, args.bd, args.usuario, args.clave, args.transporte)
    try:
        api.conectar()
    except ErrorOdoo as exc:
        print(f"No se puede conectar con Odoo en {args.url}: {exc}", file=sys.stderr)
        return 1

    print(f"Verificando {m.empresa['nombre']} en la base «{args.bd}»")
    inf = Informe()
    try:
        comprobar_modulos(api, inf)
        comprobar_compania(api, inf, m)
        comprobar_impuestos(api, inf, m)
        comprobar_maestros(api, inf, m, e)
        comprobar_tarifas(api, inf, m)
        comprobar_stock(api, inf)
        comprobar_historico(api, inf)
        comprobar_usuarios(api, inf)
    except ErrorOdoo as exc:
        print(f"\nERROR consultando Odoo: {exc}", file=sys.stderr)
        return 1

    print()
    if inf.fallos:
        print(f"Resultado: {inf.fallos} comprobaciones en rojo, {inf.avisos} avisos.")
        return 1
    if inf.avisos:
        print(f"Resultado: todo correcto, con {inf.avisos} avisos.")
        return 0
    print("Resultado: todo en verde.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
