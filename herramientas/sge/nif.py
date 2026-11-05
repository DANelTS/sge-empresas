"""Generación y validación de NIF, CIF y NIE españoles.

Todo lo que se genera aquí tiene dígito de control válido: el módulo `base_vat`
de Odoo (que se instala con la localización española) rechaza los NIF mal
formados, así que un dato inventado pero inválido rompería la importación.

Referencia del algoritmo: Agencia Tributaria, «Comprobación de un NIF de
persona jurídica» y «Comprobación de un NIF de persona física».
"""
from __future__ import annotations

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
# Letras válidas de CIF y qué control les corresponde.
CIF_LETRAS = "ABCDEFGHJNPQRSUVW"
CIF_SOLO_LETRA = "KPQS"          # el control es siempre una letra
CIF_SOLO_DIGITO = "ABEH"         # el control es siempre un dígito
# Las demás (C, D, F, G, J, N, U, V, W) admiten letra o dígito.
LETRAS_CONTROL = "JABCDEFGHI"


def letra_dni(numero: int) -> str:
    """Letra de control de un DNI de 8 cifras."""
    return LETRAS_DNI[numero % 23]


def dni(numero: int) -> str:
    """Devuelve el DNI completo (8 cifras y letra) a partir del número."""
    if not 0 <= numero <= 99_999_999:
        raise ValueError(f"número de DNI fuera de rango: {numero}")
    return f"{numero:08d}{letra_dni(numero)}"


def nie(numero: int) -> str:
    """NIE: X, Y o Z + 7 cifras + letra. El número se calcula como si la
    letra inicial fuera 0, 1 o 2."""
    if not 0 <= numero <= 9_999_999:
        raise ValueError(f"número de NIE fuera de rango: {numero}")
    inicial = "XYZ"[numero // 1_000_000 % 3]
    resto = numero % 1_000_000
    return f"{inicial}{resto:07d}{letra_dni(int(f'{numero // 1_000_000 % 3}{resto:07d}'))}"


def digito_control_cif(letra: str, cifras: str) -> str:
    """Dígito (o letra) de control de un CIF a partir de la letra y las 7 cifras."""
    letra = letra.upper()
    if letra not in CIF_LETRAS:
        raise ValueError(f"letra de CIF no válida: {letra}")
    if len(cifras) != 7 or not cifras.isdigit():
        raise ValueError(f"se esperaban 7 cifras, llegó {cifras!r}")
    digitos = [int(c) for c in cifras]
    suma_pares = digitos[1] + digitos[3] + digitos[5]
    suma_impares = sum(sum(int(d) for d in str(2 * d)) for d in digitos[0::2])
    control = (10 - (suma_pares + suma_impares) % 10) % 10
    if letra in CIF_SOLO_LETRA:
        return LETRAS_CONTROL[control]
    if letra in CIF_SOLO_DIGITO:
        return str(control)
    return str(control)  # las demás admiten las dos formas; usamos el dígito


def cif(letra: str, cifras: str) -> str:
    return f"{letra.upper()}{cifras}{digito_control_cif(letra, cifras)}"


def valido(nif: str) -> bool:
    """Comprueba un NIF/CIF/NIE. No distingue mayúsculas ni espacios."""
    nif = nif.strip().upper().replace("-", "").replace(" ", "")
    if len(nif) != 9:
        return False
    if nif[0].isdigit():
        return nif[:8].isdigit() and nif[8] == letra_dni(int(nif[:8]))
    if nif[0] in "XYZ":
        if not nif[1:8].isdigit():
            return False
        numero = int(f"{'XYZ'.index(nif[0])}{nif[1:8]}")
        return nif[8] == letra_dni(numero)
    if nif[0] in CIF_LETRAS and nif[1:8].isdigit():
        esperado = digito_control_cif(nif[0], nif[1:8])
        return nif[8] == esperado
    return False


def iban_es(banco: str, sucursal: str, cuenta: str) -> str:
    """IBAN español con dígitos de control correctos (ISO 13616).

    banco: 4 cifras; sucursal: 4 cifras; cuenta: 10 cifras.
    """
    for trozo in (banco, sucursal, cuenta):
        if not trozo.isdigit():
            raise ValueError("banco, sucursal y cuenta deben ser dígitos")
    if (len(banco), len(sucursal), len(cuenta)) != (4, 4, 10):
        raise ValueError("longitudes esperadas: 4, 4 y 10")
    bban = f"{banco}{sucursal}{cuenta}"
    # ES = 14 28 según la tabla de conversión de letras a números.
    intermedio = f"{bban}142800"
    resto = int(intermedio) % 97
    control = 98 - resto
    return f"ES{control:02d}{bban}"


def valido_iban(iban: str) -> bool:
    limpio = iban.replace(" ", "").upper()
    if len(limpio) < 5 or not limpio[:2].isalpha():
        return False
    reordenado = limpio[4:] + limpio[:4]
    numerico = "".join(
        str(ord(c) - 55) if c.isalpha() else c for c in reordenado
    )
    return int(numerico) % 97 == 1
