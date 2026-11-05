# Decisiones técnicas y trampas de Odoo 19

Este documento recoge **por qué** el repositorio está montado así y qué cosas de
Odoo 19 se comportan de forma distinta a como cuentan la mayoría de los
tutoriales. Todo lo que aparece aquí se ha comprobado sobre una instancia real
(`odoo:19.0`, compilación 20261102) con PostgreSQL 17, no de memoria.

## 1. Imágenes: `odoo:19.0` oficial, PostgreSQL 17

- **Odoo**: imagen oficial `odoo:19.0`. Se decidió dejarla «flotante» (sin fijar
  la fecha de compilación) para que el alumnado reciba las correcciones de Odoo
  sin tocar el compose. Contrapartida: dos alumnos que arranquen en fechas
  distintas pueden tener compilaciones distintas. Si alguna vez hay que blindar
  la reproducibilidad, basta con cambiar la etiqueta por una con fecha
  (`odoo:19.0-20261102`) o por el digest.
- **PostgreSQL 17**: Odoo 19 exige PostgreSQL 13 o superior (antes era 12).
  Se fija la **versión mayor** (`postgres:17`) para que las actualizaciones
  menores de seguridad entren solas sin cambiar el motor.
- La imagen oficial incluye **wkhtmltopdf 0.12.6.1** (informes PDF), `psql` y un
  Python 3.12 con las dependencias de Odoo. Por eso no hace falta construir nada
  para la UD3: el PDF de facturas y albaranes funciona de serie.
- No se usa Odoo Enterprise ni OCA `l10n-spain`: la localización española de
  serie (`l10n_es`) ya trae el plan contable de pymes, los impuestos y la
  validación de NIF. Los módulos OCA hacen falta para SII, Veri*factu y
  Facturae con requisitos de producción, que no son el objetivo del módulo.

## 2. La contraseña maestra ya no se pasa por línea de comandos

En Odoo 18 se podía arrancar con `--admin-passwd`. **En la 19 esa opción no
existe**: si se pasa, el servidor ni arranca (`no such option: --admin-passwd`).
La contraseña maestra del gestor de bases de datos solo se lee del fichero de
configuración (`admin_passwd`).

Solución: `docker/entrada.sh`. Genera `/tmp/odoo.conf` a partir de
`config/odoo.conf` sustituyendo las marcas `@DB_PASSWORD@` y `@ADMIN_PASSWD@`
por lo que venga de `.env`, y luego delega en el script de arranque de la
imagen. Así no hay contraseñas en el repositorio y el `.env` sigue siendo el
único sitio donde se tocan.

## 3. La 19 estrenó subórdenes en la línea de comandos

`odoo --help` ya no lista opciones sueltas sino órdenes:

```
odoo server ...     arranca el servidor (es la orden por defecto)
odoo shell ...      consola de Python con el ORM cargado
odoo db ...         init | load | dump | duplicate | rename | drop
odoo module ...     install | upgrade | uninstall
odoo i18n ...       idiomas y traducciones
```

Dos consecuencias prácticas, muy útiles:

- **Crear la base de datos desde la línea de comandos**, con país e idioma:

  ```
  docker compose run --rm odoo db init empresa --country ES --language es_ES --password admin
  ```

- **Copias de seguridad conscientes del filestore** (el adjunto de los logos y
  de los PDF), sin pasar por la interfaz:

  ```
  docker compose run --rm odoo db dump empresa /repo/salida/copia.zip
  docker compose run --rm odoo db load empresa /repo/salida/copia.zip --force
  ```

`--without-demo` también cambió: en la 19 es un booleano. `--without-demo=all`
(como se ve en mil artículos) provoca un aviso y se interpreta como `True`; lo
correcto es `--without-demo`.

## 4. El orden importa: país antes de Facturación

Si se instala **Facturación** con la compañía en Estados Unidos (el valor por
defecto), Odoo carga el plan contable genérico y la moneda **USD**. Instalar
después `l10n_es` **no** cambia nada: el plan ya está cargado y la compañía no
se migra sola. Comprobado: 4 impuestos, 51 cuentas, moneda USD.

El orden correcto (y el que siguen las guías) es:

1. Crear la base con `--country ES --language es_ES` (o poner el país a mano en
   *Ajustes → Compañías* **antes** de instalar nada más).
2. Instalar Facturación. Ahora sí: plan `es_pymes`, 646 cuentas, 168 impuestos,
   moneda EUR.

Si alguien se equivoca, la salida limpia es borrar la base y repetir. Queda
documentado en el apartado «Si algo falla» de la guía S16.

## 5. Los impuestos españoles se llaman «21% B» y «21% S»

La localización crea **dos impuestos por tipo**: «21% B» para bienes y «21% S»
para servicios (en inglés, *G* de *goods* y *S*). Tienen el mismo importe y el
mismo nombre visible salvo la letra final.

Consecuencia para la importación de productos: si el CSV trae una columna
`taxes_id` con el valor «21% B», el importador busca por nombre y encuentra
**dos** registros (el de venta y el de compra), avisa de la ambigüedad y asigna
lo que le parece o deja la celda vacía. Comprobado: unos productos quedaban con
impuesto de venta y otros con el de compra, sin criterio.

Por eso **el CSV de productos no lleva impuestos**: los asigna
`cargar_historico.py` por importe y por tipo, buscando en `account.tax` y
eligiendo la terminación `B`/`S` según sea mercancía o servicio. `verificar.py`
lo comprueba después.

## 6. Las provincias se llaman como dice el INE, en bilingüe

Odoo 19 nombra las provincias con las dos denominaciones oficiales:
«Alacant (Alicante)», «València (Valencia)», «Bizkaia (Vizcaya)», «Araba/Álava»,
«A Coruña (La Coruña)», «Ourense (Orense)»… Si el CSV pone «Valencia», el
importador no encuentra la provincia y rechaza la fila.

`herramientas/sge/provincias.py` traduce el nombre corto al que espera Odoo.

## 7. Odoo valida los NIF de verdad

El módulo `base_vat` (que se instala con la localización) comprueba el dígito de
control. Un CIF inventado como `B12345678` se rechaza con
«Parece que el número NIF no es válido». Por eso todos los documentos del
repositorio se generan con `sge/nif.py`, que calcula el dígito correcto (y
también el IBAN).

Efecto colateral útil: los NIF ficticios son válidos de formato pero no
existen, y Odoo los guarda con el prefijo del país (`ESB43331511`).

## 8. La API externa: XML-RPC sigue vivo, JSON-2 es el futuro

- **XML-RPC** (`/xmlrpc/2`) **funciona en la 19** (comprobado: `version`,
  `authenticate`, `execute_kw`). Odoo lo marca como obsoleto y lo retirará en la
  **22**. Cada llamada deja un aviso en el registro.
- **JSON-2** (`/json/2/<modelo>/<método>`) es la API nueva. Necesita una **clave
  de API** creada en *Mi perfil → Seguridad de la cuenta → Nueva clave de API* y
  se llama con `Authorization: bearer <clave>` y la cabecera
  `X-Odoo-Database`. Los argumentos van por nombre (`{"ids": [...], "vals": {...}}`),
  no por posición.

Decisión: `herramientas/odoo_api.py` encapsula el transporte y usa **XML-RPC
por defecto** (se autentica con usuario y contraseña, sin crear nada), con
`--transporte json2` disponible para la UD5, donde se enseñará la API nueva.
Todo el repositorio habla con Odoo a través de esa clase: cambiar de transporte
es cambiar una línea.

## 9. Detalles del ORM que afectan a la carga del histórico

Comprobados en la 19 y usados en `cargar_historico.py`:

- **Almacenable** es `type='consu'` **con** `is_storable=True`. El antiguo
  `type='product'` ya no existe.
- `standard_price` (el coste) no es una columna de `product_template`: vive en
  `product_product` y se guarda por compañía (`{"1": 8.4}`).
- Las **cantidades hechas** de un albarán se ponen en `stock.move.quantity` y se
  marcan con `picked=True` antes de `button_validate()`.
- `sale.order` **no** tiene un método público para facturar: se usa el asistente
  `sale.advance.payment.inv` con `advance_payment_method='delivered'`, que es lo
  que hace el botón «Crear factura» de la interfaz.
- `purchase.order` sí tiene `action_create_invoice()`.
- Los **cobros** se registran con el asistente `account.payment.register`
  (contexto `active_model='account.move'`, `active_ids=[factura]`), que además
  concilia el pago con la factura.
- Al **confirmar** un pedido, Odoo reescribe `date_order` con la fecha actual:
  hay que volver a escribir la fecha histórica después de confirmar.

## 10. El importador: la columna `id` crea identificadores `__import__`

Si el CSV lleva una columna `id`, cada registro queda registrado en
`ir_model_data` como `__import__.<valor>` (por ejemplo
`__import__.prod-TOS-010`). Eso permite que los scripts encuentren los datos del
alumno sin depender de la base de datos concreta, y que dos importaciones
distintas no dupliquen registros.

Detalle de la 19 que solo afecta a quien automatice importaciones por RPC: el
campo binario `base_import.import.file` espera el **texto del CSV tal cual**, no
en base64 como en versiones anteriores. Por eso las pruebas automáticas del
repositorio hacen el `create` por XML-RPC con el texto y la ejecución por
JSON-RPC.

## 11. Sin servidor de correo

No hay SMTP. Las acciones «Enviar por correo» dejan el mensaje en la cola de
`mail.mail` en estado `exception` o `outgoing`. No es un fallo: está explicado en
las guías para que nadie pierda la mañana buscando el problema.

## 12. Dos bloqueos de la 19 que aparecen al automatizar

Ninguno de los dos se ve en los tutoriales, y los dos paran la carga a mitad:

- **Confirmación de entrega por SMS.** Si el contacto del albarán tiene teléfono,
  `button_validate()` no valida: devuelve el asistente `confirm.stock.sms`, que
  espera un código enviado por SMS. En el aula no hay pasarela de SMS. La salida
  está en el propio código de Odoo: llamar a `button_validate()` con
  `context={'skip_sms': True}`.
- **Cuenta bancaria «no verificada».** Desde la 19, una factura de cliente no se
  puede confirmar si la cuenta bancaria de la empresa no está marcada como
  verificada (`res.partner.bank.allow_out_payment`). El aviso habla de «haz clic
  en Enviar dinero para validarla», que no es lo que uno espera al importar. Al
  crear la cuenta de la empresa hay que poner ese campo a `True`.

## 13. Nada de `type='product'`

En la 19 un producto almacenable es `type='consu'` **con** `is_storable=True`.
Filtrar por `type == 'product'` (como se hacía en la 15) devuelve cero
resultados y el script sigue adelante **sin dar error**: es exactamente el fallo
que dejó dieciséis productos con stock negativo en la primera prueba de la carga
del histórico. Si algo «no hace nada» con productos, mira ese filtro.
