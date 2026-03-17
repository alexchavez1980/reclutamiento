"""
Autenticación OAuth2 con Microsoft Graph vía Device Code Flow.

El usuario aprueba el acceso UNA vez desde el navegador.
Las sesiones siguientes usan el token cacheado (refresh automático).
"""

import json
import logging
import msal

from config import GRAPH_CLIENT_ID, GRAPH_TENANT_ID, GRAPH_SCOPES, GRAPH_TOKEN_CACHE

log = logging.getLogger("r1_detector.auth")

AUTHORITY = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}"


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    try:
        with open(GRAPH_TOKEN_CACHE, "r") as f:
            cache.deserialize(f.read())
    except FileNotFoundError:
        pass
    return cache


def _save_cache(cache: msal.SerializableTokenCache):
    if cache.has_state_changed:
        with open(GRAPH_TOKEN_CACHE, "w") as f:
            f.write(cache.serialize())


def get_access_token() -> str:
    """
    Obtiene un access token válido para Microsoft Graph.

    Primera ejecución: muestra un código + URL para autorizar en el navegador.
    Ejecuciones siguientes: usa el refresh token cacheado (silencioso).
    """
    if not GRAPH_CLIENT_ID:
        raise RuntimeError(
            "GRAPH_CLIENT_ID no configurado. "
            "Registrá una app en Azure Portal → Entra ID → App Registrations."
        )

    cache = _load_cache()

    app = msal.PublicClientApplication(
        GRAPH_CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    # Intentar token silencioso (cache/refresh)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(GRAPH_SCOPES, account=accounts[0])
        if result and "access_token" in result:
            log.info("Token obtenido desde cache (silencioso).")
            _save_cache(cache)
            return result["access_token"]

    # Primera vez o token expirado: Device Code Flow
    flow = app.initiate_device_flow(scopes=GRAPH_SCOPES)
    if "user_code" not in flow:
        raise RuntimeError(f"Error iniciando Device Code Flow: {flow}")

    print("\n" + "=" * 60)
    print("  🔐 AUTORIZACIÓN REQUERIDA")
    print("=" * 60)
    print(f"  1. Abrí este link: {flow['verification_uri']}")
    print(f"  2. Ingresá el código: {flow['user_code']}")
    print(f"  3. Autorizá con tu cuenta de Outlook/Microsoft 365")
    print("=" * 60 + "\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "desconocido"))
        raise RuntimeError(f"Autenticación fallida: {error}")

    log.info("Token obtenido via Device Code Flow.")
    _save_cache(cache)
    return result["access_token"]
