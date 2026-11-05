# CHANGELOG — sge-empresas

Notas para el profesor: qué hay nuevo en cada entrega y qué conviene revisar.
Corresponde a los hitos del plan de trabajo de la UD3 (§7).

## 2026-11-05 · Cambio de diseño del entorno

A petición del profesor: menos acoplamiento y menos piezas propias.

- **Se retira el entrypoint** (`docker/entrada.sh`) **y el `.env`**. Ahora
  `config/odoo.conf.example` se copia a `config/odoo.conf` (que está en
  `.gitignore`) y se monta en `/etc/odoo` en solo lectura. Odoo arranca con el
  entrypoint oficial de la imagen.
- **El contenedor de Odoo deja de ver el repositorio**: solo monta `config/`,
  `addons/` y `salida/copias/`. Ya no puede leer catálogos, bandejas ni las
  variantes de otros alumnos.
- **Odoo y PostgreSQL escuchan solo en `127.0.0.1`**. Con la contraseña maestra
  conocida, publicarlos en la red del aula permitiría a cualquiera borrar la base
  del compañero desde el gestor de bases de datos.
- **Comandos nuevos**: `docker compose run --rm odoo odoo db init …` (el primer
  `odoo` es el servicio, el segundo el comando) y las copias con
  `docker compose exec odoo odoo db dump … /copias/…`.
- Instaladores actualizados: crean `config/odoo.conf` si falta y dan permisos a
  `salida/copias` (hace falta en Linux; en Windows y macOS no).

Probado con podman-compose: stack arriba con la configuración montada, base
`demo` creada y cargada (72 ventas, 18 compras, `verificar.py` en verde), copia de
seguridad escrita en `/copias` y restauración con `cp` + `db load`.

## 2026-11-05 · Segunda entrega (S18 y S19)

### Qué hay

- **Motor de bandejas** (`sge/sucesos.py`): plantillas YAML con marcas
  `{{cliente:CLI-03}}`, `{{producto:…}}`, `{{precio_tarifa:CLI-02:…}}` que se
  resuelven con los datos de cada variante. Lo que no se imprime es el bloque
  `operaciones`, que queda para el solucionario.
- **Bandejas S18** (ciclo de venta) en los seis sectores: 7-8 sucesos con
  presupuesto perdido, cambio de pedido, entrega parcial, cobro a cuenta y
  rectificativa.
- **Bandejas S19** (compras e inventario) en los seis sectores: 6 sucesos con
  reposición, recepción a medias, merma o rotura, factura con precio distinto y
  compra de servicio.
- **Guías S18 y S19** con las rutas verificadas en la 19 (incluido que el menú
  de compras se llama «Compra» en singular y que las categorías de producto
  cuelgan de Ventas).
- **`docs/modelo-de-datos.md`** y **`sql/ejemplos/`**: cuatro consultas probadas
  sobre una base real.
- **Reglas de reabastecimiento**: `cargar_historico.py` crea las de mínimo y
  máximo del catálogo (25 en la demo). Sin ellas el planificador no proponía
  nada y la S19 no se podía hacer.

### Qué está probado

- Los seis sectores generan sus seis CSV, la ficha y las bandejas S17, S18 y S19
  sin marcas sin resolver.
- Cuatro sectores cargados de punta a punta (tostadero A00, aceite A00,
  cervecería A00, bicicletas A07): 72 ventas, 18 compras, sin stock negativo y
  `verificar.py` en verde.
- El stock inicial ya es proporcional a la rotación: antes daba 22 unidades a
  todo y dejaba 48.000 € inmovilizados en bicicletas eléctricas.

### Qué conviene revisar

1. Ejecutar `docker compose` en tu equipo (aquí solo hay Podman): sigue siendo lo
   único sin probar de verdad.
2. Los precios y la coherencia comercial de las bandejas nuevas de los cinco
   sectores.
3. Que la dificultad de S18 y S19 encaje con el grupo: son 7-8 y 6 sucesos.

## 2026-11-05 · Primera entrega (H0 + H1)

### Qué hay

- **Entorno**: `docker-compose.yml` con Odoo 19 Community (`odoo:19.0`),
  PostgreSQL 17 y un servicio `herramientas` con Python y sus dependencias.
  `config/odoo.conf` y `docker/entrada.sh` resuelven la contraseña maestra desde
  `.env` (la 19 ya no la acepta por línea de comandos).
- **Seis empresas**: Tostadero Manzanares (demo del profesor), Cervecera Lúpulo
  Norte, Ciclos Rodadura, Suministros Ofimat, Cooperativa Olivar del Tajo y
  Vivero La Fresneda. Cada una con `catalogo.yaml`, `nombres.yaml` y `FICHA.md`.
- **Generador** (`generar.py`): variante determinista por (empresa, alumno) con
  NIF e IBAN válidos, precios ±10 % con terminación comercial, direcciones
  coherentes CP-provincia, clientes de una bolsa de nombres. Produce seis CSV
  para el importador de Odoo, `datos-empresa.md`, `LEEME.md`, la FICHA con los
  datos de la variante y la bandeja `s17-altas.md`.
- **Carga del histórico** (`cargar_historico.py`): asigna IVA a los productos,
  fija el stock inicial por simulación (nunca negativo), crea compras y ventas
  con albaranes, facturas, cobros totales, parciales y vencidos. Idempotente.
- **Comprobación** (`verificar.py`): aplicaciones, compañía, impuestos, maestros,
  stock, histórico y usuarios, con pista de arreglo en cada rojo.
- **Documentación**: guías S16 y S17, `herramientas/copia_seguridad.md`,
  `docs/decisiones-tecnicas.md` (once hallazgos verificados en la 19),
  `docs/glosario-empresarial.md` y README.

### Qué está probado

Sobre `odoo:19.0-20261102` + `postgres:17`, con una base creada desde cero:

- Las seis empresas generan sin errores y de forma determinista (misma pareja
  produce ficheros idénticos; dos alumnos distintos, precios distintos).
- En **tostadero** y en **aceite** (este con IVA 4/10/21 en el mismo catálogo):
  los seis CSV se importan con el asistente real sin errores ni avisos, el
  histórico carga 72 ventas y 18 compras en menos de dos minutos y
  `verificar.py` termina en verde (solo queda el aviso de usuarios, que se crean
  en la S16).
- Los seis sectores planifican su histórico con volúmenes verosímiles:
  16.700 € (aceite) a 46.400 € (bicicletas) por trimestre.

### Qué conviene que revises

1. **Ejecutar `docker compose` de verdad** en tu equipo: aquí no hay Docker, así
   que el compose está validado como YAML y cada pieza se ha probado por separado
   con Podman. Comprueba `docker compose up -d`, el healthcheck de Odoo y
   `docker compose run --rm herramientas generar.py …`.
2. **Contenido de las cinco fichas nuevas**: están escritas por agentes con el
   esquema de la demo. Revisa sobre todo precios y coherencia del sector.
3. **Tipos de IVA**: están los que fijamos (cerveza 21 %, aceite 4/10/21,
   plantas 10 %, material de oficina 21 %). Falta confirmar con la AEAT el tipo
   vigente en 2026 de alguna familia; la ficha del aceite lleva la nota.
4. **`altas_manuales`**: solo la demo tiene un bloque escrito a mano. Los otros
   cinco sectores usan un bloque derivado automáticamente; conviene escribir uno
   propio por sector para que la S17 tenga más sustancia.
5. **Usuarios de la S16**: el script no los crea (es tarea del alumno), por eso
   `verificar.py` avisa mientras no existan.

### Pendiente

Guías S18 a S21 y trabajo personal, bandejas de sucesos de S18/S19 y de la
semana de operaciones, `docs/modelo-de-datos.md`, `sql/ejemplos/` y el
repositorio privado `sge-profesor`.
