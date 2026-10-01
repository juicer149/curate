"""outline_folds: language-free, on hand-made facts."""
from __future__ import annotations

from curate import RawFact, Span, outline_folds
from curate.curation import curate

PYTHON = {"class": "open", "function": "closed"}
MARKDOWN = {f"h{n}": "open" for n in range(1, 7)}


def folds(facts, kinds):
    scopes = curate([RawFact(label, Span(s, e)) for label, s, e in facts])
    return [(f.start, f.end) for f in outline_folds(scopes, kinds)]


def test_functions_fold_whole_and_hide_what_is_inside():
    facts = [
        ("function", 7, 19), ("function", 11, 13), ("if", 15, 17),
        ("class", 22, 24), ("function", 23, 24),
    ]
    assert folds(facts, PYTHON) == [(7, 19), (23, 24)]


def test_class_keeps_its_header_and_shows_each_method():
    facts = [("class", 1, 10), ("function", 4, 6), ("function", 8, 10)]
    assert folds(facts, PYTHON) == [(1, 3), (4, 6), (8, 10)]


def test_open_entry_without_entries_inside_folds_whole():
    assert folds([("class", 1, 5)], PYTHON) == [(1, 5)]


def test_entries_inside_non_entries_still_show():
    # def inside `if TYPE_CHECKING:` or `if __name__ == "__main__":`
    facts = [("if", 1, 10), ("function", 2, 5), ("function", 7, 10)]
    assert folds(facts, PYTHON) == [(2, 5), (7, 10)]


def test_markdown_every_heading_shows():
    # tests/fixtures/markdown_minimal.md
    facts = [
        ("h1", 1, 16), ("h2", 5, 12), ("h3", 9, 12), ("h2", 13, 16),
        ("h1", 17, 19),
    ]
    assert folds(facts, MARKDOWN) == [(1, 4), (5, 8), (9, 12), (13, 16), (17, 19)]


def test_single_line_ranges_are_dropped():
    # class line directly followed by its first method: no header fold
    facts = [("class", 1, 4), ("function", 2, 4), ("function", 6, 6)]
    assert folds(facts, PYTHON) == [(2, 4)]


def test_no_kinds_means_no_folds():
    assert folds([("function", 1, 5)], {}) == []


def test_folds_never_overlap():
    facts = [
        ("class", 1, 30), ("function", 3, 10), ("class", 12, 30),
        ("function", 14, 20), ("function", 15, 18), ("function", 22, 30),
    ]
    out = folds(facts, PYTHON)
    for (s1, e1), (s2, e2) in zip(out, out[1:]):
        assert e1 < s2
    assert out == [(1, 2), (3, 10), (12, 13), (14, 20), (22, 30)]
