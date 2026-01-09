from __future__ import annotations

"""
Producer registry.

A producer is a callable:
    (source: str) -> ScopeGraph

The engine does not know or care how the graph is built.
"""

from typing import Callable

from ..model import ScopeGraph
from .treesitter import build_graph


Producer = Callable[[str], ScopeGraph]


def get_producer(language: str) -> Producer:
    """
    Return a producer function for the given language.

    The returned callable takes source text and produces a ScopeGraph.
    """

    def producer(source: str) -> ScopeGraph:
        return build_graph(language, source)

    return producer


__all__ = ["Producer", "get_producer"]
