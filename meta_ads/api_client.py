"""
HTTP-klient til Meta Marketing API.
Håndterer autentificering, requests og fejlhåndtering.
"""

import json
import logging
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from . import config

logger = logging.getLogger(__name__)

BASE_URL = f"https://graph.facebook.com/{config.API_VERSION}"


class MetaAPIError(Exception):
    """Fejl fra Meta API."""

    def __init__(self, message, error_code=None, error_subcode=None):
        super().__init__(message)
        self.error_code = error_code
        self.error_subcode = error_subcode


class MetaAPIClient:
    """Klient til at kommunikere med Meta Marketing API."""

    def __init__(self, access_token=None, ad_account_id=None):
        self.access_token = access_token or config.META_ACCESS_TOKEN
        self.ad_account_id = ad_account_id or config.META_AD_ACCOUNT_ID

        if not self.access_token:
            raise ValueError(
                "META_ACCESS_TOKEN skal sættes som environment variable "
                "eller angives direkte."
            )
        if not self.ad_account_id:
            raise ValueError(
                "META_AD_ACCOUNT_ID skal sættes som environment variable "
                "eller angives direkte."
            )

        if not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"

    def _request(self, method, endpoint, params=None, retries=3):
        """Send en request til Meta API med retry-logik."""
        url = f"{BASE_URL}/{endpoint}"
        params = params or {}
        params["access_token"] = self.access_token

        for attempt in range(retries):
            try:
                if method == "GET":
                    query = urlencode(params)
                    full_url = f"{url}?{query}"
                    req = Request(full_url, method="GET")
                elif method == "POST":
                    data = urlencode(params).encode("utf-8")
                    req = Request(url, data=data, method="POST")
                elif method == "DELETE":
                    query = urlencode(params)
                    full_url = f"{url}?{query}"
                    req = Request(full_url, method="DELETE")
                else:
                    raise ValueError(f"Ukendt HTTP-metode: {method}")

                req.add_header("Content-Type", "application/x-www-form-urlencoded")

                with urlopen(req, timeout=30) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body)

            except HTTPError as e:
                body = e.read().decode("utf-8")
                try:
                    error_data = json.loads(body)
                    error_info = error_data.get("error", {})
                    msg = error_info.get("message", str(e))
                    code = error_info.get("code")
                    subcode = error_info.get("error_subcode")
                    error_type = error_info.get("type", "")
                    fbtrace = error_info.get("fbtrace_id", "")
                except (json.JSONDecodeError, KeyError):
                    msg = str(e)
                    code = None
                    subcode = None
                    error_type = ""
                    fbtrace = ""

                logger.debug(
                    "API fejl detaljer - Type: %s, Kode: %s, Subkode: %s, "
                    "Besked: %s, FBTrace: %s",
                    error_type, code, subcode, msg, fbtrace,
                )

                if e.code == 429 and attempt < retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Rate limited. Venter %ds før retry...", wait)
                    time.sleep(wait)
                    continue

                raise MetaAPIError(msg, error_code=code, error_subcode=subcode)

            except URLError as e:
                if attempt < retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Netværksfejl: %s. Retry om %ds...", e, wait)
                    time.sleep(wait)
                    continue
                raise MetaAPIError(f"Netværksfejl: {e}")

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params)

    def post(self, endpoint, params=None):
        return self._request("POST", endpoint, params)

    def delete(self, endpoint, params=None):
        return self._request("DELETE", endpoint, params)
