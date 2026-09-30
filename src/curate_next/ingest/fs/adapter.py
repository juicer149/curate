"""curate_core.ingest.fs.adapter

Filesystem → ContainerTree adapter.

This module:
- walks the filesystem
- applies PathRules (policy)
- produces a deterministic ContainerTree

It does NOT:
- read file contents
- parse languages
- produce scopes
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from curate_core.containers import (
    ContainerKind,
    ContainerNode,
    ContainerTree,
    build_container_tree,
)
from .rules.protocol import PathRule
from .rules.registry import PATH_RULES


def ingest_filesystem(
    *,
    root: Path,
    rule_keys: Sequence[str] = ("binary", "gitignore", "manifest"),
    ordering: str = "files_first",
) -> ContainerTree:
    """
    Build a ContainerTree from a filesystem root.

    Parameters:
        root:
            Root directory.

        rule_keys:
            Ordered list of rule identifiers to apply.

        ordering:
            Sibling ordering strategy:
            - "files_first"
            - "folders_first"
    """

    root = root.expanduser().resolve()

    rules = _instantiate_rules(rule_keys)
    for r in rules:
        try:
            r.prepare(root=root)
        except Exception:
            continue

    def children_fn(parent: ContainerNode) -> Iterable[tuple[str, ContainerKind]]:
        path = root if parent.address.is_root else (root / parent.name)

        try:
            entries = list(path.iterdir())
        except Exception:
            return ()

        entries = [p for p in entries if _allowed(p, rules)]
        entries = _order(entries, ordering)

        for p in entries:
            kind = (
                ContainerKind.TERMINAL
                if p.is_file()
                else ContainerKind.CONTAINER            )
            yield (p.name, kind)

    return build_container_tree(
        root_name=root.name,
        children_fn=children_fn,
    )


# ---------------------------------------------------------------------------

def _instantiate_rules(keys: Sequence[str]) -> tuple[PathRule, ...]:
    out = []
    for k in keys:
        factory = PATH_RULES.get(k)
        if not factory:
            continue
        try:
            out.append(factory())
        except Exception:
            continue
    return tuple(out)


def _allowed(path: Path, rules: Sequence[PathRule]) -> bool:
    for r in rules:
        try:
            verdict = r.allow(path=path)
        except Exception:
            continue
        if verdict is False:
            return False
    return True


def _order(paths: Sequence[Path], ordering: str) -> list[Path]:
    items = list(paths)

    if ordering == "files_first":
        items.sort(key=lambda p: (p.is_dir(), p.name))
    elif ordering == "folders_first":
        items.sort(key=lambda p: (p.is_file(), p.name))
    else:
        raise ValueError(f"Unknown ordering: {ordering!r}")

    for r in PATH_RULES.values():
        try:
            items = list(r().order_children(parent=None, children=items))  # type: ignore
        except Exception:
            continue

    return items
