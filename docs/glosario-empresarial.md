# Glosario empresarial

Los términos que aparecen en las fichas, en las bandejas de sucesos y en las
pantallas de Odoo, explicados como se usan en una empresa real. Entre paréntesis,
dónde se ven en el ERP.

## El ciclo de venta

**Presupuesto** (Ventas → Pedidos → Presupuestos). Documento que se envía a un
cliente con lo que se le ofrece y a qué precio. **No** compromete nada: ni el
stock, ni la facturación. Caduca solo. En Odoo un presupuesto es un pedido de
venta en estado borrador.

**Pedido de venta** (Ventas → Pedidos). El cliente acepta el presupuesto y eso
pasa a ser un compromiso: hay que servir y hay que cobrar. A partir de aquí el
pedido reserva stock y genera la orden de entrega.

**Albarán** u **orden de entrega** (Inventario → Operaciones → Traslados).
Documento que acompaña a la mercancía y que firma quien la recibe. Dice qué se
entregó **de verdad**, que no siempre es lo que decía el pedido: puede faltar
género. Mientras no se valida, el stock no se mueve.

**Entrega parcial** (en Odoo, *backorder* o pedido pendiente). Cuando se sirve
menos de lo pedido, el albarán se cierra con lo entregado y queda abierto un
albarán pendiente con el resto. El cliente recibe dos entregas y, si se factura
por lo entregado, dos facturas.

**Factura** (Facturación → Clientes → Facturas). Documento que reclama el pago.
Debe llevar numeración correlativa, fecha, datos fiscales de las dos partes,
base imponible, tipo de IVA y total. Una vez emitida **no se modifica**: si hay
un error, se corrige con una rectificativa.

**Factura rectificativa** o **abono** (Facturación → Clientes → Facturas
rectificativas). Documento que corrige una factura anterior: devolución,
descuento posterior, error de precio. Va en negativo (o con signo contrario) y
deja la original como estaba, porque la original ya está presentada.

**Vencimiento** (en la factura, pestaña *Otra información* y en el informe de
facturas). La fecha en que la factura debe estar pagada. «30 días» significa 30
días desde la fecha de factura; «fin del mes siguiente», el último día del mes
siguiente.

**Cobro** (Facturación → Clientes → Pagos). El apunte de que el cliente ha
pagado. En Odoo un cobro se **concilia** con la factura: si el importe coincide,
la factura pasa a *Pagada*; si es menor, queda *Parcialmente pagada*.

**Moroso**. Cliente que no paga en plazo. En el ERP se ve como factura vencida
con importe pendiente. La empresa hace *gestión de cobros*: reclamar, y si no
hay manera, llevar el saldo a incobrable.

## El ciclo de compra

**Solicitud de presupuesto** (Compras → Pedidos). Lo que se pide a un proveedor
para saber precio y plazo. Equivale al presupuesto de venta, pero al revés.

**Pedido de compra**. Compromiso de compra. Genera una **recepción** en el
almacén.

**Recepción** (Inventario → Operaciones → Traslados). La entrada de mercancía.
Se puede recibir parcial: el proveedor sirve la mitad porque no tenía.

**Factura de proveedor** (Facturación → Proveedores → Facturas). Lo que nos
cobra el proveedor. Se compara con lo recibido: si no coincide (falta género,
precio distinto), se reclama antes de pagar.

**Pago**. La salida de dinero. Igual que el cobro, se concilia con la factura.

## Almacén

**Stock** o **existencias**. Unidades disponibles de un producto en una
ubicación.

**Ubicación** (Inventario → Configuración → Gestión de almacenes → Ubicaciones). Dónde está físicamente
la mercancía: el almacén, una estantería, una nave. Odoo distingue ubicaciones
internas, de cliente, de proveedor y virtuales (inventario, producción,
existencias perdidas).

**Ajuste de inventario** o **regularización** (Inventario → Operaciones →
Ajustes). Corregir el stock del sistema para que cuadre con el recuento físico.
Se usa por roturas, mermas, robos o errores de recepción.

**Stock mínimo** y **punto de pedido**. El mínimo es la cantidad por debajo de la
cual no conviene bajar. El punto de pedido añade el consumo durante el plazo de
entrega: si se tarda 10 días en recibir y se venden 2 al día, hay que pedir con
20 unidades por encima del mínimo.

**Regla de reabastecimiento** (Inventario → Operaciones → Abastecimiento). Regla
automática: «si el stock baja de X, propón comprar hasta Y». El planificador la
ejecuta y genera las propuestas de compra.

**Merma**. Pérdida de género que no se vende: planta que se muere, café que se
pasa, botella rota.

**Lote** o **número de serie** (Inventario → Productos → Números de
serie/lote). Identificador de un grupo de unidades fabricadas o recibidas juntas.
Sirve para trazabilidad: saber de qué partida salió lo que se vendió.

## Fiscal

**NIF**. Número de identificación fiscal. Para personas físicas es el DNI con
letra; para sociedades, el CIF (letra de tipo de sociedad + 7 cifras + control).

**Razón social**. El nombre legal de la empresa, el que va en las facturas. No
tiene por qué coincidir con la marca comercial.

**Base imponible**. El importe sobre el que se calcula el impuesto: precio ×
cantidad, menos descuentos.

**IVA repercutido**. El que la empresa cobra a sus clientes. Lo ingresa en
Hacienda, no es suyo.

**IVA soportado**. El que la empresa paga a sus proveedores. Se lo descuenta.

**Liquidación de IVA**. Cada trimestre, la empresa ingresa *repercutido −
soportado* (si sale a favor, compensa o devuelven).

**Tipo general, reducido y superreducido**. En España, 21 %, 10 % y 4 %. Cada
producto tiene el suyo según su naturaleza, no según lo que diga el proveedor.
En Odoo, la localización española crea dos impuestos por cada tipo: «21% B» para
bienes y «21% S» para servicios.

**Recargo de equivalencia**. Régimen especial del comercio minorista: el
comerciante paga el IVA más un recargo y no liquida. Solo afecta a minoristas
personas físicas.

**Operación intracomunitaria**. Compra o venta a otro país de la UE. Va al 0 %
con NIF-IVA del cliente y se declara aparte.

## CRM

**Oportunidad** (CRM → Ventas). Una posible venta con un cliente, con su importe
estimado y su probabilidad. Se mueve por **etapas** (nuevo, contactado,
propuesta, negociación, ganada o perdida).

**Lead** o **cliente potencial**. Contacto que aún no es cliente y del que no se
sabe si hay negocio.

**Tasa de conversión**. De cada 100 oportunidades, cuántas acaban en pedido. Sirve
para saber si el comercial dedica el tiempo a lo que compensa.

## Comercial y financiero

**Tarifa** o **lista de precios** (Ventas → Productos → Listas de precios). El
conjunto de precios aplicables a un cliente. Un cliente con tarifa especial paga
menos que el precio de catálogo.

**Descuento por volumen**. Rebaja que depende de la cantidad pedida o del
volumen anual contratado.

**Portes**. El coste del transporte. Normalmente lo paga el cliente si el pedido
no llega a un mínimo.

**Condiciones de pago**. Plazo y forma: contado, 30 días, 60 días, pagaré,
domiciliación.

**Cuenta a cobrar** (de clientes) y **cuenta a pagar** (de proveedores). El
dinero que te deben y el que debes.

**Margen**. Precio de venta menos coste. En porcentaje, margen sobre venta.

**Rotación**. Cuántas veces se vende y repone el stock en un periodo. Rotación
baja significa dinero dormido en el almacén.

**Deterioro**. Reconocer en contabilidad que un saldo a cobrar probablemente no
se cobrará.

## Del ERP

**Dato maestro**. Información estable que usan todos los documentos: productos,
clientes, proveedores, tarifas. Se da de alta una vez y se reutiliza. Un error
aquí se propaga a todas las facturas.

**Transacción**. Cualquier movimiento que cambia el estado de la empresa: un
pedido, una entrega, una factura. En el ERP, un documento con su ciclo de vida.

**Módulo**. Pieza de software que añade funciones (Ventas, Inventario,
Facturación). Se instala y se desinstala.

**Localización**. El paquete de un país: plan contable, impuestos, modelos de
declaración. La española es `l10n_es`.

**Asiento contable** (Facturación → Contabilidad → Asientos contables). El
registro de una operación en el libro: una cuenta de debe y otra de haber.

**Diario**. El libro donde se anotan los asientos de un tipo: ventas, compras,
banco, caja.

**Conciliación**. Emparejar el movimiento del banco con la factura que
corresponde, para saber qué está pagado y qué no.

**Modo desarrollador** (Ajustes → Activar el modo desarrollador). Muestra menús
técnicos: modelos, campos, vistas, acciones. Se usa a partir de la UD4.
