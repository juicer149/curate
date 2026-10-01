"""
Tree-sitter producer: source text -> RawFactSet.

Observes structural regions with a Tree-sitter grammar and reports them
as RawFact(label, Span) over 1-based, inclusive LINE coordinates.

It does NOT decide structure: no addresses, no nesting, no root, no
conflict resolution. That is curation's job.

Layout:
    spec.py         LanguageSpec: what a language file provides
    walk.py         collect_facts: the language-free tree walk
    languages/      one file per language (python.py, markdown.py, ...)

Tree-sitter is imported lazily, so `import curate` works without it.
"""

from __future__ import annotations

from ...facts import RawFactSet
from .languages import get_spec, language_for_path
from .spec import LanguageSpec
from .walk import collect_facts

__all__ = [
    "LanguageSpec",
    "build_raw_facts",
    "collect_facts",
    "get_spec",
    "language_for_path",
]


def build_raw_facts(*, source: str, language: str) -> RawFactSet:
    """
    Producer contract: (source, language) -> RawFactSet.

    Unknown languages produce no facts. Raises if Tree-sitter or the
    grammar is missing; compile_scopes turns that into an empty result
    and reports it through on_error.
    """
    spec = get_spec(language)
    if spec is None:
        return RawFactSet.from_iter(())

    from tree_sitter import Parser

    parser = Parser(spec.load())
    tree = parser.parse(source.encode("utf-8", errors="replace"))
    return RawFactSet.from_iter(
        collect_facts(
            tree.root_node,
            scopes=spec.scopes,
            wrappers=spec.wrappers,
            label=spec.label,
        )
    )
