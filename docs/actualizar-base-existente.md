# Ya tienes la base cargada: cómo ponerla al día

El repositorio cambió después de que cargaras tu empresa. Hay tres cosas nuevas
que tu base no tiene:

1. **Las listas de precios** vienen desactivadas en Odoo 19 y hay que activarlas
   en Ajustes. Sin eso, el menú *Listas de precios* no existe y la columna de
   tarifa de los clientes no se importa.
2. **Cada producto comprable necesita su proveedor** (ficha de proveedor). Sin
   ella, el planificador de la S19 no propone ninguna compra y el producto sale
   como «sin proveedor» en Inventario.
3. **Las reglas de reabastecimiento** ahora se quedan en *Manual*. Si las tenías
   en *Automático*, el planificador diario te habrá creado solicitudes de
   presupuesto que no hiciste tú.

No hay que rehacer nada ni restaurar una copia: **no se toca tu histórico ni las
operaciones que ya has hecho**.

## Pasos

### 1. Traer los cambios

```powershell
git pull
```

### 2. Regenerar tu variante

```powershell
docker compose run --rm herramientas generar.py --empresa <sector> --alumno <NN>
```

Los CSV cambian poco (aparecen proveedores nuevos en algunos sectores y la
cerveza pasa a ser «no se compra, se produce»), pero conviene tenerlos al día.

### 3. Volver a importar dos CSV

En este orden, como en la S17:

1. **Contactos → Importar** → `maestros/5-proveedores.csv`
2. **Ventas → Productos → Productos → Importar** → `maestros/4-productos.csv`

No se duplica nada: los ficheros llevan la columna `id` (identificador externo),
así que Odoo **actualiza** los registros que ya existen. El importador te dirá
que hay registros actualizados, no creados.

> Si tu sector es `aceite` o `cerveceria`, este paso es obligatorio: sus
> catálogos ganaron proveedores y la cerveza ya no se compra.
> Si es otro, puedes saltártelo, pero no molesta.

### 4. Reparar

```powershell
docker compose run --rm herramientas cargar_historico.py --empresa <sector> --alumno <NN> --reparar
```

Hace cuatro cosas, todas repetibles sin efectos raros:

- activa las listas de precios en Ajustes;
- crea los proveedores que falten;
- completa la regla de descuento de cada tarifa;
- asigna a cada producto su ficha de proveedor y pone las reglas de
  reabastecimiento en *Manual*.

Te dice cuántas cosas ha cambiado. Si lo ejecutas dos veces, la segunda sale a
cero: es la señal de que ya estaba bien.

### 5. Comprobar

```powershell
docker compose run --rm herramientas verificar.py --empresa <sector> --alumno <NN>
```

Tiene que salir en verde. Los únicos avisos normales son los de usuarios
(«solo hay un usuario interno», que se resuelve en la S16) y los de los productos
de alta manual si aún no los has creado.

## Si algo sale en rojo

| Mensaje | Qué hacer |
|---|---|
| «faltan N proveedores» | No has importado `5-proveedores.csv` (paso 3). |
| «N productos sin proveedor» | Vuelve a ejecutar el paso 4; si sigue, mira que el producto esté en `4-productos.csv`. |
| «la lista X no tiene regla de descuento» | La lista no existe: impórtala con `2-tarifas.csv` y repite el paso 4. |
| «las listas de precios están desactivadas en Ajustes» | Ejecuta el paso 4 otra vez; si no, actívalo a mano en **Ajustes → Ventas → Precios**. |
