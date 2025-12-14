# Curate

**Curate** is a semantic code structure analyzer designed to power
editor features such as **context-aware folding**, **documentation views**
and **structural navigation**.

Curate separates **semantic understanding** from **editor behaviour**.

> You tell Curate *what the code is*.  
> Your editor decides *how to show it*.

---

## Why Curate?

Traditional folding is:
- indentation-based
- syntax-based
- unaware of documentation vs code

Curate instead builds a **semantic model** of your source code and lets
you fold, view, and navigate based on *meaning*.

Examples:
- Fold only code, keep docs visible
- Fold only docs, keep code visible
- Fold everything inside the current class
- Fold just the body of the function under the cursor
- Show only class / function headers

---

## Features

### ✅ Implemented
- Python source analysis via AST
- Explicit docstring extraction
- Docstring HEAD / BODY split
- Semantic entities (module, class, function, docstring)
- Lexical scope tree
- Line-based semantic queries
- Deterministic fold plans
- Editor-facing fold engine
- 100% deterministic, stateless core
- Extensive test coverage

### 🚧 Planned / Optional
- Indentation-based block entities (`if`, `try`, `match`, …)
- Outline / symbol view generation
- Support for other languages
- Editor plugins (Neovim first)

---

## Installation

Curate is currently intended for **local development and editor integration**.

```bash
pip install -e .
````

Requires:

* Python ≥ 3.10

---

## Quick Start

### Analyze a file (debug view)

```bash
python -m curate path/to/file.py
```

This prints a human-readable tree of:

* scopes
* entities
* docstrings
* heads and bodies

Useful for debugging and understanding the model.

---

### Use the engine (editor-facing)

```python
from curate import fold_for_cursor, Action

folds = fold_for_cursor(
    source_text=buffer_text,
    cursor_line=29,
    action=Action.TOGGLE_LOCAL,
)
```

Returns:

```python
((start_line, end_line), ...)
```

Your editor applies the folds.

---

## Engine Actions

| Action           | Description                              |
| ---------------- | ---------------------------------------- |
| `TOGGLE_LOCAL`   | Fold the body of the entity under cursor |
| `TOGGLE_CODE`    | Hide code in current scope               |
| `TOGGLE_DOCS`    | Hide docs in current scope               |
| `TOGGLE_MINIMUM` | Show only entity heads                   |

These map naturally to editor keybindings like:

* `leader + t`
* `leader + T`

---

## Public API

Curate intentionally exposes a **small public surface**.

### Entry points

* `analyze_text(source_text)`
* `analyze_file(path)`

### Engine

* `fold_for_cursor(...)`
* `Action`

### Queries (advanced)

* `best_entity_at_line`
* `entities_at_line`
* `scope_at_line`
* `parent_entity`
* `direct_children`
* `descendants`

Everything else is considered internal.

---

## Architecture

Curate is structured as a pipeline:

```
Source Text
    ↓
Analyzer (AST + text)
    ↓
Semantic Model (Scope / Entity / Line)
    ↓
Queries / Views / Fold Plans
    ↓
Engine
    ↓
Editor (Lua, etc.)
```

Key properties:

* editor-agnostic
* stateless
* deterministic
* fully testable

For details, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Editor Integration (Neovim)

Curate is designed to be called from Lua (or any editor language):

```lua
-- pseudo-code
local folds = call_python_engine(buffer_text, cursor_line, action)
apply_folds(folds)
```

Curate:

* never touches editor state
* never tracks folded regions
* never assumes UI behaviour

This keeps the integration simple and robust.

### Editor ↔ Engine Contract

Editors are expected to:

1. Provide:

   * full buffer text (or a temporary file)
   * a 1-based cursor line
   * an explicit semantic action

2. Invoke Curate as a pure function:

```text
python -m curate <file> --line <N> --action <local|minimum|code|docs>
```

3. Consume JSON output of the form:

```json
{
  "folds": [
    { "start": 10, "end": 25 },
    { "start": 40, "end": 72 }
  ]
}
```

4. Apply folds using editor-native mechanisms.

Curate guarantees:

* inclusive line ranges (`start <= end`)
* non-overlapping, ordered folds
* deterministic output for identical input
* no side effects or editor state assumptions

A reference Neovim client implementation exists and is tested, but is intentionally kept outside the core engine.

---

## Testing

See `TESTING.md` for an overview of the test strategy, contracts, and
commands for running Python and Lua tests.

Run everything with:

```bash
make test-all
```

The core is heavily tested to ensure:

* stable semantics
* correct folding behaviour
* safe editor integration

---

## Philosophy

Curate follows a strict rule:

> **Model first. UI second.**

By making the semantic model correct and explicit,
all editor features become easier and safer to implement.

---

## Status

Curate is:

* stable for experimentation
* suitable for real editor integration
* under active development

The API is expected to remain stable.
