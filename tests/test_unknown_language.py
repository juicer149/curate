from curate import fold


def test_unknown_language_is_safe():
    src = "just text\nwith lines"
    total = len(src.splitlines())
    for cursor in range(1, total + 1):
        ranges = fold(
            source=src,
            cursor=cursor,
            mode="children",
            language="unknown",
        )
        for a, b in ranges:
            assert 1 <= a < b <= total
