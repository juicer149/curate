"""treesitter.producer — generic Tree-sitter -> ScopeSet compiler

Algorithm (structural only):
1) Load LanguageSpec by key
2) If no loader -> fallback to module-only ScopeSet
3) Parse source with Tree-sitter
4) Walk syntax tree:
   - wrapper forwarding (start_line override into child)
   - emit Scope when node.type in rules.scope_node_types
5) Return ScopeSet with deterministic ordering

Non-goals:
- no header/body splitting
- no doc detection
- no filtering/policy
"""

from __future__ import annotations

from typing import Optional

from tree_sitter import Parser

from ...facts import Scope, ScopeSet
from .registry import LANGUAGES


def _module_only(source: str) -> ScopeSet:
    # Use count("\n")+1 to match editor line model (trailing newline adds a line)
    total_lines = max(1, source.count("\n") + 1)
    return ScopeSet((Scope(id=0, parent_id=None, kind="module", start=1, end=total_lines),))


def build_scope_set(*, source: str, language: str) -> ScopeSet:
    spec = LANGUAGES.get((language or "default").lower(), LANGUAGES["default"])

    if spec.loader is None:
        return _module_only(source)

    try:
        parser = Parser(spec.loader())
        tree = parser.parse(source.encode("utf-8", errors="replace"))
        root = tree.root_node
    except Exception:
        return _module_only(source)

    scopes: list[Scope] = [
        Scope(id=0, parent_id=None, kind="module", start=1, end=max(1, root.end_point[0] + 1))
    ]
    next_id = 1

    def walk(node, parent_id: int, forced_start: Optional[int] = None) -> None:
        nonlocal next_id

        # 1) Wrapper forwarding
        for wr in spec.rules.wrapper_rules:
            if node.type == wr.wrapper_type:
                for ch in node.children:
                    if ch.type in wr.target_types:
                        wrapper_start = node.start_point[0] + 1
                        walk(ch, parent_id, forced_start=wrapper_start)

                        # Walk remaining children as transparent structure
                        for other in node.children:
                            if other is not ch:
                                walk(other, parent_id)
                        return

        # 2) Scope emission
        if node.type in spec.rules.scope_node_types:
            start = node.start_point[0] + 1
            end = node.end_point[0] + 1

            # forced_start may only move start earlier
            if forced_start is not None and forced_start < start:
                start = forced_start

            sid = next_id
            next_id += 1

            # Ensure end is at least start (defensive)
            end = max(start, end)

            scopes.append(Scope(id=sid, parent_id=parent_id, kind=node.type, start=start, end=end))
            parent_id = sid

        # 3) Recurse
        for ch in node.children:
            walk(ch, parent_id)

    for ch in root.children:
        walk(ch, parent_id=0)

    # Deterministic: outer first, stable tie-break by id
    scopes.sort(key=lambda s: (s.start, -s.end, s.id))
    return ScopeSet(tuple(scopes))
