# src/curate/query.py
"""
Structural query engine.

Implements a small, lisp-like relation system over scopes.

Design principles:
- No mutation
- No global state
- Relations are pure functions
- Dispatch via registry, not conditionals
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from .index import Index, deepest_scope_at_line
from .model import Scope, ScopeGraph
from .types import Axis, QueryDict


@dataclass(frozen=True, slots=True)
class Query:
    cursor: int
    axis: Axis = "self"

    kinds: tuple[str, ...] = ()
    include_target: bool = False
    max_items: int | None = None

    kind: str | None = None  # for all_of_kind


def query_from_dict(*, cursor: int, d: QueryDict) -> Query:
    kinds = d.get("kinds", ())
    if isinstance(kinds, list):
        kinds = tuple(kinds)

    return Query(
        cursor=cursor,
        axis=d.get("axis", "self"),
        kinds=tuple(kinds) if kinds else (),
        include_target=bool(d.get("include_target", False)),
        max_items=d.get("max_items", None),
        kind=d.get("kind", None),
    )


def _matches(scope: Scope, q: Query) -> bool:
    """
    Might be moved to __eq__ of Scope or similar later.
    """
    return (not q.kinds) or (scope.kind in q.kinds)


def _cap(scopes: Iterable[Scope], max_items: int | None) -> tuple[Scope, ...]:
    if max_items is None:
        return tuple(scopes)
    out: list[Scope] = []
    for s in scopes:
        out.append(s)
        if len(out) >= max_items:
            break
    return tuple(out)


# ---- Primitive walkers (small “relations kernel”) ---------------------------

def _walk_chain(
    *,
    start_id: int,
    step: Callable[[int], Optional[int]],
    by_id: dict[int, Scope],
    include_start: bool,
    max_items: int | None,
) -> tuple[Scope, ...]:
    out: list[Scope] = []
    cur = start_id

    if include_start:
        s = by_id.get(cur)
        if s is not None:
            out.append(s)

    while True:
        nxt = step(cur)
        if nxt is None:
            break
        s = by_id.get(nxt)
        if s is not None:
            out.append(s)
        cur = nxt
        if max_items is not None and len(out) >= max_items:
            break

    return tuple(out)


def _walk_tree_dfs(
    *,
    root_id: int,
    children: dict[int, tuple[int, ...]],
    by_id: dict[int, Scope],
    include_root: bool,
    max_items: int | None,
) -> tuple[Scope, ...]:
    out: list[Scope] = []
    if include_root:
        s = by_id.get(root_id)
        if s is not None:
            out.append(s)
            if max_items is not None and len(out) >= max_items:
                return tuple(out)

    stack = list(reversed(children.get(root_id, ())))
    while stack:
        sid = stack.pop()
        s = by_id.get(sid)
        if s is not None:
            out.append(s)
            if max_items is not None and len(out) >= max_items:
                break
        kids = children.get(sid, ())
        if kids:
            stack.extend(reversed(kids))
    return tuple(out)


# ---- Relations (Axis handlers) ----------------------------------------------

Relation = Callable[[ScopeGraph, Index, Scope, Query], tuple[Scope, ...]]


def rel_self(_g: ScopeGraph, _idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    return (target,) if _matches(target, q) else ()


def rel_parent(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    pid = idx.parent.get(target.id)
    if pid is None:
        return ()
    s = idx.by_id.get(pid)
    if s is None or not _matches(s, q):
        return ()
    return (s,)


def rel_children(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    kids = (idx.by_id[cid] for cid in idx.children.get(target.id, ()))
    return _cap((s for s in kids if _matches(s, q)), q.max_items)


def rel_ancestors(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    def step(cur: int) -> Optional[int]:
        return idx.parent.get(cur)

    chain = _walk_chain(
        start_id=target.id,
        step=step,
        by_id=idx.by_id,
        include_start=q.include_target,
        max_items=q.max_items,
    )
    return tuple(s for s in chain if _matches(s, q))


def rel_descendants(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    desc = _walk_tree_dfs(
        root_id=target.id,
        children=idx.children,
        by_id=idx.by_id,
        include_root=q.include_target,
        max_items=q.max_items,
    )
    return tuple(s for s in desc if _matches(s, q))


def rel_siblings(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    pid = idx.parent.get(target.id)
    if pid is None:
        return ()
    sib_ids = idx.children.get(pid, ())
    sibs = (idx.by_id[sid] for sid in sib_ids if sid != target.id)
    return _cap((s for s in sibs if _matches(s, q)), q.max_items)


def _rel_next_prev(idx: Index, target: Scope, q: Query, direction: int) -> tuple[Scope, ...]:
    p = idx.pos.get(target.id)
    if p is None:
        return ()
    j = p + direction
    while 0 <= j < len(idx.order):
        s = idx.by_id[idx.order[j]]
        if _matches(s, q):
            return (s,)
        j += direction
    return ()


def rel_next(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    return _rel_next_prev(idx, target, q, +1)


def rel_prev(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    return _rel_next_prev(idx, target, q, -1)


def _rel_next_prev_same_kind(idx: Index, target: Scope, q: Query, direction: int) -> tuple[Scope, ...]:
    ids = idx.kind_to_ids.get(target.kind, ())
    if not ids:
        return ()
    pos = None

    # Could be optimized with binary search if needed
    # or O(1) with kind_pos: dict[str, dict[int, int]]
    # but this is unlikely to be a bottleneck
    for i, sid in enumerate(ids):
        if sid == target.id:
            pos = i
            break

    if pos is None:
        return ()
    j = pos + direction
    while 0 <= j < len(ids):
        s = idx.by_id[ids[j]]
        if _matches(s, q):
            return (s,)
        j += direction
    return ()


def rel_next_same_kind(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    return _rel_next_prev_same_kind(idx, target, q, +1)


def rel_prev_same_kind(_g: ScopeGraph, idx: Index, target: Scope, q: Query) -> tuple[Scope, ...]:
    return _rel_next_prev_same_kind(idx, target, q, -1)


def rel_all_of_kind(_g: ScopeGraph, idx: Index, _t: Scope, q: Query) -> tuple[Scope, ...]:
    kind = q.kind or ""
    ids = idx.kind_to_ids.get(kind, ())
    scopes = (idx.by_id[sid] for sid in ids)
    return _cap((s for s in scopes if _matches(s, q)), q.max_items)


# ------------------------------------------------------------------------------
# ---- Relation registry -------------------------------------------------------
# ------------------------------------------------------------------------------
"""
The idea is that this imitates lisp-style meets prolog for “relation” functions 
that take(graph, index, target_scope, query) and return tuple[scopes].
"""

RELATIONS: dict[Axis, Relation] = {
    "self": rel_self,
    "parent": rel_parent,
    "children": rel_children,
    "ancestors": rel_ancestors,
    "descendants": rel_descendants,
    "siblings": rel_siblings,
    "next": rel_next,
    "prev": rel_prev,
    "next_same_kind": rel_next_same_kind,
    "prev_same_kind": rel_prev_same_kind,
    "all_of_kind": rel_all_of_kind,
}


def resolve_scopes(graph: ScopeGraph, idx: Index, q: Query) -> tuple[Scope, ...]:
    target = deepest_scope_at_line(idx, q.cursor)
    if target is None:
        return ()
    rel = RELATIONS.get(q.axis)
    if rel is None:
        return ()
    return rel(graph, idx, target, q)
