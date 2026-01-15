"""
Invariant tests for Curate.

These tests assert *safety* and *structural correctness* only.
They do NOT assert semantic meaning or exact folding behavior.

Invariants tested here must hold for:
- all cursor positions
- all supported folding modes
- valid and unknown languages

If any of these fail, Curate has violated a core contract.
"""

from pathlib import Path

from curate import fold


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

FIXTURE = Path(__file__).parent / "fixtures/python_minimal.py"
TEXT = FIXTURE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Core invariants
# ---------------------------------------------------------------------------

def test_fold_never_crashes_for_any_cursor():
    """
    Invariant:
    - fold() must never crash
    - for any cursor position
    - for any supported mode
    - returned ranges (if any) must be valid and in-bounds

    This test intentionally does NOT assert:
    - exact line numbers
    - minimum fold size
    - semantic correctness

    It only asserts safety and consistency.
    """
    total_lines = len(TEXT.splitlines())

    for cursor in range(1, total_lines + 1):
        for mode in ("self", "children"):
            ranges = fold(
                source=TEXT,
                cursor=cursor,
                mode=mode,
                language="python",
            )

            # fold() must always return an iterable of ranges
            assert isinstance(ranges, tuple)

            for a, b in ranges:
                # type safety
                assert isinstance(a, int)
                assert isinstance(b, int)

                # bounds safety
                assert 1 <= a <= b <= total_lines


def test_fold_returns_no_duplicate_ranges():
    """
    Invariant:
    - fold() must not return duplicate ranges

    Duplicate ranges indicate either:
    - a projection bug
    - or broken normalization
    """
    ranges = fold(
        source=TEXT,
        cursor=7,  # inside top()
        mode="children",
        language="python",
    )

    assert len(ranges) == len(set(ranges))


def test_fold_ranges_are_sorted():
    """
    Invariant:
    - fold() must return ranges in ascending order

    This is required for:
    - editor folding APIs
    - predictable downstream processing
    """
    ranges = fold(
        source=TEXT,
        cursor=7,
        mode="children",
        language="python",
    )

    assert list(ranges) == sorted(ranges)


def test_fold_is_deterministic():
    """
    Invariant:
    - fold() must be deterministic

    Same input must always yield the same output.
    """
    r1 = fold(
        source=TEXT,
        cursor=12,
        mode="self",
        language="python",
    )
    r2 = fold(
        source=TEXT,
        cursor=12,
        mode="self",
        language="python",
    )

    assert r1 == r2
