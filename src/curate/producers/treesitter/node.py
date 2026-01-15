"""
Tree-sitter node helpers.

This module provides:
- A minimal protocol describing the Tree-sitter node interface
- Small, pure helper functions for extracting line-based spans

This module must remain:
- Language-agnostic
- Free of policy
- Free of traversal logic
"""

from __future__ import annotations

from typing import Optional, Protocol


class TSNode(Protocol):
    """
    Minimal structural interface of a Tree-sitter AST node.

    This protocol exists to:
    - Avoid tight coupling to concrete Tree-sitter classes
    - Enable static type checking
    """
    type: str
    children: list["TSNode"]

    @property
    def start_point(self) -> tuple[int, int]: ...
    @property
    def end_point(self) -> tuple[int, int]: ...

    def child_by_field_name(self, name: str) -> Optional["TSNode"]: ...


def node_span_lines(node: TSNode) -> tuple[int, int]:
    """
    Compute the inclusive line span of a node.

    Pseudocode:
    - Convert Tree-sitter 0-based line numbers to 1-based
    - Ensure end >= start
    """
    s = node.start_point[0] + 1
    e = node.end_point[0] + 1
    return s, max(s, e)


def body_start_line(node: TSNode) -> Optional[int]:
    """
    Determine where the 'body' of a node begins.

    Pseudocode:
    - Look up the child node named 'body'
    - If present: return its starting line (1-based)
    - Else: return None

    This is used to compute header vs body split for scopes.
    """
    body = node.child_by_field_name("body")
    return None if body is None else (body.start_point[0] + 1)
