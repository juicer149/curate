# curate_next/producers/registry.py

"""
Producer registry.

A producer is a backend that converts:

    (source: str, language: str) -> ScopeSet

Producers are selected by string key and instantiated lazily.
Missing dependencies or import failures are handled by returning None,
allowing the caller to apply an explicit fallback.
"""

from typing import Callable, Dict, Optional
from ..facts import ScopeSet

# Concrete producer callable signature
Producer = Callable[..., ScopeSet]


def _treesitter() -> Optional[Producer]:
    """
    Tree-sitter producer factory.

    Returns:
        build_scope_set callable if Tree-sitter dependencies are available,
        otherwise None.
    """
    try:
        from .treesitter import build_scope_set
    except ImportError:
        return None
    return build_scope_set


def _noop() -> Producer:
    """
    No-op producer factory.

    Always available. Produces a single module-level scope
    covering the entire source.
    """
    from .noop import build_scope_set
    return build_scope_set


# Registry of available producer factories.
# Factories must be zero-argument callables returning either:
#   - a Producer callable
#   - or None if unavailable
PRODUCERS: Dict[str, Callable[[], Optional[Producer]]] = {
    "treesitter": _treesitter,
    "noop": _noop,
}
