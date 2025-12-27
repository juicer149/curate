"""
Query primitives.

Prolog analogy
--------------
These are pure queries over facts.

No folding semantics live here.
"""

from __future__ import annotations
from typing import Iterable

from .model import Scope, ScopeGraph
from .index import GraphIndex
from .rules import Rules


def children_of(idx: GraphIndex, *, scope: Scope) -> Iterable[Scope]:
    return idx.children.get(scope.id, ())


def select_scope_at_line(
    graph: ScopeGraph,
    idx: GraphIndex,
    rules: Rules,
    *,
    line: int,
) -> Scope | None:
    """
    Select the best navigable scope for a cursor line.
    """
    exact: list[Scope] = []
    containing: list[Scope] = []

    for s in graph.scopes:
        if not rules.navigable(s):
            continue

        if line == s.start:
            exact.append(s)
        elif s.start < line <= s.end:
            containing.append(s)

    if exact:
        return min(exact, key=lambda s: s.length)
    if containing:
        return min(containing, key=lambda s: s.length)

    return None
