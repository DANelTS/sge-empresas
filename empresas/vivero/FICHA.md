# Vivero La Fresneda S.L. — la empresa del profesor

> **Todos los datos de esta empresa son ficticios**: el nombre, el NIF, las
> direcciones, los clientes y los proveedores. El NIF tiene dígito de control
> válido porque Odoo lo comprueba, pero no corresponde a ninguna empresa real.

## Quiénes somos

Vivero La Fresneda es un centro de jardinería con vivero propio en Colmenar
Viejo (Madrid), en la carretera de Guadalix. Ocupamos unos 8.000 m²: tres
invernaderos, la zona de árboles y arbustos, el almacén y la tienda abierta al
público.

Tenemos tres líneas de negocio: la **venta** de planta, sustratos, macetas,
herramientas y riego; el **diseño e instalación** de jardines, con plano,
plantación y riego; y el **mantenimiento** mensual de jardines privados,
comunidades y zonas verdes municipales.

Vendemos a particulares, pero sobre todo a comunidades de propietarios,
empresas con jardín, dos ayuntamientos y un paisajista que revende nuestra
planta. Es cliente, no competencia.

## Cómo estamos organizados

```
Dirección (gerencia)
├── Comercial ........... mostrador, presupuestos, visitas y tarifas
├── Vivero y almacén .... producción propia, reposición, stock y pedidos
├── Compras ............. planta, sustratos, macetas y herramientas
└── Administración ...... facturación, cobros, pagos y contratos
```

Somos siete personas. El comercial pasa media jornada en el mostrador y media
visitando comunidades; en el vivero hay tres entre producción y almacén;
compras y administración son la misma persona. Con ese tamaño, todos deben
mirar los mismos datos: ahí entra el ERP.

## Un día normal

Un martes de marzo, el administrador de una comunidad llama porque se les han
muerto los setos. El comercial va a verlo, mide el seto, mira el riego y
prepara un **presupuesto**: 40 photinias, 20 sacos de sustrato, una línea de
goteo y el mantenimiento mensual. La junta lo aprueba y el presupuesto se
convierte en **pedido de venta**, con tarifa de comunidades y pago a 30 días.

El pedido llega al vivero como **orden de entrega**. El almacén separa la
planta, comprueba que está sana y entrega con **albarán**. El presidente de la
comunidad firma: ese papel dice qué se ha entregado de verdad. A final de mes,
administración emite la **factura** y registra el **cobro**.

En paralelo, cuando el photinia baja de 8 unidades, el sistema avisa y compras
lanza un **pedido de compra** al vivero productor. La planta llega en dos días,
se firma la **recepción** y la factura se paga a 30 días. Ese es el ciclo del
módulo, documento a documento.

## El calendario manda

El sector no vende igual todo el año. Entre marzo y mayo se concentra casi la
mitad de la facturación: es cuando se planta y cuando las comunidades aprueban
sus presupuestos. En diciembre hay un segundo pico: abetos, flor de pascua y
centros de Navidad. Enero y febrero son el valle. En verano suben el riego y el
mantenimiento; en otoño vuelve la plantación de árboles y setos.

Por eso no se compra igual todo el año: en febrero se hace acopio de temporada,
en noviembre se prepara Navidad y en enero se inventaría y se tira lo que no ha
aguantado. El mantenimiento mensual sostiene la empresa en los meses flojos y
permite pagar la nómina de enero.

## Condiciones comerciales

- **Formas de pago:** contado para particulares; **30 días** para comunidades,
  empresas y paisajistas; **45 días** para una comunidad, el colegio y un
  ayuntamiento; **fin del siguiente mes** para el hotel y el otro ayuntamiento.
- **Tarifas:** dos listas además de la general.
  - *Tarifa profesionales*: **10 % de descuento**, para empresas con jardín,
    ayuntamientos y el paisajista que revende.
  - *Tarifa comunidades*: **5 % de descuento**, solo para comunidades.
  - Los particulares, sin descuento.
- **Portes:** gratis desde 60 € en 15 km; por debajo, 6 € como línea del
  pedido. Fuera de ese radio se presupuesta por kilómetros y la entrega se
  factura al 21 %.
- **Devoluciones:** la planta viva se cambia en 48 horas si viene enferma o no
  es la variedad pedida, con ticket o albarán. Si el error es nuestro se repone
  y se emite **factura rectificativa**; la original no se toca.

## Tipos de IVA que aplicamos

| Familia | IVA | Por qué |
|---|---|---|
| Plantas, árboles y arbustos | 10 % | La planta viva ornamental va al tipo reducido. |
| Sustratos, abonos y fertilizantes | 10 % | Son productos para la producción vegetal. |
| Herramientas, macetas y riego | 21 % | Artículos manufacturados: tipo general. |
| Decoración de jardín | 21 % | Mobiliario y adornos, no planta. |
| Servicios de jardinería | 21 % | Diseño, riego, mantenimiento, poda y entrega. |

El error clásico está en el mismo pedido: un olivo de 78 € y la maceta de
cerámica donde se planta. El olivo va al **10 %** y la maceta al **21 %**,
aunque se vendan juntos y la maceta sea «para la planta». No decide el destino,
sino lo que es el artículo: planta viva frente a cerámica cocida. Pasa lo mismo
con el sustrato (10 %) y la pala (21 %). Una factura mezcla los dos tipos en el mismo
total; por eso cada producto lleva su impuesto desde la familia, y cambiarlo
«para que cuadre» descuadra el libro de IVA.

## La planta se muere: stock y merma

Una caja de tornillos no se estropea; una planta sí. Si no se riega, si llega
una helada o se queda tres semanas en el invernadero, se muere y hay que
tirarla. Eso es la **merma**, un coste real que hay que medir.

Por eso el stock de planta viva se revisa cada semana con un inventario: se
cuenta lo que hay, se compara con el sistema y la diferencia se registra como
pérdida. Si entran 1.200 petunias y se venden 900, pero solo quedan 250, hay 50
plantas muertas: no han desaparecido, se han perdido. Sin ese control, la merma
se come el margen y nadie sabe por qué.

El mínimo avisa de reponer antes de quedarse sin planta en campaña;
el máximo evita comprar de más y tener que tirarla. En temporada, comprar tarde y comprar de más cuestan lo
mismo: margen.

## Mantenimiento: por qué se factura mes a mes

El mantenimiento no es un trabajo que se termina, es un servicio continuo. El
cliente no compra «un jardín cuidado», compra que alguien vaya dos veces al mes,
pode, abone, revise el riego y reponga lo que falle. Por eso se factura **mes
vencido**, una factura por mes y no una al año: el trabajo de enero ya está
hecho cuando se cobra enero, y el cliente puede rescindir con aviso previo.

En Odoo eso es un pedido de venta con una línea de servicio y facturación
periódica mensual: el pedido es el contrato y de él salen doce facturas al año,
cada una con su vencimiento. Una poda extraordinaria se añade como línea aparte
en la factura del mes. Mezclar cuota y trabajo extra acaba en discusión.

## Para saber más

- `docs/glosario-empresarial.md` — presupuesto, pedido, albarán, factura,
  vencimiento, abono, IVA repercutido y soportado.
- `docs/modelo-de-datos.md` — qué tablas de PostgreSQL guardan todo esto.
