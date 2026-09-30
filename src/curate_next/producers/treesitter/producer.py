"""
treesitter.producer — Tree-sitter → RawScopeSet

This producer:
- parses source text with Tree-sitter
- walks the syntax tree
- emits raw structural observations (RawScope)

It does NOT:
- assign addresses
- enforce laminarity
- create root scopes
- sort or normalize output
"""

from __future__ import annotations

from typing import List

from tree_sitter import Parser

from curate_next.facts import Position, RawScope, RawScopeSet
from .registry import LANGUAGES


def build_raw_scope_set(*, source: str, language: str) -> RawScopeSet:
    spec = LANGUAGES.get(language, LANGUAGES["default"])

    # If no grammar loader exists, emit no raw scopes.
    if spec.loader is None:
        return RawScopeSet(())

    try:
        parser = Parser(spec.loader())
        tree = parser.parse(source.encode("utf-8", errors="replace"))
        root_node = tree.root_node
    except Exception:
        # Structural degradation: emit nothing.
        return RawScopeSet(())

    rules = spec.rules
    raw_scopes: List[RawScope] = []

    def span_lines(node) -> int:
        return node.end_point[0] - node.start_point[0] + 1

    def should_emit(node) -> bool:
        if node.type in rules.exclude:
            return False
        if node.type not in rules.include:
            return False
        if rules.only_multiline and span_lines(node) < 2:
            return False
        return True

    def walk(node) -> None:
        if should_emit(node):
            raw_scopes.append(
                RawScope(
                    label=node.type,
                    start=Position(
                        row=node.start_point[0] + 1,
                        col=node.start_point[1],
                    ),
                    end=Position(
                        row=node.end_point[0] + 1,
                        col=node.end_point[1],
                    ),
                    meta={
                        "node_type": node.type,
                        "byte_range": (node.start_byte, node.end_byte),
                    },
                )
            )

        for ch in node.children:
            walk(ch)

    for ch in root_node.children:
        walk(ch)

    return RawScopeSet(raw_scopes)
