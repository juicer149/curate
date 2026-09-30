"""
curate_core.ingest.fs.rules.registry

Central registry for PathRule factories.
"""

from __future__ import annotations

from typing import Callable, Dict

from .protocol import PathRule

Factory = Callable[[], PathRule]

PATH_RULES: Dict[str, Factory] = {}
