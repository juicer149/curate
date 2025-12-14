# Curate – Python Engine

This directory contains the **semantic core** of Curate.

Everything here is:
- editor-agnostic
- stateless
- deterministic
- testable in isolation

The Python engine is the **single source of truth**.
Editor integrations (Lua, etc.) merely invoke it.

---

## Responsibilities

The Python backend is responsible for:

- Parsing Python source code
- Building a semantic model (scopes, entities, lines)
- Classifying code vs documentation
- Producing deterministic fold plans
- Answering structural queries for editor features

It does **not**:
- track editor state
- manage folds
- care about UI behavior
- cache results

---

## High-level Architecture

```

Source Text
↓
Analyzer (AST + text)
↓
Semantic Model

* Line
* Entity
* Scope
  ↓
  Queries / Views
  ↓
  Fold Plan
  ↓
  Engine (fold_for_cursor)

````

Each stage is pure and testable.

---

## Public API

The public API is intentionally small and explicit.

### Entry points

```python
from curate import analyze_text, analyze_file
````

* `analyze_text(source_text: str) -> Scope`
* `analyze_file(path: str) -> Scope`

These produce a **semantic model**, not folds.

---

### Engine (editor-facing)

```python
from curate import fold_for_cursor, Action
```

```python
folds = fold_for_cursor(
    source_text,
    cursor_line=42,
    action=Action.TOGGLE_MINIMUM,
)
```

Returns:

```python
((start_line, end_line), ...)
```

Properties:

* 1-based line numbers
* inclusive ranges
* normalized and non-overlapping
* no side effects

This is the primary API used by Neovim.

---

### Actions

```python
class Action(Enum):
    TOGGLE_LOCAL
    TOGGLE_CODE
    TOGGLE_DOCS
    TOGGLE_MINIMUM
```

Actions represent **user intent**, not structure.

| Action           | Meaning                                      |
| ---------------- | -------------------------------------------- |
| `TOGGLE_LOCAL`   | Fold the body of the entity under the cursor |
| `TOGGLE_CODE`    | Hide code, show docs in current scope        |
| `TOGGLE_DOCS`    | Hide docs, show code in current scope        |
| `TOGGLE_MINIMUM` | Show only entity heads                       |

---

## Semantic Model

### Line

```python
Line(
    number: int,
    text: str,
    kinds: FrozenSet[str],
)
```

A `Line` represents a single physical line of text.

Kinds may include:

* `"code"`
* `"doc"`
* `"comment"`

Lines may carry **multiple semantic tags**.

---

### Entity

```python
Entity(
    is_code: bool,
    kind: str | None,
    name: str | None,
    head: Tuple[Line, ...],
    body: Tuple[Line, ...],
)
```

Entities represent **semantic ownership**.

Examples:

* class
* function
* async function
* docstring

Key invariant:

> **Docstrings are split exactly once — in the analyzer.**
> Downstream layers must treat `head` and `body` as authoritative.

---

### Scope

```python
Scope(
    lines: Tuple[Line, ...],
    entities: Tuple[Entity, ...],
    children: Tuple[Scope, ...],
)
```

Scopes represent **lexical containment**.

* scopes are nested
* entities live inside scopes
* no parent pointers are stored
* relationships are derived via queries

---

## Analyzer (`analyzer.py`)

The analyzer builds the semantic model.

Responsibilities:

* AST traversal
* docstring extraction
* head/body splitting
* entity ownership
* line tagging
* scope construction

Important rules:

* Docstring lines are **never part of code bodies**
* Every line has exactly one semantic owner
* Doc HEAD = summary paragraph
* Doc BODY = remaining content

---

## Query Layer (`query.py`)

Queries derive structure from the model.

Provided queries:

* `entities_at_line`
* `best_entity_at_line`
* `scope_at_line`
* `parent_entity`
* `direct_children`
* `descendants`

All queries are:

* stateless
* deterministic
* derived (no stored parent pointers)

---

## Views (`views.py`)

Views operate **only on lines**, not entities.

```python
ViewMode:
    FULL
    MINIMUM
    CODE_ONLY
    DOCS_ONLY
```

Views answer the question:

> “Which lines should be visible?”

They do **not** compute folds directly.

---

## Fold Plans (`foldplan.py`)

Fold plans convert views into fold ranges.

Properties:

* inclusive line ranges
* normalized
* non-overlapping
* stable ordering

This separation allows:

* testing folds without an editor
* reuse across integrations
* strict correctness guarantees

---

## Engine (`engine.py`)

The engine ties everything together.

```python
fold_for_cursor(source_text, cursor_line, action)
```

Rules:

* no state
* no caching
* analyze on every call
* correctness over speed (v0.1)

This function is the **only semantic entrypoint** editors should call.

---

## CLI (`cli.py`)

The CLI is a thin wrapper around the engine:

```bash
python -m curate file.py --line 42 --action minimum
```

Output:

```json
{
  "action": "minimum",
  "cursor_line": 42,
  "entity": { "kind": "function", "name": "foo" },
  "folds": [{ "start": 10, "end": 38 }]
}
```

The CLI exists primarily for:

* editor IPC (Lua)
* debugging
* integration testing

---

## Testing Philosophy

The Python backend is heavily tested.

Goals:

* semantic correctness
* stable contracts
* deterministic folding
* editor-safe behavior

Tests assert:

* inclusive fold ranges
* non-overlapping folds
* correct doc/code separation
* strict ordering
* safe no-op behavior

See `TESTING.md` for details.

---

## Stability Guarantees

### Stable

* Public API in `curate/__init__.py`
* `fold_for_cursor`
* `Action`
* CLI JSON contract

### Internal (may change)

* analyzer internals
* block extraction
* rendering helpers
* debug utilities

---

## Philosophy

Curate follows a strict principle:

> **Correct semantics first. Editor UX second.**

By making the model explicit and deterministic,
all editor features become simpler, safer, and composable.
