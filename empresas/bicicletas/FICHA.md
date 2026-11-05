# Ciclos Rodadura S.L. — empresa del sector de bicicletas

> **Todos los datos de esta empresa son ficticios**: nombre, NIF, direcciones,
> clientes y proveedores. El NIF tiene dígito de control válido porque Odoo lo
> comprueba, pero no existe.

## Quiénes somos

Ciclos Rodadura es una tienda de bicicletas con taller propio en Alcobendas
(Madrid), en la Avenida de la Industria. La tienda ocupa 220 m² de expositor y
el taller otros 60 m² detrás, con una puerta de doble hoja que no para de
abrirse.

Vendemos bicicletas urbanas, de montaña, gravel y eléctricas, además de
recambios, accesorios y ropa. Pero el negocio no se sostiene solo con la venta:
una bici de 479 € deja unos 190 € de margen y se cambia cada pocos años,
mientras que vuelve al taller dos veces al año y cada visita deja entre 22 y
75 € con mucho menos coste. Por eso el taller no es un añadido: es lo que paga
la nave y los sueldos.

Nuestros clientes son, sobre todo, particulares del norte de Madrid. El resto
son otros talleres y tiendas que nos compran recambios cuando se quedan sin
existencias, dos empresas de reparto con flota eléctrica y dos clubes
deportivos.

## Cómo estamos organizados

```
Dirección (gerencia)
├── Tienda y mostrador ..... venta directa, presupuestos de flota y tarifas
├── Taller ................. recepción de bicis, reparación y montajes a medida
├── Compras y almacén ...... pedidos a proveedores, stock y reposición
└── Administración ......... facturación, cobros, pagos y banca
```

Somos cinco personas y media: gerencia, dos mecánicos, mostrador y
administración a media jornada. Todos hacen de todo, y esa es justo la razón de
tener un ERP: que los cinco miren los mismos datos.

## Un día normal

Un martes cualquiera empieza con una bici colgada del soporte: el cliente dice
que la rueda trasera «hace un ruido». El mecánico la revisa y mostrador prepara
un **presupuesto** con dos líneas: *centrado de rueda* y *cámara 29"*. El
cliente lo aprueba y el presupuesto se convierte en **pedido de venta**. Ahí
está la primera idea del módulo: un trabajo de taller es un pedido de venta más,
con líneas de servicio y de recambio.

Al terminar, administración emite el **albarán** —la bici se lleva— y a final
de mes la **factura**. El cliente paga con tarjeta y se registra el **cobro**.

En paralelo, un club de Tres Cantos pide presupuesto para mantener sus catorce
bicicletas con la *tarifa flotas*. Acepta, pero no las quiere todas a la vez: se
entregan en tres **albaranes** parciales y se factura todo junto a fin de mes. Y
cuando en el almacén quedan menos de quince cubiertas de 29", salta el aviso y
compras lanza un **pedido de compra** a Neumáticos Ciclo Levante, que llega en
cuatro días con su **recepción** y factura a 45 días.

Ese es el ciclo que vais a manejar, del presupuesto a la factura: comprar,
almacenar, vender, entregar, facturar y cobrar.

## Condiciones comerciales

- **Formas de pago a clientes:** pago inmediato para particulares, que pagan la
  reparación al recoger la bici; **30 días** para talleres, tiendas y clubes;
  **45 días** para dos clientes de siempre; **fin del mes siguiente** para las
  dos empresas con flota.
- **Tarifas:** además de la general hay dos listas.
  - *Tarifa taller*: **10 %**. Para talleres y tiendas que compran recambios
    para revender. El descuento es pequeño a propósito: el recambio ya lleva
    poco margen.
  - *Tarifa flotas*: **15 %**. Para empresas de reparto y clubes: compran mucho
    y con mantenimiento contratado.
  - Los particulares pagan la tarifa general, sin descuento.
- **Portes:** recogida gratuita en tienda, también de bicicletas montadas.
  Recambios y ropa, 5,90 € y gratis desde 60 € en Madrid.
- **Devoluciones:** 14 días naturales en producto sin usar. Un servicio de
  taller ya realizado no se devuelve; si el trabajo está mal hecho se repite sin
  cargo y, si ya se cobró, se emite **factura rectificativa**: la original nunca
  se toca.

## Tipos de IVA que aplicamos

| Familia | IVA | Por qué |
|---|---|---|
| Bicicletas (urbanas, montaña, gravel, eléctricas) | 21 % | Bien mueble: tipo general, también las eléctricas. |
| Recambios y componentes | 21 % | No son alimentos ni productos de los anexos. |
| Accesorios y ropa | 21 % | Tipo general, también la ropa deportiva. |
| Taller (mano de obra, montajes) | 21 % | Servicio de reparación: tipo general. |
| Alquiler de bicicletas | 21 % | Servicio de alquiler: tipo general. |

Todo va al 21 %. Es la primera tentación —buscar un tipo reducido para la
reparación o la bici eléctrica— y no existe: el 10 % está pensado para
alimentación, vivienda, sanidad y transporte de viajeros. Que el taller «sea un
servicio» no cambia el porcentaje.

Lo que sí cambia es **qué impuesto se elige en Odoo**. Conviven **«21% B»** y
**«21% S»**: la B es de *bienes* y la S de *servicios*. El porcentaje es el
mismo, pero apuntan a cuentas distintas: el libro de IVA y el modelo 303 separan
entregas de bienes y prestaciones de servicios. Si a una revisión le pones
«21% B», el cliente paga lo mismo pero el trimestre no casa. Bici, recambio,
casco y maillot son **B**; mano de obra, montaje y alquiler son **S**.

## Producto y servicio: por qué el taller no tiene existencias

Un producto almacenable —una cubierta— se compra, se guarda y se vende: tiene
referencia, código de barras, ubicación y un número de unidades que sube y baja.
Un servicio —una puesta a punto— no se puede guardar en una estantería: no
existe hasta que se presta. Lo que se vende son las **horas de un mecánico**, y
esas horas no se almacenan, se pierden si el taller está vacío. En Odoo se marca
como servicio, sin inventario ni código de barras; su «disponibilidad» es la
agenda del taller, no un número de unidades.

Ahora el matiz: el servicio no tiene stock, **pero sí consume recambios**. Para
cambiar una cubierta hacen falta una cubierta y una cámara, y esas sí salen del
almacén. Por eso un trabajo de taller se factura con **dos tipos de línea**: la
mano de obra (servicio) y los materiales (producto). Si solo se cobra la mano de
obra, el almacén descuenta una cubierta que nadie ha pagado: el stock deja de
ser real y el margen miente. La regla de oro: **todo lo que sale del almacén va
en una línea; el tiempo, en otra**. Las dos llevan el mismo 21 %, pero solo una
mueve existencias.

El mismo razonamiento vale para el alquiler: la bici alquilada no es mercancía,
es inversión de la empresa. El cliente compra el **uso** de un día, y eso es un
servicio; la bici sigue siendo nuestra y no es stock para vender. Lo que sí
consume son cámaras, pastillas y horas de taller cuando vuelve con un pinchazo.

## Para saber más

- `docs/glosario-empresarial.md` — presupuesto, pedido, albarán, factura,
  vencimiento, abono, IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL guardan todo esto.
