"""curate_core.containers.model

Pure container geometry.

This module defines the minimal data model for hierarchical containers
that live in Address space.

Key ideas:
- containment is expressed ONLY via Address prefix
- nodes are immutable
- nodes carry no semantic meaning beyond "container vs terminal"

This layer does NOT know about:
- filesystem
- files
- sources
- languages
- scopes
- editors
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from curate_core.address import Address


class ContainerKind(str, Enum):
    """
    Container classification.

    Semantics:
    - ROOT: unique root of a container tree
    - CONTAINER: may have children
    - TERMINAL: leaf at this layer (may receive children from another layer)
    """

    ROOT = "root"
    CONTAINER = "container"
    TERMINAL = "terminal"


@dataclass(frozen=True, slots=True)
class ContainerNode:
    """
    A node in a container hierarchy.

    Invariants:
    - address uniquely identifies position in the hierarchy
    - containment is defined by Address prefix
    - kind expresses structural intent only (no policy)

    TERMINAL nodes are leaves at THIS layer, but may be extended later
    (e.g. a file receiving Scope children).
    """

    address: Address
    kind: ContainerKind
    name: str


@dataclass(frozen=True, slots=True)
class ContainerTree:
    """
    Immutable container tree.

    Invariants:
    - root.address == Address.root()
    - all addresses are unique
    - sibling indices are contiguous (0..k-1)
    """

    root: ContainerNode
    nodes: Mapping[Address, ContainerNode]
