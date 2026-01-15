# Curate

**Curate** is a structural analysis engine for source code.

It parses source text into a **stable, immutable scope graph** and provides a
query system for navigating code structure in a deterministic and safe way.

Curate is designed to be used as the **foundation layer for AI context managers**,
editor tooling, and structural code navigation — not as a semantic analyzer.

---

## What Curate Is (and Is Not)

### Curate **is**
- A **structural parser** (based on Tree-sitter)
- A **scope graph builder**
- A **query engine** over structural relations
- Deterministic, immutable, and safe
- Language-aware (currently Python, extensible)

### Curate **is not**
- A semantic analyzer
- A type checker
- An AI system
- A formatter or linter

Curate answers questions like:

> *“What structural blocks exist here, and where are they?”*

Not:

> *“What does this code mean?”*

---

## Core Concepts

### 1. ScopeGraph

Every source file is parsed into a **ScopeGraph**:

```python
@dataclass(frozen=True)
class ScopeGraph:
    scopes: tuple[Scope, ...]
````

Each `Scope` represents a structural block:

```python
@dataclass(frozen=True)
class Scope:
    id: int
    parent_id: int | None
    kind: str              # e.g. "module", "function", "class", "if"
    start: int             # 1-based, inclusive
    end: int               # 1-based, inclusive
    header_lines: int
```

### Guarantees

* Scopes are **laminar** (nested or disjoint, never partially overlapping)
* Graph is **immutable**
* Same input → same output (deterministic)
* Safe to share across threads

---

### 2. Ranges

Curate works with **line ranges**:

```python
Range = tuple[int, int]  # (start_line, end_line), 1-based inclusive
```

All returned ranges satisfy:

```
1 <= start <= end <= total_lines
```

They are **always safe** to use with:

```python
lines = source.splitlines()
slice = lines[start - 1 : end]
```

---

## Primary API

### `query_ranges()` — **Main Entry Point**

```python
from curate import query_ranges

ranges = query_ranges(
    source=source_text,
    cursor=cursor_line,
    query={
        "axis": "self" | "children" | "parent" | "ancestors" | "descendants" | "siblings",
        "kinds": ["function", "class"],   # optional
        "max_items": 10,                  # optional
    },
    language="python",
)
```

### Guarantees

* Deterministic
* No duplicate ranges
* Sorted output
* Safe for text slicing
* Never crashes for any cursor
* Handles empty / unknown-language input safely

This is the **recommended API** for:

* AI context managers
* Structural extraction
* Skeleton building
* Token-budgeted context selection

---

## Query Axes

| Axis          | Meaning                         |
| ------------- | ------------------------------- |
| `self`        | The scope containing the cursor |
| `children`    | Direct child scopes             |
| `parent`      | Immediate parent scope          |
| `ancestors`   | All parents up to module        |
| `descendants` | All nested scopes               |
| `siblings`    | Scopes with same parent         |

---

## Producer System

Curate separates **parsing** from **querying**.

```python
from curate.producers import get_producer

producer = get_producer("python")
graph = producer(source_text)
```

### Guarantees

* Always returns a valid `ScopeGraph`
* Unknown languages fall back safely
* Empty source still produces a module scope
* No mutation, ever

---

## Indexing

```python
from curate.index import build_index

idx = build_index(graph)
```

The index enables:

* O(log n) deepest-scope lookup
* O(1) parent/child traversal
* Deterministic ordering

This is internal for most users — `query_ranges()` handles it automatically.

---

## Convenience API (Editor-Oriented)

### `fold()`

```python
from curate import fold

ranges = fold(
    source=source_text,
    cursor=cursor_line,
    mode="self" | "children",
    language="python",
)
```

`fold()` is a **preset query wrapper** intended for editor integrations
(e.g. code folding).

> **Do not use `fold()` for AI context management.**
> Use `query_ranges()` instead.

---

## Using Curate for AI Context Management

Curate intentionally stops at **structure**.

A typical AI context manager workflow:

```python
# 1. Extract structure
ranges = query_ranges(
    source=source,
    cursor=cursor,
    query={"axis": "descendants", "kinds": ["function", "class"]},
)

# 2. Slice text
lines = source.splitlines()
chunks = ["\n".join(lines[a-1:b]) for a, b in ranges]

# 3. Apply semantic relevance, token budgeting, ordering, etc.
```

Curate guarantees that:

* slicing will never crash
* structure is consistent
* repeated queries are independent

---

## Supported Languages

| Language | Status                       |
| -------- | ---------------------------- |
| Python   | Stable                     |
| Other    | Planned (via Tree-sitter) |

Language rules live in:

```
src/curate/producers/treesitter/languages/
```

---

## Testing & Guarantees

Curate is heavily tested for **invariants**, not just behavior.

Verified properties include:

* Determinism
* Immutability
* Laminar hierarchy
* Query independence
* Thread safety
* Safe slicing
* Token-limit enforcement

See:

* `tests/test_context_manager_invariants.py`
* `TEST_STATUS.md`

---

## Design Philosophy

Curate follows three core principles:

1. **Structure over semantics**
2. **Immutability everywhere**
3. **APIs over heuristics**

Curate tells you *what exists and where*.
You decide *what matters*.

---

## License

MIT

---

## Status

**Production-ready as a structural foundation for AI context managers.**
