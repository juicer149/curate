"""treesitter.producer — syntax tree → ScopeSet

This module:
- walks Tree-sitter trees
- emits laminar structural facts
- assigns hierarchical addresses

No interpretation.
"""

from tree_sitter import Parser

from ...facts import Scope, ScopeSet, ScopeAddress
from .registry import LANGUAGES


def build_scope_set(*, source: str, language: str) -> ScopeSet:
    spec = LANGUAGES.get(language, LANGUAGES["default"])

    total_lines = max(1, source.count("\n") + 1)
    root = Scope(
        address=(0,),
        label="module",
        start=1,
        end=total_lines,
    )

    if spec.loader is None:
        return ScopeSet((root,))

    try:
        parser = Parser(spec.loader())
        tree = parser.parse(source.encode("utf-8", errors="replace"))
        root_node = tree.root_node
    except Exception:
        return ScopeSet((root,))

    scopes: list[Scope] = [root]
    counters: dict[ScopeAddress, int] = {(0,): 0}

    rules = spec.rules

    def next_address(parent: ScopeAddress) -> ScopeAddress:
        n = counters.get(parent, 0)
        counters[parent] = n + 1
        return parent + (n,)

    def span(node) -> int:
        return node.end_point[0] - node.start_point[0] + 1

    def should_emit(node) -> bool:
        if node.type in rules.exclude:
            return False
        if node.type not in rules.include:
            return False
        if rules.only_multiline and span(node) < 2:
            return False
        return True

    def walk(node, parent_addr: ScopeAddress) -> None:
        current_parent = parent_addr

        if should_emit(node):
            addr = next_address(parent_addr)
            scopes.append(
                Scope(
                    address=addr,
                    label=node.type,
                    start=node.start_point[0] + 1,
                    end=max(
                        node.end_point[0] + 1,
                        node.start_point[0] + 1,
                    ),
                )
            )
            current_parent = addr

        for ch in node.children:
            walk(ch, current_parent)

    for ch in root_node.children:
        walk(ch, (0,))

    scopes.sort(key=lambda s: (s.start, -s.end, s.address))
    return ScopeSet(tuple(scopes))
