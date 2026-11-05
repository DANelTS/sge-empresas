# S18 · CRM y ciclo de venta completo

**Sesión:** jueves 12 de noviembre de 2026 · 2 h
**CE que trabaja:** 3b (formularios) y 3a (manipulación de datos).

## Objetivo

Recorrer entero el camino que hace un pedido en una empresa: del primer
contacto con el cliente al dinero en el banco. Crear la oportunidad en el CRM,
pasar el presupuesto, confirmar el pedido, entregar (a veces a medias), facturar
y cobrar. Al terminar sabes leer en Odoo en qué punto está cada venta.

## Contexto empresarial: cinco documentos, no uno

Cuando alguien vende «un pedido», en realidad pasan cinco cosas distintas, y
cada una la usa una persona diferente:

1. **Oportunidad (CRM).** El comercial huele un negocio: un bar que quiere
   cambiar de proveedor. Todavía no hay nada comprometido, solo una probabilidad.
2. **Presupuesto.** Se pone por escrito qué se ofrece y a qué precio. El cliente
   puede decir que no, y no pasa nada: no hay stock reservado ni factura.
3. **Pedido.** El cliente acepta. Ahora sí hay compromiso: hay que servir y hay
   que cobrar. El almacén recibe la orden de preparar género.
4. **Albarán.** El papel que firma quien recibe. Dice lo que **de verdad** salió
   del almacén, que puede ser menos de lo pedido.
5. **Factura y cobro.** La factura reclama el dinero; el cobro lo cierra. Entre
   una y otro está el **vencimiento**, que es la fecha en la que el dinero debería
   estar.

La gracia del ERP es que los cinco están encadenados: del presupuesto sale el
pedido, del pedido el albarán, del albarán la factura. Si alguien cambia una
cantidad, se ve en toda la cadena. Y cuando el cliente llama preguntando «¿qué
me falta?», la respuesta está en un botón, no en una carpeta.

## Antes de empezar

- Base con maestros importados y `verificar.py` en verde (sesión S17).
- Tu bandeja del día:

  ```powershell
  docker compose run --rm herramientas generar.py --empresa <sector> --alumno <NN>
  ```

  Ábrela en `salida/<sector>-A<NN>/bandejas/s18-ventas.md`.

## Los pasos, sobre el primer suceso de tu bandeja

Los clics son los mismos para todos los sucesos; lo que cambia es el contenido.
No copies el orden de la demo: lee cada mensaje y decide.

### 1. De la llamada a la oportunidad (CRM)

**CRM → Ventas → Mi flujo → Nuevo.**

- *Cliente*: el de la bandeja (escríbelo y elígelo del desplegable; si no
  existe, no lo inventes: dálo de alta en Contactos).
- *Asunto*: el negocio, en una línea («Buffet de desayunos, cambio de proveedor»).
- *Ingreso esperado*: lo que calcules a ojo. Sirve para el pronóstico, no es
  contabilidad.
- *Fecha de cierre*: cuándo crees que se decidirá.

Después **arrastra la tarjeta** por las etapas (*Nuevo → Contactado →
Propuesta → Negociación*) o cambia la etapa en el formulario. Si el cliente dice
que no, la etapa es **Perdido** y hay que escribir el **motivo**: dentro de tres
meses, ese dato es oro para saber por qué se pierde.

### 2. Del CRM al presupuesto

En la oportunidad, botón **Nueva cotización** (o **Ventas → Pedidos →
Presupuestos → Nuevo** y eliges el cliente).

- Añade las líneas: producto, cantidad y precio. Si el cliente tiene tarifa, el
  precio se calcula solo; si no, se toma el de catálogo.
- Comprueba el **impuesto** de cada línea: 21 % o 10 % según el producto, y «B»
  o «S» según sea mercancía o servicio.
- **Enviar por correo** deja el mensaje en cola (no hay servidor de correo en el
  aula). No es un fallo: mira en *Ajustes → Técnico → Correo electrónico*.
- **Confirmar** convierte el presupuesto en pedido. Solo se confirma cuando el
  cliente ha dicho que sí.

### 3. Entrega: total o parcial

**Inventario → Operaciones → Traslados** (o el botón inteligente *Entrega* del
pedido).

- Abre el albarán y pon en cada línea la **cantidad hecha** (la que sale de
  verdad). Si es todo, *Validar* y listo.
- Si es menos, valida igualmente: Odoo pregunta si quieres **crear un albarán
  pendiente** (*backorder*). Di que sí. Quedan dos documentos: uno entregado y
  otro pendiente con el resto.
- Ese albarán pendiente es el que explica la llamada del cliente de la bandeja
  («nos falta género»). No se resuelve «editando» el albarán cerrado: se sirve el
  pendiente.

### 4. Factura

Desde el pedido, **Crear factura**. Ojo a dos opciones:

- **Facturar lo entregado** (política *delivered*): solo lo que ha salido del
  almacén. Es lo correcto cuando hay entregas parciales.
- **Facturar lo pedido**: se factura todo aunque no se haya servido. Solo si se
  ha acordado así.

La factura nace en borrador: revisa fecha, líneas y totales, y **Publicar**
(antes «Confirmar»). Publicar le asigna número correlativo y ya no se puede
editar.

### 5. Cobro

**Facturación → Clientes → Facturas → botón *Registrar pago*.**

- Importe completo → la factura pasa a *Pagada*.
- Importe menor → queda *Parcialmente pagada* y el resto sigue pendiente con su
  vencimiento. Es lo que ha hecho el cliente de la bandeja que transfiere «a
  cuenta».
- La fecha del pago es la del banco, no la de hoy.

### 6. Cuando la factura está mal: rectificativa

**Facturación → Clientes → Facturas → botón *Factura rectificativa***.

La factura original **no se toca**: ya está emitida y presentada. Se emite una
**rectificativa** con el importe corregido, se publica y se concilia con la
original. En la ficha del cliente quedan las dos, y eso es correcto.

## Tu ejercicio

Procesa los sucesos de `s18-ventas.md` **en orden**, dejando cada uno cerrado
antes de pasar al siguiente. Algunos se resuelven en el CRM, otros solo en
Ventas, y uno obliga a rectificar una factura.

Antes de empezar, una copia de seguridad (`copia_seguridad.md`). Si te lías a
mitad, restauras y vuelves a empezar sin miedo.

## Comprueba tu trabajo

Las comprobaciones concretas están al final de tu bandeja. Como norma general:

- [ ] Cada presupuesto está en el estado que toca: *Presupuesto*, *Pedido de
      venta* o *Cancelado*, y los perdidos tienen motivo.
- [ ] Los pedidos facturados del todo aparecen como **Completamente facturado**;
      los que tienen entrega parcial, como **A facturar** si aún queda algo por
      facturar.
- [ ] En los pedidos con entrega parcial hay **dos albaranes**: uno *Hecho* y otro
      *Listo* o *Esperando*.
- [ ] Las facturas publicadas llevan número y fecha coherentes con el orden en
      que las has emitido.
- [ ] Las facturas cobradas a medias siguen con importe pendiente y su
      vencimiento.
- [ ] La factura mal emitida tiene su rectificativa y la original sigue ahí.

## Si algo falla

**«No hay existencias» al validar un albarán.** Odoo permite stock negativo, pero
no debería pasar: si ocurre, mira el producto en *Inventario → Informes → Stock*
y haz un ajuste de inventario explicando el motivo (rotura, merma, recuento).

**He confirmado un presupuesto y el cliente se echa atrás.** No se borra: se
**cancela** el pedido, y si ya hay albarán, se cancela también. Queda el rastro,
que es lo que interesa.

**La factura no me deja publicarla.** Casi siempre es la fecha: no puede ser
anterior a la última factura publicada del mismo diario. Corrige la fecha o
mira el mensaje exacto.

**He facturado lo pedido y solo he entregado la mitad.** Emite una rectificativa
por la parte no entregada, o cancela esa factura si aún es borrador y vuelve a
facturar lo entregado.

**El botón «Crear factura» no aparece.** El pedido no está confirmado, o su
política de facturación es *pedido* y ya está facturado. Mira el estado en la
parte superior derecha del formulario.

Apunta cada incidencia: es material para la memoria (CE 3f).
