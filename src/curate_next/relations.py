"""curate.relations — pure relational functions (stateless)

No DSL.
No policies.
No side effects.

All functions operate on:
- Index (derived)
- Scope (fact)
"""

from __future__ import annotations

from .facts import Scope
from .index import Index


def parent(idx: Index, s: Scope) -> Scope | None:
    pid = idx.parent.get(s.id)
    return None if pid is None else idx.by_id[pid]


def children(idx: Index, s: Scope) -> tuple[Scope, ...]:
    return tuple(idx.by_id[cid] for cid in idx.children.get(s.id, ()))


def ancestors(idx: Index, s: Scope) -> tuple[Scope, ...]:
    out: list[Scope] = []
    cur = s
    while True:
        p = parent(idx, cur)
        if p is None:
            return tuple(out)
        out.append(p)
        cur = p


def descendants(idx: Index, s: Scope) -> tuple[Scope, ...]:
    out: list[Scope] = []

    def walk(x: Scope) -> None:
        for c in children(idx, x):
            out.append(c)
            walk(c)

    walk(s)
    return tuple(out)


def siblings(idx: Index, s: Scope) -> tuple[Scope, ...]:
    p = parent(idx, s)
    if p is None:
        return ()
    return tuple(c for c in children(idx, p) if c.id != s.id)
