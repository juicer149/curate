"""
curate.compile — compilation facade

Selects a syntax-tree producer and compiles source text
into a deterministic, laminar ScopeSet.

No interpretation.
No project or workspace awareness.
"""

from .facts import ScopeSet
from .producers.treesitter import build_scope_set


def compile_scope_set(*, source: str, language: str = "default") -> ScopeSet:
    """
    Compile source text into structural facts.

    Guarantees:
    - always returns a ScopeSet
    - always contains a root scope
    - never raises on parse failure
    """
    return build_scope_set(source=source, language=language)
