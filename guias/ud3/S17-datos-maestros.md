# S17 · Datos maestros: importar y dar de alta

**Sesión:** martes 10 de noviembre de 2026 · 1 h
**CE que trabaja:** 3b (formularios) y 3a (manipulación de datos).

## Objetivo

Cargar en Odoo los datos maestros de tu empresa —familias de producto,
productos, tarifas, clientes y proveedores— por dos vías: **importación de CSV**
para el volumen y **formulario** para lo que se da de alta de uno en uno. Al
final, el sistema tiene que saber qué vendes, a quién y a qué precio, y debe
pasar la comprobación automática sin ningún rojo.

## Contexto empresarial: qué es un dato maestro

Los **datos maestros** son los que describen la empresa y no cambian con cada
operación: qué productos tienes, quién te compra, quién te vende, a qué precio.
Todo lo demás —pedidos, albaranes, facturas— se apoya en ellos.

Por eso un error aquí es caro: si un producto tiene el coste mal, todos los
márgenes salen mal; si un cliente tiene el IVA o la tarifa equivocada, todas sus
facturas salen mal; si un proveedor está duplicado, las compras se reparten
entre dos fichas y el histórico de compras deja de tener sentido. En una empresa
real, los datos maestros los mantiene una persona concreta y con criterios
escritos: es lo que se llama *gobierno del dato*.

En esta sesión vas a cargar unos 30 productos, 18 clientes y 6 proveedores. A
mano serían dos horas; por CSV son cinco minutos. Ese es el argumento de la
importación masiva, y también su riesgo: un CSV mal montado mete 30 errores de
una vez.

## Antes de empezar

- Tu base `empresa` con la compañía configurada (sesión S16).
- Tu variante generada:

  ```powershell
  docker compose run --rm herramientas generar.py --empresa <sector> --alumno <NN>
  ```

- Abre `salida/<sector>-A<NN>/LEEME.md`: tiene el orden exacto de importación.

## Paso 1 · Importar las familias de producto

**Ventas → Configuración → Productos → Categorías → botón *Importar registros***.

> Ojo con la ruta: en la 19 las categorías de producto cuelgan de **Ventas**, no
> de Inventario, aunque se usen en el almacén.

Fichero: `maestros/1-categorias-producto.csv`.

Comprueba la pantalla de mapeo: la columna `name` tiene que estar mapeada a
**Nombre** y `id` a **Identificador externo**. Pulsa **Probar** y luego
**Importar**.

> Para qué sirven las familias: agrupar productos para informes y para aplicar
> criterios comunes. En la UD3 las usarás para preguntar «cuánto he vendido de
> cada familia» sin escribir veinte nombres.

## Paso 2 · Importar las tarifas y sus reglas

**Ventas → Productos → Listas de precios → Importar**.

1. `maestros/2-tarifas.csv` — crea las listas (`Tarifa hostelería`,
   `Tarifa distribución`…). La moneda debe resolverse a `EUR`.
2. `maestros/3-reglas-tarifa.csv` — crea la regla de cada lista: un descuento
   porcentual global. El campo `pricelist_id` se mapea a **Lista de precios** y
   se resuelve por el nombre de la tarifa.

Si la segunda importación se queja de que no encuentra la lista de precios, es
que la primera no se ha importado (o se ha importado en otra base).

## Paso 3 · Importar los productos

**Ventas → Productos → Productos → Importar**. Fichero:
`maestros/4-productos.csv`.

Columnas y su significado:

| Columna | Campo de Odoo | Ojo con |
|---|---|---|
| `id` | Identificador externo | No lo cambies: los scripts lo usan para encontrar el producto. |
| `name` | Nombre | Es lo que ve el cliente en la factura. |
| `default_code` | Referencia interna | Tu código (`TOS-010`). Único. |
| `categ_id` | Categoría de producto | Se resuelve por nombre: tiene que existir ya (paso 1). |
| `list_price` | Precio de venta | Sin IVA. |
| `standard_price` | Coste | Sin IVA. |
| `type` | Tipo de producto | `consu` para mercancía, `service` para servicios. |
| `is_storable` | Rastrear inventario | `True` en lo que se guarda en el almacén. |
| `purchase_ok` / `sale_ok` | Compra / Ventas | Una materia prima se compra pero no se vende. |
| `barcode` | Código de barras | EAN-13 válido, por si algún día usas lector. |

**Lo que este CSV no trae, y por qué.** No hay columna de impuestos. En la
localización española el impuesto de venta y el de compra se llaman igual
(«21% B»), y el importador busca por nombre: encuentra dos, avisa y asigna el que
le parece. Por eso los impuestos los pone el script en el paso 6, que sí sabe
distinguir venta de compra. Si en la pantalla de mapeo ves que no hay columna de
impuestos, no es un error.

## Paso 4 · Importar proveedores y clientes

**Contactos → Importar**. Primero `maestros/5-proveedores.csv` y después
`maestros/6-clientes.csv`.

- `is_company` distingue empresa de particular. Un particular no lleva CIF sino
  DNI, y el contacto se trata distinto en CRM y en facturación.
- `vat` es el NIF. Odoo lo valida: los del repositorio son ficticios pero con
  dígito de control correcto.
- `state_id` se resuelve por **provincia**, y Odoo las nombra en bilingüe
  («València (Valencia)»). Si escribes «Valencia» a mano, no la encuentra.
- `property_payment_term_id` es la **condición de pago** y se resuelve por
  nombre («30 días»). Si no existe esa condición, la fila falla.
- `property_product_pricelist` es la **tarifa**; se resuelve por nombre.
- `ref` es tu código de cliente (`CLI-01`). Los scripts lo usan como respaldo.

## Paso 5 · Dar de alta a mano lo que indica la bandeja

Abre `salida/<sector>-A<NN>/bandejas/s17-altas.md`. Son **dos productos y un
proveedor** que no vienen en los CSV y que tienes que crear con el formulario,
como se hace en una empresa cuando surge un producto nuevo.

Para cada uno: **Nuevo**, rellena los campos de la especificación (referencia,
nombre, categoría, coste, precio, tipo, proveedor, mínimo y máximo), guarda y
comprueba que aparece en la lista. Fíjate en la diferencia entre *Guardar* y
*Descartar*: el segundo no avisa.

> Los productos de alta manual no llevan IVA hasta que ejecutes el paso 6: el
> script asigna impuestos a todos los productos que encuentre por referencia,
> incluidos estos.

## Paso 6 · Cargar el histórico (impuestos, stock y tres meses de actividad)

```powershell
docker compose run --rm herramientas cargar_historico.py --empresa <sector> --alumno <NN>
```

Esto hace cuatro cosas, en este orden: asigna el IVA a cada producto, fija el
stock inicial al 30/07/2026, crea las compras y crea las ventas con sus
albaranes, facturas y cobros. Tarda un par de minutos. **No lo ejecutes dos
veces**: el propio script te avisa y se para.

Después, la comprobación:

```powershell
docker compose run --rm herramientas verificar.py --empresa <sector> --alumno <NN>
```

Todo tiene que salir en verde. Si algo sale en rojo, el propio mensaje dice qué
hacer (falta un CSV, falta un impuesto, hay stock negativo…).

## Paso 7 · Copia de seguridad

```powershell
docker compose run --rm odoo db dump empresa /repo/salida/copia-S17.zip
```

## Comprueba tu trabajo

- [ ] En **Ventas → Productos** hay 30 y pico productos con su referencia, su
      categoría y su precio, y ninguno con IVA vacío.
- [ ] En **Contactos** están tus 18 clientes y tus 6 proveedores, sin duplicados.
- [ ] Los clientes de hostelería tienen asignada *Tarifa hostelería*.
- [ ] Los dos productos de la bandeja existen con los datos exactos.
- [ ] `verificar.py` termina con «todo en verde» (o solo con avisos de usuarios).
- [ ] Tienes `salida/copia-S17.zip`.

## Si algo falla

**«No matching record found for name … in field Categoría de producto».**
No has importado las categorías, o las has importado en otra base. Paso 1.

**«No matching record found for name … in field Provincia».**
La provincia está escrita en corto. Odoo espera «Alacant (Alicante)»,
«València (Valencia)», «Bizkaia (Vizcaya)»… Usa el CSV tal cual.

**«Duplicate external ID».**
Has importado el mismo fichero dos veces. Odoo no duplica: actualiza, y avisa si
el identificador ya existía. Comprueba en **Ajustes → Técnico → Secuencias e
identificadores** que no hay dos registros con el mismo `id`.

**Los acentos salen raros al abrir el CSV en Excel.**
Excel abre los CSV en la codificación de Windows y rompe los acentos. **No
guardes desde Excel**: importa el fichero original del repositorio. Si necesitas
mirarlo, ábrelo en VS Code.

**Al importar productos, la columna `categ_id` sale sin mapear.**
El nombre de la categoría del CSV no coincide exactamente con el que hay en
Odoo (un acento, un espacio). Corrige la categoría en Odoo o en el CSV, no en la
pantalla de mapeo.

**`cargar_historico.py` dice que faltan productos o clientes.**
Falta importar un CSV, o has importado una variante distinta de la que estás
cargando. Comprueba que el número de alumno es el tuyo.

**Stock negativo tras cargar el histórico.**
No debería ocurrir: el stock inicial se calcula para que no falte. Si pasa, es
un fallo del repositorio: apúntalo con la captura y avisa al profesor.
