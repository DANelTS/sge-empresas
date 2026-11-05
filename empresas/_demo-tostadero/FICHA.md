# Tostadero Manzanares S.L. — la empresa del profesor

> **Todos los datos de esta empresa son ficticios**: el nombre, el NIF, las
> direcciones, los clientes y los proveedores. El NIF tiene dígito de control
> válido porque Odoo lo comprueba, pero no corresponde a ninguna empresa real.

## Quiénes somos

Tostadero Manzanares es un tostador de café artesanal con sede en Valdemoro
(Madrid). Compramos café verde a importadores —Brasil, Colombia y Etiopía— y lo
tostamos en pequeñas partidas de 12 kilos en nuestra nave del polígono. Vendemos
el café tostado en grano o molido, en bolsas de 250 g y 1 kg, y también en
formatos profesionales de 5 kg para bares que consumen mucho.

Nuestros clientes son, sobre todo, cafeterías, restaurantes y hoteles de Madrid
y de las provincias cercanas: gente que sirve café todos los días y necesita
recibirlo con regularidad. Una parte menor de la facturación viene de
particulares que compran por teléfono o en nuestra pequeña tienda, y de un
distribuidor que revende nuestra marca en el norte de España.

Además del café vendemos menaje (molinillos, prensas, jarras, tazas) y unos
pocos servicios: formación de baristas, puesta a punto de molinillos y
mantenimiento anual de las máquinas de espresso. El menaje y la formación
existen sobre todo para fidelizar: quien compra la máquina en nuestra casa
compra también el café.

## Cómo estamos organizados

```
Dirección (gerencia)
├── Comercial ........... visita bares, prepara presupuestos, cierra pedidos y tarifas
├── Almacén ............. tueste, envasado, stock y expedición de pedidos
├── Compras ............. café verde, envases y menaje a proveedores
└── Administración ...... facturación, cobros, pagos y banca
```

En una empresa así, cuatro personas se reparten esas tareas: el comercial
también atiende el teléfono, y administración lleva a la vez la facturación y
los cobros. Esa es justo la razón de tener un ERP: que los cuatro miren los
mismos datos en lugar de cuatro hojas de cálculo.

## Un día normal

Un martes cualquiera empieza con un correo de una cafetería que quiere cambiar
de proveedor. El comercial visita el bar, apunta cuántos cafés sirve al día y
prepara un **presupuesto**: 20 kg de mezcla de la casa al mes, con la tarifa de
hostelería y pago a 30 días. La cafetería acepta y el presupuesto se convierte
en **pedido de venta**.

El pedido llega al almacén como una **orden de entrega**. El almacén tuesta el
jueves, envasa, prepara el **albarán** y lo entrega. El cliente firma el
albarán: ese papel dice qué se ha entregado de verdad, aunque luego se facture
otra cosa. Al final del mes, administración emite la **factura** con lo
entregado, con su número correlativo y su fecha de vencimiento a 30 días. El
cliente paga por transferencia y administración registra el **cobro** contra esa
factura, que deja de estar pendiente.

Y en paralelo: cuando el café verde de Brasil baja de 8 sacos, el sistema avisa
y compras lanza un **pedido de compra** al importador. A los diez días llega el
camión, el almacén firma la **recepción** y a fin de mes llega la factura del
proveedor, que se paga a 30 días.

Ese es el ciclo completo que vais a manejar en este módulo: comprar, almacenar,
vender, entregar, facturar y cobrar. Todo encadenado: del presupuesto sale el
pedido, del pedido el albarán y del albarán la factura, y cada documento guarda
el enlace con el anterior.

## Condiciones comerciales

- **Formas de pago a clientes:** contado para particulares; **30 días** para
  cafeterías y restaurantes; **45 días** en algún cliente antiguo y **fin del
  mes siguiente** para hoteles y para el distribuidor.
- **Tarifas:** hay dos listas de precios además de la general.
  - *Tarifa hostelería*: **8 % de descuento** sobre la tarifa general. Se aplica
    a cafeterías, restaurantes, hoteles y a la tienda de café.
  - *Tarifa distribución*: **15 % de descuento**, solo para el distribuidor.
  - Los particulares pagan el precio de tarifa, sin descuento.
- **Portes:** gratuitos a partir de 150 € de pedido en la zona de Madrid. Por
  debajo de esa cantidad se cobran 9 € de porte, que se añaden como línea del
  pedido. Fuera de Madrid, porte único de 18 €.
- **Devoluciones:** el café tostado no se devuelve salvo error nuestro. Si el
  tueste no es el pedido, se repone y se emite **factura rectificativa** por la
  diferencia, nunca se modifica la factura original.

## Tipos de IVA que aplicamos

| Familia | IVA | Por qué |
|---|---|---|
| Café tostado (grano, molido, monodosis, café frío) | 10 % | Es un alimento elaborado, no una materia prima agrícola. |
| Café verde (materia prima) | 10 % | Producto alimenticio destinado a la industria. |
| Menaje, maquinaria, envases | 21 % | Tipo general: no son alimentos. |
| Servicios (formación, mantenimiento, asesoría) | 21 % | Tipo general de servicios. |

En Odoo veréis que los impuestos se llaman **«21% B»** y **«21% S»**: la B es de
*bienes* y la S de *servicios*. Elegir mal uno de los dos descuadra la factura y
el libro de IVA, así que conviene fijarse.

## Para saber más

- `docs/glosario-empresarial.md` — presupuesto, pedido, albarán, factura,
  vencimiento, abono, IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL guardan todo esto.
