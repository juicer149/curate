import json
import subprocess
import sys
from pathlib import Path


def test_cli_json_output():
    """
    CLI contract:
    - --output json must emit valid JSON
    - JSON must be a list of [start, end] ranges
    """

    source = """
def f():
    \"\"\"Docstring\"\"\"
    x = 1
    y = 2
    return x + y
"""

    # Run: python -m curate --line 1 --output json
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "curate",
            "--line",
            "1",
            "--output",
            "json",
        ],
        input=source,
        text=True,
        capture_output=True,
    )

    assert proc.returncode == 0, proc.stderr

    # Must be valid JSON
    data = json.loads(proc.stdout)

    assert isinstance(data, list)

    for item in data:
        assert isinstance(item, list)
        assert len(item) == 2

        start, end = item
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start < end
