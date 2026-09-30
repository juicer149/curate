"""curate_next.compile — compilation facade (Raw -> Derived)

Pipeline:
- select producer -> RawScopeSet
- derive -> ScopeSet

Guarantees:
- always returns a ScopeSet
- always contains a root scope
- never raises due to missing producer / optional deps
"""

from __future__ import annotations

from typing import Callable

from .facts import RawScopeSet, ScopeSet
from .derive import derive_scope_set
from .producers.registry import PRODUCERS, Producer


def compile_scope_set(
    *,
    source: str,
    language: str = "default",
    producer: str = "treesitter",
    on_error: Callable[[Exception], None] | None = None,
) -> ScopeSet:
    factory = PRODUCERS.get(producer) or PRODUCERS["noop"]

    try:
        build_raw: Producer = factory()
        raw: RawScopeSet = build_raw(source=source, language=language)
    except Exception as e:
        if on_error is not None:
            on_error(e)
        raw = RawScopeSet(())

    # derive is intentionally total
    return derive_scope_set(source=source, raw=raw)
