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
"""

from __future__ import annotations

from typing import Literal, Mapping

from .address import Address
from .facts import ScopeSet
from .geometry import Span

OutlineKind = Literal["open", "closed"]

OPEN: OutlineKind = "open"
CLOSED: OutlineKind = "closed"


def outline_folds(scopes: ScopeSet, kinds: Mapping[str, str]) -> tuple[Span, ...]:
    """Ranges to fold for the outline, ordered by start line."""
    entries = sorted(
        (s for s in scopes.scopes if s.label in kinds and s.address != Address.root()),
        key=lambda s: s.address.depth,
    )

    # For every scope: the first line of an entry strictly inside it.
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

    closed = {e.address for e in entries if kinds[e.label] == CLOSED}

    folds: list[Span] = []
    for e in entries:
        if _inside_any(e.address, closed):
            continue
        start, end = e.span.start, e.span.end
        if kinds[e.label] == OPEN and e.address in first_inside:
            end = first_inside[e.address] - 1
        if end > start:
            folds.append(Span(start, end))

    return tuple(sorted(folds, key=lambda s: s.start))


def _inside_any(address: Address, ancestors: set[Address]) -> bool:
    a = address.parent
    while a is not None:
        if a in ancestors:
            return True
        a = a.parent
    return False
