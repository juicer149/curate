from __future__ import annotations

"""
Tree-sitter producer orchestration.

This module coordinates:
- language selection
- parser setup
- traversal + interpretation
- safe fallback behavior
"""

from ...model import Scope, ScopeGraph
from ...types import Role
from .node import body_start_line, node_span_lines
from .traverse import TraversalState, add_scope
from .interpret import policy_for, select_wrapper_target
from .registry import LANGUAGE_LOADERS, LANGUAGE_RULES


def _empty_graph(source: str, role: Role) -> ScopeGraph:
    total_lines = source.count("\n") + 1 if source else 1
    return ScopeGraph((
        Scope(
            id=0,
            parent_id=None,
            kind="module",
            start=1,
            end=total_lines,
            role=role,
            header_lines=1,
        ),
    ))


def build_graph(language: str, source: str, role: Role = "code") -> ScopeGraph:
    lang = (language or "default").lower()
    rules = LANGUAGE_RULES.get(lang, LANGUAGE_RULES["default"])
    loader = LANGUAGE_LOADERS.get(lang)

    if loader is None:
        return _empty_graph(source, role)

    try:
        from tree_sitter import Parser
        parser = Parser(loader())
    except Exception:
        return _empty_graph(source, role)

    tree = parser.parse(source.encode("utf-8", errors="replace"))
    total_lines = source.count("\n") + 1 if source else 1

    st = TraversalState(
        next_id=1,
        scopes=[
            Scope(
                id=0,
                parent_id=None,
                kind="module",
                start=1,
                end=max(1, total_lines),
                role=role,
                header_lines=1,
            )
        ],
    )

    def walk(node, parent_id: int, forced_start: Optional[int] = None) -> None:
        pol = policy_for(node, rules)

        if pol.noop or (not pol.is_scope and not pol.include_in_child_start):
            for ch in node.children:
                walk(ch, parent_id)
            return

        if pol.include_in_child_start:
            target = select_wrapper_target(node, rules)
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

        if pol.is_scope:
            s, e = node_span_lines(node)
            if forced_start is not None and forced_start < s:
                s = forced_start

            bstart = body_start_line(node)
            header_lines = (bstart - s) if bstart and bstart > s else 1

            sid = add_scope(
                st,
                parent_id=parent_id,
                kind=pol.kind or node.type,
                start=s,
                end=e,
                role=role,
                header_lines=header_lines,
            )

            body = node.child_by_field_name("body")
            children = body.children if body is not None else node.children
            for ch in children:
                walk(ch, sid)

    for ch in tree.root_node.children:
        walk(ch, parent_id=0)

    scopes = sorted(st.scopes, key=lambda sc: (sc.start, -sc.end, sc.id))
    return ScopeGraph(tuple(scopes))
