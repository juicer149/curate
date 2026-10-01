"""
Markdown: sections by heading.

The block grammar nests a `section` per heading: everything up to the
next heading of the same or a higher level, with deeper headings as
child sections. Each section is labelled by its heading level, h1..h6.
"""

from __future__ import annotations

from typing import Any

from ..spec import LanguageSpec

NAMES = ("markdown", "md")
EXTENSIONS = (".md", ".markdown")

_SETEXT = {"setext_h1_underline": "h1", "setext_h2_underline": "h2"}


def _load() -> Any:
    import tree_sitter_markdown as ts
    from tree_sitter import Language

    return Language(ts.language())


def _heading_level(node: Any, default: str) -> str:
    """h1..h6 from the section's heading marker; `default` if it has none."""
    for child in node.children:
        if child.type == "atx_heading":
            for part in child.children:
                kind = part.type  # atx_h2_marker -> h2
                if kind.startswith("atx_h") and kind.endswith("_marker"):
                    return "h" + kind[len("atx_h"):-len("_marker")]
        elif child.type == "setext_heading":
            for part in child.children:
                if part.type in _SETEXT:
                    return _SETEXT[part.type]
    return default


SPEC = LanguageSpec(
    scopes={"section": "section"},
    label=_heading_level,
    load=_load,
)
