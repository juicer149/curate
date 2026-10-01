"""What a language file provides: a grammar and how it maps to scopes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional


@dataclass(frozen=True, slots=True)
class LanguageSpec:
    """
    How one Tree-sitter grammar maps to structural observations.

    scopes:
        node type -> fact label, for nodes that are structural regions.

    load:
        Returns the tree_sitter.Language. Called lazily, so the grammar
        package is only needed when the language is actually used.

    wrappers:
        node types that wrap a scope node (e.g. Python decorators). The
        wrapped scope's span starts at the wrapper's first line.

    label:
        Optional rule for languages whose label depends on more than the
        node type: (node, label from `scopes`) -> label. Markdown uses it
        to turn every `section` into h1..h6.

    outline:
        label -> "open" | "closed": which scopes make up the file's
        outline and how they show (see curate.outline).
    """

    scopes: Mapping[str, str]
    load: Callable[[], Any]
    wrappers: frozenset[str] = field(default_factory=frozenset)
    label: Optional[Callable[[Any, str], str]] = None
    outline: Mapping[str, str] = field(default_factory=dict)
