"""
curate_core.sources.backends.http — HTTP source backend

Responsibilities:
- fetch text over HTTP(S)
- decode as UTF-8 (best-effort)

Non-responsibilities:
- no retries
- no auth
- no caching
- no rate limiting

Invariants:
- network failure -> empty string
"""

from __future__ import annotations
from typing import Mapping, Any
import urllib.request


class HttpSource:
    """
    Simple HTTP source backend to show extensabliity.
    """

    def read(self, *, spec: Mapping[str, Any]) -> str:
        try:
            url = spec.get("url")
            if not isinstance(url, str):
                return ""

            with urllib.request.urlopen(url, timeout=5) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception:
            return ""
