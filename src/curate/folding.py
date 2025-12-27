"""
Folding primitives.

Why this exists
---------------
This module turns structure + rules into fold ranges.

It does NOT:
- select scopes
- interpret intent
"""

from __future__ import annotations
from typing import Set

from .model import Scope
from .rules import Rules
from .types import Range
from .index import GraphIndex
from .query import children_of


def body_range(scope: Scope, rules: Rules) -> Range | None:
    header = rules.header_size(scope)
    start = scope.start + header
    end = scope.end

    if start >= end:
        return None
    return (start, end)


def fold_self(scope: Scope, rules: Rules) -> Set[Range]:
    if not rules.foldable(scope):
        return set()

    r = body_range(scope, rules)
    return {r} if r else set()


def fold_children(
    idx: GraphIndex,
    *,
    scope: Scope,
    rules: Rules,
) -> Set[Range]:
    out: Set[Range] = set()

    for child in children_of(idx, scope=scope):
        if not rules.foldable(child):
            continue
        r = body_range(child, rules)
        if r:
            out.add(r)

    return out
