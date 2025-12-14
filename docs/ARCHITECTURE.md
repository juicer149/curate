# Curate — Architecture

Curate is a **semantic code structure analyzer** designed to power
editor features such as folding, outlining, and documentation views.

The core idea is simple:

> **First build a correct semantic model of code and documentation.  
> Then derive editor behaviour from that model.**

This document explains how Curate is structured, why it is structured
this way, and how the pieces fit together.

---

## Design Goals

Curate is built around the following principles:

### 1. Editor-agnostic core
The core logic:
- has no editor state
- has no cursor, buffer, or UI assumptions
- is fully testable with plain Python

Editors (Neovim, VS Code, etc.) are thin adapters on top.

### 2. Deterministic and stateless
Given:
- source text
- cursor line
- action

Curate always returns the same result.
There is no hidden state.

### 3. Explicit ownership
Every line of source belongs to **exactly one semantic owner**:
- code
- docstring
- comment

No line is interpreted twice or ambiguously.

### 4. Documentation is first-class
Docstrings are not treated as “part of code bodies”.
They are modeled as their own entities with structure.

---

## High-level Architecture

```

```
        ┌──────────────────┐
        │   Source Text    │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │     Analyzer     │
        │  (AST + text)    │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │  Semantic Model  │
        │  (Scope / Entity │
        │   / Line)        │
        └────────┬─────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
```

Queries         Views       Fold Plan
(read-only)    (line sets)   (ranges)
└────────────┼────────────┘
▼
┌──────────────────┐
│     Engine       │
│ (editor-facing) │
└────────┬─────────┘
▼
┌──────────────────┐
│   Editor (Lua)   │
└──────────────────┘

````

---

## Core Data Model

### Line

```python
Line(
    number: int,
    text: str,
    kinds: FrozenSet[str]  # "code", "doc", "comment"
)
````

* Immutable
* Represents a physical line in the file
* `kinds` allows layered semantics (e.g. code + doc)

---

### Entity

```python
Entity(
    is_code: bool,
    kind: Optional[str],     # class, function, docstring, block, ...
    name: Optional[str],
    head: Tuple[Line, ...],
    body: Tuple[Line, ...],
)
```

Entities are **semantic units**.

Examples:

* a class
* a function
* a docstring
* a future block (`if`, `try`, etc.)

#### Head / Body split

* **HEAD**: the signature or summary
* **BODY**: implementation or details

This split is **authoritative** and done once during analysis.
No downstream code re-interprets docstrings.

---

### Scope

```python
Scope(
    lines: Tuple[Line, ...],
    entities: Tuple[Entity, ...],
    children: Tuple[Scope, ...],
)
```

A scope is a **lexical region**:

* module
* class
* function

Scopes:

* contain entities defined directly inside them
* may contain nested scopes
* do NOT store parent references (derived instead)

---

## Analyzer Layer (`analyzer.py`)

The analyzer is responsible for building the semantic model.

Responsibilities:

* parse source using Python AST
* extract code entities (classes, functions)
* extract docstrings via AST ownership
* split docstrings into HEAD / BODY
* ensure docstring lines are never part of code bodies
* build the scope tree

Key invariant:

> **Each line has exactly one semantic owner.**

---

## Query Layer (`query.py`)

The query layer provides **read-only access** to the model.

Examples:

* `best_entity_at_line`
* `entities_at_line`
* `scope_at_line`
* `parent_entity`
* `direct_children`
* `descendants`

Important properties:

* queries never mutate state
* parent/child relations are *derived*, not stored
* enables flexible traversal without cycles

This layer is what enables context-aware editor behaviour.

---

## Views (`views.py`)

Views produce **linear line selections** from a scope.

View modes:

* `FULL` — everything
* `CODE_ONLY` — code, no docs
* `DOCS_ONLY` — docs, no code
* `MINIMUM` — entity heads only

Views:

* operate only on `Line.kinds`
* do not inspect AST or entities directly
* are deterministic and testable

---

## Fold Plan (`foldplan.py`)

A fold plan answers one question:

> Which line ranges should be hidden for a given view?

Output:

```python
Tuple[(start_line, end_line), ...]
```

Properties:

* inclusive ranges
* normalized
* non-overlapping

Fold plans are pure data and editor-independent.

---

## Engine (`engine.py`)

The engine is the **only editor-facing logic**.

Signature:

```python
fold_for_cursor(
    source_text: str,
    cursor_line: int,
    action: Action,
) -> Tuple[(start, end), ...]
```

### Actions

* `TOGGLE_LOCAL` — fold the local entity body (leader+t)
* `TOGGLE_CODE` — hide code in current scope
* `TOGGLE_DOCS` — hide docs in current scope
* `TOGGLE_MINIMUM` — show heads only

The engine:

* re-analyzes the buffer (stateless)
* resolves cursor context via queries
* delegates folding logic to fold plans

The engine does **not**:

* track folded state
* talk to the editor
* maintain caches

---

## Public API Surface (`__init__.py`)

Curate exposes a deliberately small public API:

### Entry points

* `analyze_text`
* `analyze_file`

### Engine

* `fold_for_cursor`
* `Action`

### Advanced queries

* `best_entity_at_line`
* `scope_at_line`
* `parent_entity`, etc.

Everything else is considered internal.

---

## Editor Integration Philosophy

Editors are responsible for:

* providing source text
* providing cursor line
* applying fold ranges

Curate is responsible for:

* understanding code structure
* deciding *what* should fold

This separation keeps Curate:

* reusable
* testable
* stable

---

## Extensibility

Curate is designed to grow in these directions:

* indentation-based blocks (`if`, `try`, `match`)
* additional languages (new analyzers)
* outline / symbol views
* documentation-only navigation
* structural refactoring helpers

None of these require changing the engine API.

---

## Summary

Curate is built as:

> **Semantic analysis first.
> Editor behaviour second.**

This architecture allows Curate to stay small, correct, and powerful,
while enabling rich editor features without embedding editor logic
inside the core.
