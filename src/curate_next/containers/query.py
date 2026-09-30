"""curate_core.containers.query

Read-only queries over ContainerTree.

All relations are derived from Address algebra.
"""

from __future__ import annotations

from typing import Tuple

from curate_core.address import Address
from .model import ContainerNode, ContainerTree


def node_by_address(tree: ContainerTree, addr: Address) -> ContainerNode | None:
    return tree.nodes.get(addr)


def parent_node(tree: ContainerTree, node: ContainerNode) -> ContainerNode | None:
    p = node.address.parent
    if p is None:
        return None
    return tree.nodes.get(p)


def children_nodes(tree: ContainerTree, node: ContainerNode) -> Tuple[ContainerNode, ...]:
    """
    Enumerate children in address order (0..k-1).

    Safe because builder guarantees contiguous sibling indices.
    """
    out = []
    i = 0
    while True:
        addr = node.address + i
        child = tree.nodes.get(addr)
        if child is None:
            break
        out.append(child)
        i += 1
    return tuple(out)


def is_ancestor(a: ContainerNode, b: ContainerNode) -> bool:
    return a.address.is_prefix_of(b.address)
