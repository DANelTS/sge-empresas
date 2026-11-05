# Modelo de datos de Odoo 19 (lo que se ve en la UD3)

Las pantallas de Odoo son vistas sobre **tablas de PostgreSQL**. Este documento
recoge las que se usan en la UD3, con los nombres de columna comprobados en la
19, para poder consultarlas con SQL desde psql o DBeaver.

## Cómo guarda las cosas Odoo

| Concepto | En PostgreSQL | Consecuencia al consultar |
|---|---|---|
| Modelo | Una tabla con el nombre en singular (`sale.order` → `sale_order`) | Los nombres llevan guion bajo |
| Campo many2one | Columna `<campo>_id` con el id del registro | Hay que hacer `JOIN` para ver el nombre |
| Campos traducidos | Columna `jsonb` (`name`, `street`…) con un valor por idioma | `name->>'es_ES'` |
| Dinero | `numeric` con 2 decimales, en la moneda de la compañía | `SUM()` sin problemas de coma flotante |
| Fechas | `timestamp without time zone`, **en UTC** | Verano: +2 h respecto a Madrid |
| Selecciones | `varchar` con la clave (`sale`, `posted`, `out_invoice`) | No se filtra por la etiqueta en español |

Los identificadores externos (`__import__.prod-TOS-010`) viven en `ir_model_data`,
que es la tabla que permite encontrar un registro por su `id` de importación.

## Las tablas que se usan

### Contactos — `res_partner`

Clientes, proveedores y la propia empresa (cada compañía es también un
`res_partner`).

| Columna | Qué es |
|---|---|
| `id` | Identificador interno. |
| `name` | Nombre. |
| `is_company` | `true` empresa, `false` particular. |
| `vat` | NIF, guardado con prefijo del país (`ESB43331511`). |
| `ref` | Referencia interna (`CLI-01`). |
| `street`, `zip`, `city`, `state_id`, `country_id` | Dirección. `state_id` apunta a `res_country_state`. |
| `customer_rank`, `supplier_rank` | Si es cliente o proveedor (0 o mayor que 0). |
| `property_payment_term_id` | Condición de pago de cliente. |

### Productos — `product_template` y `product_product`

Odoo separa la **plantilla** (lo que describes) de la **variante** (lo que se
mueve en el almacén). Un producto sin atributos tiene una sola variante, pero el
stock y el coste viven siempre en `product_product`.

| Tabla | Columnas que importan |
|---|---|
| `product_template` | `name` (jsonb), `default_code` (referencia), `categ_id`, `list_price` (precio de venta), `type` (`consu` o `service`), `is_storable`, `sale_ok`, `purchase_ok` |
| `product_product` | `product_tmpl_id`, `default_code`, `standard_price` (coste, **jsonb por compañía**: `standard_price->>'1'`), `barcode` |
| `product_category` | `name` (texto, no traducible), `parent_id` |

> En la 19 un producto almacenable es `type='consu'` **con** `is_storable=true`.
> Buscar `type='product'` (como en versiones antiguas) no devuelve nada.

### Ventas — `sale_order` y `sale_order_line`

| Columna | Qué es |
|---|---|
| `name` | Número del pedido (`S00042`). |
| `state` | `draft` (presupuesto), `sent`, `sale` (pedido), `done`, `cancel`. |
| `partner_id` | Cliente. |
| `date_order` | Fecha del pedido (UTC). |
| `invoice_status` | `to invoice`, `invoiced`, `upselling`, `no`. |
| `amount_untaxed`, `amount_tax`, `amount_total` | Bases e importes. |
| `pricelist_id` | Tarifa aplicada. |
| `sale_order_line` | `order_id`, `product_id`, `product_uom_qty` (pedido), `qty_delivered` (entregado), `qty_invoiced` (facturado), `price_unit`, `discount`, `price_subtotal`. |

### Compras — `purchase_order`

`name`, `partner_id`, `state` (`draft`, `sent`, `purchase`, `done`, `cancel`),
`date_order`, `amount_total`, `invoice_status`, `receipt_status` (si está
recibido del todo).

### Almacén — `stock_quant`, `stock_move`, `stock_location`

| Tabla | Qué es |
|---|---|
| `stock_quant` | **Stock actual**: una fila por producto y ubicación. `quantity` (físico), `reserved_quantity` (reservado). Disponible = `quantity - reserved_quantity`. |
| `stock_move` | Cada movimiento: entrada, salida o traspaso. `product_id`, `location_id` (origen), `location_dest_id` (destino), `quantity` (hecho), `product_uom_qty` (pedido), `state` (`done` para los hechos), `date`. |
| `stock_location` | Ubicaciones. `usage`: `internal` (almacén), `supplier`, `customer`, `inventory` (ajustes), `production`. |
| `stock_warehouse_orderpoint` | Reglas de reabastecimiento: `product_id`, `location_id`, `product_min_qty`, `product_max_qty`, `qty_to_order_computed`. |

El stock de un producto **no** es una columna: es la suma de sus quants en
ubicaciones internas. Y un albarán (`stock_picking`) agrupa varios `stock_move`.

### Facturación — `account_move` y `account_move_line`

Una factura es un `account_move`; sus líneas, `account_move_line`.

| Columna | Qué es |
|---|---|
| `move_type` | `out_invoice` (factura de cliente), `out_refund` (rectificativa), `in_invoice` (proveedor), `in_refund`, `entry` (asiento). |
| `state` | `draft`, `posted`, `cancel`. Solo cuentan las `posted`. |
| `name` | Número de factura. En borrador es `/`. |
| `invoice_date` | Fecha de la factura. |
| `invoice_date_due` | **Vencimiento**. |
| `payment_state` | `not_paid`, `partial`, `paid`, `in_payment`, `reversed`. |
| `amount_total`, `amount_residual` | Total y lo que queda pendiente. |
| `partner_id` | Cliente o proveedor. |
| `reversed_entry_id` | Si es rectificativa, la factura original. |

En `account_move_line`: `move_id`, `account_id`, `product_id`, `quantity`,
`price_unit`, `discount`, `price_subtotal`, `balance` (debe/haber),
`date_maturity` (vencimiento de la línea) y `display_type` (`product`,
`payment_term`, `tax`…).

### CRM — `crm_lead`

`name`, `partner_id`, `stage_id` (etapa), `expected_revenue`, `probability`,
`type` (`opportunity` o `lead`), `active`, `lost_reason_id`, `date_closed`.

Las etapas están en `crm_stage` (`name`, `sequence`, `is_won`).

## Relaciones, en una línea

```
res_partner ──< sale_order ──< sale_order_line >── product_product
     │              └──< stock_picking ──< stock_move >── stock_location
     │              └──< account_move ──< account_move_line
     └──< purchase_order ──< purchase_order_line >── product_product
product_product >── stock_quant >── stock_location
crm_lead ──> res_partner
```

## Consultas de ejemplo

Están en `sql/ejemplos/`, listas para pegar en psql o DBeaver. Todas son de
**lectura**: nunca se hace `UPDATE` ni `DELETE` a mano sobre una base de Odoo.

1. `01-ventas-por-cliente.sql` — facturación por cliente en un periodo.
2. `02-facturas-pendientes.sql` — quién nos debe dinero y cuándo vencía.
3. `03-stock-bajo-minimo.sql` — qué hay que reponer.
4. `04-stock-por-producto.sql` — existencias disponibles por producto.

## Tres trampas al consultar

1. **Las fechas están en UTC.** Un pedido de las 23:30 del 30 de septiembre en
   Madrid es del 30 a las 21:30 UTC; uno de la 01:00 del 1 de octubre es del 30 a
   las 23:00 UTC. Para informes por mes, conviene filtrar por
   `date_order AT TIME ZONE 'Europe/Madrid'`.
2. **Los borradores no son ventas.** Filtra `state = 'sale'` en pedidos y
   `state = 'posted'` en facturas, o contarás presupuestos como ingresos.
3. **El stock es la suma de quants**, no una columna del producto. Y ojo con
   `reserved_quantity`: lo reservado está en el almacén pero comprometido con un
   pedido.
