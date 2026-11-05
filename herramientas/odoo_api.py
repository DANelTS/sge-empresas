"""Cliente mínimo de la API externa de Odoo 19.

Transporte por defecto: **XML-RPC** (`/xmlrpc/2`), que en la 19 sigue
funcionando aunque esté marcado como obsoleto (Odoo lo retirará en la 22).
Ventaja para el aula: se autentica con el usuario y la contraseña que el alumno
ya tiene, sin crear nada más.

Transporte alternativo: **JSON-2** (`/json/2`), la API nueva de la 19. Necesita
una clave de API creada en *Mi perfil → Seguridad de la cuenta → Nueva clave de
API*. Es el camino que se usará en la UD5 y el que sobrevivirá a la 22.

Todo el resto del repositorio habla con Odoo a través de esta clase: si algún
día hay que cambiar de transporte, se cambia aquí y nada más.
"""
from __future__ import annotations

import json
import xmlrpc.client

import requests


class ErrorOdoo(RuntimeError):
    """Error devuelto por Odoo, con el mensaje limpio."""


class Odoo:
    def __init__(self, url: str, base: str, usuario: str, clave: str,
                 transporte: str = "xmlrpc"):
        self.url = url.rstrip("/")
        self.base = base
        self.usuario = usuario
        self.clave = clave
        self.transporte = transporte
        self.uid = None
        # Leemos siempre en español: los nombres de impuestos y de menús cambian
        # con el idioma y aquí se comparan por texto.
        self.contexto = {"lang": "es_ES"}
        if transporte == "xmlrpc":
            self._comun = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self._objetos = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)
        elif transporte == "json2":
            self._sesion = requests.Session()
            self._sesion.headers.update({
                "Authorization": f"bearer {clave}",
                "X-Odoo-Database": base,
                "Content-Type": "application/json",
            })
        else:
            raise ValueError("transporte debe ser 'xmlrpc' o 'json2'")

    # -- conexión ----------------------------------------------------------
    def conectar(self) -> int:
        if self.transporte == "xmlrpc":
            self.uid = self._comun.authenticate(self.base, self.usuario, self.clave, {})
            if not self.uid:
                raise ErrorOdoo("usuario o contraseña incorrectos")
        else:
            # En JSON-2 no hay authenticate: la primera llamada valida la clave.
            self.uid = self.llamar("res.users", "search", [[["login", "=", self.usuario]]], limite=1)[0]
        return self.uid

    def version(self) -> str:
        if self.transporte == "xmlrpc":
            return self._comun.version()["server_version"]
        r = requests.get(f"{self.url}/json/2/res.users/search_read", headers=self._sesion.headers, timeout=20)
        return r.headers.get("X-Odoo-Version", "19.0")

    # -- llamadas ----------------------------------------------------------
    def llamar(self, modelo: str, metodo: str, args=None, kwargs=None, limite=None):
        args = args or []
        kwargs = dict(kwargs or {})
        if self.transporte == "xmlrpc":
            kwargs.setdefault("context", dict(self.contexto))
        if limite is not None:
            kwargs["limit"] = limite
        if self.transporte == "xmlrpc":
            try:
                return self._objetos.execute_kw(
                    self.base, self.uid, self.clave, modelo, metodo, args, kwargs
                )
            except xmlrpc.client.Fault as exc:
                texto = getattr(exc, "faultString", str(exc))
                # Algunos botones de Odoo no devuelven nada y el servidor XML-RPC
                # no sabe serializar un None: la operación sí se ha hecho.
                if "cannot marshal None" in texto:
                    return None
                raise ErrorOdoo(_limpiar(texto)) from exc
            except xmlrpc.client.ProtocolError as exc:
                raise ErrorOdoo(f"no se puede hablar con Odoo en {self.url}: {exc}") from exc
        else:
            r = self._sesion.post(f"{self.url}/json/2/{modelo}/{metodo}", timeout=120,
                                  data=json.dumps(kwargs or (args[0] if len(args) == 1 else args)))
            if r.status_code >= 400:
                raise ErrorOdoo(_limpiar(r.text))
            return r.json() if r.content else None

    # -- atajos ------------------------------------------------------------
    def buscar(self, modelo, dominio, campos=None, limite=None, orden=None):
        valores = {"domain": dominio}
        if campos:
            valores["fields"] = campos
        if orden:
            valores["order"] = orden
        if limite:
            valores["limit"] = limite
        return self.llamar(modelo, "search_read", [], valores)

    def buscar_ids(self, modelo, dominio, limite=None):
        return self.llamar(modelo, "search", [dominio], {"limit": limite} if limite else {})

    def leer(self, modelo, ids, campos):
        return self.llamar(modelo, "read", [ids], {"fields": campos})

    def crear(self, modelo, valores) -> int:
        if self.transporte == "xmlrpc":
            return self.llamar(modelo, "create", [valores])
        return self.llamar(modelo, "create", [{"vals_list": [valores]}])[0]

    def escribir(self, modelo, ids, valores) -> bool:
        if isinstance(ids, int):
            ids = [ids]
        if self.transporte == "xmlrpc":
            return self.llamar(modelo, "write", [ids, valores])
        return self.llamar(modelo, "write", [{"ids": ids, "vals": valores}])

    def ejecutar(self, modelo, metodo, ids, *args, contexto=None):
        """Llama a un método sobre registros concretos (botones de la interfaz)."""
        if isinstance(ids, int):
            ids = [ids]
        if self.transporte == "xmlrpc":
            kwargs = {"context": contexto} if contexto else {}
            return self.llamar(modelo, metodo, [ids, *args], kwargs)
        payload = {"ids": ids}
        if contexto:
            payload["context"] = contexto
        return self.llamar(modelo, metodo, [payload] + list(args))

    def modelo(self, modelo: str):
        return _Modelo(self, modelo)


class _Modelo:
    """Azúcar para escribir `api.modelo('sale.order').crear({...})`."""

    def __init__(self, api: Odoo, nombre: str):
        self.api = api
        self.nombre = nombre

    def crear(self, valores) -> int:
        return self.api.crear(self.nombre, valores)

    def buscar(self, dominio, campos=None, limite=None, orden=None):
        return self.api.buscar(self.nombre, dominio, campos, limite, orden)

    def ids(self, dominio, limite=None):
        return self.api.buscar_ids(self.nombre, dominio, limite)

    def leer(self, ids, campos):
        return self.api.leer(self.nombre, ids, campos)

    def escribir(self, ids, valores):
        return self.api.escribir(self.nombre, ids, valores)

    def ejecutar(self, ids, metodo, *args, contexto=None):
        return self.api.ejecutar(self.nombre, metodo, ids, *args, contexto=contexto)


def _limpiar(texto: str) -> str:
    """Quita el ruido de las trazas de Odoo y deja el mensaje útil."""
    try:
        datos = json.loads(texto)
        datos = datos.get("data", datos)
        mensaje = datos.get("message") or texto
        argumentos = datos.get("arguments")
        if argumentos:
            mensaje = f"{mensaje}: {argumentos[0]}"
        return mensaje
    except (ValueError, AttributeError):
        pass
    # Las trazas de Odoo acaban con la línea que importa: "TipoError: mensaje".
    lineas = [l.strip() for l in texto.strip().splitlines() if l.strip()]
    for linea in reversed(lineas):
        if ": " in linea and not linea.startswith(("File ", "return", "raise", "self.")):
            return linea[:400]
    return lineas[-1][:400] if lineas else "error desconocido"
