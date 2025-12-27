"""
Indexing layer.

Why this exists
---------------
Queries should be fast and mechanical.

This module derives lookup tables from the inert fact database
without adding semantics.
"""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass

from .model import Scope, ScopeGraph


@dataclass(frozen=True)
class GraphIndex:
    by_id: dict[int, Scope]
    children: dict[int | None, list[Scope]]


def build_index(graph: ScopeGraph) -> GraphIndex:
    by_id: dict[int, Scope] = {}
    children: dict[int | None, list[Scope]] = defaultdict(list)

    for s in graph.scopes:
        by_id[s.id] = s
        children[s.parent_id].append(s)

    return GraphIndex(by_id=by_id, children=dict(children))
