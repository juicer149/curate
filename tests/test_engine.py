from pathlib import Path

import pytest

from curate.engine import fold_for_cursor, Action


@pytest.fixture()
def source_text():
    here = Path(__file__).parent
    p = here / "example_model.py"
    return p.read_text(encoding="utf-8")


# ------------------------------------------------------------
# leader + t  (TOGGLE_LOCAL)
# ------------------------------------------------------------

def test_toggle_local_on_function_body(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=29,  # inside __init__ body
        action=Action.TOGGLE_LOCAL,
    )

    assert folds
    start, end = folds[0]
    assert start <= 29 <= end


def test_toggle_local_on_function_docstring(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=26,  # inside docstring body
        action=Action.TOGGLE_LOCAL,
    )

    assert folds
    start, end = folds[0]
    assert start <= 26 <= end


def test_toggle_local_on_entity_head_does_nothing(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=12,  # class Example:
        action=Action.TOGGLE_LOCAL,
    )
    assert folds == ()


def test_toggle_local_on_blank_line_does_nothing(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=31,  # blank line between methods
        action=Action.TOGGLE_LOCAL,
    )
    assert folds == ()


# ------------------------------------------------------------
# leader + T  (scope-based toggles)
# ------------------------------------------------------------

def test_toggle_code_inside_method(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=29,
        action=Action.TOGGLE_CODE,
    )

    folded = {l for a, b in folds for l in range(a, b + 1)}

    # docs folded
    assert 26 in folded
    # code visible
    assert 29 not in folded


def test_toggle_docs_inside_method(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=29,
        action=Action.TOGGLE_DOCS,
    )

    folded = {l for a, b in folds for l in range(a, b + 1)}

    # code folded
    assert 29 in folded
    # docs visible
    assert 26 not in folded


def test_toggle_minimum_inside_class(source_text):
    folds = fold_for_cursor(
        source_text,
        cursor_line=14,  # inside class docstring
        action=Action.TOGGLE_MINIMUM,
    )

    folded = {l for a, b in folds for l in range(a, b + 1)}

    # method bodies folded
    assert 29 in folded
    assert 39 in folded

    # other class untouched
    assert 51 not in folded


# ------------------------------------------------------------
# safety / invariants
# ------------------------------------------------------------

def test_engine_never_returns_invalid_ranges(source_text):
    for line in range(1, 90):
        for action in Action:
            folds = fold_for_cursor(source_text, line, action)
            for start, end in folds:
                assert start <= end
                assert start >= 1
