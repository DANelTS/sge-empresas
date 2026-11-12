#!/usr/bin/env python3
"""configurar_compania.py — deja la compañía con los datos de la variante.

En clase, la compañía la configura el alumno a mano (guía S16): es parte del
ejercicio. Este script existe para el **profesor**: montar la base de referencia
de una variante sin tocar la interfaz, para las pruebas automáticas y para el
resolvedor del repositorio privado.

    docker compose run --rm herramientas configurar_compania.py --empresa cerveceria --alumno 07

Es idempotente: si se ejecuta dos veces, deja los mismos valores.
"""
from __future__ import annotations

import argparse
import os
import sys

from odoo_api import ErrorOdoo, Odoo
from sge import catalogo, maestros
from sge.provincias import odoo as provincia_odoo
from sge.variante import Variante


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
    m = maestros.construir(e, Variante(args.empresa, args.alumno))
    d = m.empresa

    api = Odoo(args.url, args.bd, args.usuario, args.clave, args.transporte)
    try:
        api.conectar()
    except ErrorOdoo as exc:
        print(f"No se puede conectar con Odoo en {args.url}: {exc}", file=sys.stderr)
        return 1

    empresa = api.buscar("res.company", [], ["id", "name", "partner_id"], limite=1)[0]
    pais = api.buscar("res.country", [["code", "=", "ES"]], ["id"], limite=1)[0]["id"]
    provincia = api.buscar("res.country.state",
                           [["country_id", "=", pais], ["name", "=", provincia_odoo(d["provincia"])]],
                           ["id"], limite=1)
    if not provincia:
        print(f"No encuentro la provincia {d['provincia']!r} en Odoo.", file=sys.stderr)
        return 1

    valores = {
        "name": d["nombre"],
        "vat": d["cif"],
        "street": d["domicilio"],
        "zip": d["cp"],
        "city": d["poblacion"],
        "state_id": provincia[0]["id"],
        "country_id": pais,
        "phone": d["telefono"],
        "email": d["email"],
        "website": d["web"],
    }
    api.escribir("res.company", empresa["id"], valores)

    # Cuenta bancaria de la empresa (para los datos de pago de las facturas).
    cuenta = api.buscar("res.partner.bank",
                        [["partner_id", "=", empresa["partner_id"][0]]], ["acc_number"], limite=1)
    # allow_out_payment: en la 19 una cuenta "no verificada" bloquea la
    # confirmación de facturas de cliente. Sin esto, la primera factura de venta
    # se queda en borrador con un aviso de cuenta bancaria no verificada.
    valores_cuenta = {"acc_number": d["iban"], "allow_out_payment": True}
    if cuenta:
        api.escribir("res.partner.bank", cuenta[0]["id"], valores_cuenta)
    else:
        valores_cuenta.update({
            "partner_id": empresa["partner_id"][0],
            "company_id": empresa["id"],
        })
        api.crear("res.partner.bank", valores_cuenta)

    # Listas de precios: en la 19 el ajuste viene DESACTIVADO y, sin él, el menú
    # «Ventas → Productos → Listas de precios» no existe para el usuario normal ni
    # el importador reconoce la columna de tarifa del cliente. Se activa con el
    # mismo interruptor de Ajustes → Ventas → Precios.
    # Se escribe la relación directamente: el asistente de ajustes puede no
    # hacer nada si el servidor tiene cacheado el valor anterior, y entonces
    # devuelve éxito sin haber activado nada.
    interno = api.buscar("ir.model.data", [["module", "=", "base"], ["name", "=", "group_user"]],
                         ["res_id"], limite=1)
    grupo = api.buscar("ir.model.data",
                       [["module", "=", "product"], ["name", "=", "group_product_pricelist"]],
                       ["res_id"], limite=1)
    if interno and grupo:
        api.escribir("res.groups", [interno[0]["res_id"]],
                     {"implied_ids": [(4, grupo[0]["res_id"])]})

    print(f"Compañía configurada: {d['nombre']} — NIF {d['cif']} — {d['cp']} {d['poblacion']}")
    print(f"Cuenta bancaria: {d['iban']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
