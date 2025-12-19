# README.md — Python AST Backend

````markdown
# Curate Python Backend (AST-based)

This backend provides **structural folding for Python source code**
using Python’s built-in `ast` module.

It is one backend among many in Curate’s architecture and is responsible
only for **extracting structure and producing fold ranges**.
It does not know about editors, UI, or user keybindings.

---

## Position in Curate Architecture

High-level pipeline (Python backend highlighted):

    Adapter (CLI / editor)
        ↓
    Config (input contract)
        ↓
    engine.fold
        ↓
    backend_factory.get_backend
        ↓
    PythonASTBackend.fold        ← this backend
        ↓
    engine normalization
        ↓
    Adapter applies folds

The Python backend owns:

- parsing Python source text
- building a structural tree
- interpreting `level` and `fold_children`
- computing fold ranges

The engine owns:

- backend selection
- normalization
- output contract

---

## Structural Model

The backend converts Python source into a tree of **Node** objects.

Each Node represents a contiguous line span with ownership:

- `module`
- `class`
- `function`
- `doc` (docstring)

All nodes share the same shape:

- `start` : 1-based start line (inclusive)
- `end`   : 1-based end line (inclusive)
- `parent`
- `children`

Docstrings are detected using Python’s
“first statement is a string literal” rule.

---

## v1 Folding Semantics

### Uniform Treatment of Nodes

In **v1**, all structural nodes are treated uniformly:

- classes
- functions
- docstrings

There is **no semantic distinction** between code and documentation yet.

This is intentional.

Semantic differentiation (code vs docs) is planned for **v1.5**.

---

### Headers and Bodies

Folding operates on the concept of **header** and **body**.

| Node type | Header lines | Foldable body |
|---------|-------------|---------------|
| class / function / module | 1 | `(start + 1, end)` |
| docstring (`doc`) | 2 (if available) | `(start + 2, end)` |

Rules:

- If a node’s span is **not larger than its header**, it has **no foldable body**
- Single-line docstrings never fold
- Multi-line docstrings fold after their header

---

## `level` Semantics

`level` controls **how far up the structural tree** the folding target is chosen.

Backend contract:

- `level == 0`  
  → smallest structural scope containing the cursor (**mandatory**)
- `level == 1`  
  → parent of that scope
- `level == N`  
  → N ancestors up, stopping at the root

The engine does **not** interpret `level`.
This backend is responsible for its meaning.

---

## `fold_children` (f vs F)

`fold_children` selects **how the target scope is folded**.

### `fold_children = True`  (`f`)

Fold the **bodies of the target’s children**, keeping each child’s header visible.

Example (cursor on class):

```python
class X:
    def a():
        ...
    def b():
        ...
````

Result:

```python
class X:
    def a():
    def b():
```

---

### `fold_children = False` (`F`)

Fold the **body of the target itself**, keeping only its header visible.

Result:

```python
class X:
```

---

## Cursor in Docstrings

In v1, docstrings are first-class structural nodes.

If the cursor is inside a docstring:

* the docstring node itself becomes the target
* folding behaves exactly like for any other node

There is no implicit “jump to parent” in v1.

---

## What This Backend Does *Not* Do

This backend intentionally does **not**:

* distinguish code vs documentation semantically
* interpret editor state
* cache ASTs
* track incremental changes
* modify source code

It is purely:

> text → structure → ranges

---

## Future Direction (v1.5+)

Planned extensions without breaking the backend interface:

* semantic distinction between code and documentation
* different folding policies per node kind
* selective folding based on cursor context (e.g. “docs only”)
* subtree folding strategies

The current design keeps these extensions local to the backend.

---

## Design Rationale

This backend follows Curate’s core principles:

* **Structure over text**
  (AST ownership, not indentation heuristics)

* **Folding is a view, not a mutation**

* **Minimal contracts**
  (engine trusts backend invariants)

* **Deferred semantics**
  (model first, interpretation later)

The result is a predictable, testable, and extensible folding backend.
