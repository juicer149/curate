from __future__ import annotations

from dataclasses import dataclass

from .index import Index, deepest_scope_at_line
from .model import ScopeGraph
from .types import FoldMode, Range


@dataclass(frozen=True, slots=True)
class Intent:
    cursor: int
    level: int
    mode: FoldMode


def _ascend(idx: Index, sid: int, levels: int) -> int:
    cur = sid
    for _ in range(levels):
        s = idx.by_id.get(cur)
        if s is None or s.parent_id is None:
            break
        cur = s.parent_id
    return cur


def _body_range(s) -> Range | None:
    start = s.body_start
    end = s.end

    if start is None:
        return None

    if start < end:
        return (start, end)

    return None


def evaluate(graph: ScopeGraph, idx: Index, intent: Intent) -> tuple[Range, ...]:
    target = deepest_scope_at_line(graph, intent.cursor)
    if target is None:
        return ()

    sid = _ascend(idx, target.id, intent.level)
    scope = idx.by_id.get(sid)
    if scope is None:
        return ()

    if intent.mode == "self":
        r = _body_range(scope)
        return (r,) if r else ()

    out: list[Range] = []
    for cid in idx.children.get(scope.id, ()):
        ch = idx.by_id[cid]
        r = _body_range(ch)
        if r:
            out.append(r)

    return tuple(out)
