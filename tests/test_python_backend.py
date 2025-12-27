# tests/test_python_backend.py

import pathlib
import pytest

from curate import fold


@pytest.fixture
def source_text() -> str:
    path = pathlib.Path(__file__).parent / "example_model.py"
    return path.read_text(encoding="utf-8")


def test_class_example_fold_children(source_text):
    # children/local: fold all immediate children to their headers
    # - class docstring body (if any)
    # - method bodies (def-line header stays visible)
    assert fold(
        source=source_text,
        cursor=19,   # class Example:
        level=0,
        mode="children",
    ) == (
        (23, 26),  # class docstring body (header=3)
        (29, 37),  # __init__ body (header=1)
        (40, 46),  # display body (header=1)
    )


def test_class_example_fold_self(source_text):
    # self/maximal: fold the whole class body to the class header
    assert fold(
        source=source_text,
        cursor=19,
        level=0,
        mode="self",
    ) == (
        (20, 46),
    )


def test_method_fold_children(source_text):
    # children/local on a method: fold its children (the docstring body)
    assert fold(
        source=source_text,
        cursor=28,   # def __init__:
        level=0,
        mode="children",
    ) == (
        (32, 35),  # __init__ docstring body (header=3)
    )


def test_method_parent_fold_children(source_text):
    # inside __init__, level=1 => class Example
    assert fold(
        source=source_text,
        cursor=28,
        level=1,
        mode="children",
    ) == (
        (23, 26),
        (29, 37),
        (40, 46),
    )


def test_method_parent_fold_self(source_text):
    # inside __init__, level=1 => class Example, fold whole class
    assert fold(
        source=source_text,
        cursor=28,
        level=1,
        mode="self",
    ) == (
        (20, 46),
    )


def test_second_class_fold_children(source_text):
    assert fold(
        source=source_text,
        cursor=49,   # class ExampleForTwoClassesInFile:
        level=0,
        mode="children",
    ) == (
        (53, 56),  # class docstring body (header=3)
        (59, 67),  # __init__ body
        (70, 76),  # summarize body
    )


def test_top_level_function_fold_self(source_text):
    assert fold(
        source=source_text,
        cursor=79,   # def example_function:
        level=0,
        mode="self",
    ) == (
        (80, 86),
    )


def test_module_fold_children(source_text):
    # inside function, level=1 => module, children/local folds module children bodies
    assert fold(
        source=source_text,
        cursor=79,
        level=1,
        mode="children",
    ) == (
        (5, 13),    # module docstring body (header=3)
        (20, 46),   # class Example body
        (50, 76),   # second class body
        (80, 86),   # function body
    )


def test_one_line_docstring_has_no_body():
    src = '''
def f():
    """One line."""
    pass
'''
    assert fold(
        source=src,
        cursor=2,
        level=0,
        mode="children",
    ) == ()
