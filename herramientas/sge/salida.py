"""Escritura de la variante: CSV para el importador de Odoo y documentos."""
from __future__ import annotations

import json
import pathlib

from . import provincias
from .catalogo import Empresa
from .maestros import Maestros
from .util import escribir_csv, escribir_texto, euros

COLUMNAS_CATEGORIAS = ["id", "name", "parent_id"]
COLUMNAS_TARIFAS = ["id", "name", "currency_id"]
COLUMNAS_REGLAS = ["id", "pricelist_id", "applied_on", "compute_price", "percent_price", "min_quantity"]
COLUMNAS_PRODUCTOS = [
    "id", "name", "default_code", "categ_id", "list_price", "standard_price",
    "type", "is_storable", "purchase_ok", "sale_ok", "barcode",
]
COLUMNAS_CONTACTOS = [
    "id", "name", "is_company", "vat", "street", "zip", "city", "state_id",
    "country_id", "phone", "email", "ref", "property_payment_term_id",
    "property_product_pricelist", "customer_rank", "supplier_rank", "lang", "comment",
]

NOMBRE_FICHEROS = {
    "categorias": "1-categorias-producto.csv",
    "tarifas": "2-tarifas.csv",
    "productos": "4-productos.csv",
    "proveedores": "5-proveedores.csv",
    "clientes": "6-clientes.csv",
}


def _si(valor: bool) -> str:
    return "True" if valor else "False"


def escribir_csvs(destino: pathlib.Path, m: Maestros) -> dict[str, pathlib.Path]:
    rutas = {}

    # Resto de versiones anteriores: el CSV de reglas de tarifa ya no se genera
    # (la lista de reglas no tiene botón de importación). Si quedó de una
    # ejecución anterior, confunde.
    (destino / "3-reglas-tarifa.csv").unlink(missing_ok=True)

    rutas["categorias"] = destino / NOMBRE_FICHEROS["categorias"]
    escribir_csv(rutas["categorias"], COLUMNAS_CATEGORIAS, [
        {"id": c["id"], "name": c["nombre"]} for c in m.categorias
    ])

    con_descuento = [t for t in m.tarifas if t["descuento"]]
    rutas["tarifas"] = destino / NOMBRE_FICHEROS["tarifas"]
    escribir_csv(rutas["tarifas"], COLUMNAS_TARIFAS, [
        {"id": t["id"], "name": t["nombre"], "currency_id": "EUR"} for t in con_descuento
    ])


    rutas["productos"] = destino / NOMBRE_FICHEROS["productos"]
    escribir_csv(rutas["productos"], COLUMNAS_PRODUCTOS, [
        {
            "id": p["id"],
            "name": p["nombre"],
            "default_code": p["ref"],
            "categ_id": p["categoria_nombre"],
            "list_price": f"{p['pvp']:.2f}",
            "standard_price": f"{p['coste']:.2f}",
            "type": "service" if p["tipo"] == "servicio" else "consu",
            "is_storable": _si(p["tipo"] == "almacenable"),
            "purchase_ok": _si(p["compra"]),
            "sale_ok": _si(p["venta"]),
            "barcode": p["barcode"],
        }
        for p in m.productos
    ])

    def contacto(c: dict, cliente: bool) -> dict:
        return {
            "id": c["id"],
            "name": c["nombre"],
            "is_company": _si(c["es_empresa"]) if cliente else "True",
            "vat": c["nif"],
            "street": c["calle"],
            "zip": c["cp"],
            "city": c["poblacion"],
            "state_id": provincias.odoo(c["provincia"]),
            "country_id": "España",
            "phone": c["telefono"],
            "email": c["email"],
            "ref": c["ref"] if cliente else c["clave"],
            "property_payment_term_id": c["cond_pago"],
            "property_product_pricelist": c.get("tarifa_nombre", "") if cliente else "",
            "customer_rank": "1" if cliente else "0",
            "supplier_rank": "0" if cliente else "1",
            "lang": "es_ES",
            "comment": c.get("comentario", ""),
        }

    nombres_tarifa = {t["clave"]: t["nombre"] for t in m.tarifas}
    for c in m.clientes:
        c["tarifa_nombre"] = nombres_tarifa.get(c.get("tarifa"), "")

    rutas["proveedores"] = destino / NOMBRE_FICHEROS["proveedores"]
    escribir_csv(rutas["proveedores"], COLUMNAS_CONTACTOS, [contacto(p, cliente=False) for p in m.proveedores])

    rutas["clientes"] = destino / NOMBRE_FICHEROS["clientes"]
    escribir_csv(rutas["clientes"], COLUMNAS_CONTACTOS, [contacto(c, cliente=True) for c in m.clientes])

    return rutas


def escribir_resumen(destino: pathlib.Path, e: Empresa, m: Maestros) -> pathlib.Path:
    """JSON con todo lo generado. Lo usa el resolvedor del repositorio privado."""
    ruta = destino / "resumen.json"
    datos = {
        "empresa": e.clave,
        "identidad": m.empresa,
        "categorias": m.categorias,
        "tarifas": m.tarifas,
        "productos": m.productos,
        "proveedores": m.proveedores,
        "clientes": m.clientes,
    }
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta


def escribir_datos_empresa(destino: pathlib.Path, e: Empresa, m: Maestros) -> pathlib.Path:
    """Ficha de identidad fiscal: lo que hay que teclear en Ajustes → Compañías."""
    d = m.empresa
    texto = f"""# Datos de la compañía — {d['nombre']}

> Todos los datos de esta empresa son ficticios. El NIF tiene dígito de control
> válido (si no, Odoo lo rechaza), pero no corresponde a ninguna empresa real.

| Campo en Odoo | Valor |
|---|---|
| Nombre de la compañía | `{d['nombre']}` |
| NIF | `{d['cif']}` |
| Dirección | {d['domicilio']} |
| C.P. / Ciudad | {d['cp']} — {d['poblacion']} |
| Provincia | {d['provincia']} |
| País | España |
| Moneda | EUR (euro) |
| Teléfono | {d['telefono']} |
| Correo electrónico | {d['email']} |
| Sitio web | {d['web']} |
| IBAN de la cuenta de la empresa | `{d['iban']}` |

Condiciones comerciales:

- Forma de pago **a clientes**: {d['cond_pago_ventas']}.
- Forma de pago **a proveedores**: {d['cond_pago_compras']}.

Al terminar, comprueba en **Ajustes → Usuarios y compañías → Compañías** que el
país es España y la moneda EUR. Si la moneda ha quedado en USD, es que se
instaló Facturación antes de poner el país: hay que rehacer la base de datos
(ver la guía S16).
"""
    ruta = destino / "datos-empresa.md"
    escribir_texto(ruta, texto)
    return ruta


def escribir_leeme(destino: pathlib.Path, e: Empresa, m: Maestros) -> pathlib.Path:
    n_prod = len(m.productos)
    n_serv = sum(1 for p in m.productos if p["tipo"] == "servicio")
    total = len(m.clientes) + len(m.proveedores)
    texto = f"""# Tu empresa: {m.empresa['nombre']}

Carpeta generada automáticamente por `generar.py`. **No la edites a mano**: si
vuelves a generar tu variante se sobrescribe.

## Qué hay aquí

| Fichero | Para qué |
|---|---|
| `datos-empresa.md` | Los datos fiscales que configuras en Odoo (sesión S16). |
| `maestros/1-categorias-producto.csv` | {len(m.categorias)} familias de producto. |
| `maestros/2-tarifas.csv` | {len([t for t in m.tarifas if t['descuento']])} listas de precios con descuento. |
| `maestros/4-productos.csv` | {n_prod} productos ({n_serv} de ellos son servicios). |
| `maestros/5-proveedores.csv` | {len(m.proveedores)} proveedores. |
| `maestros/6-clientes.csv` | {len(m.clientes)} clientes. |
| `resumen.json` | Los mismos datos en crudo (lo usa el profesor para corregir). |

## En qué orden se importan (sesión S17)

El orden **no es opcional**: los productos necesitan las categorías y los
clientes necesitan las tarifas.

0. **Antes de nada**: **Ajustes → Ventas → Precios → Listas de precios**. Sin
   este interruptor el menú de listas de precios no existe y la columna de tarifa
   de los clientes no se mapea.
1. `1-categorias-producto.csv` → menú **Ventas → Configuración → Productos →
   Categorías** (botón *Importar registros*).
2. `2-tarifas.csv` → **Ventas → Productos → Listas de precios**.
3. `4-productos.csv` → **Ventas → Productos → Productos**.
4. `5-proveedores.csv` y `6-clientes.csv` → **Contactos**.

El descuento de cada tarifa **no va en un CSV**: la pestaña *Reglas* de una lista
de precios es una lista incrustada y no tiene botón *Importar*. Lo crea
`cargar_historico.py` (paso 6) y `verificar.py` lo comprueba.

En cada importación: carga el fichero, comprueba que las columnas se han mapeado
solas (los encabezados son los nombres técnicos de los campos de Odoo), pulsa
**Probar** antes de **Importar** y lee los avisos. Si abres el importador desde
el menú equivocado, media tabla sale sin mapear: cierra y entra por el menú que
toca.

## Lo que el CSV no trae a propósito

- **Los impuestos (IVA)**: en la localización española el impuesto de venta y el
  de compra se llaman igual («21% B»), y el importador no distingue uno de otro:
  asigna el que le parece o deja la celda vacía. Los asigna el script
  `cargar_historico.py` según la familia de producto, y `verificar.py` comprueba
  que han quedado bien.
- **El stock inicial**: lo pone también `cargar_historico.py`, porque depende del
  histórico que se carga a la vez.
"""
    ruta = destino / "LEEME.md"
    escribir_texto(ruta, texto)
    return ruta


def copiar_ficha(destino: pathlib.Path, e: Empresa, m: Maestros, alumno: int) -> pathlib.Path:
    """FICHA del sector + bloque con los datos de esta variante."""
    origen = e.carpeta / "FICHA.md"
    d = m.empresa
    bloque = f"""

---

## Tus datos (variante A{alumno:02d})

Los datos fiscales exactos de tu variante están en `datos-empresa.md`. Los que
cambian respecto al ejemplo de la ficha son:

- **Nombre completo**: `{d['nombre']}`
- **NIF**: `{d['cif']}`
- **IBAN**: `{d['iban']}`
- **Teléfono**: `{d['telefono']}`

Los precios y las cantidades de tu catálogo también son los tuyos: no coinciden
con los de otro alumno del mismo sector.
"""
    contenido = origen.read_text(encoding="utf-8") if origen.is_file() else f"# {d['nombre']}\n"
    ruta = destino / "FICHA.md"
    escribir_texto(ruta, contenido.rstrip() + bloque)
    return ruta
