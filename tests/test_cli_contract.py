import json
import subprocess
import sys
from pathlib import Path

SRC = Path("tests/fixtures/python_minimal.py").read_text()


def test_cli_json_output():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "curate",
            "--line",
            "6",
            "--output",
            "json",
        ],
        input=SRC,
        text=True,
        capture_output=True,
    )

    assert proc.returncode == 0

    payload = json.loads(proc.stdout)
    assert isinstance(payload, dict)
    assert "folds" in payload

    for a, b in payload["folds"]:
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert a < b
