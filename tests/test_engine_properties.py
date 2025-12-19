# tests/test_engine_properties.py

from pathlib import Path

import pytest

from curate import Config, fold


@pytest.fixture
def source_text() -> str:
    path = Path(__file__).parent / "example_model.py"
    return path.read_text(encoding="utf-8")


def test_engine_never_returns_invalid_ranges(source_text):
    """
    Core invariant for Curate v1:

    - fold() must never crash
    - all returned ranges must be valid
    - ranges must stay within file bounds
    """

    total_lines = len(source_text.splitlines())

    for cursor in range(1, total_lines + 1):
        for level in range(0, 4):  # small, safe bound
            for fold_children in (True, False):
                cfg = Config(
                    file_type="python",
                    content=source_text,
                    cursor=cursor,
                    level=level,
                    fold_children=fold_children,
                )

                ranges = fold(cfg)

                for start, end in ranges:
                    assert isinstance(start, int)
                    assert isinstance(end, int)

                    assert start <= end
                    assert start >= 1
                    assert end <= total_lines
