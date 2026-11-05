# Copias de seguridad de la base de datos

Una copia de seguridad de Odoo son **dos cosas**: la base de datos PostgreSQL y
el *filestore*, que es la carpeta donde Odoo guarda los archivos subidos (logos,
adjuntos, PDF generados). Si copias solo la base, te llevas los registros pero
las imágenes y los PDF salen rotos. El comando `odoo db` de la 19 lo hace todo
de una vez, en un ZIP.

## Hacer la copia

Con el entorno levantado:

```powershell
docker compose exec odoo odoo db dump empresa /copias/copia-S16.zip
```

Cambia el nombre del fichero por el que quieras: `copia-S16.zip`,
`copia-antes-de-importar.zip`, `copia-final.zip`. Se guarda en tu carpeta
`salida/` del repositorio (`salida/` está en `.gitignore`: nunca se sube).

Para ver lo que hay dentro del ZIP (es un ZIP normal):

```powershell
tar -tf salida/copia-S16.zip
```

Debe contener un `dump.sql` y una carpeta `filestore/`.

> **Si da `Permission denied` en `/copias`** (pasa en Linux, no en Windows ni en
> macOS), dale permiso a la carpeta desde el anfitrión:
> `chmod 777 salida/copias`. El contenedor de Odoo corre con el usuario 100 y
> necesita escribir ahí.

**Cuánto ocupa.** Una base de la UD3 ronda los 30–60 MB con filestore, según
cuántos PDF hayas generado. Si te sale mucho más, mira cuántas copias has dejado
en `salida/`.

## Restaurar una copia

```powershell
docker compose stop odoo
docker compose exec odoo odoo db load empresa /copias/copia-S16.zip --force
docker compose start odoo
```

- `db load <nombre> <fichero>` restaura el ZIP en la base `<nombre>`. Si la base
  ya existe y no pones `--force`, se niega: es una protección, no un error.
- `--force` borra antes la base existente. **Es destructivo**: comprueba dos
  veces el nombre del fichero.
- La restauración se hace con Odoo parado para que nadie esté escribiendo.

Puedes restaurar con **otro nombre** para no pisar tu trabajo actual:

```powershell
docker compose exec odoo odoo db load empresa-pruebas /copias/copia-S16.zip
```

Sale una base nueva, `empresa-pruebas`, que puedes abrir desde el selector de
bases de datos. Es la forma de comprobar que una copia sirve de verdad: si
restaura y abre, la copia está bien.

## La copia por la interfaz (equivalente)

1. Entra en <http://localhost:8069/web/database/manager>.
2. **Backup** (Respaldo) de la base `empresa`, formato ZIP, con la contraseña
   maestra de `config/odoo.conf` (`admin_passwd`).
3. El navegador descarga el ZIP; guárdalo donde quieras.

Para restaurar: **Restore** en esa misma pantalla, subiendo el ZIP y poniendo el
nombre de la base.

Las dos vías hacen lo mismo. La de línea de comandos es mejor en clase porque no
depende de que el navegador tenga espacio ni de la contraseña maestra.

## Rutina que se pide en la UD3

| Momento | Copia | Para qué |
|---|---|---|
| S16, al terminar la configuración | `copia-S16.zip` | Punto de partida limpio. |
| S17, después de importar y verificar | `copia-S17.zip` | Si algo se rompe en la S18, vuelves aquí. |
| Antes de la prueba de la S22 | `copia-final.zip` | Es la que se entrega en la prueba práctica. |
| Al terminar el trabajo personal | `copia-trabajo.zip` | Se entrega con la memoria. |

**Guarda las copias también fuera de `salida/`** (una carpeta en el escritorio, o
la nube del centro). Un `docker compose down -v` borra los volúmenes, y con ellos
la base; la copia es lo único que te salva.

## Errores frecuentes

**«database already exists».** Falta `--force`, o el nombre de la base está mal
escrito.

**La copia pesa 0 bytes.** El contenedor no pudo escribir en `/copias`.
Comprueba que existe la carpeta `salida/copias/` en tu repositorio: es la que el
compose monta (línea `./salida/copias:/copias`).

**Al restaurar, Odoo arranca con otra base.** Odoo abre la última base usada.
Selecciona la correcta en el selector (`/web/database/selector`) o pon su nombre
en el servicio `odoo` o en el parámetro `--database`.

**Restauro y no veo mis datos.** Has cargado el ZIP en otra base con otro
nombre. Mira la lista de bases en `/web/database/manager`.
