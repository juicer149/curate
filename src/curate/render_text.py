from typing import Tuple

from .scope import Scope
from .entity import Entity
from .line import Line


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _indent(n: int) -> str:
    return "  " * n


# ------------------------------------------------------------
# Rendering
# ------------------------------------------------------------

def render_entity(e: Entity, depth: int) -> str:
    """
    Render a single Entity in a human-readable, debug-friendly form.

    IMPORTANT INVARIANT:
    - Entity.head / Entity.body are already semantically correct.
    - Rendering MUST NOT re-interpret or re-split content.
    """
    kind = "CODE" if e.is_code else "DOC"
    label = f"{kind} [{e.kind}]"
    if e.name:
        label += f" {e.name}"

    out = [f"{_indent(depth)}{label}"]

    head = e.head
    body = e.body

    # ----------------------------
    # Render HEAD
    # ----------------------------

    out.append(f"{_indent(depth + 1)}HEAD")
    if head:
        for l in head:
            out.append(f"{_indent(depth + 2)}{l.number} | {l.text}")
    else:
        out.append(f"{_indent(depth + 2)}(empty)")

    # ----------------------------
    # Render BODY
    # ----------------------------

    out.append(f"{_indent(depth + 1)}BODY")
    if body:
        for l in body:
            out.append(f"{_indent(depth + 2)}{l.number} | {l.text}")
    else:
        out.append(f"{_indent(depth + 2)}(empty)")

    return "\n".join(out)


def render_scope(scope: Scope, depth: int = 0) -> str:
    out = [f"{_indent(depth)}Scope"]

    if scope.entities:
        out.append(f"{_indent(depth + 1)}Entities")
        for e in scope.entities:
            out.append(render_entity(e, depth + 2))

    if scope.children:
        out.append(f"{_indent(depth + 1)}Children")
        for c in scope.children:
            out.append(render_scope(c, depth + 2))

    return "\n\n".join(out)
