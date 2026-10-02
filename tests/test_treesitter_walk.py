"""collect_facts on hand-built nodes: runs without tree-sitter installed."""
from __future__ import annotations

from dataclasses import dataclass, field

from curate.producers.treesitter import collect_facts
from curate.producers.treesitter.languages.markdown import SPEC as MARKDOWN
from curate.producers.treesitter.languages.python import SPEC as PYTHON


@dataclass
class N:
    """Minimal stand-in for a Tree-sitter node (rows are 0-based)."""
    type: str
    start: int
    end: int
    children: list["N"] = field(default_factory=list)
    end_col: int = 1  # Python-like nodes end mid-line, after their last character

    @property
    def start_point(self) -> tuple[int, int]:
        return (self.start, 0)

    @property
    def end_point(self) -> tuple[int, int]:
        return (self.end, self.end_col)


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


def test_decorated_definition_keeps_its_head():
    tree = N("module", 0, 6, [
        N("decorated_definition", 0, 6, [
            N("decorator", 0, 0),
            N("decorator", 1, 1),
            N("class_definition", 2, 6, [N("function_definition", 4, 6)]),
        ]),
    ])
    out = collect_facts(tree, scopes=PYTHON.scopes, wrappers=PYTHON.wrappers)
    assert [(f.label, f.span.start, f.head) for f in out] == [
        ("class", 1, 3),
        ("function", 5, None),
    ]


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


def test_node_ending_at_column_zero_does_not_own_that_line():
    # Markdown sections end at (row of next heading, 0).
    tree = N("document", 0, 5, [
        N("section", 0, 4, end_col=0, children=[
            N("section", 2, 4, end_col=0),
        ]),
        N("section", 4, 5, end_col=0),
    ])
    out = collect_facts(tree, scopes={"section": "section"})
    assert [(f.span.start, f.span.end) for f in out] == [(1, 4), (3, 4), (5, 5)]


def test_single_line_node_at_column_zero_keeps_its_line():
    out = collect_facts(N("section", 3, 3, end_col=0), scopes={"section": "section"})
    assert [(f.span.start, f.span.end) for f in out] == [(4, 4)]


def test_markdown_sections_are_labelled_by_heading_level():
    def section(level: int, start: int, end: int, *children: N) -> N:
        heading = N("atx_heading", start, start, [N(f"atx_h{level}_marker", start, start)])
        return N("section", start, end, [heading, *children], end_col=0)

    setext = N("section", 6, 8, [
        N("setext_heading", 6, 7, [N("paragraph", 6, 6), N("setext_h2_underline", 7, 7)]),
    ], end_col=0)
    tree = N("document", 0, 8, [
        section(1, 0, 4, section(3, 2, 4)),
        N("section", 4, 6, [N("paragraph", 4, 5)], end_col=0),
        setext,
    ])
    out = collect_facts(tree, scopes=MARKDOWN.scopes, label=MARKDOWN.label)
    assert [(f.label, f.span.start, f.span.end) for f in out] == [
        ("h1", 1, 4),
        ("h3", 3, 4),
        ("section", 5, 6),
        ("h2", 7, 8),
    ]
