# S19 · Compras e inventario

**Sesión:** martes 17 de noviembre de 2026 · 1 h
**CE que trabaja:** 3b (formularios) y 3a (manipulación de datos).

## Objetivo

Reponer sin quedarse sin género y sin inmovilizar dinero de más: reglas de
reabastecimiento, pedido de compra, recepción (también parcial), factura del
proveedor y ajuste de inventario cuando algo se rompe.

## Contexto empresarial: comprar es una decisión, no un trámite

Toda compra es dinero inmovilizado hasta que se vende. Si compras mucho, el
almacén se llena y no tienes caja; si compras poco, te quedas sin género y el
cliente se va a la competencia. El equilibrio tiene dos números:

- **Stock mínimo**: por debajo de ahí no se debe bajar.
- **Plazo de entrega**: lo que tarda el proveedor en servir.

Con los dos se calcula el **punto de pedido**: hay que pedir cuando quede
*consumo durante el plazo + stock mínimo*. Si vendes 2 sacos al día y el
proveedor tarda 10 días, con menos de 20 sacos vas tarde, aunque tu mínimo sea
10.

Eso es lo que automatizan las **reglas de reabastecimiento**: el sistema vigila
el stock y propone la compra. Tú decides si la confirmas.

Y luego está la realidad: el proveedor sirve la mitad, un saco llega roto, la
factura trae un precio que no es el pactado. Por eso el ciclo de compra tiene
los mismos cuatro documentos que el de venta, pero al revés: **presupuesto →
pedido → recepción → factura**, y luego el pago.

## Antes de empezar

- `verificar.py` en verde y copia de seguridad del día anterior.
- Tu bandeja: `salida/<sector>-A<NN>/bandejas/s19-compras.md`
  (si no la tienes, vuelve a ejecutar `generar.py`).

## Los pasos

### 0. ¿Odoo compra solo? No

Conviene tenerlo claro antes de tocar nada, porque es la duda de todo el mundo al
ver el aviso de reposición:

- **Odoo no envía ningún pedido a ningún proveedor.** Ni en la 19 ni en ninguna
  otra versión. No hay correo saliente en el aula y, aunque lo hubiera, el envío
  es siempre un acto humano.
- Lo que hace la **regla de reabastecimiento** (el mínimo y el máximo de cada
  producto) es *proponer*. La propuesta aparece en **Inventario → Operaciones →
  Abastecimiento** con la cantidad que falta para llegar al máximo.
- Esa regla tiene un **disparador**:
  - *Manual*: solo propone. Tú decides si compras. **Es como están las del
    repositorio**, para que veas la propuesta antes de que se convierta en algo.
  - *Automático*: el planificador (un proceso que corre a diario, o el botón
    *Ejecutar planificador*) crea **borradores** de pedido de compra agrupados
    por proveedor. Borradores: *Solicitudes de presupuesto*, sin confirmar. Nadie
    las envía.
- Si un producto **no tiene proveedor**, Odoo no puede proponer nada: no sabe a
  quién comprar. Sale marcado en Inventario y la regla no genera propuesta. Se
  arregla con `cargar_historico.py --solo-proveedores`, que asigna a cada
  producto el proveedor de su catálogo con su precio y su plazo de entrega.

> En una empresa real el disparador suele estar en automático y alguien revisa
> cada mañana las solicitudes de presupuesto antes de confirmarlas. Automatizar
> la *propuesta* es lo que ahorra trabajo; automatizar la *compra* es lo que
> arruina a una empresa.

### 1. Ver qué falta reponer

**Inventario → Operaciones → Abastecimiento**. Si no hay propuestas, pulsa
**Abastecimiento: ejecutar planificador** (arriba a la derecha). Odoo compara el
stock con las reglas de mínimo y máximo de cada producto y propone cantidades.

También sirve mirar **Inventario → Informes → Stock** y filtrar por *Cantidad
disponible* menor que el mínimo.

### 2. Del aviso al pedido de compra

**Compra → Pedidos → Solicitudes de presupuesto → Nuevo** (o confirmar la
propuesta del planificador).

- Proveedor y líneas: producto, cantidad y precio. El precio se toma del coste o
  de la lista de precios de proveedor si la hay.
- Fecha prevista: cuándo esperas recibirlo. Odoo la usa para el planificador.
- **Confirmar pedido**: a partir de aquí el proveedor ya te lo puede servir.

### 3. Recepción, completa o parcial

**Inventario → Operaciones → Traslados**, filtro *Recepciones* (o el botón
inteligente *Recepción* del pedido).

- Pon la **cantidad recibida** de cada línea. Si es menos de lo pedido, valida
  igual y acepta el **albarán pendiente** con el resto.
- La fecha de la recepción es la del muelle, no la de hoy: si te llega el lunes
  y lo metes el miércoles, la recepción es del lunes (se puede corregir en el
  albarán, pestaña *Otra información*).

### 4. Factura del proveedor

**Facturación → Proveedores → Facturas**, o desde el pedido con **Crear
factura**.

Aquí se comparan tres cosas: lo pedido, lo recibido y lo facturado. Si el
proveedor factura un precio distinto al pactado, se reclama **antes** de
publicar; si ya está publicada, se le pide un **abono** (su factura
rectificativa) y se registra.

### 5. Cuando algo se rompe: ajuste de inventario

**Inventario → Operaciones → Ajustes → Nuevo.**

- Producto, ubicación y **cantidad contada** (la real, no la del sistema).
- En *Motivo* escribe qué ha pasado. Ese texto es lo que salva una auditoría.
- Aplicar. Odoo genera el movimiento y deja el stock cuadrado.

Un ajuste **no** es una compra: no hay proveedor ni factura, y la pérdida va a
la cuenta de mermas. Por eso hay que documentarlo.

### 6. Devolución al proveedor (si te toca)

Desde la recepción, **Devolver**. Se genera un albarán de devolución (salida de
stock) y el proveedor debe emitir el abono. No se «borra» la recepción: se
devuelve, y queda el rastro de las dos operaciones.

## Tu ejercicio

Resuelve los sucesos de `s19-compras.md` en orden. Fíjate en que algunos son
compras de **servicio** (no mueven stock) y otros de mercancía.

## Comprueba tu trabajo

- [ ] El pedido de compra está confirmado y su recepción hecha.
- [ ] Si la recepción fue parcial, hay **dos recepciones**: una *Hecha* y otra
      pendiente.
- [ ] El ajuste de inventario tiene motivo escrito y el stock coincide con lo
      que hay físicamente.
- [ ] Ningún producto ha quedado con stock negativo.
- [ ] La factura del proveedor está registrada y, si hubo reclamación, consta.
- [ ] El coste actualizado del producto se ve en su ficha (pestaña *Compra*).
- [ ] `verificar.py` sigue en verde.

## Si algo falla

**El planificador no propone nada.** O el producto no tiene regla de
reabastecimiento (mínimo/máximo), o no tiene proveedor, o su stock está por
encima del mínimo. La regla se configura en la ficha del producto, pestaña
*Inventario* → *Reglas de reabastecimiento*; el proveedor, en la pestaña
*Compra* (y se repara con `cargar_historico.py --solo-proveedores`).

**En Inventario aparecen productos «sin proveedor».** No tienen ficha de
proveedor (`product.supplierinfo`): el planificador no sabe a quién comprar y no
propone nada. Se arregla con `cargar_historico.py --solo-proveedores`.

**Veo solicitudes de presupuesto que no he creado yo.** Alguna regla tiene el
disparador en *Automático* y el planificador diario las ha creado. Son
borradores: ni se han confirmado ni se han enviado. Se descartan sin más, o se
cambia el disparador a *Manual* en la regla.

**«No se puede validar: cantidad mayor que la reservada».** Estás poniendo más
cantidad de la que el sistema espera. Revisa las unidades: a veces el CSV trae
el producto en unidades y tú estás pensando en cajas.

**La recepción no aparece en Traslados.** Filtra por tipo *Recepciones* y quita
los filtros por defecto; o entra por el botón inteligente del pedido.

**La factura del proveedor no cuadra con el pedido.** Compara línea a línea:
cantidad recibida ≠ facturada es lo más habitual. Si el proveedor factura lo
pedido y tú recibiste menos, reclama antes de publicar.

**He aplicado un ajuste y el stock sigue igual.** Mira la fecha del movimiento:
si es futura, no cuenta todavía. Y comprueba que la ubicación es la interna
correcta (WH/Stock), no una ubicación virtual.
