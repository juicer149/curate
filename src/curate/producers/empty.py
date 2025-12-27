"""
Empty structure producer.

Why this exists
---------------
This is the safe default for unsupported languages.

It guarantees:
- no crashes
- no folding
- preserved engine invariants

Design principle
----------------
"Silence is better than guessing."
"""

from ..model import ScopeGraph


def build_graph(source: str) -> ScopeGraph:
    return ScopeGraph(())
