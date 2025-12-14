"""
Block extraction (indentation-based).

This module discovers fold-worthy blocks that are NOT represented as separate
top-level AST nodes in a way that is convenient for editor folding.

Examples:
- if / elif / else
- for / while
- try / except / finally
- with
- match / case

Rule (Pythonic indentation):
A block starts at a "block head" line that ends with ':' and begins with a known
keyword. The block body continues until the next non-blank, non-comment line
whose indent is <= the head indent.

This is intentionally text/indent based.
It complements AST ownership rather than replaces it.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from .entity import Entity
from .line import Line


BLOCK_KEYWORDS = {
    "if",
    "elif",
    "else",
    "for",
    "while",
    "try",
    "except",
    "finally",
    "with",
    "match",
    "case",
}


def _indent_width(s: str) -> int:
    """
    Compute indentation width in a stable way.

    v0.1 policy:
    - tabs are counted as 4 spaces (simple, deterministic)
    - indentation is computed from leading whitespace only
    """
    width = 0
    for ch in s:
        if ch == " ":
            width += 1
        elif ch == "\t":
            width += 4
        else:
            break
    return width


def _is_blank(line: Line) -> bool:
    return line.text.strip() == ""


def _is_comment(line: Line) -> bool:
    return line.text.lstrip().startswith("#")


def _first_token(text: str) -> Optional[str]:
    s = text.lstrip()
    if not s:
        return None
    token = []
    for ch in s:
        if ch.isalnum() or ch == "_":
            token.append(ch)
        else:
            break
    return "".join(token) if token else None


def _is_entity_marker_line(line: Line) -> bool:
    """
    Lines that should not be treated as "block heads" by this module.
    (They are handled by AST or future entity extractors.)
    """
    s = line.text.lstrip()
    if s.startswith("@"):
        return True
    if s.startswith("def "):
        return True
    if s.startswith("class "):
        return True
    if s.startswith('"""') or s.startswith("'''"):
        return True
    return False


def _is_block_head(line: Line) -> Optional[str]:
    """
    Return keyword if line is a recognized block head, else None.
    """
    if "doc" in line.kinds:
        return None
    if _is_blank(line) or _is_comment(line):
        return None
    if _is_entity_marker_line(line):
        return None

    s = line.text.lstrip()
    if not s.endswith(":"):
        return None

    kw = _first_token(s)
    if kw in BLOCK_KEYWORDS:
        return kw
    return None


def _block_end(lines: Tuple[Line, ...], head_index: int) -> int:
    """
    Given a head line index in 'lines', find the inclusive end index of its body.
    """
    head = lines[head_index]
    head_indent = _indent_width(head.text)

    # If there's no following lines, body is empty.
    if head_index + 1 >= len(lines):
        return head_index

    last = head_index
    for j in range(head_index + 1, len(lines)):
        cur = lines[j]

        # blanks/comments are considered part of the body area (do not terminate)
        if _is_blank(cur) or _is_comment(cur):
            last = j
            continue

        cur_indent = _indent_width(cur.text)

        # Termination condition: dedent to <= head indent
        if cur_indent <= head_indent:
            return last

        last = j

    return last


def extract_block_entities(scope_lines: Tuple[Line, ...]) -> List[Entity]:
    """
    Extract block entities from the given scope lines.

    Returned entities are non-overlapping by construction:
    - once a block head is found, we skip scanning until after its body end
    """
    out: List[Entity] = []
    i = 0

    while i < len(scope_lines):
        line = scope_lines[i]
        kw = _is_block_head(line)

        if not kw:
            i += 1
            continue

        end_i = _block_end(scope_lines, i)

        head = (line,)
        body = tuple(scope_lines[i + 1 : end_i + 1]) if end_i >= i + 1 else tuple()

        out.append(
            Entity(
                kind="block",
                name=kw,
                category=None,
                head=head,
                body=body,
            )
        )

        # Skip to after this block
        i = end_i + 1

    return out
