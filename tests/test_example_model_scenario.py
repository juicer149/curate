# tests/test_example_model_scenario.py

from pathlib import Path
from curate import fold


def test_example_model_high_level_behavior():
    """
    Scenario test using a realistic Python file.

    This test intentionally does NOT assert exact line numbers everywhere.
    It asserts structural expectations only.
    """
    source = Path(__file__).parent / "example_model.py"
    text = source.read_text(encoding="utf-8")

    ranges = fold(
        source=text,
        cursor=1,
        level=0,
        mode="children",
        language="python",
    )

    # Expect folding of top-level definitions:
    # - two classes
    # - one top-level function
    assert len(ranges) >= 3


def test_example_model_class_behavior():
    source = Path(__file__).parent / "example_model.py"
    text = source.read_text(encoding="utf-8")

    ranges = fold(
        source=text,
        cursor=20,   # inside first class
        level=0,
        mode="children",
        language="python",
    )

    # Expect class children (docstring + methods)
    assert len(ranges) >= 2


def test_example_model_method_self_fold():
    source = Path(__file__).parent / "example_model.py"
    text = source.read_text(encoding="utf-8")

    ranges = fold(
        source=text,
        cursor=29,   # inside __init__
        level=0,
        mode="self",
        language="python",
    )

    # Folding a method should fold *something*
    assert ranges
