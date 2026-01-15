from pathlib import Path
from curate import fold

SRC = Path(__file__).parent / "fixtures/python_minimal.py"
TEXT = SRC.read_text(encoding="utf-8")


def test_self_top_body_range():
    ranges = fold(
        source=TEXT,
        cursor=7,   # inside top()
        mode="self",
        language="python",
    )
    assert ranges == ((8, 19),)


def test_children_of_top_fold_inner_and_if():
    ranges = fold(
        source=TEXT,
        cursor=7,
        mode="children",
        language="python",
    )
    assert set(ranges) == {(12, 13), (16, 17)}


def test_class_method_self():
    ranges = fold(
        source=TEXT,
        cursor=23,
        mode="self",
        language="python",
    )
    assert ranges == ((24, 24),) or ranges == ()
