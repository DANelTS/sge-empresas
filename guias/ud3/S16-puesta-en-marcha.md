# S16 · Puesta en marcha de la empresa

**Sesión:** jueves 5 de noviembre de 2026 · 2 h
**Bloque:** UD3 «Organización y consulta de la información» (RA3)
**CE que trabaja:** preparación del entorno y documentación de incidencias (3f).

## Objetivo

Pasar de un ERP vacío a *tu* empresa montada: base de datos creada, aplicaciones
instaladas, datos fiscales correctos, impuestos españoles revisados y dos
usuarios con permisos distintos. Al terminar la sesión tienes tu primera copia
de seguridad y sabes restaurarla.

## Contexto empresarial: por qué esto va antes de vender

Una empresa no empieza a facturar el día que instala el ERP. Antes tiene que
existir fiscalmente: tiene un **NIF**, una **razón social** (el nombre legal, que
no siempre coincide con la marca comercial), un domicilio fiscal y un régimen de
IVA. Si esos datos están mal, todo lo que salga del sistema estará mal: las
facturas llevarán un NIF que no es, el IVA se calculará con el tipo de otro país
y Hacienda devolverá el envío.

El **IVA repercutido** es el que la empresa cobra a sus clientes en cada factura
y luego ingresa en Hacienda. El **IVA soportado** es el que paga a sus
proveedores. La empresa ingresa la diferencia: repercutido menos soportado. Por
eso el ERP necesita saber, antes de la primera venta, en qué país está, con qué
moneda trabaja y qué impuestos aplica. Odoo no adivina nada de eso: lo instala
la **localización** del país, y esa localización solo se aplica bien si el país
está puesto antes de instalar Facturación.

## Antes de empezar

- Docker Desktop arrancado (el icono de la ballena, en verde).
- Git instalado.
- 4 GB de RAM libres. La primera vez hay que descargar unos 2 GB de imágenes.
- El repositorio clonado y tu `config/odoo.conf` creado a partir del ejemplo.

```powershell
git clone https://github.com/TU-USUARIO/sge-empresas.git
cd sge-empresas
copy config\odoo.conf.example config\odoo.conf
notepad config\odoo.conf
```

Ese fichero trae la conexión con PostgreSQL y la contraseña maestra del gestor de
bases de datos (`admin_passwd`). Para el aula funciona tal cual; si quieres
cambiarla, hazlo ahora y apúntala.

> **En Linux o macOS** el comando de copia es `cp config/odoo.conf.example
> config/odoo.conf`, y los permisos de los volúmenes pueden necesitar `:z` al
> final (SELinux).

## Paso 1 · Arrancar el entorno

```powershell
docker compose up -d
docker compose ps
```

Deben aparecer `sge-db-1` y `sge-odoo-1` en estado `running` (el de base de datos
primero, `healthy`). Abre <http://localhost:8069>: tiene que salir la pantalla de
Odoo, aún sin base de datos.

Si el puerto 8069 está ocupado, cambia el mapeo en `docker-compose.yml`
(`127.0.0.1:8070:8069`) y vuelve a levantar.

## Paso 2 · Crear la base de datos `empresa`

Tienes dos caminos. El **A** es rápido y reproducible; el **B** enseña lo que
hace el gestor por dentro. Haz el A y lee el B.

### Camino A · por línea de comandos (recomendado)

```powershell
docker compose run --rm odoo odoo db init empresa --country ES --language es_ES --username admin --password admin
```

Ese comando crea la base **sin datos de demostración**, con **país España**,
**idioma español** y un usuario `admin` con la contraseña que le indiques.
Tarda menos de un minuto.

Después instala las cinco aplicaciones del módulo:

```powershell
docker compose run --rm odoo odoo module install -d empresa account sale_management purchase stock crm
```

Tarda uno o dos minutos. Cuando termine, recarga <http://localhost:8069> y entra
con `admin` y tu contraseña.

> La contraseña que pongas aquí tiene que coincidir con `admin_passwd` de
> `config/odoo.conf`: los scripts del repositorio la usan para conectarse.

### Camino B · desde la pantalla (para entender qué hemos hecho)

1. Entra en <http://localhost:8069/web/database/manager>.
2. **Crear base de datos**: nombre `empresa`, contraseña la de `admin_passwd`,
   **desmarca** «Cargar datos de demostración».
3. Entra. Ve a **Ajustes → Usuarios y compañías → Compañías**, abre «Mi
   compañía» y pon **País: España**. Guarda.
4. Ahora instala las aplicaciones en **Aplicaciones** (menú superior izquierdo):
   *CRM*, *Ventas*, *Compras*, *Inventario* y *Facturación*.

El orden del punto 3 no es un capricho: si instalas Facturación con la compañía
en Estados Unidos, Odoo carga el plan contable genérico y la moneda USD, y ya no
hay forma limpia de cambiarlo (ver «Si algo falla»).

## Paso 3 · Configurar tu compañía

1. Genera tu variante (si no lo has hecho ya):

   ```powershell
   docker compose run --rm herramientas generar.py --empresa cerveceria --alumno 07
   ```

   Cambia `cerveceria` por el sector que te haya tocado y `07` por tu número de
   lista. Se crea la carpeta `salida/<sector>-A07/`.

2. Abre `salida/<sector>-A07/datos-empresa.md`: ahí están tus datos fiscales.

3. En Odoo: **Ajustes → Usuarios y compañías → Compañías → Mi compañía**.
   Rellena nombre (con tu sufijo `— A07`), NIF, dirección, C.P., ciudad, país,
   teléfono, correo y web. Sube el logo si quieres (Adjuntar).

4. Comprueba **Moneda: EUR**. Si pone USD, para y lee «Si algo falla».

5. Guarda y recarga: el nombre de la compañía tiene que aparecer en la barra
   superior.

**Qué es cada cosa.** La *razón social* es el nombre jurídico; el *nombre
comercial* es el que ve el cliente. El *NIF* identifica a la empresa ante
Hacienda y Odoo lo valida: si el dígito de control no cuadra, no te deja
guardar. El *domicilio fiscal* determina qué administración te corresponde y,
en parte, qué impuestos aplicas.

## Paso 4 · Revisar los impuestos que ha creado la localización

**Facturación → Configuración → Contabilidad → Impuestos**.

Verás decenas de impuestos. Fíjate en los que empiezan por un porcentaje:

| Nombre | Qué es |
|---|---|
| `21% B` | IVA general del 21 % para **bienes** (mercancías). |
| `21% S` | IVA general del 21 % para **servicios**. |
| `10% B` | IVA reducido del 10 % (alimentos elaborados, hostelería). |
| `4% B` | IVA superreducido del 4 % (pan, leche, aceite de oliva…). |
| `0% B` | Operaciones exentas o no sujetas (exportaciones, entregas intracomunitarias). |

La letra final no es decorativa: Odoo distingue el impuesto de un bien del de un
servicio porque las declaraciones se presentan separadas. En la ficha de tu
empresa tienes qué familia de producto lleva cada tipo y por qué.

Abre uno de ellos y mira sus pestañas: **venta** o **compra** (`type_tax_use`),
cuenta contable que usa, y si el impuesto está incluido en el precio
(`price_include`) o se suma.

> **Cuidado con los impuestos «zombi».** La localización trae todavía los tipos
> temporales de 2023 y 2024 (`2% B`, `5% B`, `7.5% B`, `7.5% S`), que ya no
> existen: eran las bajadas temporales del IVA de los alimentos y decayeron. No
> los uses. Si quieres que no molesten, selecciónalos en la lista
> (**Acción → Archivar**) y desaparecen del desplegable. Los tipos válidos en
> noviembre de 2026 son 21 %, 10 %, 4 % y los 0 % de las operaciones exentas.

## Paso 5 · Dos usuarios con permisos distintos

**Ajustes → Usuarios y compañías → Usuarios → Nuevo.**

1. **Comercial**: nombre «Comercial — A07», correo, y en *Derechos de acceso*
   marca:
   - **Ventas**: «Usuario: Mostrar todos los documentos».
   - **Facturación**: «Facturación».
   Deja *Inventario* sin marcar: un comercial no debe tocar el almacén.

2. **Almacén**: nombre «Almacén — A07», y marca solo **Inventario: Usuario**.

Guarda y comprueba entrando con cada uno (cierra sesión o abre una ventana de
incógnito). El comercial no debe ver el menú *Inventario*; el de almacén no debe
poder crear facturas.

**Por qué se hace así.** En una empresa real nadie tiene todos los permisos: el
comercial no debe poder cambiar el stock y el de almacén no debe emitir facturas.
Los permisos en Odoo son *grupos*; cada grupo abre menús y permite acciones. Dar
de más es un riesgo (y un suspenso en la UD2).

## Paso 6 · Tu primera copia de seguridad

Sigue `herramientas/copia_seguridad.md`. En resumen:

```powershell
docker compose exec odoo odoo db dump empresa /copias/copia-S16.zip
```

Guarda ese ZIP fuera del repositorio (por ejemplo en tu carpeta de clase) y
apunta en tu cuaderno de incidencias la hora y el tamaño. Lo vas a necesitar en
la S22.

## Comprueba tu trabajo

- [ ] `docker compose ps` muestra los dos servicios en marcha.
- [ ] La base se llama `empresa` y **no** tiene datos de demostración (no
      aparecen clientes ni productos de ejemplo).
- [ ] En **Ajustes → Compañías** el nombre lleva tu sufijo `— ANN`, el NIF es el
      de `datos-empresa.md` y la moneda es **EUR**.
- [ ] En **Facturación → Configuración → Contabilidad → Impuestos** existen
      `21% B`, `21% S`, `10% B` y `4% B`.
- [ ] Existen los usuarios *Comercial* y *Almacén*, y cada uno ve solo lo suyo.
- [ ] Tienes `salida/copia-S16.zip` y sabes cuánto pesa.

## Si algo falla

**1. `docker compose up` se queda en «starting» y Odoo no responde.**
Mira el registro: `docker compose logs -f odoo`. Casi siempre es que PostgreSQL
todavía no acepta conexiones; espera un minuto. Si dice
`password authentication failed`, la contraseña de `odoo.conf` no coincide con la que
se usó al crear el volumen: `docker compose down -v` y empieza de cero (perderás
la base).

**2. El puerto 8069 está ocupado.**
Cambia el mapeo a `127.0.0.1:8070:8069` en `docker-compose.yml`, `docker compose down` y `up -d`.

**3. La moneda es USD y los impuestos son «15%» y «0% Exports».**
Instalaste Facturación antes de poner el país. No se arregla desde la interfaz:
crea la base otra vez con el Paso 2 camino A (`--country ES`). Es más rápido que
perseguirlo.

**4. Odoo rechaza el NIF.**
El NIF de tu variante lo genera el repositorio con dígito de control válido. Si
lo has tecleado a mano, copia y pega desde `datos-empresa.md`. Ojo con la letra
final: la `O` no existe, es un cero.

**5. `docker compose run --rm herramientas ...` no encuentra el comando.**
Escribe `docker compose run --rm herramientas` y el nombre del script sin ruta
(`generar.py`, no `herramientas/generar.py`). Si sale «permission denied» en
Linux, añade `:z` al volumen del compose.

**6. «No se puede conectar con la base de datos» al crear la base.**
La base de datos aún no está lista: `docker compose up -d db`, espera a que
`docker compose ps` diga `healthy` y repite.

Apunta cada incidencia y cómo la resolviste: es material directo para la memoria
del trabajo personal (CE 3f).
