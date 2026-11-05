# S20 · Cuestionario de consultas

**Entrega:** un documento (o un PDF) con las diez respuestas y su prueba.
**Individual.** Cada pregunta se responde sobre **tu** empresa: los números son
tuyos y no coinciden con los de nadie más.

## Cómo se entrega cada respuesta

| Tipo de pregunta | Qué adjuntas |
|---|---|
| Resuelta con la interfaz | Captura de pantalla con el **filtro visible** y el resultado. |
| Resuelta con SQL | El texto completo de la consulta y la salida de `psql` (o captura de DBeaver). |
| Con exportación | El fichero exportado (XLSX o CSV) además de la respuesta. |

Regla de oro: si no puedes explicar la consulta, no cuenta. En la prueba de la
S22 se pregunta por ella.

## Las diez preguntas

**1. ¿Cuántas facturas de cliente has emitido entre el 1 de agosto y el 31 de
octubre de 2026, y por qué importe total (sin IVA)?**
*Interfaz:* **Facturación → Clientes → Facturas**, filtro por fecha de factura y
estado *Publicado*; el total sale sumando la columna o con el pivote.

**2. ¿Qué tres clientes han facturado más en septiembre de 2026?**
*Interfaz:* agrupa por cliente y ordena por importe. Indica también qué
porcentaje del total de septiembre representa cada uno.

**3. ¿Cuánto dinero tienes pendiente de cobro a día de hoy y en cuántas facturas?**
*Interfaz o SQL.* Ojo: pendiente no es lo mismo que «no pagada del todo».

**4. ¿Qué clientes tienen alguna factura vencida hace más de 30 días?**
*SQL obligatorio.* Devuelve cliente, número de factura, vencimiento, importe
pendiente y días de retraso, ordenado de más antiguo a más reciente.

**5. ¿Qué familia de producto ha facturado más en el trimestre y cuánto?**
*Interfaz, con vista pivote.* Agrupa por categoría de producto y por mes.

**6. ¿Qué productos están por debajo de su stock mínimo en este momento?**
*SQL obligatorio.* **Exporta el resultado a CSV** con referencia, nombre,
existencias, mínimo y cuánto falta.

**7. ¿Cuál es el margen bruto (precio de venta menos coste) por familia, sobre lo
facturado en el trimestre?**
*SQL.* Necesitas `product_template.list_price`, el coste de
`product_product.standard_price` y las cantidades facturadas en
`account_move_line`. Explica en una línea cómo has calculado el coste.

**8. ¿Qué pedidos de venta tienen todavía entrega pendiente?**
*Interfaz.* Filtra por estado del pedido y por la cantidad entregada; indica
pedido, cliente y qué falta.

**9. ¿Qué proveedor te ha facturado más en el trimestre?**
*SQL.* Facturas de proveedor publicadas (`move_type = 'in_invoice'`).

**10. Exporta a XLSX el listado de facturas pendientes de cobro**, con estas
columnas exactamente: número, cliente, fecha de factura, vencimiento, total,
pendiente y días de retraso.
*Exportación desde la interfaz* (no vale hacerlo a mano en Excel).

## Criterios de corrección

| Criterio | Peso |
|---|---|
| Las diez preguntas están respondidas y son correctas para tu base | 40 % |
| Cada respuesta lleva su prueba (captura, consulta o fichero) | 25 % |
| Las consultas SQL están bien construidas (filtros de estado, JOINs correctos) y se explican | 20 % |
| Las dos exportaciones tienen el formato y las columnas pedidas | 10 % |
| Presentación, ortografía y vocabulario técnico | 5 % |

## Avisos

- Las facturas **rectificativas** restan: si no las tienes en cuenta, el total no
  cuadra.
- Los **borradores** no son ventas. Filtra siempre por estado publicado.
- Las fechas de la base están en **UTC**; para agrupar por meses en España usa
  `date_order AT TIME ZONE 'Europe/Madrid'` o filtra por fecha de factura, que es
  un campo de fecha pura.
- Si un resultado te sale raro, compara con la interfaz antes de entregarlo: la
  misma pregunta por los dos caminos tiene que dar lo mismo.
