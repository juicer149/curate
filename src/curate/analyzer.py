# ================================================================
# src/curate/analyzer.py
# ================================================================
"""
Core analyzer for Curate.

Responsibilities:
- Build Line objects from source text
- Extract a Scope tree (module / class / function)
- Represent both code entities and docstring entities explicitly
- Ensure every line has a single semantic ownership (code vs doc)

Key rules:
- Docstrings are extracted via AST ownership (first statement)
- Docstring lines are NEVER part of code entity bodies
- Docstrings are split into HEAD / BODY:
    HEAD = summary paragraph (until first blank line)
    BODY = remainder (including doctest, examples, etc.)
"""

from __future__ import annotations

import ast
from typing import Tuple, Union, Optional, List

from .entity import Entity
from .line import Line
from .scope import Scope

# ------------------------------------------------------------
# Types
# ------------------------------------------------------------

DocNode = Union[
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
]

# ------------------------------------------------------------
# Lines
# ------------------------------------------------------------

def build_lines(source_text: str) -> Tuple[Line, ...]:
    lines: List[Line] = []
    for i, text in enumerate(source_text.splitlines(), start=1):
        kinds = set()
        if text.lstrip().startswith("#"):
            kinds.add("comment")
        else:
            kinds.add("code")
        lines.append(Line(i, text, frozenset(kinds)))
    return tuple(lines)

# ------------------------------------------------------------
# Docstring helpers
# ------------------------------------------------------------

_TRIPLE_DOUBLE = '"""'
_TRIPLE_SINGLE = "'''"
_DELIMS = (_TRIPLE_DOUBLE, _TRIPLE_SINGLE)

def _detect_delim(s: str) -> Optional[str]:
    s2 = s.lstrip()
    for d in _DELIMS:
        if s2.startswith(d):
            return d
    return None

def _strip_doc_delimiters(raw: Tuple[Line, ...]) -> Tuple[Line, ...]:
    """
    Remove docstring delimiters while preserving indentation.
    Handles:
    - one-line docstrings: /"/"/"/summary/"/"/"
    - multi-line docstrings with delimiters on own lines
    """
    if not raw:
        return raw

    def replace_text(src: Line, new_text: str) -> Line:
        indent = src.text[: len(src.text) - len(src.text.lstrip())]
        return Line(src.number, indent + new_text, src.kinds)

    first = raw[0]
    last = raw[-1]
    delim = _detect_delim(first.text) or _detect_delim(last.text)
    if delim is None:
        return raw

    # One-line docstring
    if len(raw) == 1:
        stripped = first.text.lstrip()
        if stripped.startswith(delim) and stripped.endswith(delim):
            inner = stripped[len(delim):-len(delim)].strip()
            return (replace_text(first, inner),)
        return raw

    content = list(raw)

    # Opening delimiter
    if first.text.lstrip().strip() == delim:
        content = content[1:]
    elif first.text.lstrip().startswith(delim):
        after = first.text.lstrip()[len(delim):].strip()
        if after:
            content[0] = replace_text(content[0], after)
        else:
            content = content[1:]

    # Closing delimiter
    if content:
        last2 = content[-1]
        stripped = last2.text.lstrip()
        if stripped.strip() == delim:
            content = content[:-1]
        elif stripped.endswith(delim):
            before = stripped[:-len(delim)].strip()
            content[-1] = replace_text(last2, before)

    return tuple(content)

def _docstring_span(node: DocNode) -> Optional[tuple[int, int]]:
    """
    Return (start_lineno, end_lineno) for node docstring if present.

    NOTE:
    This function is only valid for nodes that *can* own docstrings
    (Module, ClassDef, FunctionDef, AsyncFunctionDef).
    """
    if not node.body:
        return None

    first = node.body[0]
    if not isinstance(first, ast.Expr):
        return None

    value = first.value

    # Python 3.8+
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        assert first.end_lineno is not None
        return first.lineno, first.end_lineno

    # Python <3.8 (legacy)
    if isinstance(value, ast.Str):
        assert first.end_lineno is not None
        return first.lineno, first.end_lineno

    return None

# ------------------------------------------------------------
# Docstring extraction
# ------------------------------------------------------------

def extract_docstring(node: DocNode, lines: Tuple[Line, ...]) -> Entity | None:
    """
    IMPORTANT MODEL INVARIANT:

    - Docstrings are split into HEAD and BODY exactly once, here.
    - HEAD = summary paragraph (until first blank line)
    - BODY = remaining content (Args, Returns, examples, etc.)

    Downstream layers (rendering, folding, views, export)
    MUST treat Entity.head / Entity.body as authoritative and
    MUST NOT re-split or reinterpret docstrings.
    """

    if not ast.get_docstring(node, clean=False):
        return None

    span = _docstring_span(node)
    if not span:
        return None

    start, end = span
    raw = tuple(lines[start - 1 : end])
    content = _strip_doc_delimiters(raw)
    tagged = tuple(l.with_kind("doc") for l in content)

    # Strip leading blank lines
    i = 0
    while i < len(tagged) and tagged[i].text.strip() == "":
        i += 1
    tagged = tagged[i:]

    head: List[Line] = []
    body: List[Line] = []

    split_at: Optional[int] = None
    for j, l in enumerate(tagged):
        if l.text.strip() == "":
            split_at = j
            break

    if split_at is None:
        head = list(tagged)
    else:
        head = [l for l in tagged[:split_at] if l.text.strip()]
        tail = tagged[split_at + 1 :]
        k = 0
        while k < len(tail) and tail[k].text.strip() == "":
            k += 1
        body = list(tail[k:])

    return Entity(
        is_code=False,
        kind="docstring",
        name=None,
        head=tuple(head),
        body=tuple(body),
    )

# ------------------------------------------------------------
# Code entities
# ------------------------------------------------------------

def extract_entity(node: ast.AST, lines: Tuple[Line, ...]) -> Entity | None:
    span: Optional[tuple[int, int]] = None

    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        span = _docstring_span(node)

    def filtered_body(start: int, end: int) -> Tuple[Line, ...]:
        out = []
        for l in lines[start:end]:
            if span and span[0] <= l.number <= span[1]:
                continue
            out.append(l)
        return tuple(out)

    if isinstance(node, ast.ClassDef):
        assert node.end_lineno is not None
        return Entity(
            True,
            "class",
            node.name,
            (lines[node.lineno - 1],),
            filtered_body(node.lineno, node.end_lineno),
        )

    if isinstance(node, ast.FunctionDef):
        assert node.end_lineno is not None
        return Entity(
            True,
            "function",
            node.name,
            (lines[node.lineno - 1],),
            filtered_body(node.lineno, node.end_lineno),
        )

    if isinstance(node, ast.AsyncFunctionDef):
        assert node.end_lineno is not None
        return Entity(
            True,
            "async_function",
            node.name,
            (lines[node.lineno - 1],),
            filtered_body(node.lineno, node.end_lineno),
        )

    return None


# ------------------------------------------------------------
# Scope builder
# ------------------------------------------------------------

def build_scope(node: ast.AST, lines: Tuple[Line, ...]) -> Scope:
    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", None)
        scope_lines = tuple(lines[start - 1 : end]) if end else lines
    else:
        scope_lines = lines

    scope = Scope(lines=scope_lines)

    # Own docstring
    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        doc = extract_docstring(node, lines)
        if doc:
            scope.add_entity(doc)
            mapping = {l.number: l for l in (*doc.head, *doc.body)}
            scope.lines = tuple(mapping.get(l.number, l) for l in scope.lines)

    # Children
    for child in ast.iter_child_nodes(node):
        ent = extract_entity(child, lines)
        if ent:
            scope.add_entity(ent)

        if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            scope.add_child(build_scope(child, lines))

    # Propagate descendant doc tags
    def collect_docs(s: Scope) -> dict[int, Line]:
        out = {}
        for e in s.entities:
            if not e.is_code and e.kind == "docstring":
                for l in (*e.head, *e.body):
                    out[l.number] = l
        for c in s.children:
            out.update(collect_docs(c))
        return out

    docs = collect_docs(scope)
    if docs:
        scope.lines = tuple(docs.get(l.number, l) for l in scope.lines)

    return scope

# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

def analyze_source(source_text: str) -> Scope:
    lines = build_lines(source_text)
    tree = ast.parse(source_text)
    return build_scope(tree, lines)
