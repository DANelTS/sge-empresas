"""Nombres de provincia tal como los escribe Odoo 19 con la localización española.

Odoo usa la denominación bilingüe oficial en las provincias con dos nombres
(«Alacant (Alicante)», «Bizkaia (Vizcaya)»…). En los catálogos escribimos el
nombre corto y aquí se traduce al que hay que poner en el CSV: si no coincide
exactamente, el importador no encuentra la provincia y la fila falla.

Fuente: lista de `res.country.state` para ES en Odoo 19 (comprobada en la 19.0).
"""

PROVINCIAS = {
    "A Coruña": "A Coruña (La Coruña)",
    "La Coruña": "A Coruña (La Coruña)",
    "Álava": "Araba/Álava",
    "Araba": "Araba/Álava",
    "Albacete": "Albacete",
    "Alicante": "Alacant (Alicante)",
    "Almería": "Almería",
    "Asturias": "Asturias",
    "Ávila": "Ávila",
    "Badajoz": "Badajoz",
    "Barcelona": "Barcelona",
    "Burgos": "Burgos",
    "Cáceres": "Cáceres",
    "Cádiz": "Cádiz",
    "Cantabria": "Cantabria",
    "Castellón": "Castelló (Castellón)",
    "Ceuta": "Ceuta",
    "Ciudad Real": "Ciudad Real",
    "Córdoba": "Córdoba",
    "Cuenca": "Cuenca",
    "Girona": "Girona (Gerona)",
    "Gerona": "Girona (Gerona)",
    "Granada": "Granada",
    "Guadalajara": "Guadalajara",
    "Guipúzcoa": "Gipuzkoa (Guipúzcoa)",
    "Gipuzkoa": "Gipuzkoa (Guipúzcoa)",
    "Huelva": "Huelva",
    "Huesca": "Huesca",
    "Baleares": "Illes Balears (Islas Baleares)",
    "Jaén": "Jaén",
    "León": "León",
    "Lleida": "Lleida (Lérida)",
    "Lérida": "Lleida (Lérida)",
    "Lugo": "Lugo",
    "Madrid": "Madrid",
    "Málaga": "Málaga",
    "Murcia": "Murcia",
    "Navarra": "Navarra (Nafarroa)",
    "Ourense": "Ourense (Orense)",
    "Orense": "Ourense (Orense)",
    "Palencia": "Palencia",
    "Las Palmas": "Las Palmas",
    "Pontevedra": "Pontevedra",
    "La Rioja": "La Rioja",
    "Salamanca": "Salamanca",
    "Santa Cruz de Tenerife": "Santa Cruz de Tenerife",
    "Segovia": "Segovia",
    "Sevilla": "Sevilla",
    "Soria": "Soria",
    "Tarragona": "Tarragona",
    "Teruel": "Teruel",
    "Toledo": "Toledo",
    "Valencia": "València (Valencia)",
    "Valladolid": "Valladolid",
    "Bizkaia": "Bizkaia (Vizcaya)",
    "Vizcaya": "Bizkaia (Vizcaya)",
    "Zamora": "Zamora",
    "Zaragoza": "Zaragoza",
    "Melilla": "Melilla",
}


def odoo(provincia: str) -> str:
    """Devuelve el nombre exacto que espera Odoo; error si no está en la tabla."""
    try:
        return PROVINCIAS[provincia]
    except KeyError:
        raise ValueError(f"provincia desconocida: {provincia!r} (añádela a provincias.py)")
