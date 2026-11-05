#!/usr/bin/env bash
# instalar.sh — deja el entorno de trabajo listo en macOS o Linux.
#
#   ./instalar.sh                          solo el entorno (lo que necesita un alumno)
#   ./instalar.sh --sector cerveceria --alumno 07    además, genera su variante
#   ./instalar.sh --sector _demo-tostadero --alumno 0 --completo   demo lista (profesor)
#
# Con --completo también importa los maestros, configura la compañía, carga el
# histórico y verifica. Es el camino del profesor para ensayar la demo.
set -euo pipefail

SECTOR=""
ALUMNO=""
COMPLETO=0
BD="${ODOO_BD:-empresa}"

rojo() { printf '\033[31m%s\033[0m\n' "$*"; }
verde() { printf '\033[32m%s\033[0m\n' "$*"; }
paso() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

uso() {
  cat <<'TXT'
Uso: ./instalar.sh [--sector NOMBRE --alumno NN] [--completo] [--bd NOMBRE]

  --sector    carpeta de empresas/ (cerveceria, bicicletas, oficina, aceite, vivero)
  --alumno    número de lista 01-22 (00 = variante canónica)
  --completo  importa maestros, configura compañía, carga histórico y verifica
  --bd        nombre de la base de datos (por defecto "empresa")

Sin --sector solo deja Docker y la base preparados.
TXT
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sector) SECTOR="${2:-}"; shift 2 ;;
    --alumno) ALUMNO="${2:-}"; shift 2 ;;
    --bd) BD="${2:-}"; shift 2 ;;
    --completo) COMPLETO=1; shift ;;
    -h|--help) uso; exit 0 ;;
    *) rojo "Opción desconocida: $1"; uso; exit 2 ;;
  esac
done

cd "$(dirname "$0")"

# ---------------------------------------------------------------------------
paso "1. Comprobando Docker"
# ---------------------------------------------------------------------------
# Se acepta cualquier motor compatible: Docker con el plugin compose, o Podman
# con podman-compose (habitual en Fedora). El fichero es el mismo.
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
  MOTOR=docker
elif command -v podman-compose >/dev/null 2>&1; then
  COMPOSE=(podman-compose)
  MOTOR=podman
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
  MOTOR=docker
elif command -v podman >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
  COMPOSE=(podman compose)
  MOTOR=podman
else
  rojo "No encuentro un motor de contenedores con compose."
  echo "  Windows/macOS: instala Docker Desktop y ábrelo."
  echo "  Fedora/Linux sin Docker: sudo dnf install podman-compose"
  exit 1
fi

if [[ "$MOTOR" == "docker" ]] && ! docker info >/dev/null 2>&1; then
  rojo "El motor de Docker no responde. ¿Está Docker Desktop arrancado?"
  exit 1
fi
if [[ "$MOTOR" == "podman" ]] && ! podman info >/dev/null 2>&1; then
  rojo "El motor de Podman no responde."
  exit 1
fi
if [[ "$MOTOR" == "podman" ]]; then
  # Podman no resuelve nombres cortos (odoo:19.0) sin preguntar, y en un script
  # no hay terminal. Se le dice explícitamente que busque en Docker Hub.
  REGISTRIES="$(mktemp)"
  printf 'unqualified-search-registries = ["docker.io"]\n' > "$REGISTRIES"
  export CONTAINERS_REGISTRIES_CONF="$REGISTRIES"
fi
verde "Motor disponible: $MOTOR (${COMPOSE[*]})"

# ---------------------------------------------------------------------------
paso "2. Fichero .env"
# ---------------------------------------------------------------------------
if [[ -f .env ]]; then
  verde ".env ya existe; no lo toco"
else
  # Sin tuberías que cierren antes de tiempo: con "set -o pipefail" un head que
  # corta a tr le hace devolver 141 y el script aborta.
  nueva_clave() {
    if command -v openssl >/dev/null 2>&1; then
      openssl rand -hex 16 | cut -c1-20
    else
      od -An -N20 -tx1 /dev/urandom | tr -d ' \n'
    fi
  }
  CLAVE_BD="$(nueva_clave)"
  CLAVE_ADMIN="$(nueva_clave)"
  sed -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${CLAVE_BD}|" \
      -e "s|^ADMIN_PASSWD=.*|ADMIN_PASSWD=${CLAVE_ADMIN}|" \
      -e "s|^ODOO_CLAVE=.*|ODOO_CLAVE=${CLAVE_ADMIN}|" \
      .env.example > .env
  verde ".env creado con contraseñas aleatorias"
  echo "  Guárdalas: la maestra del gestor es ADMIN_PASSWD."
fi

# ---------------------------------------------------------------------------
paso "3. Arrancando PostgreSQL y Odoo"
# ---------------------------------------------------------------------------
"${COMPOSE[@]}" up -d

echo -n "  Esperando a que Odoo responda"
for _ in $(seq 1 60); do
  if curl -fsS -o /dev/null "http://localhost:${ODOO_PUERTO:-8069}/web/login" 2>/dev/null; then
    echo; verde "  Odoo en marcha en http://localhost:${ODOO_PUERTO:-8069}"
    break
  fi
  echo -n "."
  sleep 3
done
if ! curl -fsS -o /dev/null "http://localhost:${ODOO_PUERTO:-8069}/web/login" 2>/dev/null; then
  rojo "  Odoo no responde. Mira el registro:"
  echo "    ${COMPOSE[*]} logs --tail 50 odoo"
  exit 1
fi

# ---------------------------------------------------------------------------
paso "4. Base de datos '${BD}'"
# ---------------------------------------------------------------------------
CLAVE="$(grep -E '^ODOO_CLAVE=' .env | cut -d= -f2-)"
if "${COMPOSE[@]}" exec -T db psql -U odoo -lqt 2>/dev/null | cut -d'|' -f1 | grep -qw "$BD"; then
  verde "La base '${BD}' ya existe"
else
  echo "  Creando la base (país España, idioma español)…"
  "${COMPOSE[@]}" run --rm odoo db init "$BD" --country ES --language es_ES \
      --username admin --password "$CLAVE" >/dev/null
  echo "  Instalando CRM, Ventas, Compras, Inventario y Facturación…"
  "${COMPOSE[@]}" run --rm odoo module install -d "$BD" \
      account sale_management purchase stock crm >/dev/null
  verde "Base creada con la localización española"
fi

# ---------------------------------------------------------------------------
if [[ -n "$SECTOR" ]]; then
  paso "5. Generando la variante ${SECTOR} A$(printf '%02d' "${ALUMNO:-0}")"
  "${COMPOSE[@]}" run --rm herramientas generar.py --empresa "$SECTOR" --alumno "${ALUMNO:-0}"
fi

# ---------------------------------------------------------------------------
if [[ "$COMPLETO" == "1" ]]; then
  paso "6. Cargando datos (camino del profesor)"
  export ODOO_BD="$BD"
  if ! "${COMPOSE[@]}" run --rm herramientas importar_maestros.py \
      --empresa "$SECTOR" --alumno "${ALUMNO:-0}" --bd "$BD" --url http://odoo:8069; then
    rojo "La importación de maestros ha fallado."
    echo "  La base '$BD' puede haber quedado a medias. Lo más rápido:"
    echo "    ./instalar.sh --bd ${BD}-2 --sector $SECTOR --alumno ${ALUMNO:-0} --completo"
    exit 1
  fi
  "${COMPOSE[@]}" run --rm herramientas configurar_compania.py \
      --empresa "$SECTOR" --alumno "${ALUMNO:-0}" --bd "$BD" --url http://odoo:8069
  "${COMPOSE[@]}" run --rm herramientas cargar_historico.py \
      --empresa "$SECTOR" --alumno "${ALUMNO:-0}" --bd "$BD" --url http://odoo:8069
  "${COMPOSE[@]}" run --rm herramientas verificar.py \
      --empresa "$SECTOR" --alumno "${ALUMNO:-0}" --bd "$BD" --url http://odoo:8069 || true
fi

# ---------------------------------------------------------------------------
paso "Listo"
# ---------------------------------------------------------------------------
echo "  Odoo:    http://localhost:${ODOO_PUERTO:-8069}  (usuario admin)"
echo "  Base:    ${BD}"
if [[ -n "$SECTOR" ]]; then
  echo "  Variante: salida/${SECTOR}-A$(printf '%02d' "${ALUMNO:-0}")/"
  if [[ "$COMPLETO" == "1" ]]; then
    echo "  Datos cargados y verificados: la base está lista para demostrar."
  else
    echo "  Siguiente paso: abre su LEEME.md e importa los CSV en Odoo."
  fi
fi
echo
echo "  Parar el entorno:   ${COMPOSE[*]} down"
echo "  Ver el registro:    ${COMPOSE[*]} logs -f odoo"
