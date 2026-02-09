"""HTTP session management for Plaud API.

Provides a configured ``requests.Session`` with browser-like headers,
automatic retry on 5xx, and error mapping to custom exceptions.
"""

from __future__ import annotations

import random
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from plaud.exceptions import APIError, AuthenticationError, NotFoundError


def _make_retry_adapter() -> HTTPAdapter:
    """Create an HTTPAdapter with retry strategy for 5xx errors."""
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    )
    return HTTPAdapter(max_retries=retry)


_BROWSER_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://web.plaud.ai",
    "Referer": "https://web.plaud.ai/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15"
    ),
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "app-platform": "web",
    "edit-from": "web",
    "Priority": "u=3, i",
}


class PlaudSession:
    """Thin wrapper around ``requests.Session`` pre-configured for Plaud API.

    Features:
        - Browser-like headers required by the reverse-engineered API
        - Bearer token in ``Authorization`` header
        - Automatic retry on transient 5xx errors
        - Maps HTTP error codes to typed exceptions
    """

    def __init__(self, token: str) -> None:
        self._session = requests.Session()
        self._session.headers.update(_BROWSER_HEADERS)
        self._session.headers["Authorization"] = f"bearer {token}"

        adapter = _make_retry_adapter()
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get(self, url: str, *, params: dict[str, Any] | None = None,
            timeout: int = 30, **kwargs: Any) -> dict[str, Any]:
        params = dict(params or {})
        params.setdefault("r", random.random())
        resp = self._session.get(url, params=params, timeout=timeout, **kwargs)
        return self._handle(resp)

    def post(self, url: str, *, json: Any = None,
             timeout: int = 30, **kwargs: Any) -> dict[str, Any]:
        if isinstance(json, dict):
            json.setdefault("r", random.random())
        resp = self._session.post(url, json=json, timeout=timeout, **kwargs)
        return self._handle(resp)

    def patch(self, url: str, *, json: dict[str, Any] | None = None,
              timeout: int = 30, **kwargs: Any) -> dict[str, Any]:
        if json is not None:
            json.setdefault("r", random.random())
        resp = self._session.patch(url, json=json, timeout=timeout, **kwargs)
        return self._handle(resp)

    def put_raw(self, url: str, *, data: Any = None,
                headers: dict[str, str] | None = None,
                timeout: int = 120) -> requests.Response:
        """PUT without JSON wrapping — used for S3 uploads."""
        return self._session.put(url, data=data, headers=headers, timeout=timeout)

    # ------------------------------------------------------------------
    # Response handling
    # ------------------------------------------------------------------

    @staticmethod
    def _handle(resp: requests.Response) -> dict[str, Any]:
        """Parse JSON response and raise typed exceptions on errors."""
        if resp.status_code == 401:
            raise AuthenticationError(
                "Authentication failed (401). Token may be expired — "
                "run `plaud auth setup` or set a new PLAUD_TOKEN."
            )
        if resp.status_code == 404:
            raise NotFoundError(f"Resource not found: {resp.url}")
        if resp.status_code >= 400:
            raise APIError(
                f"API error {resp.status_code}: {resp.text[:300]}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()
