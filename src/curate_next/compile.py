# curate_next/compile.py

"""
curate_next.compile — compilation facade

Selects a producer backend and compiles source text into a deterministic,
laminar ScopeSet.

Design guarantees:
- Always returns a ScopeSet
- Never raises due to missing producers or languages
- Producers are selected by string key (lookup, not conditionals)
- Fallback behavior is explicit and structural (noop producer)

This module contains:
- NO interpretation
- NO editor or workspace logic
- NO syntax-tree assumptions
"""

from __future__ import annotations

from .facts import ScopeSet
from .producers.registry import PRODUCERS


def compile_scope_set(
    *,
    source: str,
    language: str = "default",
    producer: str = "treesitter",
) -> ScopeSet:
    """
    Compile source text into structural facts.

    Args:
        source:
            Source text to compile.
        language:
            Language key understood by the selected producer.
        producer:
            Producer backend key (e.g. "treesitter", "noop").

    Returns:
        ScopeSet:
            Always a valid ScopeSet containing at least a root scope.

    Failure handling:
        - Unknown producer key → noop
        - Producer import failure → noop
        - Producer runtime failure → noop
    """
    # Resolve producer factory
    factory = PRODUCERS.get(producer)
    if factory is None:
        factory = PRODUCERS["noop"]

    # Instantiate producer
    build = factory()
    if build is None:
        # Producer unavailable (e.g. missing dependencies)
        build = PRODUCERS["noop"]()

    # Execute producer with hard structural fallback
    try:
        return build(source=source, language=language)
    except Exception:
        # Any producer failure degrades to structural noop
        noop = PRODUCERS["noop"]()
        return noop(source=source, language=language)
