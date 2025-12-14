import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "tests" / "example_model.py"


def run_cmd(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def test_cli_help():
    code, out, err = run_cmd([sys.executable, "-m", "curate", "--help"])
    assert code == 0
    assert "usage" in (out or err).lower()


def test_cli_valid_file_outputs_json():
    code, out, err = run_cmd([sys.executable, "-m", "curate", str(EXAMPLE), "--line", "1", "--action", "minimum"])
    assert code == 0, err
    payload = json.loads(out)
    assert isinstance(payload.get("folds"), list)


def test_cli_bad_path_errors():
    code, out, err = run_cmd([sys.executable, "-m", "curate", str(ROOT / "no_such_file.py")])
    assert code != 0


def test_cli_invalid_action_errors():
    code, out, err = run_cmd([sys.executable, "-m", "curate", str(EXAMPLE), "--line", "1", "--action", "nope"])
    assert code != 0
    assert "Unknown action" in (err or out)
    # stdout should not be valid JSON
    try:
        json.loads(out)
        assert False, "stdout should not be JSON on error"
    except Exception:
        pass
