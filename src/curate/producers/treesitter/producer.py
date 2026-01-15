"""
Tree-sitter producer backend.

This module is responsible for turning source text into a ScopeGraph
using the Tree-sitter parsing library.

Responsibilities:
- load the correct Tree-sitter grammar via the registry
- parse source text into a syntax tree
- walk the syntax tree and emit structural scopes
- guarantee a valid ScopeGraph for any input

Non-responsibilities:
- selecting which producer backend to use
- interpreting scopes semantically
- handling editor or AI concerns

This module implements the implicit Producer contract:

    (language: str, source: str) -> ScopeGraph
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ...model import Scope, ScopeGraph
from .node import body_start_line, node_span_lines
from .registry import LANGUAGES
from .rules import LanguageRules, NodePolicy


# ---------------------------------------------------------------------------
# Internal construction state
# ---------------------------------------------------------------------------

@dataclass
class _State:
    """
    Mutable construction state used while walking the syntax tree.

    next_id:
        Monotonically increasing scope identifier.

    scopes:
        Accumulated list of scopes emitted so far.
    """
    next_id: int
    scopes: list[Scope]


# ---------------------------------------------------------------------------
# Fallback
# ---------------------------------------------------------------------------

def _empty_graph(source: str) -> ScopeGraph:
    """
    Produce a minimal ScopeGraph containing only a module-level scope.

    This is used when:
    - no grammar loader is available
    - Tree-sitter fails to initialize
    - parsing fails for any reason
    """
    total_lines = len(source.splitlines()) if source else 1
    module = Scope(
        id=0,
        parent_id=None,
        kind="module",
        start=1,
        end=max(1, total_lines),
        header_lines=1,
    )
    return ScopeGraph((module,))


# ---------------------------------------------------------------------------
# Policy helpers
# ---------------------------------------------------------------------------

def _policy_for(node, rules: LanguageRules) -> NodePolicy:
    """
    Resolve the NodePolicy for a syntax node.
    """
    return rules.node_policies.get(node.type, rules.default_policy)


def _select_wrapper_target(node, rules: LanguageRules):
    """
    If this node is a wrapper, select the child node that should receive
    the wrapper's start position.
    """
    for rule in rules.wrapper_rules:
        if node.type != rule.wrapper_type:
            continue
        for ch in getattr(node, "children", []):
            if getattr(ch, "type", None) in rule.target_types:
                return ch
    return None


def _add_scope(
    st: _State,
    *,
    parent_id: Optional[int],
    kind: str,
    start: int,
    end: int,
    header_lines: int,
) -> int:
    """
    Allocate and append a new Scope to the construction state.
    """
    sid = st.next_id
    st.next_id += 1
    st.scopes.append(
        Scope(
            id=sid,
            parent_id=parent_id,
            kind=kind,
            start=start,
            end=end,
            header_lines=max(1, int(header_lines)),
        )
    )
    return sid


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_graph(*, language: str, source: str) -> ScopeGraph:
    """
    Build a ScopeGraph from source text using the Tree-sitter backend.

    Parameters:
        language:
            Language identifier (e.g. "python").
            If unknown, falls back to the default language rules.

        source:
            Source code as a single string.

    Returns:
        A ScopeGraph representing the structural scopes of the source.
    """
    lang = (language or "default").lower()
    spec = LANGUAGES.get(lang, LANGUAGES["default"])
    rules: LanguageRules = spec.rules

    if spec.loader is None:
        return _empty_graph(source)

    try:
        from tree_sitter import Parser
        parser = Parser(spec.loader())
    except Exception:
        return _empty_graph(source)

    tree = parser.parse(source.encode("utf-8", errors="replace"))
    root = tree.root_node

    total_lines = len(source.splitlines()) if source else 1
    st = _State(
        next_id=1,
        scopes=[
            Scope(
                id=0,
                parent_id=None,
                kind="module",
                start=1,
                end=max(1, total_lines),
                header_lines=1,
            )
        ],
    )

    def walk(node, parent_id: int, forced_start: Optional[int] = None) -> None:
        """
        Recursive descent over the syntax tree, emitting scopes as dictated
        by the active LanguageRules.
        """
        pol = _policy_for(node, rules)

        # Transparent recursion
        if pol.noop or (not pol.is_scope and not pol.include_in_child_start):
            for ch in node.children:
                walk(ch, parent_id)
            return

        # Wrapper node: forward start line into selected child
        if pol.include_in_child_start:
            target = _select_wrapper_target(node, rules)
            if target is not None:
                fs = node.start_point[0] + 1
                walk(target, parent_id, forced_start=fs)
                for ch in node.children:
                    if ch is not target:
                        walk(ch, parent_id)
            else:
                for ch in node.children:
                    walk(ch, parent_id)
            return

        # Scope node
        start, end = node_span_lines(node)
        if forced_start is not None and forced_start < start:
            start = forced_start

        body_start = body_start_line(node)
        header_lines = (
            body_start - start
            if body_start is not None and body_start > start
            else 1
        )

        sid = _add_scope(
            st,
            parent_id=parent_id,
            kind=pol.kind or node.type,
            start=start,
            end=end,
            header_lines=header_lines,
        )

        body = node.child_by_field_name("body")
        children = body.children if body is not None else node.children
        for ch in children:
            walk(ch, sid)

    for ch in root.children:
        walk(ch, parent_id=0)

    scopes = sorted(st.scopes, key=lambda s: (s.start, -s.end, s.id))
    return ScopeGraph(tuple(scopes))
