from __future__ import annotations

"""
Tree traversal mechanics.

This module contains the pure traversal algorithm:
- DFS walk
- parent/child propagation
- state management

It contains NO language logic and NO semantic interpretation.
"""

from dataclasses import dataclass
from typing import Optional

from ...model import Scope
from ...types import Role
from .node import TSNode


@dataclass
class TraversalState:
    next_id: int
    scopes: list[Scope]


def add_scope(
    st: TraversalState,
    *,
    parent_id: Optional[int],
    kind: str,
    start: int,
    end: int,
    role: Role,
    header_lines: int,
) -> int:
    sid = st.next_id
    st.next_id += 1
    st.scopes.append(
        Scope(
            id=sid,
            parent_id=parent_id,
            kind=kind,
            start=start,
            end=end,
            role=role,
            header_lines=max(1, header_lines),
        )
    )
    return sid
