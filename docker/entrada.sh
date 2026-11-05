#!/bin/sh
# docker/entrada.sh — arranque del contenedor de Odoo.
#
# Para qué existe esta pieza:
#   Odoo 19 ya NO acepta la contraseña maestra por línea de comandos (la opción
#   --admin-passwd desapareció) y solo la lee del fichero de configuración.
#   Como no queremos contraseñas escritas en el repositorio, este script genera
#   /tmp/odoo.conf a partir de config/odoo.conf sustituyendo las marcas @...@
#   por lo que venga en el entorno (que Docker Compose rellena desde .env).
#
# Después delega en el script de arranque de la imagen oficial de Odoo, que es
# quien espera a PostgreSQL y lanza el proceso.
set -eu

CONF=/tmp/odoo.conf

python3 - "$CONF" <<'PY'
import os
import pathlib
import sys

destino = pathlib.Path(sys.argv[1])
plantilla = pathlib.Path("/repo/config/odoo.conf").read_text(encoding="utf-8")

valores = {
    "@DB_HOST@": os.environ.get("HOST", "db"),
    "@DB_PORT@": os.environ.get("PORT", "5432"),
    "@DB_USER@": os.environ.get("USER", "odoo"),
    "@DB_PASSWORD@": os.environ.get("POSTGRES_PASSWORD") or os.environ.get("PASSWORD", ""),
    "@ADMIN_PASSWD@": os.environ.get("ADMIN_PASSWD", ""),
}

for marca, valor in valores.items():
    if not valor:
        sys.exit(
            f"ERROR: falta el valor de {marca}.\n"
            "Copia .env.example a .env y rellena las contraseñas."
        )
    plantilla = plantilla.replace(marca, valor)

destino.write_text(plantilla, encoding="utf-8")
PY

export ODOO_RC="$CONF"

# "$@" son los argumentos de la orden de docker compose (por defecto: server).
# Envolverlos en "odoo" permite usar también las submórdenes de la 19:
#   docker compose run --rm odoo db init empresa --country ES
#   docker compose run --rm odoo module install -d empresa account stock
exec /entrypoint.sh odoo "$@"
