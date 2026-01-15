"""curate.index — derived acceleration structure (stateless)

Index contains no new information:
- derived from ScopeSet
- safe to rebuild anytime
- provides fast navigation primitives

Assumes:
- scopes are laminar
- scopes are in deterministic order (start asc, end desc, id asc)
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Optional

from .facts import Scope, ScopeSet


@dataclass(frozen=True, slots=True)
class Index:
    scopes: tuple[Scope, ...]
    by_id: dict[int, Scope]
    parent: dict[int, Optional[int]]
    children: dict[int, tuple[int, ...]]
    starts: tuple[int, ...]
    ends: tuple[int, ...]


def build_index(scopeset: ScopeSet) -> Index:
    scopes = scopeset.scopes
    by_id = {s.id: s for s in scopes}
    parent = {s.id: s.parent_id for s in scopes}

    kids: dict[int, list[int]] = {}
    for s in scopes:
        if s.parent_id is not None:
            kids.setdefault(s.parent_id, []).append(s.id)

    # Deterministic child ordering
    children: dict[int, tuple[int, ...]] = {}
    for pid, ids in kids.items():
        ids.sort(key=lambda sid: (by_id[sid].start, -by_id[sid].end, sid))
        children[pid] = tuple(ids)

    starts = tuple(s.start for s in scopes)
    ends = tuple(s.end for s in scopes)

    return Index(
        scopes=scopes,
        by_id=by_id,
        parent=parent,
        children=children,
        starts=starts,
        ends=ends,
    )


def scope_at_line(idx: Index, line: int) -> Optional[Scope]:
    """
    Return the deepest scope containing `line` (1-based), or None.

    Complexity:
    - bisect into starts
    - back up until we find a containing candidate
    - descend through children (laminar => at most one child contains line)
    """
    if not idx.scopes:
        return None

    i = bisect_right(idx.starts, line) - 1
    if i < 0:
        return None

    while i >= 0 and idx.ends[i] < line:
        i -= 1
    if i < 0:
        return None

    cand = idx.scopes[i]
    if not cand.contains(line):
        return None

    while True:
        found = None
        for cid in idx.children.get(cand.id, ()):
            c = idx.by_id[cid]
            if c.contains(line):
                found = c
                break
        if found is None:
            return cand
        cand = found
