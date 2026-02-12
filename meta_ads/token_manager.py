"""
Token-håndtering til Meta Marketing API.
Understøtter udveksling af kortlivede tokens til langlivede tokens,
og validering af eksisterende tokens.
"""

import json
import logging
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from . import config

logger = logging.getLogger(__name__)

BASE_URL = f"https://graph.facebook.com/{config.API_VERSION}"


def validate_token(access_token):
    """
    Valider en access token og returner info om den.

    Returns:
        Dict med token-info (type, app_id, expires_at, is_valid, scopes)
        eller None hvis token er ugyldig.
    """
    params = urlencode({
        "input_token": access_token,
        "access_token": access_token,
    })
    url = f"{BASE_URL}/debug_token?{params}"
    req = Request(url, method="GET")

    try:
        with urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body).get("data", {})
            return data
    except HTTPError:
        return None


def exchange_for_long_lived_token(short_lived_token=None):
    """
    Byt en kortlivet token til en langlivet token (~60 dage).

    Kræver META_APP_ID og META_APP_SECRET som environment variables.

    Args:
        short_lived_token: Kortlivet token. Bruger META_ACCESS_TOKEN hvis None.

    Returns:
        Dict med 'access_token' og 'expires_in' (sekunder).

    Raises:
        ValueError: Hvis app credentials mangler.
        RuntimeError: Hvis token-udveksling fejler.
    """
    token = short_lived_token or config.META_ACCESS_TOKEN
    if not token:
        raise ValueError("Ingen access token tilgængelig at udveksle.")

    if not config.META_APP_ID or not config.META_APP_SECRET:
        raise ValueError(
            "META_APP_ID og META_APP_SECRET skal sættes som environment "
            "variables for at kunne udveksle tokens.\n"
            "Find dem i Meta Developer Portal → din app → Settings → Basic."
        )

    params = urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": config.META_APP_ID,
        "client_secret": config.META_APP_SECRET,
        "fb_exchange_token": token,
    })
    url = f"{BASE_URL}/oauth/access_token?{params}"
    req = Request(url, method="GET")

    try:
        with urlopen(req, timeout=15) as response:
            body = response.read().decode("utf-8")
            result = json.loads(body)
            logger.info(
                "Token udvekslet. Ny token udløber om %d dage.",
                result.get("expires_in", 0) // 86400,
            )
            return result
    except HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            error_msg = json.loads(body).get("error", {}).get("message", str(e))
        except (json.JSONDecodeError, KeyError):
            error_msg = str(e)
        raise RuntimeError(f"Kunne ikke udveksle token: {error_msg}")
