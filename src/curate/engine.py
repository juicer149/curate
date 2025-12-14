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

    TOGGLE_LOCAL = "local"      # leader+t
    TOGGLE_CODE = "code"        # leader+T (code)
    TOGGLE_DOCS = "docs"        # leader+T (docs)
    TOGGLE_MINIMUM = "minimum"  # leader+T (minimum)


def payload_for_action(scope, cursor_line: int, action: str) -> dict:
    """
    Convenience API for tests and Lua client: return JSON-like payload
    with `folds` for the given action.
    """
    # Map string to Action
    action_map = {
        "local": Action.TOGGLE_LOCAL,
        "minimum": Action.TOGGLE_MINIMUM,
        "code": Action.TOGGLE_CODE,
        "docs": Action.TOGGLE_DOCS,
    }
    if action not in action_map:
        raise ValueError(f"Unknown action: {action}")

    # Compute ranges
    ranges = ()
    if isinstance(scope, str):
        # If scope provided as text, analyze first
        ranges = fold_for_cursor(scope, cursor_line, action_map[action])
    else:
        # Scope object → reuse query helpers
        # Use same logic as fold_for_cursor but bypass analyze_text
        if action_map[action] == Action.TOGGLE_LOCAL:
            from .query import best_entity_at_line
            entity = best_entity_at_line(scope, cursor_line)
            if entity and entity.body and any(l.number == cursor_line and l.text.strip() for l in entity.body):
                start = entity.body[0].number
                end = entity.body[-1].number
                ranges = ((start, end),)
            else:
                ranges = ()
        else:
            from .foldplan import fold_plan_for_view
            from .views import ViewMode
            view = {
                Action.TOGGLE_MINIMUM: ViewMode.MINIMUM,
                Action.TOGGLE_CODE: ViewMode.CODE_ONLY,
                Action.TOGGLE_DOCS: ViewMode.DOCS_ONLY,
            }[action_map[action]]
            ranges = fold_plan_for_view(scope, view)

    # Format as payload
    return {"folds": [{"start": s, "end": e} for (s, e) in ranges]}


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
