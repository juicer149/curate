"""curate_core.containers.build

Deterministic construction of container trees.

This module assigns Address coordinates based purely on:
- explicit child ordering
- structural containment

It does NOT:
- inspect filesystem
- apply inclusion/exclusion policy
- read sources
"""

from __future__ import annotations

from typing import Dict, Iterable, Sequence

from curate_core.address import Address
from .model import ContainerKind, ContainerNode, ContainerTree


def build_container_tree(
    *,
    root_name: str,
    children_fn,
) -> ContainerTree:
    """
    Build a container tree starting at Address.root().

    Parameters:
        root_name:
            Human-readable name for the root node.

        children_fn:
            Callable of the form:
                (parent: ContainerNode) -> Iterable[tuple[str, ContainerKind]]

            It must:
            - return children in deterministic order
            - NOT raise (totality expected from caller)

    Address assignment:
    - sibling order defines address suffix (0..k-1)
    """

    nodes: Dict[Address, ContainerNode] = {}

    root_addr = Address.root()
    root = ContainerNode(
        address=root_addr,
        kind=ContainerKind.ROOT,
        name=root_name,
    )
    nodes[root_addr] = root

    def assign(parent: ContainerNode) -> None:
        try:
            children = list(children_fn(parent))
        except Exception:
            return

        for i, (name, kind) in enumerate(children):
            addr = parent.address + i
            node = ContainerNode(
                address=addr,
                kind=kind,
                name=name,
            )
            nodes[addr] = node

            if kind is not ContainerKind.TERMINAL:
                assign(node)

    assign(root)

    return ContainerTree(root=root, nodes=nodes)
