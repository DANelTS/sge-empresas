# sge-empresas

Entorno de trabajo y datos de las empresas ficticias del módulo **Sistemas de
Gestión Empresarial** (0491) de 2.º de DAM — IES Pío Baroja.

Cada alumno lleva **su propia empresa**: un ERP Odoo 19 con sus productos,
clientes, proveedores, tres meses de histórico y una bandeja de sucesos que hay
que ir resolviendo. Este repositorio pone el entorno, los datos y las guías.

> Todos los datos son ficticios: empresas, personas, NIF, direcciones y correos.
> Los NIF son válidos de formato (dígito de control correcto) para que Odoo los
> acepte, pero no existen.

## Lo que necesitas

- **Docker Desktop** en marcha (Windows o macOS) o Docker Engine (Linux).
- **Git**.
- 4 GB de RAM libres y unos 4 GB de disco la primera vez.
- No hace falta Python, ni PostgreSQL, ni Odoo instalados en tu equipo: todo
  corre en contenedores.

## Puesta en marcha (5 minutos)

```powershell
git clone https://github.com/TU-USUARIO/sge-empresas.git
cd sge-empresas
copy .env.example .env
notepad .env
docker compose up -d
```

En `.env` cambia las dos contraseñas (sin espacios, sin `#`, sin `$`). Después:

```powershell
docker compose run --rm odoo db init empresa --country ES --language es_ES --username admin --password admin
docker compose run --rm odoo module install -d empresa account sale_management purchase stock crm
```

Abre <http://localhost:8069>, entra con `admin` y la contraseña que hayas puesto
y sigue la guía de la sesión: `guias/ud3/S16-puesta-en-marcha.md`.

> La contraseña de `admin` tiene que ser la misma que `ODOO_CLAVE` en `.env`.

## Elige tu empresa y genera tu variante

Las empresas están en `empresas/`. Cada una es un sector distinto; en el Aula
Virtual se publica qué sector le toca a cada número de lista (máximo 5 alumnos
por sector).

| Carpeta | Empresa | Sector |
|---|---|---|
| `_demo-tostadero` | Tostadero Manzanares | Café tostado (solo la usa el profesor) |
| `cerveceria` | Cervecera Lúpulo Norte | Cerveza artesanal |
| `bicicletas` | Ciclos Rodadura | Tiendas y taller de bicicletas |
| `oficina` | Suministros Ofimat | Material de oficina |
| `aceite` | Cooperativa Olivar del Tajo | Aceite de oliva |
| `vivero` | Vivero La Fresneda | Centro de jardinería |

Genera tu variante con tu número de lista:

```powershell
docker compose run --rm herramientas generar.py --empresa cerveceria --alumno 07
```

Se crea `salida/cerveceria-A07/` con:

- `FICHA.md` — tu empresa explicada, y tus datos fiscales al final.
- `datos-empresa.md` — lo que hay que teclear en Odoo.
- `maestros/*.csv` — los CSV que importas en Odoo (en orden, lo dice `LEEME.md`).
- `resumen.json` — los mismos datos en crudo (lo usa el profesor para corregir).

La misma pareja (empresa, alumno) genera **siempre los mismos números**. Si
borras la carpeta y vuelves a ejecutar, sale idéntica.

La variante `00` es la canónica: la que se usa en las demostraciones y en las
pruebas automáticas del repositorio.

## Los tres comandos del día a día

```powershell
docker compose run --rm herramientas generar.py --empresa <sector> --alumno <NN>
docker compose run --rm herramientas cargar_historico.py --empresa <sector> --alumno <NN>
docker compose run --rm herramientas verificar.py --empresa <sector> --alumno <NN>
```

`generar.py` crea los datos; `cargar_historico.py` los mete en Odoo (impuestos,
stock inicial, compras, ventas, facturas y cobros); `verificar.py` dice en verde
y rojo qué está bien y qué falta. Añade `--seco` a los dos primeros para ver qué
harían sin tocar nada.

## Estructura del repositorio

```
sge-empresas/
├── docker-compose.yml        Odoo 19 + PostgreSQL 17 + servicio de herramientas
├── config/odoo.conf          configuración de Odoo (plantilla)
├── docker/entrada.sh         genera la configuración desde .env al arrancar
├── herramientas/             scripts en Python (corren en contenedor)
│   ├── generar.py            datos maestros y documentos de una variante
│   ├── cargar_historico.py   histórico en Odoo por API
│   ├── verificar.py          lista de comprobación
│   ├── configurar_compania.py  (solo profesor) monta la compañía por API
│   ├── odoo_api.py           cliente de la API de Odoo
│   └── sge/                  generación de datos (NIF, catálogo, variantes...)
├── empresas/<sector>/        catálogo, bolsa de nombres y FICHA de cada empresa
├── guias/ud3/                guías de las sesiones
├── docs/                     glosario, modelo de datos, decisiones técnicas
├── sql/ejemplos/             consultas de ejemplo
└── salida/                   aquí se generan las variantes y las copias (no se sube)
```

## Cosas que conviene saber

- **Odoo 19 Community**: no hay contabilidad completa, ni Studio, ni nada de
  Enterprise. Ningún material depende de esas funciones.
- **Sin servidor de correo**: los «Enviar por correo» dejan el mensaje en cola.
  No es un fallo.
- **Las copias de seguridad** incluyen el filestore (logos y PDF):
  `docker compose run --rm odoo db dump empresa /repo/salida/copia.zip`. Ver
  `herramientas/copia_seguridad.md`.
- **Los datos se guardan en volúmenes**: `docker compose down` los conserva;
  `docker compose down -v` los borra.

## Si algo no arranca

1. `docker compose ps` — ¿están los dos servicios en marcha?
2. `docker compose logs --tail 50 odoo` — el error suele estar en las últimas líneas.
3. `docker compose down` y `docker compose up -d` — reinicio limpio, sin perder datos.
4. Si el puerto 8069 está ocupado: cambia `ODOO_PUERTO=8070` en `.env`.

Los problemas concretos de cada sesión están en el apartado «Si algo falla» de su
guía.

## Documentación

- `docs/decisiones-tecnicas.md` — por qué el entorno está montado así y qué
  cambia en Odoo 19 respecto a los tutoriales que hay por internet.
- `docs/glosario-empresarial.md` — presupuesto, albarán, factura, vencimiento,
  IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL hay detrás de cada pantalla.
