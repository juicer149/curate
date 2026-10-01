"""Language lookup: runs without tree-sitter (language files are data)."""
from __future__ import annotations

import pytest

from curate.producers.treesitter import LanguageSpec, get_spec, language_for_path
from curate.producers.treesitter.languages import resolve


@pytest.mark.parametrize("name, canonical", [
    ("python", "python"),
    ("Python", "python"),
    ("py", "python"),
    ("markdown", "markdown"),
    ("md", "markdown"),
])
def test_names_and_aliases_resolve(name, canonical):
    assert resolve(name) == canonical
    assert isinstance(get_spec(name), LanguageSpec)


@pytest.mark.parametrize("name", ["", "cobol", "../python", "languages.python", "__init__", "spec"])
def test_unknown_or_unsafe_names_give_none(name):
    assert resolve(name) is None
    assert get_spec(name) is None


@pytest.mark.parametrize("path, language", [
    ("a/b/module.py", "python"),
    ("stubs.pyi", "python"),
    ("README.md", "markdown"),
    ("notes.MARKDOWN", "markdown"),
    ("Makefile", None),
    ("data.xyz", None),
])
def test_language_from_file_suffix(path, language):
    assert language_for_path(path) == language


def test_unknown_language_produces_no_facts():
    from curate.producers.treesitter import build_raw_facts

    assert len(build_raw_facts(source="x = 1\n", language="cobol").items) == 0
