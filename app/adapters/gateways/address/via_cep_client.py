from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class ViaCepClient:
    """
    Thin HTTP client for the ViaCEP public API.

    Keeps network I/O isolated from mapping / domain concerns.
    """

    def __init__(
        self,
        base_url: str = "https://viacep.com.br/ws",
        timeout_seconds: float = 5.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def fetch_by_cep(self, digits: str) -> dict[str, Any] | None:
        """
        Fetch raw ViaCEP JSON for an 8-digit Brazilian CEP.

        Args:
            digits: CEP with digits only (exactly 8 characters).

        Returns:
            Parsed JSON dict, or None on HTTP/network failure.
        """
        url = f"{self._base_url}/{digits}/json/"
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "CowTrackAPI/1.0"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self._timeout_seconds,
            ) as response:
                payload = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, OSError):
            return None

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None
        return data
