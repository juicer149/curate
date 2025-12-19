# tests/test_python_backend.py
'''
Tests for the Python AST backend.

These tests reflect **Curate v1 semantics**:

- Docstrings are first-class structural nodes.
- Doc folding rules:
    - header = 2 lines (""" + summary)
    - body = remaining lines
    - doc length <= 1 → no fold
- All nodes (module, class, function, doc) are folded uniformly.
- `level` selects which scope is targeted.
- `fold_children` controls whether the node itself or its children are folded.
'''

import pathlib
import pytest

from curate import Config, fold


@pytest.fixture
def source_text() -> str:
    path = pathlib.Path(__file__).parent / "example_model.py"
    return path.read_text(encoding="utf-8")


def test_class_example_fold_children(source_text):
    """
    Cursor on class Example.
    fold_children=True → fold bodies of all children.

    Children:
    - class docstring
    - __init__
    - display
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=12,          # class Example:
        level=0,
        fold_children=True,
    )

    assert fold(cfg) == (
        (15, 19),  # class docstring body
        (22, 30),  # __init__ body (docstring body)
        (33, 39),  # display body (docstring body)
    )


def test_class_example_fold_scope(source_text):
    """
    Cursor on class Example.
    fold_children=False → fold entire class body (doc + code).
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=12,
        level=0,
        fold_children=False,
    )

    assert fold(cfg) == (
        (13, 39),
    )


def test_method_fold_children_no_children(source_text):
    """
    Cursor inside __init__.
    fold_children=True.

    __init__ has a docstring child, so that docstring body is folded.
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=25,          # inside __init__
        level=0,
        fold_children=True,
    )

    assert fold(cfg) == (
        (24, 28),  # __init__ docstring body
    )


def test_method_parent_fold_children(source_text):
    """
    Cursor inside __init__.
    level=1 → class Example.
    fold_children=True → fold all class children bodies.
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=25,
        level=1,
        fold_children=True,
    )

    assert fold(cfg) == (
        (15, 19),  # class docstring body
        (22, 30),  # __init__ docstring body
        (33, 39),  # display docstring body
    )


def test_method_parent_fold_scope(source_text):
    """
    Cursor inside __init__.
    level=1 → class Example.
    fold_children=False → fold entire class body.
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=25,
        level=1,
        fold_children=False,
    )

    assert fold(cfg) == (
        (13, 39),
    )


def test_second_class_fold_children(source_text):
    """
    Cursor on second class.
    fold_children=True → fold all child bodies.
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=42,          # class ExampleForTwoClassesInFile
        level=0,
        fold_children=True,
    )

    assert fold(cfg) == (
        (45, 49),  # class docstring body
        (52, 60),  # __init__ docstring body
        (63, 69),  # summarize docstring body
    )


def test_top_level_function_fold_scope(source_text):
    """
    Cursor on top-level function.
    fold_children=False → fold entire function body (doc + code).
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=72,          # example_function
        level=0,
        fold_children=False,
    )

    assert fold(cfg) == (
        (73, 79),
    )


def test_top_level_function_parent_scope(source_text):
    """
    Cursor inside top-level function.
    level=1 → module.
    fold_children=True → fold bodies of all module children.
    """
    cfg = Config(
        file_type="python",
        content=source_text,
        cursor=72,
        level=1,
        fold_children=True,
    )

    assert fold(cfg) == (
        (4, 6),     # module docstring body
        (13, 39),   # class Example body
        (43, 69),   # second class body
        (73, 79),   # function body
    )

def test_unknown_filetype_returns_empty():
    cfg = Config(
        file_type="nope",
        content="",
        cursor=1,
        level=0,
        fold_children=False,
    )
    assert fold(cfg) == ()


def test_one_line_docstring_has_no_body():
    src = '''
def f():
    """One line."""
    pass
'''
    cfg = Config(
        file_type="python",
        content=src,
        cursor=2,
        level=0,
        fold_children=True,
    )
    assert fold(cfg) == ()
