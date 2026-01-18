"""Simple benchmark for Curate core (structural facts only).

Measures:
- compile_scope_set (Tree-sitter -> ScopeSet)
- parent lookup
- ancestors traversal
- full descendant scan

Run with:
    python bench_curate_core.py
"""

from time import perf_counter
from statistics import mean

from curate_next import compile_scope_set
from curate_next import relations


# -----------------------------
# Test source (scale here)
# -----------------------------

SRC = """
def foo(x):
    '''
    This is a docstring
    '''
    if x > 0:
        return x
    else:
        return -x

def bar(y):
    for i in range(y):
        if i % 2 == 0:
            print(i)

class Baz:
    def method(self):
        try:
            return foo(10)
        except Exception:
            return None
""" * 100   # repeat to simulate larger file


ITERATIONS = 1000



# -----------------------------
# Helpers
# -----------------------------

def timeit(fn):
    t0 = perf_counter()
    fn()
    return perf_counter() - t0


def find_scope_at_line(scopes, line):
    """
    Pure Curate-style lookup:
    return deepest scope that contains `line`.
    """
    best = None
    for s in scopes:
        if s.start <= line <= s.end:
            if best is None or len(s.id) > len(best.id):
                best = s
    return best


# -----------------------------
# Benchmarks
# -----------------------------

compile_times = []
lookup_times = []
parent_times = []
ancestor_times = []
descendant_times = []

for _ in range(ITERATIONS):
    # compile
    t = timeit(lambda: compile_scope_set(source=SRC, language="python"))
    compile_times.append(t)

    scopes = compile_scope_set(source=SRC, language="python")

    # scope lookup (cursor → deepest scope)
    from random import randint
    CURSOR_LINE = randint(1, SRC.count("\n"))  # random line in
    t = timeit(lambda: find_scope_at_line(scopes, CURSOR_LINE))
    lookup_times.append(t)

    scope = find_scope_at_line(scopes, CURSOR_LINE)
    if scope is None:
        continue

    # parent
    t = timeit(lambda: relations.parent(scopes, scope))
    parent_times.append(t)

    # ancestors
    t = timeit(lambda: relations.ancestors(scopes, scope))
    ancestor_times.append(t)

    # descendants (worst-case structural scan)
    t = timeit(lambda: relations.descendants(scopes, scope))
    descendant_times.append(t)


# -----------------------------
# Report
# -----------------------------

print("=== Curate core benchmark ===")
print(f"Iterations: {ITERATIONS}")
print(f"Source size (chars): {len(SRC)}")
print()

print(f"compile_scope_set:   {mean(compile_times)*1000:.3f} ms")
print(f"scope_at_line:       {mean(lookup_times)*1000:.3f} ms")
print(f"parent():            {mean(parent_times)*1000:.6f} ms")
print(f"ancestors():         {mean(ancestor_times)*1000:.6f} ms")
print(f"descendants():       {mean(descendant_times)*1000:.6f} ms")
