"""
curate_core.containers

Pure container geometry in Address space.
This package defines:
- container nodes
- deterministic address assignment
- prefix-based containment queries

It is intentionally unaware of:
- filesystem paths
- sources
- languages
- parsing
- editors
"""

from .model import ContainerKind, ContainerNode, ContainerTree
from .build import build_container_tree
from .query import (
    node_by_address,
    parent_node,
    children_nodes,
    is_ancestor,
)

__all__ = [
    "ContainerKind",
    "ContainerNode",
    "ContainerTree",
    "build_container_tree",
    "node_by_address",
    "parent_node",
    "children_nodes",
    "is_ancestor",
]
