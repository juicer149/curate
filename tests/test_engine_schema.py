import json
from pathlib import Path
from curate.api import analyze_file
from curate.engine import payload_for_action

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "tests" / "example_model.py"


def _validate_folds(folds):
    assert isinstance(folds, list)
    last_end = -1
    for f in folds:
        assert "start" in f and "end" in f
        assert isinstance(f["start"], int) and isinstance(f["end"], int)
        assert f["start"] <= f["end"]  # inclusive ranges allow single-line folds
        assert f["start"] > last_end  # non-overlapping, strictly increasing by start
        last_end = f["end"]


def test_engine_actions_schema():
    scope = analyze_file(str(EXAMPLE))
    for action in ("local", "minimum", "code", "docs"):
        payload = payload_for_action(scope, cursor_line=1, action=action)
        assert "folds" in payload
        _validate_folds(payload["folds"])
