"""
Cliente mínimo para buscar canciones en Spotify usando el flujo
"Client Credentials": no necesita que inicies sesión, solo un Client
ID y Secret gratis.

Cómo conseguirlos (5 minutos):
1. Entra a https://developer.spotify.com/dashboard con tu cuenta de Spotify.
2. Créate una app (el nombre y la descripción no importan).
3. En la configuración de la app, copia el "Client ID" y el "Client Secret".
4. Pégalos abajo.

Esto solo permite BUSCAR canciones (para saber qué URI abrir); NO da
acceso a tu cuenta de Spotify ni a tus playlists.
"""
import base64
import time
import requests

SPOTIFY_CLIENT_ID = "PON_AQUI_TU_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "PON_AQUI_TU_CLIENT_SECRET"

_token_cache = {"token": None, "expira": 0}


def _obtener_token():
    if _token_cache["token"] and time.time() < _token_cache["expira"]:
        return _token_cache["token"]

    credenciales = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    credenciales_b64 = base64.b64encode(credenciales.encode()).decode()

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {credenciales_b64}"},
        data={"grant_type": "client_credentials"},
        timeout=10,
    )
    resp.raise_for_status()
    datos = resp.json()
    _token_cache["token"] = datos["access_token"]
    _token_cache["expira"] = time.time() + datos["expires_in"] - 30
    return _token_cache["token"]


def buscar_uri_cancion(consulta):
    """
    Devuelve el URI de Spotify (ej: 'spotify:track:abc123') de la
    primera canción encontrada, o None si no encontró nada o si
    todavía no configuraste las credenciales arriba.
    """
    if "PON_AQUI" in SPOTIFY_CLIENT_ID:
        return None
    try:
        token = _obtener_token()
        resp = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": consulta, "type": "track", "limit": 1},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json()["tracks"]["items"]
        if not items:
            return None
        return items[0]["uri"]
    except Exception:
        return None
