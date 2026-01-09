from __future__ import annotations

"""
Node-level semantics expressed as data.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class NodePolicy:
    """
    Policy describing how a Tree-sitter node behaves.

    is_scope:
      Create a Scope from this node.

    noop:
      Node never becomes a scope; traversal continues transparently.

    include_in_child_start:
      Node is a wrapper. Its start line should be forwarded
      to a selected child scope.

    kind:
      Optional override of scope.kind.
    """

    is_scope: bool
    noop: bool = False
    include_in_child_start: bool = False
    kind: Optional[str] = None
