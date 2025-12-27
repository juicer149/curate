"""
Intent evaluation.

Why this exists
---------------
This is the semantic core.

It combines:
- user intent
- structural facts
- folding rules

And produces fold ranges.
"""

from __future__ import annotations
from dataclasses import dataclass

from .types import FoldMode, Range
from .model import ScopeGraph
from .index import GraphIndex
from .rules import Rules
from .query import select_scope_at_line
from .folding import fold_self, fold_children


@dataclass(frozen=True)
class Intent:
    cursor: int
    level: int
    mode: FoldMode


def evaluate(
    graph: ScopeGraph,
    idx: GraphIndex,
    rules: Rules,
    intent: Intent,
) -> set[Range]:
    base = select_scope_at_line(
        graph, idx, rules, line=intent.cursor
    )

    if base is None:
        return set()

    scope = base
    for _ in range(intent.level):
        if scope.parent_id is None:
            break
        scope = idx.by_id.get(scope.parent_id, scope)

    if intent.mode == "self":
        return fold_self(scope, rules)

    return fold_children(idx, scope=scope, rules=rules)
