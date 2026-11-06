#!/usr/bin/env python3
"""importar_maestros.py — importa los CSV de la variante con el asistente de Odoo.

Hace exactamente lo mismo que el alumno a mano (crear un registro de
`base_import.import`, mapear las columnas y ejecutar), pero de una vez y en el
orden correcto. Sirve para dos cosas:

- montar la base de referencia del profesor sin repetir veinte clics;
- probar de verdad que los CSV se importan como deben (si el alumno lo hace a
  mano y falla, aquí falla igual).

Uso:

    docker compose run --rm herramientas importar_maestros.py --empresa cerveceria --alumno 07
    docker compose run --rm herramientas importar_maestros.py --empresa cerveceria --alumno 07 --seco

`--seco` hace una importación de prueba: Odoo lo procesa todo y luego lo deshace.
"""
from __future__ import annotations

import argparse
import os
import sys

from odoo_api import ErrorOdoo, Odoo
from sge import catalogo, maestros
from sge.variante import Variante

RAIZ = catalogo.RAIZ

# Orden obligatorio: los productos necesitan la categoría y los clientes la tarifa.
FICHEROS = [
    ("product.category", "1-categorias-producto.csv"),
    ("product.pricelist", "2-tarifas.csv"),
    ("product.template", "4-productos.csv"),
    ("res.partner", "5-proveedores.csv"),
    ("res.partner", "6-clientes.csv"),
]

OPCIONES = {
    "has_headers": True,
    "advanced": True,
    "keep_matches": False,
    "encoding": "utf-8",
    "separator": ",",
    "quoting": '"',
    "tracking_disable": True,
    "name_create_enabled_fields": {},
}


def importar_fichero(api: Odoo, modelo: str, ruta, seco: bool) -> tuple[int, list]:
    texto = ruta.read_text(encoding="utf-8")
    cabecera = texto.splitlines()[0].split(",")

    # En la 19 el campo binario espera el texto tal cual (no en base64).
    importacion = api.crear("base_import.import", {
        "res_model": modelo,
        "file": texto,
        "file_name": ruta.name,
        "file_type": "text/csv",
    })
    # dryrun va como kwarg, no como argumento posicional: si se cuela en la
    # posición de `options`, Odoo lo interpreta como "prueba" y no guarda nada.
    resultado = api.llamar(
        "base_import.import", "execute_import",
        [[importacion], cabecera, cabecera, dict(OPCIONES)],
        {"dryrun": seco},
    )
    resultado = resultado or {}
    mensajes = resultado.get("messages") or []
    errores = [m for m in mensajes if m.get("type") == "error"]
    avisos = [m for m in mensajes if m.get("type") == "warning"]
    creados = len(resultado.get("ids") or [])
    return creados, errores + avisos


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--empresa", required=True)
    p.add_argument("--alumno", required=True, type=int)
    p.add_argument("--carpeta", default=None,
                   help="carpeta de la variante (por defecto salida/<sector>-A<NN>)")
    p.add_argument("--seco", action="store_true", help="prueba sin escribir nada")
    p.add_argument("--url", default=os.environ.get("ODOO_URL", "http://odoo:8069"))
    p.add_argument("--bd", default=os.environ.get("ODOO_BD", "empresa"))
    p.add_argument("--usuario", default=os.environ.get("ODOO_USUARIO", "admin"))
    p.add_argument("--clave", default=os.environ.get("ODOO_CLAVE", "admin"))
    p.add_argument("--transporte", default=os.environ.get("ODOO_API", "xmlrpc"))
    args = p.parse_args(argv)

    empresa = catalogo.cargar(args.empresa)
    maestros.construir(empresa, Variante(args.empresa, args.alumno))  # valida el catálogo

    carpeta = (RAIZ / "salida" / f"{args.empresa}-A{args.alumno:02d}") if not args.carpeta \
        else __import__("pathlib").Path(args.carpeta)
    if not (carpeta / "maestros").is_dir():
        print(f"No encuentro {carpeta}/maestros. Ejecuta antes generar.py.", file=sys.stderr)
        return 2

    api = Odoo(args.url, args.bd, args.usuario, args.clave, args.transporte)
    try:
        api.conectar()
    except ErrorOdoo as exc:
        print(f"No se puede conectar con Odoo en {args.url}: {exc}", file=sys.stderr)
        return 1

    if args.seco:
        print("Modo de prueba: Odoo procesa los ficheros y deshace los cambios.\n")

    fallos = 0
    for modelo, nombre in FICHEROS:
        ruta = carpeta / "maestros" / nombre
        if not ruta.is_file():
            print(f"  falta {ruta}")
            fallos += 1
            continue
        try:
            creados, mensajes = importar_fichero(api, modelo, ruta, args.seco)
        except ErrorOdoo as exc:
            print(f"  {nombre}: ERROR — {exc}")
            fallos += 1
            continue
        marca = "ok" if not mensajes else f"{len(mensajes)} avisos"
        print(f"  {nombre:<32} {creados:>3} registros · {marca}")
        for m in mensajes[:3]:
            print(f"      - {m.get('field')}: {m.get('message', '')[:120]}")
        if any(m.get("type") == "error" for m in mensajes):
            fallos += 1

    print()
    if fallos:
        print(f"Importación terminada con {fallos} fichero(s) con problemas.")
        return 1
    print("Importación terminada sin errores.")
    if not args.seco:
        print("Siguiente paso: cargar_historico.py (impuestos, stock e histórico).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
