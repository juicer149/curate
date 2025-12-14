# tests/test_engine_properties.py
from curate.engine import fold_for_cursor, Action


def test_toggle_local_folds_only_inside_file(example_model):
    source = example_model["source_text"]
    total = example_model["total_lines"]

    for line in range(1, total + 1):
        folds = fold_for_cursor(
            source,
            cursor_line=line,
            action=Action.TOGGLE_LOCAL,
        )

        for start, end in folds:
            assert start <= end
            assert start >= 1
            assert end <= total
