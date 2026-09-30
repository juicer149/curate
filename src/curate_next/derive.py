"""curate_next.core.derive — derive laminar structure + addresses from RawScopeSet

This module is the *structural motor* of Curate.

Pipeline
--------
Input:
- source text
- RawScopeSet (producer facts: label + positional span)

Output:
- ScopeSet with:
  - deterministic laminar structure (line-based)
  - deterministic Address assignment
  - always a root scope at Address.root()

Design principles
-----------------
- Producers never assign addresses or hierarchy
- Core owns laminarity + address policy
- Derivation is TOTAL (never raises for bad input)
- Determinism over completeness: when in doubt, drop consistently

Position handling
-----------------
Raw scopes may have (row, col). Core derives structure by projecting to LINE spans:
    start_line = raw.start.row
    end_line   = raw.end.row

Column precision and meta are carried through but do not affect laminar policy.

Laminar policy (important)
--------------------------
Scopes are made laminar via a containment stack (line geometry).

Sibling policy under same parent:
- Siblings must not *cross* the accepted frontier.
- Nested scopes are handled by the stack.
- Equal-span scopes are reduced to one representative (policy below).
"""

from __future__ import annotations

from typing import Dict, List

from .address import Address
from .facts import Position, RawScope, RawScopeSet, Scope, ScopeSet
from .normalize import clamp_to_document, clamp_to_parent, compose


def _total_lines(source: str) -> int:
    return max(1, source.count("\n") + 1)


def derive_scope_set(*, source: str, raw: RawScopeSet) -> ScopeSet:
    # ------------------------------------------------------------
    # document + root
    # ------------------------------------------------------------
    total = _total_lines(source)
    clamp_doc = clamp_to_document(total)

    root_addr = Address.root()
    root = Scope(
        address=root_addr,
        label="module",
        start=1,
        end=total,
        meta={"kind": "root"},
    )

    # ------------------------------------------------------------
    # normalize raw scopes to document bounds (line projection)
    # ------------------------------------------------------------
    candidates: List[RawScope] = []
    for r in raw:
        s_line, e_line = clamp_doc(r.start_line, r.end_line)

        # Keep original column if present; clamp only rows.
        start = r.start.with_row(s_line)
        end = r.end.with_row(e_line)

        candidates.append(
            RawScope(
                label=r.label,
                start=start,
                end=end,
                meta=r.meta,
            )
        )

    # Sort by LINE geometry first, then label for deterministic tie-breaking
    candidates.sort(key=lambda r: (r.start_line, -r.end_line, r.label))

    # ------------------------------------------------------------
    # derivation state
    # ------------------------------------------------------------
    derived: List[Scope] = [root]

    # containment stack (always laminar)
    stack: List[Scope] = [root]

    # next child index per parent (guarantees 0..k-1, no gaps)
    next_index: Dict[tuple[int, ...], int] = {root_addr.parts: 0}

    # frontier per parent: end of last *accepted* sibling
    last_end: Dict[tuple[int, ...], int] = {root_addr.parts: root.start - 1}

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------
    def contains(parent: Scope, start: int, end: int) -> bool:
        return parent.start <= start and end <= parent.end

    def assign_child(parent: Scope) -> Address:
        k = parent.address.parts
        i = next_index.get(k, 0)
        next_index[k] = i + 1
        return parent.address + i

    # ------------------------------------------------------------
    # main derivation loop
    # ------------------------------------------------------------
    for r in candidates:
        start, end = r.start_line, r.end_line

        # Find deepest container that can contain this span (line geometry)
        while stack and not contains(stack[-1], start, end):
            stack.pop()

        if not stack:
            stack = [root]

        parent = stack[-1]

        # Clamp strictly inside parent (defensive)
        norm = compose(clamp_to_parent(parent.start, parent.end))
        start, end = norm(start, end)

        # --------------------------------------------------------
        # Equal-span reduction policy
        # --------------------------------------------------------
        # If a raw scope has EXACTLY the same line span as its parent,
        # we drop it. This avoids infinite or meaningless chains.
        #
        # Policy: first (sorted) representative wins.
        if start == parent.start and end == parent.end:
            continue

        # --------------------------------------------------------
        # Refined sibling overlap policy
        # --------------------------------------------------------
        pe = last_end.get(parent.address.parts, parent.start - 1)

        # Drop ONLY if this scope truly crosses the accepted frontier:
        #   it starts before or at pe AND extends beyond pe.
        #
        # If it is fully contained (end <= pe), it *should* belong
        # under a deeper scope, and the stack logic is responsible
        # for placing it correctly.
        if start <= pe and end > pe:
            continue

        # Accept scope
        addr = assign_child(parent)

        # Carry producer payload through (but do not interpret it here)
        meta = dict(r.meta)
        # Optionally preserve raw positions for downstream tools:
        meta.setdefault("start_pos", (int(r.start.row), r.start.col))
        meta.setdefault("end_pos", (int(r.end.row), r.end.col))

        sc = Scope(
            address=addr,
            label=r.label,
            start=start,
            end=end,
            meta=meta,
        )

        derived.append(sc)

        # Update sibling frontier for this parent
        last_end[parent.address.parts] = max(pe, end)

        # This scope becomes the new deepest container
        stack.append(sc)

        # Initialize state for this new parent
        next_index.setdefault(sc.address.parts, 0)
        last_end.setdefault(sc.address.parts, sc.start - 1)

    # ------------------------------------------------------------
    # finalize
    # ------------------------------------------------------------
    return ScopeSet(tuple(derived))
