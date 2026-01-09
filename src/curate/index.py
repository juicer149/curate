from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .model import Scope, ScopeGraph


@dataclass(frozen=True, slots=True)
class Index:
    by_id: dict[int, Scope]
    children: dict[int, tuple[int, ...]]


def build_index(graph: ScopeGraph) -> Index:
    by_id = {s.id: s for s in graph.scopes}
    kids: dict[int, list[int]] = {}

    for s in graph.scopes:
        if s.parent_id is not None:
            kids.setdefault(s.parent_id, []).append(s.id)

    return Index(by_id, {k: tuple(v) for k, v in kids.items()})


def deepest_scope_at_line(graph: ScopeGraph, line: int) -> Optional[Scope]:
    best = None
    for s in graph.scopes:
        if s.contains_line(line):
            if best is None or s.length <= best.length:
                best = s
    return best
