# Curate vNext — Architecture & Data Flow

This document describes **what Curate is**, **what it is not**, and
how its **data objects move through the system**.

Curate is intentionally small.
It defines *structural facts* and *deterministic relations* over source code.
All higher-level meaning, policy, and tooling live outside.

---

## 1. Core Idea

Curate answers exactly one question:

> **“What structural regions exist in this source text, and how are they nested?”**

It does **not** answer:
- what the code means
- which parts are important
- how code should be folded
- how much context an AI should receive

Curate produces **facts**, not decisions.

---

## 2. Core Data Objects (IR)

### 2.1 `Scope`

A `Scope` is the atomic structural fact.

```text
Scope
 ├─ id        : int
 ├─ parent_id : int | None
 ├─ kind      : str
 ├─ start     : int   (1-based, inclusive)
 └─ end       : int   (1-based, inclusive)
```

Properties:

* purely positional
* immutable
* no text
* no semantics

A scope answers:

> “There exists a region of text from line X to Y.”

Nothing more.

---

### 2.2 `ScopeSet`

A `ScopeSet` is an **immutable collection of scopes**.

Key invariants:

* scopes are **laminar**
  (any two scopes are either nested or disjoint)
* ordering is deterministic
* safe to share across threads
* structural equality is well-defined

`ScopeSet` behaves like a Python container:

* iterable
* indexable
* sliceable (returns a new `ScopeSet`)

`ScopeSet` deliberately does **not**:

* answer queries
* know about files or projects
* interpret scope kinds

It is a *fact set*, not a query engine.

---

## 3. Compilation Pipeline (Fact Creation)

### 3.1 `compile_scope_set`

```
source text
    ↓
Tree-sitter (or fallback)
    ↓
ScopeSet
```

Responsibilities:

* parse source text
* identify structural regions
* emit scopes with correct nesting
* guarantee laminar structure

Non-responsibilities:

* no indexing
* no caching
* no interpretation
* no policies

If parsing fails or no grammar exists:

* a single `module` scope is returned safely

---

### 3.2 Multiple Sources

```
[SourceUnit, SourceUnit, ...]
            ↓
compile_scope_sets
            ↓
Single ScopeSet (rebased id-space)
```

Notes:

* scopes are concatenated
* ids are offset to remain unique
* provenance (file paths, modules) is intentionally external

Curate does not own project structure.

---

## 4. Derived Structures (Acceleration Only)

### 4.1 `Index`

An `Index` is a **derived acceleration structure** built from a `ScopeSet`.

```
ScopeSet
    ↓
build_index
    ↓
Index
```

Important:

* Index contains **no new information**
* it can always be rebuilt
* it exists only to make queries fast

Stored internally:

* parent / children maps
* start/end arrays for binary search
* id → scope mapping

---

### 4.2 Cursor Primitive

The fundamental operation:

```python
scope_at_line(index, line) -> Scope | None
```

Semantics:

* returns the *deepest* scope containing a line
* O(log n) + laminar descent
* safe for editor keystrokes

This is the cornerstone of all navigation.

---

## 5. Relations (Pure Structural Algebra)

Relations are **pure functions**:

```text
(Index, Scope) → tuple[Scope]
```

Available relations:

* parent
* children
* ancestors
* descendants
* siblings

Properties:

* deterministic
* no filtering
* no side effects
* no policy

Relations describe **structure only**, not importance.

---

## 6. Query Layer (Convenience, Not Policy)

`query_ranges` is a **thin adapter** on top of:

* compilation
* indexing
* relations

```
source + cursor + query
        ↓
ScopeSet
        ↓
Index
        ↓
Relations
        ↓
[(start, end), ...]
```

Guarantees:

* safe slicing ranges
* deterministic output
* no crashes for any cursor
* no duplicate ranges

This layer exists for:

* editors
* AI context selection
* tooling

It is **not** a policy engine.

---

## 7. What Curate Explicitly Does Not Do

Curate does not:

* rank scopes
* select “important” code
* manage token budgets
* manage projects or workspaces
* cache or incrementally update files
* integrate with editors directly

All of these belong to **layers above Curate**.

---

## 8. Why This Design

Curate follows three principles:

1. **Facts over heuristics**
2. **Immutability everywhere**
3. **APIs over interpretation**

Curate tells you:

> *what exists* and *where*

You decide:

> *what matters* and *why*

---

## 9. Mental Model

Think of Curate as:

* an **IR generator** (like a compiler front-end)
* a **structural index** (not semantic)
* a **foundation layer**, not a product

This makes it:

* stable
* testable
* reusable across editors, AI systems, and tools
