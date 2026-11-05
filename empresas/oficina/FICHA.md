# Suministros Ofimat S.L. — la empresa del profesor

> **Todos los datos de esta empresa son ficticios**: el nombre, el NIF, las
> direcciones, los clientes y los proveedores. El NIF tiene dígito de control
> válido porque Odoo lo comprueba, pero no corresponde a ninguna empresa real.

## Quiénes somos

Suministros Ofimat es una distribuidora de material de oficina con almacén en
San Sebastián de los Reyes (Madrid) y reparto por toda España. Compramos a
fábrica y a mayorista, guardamos stock y repartimos desde ahí. El catálogo
tiene 35 referencias en cinco familias —papel y archivadores, escritura y
corrección, informática y consumibles, mobiliario pequeño, limpieza y
cafetería— y tres servicios.

El negocio tiene un problema de partida: los productos valen poco y abultan
mucho. Una caja de 500 folios deja poco más de dos euros de margen bruto; un
bolígrafo, céntimos. Con esos números no se vive de vender caro,
se vive de **facturar volumen pequeño muchas veces al mes y de que el
cliente no llame a otro proveedor para el tóner**.

Los clientes son despachos profesionales, gestorías, consultoras y clínicas de
Madrid y provincias cercanas; colegios, que concentran el gasto en septiembre y
en junio; dos administraciones públicas; y algún particular. El grande firma
un acuerdo anual y recibe pedido cada semana; el pequeño llama cuando se le
acaba el tóner.

## Cómo estamos organizados

```
Dirección (gerencia)
├── Comercial ........... cartera de clientes, tarifas, presupuestos y altas
├── Almacén ............. recepción, picking, expedición y rutas de reparto
├── Compras ............. reposición por mínimos, proveedores y portes
└── Administración ...... facturación, cobros, pagos y conciliación bancaria
```

Seis personas para todo: el comercial atiende el teléfono y prepara las ofertas
de los concursos; administración lleva la facturación y los impagos. Por eso hay
un ERP: que todos miren el mismo stock y la misma tarifa, en lugar de tres hojas
de cálculo que nunca coinciden.

## Un día normal

Un martes entra un pedido de una gestoría: 20 cajas de folios A4 y 6 tóneres
negros compatibles, con la tarifa de empresas y pago a 30 días. El comercial lo
confirma y el pedido pasa al almacén como **orden de entrega**. El almacén cuenta
y solo hay 12 cajas de folios: el camión de la papelera llega el jueves.

Ahí empieza lo que en este sector se llama un **pedido con entregas parciales**.
El cliente ha pedido 20 cajas; servimos 12 hoy y las otras 8 quedan pendientes.
Se emite un **albarán** de 12 cajas y 6 tóneres, el cliente lo firma y el pedido
sigue abierto con una entrega pendiente. El jueves llega el género, se prepara un
segundo albarán por las 8 cajas y el pedido se cierra. Si el cliente anulara lo
que falta, se anula la línea y no se factura nada.

Se hace mal casi siempre: **se factura lo entregado, no lo pedido**. La
factura de fin de mes lleva las 12 cajas del primer albarán y las 8 del segundo;
si el segundo cae en el mes siguiente, va en la factura de ese mes. El cliente no
paga lo que no tiene y nosotros no declaramos un ingreso no realizado. En Odoo
el pedido enseña cantidad pedida, entregada y pendiente.

En paralelo, el almacén avisa de que quedan 9 cajas de folios y el mínimo está
en 30: compras lanza un **pedido de compra** a Papelera del Ebro, que sirve en
tres días. En la recepción se firma el albarán del proveedor y se comprueba lo
que llega; su factura se paga a 30 días.

El cobro: la gestoría paga por transferencia y administración casa el abono con
la factura. Si paga 200 € de una factura de 1.200 €, queda parcialmente cobrada
y el resto sigue vivo hasta el vencimiento.

## Condiciones comerciales

- **Formas de pago a clientes:** contado para particulares; **30 días** para la
  mayoría de empresas y colegios; **45 días** en clientes antiguos y
  **fin del mes siguiente** para la industria alimentaria y las
  administraciones públicas.
- **Tarifas:** hay dos listas además de la general.
  - *Tarifa empresas*: **12 % de descuento**. Es el precio de un acuerdo anual:
    el cliente nos compra todo el material y le garantizamos entrega en 48 horas.
  - *Tarifa colegios*: **18 % de descuento**. Los colegios compran por concurso,
    comparan tres ofertas y concentran el gasto en dos campañas; se lleva el
    pedido quien da mejor precio y el margen se recupera en volumen.
  - Los particulares pagan la tarifa general.
- **Descuento por volumen:** encima de la tarifa, el comercial puede aplicar un
  descuento de línea —2 % a partir de 10 cajas, 4 % a partir de 25— para pedidos
  grandes o para igualar una oferta. Va como descuento de la línea, no como
  tarifa nueva, y queda registrado con quién lo autoriza: cada punto sale del
  margen, y un 4 % extra pesa más en un tóner original (35 % de margen) que en
  una silla (51 %).
- **Portes:** gratuitos a partir de 120 € en la Comunidad de Madrid; 18 € en la
  península y 30 € a Baleares. El urgente en 24 horas lleva 12 € de recargo,
  que se añade como línea del pedido.
- **Devoluciones:** los consumibles informáticos se admiten solo con el precinto
  intacto; un tóner abierto no se devuelve. Si el error es nuestro, se repone y
  se emite **factura rectificativa**, nunca se toca la factura original.

## Tipos de IVA que aplicamos

| Familia | IVA | Por qué |
|---|---|---|
| Papel, archivadores, sobres | 21 % | Tipo general: no es alimento, libro ni medicamento. |
| Escritura y corrección | 21 % | Tipo general. |
| Tóner, tinta, periféricos | 21 % | Tipo general. |
| Mobiliario pequeño | 21 % | Tipo general, aunque sea un bien duradero. |
| Limpieza y cafetería de oficina | 21 % | Tipo general: son consumibles, no alimentos. |
| Servicios (instalación, consignación, formación) | 21 % | Tipo general de servicios. |

La pregunta que cae siempre en clase: **¿por qué un tóner de 55 € y una silla de
229 € llevan el mismo IVA?** Porque el tipo no depende del precio ni de lo que
dure el producto: depende de la naturaleza del bien. Un tóner es un artículo de
oficina y una silla es mobiliario: los dos están en el tipo general. Lo que sí
cambia el tipo es otra cosa: un libro tributa al 4 %, y por eso esta empresa
**no vende libros**. Un colegio que pide libros de texto no nos llama: los
compra en una librería. Y el café de la máquina es un alimento, así que aquí
vendemos vasos y servilletas, pero no el café.

En Odoo los impuestos se llaman **«21% B»** y **«21% S»**: la B es de *bienes* y
la S de *servicios*. Elegir mal uno de los dos descuadra la factura y el libro
de IVA.

## Para saber más

- `docs/glosario-empresarial.md` — presupuesto, pedido, albarán, factura,
  vencimiento, abono, IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL guardan todo esto.
