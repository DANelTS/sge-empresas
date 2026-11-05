#!/usr/bin/env python3
"""generar.py — crea la variante de un alumno a partir del catálogo del sector.

Uso (desde el servicio de herramientas del compose):

    docker compose run --rm herramientas generar.py --empresa cerveceria --alumno 07
    docker compose run --rm herramientas generar.py --empresa cerveceria --alumno 07 --destino salida/pruebas

Sin --destino, escribe en `salida/<sector>-A<NN>/`. La variante 00 es la
canónica: la que usan las pruebas del repositorio y las demostraciones.

El resultado es siempre el mismo para la misma pareja (empresa, alumno): los
números salen de una semilla derivada de ambos.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from sge import bandejas, catalogo, maestros, salida, sucesos
from sge.variante import Variante

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def argumentos(argv=None):
    p = argparse.ArgumentParser(
        description="Genera la variante de un alumno para una empresa del catálogo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--empresa", required=True, help="clave del sector (p. ej. cerveceria)")
    p.add_argument("--alumno", required=True, type=int,
                   help="número de lista 01-22 (00 = variante canónica)")
    p.add_argument("--destino", default=None,
                   help="carpeta de salida (por defecto salida/<sector>-A<NN>)")
    p.add_argument("--lista", action="store_true", help="lista los sectores disponibles")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = argumentos(argv)

    if args.lista:
        for clave in catalogo.sectores():
            e = catalogo.cargar(clave)
            print(f"{clave:20} {e.nombre}")
        return 0

    if not 0 <= args.alumno <= 22:
        print("El número de alumno debe estar entre 00 y 22.", file=sys.stderr)
        return 2

    empresa = catalogo.cargar(args.empresa)
    variante = Variante(args.empresa, args.alumno)
    m = maestros.construir(empresa, variante)

    destino = pathlib.Path(args.destino) if args.destino else (
        RAIZ / "salida" / f"{args.empresa}-A{args.alumno:02d}"
    )
    destino = destino.resolve()
    destino.mkdir(parents=True, exist_ok=True)

    salida.escribir_csvs(destino / "maestros", m)
    salida.escribir_resumen(destino, empresa, m)
    salida.escribir_datos_empresa(destino, empresa, m)
    salida.escribir_leeme(destino, empresa, m)
    salida.copiar_ficha(destino, empresa, m, args.alumno)
    bandejas.escribir(destino, empresa, m, variante)
    for sesion in ("s18-ventas", "s19-compras"):
        sucesos.escribir_en(destino, empresa, m, sesion)

    print(f"Variante generada: {m.empresa['nombre']}")
    print(f"  carpeta:    {destino}")
    print(f"  NIF:        {m.empresa['cif']}")
    print(f"  productos:  {len(m.productos)}   clientes: {len(m.clientes)}   proveedores: {len(m.proveedores)}")
    print()
    print("Siguiente paso: importa los CSV en el orden que indica LEEME.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
