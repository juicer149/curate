# Curate – Core Engine (`src/curate/`)

This directory contains the **core engine and backends** for Curate.

Curate is a structural folding engine designed to be editor-agnostic.
Editors (e.g. Neovim) act as thin frontends that provide cursor position
and file contents, while Curate computes **structural fold ranges**
based on language-aware backends.

This README documents **Curate v1 semantics**, as implemented and
validated by tests.

---

## High-level architecture

```

editor (Lua / Vim / etc)
|
v
Config (file_type, content, cursor, level, fold_children)
|
v
engine.fold(cfg)
|
v
backend_factory.get_backend(file_type)
|
v
language backend (e.g. Python AST)
|
v
Iterable[Range]  # fold ranges (1-based, inclusive)

````

Curate itself does **not** apply folds.
It only computes *what* should be folded.

---

## Core concepts

### 1. Nodes

All backends produce a tree of `Node` objects.

A `Node` represents a **structural span** in a file:

| Kind      | Meaning                          |
|-----------|----------------------------------|
| `module`  | Entire file                      |
| `class`   | Class definition                 |
| `function`| Function / method definition     |
| `doc`     | Docstring                        |

Each node has:

- `kind`
- `start` (1-based line number)
- `end` (1-based line number, inclusive)
- `parent`
- `children`

Nodes are **pure structure**.
They do not encode folding rules themselves.

---

### 2. Folding model (v1)

Curate v1 follows a strict **header / body** folding model.

#### General rule

- A node may have a *foldable body*
- The fold range returned is **only the body**
- Headers always remain visible

---

### 3. Docstring semantics (important)

Docstrings are **first-class nodes** in v1.

They are treated uniformly with code nodes, but with a fixed header rule.

#### Docstring rules

Let a doc node span `N` lines:

- If `N <= 2`  
  → no foldable body
- If `N > 2`  
  → header = first **2 lines**  
  → body = remaining lines

Example:

```python
"""
Summary line.
More details.

Attributes:
    x: ...
"""
````

Header (always visible):

```
"""
Summary line.
```

Folded body:

```
More details.

Attributes:
    x: ...
"""
```

**Notes:**

* Blank lines are irrelevant
* No attempt is made to parse docstring structure
* This follows PEP 257’s “summary first” convention
* The goal is to show a short summary while folding details

---

### 4. Cursor semantics

The cursor is interpreted structurally.

Important rule:

> **Docstring nodes are never selected as the current scope.**

If the cursor is inside a docstring:

* The enclosing function / class / module is selected instead

This ensures:

* `level` behaves predictably
* Folding never “gets stuck” inside documentation

---

### 5. `level`

`level` selects how many ancestors to walk *up* from the current node.

* `level = 0` → current enclosing node
* `level = 1` → parent
* `level = 2` → grandparent
* …etc

The walk stops at the root (`module`).

---

### 6. `fold_children`

`fold_children` controls *how* folding is applied to the selected target node.

#### `fold_children = False` (scope fold)

Fold the **entire body** of the target node.

* Classes → class body
* Functions → function body
* Module → everything except header
* If the node has a docstring, the fold is the docstring body

This corresponds to an editor action like **“fold this block”**.

---

#### `fold_children = True` (children fold)

Fold the **bodies of all immediate children** of the target node.

Children may include:

* Docstrings
* Methods
* Nested functions
* Classes

Each child is folded independently according to its own rules.

This corresponds to **“fold everything inside this block”**.

---

## Python backend (`backends/python_ast.py`)

The Python backend uses the standard library `ast` module.

### Responsibilities

1. Parse source code into an AST
2. Convert AST nodes into Curate `Node`s
3. Detect docstrings explicitly
4. Build a structural node tree
5. Resolve cursor → node → ancestor
6. Compute fold ranges according to v1 rules

### Design notes

* `ast.end_lineno` is required (Python ≥ 3.8)
* Docstrings are detected via:

  * `Expr(Constant(str))` as first body element
* Doc nodes are:

  * included in the tree
  * excluded from cursor targeting

---

## Engine entry point

```python
from curate import Config, fold
```

```python
cfg = Config(
    file_type="python",
    content=source_text,
    cursor=25,        # 1-based line number
    level=1,
    fold_children=True,
)

ranges = fold(cfg)
```

Returns:

```python
Iterable[tuple[int, int]]
```

Each tuple is a **1-based, inclusive line range** suitable for editor folding APIs.

---

## v1 scope and guarantees

Curate v1 intentionally keeps semantics minimal and explicit:

* No language-specific policy branching
* No heuristics
* No “smart” doc parsing
* No editor assumptions

What you see in tests **is the contract**.

Future versions may:

* Add configurable policies
* Differentiate code vs docs
* Introduce Tree-sitter backends
* Support incremental parsing

But v1 is intentionally rigid and predictable.

---

## Summary

`src/curate/` provides:

* A small, test-locked folding engine
* Deterministic structural semantics
* Language backends with clear responsibility boundaries
* A clean separation between editor UX and folding logic

If tests pass, behavior is guaranteed.

---

*Curate v1: fold structure, not text.*
