# Ensayo de la demo (profesor)

Guion corto para tener la demo lista y probada **antes** de clase. No es el
guion completo de la sesión (ese vive en el repositorio privado, con los tiempos
y las preguntas del alumnado): esto es la preparación técnica y el recorrido que
hay que haber hecho una vez en frío.

## Las dos bases de la demo

| Base | Para qué | Cómo se crea |
|---|---|---|
| `demo` | Demo de la **S16**: compañía vacía que se configura en directo. | `./instalar.sh --bd demo` |
| `demo-cargada` | Demos de **S17 a S19**: maestros, stock e histórico ya cargados. | `./instalar.sh --sector _demo-tostadero --alumno 0 --completo --bd demo-cargada` |

La primera tarda un minuto; la segunda, cuatro o cinco (importa 29 productos, 18
clientes, 72 ventas y 18 compras).

> En Windows, `.\instalar.ps1` con los mismos parámetros. Si PowerShell se queja
> de la política de ejecución:
> `powershell -ExecutionPolicy Bypass -File .\instalar.ps1 ...`

## Antes de clase (10 minutos)

```bash
./instalar.sh --bd demo
./instalar.sh --sector _demo-tostadero --alumno 0 --completo --bd demo-cargada
```

Comprobaciones rápidas:

- [ ] `docker compose ps` muestra `db` y `odoo` en marcha.
- [ ] Las dos bases aparecen en <http://localhost:8069/web/database/selector>.
- [ ] En `demo-cargada`, **Ventas → Pedidos** tiene 72 pedidos y **Facturación →
      Clientes → Facturas** tiene 72 facturas publicadas.
- [ ] En `demo-cargada`, **Inventario → Operaciones → Abastecimiento** propone
      reposiciones (hay cinco productos bajo mínimo).
- [ ] Las copias de seguridad de partida están en `salida/`:
      `docker compose run --rm odoo db dump demo-cargada /repo/salida/demo-cargada.zip`

## Recorrido de la demo de S16 (25 min)

Se hace sobre `demo`, **vacía a propósito**: lo que se enseña es justo lo que aún
no está.

1. **Crear la base delante de ellos** (2 min). Si se hace por línea de comandos,
   que vean la orden y qué significa `--country ES`:
   ```bash
   docker compose run --rm odoo db init demo --country ES --language es_ES --password admin
   ```
   Y después instalar las cinco aplicaciones. Mientras carga, se explica qué es
   una localización.
2. **Compañía** (6 min): *Ajustes → Usuarios y compañías → Compañías*. Nombre,
   NIF (que falle uno a propósito para enseñar la validación), dirección, país,
   moneda, logo. Aquí se explica razón social, NIF y domicilio fiscal.
3. **Impuestos** (5 min): *Facturación → Configuración → Contabilidad →
   Impuestos*. Enseñar «21% B» y «21% S», y **archivar los zombis** de 2023-24
   (`2% B`, `5% B`, `7.5% B`). Es el momento de explicar IVA repercutido y
   soportado.
4. **Usuarios** (6 min): *Ajustes → Usuarios y compañías → Usuarios*. Crear
   *Comercial* (Ventas: «Usuario: Mostrar todos los documentos» + Facturación) y
   *Almacén* (Inventario: Usuario). Cerrar sesión y entrar con cada uno para
   enseñar que ven menús distintos.
5. **Copia de seguridad** (3 min): `docker compose run --rm odoo db dump demo
   /repo/salida/copia-S16-demo.zip`. Explicar qué lleva dentro (base + filestore).

## Recorrido de la demo de S18 (30 min), sobre `demo-cargada`

Se elige **un** suceso de la bandeja de la demo (por ejemplo el presupuesto del
hotel, `s18-ventas.yaml`, suceso 2) y se hace el ciclo entero:

oportunidad en CRM → presupuesto → confirmar → entrega parcial → factura de lo
entregado → cobro parcial → y enseñar los botones inteligentes que enlazan los
documentos.

Lo que **debe verse** al final, para saber que la demo va bien:

- El pedido queda en *A facturar* (no «Completamente facturado»), porque hay
  entrega parcial.
- Hay **dos albaranes**: uno *Hecho* y otro pendiente.
- La factura está *Parcialmente pagada* y muestra el importe pendiente.

## Plan B si algo falla en directo

- **Odoo no arranca**: `docker compose up -d` y esperar. Si sigue, `docker
  compose logs --tail 30 odoo`.
- **Una demo se ha quedado a medias**: `docker compose run --rm odoo db load
  demo /repo/salida/demo-cargada.zip --force` y se vuelve al punto de partida.
  Tener el ZIP hecho **antes** de clase es lo que salva la sesión.
- **No hay internet**: las imágenes ya están descargadas; el compose no necesita
  red salvo la primera vez.

## Después de clase

```bash
docker compose down          # conserva los datos
# docker compose down -v     # borra bases y filestore (solo si hay copia)
```
