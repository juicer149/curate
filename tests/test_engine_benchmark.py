# tests/test_engine_benchmark.py
from curate.engine import fold_for_cursor, Action


def test_toggle_local_benchmark(example_model, benchmark):
    """
    Micro-benchmark for semantic folding.
    """
    source = example_model["source_text"]

    benchmark(
        fold_for_cursor,
        source,
        29,
        Action.TOGGLE_LOCAL,
    )
