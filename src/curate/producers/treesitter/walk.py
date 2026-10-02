"""The language-free tree walk: syntax tree -> RawFacts."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping, Optional

from ...facts import RawFact
from ...geometry import Span


def line_span(node: Any) -> tuple[int, int]:
    """
    1-based, inclusive line span of a node.

    A node that ends at column 0 of a later row owns only the newline
    before it, not that row. Markdown sections end like this, at the
    start of the next heading; counting that row would make neighbouring
    sections cross.
    """
    start_row = node.start_point[0]
    end_row, end_col = node.end_point
    start = start_row + 1
    end = end_row if (end_col == 0 and end_row > start_row) else end_row + 1
    return start, max(start, end)


def collect_facts(
    root: Any,
    *,
    scopes: Mapping[str, str],
    wrappers: Iterable[str] = (),
    label: Optional[Callable[[Any, str], str]] = None,
) -> list[RawFact]:
    """
    Walk a syntax tree and emit one RawFact per structural node.

    A node needs: .type, .children, .start_point, .end_point
    (points are (row, column), 0-based rows).

    Iterative, so deep nesting cannot hit the recursion limit.
    """
    wrapper_types = frozenset(wrappers)
    facts: list[RawFact] = []

    # (node, start line forced by an enclosing wrapper, or None)
    stack: list[tuple[Any, Optional[int]]] = [(root, None)]

    while stack:
        node, forced_start = stack.pop()
        name = scopes.get(node.type)

        if name is not None:
            start, end = line_span(node)
            head: Optional[int] = None
            if forced_start is not None and forced_start < start:
                head, start = start, forced_start
            if label is not None:
                name = label(node, name)
            facts.append(RawFact(name, Span(start, end), head))

        child_forced: Optional[int] = None
        if node.type in wrapper_types:
            child_forced = node.start_point[0] + 1

        for child in reversed(node.children):
            forced = child_forced if child.type in scopes else None
            stack.append((child, forced))

    return facts
