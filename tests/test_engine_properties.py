# tests/test_engine_properties.py

from pathlib import Path
import pytest

from curate import fold


@pytest.fixture
def source_text() -> str:
    path = Path(__file__).parent / "example_model.py"
    return path.read_text(encoding="utf-8")


def test_engine_never_returns_invalid_ranges(source_text):
    """
    Core invariant:

    - fold() must never crash
    - all returned ranges must be structurally valid
    - ranges must stay within file bounds
    - this must hold for *all* cursors / levels / modes

    This test asserts *safety*, not semantics.
    """
    total_lines = len(source_text.splitlines())

    for cursor in range(1, total_lines + 1):
        for level in range(0, 5):
            for mode in ("self", "children"):
                ranges = fold(
                    source=source_text,
                    cursor=cursor,
                    level=level,
                    mode=mode,
                )

                for start, end in ranges:
                    assert isinstance(start, int)
                    assert isinstance(end, int)
                    assert 1 <= start < end <= total_lines
