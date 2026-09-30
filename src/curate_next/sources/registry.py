"""
curate_core.sources.registry — backend registry

Provides a static, explicit registry mapping string keys
to backend factories.

Responsibilities:
- backend lookup by stable string key
- lazy instantiation via factories

Non-responsibilities:
- no fallback logic
- no composition
- no policy decisions

Invariants:
- registry values are zero-arg callables
- factories return SourceBackend instances
"""

from __future__ import annotations
from typing import Callable, Dict

from .protocol import SourceBackend

Factory = Callable[[], SourceBackend]

SOURCE_BACKENDS: Dict[str, Factory] = {}
