# ARCHITECTURE.md (Curate)

# Curate — Architecture

This document describes the architecture of **Curate** as it exists today.

The explanation is intentionally framed in terms of:

- immutable data objects
- pure transformations
- explicit relations
- minimal, composable functions

Curate is **not** described in terms of features, commands, or editors.

Curate is a **structural fact engine**.

---

## Core Principle

> **Curate describes structure.  
> It never decides what is important.**

Curate answers exactly one class of questions:

> *What structural scopes exist in this source file, and how are they related?*

Everything else (folding, context selection, AI usage, editor UX) is **outside Curate**.

---

## High-Level Data Flow

source text (str)
↓
Producer (language-specific)
↓
ScopeGraph
↓
Index
↓
Query
↓
Scope[]
↓
Range[]

Each arrow is a **pure transformation**.

No stage mutates previous data.

---

## Fundamental Data Objects

### 1. `Scope`

**Defined in:** `model.py`

```python
Scope(
    id: int,
    parent_id: Optional[int],
    kind: str,
    start: int,
    end: int,
    header_lines: int
)
```

**Meaning**

A `Scope` is an **atomic structural fact**:

* it occupies a contiguous range of lines
* it has a parent (or is root)
* it has a kind label (opaque to Curate)

Curate does **not** interpret `kind`.
It is a string, not logic.

---

### 2. `ScopeGraph`

**Defined in:** `model.py`

```python
ScopeGraph(scopes: tuple[Scope, ...])
```

**Meaning**

A `ScopeGraph` is a **laminar set** of scopes:

* scopes are nested or disjoint
* no partial overlap is allowed
* ordering is deterministic

This is the **entire semantic output** of parsing.

---

## Producers (Parsing Layer)

### Producer Contract

```python
(source: str) -> ScopeGraph
```

Producers:

* accept raw source text
* emit **only structural facts**
* never apply policy
* never drop scopes based on importance

**Location**

```
curate/producers/
```

---

### Tree-sitter Producer

**Entry point**

```
producers/treesitter/producer.py → build_graph()
```

Pipeline:

1. load language rules (`registry.py`)
2. parse source into AST
3. walk AST
4. emit `Scope` objects
5. return `ScopeGraph`

Fallback:

* if parsing fails → single module scope

---

### Structural Rules Are Data

**Defined in**

```
producers/treesitter/rules.py
```

Rules describe **how syntax nodes map to scopes**.

They are:

* declarative
* immutable
* language-specific
* policy-free

This is intentional.

---

## Index Layer (Relational Acceleration)

### `Index`

**Defined in:** `index.py`

```python
Index(
    by_id: dict[int, Scope],
    parent: dict[int, Optional[int]],
    children: dict[int, tuple[int, ...]],
    order: tuple[int, ...],
    pos: dict[int, int],
    kind_to_ids: dict[str, tuple[int, ...]],
    starts: tuple[int, ...],
    ends: tuple[int, ...],
)
```

**Meaning**

`Index` is a **denormalized, read-only cache**.

It exists solely to make queries:

* fast
* deterministic
* simple

It contains **no new information**.

---

### Localisation Primitive

```python
deepest_scope_at_line(Index, line) -> Scope | None
```

This is the **only place** where:

* line numbers
* structure

intersect.

Everything else is relational.

---

## Query System (Relation Algebra)

### `Query`

**Defined in:** `query.py`

```python
Query(
    cursor: int,
    axis: Axis,
    kinds: tuple[str, ...],
    include_target: bool,
    max_items: Optional[int],
    kind: Optional[str]
)
```

A `Query` expresses **intent**, not outcome.

Examples:

* parent
* children
* ancestors
* descendants
* siblings
* next / prev
* all_of_kind

Curate does not know *why* you want these.

---

### Relations Are Pure Functions

Signature:

```python
(graph, index, target_scope, query) -> tuple[Scope, ...]
```

Defined in:

```
query.py
```

Relations:

* never mutate
* never inspect text
* never reorder arbitrarily
* never apply policy

This is **structural lambda calculus**.

---

### Relation Registry

```python
RELATIONS: dict[Axis, Relation]
```

Dispatch is table-driven.
No conditionals.
No heuristics.

This is intentional.

---

## Projection Layer

### Scope → Range

**Defined in:** `evaluator.py`

```python
ranges_for_scopes(scopes) -> tuple[Range, ...]
```

This converts abstract structure into **line ranges**.

At this point:

* semantics are gone
* only geometry remains

---

### Normalization (Safety Barrier)

**Defined in:** `normalize.py`

Responsibilities:

* clamp bounds
* remove invalid ranges
* deduplicate
* sort

This is the **final defensive layer**.

---

## Engine Layer (Orchestration Only)

**Defined in:** `engine.py`

Responsibilities:

* connect producer → index → query → evaluator → normalize
* expose a stable API

Public API:

```python
query_scopes()
query_ranges()
fold()   # editor convenience ONLY
```

The engine:

* contains no structural logic
* contains no policy
* contains no heuristics

---

## CLI (Imperative Shell)

**Defined in:** `__main__.py`

The CLI:

* parses arguments
* reads input
* serializes output

It is intentionally thin.
It is **not architecture**.

---

## What Curate Explicitly Does NOT Do

Curate does not:

* walk the filesystem
* read files
* decide importance
* assign weights
* enforce budgets
* render context
* speak to AI
* manage tokens

These belong to **higher layers**.

---

## Determinism Guarantees

Given:

* identical source text
* identical language rules
* identical query

Curate guarantees:

* identical ScopeGraph
* identical relations
* identical ranges

There is no randomness.
There is no hidden state.

---

## Role in the Larger System

Curate is a **structural oracle**.

It is designed to be embedded in:

* editors
* static analyzers
* context builders
* AI adapters
* documentation systems

It provides **facts**, not judgments.

---

## Final Rule

> **Curate describes what exists.
> Other systems decide what matters.**
