"""
curate_next.producers.registry — raw producer registry

A producer compiles:
    (source: str, language: str) -> RawScopeSet

Producers are optional-dependency friendly via lazy imports.
The registry guarantees a safe fallback.
"""

from __future__ import annotations

from typing import Callable, Dict, Protocol

from curate_next.facts import RawScopeSet


class Producer(Protocol):
    """Producer contract (keyword-only)."""

    def __call__(self, *, source: str, language: str) -> RawScopeSet:
        ...


Factory = Callable[[], Producer]


def _noop() -> Producer:
    from .noop import build_raw_scope_set
    return build_raw_scope_set


def _treesitter() -> Producer:
    """
    Optional producer.

    If treesitter is unavailable (missing deps, missing native libs, etc),
    we fall back to noop without raising.
    """
    try:
        from .treesitter.producer import build_raw_scope_set
        return build_raw_scope_set
    except Exception:
        return _noop()


PRODUCERS: Dict[str, Factory] = {
    "noop": _noop,
    # Reserved key: stable config even when optional deps are absent.
    "treesitter": _treesitter,
}
