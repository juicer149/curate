# tests/test_toggle_semantics_python.py
from __future__ import annotations

import pathlib

import pytest

from curate.engine import fold


# ---------------------------------------------------------------------
# Test source (shared, large, realistic)
# ---------------------------------------------------------------------

EXAMPLE_PATH = pathlib.Path(
    "tests/example_code_doc_for_manual_testing.py"
)


@pytest.fixture(scope="session")
def source_text() -> str:
    return EXAMPLE_PATH.read_text()


# ---------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------

def _fold_self(source: str, *, cursor: int, level: int = 0):
    return fold(
        source=source,
        cursor=cursor,
        level=level,
        mode="self",
        language="python",
    )


def _fold_children(source: str, *, cursor: int, level: int = 0):
    return fold(
        source=source,
        cursor=cursor,
        level=level,
        mode="children",
        language="python",
    )


# ---------------------------------------------------------------------
# Core toggle semantics
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "cursor",
    [
        25,   # simple_function
        32,   # documented_function
        56,   # nested_blocks
        98,   # class User
        129,  # class Manager
        155,  # class Outer
        184,  # complex_flow
    ],
)
def test_self_fold_is_deterministic(source_text: str, cursor: int):
    """
    Calling self-fold multiple times must always return
    the same range(s).
    """
    r1 = _fold_self(source_text, cursor=cursor)
    r2 = _fold_self(source_text, cursor=cursor)

    assert r1 == r2


def test_function_self_fold_single_range(source_text: str):
    # documented_function
    ranges = _fold_self(source_text, cursor=32)

    assert len(ranges) == 1
    start, end = ranges[0]

    # body starts after signature + docstring
    assert start > 32
    assert start < end


def test_function_children_fold_multiple_blocks(source_text: str):
    # documented_function contains if/else
    ranges = _fold_children(source_text, cursor=32)

    assert len(ranges) >= 1

    for start, end in ranges:
        assert start < end


# ---------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------

def test_class_self_fold_covers_entire_body(source_text: str):
    # class User
    ranges = _fold_self(source_text, cursor=98)

    assert len(ranges) == 1

    start, end = ranges[0]

    # first field
    assert start <= 107

    # last executable line in class (greet())
    assert end >= 121


def test_class_children_fold_methods_only(source_text: str):
    # class User
    ranges = _fold_children(source_text, cursor=98)

    # is_adult + greet
    assert len(ranges) == 2

    for start, end in ranges:
        assert start < end


# ---------------------------------------------------------------------
# Nested classes
# ---------------------------------------------------------------------

def test_nested_class_self_fold_inner(source_text: str):
    # class Inner
    ranges = _fold_self(source_text, cursor=165)

    assert len(ranges) == 1
    start, end = ranges[0]

    assert start < end


def test_nested_class_parent_level(source_text: str):
    """
    Cursor inside Inner, but level=1 means:
    fold the *parent* (Outer) body, not header.
    """
    ranges = fold(
        source=source_text,
        cursor=165,
        level=1,
        mode="self",
        language="python",
    )

    assert len(ranges) == 1
    start, end = ranges[0]

    # body of Outer starts after header
    assert start >= 161
    assert start < end


# ---------------------------------------------------------------------
# Stress / fuzz-ish stability
# ---------------------------------------------------------------------

@pytest.mark.parametrize("cursor", range(1, 236, 7))
def test_many_cursor_positions_are_stable(
    source_text: str,
    cursor: int,
):
    """
    Folding must never crash and must always
    return valid ranges.
    """
    ranges = _fold_self(source_text, cursor=cursor)

    for start, end in ranges:
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start < end
