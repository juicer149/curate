"""
Producer registry and abstraction layer.

A producer is responsible for converting raw source text into a ScopeGraph.

Design principles:
- Producers are pure functions: source -> ScopeGraph
- No global state
- No policy or querying logic
- Language-specific details are fully encapsulated

This module provides:
- A Producer type alias
- A factory for retrieving the appropriate producer by language
"""

from __future__ import annotations

from typing import Callable

from ..model import ScopeGraph
from .treesitter import build_graph as treesitter_build

Producer = Callable[[str], ScopeGraph]


def get_producer(language: str) -> Producer:
    """
    Return a producer function for the given language.

    Pseudocode:
    - Normalize language name
    - Return a closure that:
        - Accepts source text
        - Delegates to the Tree-sitter producer
        - Returns a ScopeGraph

    Note:
    - The returned function hides language dispatch from callers
    - This keeps the engine layer language-agnostic
    """
    lang = (language or "default").lower()

    def producer(source: str) -> ScopeGraph:
        return treesitter_build(language=lang, source=source)

    return producer


__all__ = ["Producer", "get_producer"]
