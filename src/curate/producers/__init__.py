"""
Producer registry.

Why this exists
---------------
Language selection is an orchestration concern.

Producers:
- know how to parse
- do NOT know about rules
- do NOT know about editors
"""

from .python_ast import build_graph as python_graph
from .empty import build_graph as empty_graph


_PRODUCERS = {
    "python": python_graph,
}


def get_producer(language: str):
    """
    Return a structure producer for the given language.

    Unknown languages fall back to a safe no-op producer.
    """
    return _PRODUCERS.get(language, empty_graph)
