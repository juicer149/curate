"""
Tree-sitter producer: source text -> RawFactSet.

Observes structural regions with a Tree-sitter grammar and reports them
as RawFact(label, Span) over 1-based, inclusive LINE coordinates.

It does NOT decide structure: no addresses, no nesting, no root, no
conflict resolution. That is curation's job.

Tree-sitter is imported lazily, so `import curate` works without it.
Unknown languages produce no facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Optional

from ..facts import RawFact, RawFactSet
from ..geometry import Span


# ---------------------------------------------------------------------
# Language specs (data only)
# ---------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class LanguageSpec:
    """
    How one Tree-sitter grammar maps to structural observations.

    scopes:
        node type -> fact label, for nodes that are structural regions.

    wrappers:
        node types that wrap a scope node (e.g. decorators). The wrapped
        scope's span starts at the wrapper's first line.

    load:
        Returns the tree_sitter.Language. Called lazily.
    """

    scopes: Mapping[str, str]
    wrappers: frozenset[str]
    load: Callable[[], Any]


def _load_python() -> Any:
    import tree_sitter_python as tspython
    from tree_sitter import Language

    return Language(tspython.language())


PYTHON = LanguageSpec(
    scopes={
        "class_definition": "class",
        "function_definition": "function",
        "if_statement": "if",
        "elif_clause": "elif",
        "else_clause": "else",
        "for_statement": "for",
        "while_statement": "while",
        "with_statement": "with",
        "try_statement": "try",
        "except_clause": "except",
        "finally_clause": "finally",
        "match_statement": "match",
        "case_clause": "case",
    },
    wrappers=frozenset({"decorated_definition"}),
    load=_load_python,
)

LANGUAGES: dict[str, LanguageSpec] = {
    "python": PYTHON,
}


# ---------------------------------------------------------------------
# Tree walk (pure; works on anything shaped like a Tree-sitter node)
# ---------------------------------------------------------------------

def collect_facts(
    root: Any,
    *,
    scopes: Mapping[str, str],
    wrappers: Iterable[str] = (),
) -> list[RawFact]:
    """
    Walk a syntax tree and emit one RawFact per structural node.

    A node needs: .type, .children, .start_point, .end_point
    (points are (row, column), 0-based rows).

    Iterative, so deep nesting cannot hit the recursion limit.
    """
    wrapper_types = frozenset(wrappers)
    facts: list[RawFact] = []

    # (node, start line forced by an enclosing wrapper, or None)
    stack: list[tuple[Any, Optional[int]]] = [(root, None)]

    while stack:
        node, forced_start = stack.pop()
        label = scopes.get(node.type)

        if label is not None:
            start = node.start_point[0] + 1
            end = max(start, node.end_point[0] + 1)
            if forced_start is not None and forced_start < start:
                start = forced_start
            facts.append(RawFact(label, Span(start, end)))

        child_forced: Optional[int] = None
        if node.type in wrapper_types:
            child_forced = node.start_point[0] + 1

        for child in reversed(node.children):
            forced = child_forced if child.type in scopes else None
            stack.append((child, forced))

    return facts


# ---------------------------------------------------------------------
# Producer
# ---------------------------------------------------------------------

def build_raw_facts(*, source: str, language: str) -> RawFactSet:
    """
    Producer contract: (source, language) -> RawFactSet.

    Raises if Tree-sitter or the grammar is missing; compile_scopes
    turns that into an empty result and reports it through on_error.
    """
    spec = LANGUAGES.get((language or "").lower())
    if spec is None:
        return RawFactSet.from_iter(())

    from tree_sitter import Parser

    parser = Parser(spec.load())
    tree = parser.parse(source.encode("utf-8", errors="replace"))
    return RawFactSet.from_iter(
        collect_facts(tree.root_node, scopes=spec.scopes, wrappers=spec.wrappers)
    )
