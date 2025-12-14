# Curate

**Curate** is a semantic code structure analyzer designed to power
editor features such as **context-aware folding**, **documentation views**,
and **structural navigation**.

Curate cleanly separates:

- **semantic understanding** (Python)
- **editor behavior** (Lua / Neovim)

> You tell Curate *what the code is*.  
> Your editor decides *how to show it*.

---

## What Curate Is (and Is Not)

Curate is:

- semantic (AST + text aware)
- deterministic
- stateless
- editor-agnostic at its core
- designed for integration, not UI

Curate is **not**:

- an editor plugin by itself
- a folding UI
- stateful or incremental (v0.1)
- tied to Neovim internally

---

## High-level Architecture

```

Neovim (Lua)
│
│  buffer text + cursor line + intent
▼
Python CLI / Engine
│
│  semantic fold ranges (JSON)
▼
Neovim applies folds

```

Key idea:

> **Python decides semantics. Lua applies effects.**

---

## Python Engine (Semantic Core)

The Python backend lives in:

```

src/curate/

```

It is responsible for:

- Parsing Python source code
- Building a semantic model:
  - Lines
  - Entities (classes, functions, docstrings)
  - Scopes
- Separating documentation from code
- Computing deterministic fold plans
- Exposing a small, stable editor-facing API

The engine is:
- pure
- stateless
- fully testable without an editor

See:
```

src/curate/README.md

```
for full engine documentation.

---

## Lua Client (Neovim Integration)

The Lua side lives in:

```

lua/curate/

```

It is responsible for:

- Capturing editor state (buffer contents, cursor line)
- Calling the Python engine via `python -m curate`
- Parsing JSON responses
- Applying folds using Neovim commands
- Defining user-facing keybindings

The Lua client contains **no semantic logic**.

It treats the Python engine as a black box.

See:
```

lua/curate/README.md

````
for Lua-side architecture and usage.

---

## The Contract Between Lua and Python

Communication happens via **CLI + JSON only**.

### Input (Lua → Python)

Lua provides:
- full buffer text (via a temporary file)
- cursor line (1-based)
- semantic action (`local`, `minimum`, `code`, `docs`)

Example invocation:

```bash
python -m curate file.py --line 42 --action minimum
````

---

### Output (Python → Lua)

Python returns JSON:

```json
{
  "action": "minimum",
  "cursor_line": 42,
  "entity": {
    "kind": "function",
    "name": "foo"
  },
  "folds": [
    { "start": 10, "end": 38 }
  ]
}
```

Contract guarantees:

* fold ranges are 1-based
* fold ranges are inclusive
* folds are ordered
* folds never overlap
* empty folds are valid and meaningful

Lua **must not reinterpret semantics** — only apply folds.

---

## Semantic Actions

Actions represent **user intent**, not implementation details.

| Action    | Meaning                                      |
| --------- | -------------------------------------------- |
| `local`   | Fold the body of the entity under the cursor |
| `minimum` | Show only entity heads                       |
| `code`    | Hide code, show documentation                |
| `docs`    | Hide documentation, show code                |

Editors are free to bind these however they want.

---

## Neovim UX Philosophy

The default Neovim behavior is intentionally simple:

* If the cursor is already inside a fold → clear folds (`zE`)
* Otherwise → compute and apply semantic folds

This gives:

* predictable toggling
* no stored state
* no desynchronization between editor and engine

---

## Installation (Development)

Curate is currently intended for **local development and editor integration**.

```bash
pip install -e .
```

Requires:

* Python ≥ 3.10
* Neovim ≥ 0.9 (for `vim.system`)

---

## Neovim Setup (Local Plugin)

Example using a local plugin path:

```lua
return {
  dir = "~/code/packages/curate",
  name = "curate",
  ft = { "python" },
  config = function()
    require("curate").setup()
  end,
}
```

Keybindings are installed with safe defaults and can be overridden.

---

## Testing

Curate has **two independent test layers**:

### Python

* pytest
* high coverage on semantic core
* strict fold and JSON contract tests

### Lua

* Busted smoke tests
* A custom harness with a stubbed `vim` API
* Real client code tested without Neovim

Run everything with:

```bash
make test-all
```

See `TESTING.md` for details.

---

## Design Principles

Curate follows a few strict rules:

* **Model first. UI second.**
* Semantics are explicit, never inferred in the editor
* Editors are clients, not peers
* Correctness > cleverness
* Determinism over heuristics

---

## Status

Curate is:

* stable for experimentation
* suitable for real editor integration
* under active development

The **engine API and CLI contract are expected to remain stable**.

---

## Roadmap (Non-binding)

Possible future work:

* indentation-based block entities
* other languages
* outline / symbol views
* LSP-style integration
* incremental analysis

None of these change the core contract.

---

## Summary

Curate works because:

* Python owns meaning
* Lua owns effects
* The boundary is explicit and tested

This makes editor features easier to build,
easier to test,
and harder to break.
