"""collect_facts on hand-built nodes: runs without tree-sitter installed."""
from __future__ import annotations

from dataclasses import dataclass, field

from curate.producers.treesitter import PYTHON, collect_facts


@dataclass
class N:
    """Minimal stand-in for a Tree-sitter node (rows are 0-based)."""
    type: str
    start: int
    end: int
    children: list["N"] = field(default_factory=list)

    @property
    def start_point(self) -> tuple[int, int]:
        return (self.start, 0)

    @property
    def end_point(self) -> tuple[int, int]:
        return (self.end, 0)


def facts(root: N) -> list[tuple[str, int, int]]:
    out = collect_facts(root, scopes=PYTHON.scopes, wrappers=PYTHON.wrappers)
    return [(f.label, f.span.start, f.span.end) for f in out]


def test_nested_definitions_become_one_based_line_facts():
    tree = N("module", 0, 9, [
        N("function_definition", 0, 5, [
            N("block", 1, 5, [
                N("if_statement", 2, 4, [N("else_clause", 4, 4)]),
            ]),
        ]),
        N("class_definition", 7, 9),
    ])
    assert facts(tree) == [
        ("function", 1, 6),
        ("if", 3, 5),
        ("else", 5, 5),
        ("class", 8, 10),
    ]


def test_decorator_line_is_part_of_the_definition():
    tree = N("module", 0, 4, [
        N("decorated_definition", 0, 4, [
            N("decorator", 0, 0),
            N("function_definition", 1, 4),
        ]),
    ])
    assert facts(tree) == [("function", 1, 5)]


def test_non_structural_nodes_emit_nothing():
    tree = N("module", 0, 2, [N("expression_statement", 0, 0), N("comment", 1, 1)])
    assert facts(tree) == []


def test_deep_nesting_does_not_recurse():
    node = N("function_definition", 0, 2000)
    root = node
    for i in range(1, 2000):
        child = N("if_statement", i, 2000)
        node.children.append(child)
        node = child
    assert len(facts(root)) == 2000
