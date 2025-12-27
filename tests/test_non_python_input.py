# tests/test_non_python_input.py

import pytest
from curate import fold


NON_PYTHON_SOURCES = {
    "lua": """
function hello(name)
    print("hello " .. name)
end
""",
    "c": """
#include <stdio.h>

int main(void) {
    printf("hello world");
    return 0;
}
""",
    "markdown": """
# Title

Some text here.

## Subtitle

More text.
""",
    "random": """
this is not code
at all
just text
"""
}


@pytest.mark.parametrize("source", NON_PYTHON_SOURCES.values())
def test_non_python_source_is_safe_and_returns_no_folds(source: str):
    """
    Non-Python input must:
    - never crash
    - never return invalid ranges
    - return no fold ranges at all
    """
    total_lines = len(source.splitlines())

    for cursor in range(1, max(total_lines, 1) + 1):
        for level in range(0, 3):
            for mode in ("self", "children"):
                ranges = fold(
                    source=source,
                    cursor=cursor,
                    level=level,
                    mode=mode,
                    language="unknown",
                )

                # Contract: no folding for unsupported languages
                assert ranges == ()
