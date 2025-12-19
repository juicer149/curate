"""
Python AST backend.

Place in pipeline:
- engine.fold(cfg) dispatches here via backend_factory.get_backend()
- this backend:
    1) parses Python source with `ast`
    2) builds a Node tree of structural spans (classes, functions, docstrings)
    3) selects a target node from (cursor, level)
    4) returns fold ranges based on fold_children (f vs F)

v1 folding semantics:
- Docstrings are first-class structural nodes.
- No code-vs-docs policy exists in v1: everything folds uniformly.
- Headers:
    - class/function/module nodes keep 1 header line visible
    - doc nodes keep 2 header lines visible (if available)
- A node with span length <= header length has no foldable body.

Navigation note (v1):
- Doc nodes are foldable, but NOT navigable scopes.
  Cursor inside a docstring still targets the enclosing module/class/function.
"""

import ast
from typing import Iterable, Optional

from curate.node import Node
from curate.types import Range


class PythonASTBackend:
    # ------------------------------------------------------------------
    # AST → Node tree
    # ------------------------------------------------------------------

    def _doc_node(self, py, parent: Node) -> Optional[Node]:
        """
        Return a doc Node for `py` if it has a docstring.

        ast represents a docstring as the first statement:
        Expr(Constant(str)).
        lineno/end_lineno span includes the triple-quote lines.
        """
        body = getattr(py, "body", None)
        if not body:
            return None

        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
            and first.end_lineno is not None
        ):
            return Node(
                kind="doc",
                start=first.lineno,
                end=first.end_lineno,
                parent=parent,
            )
        return None

    def _make_node(self, py, parent: Node) -> Optional[Node]:
        if isinstance(py, ast.ClassDef):
            assert py.end_lineno is not None
            return Node("class", py.lineno, py.end_lineno, parent)
        if isinstance(py, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assert py.end_lineno is not None
            return Node("function", py.lineno, py.end_lineno, parent)
        return None

    def _build(self, py, parent: Node) -> None:
        # Attach docstring node (if present) as the first structural child.
        doc = self._doc_node(py, parent)
        if doc:
            parent.children.append(doc)

        # Attach class/function children and recurse.
        for child in getattr(py, "body", []) or []:
            node = self._make_node(child, parent)
            if node:
                parent.children.append(node)
                self._build(child, node)

    def _tree(self, source: str) -> Node:
        tree = ast.parse(source)
        end = max(1, len(source.splitlines()))
        root = Node("module", 1, end)
        self._build(tree, root)
        return root

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _node_at(self, root: Node, line: int) -> Node:
        """
        Select the smallest *navigable* structural scope containing `line`.

        Doc nodes are foldable but NOT navigable scopes in v1.
        If the cursor is inside a docstring, we still want to target the
        enclosing module/class/function.
        """
        best: Optional[Node] = None

        def walk(n: Node) -> None:
            nonlocal best
            if not n.contains(line):
                return

            # Only module/class/function are navigable
            if n.kind != "doc":
                if best is None or n.width < best.width:
                    best = n

            for c in n:
                walk(c)

        walk(root)
        return best or root

    def _ancestor(self, node: Node, level: int) -> Node:
        cur = node
        for _ in range(level):
            if cur.parent is None:
                break
            cur = cur.parent
        return cur

    # ------------------------------------------------------------------
    # Folding primitives
    # ------------------------------------------------------------------

    def _doc_body(self, doc: Node) -> Optional[Range]:
        """
        Doc header is always 2 lines (if available):
        - opening triple quotes line
        - summary line (PEP-style)

        Body is everything after those two lines, through the end of the doc node.
        We do not special-case blank lines.

        If the doc node is only 1 line long, it has no body.
        If it's 2 lines long, it also has no body (header consumes it).
        """
        # span length in lines
        span = doc.end - doc.start + 1
        if span <= 2:
            return None
        return (doc.start + 2, doc.end)

    def _node_body(self, n: Node) -> Optional[Range]:
        """
        Non-doc nodes keep 1 header line visible.
        Body is the remainder of the node span.
        """
        if n.kind == "doc":
            return self._doc_body(n)

        span = n.end - n.start + 1
        if span <= 1:
            return None
        return (n.start + 1, n.end)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fold(
        self,
        *,
        content: str,
        cursor: int,
        level: int,
        fold_children: bool,
    ) -> Iterable[Range]:
        root = self._tree(content)
        current = self._node_at(root, cursor)
        target = self._ancestor(current, level)

        # Fold target's own body
        if not fold_children:
            r = self._node_body(target)
            return [r] if r else []

        # Fold bodies of target's children (includes doc child if present)
        ranges: list[Range] = []
        for child in target.children:
            r = self._node_body(child)
            if r:
                ranges.append(r)

        return ranges
