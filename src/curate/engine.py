from enum import Enum
from typing import Tuple

from .api import analyze_text
from .query import scope_at_line, best_entity_at_line
from .foldplan import fold_plan_for_view
from .views import ViewMode

Range = Tuple[int, int]


class Action(Enum):
    """
    Editor-facing semantic actions.

    These map 1:1 to user intent (e.g. keybindings in Neovim),
    not to structural operations.
    """

    TOGGLE_LOCAL = "toggle_local"      # leader+t
    TOGGLE_CODE = "toggle_code"        # leader+T (code)
    TOGGLE_DOCS = "toggle_docs"        # leader+T (docs)
    TOGGLE_MINIMUM = "toggle_minimum"  # leader+T (minimum)


def fold_for_cursor(
    source_text: str,
    cursor_line: int,
    action: Action,
) -> Tuple[Range, ...]:
    """
    Stateless semantic folding engine.

    INPUT:
      - source_text: full buffer contents
      - cursor_line: 1-based cursor line
      - action: semantic intent (Action)

    OUTPUT:
      - tuple of fold ranges (start, end), inclusive
    """
    root = analyze_text(source_text)

    # -------------------------------------------------
    # Local toggle (leader+t)
    #
    # Rules:
    # - Cursor must be inside an entity body
    # - Cursor must be on a non-blank line
    # - Heads, blank lines, separators do nothing
    # -------------------------------------------------
    if action == Action.TOGGLE_LOCAL:
        entity = best_entity_at_line(root, cursor_line)
        if not entity or not entity.body:
            return ()

        # Find the actual body line under the cursor
        line = next(
            (l for l in entity.body if l.number == cursor_line),
            None,
        )
        if not line:
            return ()

        # Blank lines are not valid local toggle targets
        if not line.text.strip():
            return ()

        start = entity.body[0].number
        end = entity.body[-1].number
        return ((start, end),)

    # -------------------------------------------------
    # Scope-based toggles (leader+T)
    #
    # These operate on the current scope and are
    # intentionally coarse-grained.
    # -------------------------------------------------
    scope = scope_at_line(root, cursor_line)

    if action == Action.TOGGLE_CODE:
        # Fold everything that is NOT code
        return fold_plan_for_view(scope, ViewMode.CODE_ONLY)

    if action == Action.TOGGLE_DOCS:
        # Fold everything that is NOT documentation
        return fold_plan_for_view(scope, ViewMode.DOCS_ONLY)

    if action == Action.TOGGLE_MINIMUM:
        # Fold all bodies, keep only heads
        return fold_plan_for_view(scope, ViewMode.MINIMUM)

    raise ValueError(action)
