# Tipos de IVA por familia de producto — península y Baleares, noviembre de 2026

> **Uso en el repositorio.** Los tipos de la columna «IVA de venta» son los que
> llevan las `categorias` de cada catálogo (y, cuando el producto se aparta de su
> familia, su `iva_venta`/`iva_compra`). Si cambias un tipo, cambia también la
> tabla de IVA de la `FICHA.md` del sector: el alumnado la lee para decidir qué
> impuesto poner en cada producto.
>
> Dos datos son **criterio interpretativo**, no consulta vinculante: el café
> verde (10 %) y el lúpulo (21 %). Están señalados en la tabla y en las fichas.

> Referencia normativa: Ley 37/1992 (LIVA), arts. 90 y 91, y tabla oficial «Tipos impositivos en el IVA 2026» de la AEAT (versión de 07/05/2026). Los nombres de impuesto entre comillas invertidas son los que crea la localización española de Odoo 19 (`l10n_es`).

| Familia | IVA de venta | IVA de compra | Justificación breve | Fuente (URL) |
|---|---|---|---|---|
| **1. Café verde en grano** (materia prima para tostar) | **10 %** · `10% B` | **10 %** · `10% UE B` (compra intracomunitaria) o `10% EX B` (importación) | Producto vegetal destinado a la obtención de un alimento (café tostado): art. 91.Uno.1.1.º y 2.º LIVA. La partida 0901 (café, incluido el verde) se clasifica al 10 %. No hay consulta vinculante específica para «café verde»: es el punto a confirmar si se quiere cerrar al 100 %. | [AEAT Tipos IVA 2026](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/IVA_reperc/Tipos_IVA_2026.pdf) · [LIVA art. 91](https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740) |
| **2. Café tostado en grano y molido, envasado** | **10 %** · `10% B` | **10 %** (café verde) + **21 %** (envase, etiqueta, caja) | Alimento del art. 91.Uno.1.1.º. Vender a hostelería **no** cambia el tipo: el 10 % de hostelería grava el servicio de bar/restaurante, no el grano vendido como mercancía. | [AEAT Manual IVA 2026, tipo 10 %](https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/manual-iva-2026/capitulo-04-sujetos-pasivos-repercusion-impositivo/tipo-impositivo/tipo-impositivo-reducido-10-ciento.html) |
| **3. Cápsulas y monodosis de café** | **10 %** · `10% B` | **10 %** (café) + **21 %** (cápsula, film, caja) | La DGT califica la cápsula como entrega de café al 10 % (art. 91.Uno.1.1.º); la máquina de café, en cambio, va al 21 %. El Impuesto sobre envases de plástico no reutilizables (0,45 €/kg) es independiente y no altera el tipo. | [DGT V4893-16](https://petete.tributos.hacienda.gob.es/consultas/?num_consulta=V4893-16) · [DGT V1578-18](https://petete.tributos.hacienda.gob.es/consultas/?num_consulta=V1578-18) |
| **4. Cerveza artesanal** (barril y botella) | **21 %** · `21% B` | **10 %** malta y levadura · **21 %** lúpulo, envases, etiquetas | Bebida alcohólica: excluida expresamente del 10 % (art. 91.Uno.1.1.º, último inciso). Si se sirve en el propio brewpub para consumir en el local, ese servicio va al **10 %** (`10% S`). | [AEAT Tipos IVA 2026](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/IVA_reperc/Tipos_IVA_2026.pdf) |
| **5. Malta, lúpulo y levadura** (materias primas) | Malta **10 %** · Levadura **10 %** · Lúpulo **21 %** | **10 %** (cereal/malta) · **21 %** (resto de insumos) | Malta: producto alimenticio de cereales (partida 1107). Levadura: DGT V0238-15, 10 % si es apta para obtener productos del 10 %. Lúpulo: no es alimento y no sirve para obtener un producto del 10 % (la cerveza está excluida) → 21 %. **No he localizado consulta específica sobre malta ni lúpulo**; el lúpulo es el dato más discutible de la tabla. | [DGT V0238-15](https://petete.tributos.hacienda.gob.es/consultas/?num_consulta=V0238-15) · [LIVA art. 91](https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740) |
| **6. Bicicletas, recambios y accesorios; taller** | **21 %** · `21% B` (taller: `21% S`) | **21 %** · `21% UE B` / `21% EX B` | No figuran en el art. 91 → tipo general del art. 90.Uno. La rebaja al 10 % se ha reclamado por el sector, pero **no se ha aprobado**. La mano de obra de taller es servicio y va al 21 %. | [AEAT Tipos IVA 2026](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/IVA_reperc/Tipos_IVA_2026.pdf) |
| **7. Material de oficina** (papel, bolígrafos, tóner, archivo, mobiliario) | **21 %** · `21% B` | **21 %** | Tipo general. Solo libros, periódicos y revistas tienen el 4 %; el papel de oficina, la papelería y el mobiliario no están en el art. 91. | [AEAT Tipos IVA 2026](https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/IVA_reperc/Tipos_IVA_2026.pdf) |
| **8. Aceite de oliva virgen extra** (botella y lata) | **4 %** · `4% B` | **4 %** aceituna (o compensación REAGP del 12 %) · **21 %** envases | Art. 91.Dos.1.1.º.g) LIVA: «Los aceites de oliva» al 4 % **permanente desde el 1-1-2025** (RDL 4/2024). Se aplica igual vendiendo a tienda o a hostelería: es entrega de bien, no servicio. | [AEAT Manual IVA 2025, novedades](https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/manual-iva-2025/capitulo-01-novedades-destacar-2025/tipos-impositivos.html) · [RDL 4/2024](https://www.boe.es/buscar/act.php?id=BOE-A-2024-12944) |
| **9. Plantas ornamentales y jardín** | Plantas **10 %** · Sustratos y fertilizantes **10 %** · Herramientas **21 %** · Diseño y mantenimiento **21 %** (`21% S`) | **10 %** planta y sustrato · **21 %** herramienta y maquinaria | Art. 91.Uno.1.8.º (flores y plantas vivas de carácter ornamental), 1.3.º (fertilizantes, correctores y enmiendas). El 10 % de jardines solo cubre la limpieza de parques y jardines **públicos** (2.5.º): la jardinería privada va al 21 %. | [AEAT Manual IVA 2026, tipo 10 %](https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/manual-iva-2026/capitulo-04-sujetos-pasivos-repercusion-impositivo/tipo-impositivo/tipo-impositivo-reducido-10-ciento.html) |

## Cambios normativos 2022-2026

- **2022-2023:** rebajas temporales de IVA en energía (luz y gas al 5 %/10 %) y carburantes. Todas eran temporales y ya están revertidas; no afectan a ninguna de las nueve familias.
- **1-1-2023 (RDL 20/2022):** alimentos básicos al **0 %** y aceites y pasta al **5 %**.
- **2023 y primer semestre de 2024:** prórrogas sucesivas; el RDL 8/2023 (art. 20) mantiene el 0 %/5 % hasta el 30-6-2024.
- **1-10-2024 (RDL 4/2024, art. 1):** salida gradual: básicos al **2 %** y aceites de semillas y pasta al **7,5 %**, hasta el 31-12-2024.
- **1-1-2025:** vuelta a los tipos ordinarios (básicos 4 %; aceites de semillas y pasta 10 %) y, sobre todo, **el aceite de oliva se incorpora con carácter permanente al 4 %** mediante nuevo art. 91.Dos.1.1.º.g) LIVA. No es una prórroga: no decae.
- **2025:** sin rebajas temporales en alimentación. Solo el 4 % estructural del AOVE y la leche fermentada al 4 % desde el 22-12-2024.
- **2026 (RDL 7/2026, de 20 de marzo):** rebaja coyuntural de luz, gas y carburantes al 10 % del 22-3 al 31-5-2026 (carburantes hasta 30-6). Desde el 1-6 y el 1-7-2026 vuelven al **21 %**; en noviembre de 2026 ya está todo al 21 %.
- **Noviembre de 2026:** no queda ninguna rebaja temporal en alimentación. Rigen 21 %, 10 % y 4 %, más el 0 % en supuestos tasados (donativos, etc.).
- **Recargo de equivalencia:** sin cambios desde 2012: **5,2 % / 1,4 % / 0,5 %** (y 1,75 % para labores del tabaco).

## Notas para la ficha del alumno

1. **Bienes vs. servicios en Odoo 19.** `21% B` es bien (`tax_scope = consu`) y `21% S` es servicio (`tax_scope = service`). Es el mismo tipo y la misma cuota: cambia la cuenta contable, el tratamiento en las declaraciones y el comportamiento en operaciones intracomunitarias. Regla práctica: si se entrega una cosa → B; si se presta un trabajo → S.
2. **Nombres reales de la localización española** (verificados en `l10n_es` de Odoo 19): `21% B`, `21% S`, `10% B`, `10% S`, `4% B`, `4% S`; para compras exteriores `10% UE B` (adquisición intracomunitaria) y `10% EX B` (importación). Recargo: `5.2% RE`, `1.4% RE`, `0.5% RE`.
3. **Impuestos obsoletos que Odoo sigue trayendo.** La plantilla de Odoo 19 aún incluye `0% B`, `2% B` y `7.5% B`/`7.5% S`, restos de las rebajas de 2023-2024. Hay que **archivarlos** en la base de datos del aula para que no se seleccionen por error: ya no existen en la normativa.
4. **Un mismo producto, dos tipos según la operación.** Cerveza en botella vendida para llevar: 21 % como bien. Caña servida en el local: 10 % como servicio de hostelería. Bicicleta vendida: 21 %; mano de obra del taller: 21 % como servicio (mismo tipo, distinto impuesto en Odoo).
5. **Aceite de oliva.** El 4 % no depende del envase (botella o lata) ni del cliente (tienda u hostelería). Ojo: el 4 % alcanza a los «aceites de oliva»; el aceite de orujo de oliva (partida 1510) no está en esa letra y tributa al 10 % — conviene no incluirlo en la misma ficha sin comprobarlo.
6. **Recargo de equivalencia.** Si alguna de las seis empresas es minorista persona física en RE, sus compras llevan el recargo (5,2 %/1,4 %/0,5 %) y **no deduce** el IVA soportado. En Odoo se marca la posición fiscal del cliente/proveedor, no el impuesto a mano.
7. **REAGP.** Si el vivero o la almazara son explotación agrícola en REAGP, no repercuten IVA: el cliente paga una **compensación a tanto alzado del 12 %** (agrícola y forestal) o **10,5 %** (ganadera y pesquera), que sí deduce. Es la excepción que rompe la lógica «4 %/10 %» de la tabla.
8. **Inversión del sujeto pasivo.** Las compras intracomunitarias (`10% UE B`) y las importaciones (`10% EX B`, con DUA) se autoliquidan: el alumno debe ver que el IVA de compra aparece como repercutido y soportado a la vez. Los servicios de proveedores extranjeros (p. ej. un diseño de jardín encargado a Portugal) van con inversión del sujeto pasivo al 21 %.
9. **Jardinería.** Diseño y mantenimiento periódico: 21 %. Solo las obras de **renovación o reparación en vivienda** pueden bajar al 10 % si se cumplen los tres requisitos del art. 91.Uno.2.19.º (destinatario particular o comunidad, edificio con más de 2 años, materiales ≤ 40 % de la base).
10. **Dos datos a confirmar antes de publicar.** No he localizado consulta vinculante específica sobre **café verde** ni sobre **lúpulo**; ambos están resueltos por interpretación del art. 91 (10 % y 21 % respectivamente). Si la ficha los presenta como dato cerrado, conviene una consulta a la AEAT o marcar la casilla como «criterio interpretativo».

---

### Fuentes oficiales utilizadas

- AEAT, *Tipos impositivos en el IVA 2026* (07/05/2026): https://sede.agenciatributaria.gob.es/static_files/Sede/Tema/IVA/IVA_reperc/Tipos_IVA_2026.pdf
- AEAT, Manual práctico IVA 2026, cap. 4 (tipo reducido 10 %) y cap. 6 (RE y REAGP).
- Ley 37/1992, arts. 90 y 91: https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740
- RDL 20/2022: https://www.boe.es/buscar/act.php?id=BOE-A-2022-22685 · RDL 8/2023: https://www.boe.es/buscar/act.php?id=BOE-A-2023-26452 · RDL 4/2024: https://www.boe.es/buscar/act.php?id=BOE-A-2024-12944
- RDL 7/2026 (energía): https://www.boe.es/buscar/act.php?id=BOE-A-2026-6544
- DGT: V4893-16 (cápsulas), V1578-18 (cápsulas), V0238-15 (levaduras).
