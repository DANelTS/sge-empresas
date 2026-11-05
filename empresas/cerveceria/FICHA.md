# Cervecera Lúpulo Norte S.L. — cerveza artesanal

> **Todos los datos de esta empresa son ficticios**: el nombre, el NIF, las
> direcciones, los clientes y los proveedores. El NIF tiene dígito de control
> válido porque Odoo lo comprueba, pero no corresponde a ninguna empresa real.

## Quiénes somos

Cervecera Lúpulo Norte es una fábrica de cerveza artesanal con sede en Arganda
del Rey (Madrid). Ocupamos la nave 4 de la calle de la Vega, en el polígono
industrial, y trabajamos en lotes de 1.000 litros. Compramos malta en
Valladolid, lúpulo en León, levadura en Zaragoza y botellas en Sagunto: nada de
eso lo fabricamos. Lo que hacemos es cocer, fermentar, madurar y envasar.

Tenemos cinco recetas fijas —rubia, IPA, tostada, trigo y sin alcohol— y una
edición de temporada, en barril de 20 o 30 litros y botella de 33 o 75
centilitros. El barril va a los bares, porque dura más y se sirve fresco de la
grifería; la botella va a restaurantes, a la tienda y a los particulares.

Nuestros clientes son, sobre todo, bares de Madrid y del corredor del Henares.
También servimos a tres restaurantes, a una tienda de cerveza y a un
distribuidor que coloca nuestra marca en Toledo, Guadalajara y Segovia.
Los particulares son una parte pequeña: compran en la fábrica los sábados o
encargan un growler.

El merchandising —vasos, camisetas y growlers— y los servicios —visitas,
alquiler de grifo y formación— fidelizan y aprovechan la nave: quien tiene
nuestro vaso en la barra vende nuestra cerveza.

## Cómo estamos organizados

```
Dirección (gerencia)
├── Comercial ........... ruta de bares, presupuestos, pedidos y tarifas
├── Almacén/Producción .. cocimiento, fermentación, envasado y expedición
├── Compras ............. malta, lúpulo, levadura, botellas y etiquetas
└── Administración ...... facturación, cobros, pagos y banca
```

Somos siete personas. Dirección lleva la relación con el distribuidor y las
inversiones. Comercial son dos: una hace ruta por las mañanas y otra atiende
teléfono y correo. En producción hay un maestro cervecero y un compañero de
envasado y almacén. Compras no es un departamento aparte: la asume el maestro
cervecero, que sabe cuánta malta pide la próxima cocción. Administración es una
sola persona y lleva facturas, cobros y pagos.

Ese reparto es el motivo de tener un ERP: siete personas con cuatro hojas de
cálculo acaban dando tres versiones del mismo pedido; con Odoo, todos miran los
mismos datos.

## Un día normal

Un lunes de octubre, un bar de Alcalá de Henares se queda sin rubia. Quiere dos
barriles de 30 litros y cuatro cajas de IPA de 33 cl —96 botellas— para el fin
de semana. El comercial pasa, mira lo vendido desde la última entrega y prepara
un **presupuesto**: tarifa de hostelería, un 8 % de descuento, pago a 30 días y
portes gratuitos porque supera los 180 €. El bar acepta y el presupuesto se
convierte en **pedido de venta**.

El pedido llega a almacén como **orden de entrega**. La rubia está en stock,
pero de IPA solo quedan 40 botellas: hay que envasar del tanque que maduró el
viernes. Producción lo apunta y el jueves sale el camión. El dueño del bar firma
el **albarán**, que dice qué se ha entregado de verdad: si una botella llega
rota, se anota y no se factura.

Al cierre del mes, administración emite la **factura** con lo entregado, su
número correlativo y vencimiento a 30 días. El bar paga por transferencia y
administración registra el **cobro** contra esa factura. Si se pidieron 100
botellas y se entregaron 96, la factura lleva 96: nunca inventa mercancía.

En paralelo, el maestro cervecero ve que quedan 5 sacos de malta y el mínimo
está en 8. Lanza un **pedido de compra** de 20 sacos a la maltería y 6 bolsas
de lúpulo, que tarda más porque viene de León. El miércoles se descarga, el
almacén cuenta bultos y firma la **recepción**. Días después llega la factura
del proveedor: administración la compara con el pedido y el albarán, y la paga
a 30 días. Esa comparación evita pagar mercancía que no ha entrado.

Hay una diferencia con quien solo distribuye: la cerveza tarda tres semanas en
estar lista. Lo que se vende en octubre se coció en septiembre.
Por eso el stock de producto terminado y el planning de cocciones pesan tanto
como la malta: un pedido grande no se resuelve sacando un palé, sino habiéndolo
previsto.

## Condiciones comerciales

- **Formas de pago a clientes:** pago inmediato para particulares; **30 días**
  para la mayoría de bares y restaurantes; **15 días** para dos bares antiguos;
  **45 días** para dos clientes de confianza y **fin del mes siguiente** para el
  restaurante grande y el distribuidor. Este último cobra a sus clientes y
  necesita más plazo.
- **Tarifas:** además de la general hay dos listas.
  - *Tarifa hostelería*: **8 % de descuento**. Se aplica a bares, restaurantes
    y a la tienda de cerveza.
  - *Tarifa distribución*: **15 % de descuento**, solo para el distribuidor.
  - Los particulares pagan la tarifa general, sin descuento.
  - Las tarifas no se acumulan entre sí ni con ofertas puntuales.
- **Portes:** gratuitos a partir de 180 € en la Comunidad de Madrid. Por debajo
  se cobran 12 €, que van como línea del pedido. Fuera de Madrid, porte único de
  25 €. El barril pesa y el reparto debe ser puntual: por eso el umbral es alto.
- **Devoluciones:** la cerveza es un alimento y no se devuelve salvo error
  nuestro. Si un lote sale defectuoso o un barril pierde gas, se repone y se
  emite una **factura rectificativa** por la diferencia. La factura original no
  se toca nunca: se corrige con otra factura, que es lo que exige Hacienda.
- **Barriles:** van en préstamo. No se facturan como envase y se recogen vacíos
  en la ruta siguiente. El barril que no vuelve es un coste que hay que vigilar.

## Tipos de IVA que aplicamos

| Familia | IVA | Por qué |
|---|---|---|
| Cerveza (barril, botella y packs) | 21 % | Es una bebida alcohólica: la ley la excluye de los tipos reducidos aunque sea un alimento. |
| Malta y levadura (materias primas) | 10 % | Son alimentos de cereales y levaduras (art. 91.Uno.1.1.º LIVA; DGT V0238-15), no porque se usen para hacer cerveza. |
| Lúpulo, botellas, etiquetas y cajas | 21 % | El lúpulo no es alimento y los envases tampoco: tipo general. |
| Merchandising (vasos, camisetas, growlers) | 21 % | No es alimento ni servicio cultural: tipo general. |
| Servicios (visita, alquiler de grifo, formación) | 21 % | Tipo general de servicios. |

El error típico es aplicar el 10 % a la cerveza porque «es comida». La ley
excluye expresamente las bebidas alcohólicas del tipo reducido. Toda la cerveza
va al 21 %, en barril y en botella.

En Odoo veréis que los impuestos se llaman **«21% B»** y **«21% S»**: la B es de
*bienes* y la S de *servicios*. La cerveza, la malta y las camisetas son bienes;
la visita y la formación son servicios. Elegir mal uno de los dos descuadra la
factura y el libro de IVA.

## Para saber más

- `docs/glosario-empresarial.md` — presupuesto, pedido, albarán, factura,
  vencimiento, abono, IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL guardan todo esto.
