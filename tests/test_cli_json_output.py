import json
import subprocess
import sys


def test_cli_json_output():
    """
    CLI contract:
    - --output json must emit valid JSON
    - JSON must be an object with key "folds"
    - "folds" must be a list of [start, end] integer ranges
    """

    source = """
def f():
    \"\"\"Docstring\"\"\"
    x = 1
    y = 2
    return x + y
"""

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
    payload = json.loads(proc.stdout)

    assert isinstance(payload, dict)
    assert "folds" in payload

    folds = payload["folds"]
    assert isinstance(folds, list)

    for item in folds:
        assert isinstance(item, list)
        assert len(item) == 2

        start, end = item
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start < end
