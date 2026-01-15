# src/curate/index.py
"""
Indexing layer.

Transforms a ScopeGraph into auxiliary data structures
that enable efficient structural navigation.

All expensive precomputation lives here.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Optional

from .model import Scope, ScopeGraph


@dataclass(frozen=True, slots=True)
class Index:
    """
    Precomputed navigation tables over scopes.
    """

    by_id: dict[int, Scope]
    parent: dict[int, Optional[int]]
    children: dict[int, tuple[int, ...]]        # parent_id -> child ids (sorted)
    order: tuple[int, ...]                      # ids sorted by (start, -end, id)
    pos: dict[int, int]                         # id -> position in order (O(1) next/prev)
    kind_to_ids: dict[str, tuple[int, ...]]     # kind -> ids in order
    starts: tuple[int, ...]                     # start lines aligned with order
    ends: tuple[int, ...]                       # end lines aligned with order


def build_index(graph: ScopeGraph) -> Index:
    """
    Build all lookup tables from a ScopeGraph.

    Pseudocode:
    - Sort scopes in deterministic order
    - Build parent/children mappings
    - Build kind groupings
    - Precompute positional arrays
    """

    ordered = sorted(graph.scopes, key=lambda s: (s.start, -s.end, s.id))

    by_id = {s.id: s for s in ordered}
    parent = {s.id: s.parent_id for s in ordered}

    # Build children mapping
    kids: dict[int, list[int]] = {}
    for s in ordered:
        if s.parent_id is None:
            continue
        kids.setdefault(s.parent_id, []).append(s.id)

    # Sort children deterministically
    children: dict[int, tuple[int, ...]] = {}
    for pid, lst in kids.items():
        lst.sort(key=lambda sid: (by_id[sid].start, -by_id[sid].end, sid))
        children[pid] = tuple(lst)

    # Build kind groupings
    kind_map: dict[str, list[int]] = {}
    for s in ordered:
        kind_map.setdefault(s.kind, []).append(s.id)
    kind_to_ids = {k: tuple(v) for k, v in kind_map.items()}

    # Precompute positional arrays
    order = tuple(s.id for s in ordered)
    pos = {sid: i for i, sid in enumerate(order)}
    starts = tuple(by_id[sid].start for sid in order)
    ends = tuple(by_id[sid].end for sid in order)

    return Index(
        by_id=by_id,
        parent=parent,
        children=children,
        order=order,
        pos=pos,
        kind_to_ids=kind_to_ids,
        starts=starts,
        ends=ends,
    )


def deepest_scope_at_line(idx: Index, line: int) -> Optional[Scope]:
    """
    O(log n + depth): bisect on starts + descent using laminar children.
    """
    if not idx.order:
        return None

    i = bisect_right(idx.starts, line) - 1
    if i < 0:
        return None

    # back up if we landed in a gap (start<=line but end<line)
    while i >= 0 and idx.ends[i] < line:
        i -= 1
    if i < 0:
        return None

    cand = idx.by_id[idx.order[i]]
    if not cand.contains_line(line):
        # rare: keep backing to find any containing scope
        j = i - 1
        while j >= 0:
            s = idx.by_id[idx.order[j]]
            if s.contains_line(line):
                cand = s
                break
            j -= 1
        else:
            return None

    while True:
        found = None
        for cid in idx.children.get(cand.id, ()):
            c = idx.by_id[cid]
            if c.contains_line(line):
                found = c
                break
        if found is None:
            return cand
        cand = found
