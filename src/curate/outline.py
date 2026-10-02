"""
Outline: which line ranges to fold so that only a file's skeleton shows.

Language-free. The caller says which labels are outline entries and how
each one shows:

    "closed"  folded whole: one line in the outline
              (a Python function: its body is detail)
    "open"    its own header stays visible, and so do the entries inside it
              (a Python class shows its methods; a Markdown section
              shows its subsections)

An open entry's fold covers its own lines up to its first nested entry;
with no nested entry it is folded whole. Entries inside a closed entry
disappear with it. Scopes that are not entries (an `if` block, say) are
transparent: entries inside them still show.

The resulting ranges never overlap, so an editor can apply them in any
order.

Levels fold the outline further, one nesting level at a time. Level 1
is the outline above. Each level after it closes the deepest open
entries that still show entries inside them: in Python, level 2 folds
classes whole; in Markdown, level 2 folds the deepest sections into
their headings, and so on until every top-level entry is one line.
`outline_levels` says how many levels a file has.
"""

from __future__ import annotations

from typing import Literal, Mapping

from .address import Address
from .facts import Scope, ScopeSet
from .geometry import Span

OutlineKind = Literal["open", "closed"]

OPEN: OutlineKind = "open"
CLOSED: OutlineKind = "closed"


def outline_folds(
    scopes: ScopeSet, kinds: Mapping[str, str], *, level: int = 1
) -> tuple[Span, ...]:
    """Ranges to fold for the outline at `level`, ordered by start line."""
    entries, depth, first_inside = _entries(scopes, kinds)

    closed = {e.address for e in entries if kinds[e.label] == CLOSED}
    if level > 1:
        # Open entries this deep or deeper fold whole as well.
        close_from = _deepest_open_parent(entries, kinds, depth, first_inside) - (level - 2)
        closed |= {
            e.address for e in entries
            if kinds[e.label] == OPEN and depth[e.address] >= close_from
        }

    folds: list[Span] = []
    for e in entries:
        if _inside_any(e.address, closed):
            continue
        start, end = e.span.start, e.span.end
        if e.address not in closed and e.address in first_inside:
            end = first_inside[e.address] - 1
        if end > start:
            folds.append(Span(start, end))

    return tuple(sorted(folds, key=lambda s: s.start))


def outline_levels(scopes: ScopeSet, kinds: Mapping[str, str]) -> int:
    """How many outline levels the file has: 1, plus one per nesting level to close."""
    entries, depth, first_inside = _entries(scopes, kinds)
    return 1 + _deepest_open_parent(entries, kinds, depth, first_inside)


def _entries(
    scopes: ScopeSet, kinds: Mapping[str, str]
) -> tuple[list[Scope], dict[Address, int], dict[Address, int]]:
    """
    The outline entries (outermost first), each one's entry depth (1 at the
    top, counting only entries), and for every scope the first line of an
    entry strictly inside it.
    """
    entries = sorted(
        (s for s in scopes.scopes if s.label in kinds and s.address != Address.root()),
        key=lambda s: s.address.depth,
    )

    depth: dict[Address, int] = {}
    for e in entries:
        a = e.address.parent
        while a is not None and a not in depth:
            a = a.parent
        depth[e.address] = 1 if a is None else depth[a] + 1

    # Ancestors always hold a value <= their descendants', so the walk
    # up can stop at the first ancestor that already has a smaller one.
    first_inside: dict[Address, int] = {}
    for e in entries:
        a = e.address.parent
        while a is not None:
            current = first_inside.get(a)
            if current is not None and current <= e.span.start:
                break
            first_inside[a] = e.span.start
            a = a.parent

    return entries, depth, first_inside


def _deepest_open_parent(
    entries: list[Scope],
    kinds: Mapping[str, str],
    depth: dict[Address, int],
    first_inside: dict[Address, int],
) -> int:
    """
    Depth of the deepest visible open entry with entries inside it; 0 if
    none. Entries inside a closed one never show, so they do not count.
    """
    closed = {e.address for e in entries if kinds[e.label] == CLOSED}
    return max(
        (depth[e.address] for e in entries
         if kinds[e.label] == OPEN
         and e.address in first_inside
         and not _inside_any(e.address, closed)),
        default=0,
    )


def _inside_any(address: Address, ancestors: set[Address]) -> bool:
    a = address.parent
    while a is not None:
        if a in ancestors:
            return True
        a = a.parent
    return False
