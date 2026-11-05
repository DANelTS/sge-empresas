# Cómo se monta este entorno, pieza a pieza

Este documento explica qué hace cada comando y cada fichero, para poder montar el
entorno a mano en cualquier máquina y para saber qué mirar cuando algo falla. Los
instaladores (`instalar.sh`, `instalar.ps1`) no hacen nada que no esté aquí: solo
lo ejecutan en orden.

## 1. La ruta mínima, sin instaladores

Requisitos: Docker (Desktop en Windows/macOS, Engine + plugin compose en Linux) y
Git. Nada de Python, PostgreSQL ni Odoo en la máquina.

```bash
git clone <repo> && cd sge-empresas           # 1. el repositorio
cp config/odoo.conf.example config/odoo.conf  # 2. tu configuración
docker compose up -d                          # 3. arrancar
docker compose run --rm odoo odoo db init empresa --country ES --language es_ES \
        --username admin --password admin      # 4. la base
docker compose run --rm odoo odoo module install -d empresa \
        account sale_management purchase stock crm    # 5. las aplicaciones
docker compose run --rm herramientas generar.py \
        --empresa cerveceria --alumno 07       # 6. los datos de tu empresa
```

| Paso | Qué hace de verdad | Cómo sabes que ha ido bien |
|---|---|---|
| 1 | Trae el compose, la configuración, los catálogos y los scripts. | `ls` muestra `docker-compose.yml`, `config/` y `herramientas/`. |
| 2 | Crea **tu** configuración de Odoo (la del repositorio es un ejemplo). | `ls config/` muestra `odoo.conf` y `odoo.conf.example`. |
| 3 | Descarga imágenes y levanta `db` (PostgreSQL 17) y `odoo` (19). | `docker compose ps` los muestra `healthy`; <http://localhost:8069> responde. |
| 4 | Crea la base **con país España y español**, sin datos de demostración. | `select chart_template from res_company;` devuelve `es_pymes`; la moneda es EUR. |
| 5 | Instala CRM, Ventas, Compras, Inventario y Facturación. | El menú superior muestra esas cinco aplicaciones. |
| 6 | Escribe en `salida/<sector>-A<NN>/` los CSV y documentos de la variante. | `ls salida/cerveceria-A07/maestros` muestra seis CSV. |

El **`odoo` repetido** en `run --rm odoo odoo db init` no es una errata: el primer
`odoo` es el servicio del compose y el segundo, el comando que se ejecuta dentro
de la imagen. `docker compose run` sustituye el comando por defecto del
contenedor, y el script de arranque de la imagen solo reconoce argumentos que
empiecen por `odoo` o por `-`.

Los pasos 4 y 5 también se pueden hacer por la interfaz (es lo que pide la S16):
crear la base en `/web/database/manager`, poner el país **antes** de instalar
Facturación y luego instalar las aplicaciones en **Aplicaciones**.

## 2. Qué hay en cada fichero

### `docker-compose.yml`

Tres servicios y dos volúmenes:

- **`db`**: `postgres:17`. El volumen `datos-bd` guarda los datos; si se borra el
  volumen, se borra la empresa.
- **`odoo`**: `odoo:19.0`. El volumen `datos-odoo` guarda el *filestore* (logos,
  adjuntos, PDF generados).
- **`herramientas`**: `python:3.12-slim` con PyYAML y requests. **No arranca con
  `up`**: se usa con `docker compose run --rm herramientas <script>`.

Qué ve cada contenedor del repositorio:

| Servicio | Montajes | Por qué |
|---|---|---|
| `odoo` | `./config` → `/etc/odoo` (solo lectura) | Leer `odoo.conf`. |
| `odoo` | `./addons` → `/mnt/extra-addons` | Módulos propios desde la UD4. |
| `odoo` | `./salida/copias` → `/copias` | Solo para copias de seguridad. |
| `herramientas` | `./` → `/repo` | Lee `empresas/` y escribe `salida/`. |
| `db` | volumen `datos-bd` | Los datos. |

Odoo **no** ve el repositorio: no puede leer los catálogos, ni las bandejas, ni
las variantes de otros alumnos. Solo su configuración, sus módulos y la carpeta de
copias.

Detalles que importan:

- `depends_on: db: condition: service_healthy` → Odoo no arranca hasta que
  PostgreSQL acepta conexiones. Sin eso, el arranque es una carrera.
- `127.0.0.1:8069:8069` → Odoo solo escucha en este equipo. Con la contraseña
  maestra conocida, publicarlo en la red del aula dejaría las bases de los demás
  al alcance de cualquiera desde `/web/database/manager`.
- `./config` se monta como **carpeta**, no como fichero. Montar un fichero que no
  existe hace que Docker cree un *directorio* con ese nombre y el error que sale
  después no hay quien lo lea.

### `config/odoo.conf.example` y `config/odoo.conf`

El `.example` está en el repositorio; el alumno lo copia a `config/odoo.conf`, que
está en `.gitignore`. Ahí viven la conexión con PostgreSQL y la contraseña maestra
del gestor de bases de datos. Si no se copia, Odoo arranca con la configuración
por defecto de la imagen, busca la base en `localhost` y falla con
`connection refused`.

### `herramientas/`

Scripts que se ejecutan **dentro** del contenedor de herramientas contra la API de
Odoo: `generar.py` (datos), `importar_maestros.py` (CSV), `cargar_historico.py`,
`verificar.py`, `configurar_compania.py` (solo profesor) y `odoo_api.py` (cliente
de la API). El paquete `sge/` contiene la lógica: NIF, catálogo, variantes,
histórico y bandejas.

## 3. Por qué el contenedor de Odoo no lleva entrypoint propio

Hubo un `docker/entrada.sh` que generaba la configuración al arrancar desde un
`.env`. Se retiró, y conviene saber por qué, porque el problema que resolvía sigue
existiendo.

### Lo que hace la imagen oficial

`/entrypoint.sh`, dentro de `odoo:19.0`:

1. Lee `HOST`, `PORT`, `USER` y `PASSWORD` del entorno (con valores por defecto).
2. Si el fichero de configuración **no** define ya `db_host`, `db_port`,
   `db_user` y `db_password`, los añade como argumentos `--db_*`.
3. Ejecuta `odoo` con lo que le hayas pasado.

### El problema que había

La **contraseña maestra** del gestor de bases de datos se configura con
`admin_passwd`. En Odoo 18 se podía pasar por línea de comandos; en la 19 esa
opción ya no existe y el servidor ni arranca:

```
odoo server: error: no such option: --admin-passwd
```

Solo se lee del fichero de configuración. Para inyectarla sin escribirla en el
repositorio, el wrapper renderizaba `config/odoo.conf` desde `.env` al arrancar.

### Por qué se descartó

- Obligaba a montar **todo el repositorio** dentro del contenedor de Odoo:
  acoplamiento innecesario y acceso a ficheros que no necesita.
- Añadía una pieza propia que puede fallar antes que Odoo, y un `command`
  distinto del de todos los tutoriales.
- El secreto acababa igualmente en `docker inspect`, así que la ganancia real era
  poca para el ruido que metía.

### Lo que se hace ahora

El alumno copia `config/odoo.conf.example` a `config/odoo.conf` y lo edita si
quiere. Odoo arranca con el entrypoint oficial, sin nada propio. El coste es un
paso manual (copiar un fichero) y que la contraseña maestra es conocida
(`admin`); a cambio, el contenedor de Odoo solo ve su configuración y desaparecen
las piezas que pueden romperse.

En un servidor de producción esto no se hace así: la configuración se renderiza
desde un gestor de secretos y se monta en solo lectura, o se usan *secrets* del
orquestador. Aquí se elige lo simple porque el objetivo es aprender ERP, no
administración de secretos.

## 4. Copias de seguridad sin montar el repositorio

El contenedor de Odoo solo escribe en `/copias` (que en el anfitrión es
`salida/copias`):

```bash
# hacer
docker compose exec odoo odoo db dump empresa /copias/copia.zip

# restaurar (destructivo: --force borra la base antes)
docker compose exec odoo odoo db load empresa /copias/copia.zip --force
```

## 5. Depurar cuando algo no arranca

```bash
docker compose config                              # ¿cómo interpreta compose el fichero?
docker compose ps                                  # ¿están los servicios arriba?
docker compose logs --tail 50 odoo
docker compose exec odoo cat /etc/odoo/odoo.conf   # la configuración que usa
docker compose exec db psql -U odoo -l             # ¿ve Odoo la base?
```

| Síntoma | Causa |
|---|---|
| `connection refused` a `localhost:5432` al arrancar | No existe `config/odoo.conf`: Odoo usa la configuración por defecto. |
| `password authentication failed` | `db_password` de `odoo.conf` no coincide con `POSTGRES_PASSWORD` del compose, o el volumen se creó con otra contraseña. |
| `no such option: --admin-passwd` | Alguien ha añadido ese argumento al `command`. En la 19 no existe. |
| La moneda es USD | Se instaló Facturación antes de poner el país. Hay que recrear la base. |
| `port is already allocated` | Otro proceso en 8069: cambia el puerto en el compose. |
| `permission denied` en Linux | SELinux: añade `:z` a los montajes del compose. |
