"""
Python AST structure producer.

Prolog analogy
--------------
This module asserts facts into the system.

It translates Python syntax into scopes and parent relations
without embedding any folding semantics.

Design principle
----------------
"Parse once. Emit facts. Forget semantics."
"""

from __future__ import annotations
import ast

from ..model import Scope, ScopeGraph


def build_graph(source: str) -> ScopeGraph:
    """
    Build a ScopeGraph from Python source code.

    If parsing fails, the producer refuses responsibility
    and emits an empty graph.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ScopeGraph(())

    total_lines = max(1, len(source.splitlines()))
    scopes: list[Scope] = []
    next_id = 0

    def nid() -> int:
        nonlocal next_id
        next_id += 1
        return next_id

    # Module scope
    module_id = nid()
    scopes.append(Scope(module_id, None, 1, total_lines, "code"))

    def walk(parent_id: int, node: ast.AST) -> None:
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            return

        # Docstring scope (belongs to this node)
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            ds = body[0]
            if ds.lineno and ds.end_lineno:
                scopes.append(
                    Scope(nid(), parent_id, ds.lineno, ds.end_lineno, "doc")
                )

        # Structural scopes
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if stmt.lineno and stmt.end_lineno:
                    sid = nid()
                    scopes.append(
                        Scope(
                            sid,
                            parent_id,
                            stmt.lineno,
                            stmt.end_lineno,
                            "code",
                        )
                    )
                    walk(sid, stmt)

    walk(module_id, tree)
    return ScopeGraph(tuple(scopes))
