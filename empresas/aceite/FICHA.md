# Cooperativa Olivar del Tajo S. Coop. — la almazara del sector aceite

> **Todos los datos son ficticios**: nombre, NIF, direcciones, clientes y
> proveedores. El NIF tiene dígito de control válido, pero no corresponde a
> ninguna cooperativa real.

## Quiénes somos

Cooperativa Olivar del Tajo es una almazara cooperativa de Los Yébenes (Toledo),
en la ladera sur de los Montes de Toledo. Ochenta y cuatro socios aportan la
aceituna de sus olivares —picual y cornicabra, casi toda de secano— y la
cooperativa la moltura, la almacena y la envasa. Salen unas 220.000 botellas
equivalentes al año: somos una almazara de pueblo que vende producto cuidado.

El catálogo tiene cuatro patas: el aceite de oliva virgen extra (70 % de la
facturación), la despensa de aceitunas, conservas y vinagre, la cosmética hecha
con nuestro aceite y los servicios de almazara. Vendemos a tiendas gourmet de
Toledo, Madrid y Ciudad Real, a restaurantes y hoteles, y a particulares; un
distribuidor regional completa la red.

## La campaña de recolección

La aceituna se recoge entre noviembre y enero; fuera de esos tres meses no hay
materia prima. En campaña la almazara trabaja en dos turnos y muele en las 24
horas siguientes a la recepción, porque cuanto antes se muele, mejor es el
aceite. En enero y febrero el depósito está lleno; desde marzo las existencias
solo bajan.

La estacionalidad manda en el stock: de febrero a mayo se vende con holgura, en
junio y julio quedan las últimas partidas y en agosto y septiembre solo se vende
lo guardado. Por eso hay stock mínimo y máximo por referencia: si un formato baja
del mínimo en julio, no se repone hasta noviembre y el comercial ofrece otro. La
cooperativa reserva una partida de aceite de guarda: vender todo en campaña es
fácil, llegar a agosto con aceite es el negocio.

## Cómo estamos organizados

```
Asamblea General de socios
└── Consejo Rector
    └── Gerencia
        ├── Comercial ............ tiendas gourmet, hostelería y tarifas
        ├── Almazara ............. recepción, molturación y depósitos
        ├── Envasado y almacén ... botellas, latas, stock y expedición
        └── Administración ....... facturación, cobros, pagos e IVA
```

La Asamblea elige al Consejo Rector y este nombra a la gerencia. Somos siete
fijos y dos eventuales en campaña; administración lleva facturación, cobros e
IVA. Con ese equipo, un ERP es la única forma de que todos miren los mismos
datos.

## Un día normal

Un martes de marzo entra un pedido de un restaurante de Orgaz: 12 botellas de
litro, 6 tarros de aceitunas y una cata para el equipo de sala. El comercial
prepara el presupuesto con la tarifa de hostelería y pago a 30 días; el
restaurante lo acepta y el presupuesto se convierte en pedido de venta.

El pedido llega al almacén como orden de entrega. Envasado coge aceite del
depósito, llena las botellas, etiqueta con el lote de la partida y prepara el
albarán. El cliente firma: ese documento dice qué ha salido de verdad. A final de
mes, administración emite la factura con lo entregado, su número correlativo y su
vencimiento a 30 días; el restaurante paga por transferencia y el cobro se
registra contra esa factura. En paralelo, cuando el vidrio baja del mínimo se
lanza un pedido de compra; cuando baja el depósito, se compra aceituna.

## Condiciones comerciales

- **Formas de pago:** contado para particulares; **30 días** para tiendas gourmet
  y restaurantes; **15 días** en una tienda pequeña; **45 días** en clientes
  antiguos; **fin del mes siguiente** para hoteles y distribuidor.
- **Tarifas:** además de la general hay dos listas.
  - *Tarifa hostelería*: **8 %**. Restaurantes, hoteles y tiendas gourmet, que
    compran para revender.
  - *Tarifa distribución*: **15 %**, solo para el distribuidor.
  - Los particulares pagan la tarifa general.
- **Portes:** gratis a partir de 200 € en Toledo, Madrid y Ciudad Real; por
  debajo, 12 € como línea del pedido. Fuera de esas provincias, 25 €.
- **Devoluciones:** el aceite no se devuelve salvo error nuestro. Si una botella
  llega rota se repone y se emite **factura rectificativa**, nunca se modifica la
  original.

## Tipos de IVA que aplicamos

| Familia | IVA | Por qué |
|---|---|---|
| Aceite de oliva virgen extra y virgen (botella, garrafa, lata, monodosis, suave) | 4 % | Alimento de primera necesidad: tributa al tipo superreducido. |
| Aceitunas de mesa, conservas vegetales y vinagre | 10 % | Alimentos elaborados: no llegan al superreducido. |
| Cosmética y menaje (jabón, crema, botellas y latas vacías, cajas de regalo) | 21 % | Tipo general: no son alimentos. |
| Servicios (visita, cata, asesoría, porte, mantenimiento) | 21 % | Tipo general de servicios. |

El rasgo que distingue a esta empresa es que **en un mismo pedido conviven los
tres tipos**. Un particular que prepara una boda pide 12 botellas de litro,
6 tarros de aceitunas, 10 jabones para los invitados y una cata guiada. La
factura lleva cuatro líneas y cada una su impuesto:

- 12 × 13,90 € = 166,80 € al 4 % → 6,67 € de IVA.
- 6 × 3,90 € = 23,40 € al 10 % → 2,34 €.
- 10 × 7,50 € = 75,00 € al 21 % → 15,75 €.
- Cata guiada: 120,00 € al 21 % → 25,20 €.

Base imponible 385,20 €; IVA 49,96 €; total 435,16 €. Si se pusiera el 21 % a
todo, la factura saldría casi 31 € más cara; con el 4 % a todo, la cooperativa
ingresaría 34,55 € menos de IVA del debido. Por eso el tipo se decide línea a
línea y no se puede «promediar».

Al facturar, cada línea arrastra su impuesto y el pie muestra el desglose por
tipo. En Odoo los impuestos se llaman **«4% B»**, **«10% B»**, **«21% B»** y
**«21% S»**: la B es de bienes y la S de servicios. Elegir mal uno descuadra la
factura y el libro de IVA.

Al declarar, el IVA repercutido se separa por tipo en el modelo 303 trimestral y
en el libro registro de facturas expedidas. El soportado de las compras
—aceituna, botellas, etiquetas, maquinaria— se resta del repercutido, cada uno
con su tipo. Consecuencia práctica: un litro de 13,90 € solo lleva 0,56 € de IVA,
mientras que una crema de 12,90 € lleva 2,71 €. El año que se compró la línea de
molturación, el IVA soportado del 21 % superó todo el repercutido y la
liquidación salió a devolver; no es un error. No hay prorrata: todas las ventas
están sujetas.

> **Nota:** el tipo del 4 % del aceite ha cambiado varias veces en los últimos
> años. Para 2026 el material trabaja con el 4 % y el 10 % para la despensa, pero
> el tipo del aceite y el de la aceituna a granel para molturación quedan
> **pendientes de confirmar con la AEAT**; si la Agencia publica otro criterio,
> manda el oficial.

## Para saber más

- `docs/glosario-empresarial.md` — presupuesto, pedido, albarán, factura,
  vencimiento, abono, IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL guardan todo esto.
