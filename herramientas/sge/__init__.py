"""Paquete de herramientas de sge-empresas.

Módulos:
- `nif`       generación y validación de NIF, CIF, NIE e IBAN
- `util`      redondeos comerciales, escritura de CSV y textos
- `catalogo`  lectura y validación de `empresas/<sector>/*.yaml`
- `variante`  azar determinista por (empresa, alumno)
- `maestros`  construcción de categorías, productos, contactos y tarifas
- `salida`    escritura de CSV y documentos de la variante
"""

__all__ = ["nif", "util", "catalogo", "variante", "maestros", "salida"]
