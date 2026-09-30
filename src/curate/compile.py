from __future__ import annotations
from typing import Callable

from .facts import ScopeSet, RawFactSet
from .curation import curate
from .producers import PRODUCERS

# ------------------------------------------------------------------
# Default behaviors
# ------------------------------------------------------------------

DEFAULT_LANGUAGE = "default"
DEFAULT_PRODUCER = "noop"


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def compile_scopes(
    *,
    source: str,
    language: str = DEFAULT_LANGUAGE, 
    producer: str = DEFAULT_PRODUCER, 
    on_error: Callable[[Exception], None] | None = None,
) -> ScopeSet:
    """
    Public compilation facade.

    Role:
        - Select producer
        - Guarantee totality
        - Delegate structure to curation
    """
    factory = PRODUCERS.get(producer, PRODUCERS[DEFAULT_PRODUCER])

    try:
        raw = factory()(source=source, language=language)
    except Exception as e:
        if on_error:
            on_error(e)
        raw = RawFactSet.from_iter(())

    return curate(raw.items)
