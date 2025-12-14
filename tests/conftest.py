# tests/conftest.py
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def example_model():
    """
    Parsed metadata for tests/example_model.py
    """
    root = Path(__file__).parent
    path = root / "example_model.py"

    source_text = path.read_text(encoding="utf-8")
    lines = source_text.splitlines()

    non_empty_lines = {
        i + 1
        for i, line in enumerate(lines)
        if line.strip()
    }

    return {
        "path": path,
        "source_text": source_text,
        "lines": lines,
        "non_empty_lines": non_empty_lines,
        "total_lines": len(lines),
    }
