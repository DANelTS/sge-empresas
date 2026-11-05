# Cómo se monta este entorno, pieza a pieza

Este documento explica qué hace cada comando y cada fichero del repositorio, para
poder montar el entorno a mano en cualquier máquina y para saber qué mirar cuando
algo falla. Los instaladores (`instalar.sh`, `instalar.ps1`) no hacen nada que no
esté aquí: solo lo ejecutan en orden.

## 1. La ruta mínima, sin instaladores

Requisitos: Docker (Desktop en Windows/macOS, Engine + plugin compose en Linux) y
Git. Nada de Python, PostgreSQL ni Odoo en la máquina.

```bash
git clone <repo> && cd sge-empresas     # 1. el repositorio
cp .env.example .env && $EDITOR .env    # 2. las contraseñas
docker compose up -d                    # 3. arrancar los contenedores
docker compose run --rm odoo db init empresa --country ES --language es_ES \
        --username admin --password <la de ODOO_CLAVE>          # 4. la base
docker compose run --rm odoo module install -d empresa \
        account sale_management purchase stock crm              # 5. las apps
docker compose run --rm herramientas generar.py \
        --empresa cerveceria --alumno 07                        # 6. los datos
```

| Paso | Qué hace de verdad | Cómo sabes que ha ido bien |
|---|---|---|
| 1 | Trae el compose, la configuración, los catálogos y los scripts. | `ls` muestra `docker-compose.yml` y `herramientas/`. |
| 2 | Crea el fichero de secretos que lee el compose. | `cat .env` tiene las tres contraseñas rellenas. |
| 3 | Descarga imágenes y levanta `db` (PostgreSQL 17) y `odoo` (19). | `docker compose ps` los muestra `running`/`healthy`; <http://localhost:8069> responde. |
| 4 | Crea la base **con país España y español** e instala el mínimo. | `SELECT chart_template FROM res_company;` devuelve `es_pymes` y la moneda es EUR. |
| 5 | Instala CRM, Ventas, Compras, Inventario y Facturación. | El menú superior muestra esas cinco aplicaciones. |
| 6 | Escribe en `salida/<sector>-A<NN>/` los CSV y los documentos de la variante. | `ls salida/cerveceria-A07/maestros` muestra seis CSV. |

Los pasos 4 y 5 se pueden hacer también por la interfaz (es lo que se pide en la
S16): crear la base desde `/web/database/manager`, poner el país **antes** de
instalar Facturación y luego instalar las aplicaciones en **Aplicaciones**. La
diferencia es que por línea de comandos es repetible y no depende de clics.

## 2. Qué hay en cada fichero

### `docker-compose.yml`

Tres servicios y dos volúmenes:

- **`db`**: `postgres:17`. El volumen `datos-bd` guarda los datos; si se borra el
  volumen, se borra la empresa.
- **`odoo`**: `odoo:19.0`. El volumen `datos-odoo` guarda el *filestore* (logos,
  adjuntos, PDF). Publica 8069.
- **`herramientas`**: `python:3.12-slim` con PyYAML y requests. **No arranca con
  `up`**: se usa con `docker compose run --rm herramientas <script>`. Existe para
  que el alumnado de Windows no instale Python y para que los scripts vean el
  repositorio en `/repo`.

Detalles que importan:

- `depends_on: db: condition: service_healthy` → Odoo no arranca hasta que
  PostgreSQL acepta conexiones. Sin eso, el arranque es una carrera.
- `./:/repo:ro` en `odoo` → el contenedor puede leer `config/odoo.conf` y
  `docker/entrada.sh`, pero no escribir en el repositorio.
- `./salida:/repo/salida` (sin `:ro`) → ahí sí escribe: copias de seguridad y
  variantes.

### `config/odoo.conf`

Plantilla de configuración con marcas (`@DB_PASSWORD@`, `@ADMIN_PASSWD@`…). No se
usa tal cual: se renderiza al arrancar. Explica cada opción en comentarios.

### `docker/entrada.sh`

Envuelve el arranque de la imagen oficial. Su razón de ser está en el apartado 3.

### `herramientas/`

Scripts que se ejecutan **dentro** del contenedor de herramientas contra la API de
Odoo: `generar.py` (datos), `importar_maestros.py` (CSV), `cargar_historico.py`,
`verificar.py`, `configurar_compania.py` (solo profesor) y `odoo_api.py` (cliente
de la API). El paquete `sge/` contiene la lógica: NIF, catálogo, variantes,
histórico y bandejas.

## 3. Por qué el contenedor de Odoo lleva un entrypoint propio

### Lo que hace la imagen oficial

La imagen `odoo:19.0` trae `/entrypoint.sh`. En esencia:

1. Lee `HOST`, `PORT`, `USER` y `PASSWORD` del entorno (con valores por defecto).
2. Si el fichero de configuración **no** define ya `db_host`, `db_port`,
   `db_user` y `db_password`, los añade como argumentos `--db_*` al ejecutar.
3. Ejecuta `odoo` con lo que le hayas pasado en `command`.

Eso funciona, y por eso el compose no necesita nada más para las credenciales de
PostgreSQL.

### El problema

La **contraseña maestra** del gestor de bases de datos (la que piden al crear,
duplicar o restaurar una base) se configura con `admin_passwd`. En Odoo 18 se
podía pasar por línea de comandos:

```bash
odoo --admin-passwd=loquesea        # Odoo 18
```

En la 19 esa opción **ya no existe**: el servidor ni arranca.

```
odoo server: error: no such option: --admin-passwd
```

Y solo se lee del fichero de configuración. Eso deja tres caminos:

| Opción | Coste |
|---|---|
| Escribir la contraseña en `config/odoo.conf` y montarlo | La contraseña acaba en el repositorio público. Descartado. |
| Generar una imagen propia por alumno con la contraseña dentro | Una imagen de 2 GB por persona y una contraseña en el historial de Docker. Descartado. |
| Montar un `odoo.conf` distinto por alumno, escrito a mano | Hay que mantener dos ficheros sincronizados y el alumno tiene que editar el suyo antes de arrancar. Frágil. |
| **Renderizar el fichero al arrancar desde `.env`** | Es lo que se hace: una pieza más que entender, a cambio de que el secreto viva solo en `.env`. |

### Lo que hace `docker/entrada.sh`

```sh
python3 - "$CONF" <<'PY'          # 1. lee config/odoo.conf (la plantilla)
valores = {                        # 2. sustituye las marcas por lo que hay en
    "@DB_HOST@": os.environ.get("HOST", "db"),        #    el entorno, que Docker
    "@DB_PASSWORD@": os.environ.get("POSTGRES_PASSWORD"),  # Compose rellena
    "@ADMIN_PASSWD@": os.environ.get("ADMIN_PASSWD"),      # desde .env
    ...
}
destino.write_text(plantilla)      # 3. escribe /tmp/odoo.conf
PY
export ODOO_RC="$CONF"             # 4. le dice a Odoo dónde está su config
exec /entrypoint.sh odoo "$@"      # 5. delega en el entrypoint oficial
```

Cuatro decisiones dentro de esas cinco líneas:

1. **Se renderiza, no se copia.** Si falta `ADMIN_PASSWD`, el script termina con
   un mensaje claro en vez de arrancar con la contraseña por defecto. Un fallo
   ruidoso es mejor que uno silencioso.
2. **`/tmp/odoo.conf`, no el del repositorio.** El repositorio se monta en modo
   lectura; el fichero con la contraseña se escribe en el sistema de ficheros del
   contenedor, que es efímero y no se versiona.
3. **Se exporta `ODOO_RC`.** Es la variable que Odoo lee para saber qué
   configuración usar, y vale también para las subórdenes (`db init`,
   `module install`, `shell`), que es lo que permite el paso 4 de la ruta mínima.
4. **Se delega en `/entrypoint.sh odoo "$@"`.** No se reimplementa el entrypoint
   oficial: se le pasa el control con los argumentos que venían del compose.
   Así se conserva su lógica (los `--db_*`, el orden) y solo se añade lo que
   falta.

El resultado: `docker compose run --rm odoo db init empresa …` funciona, y
`docker compose exec odoo cat /tmp/odoo.conf` deja ver la configuración real que
está usando el contenedor (sin la contraseña en claro en el repositorio).

### El coste de esta decisión

- Hay una pieza más: si el script falla, el contenedor no arranca. Se ve en
  `docker compose logs odoo` con un `ERROR: falta el valor de …`.
- `command` en el compose ya no es `odoo` sino `server` (sin el prefijo), porque
  el wrapper lo pone. Es la fuente de confusión más probable si alguien copia un
  ejemplo de internet.
- La contraseña maestra acaba en el entorno del contenedor (`docker inspect` la
  muestra). En un aula no es un riesgo; en un servidor público, sí: allí lo
  correcto sería un gestor de secretos.

### La alternativa que yo elegiría en un servidor de producción

No usar `.env` sino *secrets* del orquestador (Docker Swarm, Kubernetes, systemd
con `LoadCredential=`) y montar el `odoo.conf` ya renderizado como fichero de
solo lectura propiedad de `odoo`. Es lo mismo, pero el secreto no aparece en
`docker inspect`.

## 4. Depurar cuando algo no arranca

```bash
docker compose config            # ¿cómo interpreta compose el fichero?
docker compose ps                # ¿están los servicios arriba?
docker compose logs --tail 50 odoo
docker compose exec odoo cat /tmp/odoo.conf     # la config ya renderizada
docker compose run --rm odoo --help             # ¿responde el binario?
docker compose exec db psql -U odoo -l          # ¿ve Odoo la base?
```

Errores típicos y su causa:

| Síntoma | Causa |
|---|---|
| `falta el valor de @ADMIN_PASSWD@` | `.env` sin `ADMIN_PASSWD`, o el compose no lo pasa. |
| `password authentication failed` | La contraseña de `.env` no es la que se usó al crear el volumen: `down -v` y empezar. |
| `no such option: --admin-passwd` | Alguien ha añadido ese argumento al `command` (ya no existe en la 19). |
| La moneda es USD | Se instaló Facturación antes de poner el país. Hay que recrear la base. |
| `port is already allocated` | Otro proceso en 8069: cambia `ODOO_PUERTO` en `.env`. |
