# S20 · Consultas, informes y exportación

**Sesión:** jueves 19 de noviembre de 2026 · 2 h
**CE que trabaja:** 3a (consultas), 3c (informes) y 3d (exportación).

## Objetivo

Sacar información del ERP por dos caminos: las vistas de Odoo (filtrar, agrupar,
pivote, gráfico, informes PDF, exportar) y SQL sobre PostgreSQL. Al terminar
sabes responder preguntas de dirección con datos y adjuntar la prueba.

## Contexto empresarial: qué pregunta de verdad una dirección

Un ERP no se consulta por curiosidad. Las preguntas que se hacen en un comité de
dirección son siempre las mismas cuatro o cinco:

- **¿Quién nos compra?** Y de esos, ¿quiénes son los que de verdad sostienen la
  facturación? Casi siempre el 20 % de los clientes hace el 80 % de la venta.
- **¿Qué se vende?** Qué familias crecen, cuáles se caen, qué producto tiene
  margen y cuál se vende solo por acompañar.
- **¿Quién nos debe?** Cuánto, desde cuándo y a quién hay que llamar hoy.
- **¿Qué hay que reponer?** Qué se va a quedar sin stock antes de que llegue el
  siguiente pedido.
- **¿Con quién trabajamos?** Qué proveedor cumple plazos y cuál nos está
  encareciendo la compra.

Ninguna de esas preguntas se responde «mirando pantallas». Se responde con un
filtro guardado, un pivote o una consulta que se puede repetir el mes que viene.

## Bloque 1 · Vistas, filtros e informes

### Filtrar y agrupar (2 minutos)

En cualquier lista (**Ventas → Pedidos**, **Facturación → Clientes → Facturas**…):

- **Barra de búsqueda**: escribe `Madrid` y filtra por lo que contenga. Los
  desplegables que aparecen permiten filtrar por *Cliente*, *Vendedor*, *Fecha*…
- **Filtros**: *Añadir filtro personalizado* permite combinaciones
  (`Fecha de factura es septiembre` **y** `Estado es publicado`).
- **Agrupar por**: agrupa las filas por cliente, por mes, por producto. Es la
  forma más rápida de responder «cuánto por cliente» sin escribir SQL.
- **Favoritos**: *Guardar búsqueda actual* deja el filtro con nombre y aparece en
  el desplegable. Eso es lo que usa una empresa para que el informe sea el mismo
  todos los meses.

### Pivote y gráfico

Arriba a la derecha de la lista hay iconos para cambiar de vista: lista, kanban,
**gráfico** y **pivote**. El pivote es una tabla dinámica: arrastra *Cliente* a
filas y *Total* a medidas, y agrupa por mes en columnas. El gráfico sirve para lo
mismo, pero mirando tendencias.

### Informes PDF

- **Factura**: abre una factura publicada → **Imprimir → Factura**. Es el PDF que
  se envía al cliente, con los datos fiscales de las dos partes.
- **Albarán**: desde el traslado, **Imprimir → Albarán de entrega**.
- Informes de fábrica: **Facturación → Informes → Impuestos y fiscalidad**,
  **Ventas → Informes → Ventas**, **Inventario → Informes → Stock**.

### Exportar

En cualquier lista: **Acción → Exportar** (o el icono de exportar). Elige los
campos, el formato (XLSX o CSV) y exporta. Lo exportado respeta filtros y
agrupaciones: si has filtrado septiembre, exportas septiembre.

## Bloque 2 · SQL sobre PostgreSQL

Odoo guarda todo en PostgreSQL. Se puede consultar **en paralelo**, sin tocar la
interfaz, pero **solo para leer**: un `UPDATE` a mano rompe el ERP.

### Conectarse

**Opción A, desde el contenedor** (no hace falta instalar nada):

```powershell
docker compose exec db psql -U odoo -d empresa
```

**Opción B, DBeaver o pgAdmin** desde tu equipo:

- Host `localhost`, puerto `5433` (el que publica el compose), base `empresa`,
  usuario `odoo`, contraseña `odoo`.

### Primeras consultas

```sql
-- ¿Cuántos clientes tengo?
SELECT count(*) FROM res_partner WHERE customer_rank > 0;

-- Facturación por mes
SELECT date_trunc('month', invoice_date) AS mes,
       count(*)                          AS facturas,
       round(sum(amount_total), 2)       AS total
FROM account_move
WHERE move_type = 'out_invoice' AND state = 'posted'
GROUP BY 1 ORDER BY 1;

-- Ventas por cliente (con JOIN)
SELECT p.name                            AS cliente,
       round(sum(m.amount_untaxed), 2)   AS base
FROM account_move m
JOIN res_partner p ON p.id = m.partner_id
WHERE m.move_type = 'out_invoice' AND m.state = 'posted'
GROUP BY p.name
ORDER BY base DESC;
```

En `docs/modelo-de-datos.md` están las tablas, las columnas y las tres trampas
(fechas en UTC, borradores que no son ventas, stock como suma de quants). En
`sql/ejemplos/` hay cuatro consultas listas para pegar.

### Los JOIN que hay que saber

```sql
-- pedido → líneas → producto
FROM sale_order o
JOIN sale_order_line l ON l.order_id = o.id
JOIN product_product  pp ON pp.id = l.product_id
JOIN product_template pt ON pt.id = pp.product_tmpl_id

-- factura → líneas
FROM account_move m
JOIN account_move_line a ON a.move_id = m.id

-- stock por producto
FROM stock_quant q
JOIN product_product pp ON pp.id = q.product_id
JOIN stock_location l ON l.id = q.location_id AND l.usage = 'internal'
```

## Tu ejercicio

Responde el cuestionario de `guias/ud3/S20-cuestionario.md`. Son diez preguntas
sobre **tu** empresa: unas se resuelven con vistas, otras con SQL, y dos piden
exportar el resultado.

Para cada respuesta entrega:

1. La respuesta (un número o una lista corta).
2. **Cómo la has obtenido**: captura de la vista con el filtro visible, o el SQL
   completo.
3. En las de SQL, el resultado tal cual sale de psql.

## Comprueba tu trabajo

- [ ] Cada respuesta lleva su prueba: captura o consulta.
- [ ] Las consultas filtran por `state = 'posted'` (facturas) o `state = 'sale'`
      (pedidos). Si no, estás contando borradores.
- [ ] Los importes cuadran con lo que ves en la interfaz para el mismo periodo.
- [ ] Las dos exportaciones están en el formato pedido y con las columnas pedidas.
- [ ] Sabes explicar qué hace cada JOIN de tu consulta, no solo que funciona.

## Si algo falla

**`psql: FATAL: database "empresa" does not exist`.** Estás en otra base o el
nombre está mal. `docker compose exec db psql -U odoo -l` lista las bases.

**El puerto 5433 está ocupado.** Cambia el mapeo de `db` en `docker-compose.yml` y reinicia.

**Los números de SQL no coinciden con la interfaz.** Casi siempre es una de tres:
borradores contados, fechas en UTC (un pedido del día 1 a las 00:30 en Madrid es
del día 30 en UTC) o una factura rectificativa que resta.

**La vista pivote no me deja arrastrar.** Tienes que estar en el modo pivote
(icono de tabla), no en lista. Y algunas medidas solo aparecen si la lista tiene
esos campos.

**Exporto y salen vacías las columnas de importes.** Estás exportando el modelo
equivocado (por ejemplo líneas en vez de facturas), o los importes son campos
calculados que no están en la vista: añádelos con *Acceso a más campos*.
