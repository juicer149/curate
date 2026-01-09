from __future__ import annotations

"""
Tree-sitter node abstraction.

This module defines the minimal interface expected from Tree-sitter nodes.
It exists to isolate Tree-sitter assumptions and enable testing/mocking.
"""

from typing import Optional, Protocol


class TSNode(Protocol):
    type: str
    children: list["TSNode"]

    @property
    def start_point(self) -> tuple[int, int]: ...
    @property
    def end_point(self) -> tuple[int, int]: ...

    def child_by_field_name(self, name: str) -> Optional["TSNode"]: ...


def node_span_lines(node: TSNode) -> tuple[int, int]:
    """
    Return the inclusive 1-based line span of a Tree-sitter node.
    Tree-sitter end_point is exclusive.
    """
    start_row, _ = node.start_point
    end_row, end_col = node.end_point

    s = start_row + 1

    # Tree-sitter end_point is exclusive:
    # if column == 0, node ends on previous line
    if end_col == 0:
        e = end_row
    else:
        e = end_row + 1

    return s, max(s, e)



def body_start_line(node: TSNode) -> Optional[int]:
    """
    Return the starting line of a node's body, if present.
    """
    body = node.child_by_field_name("body")
    return None if body is None else body.start_point[0] + 1
