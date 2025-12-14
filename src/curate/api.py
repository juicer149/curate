from pathlib import Path
from .analyzer import analyze_source


def analyze_text(source_text: str):
    """
    Analyze raw source text.
    Intended for editor / IPC usage (Lua, tests, etc).
    """
    return analyze_source(source_text)


def analyze_file(path: str):
    """
    Analyze a file on disk.
    CLI-facing convenience wrapper.
    """
    source_path = Path(path)
    with open(source_path, "r", encoding="utf-8") as file:
        source_text = file.read()

    return analyze_source(source_text)
