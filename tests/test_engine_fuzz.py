# tests/test_engine_fuzz.py
import pytest

from curate.engine import fold_for_cursor, Action
from tests.utils import seeded_lines_from


def test_toggle_local_seeded_fuzz(example_model):
    """
    Deterministic fuzz test for TOGGLE_LOCAL.

    Guarantees:
    - no crashes
    - no invalid fold ranges
    """
    source = example_model["source_text"]

    cursor_lines = seeded_lines_from(
        example_model["non_empty_lines"],
        seed=7,
        count=25,
    )

    for cursor_line in cursor_lines:
        folds = fold_for_cursor(
            source,
            cursor_line=cursor_line,
            action=Action.TOGGLE_LOCAL,
        )

        for start, end in folds:
            assert 1 <= start <= end <= example_model["total_lines"]


@pytest.mark.parametrize(
    "cursor_line",
    range(1, 200),  # wide sweep, safe upper bound
)
def test_toggle_local_never_crashes(example_model, cursor_line):
    """
    Broad safety fuzz: engine must never crash
    regardless of cursor position.
    """
    source = example_model["source_text"]

    fold_for_cursor(
        source,
        cursor_line=cursor_line,
        action=Action.TOGGLE_LOCAL,
    )
