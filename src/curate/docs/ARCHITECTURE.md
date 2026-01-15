# Curate – Architecture

## Overview

Curate is a **deterministic structural analysis engine** for source code.

Its purpose is to extract *structural facts* ("scopes") from source text and allow higher‑level tools (editors, analyzers, AI systems) to **query and project** those facts in a predictable way.

Curate is intentionally **not**:

* a semantic analyzer
* a linter
* an AI system
* an editor plugin

It is a **core structural layer** designed to be reused by many consumers.

---

## Core Design Principles

### 1. Separation of Concerns

Curate is built as a strict pipeline with clearly separated responsibilities:

```
Source Text
  ↓
Producer        (syntax → structure)
  ↓
ScopeGraph      (structural facts)
  ↓
Index           (accelerated navigation)
  ↓
Query           (relations & selection)
  ↓
Ranges / Scopes (projection targets)
```

Each stage:

* consumes a well‑defined input
* produces a well‑defined output
* is unaware of how the other stages are implemented

This separation is enforced at the module level.

---

### 2. Structural, Not Semantic

Curate only answers questions of the form:

* *What structural scopes exist?*
* *How are they nested or related?*
* *Where are they located in the source?*

It does **not** answer:

* what code *means*
* whether code is *correct*
* which parts are *important*

Relevance and meaning are delegated to higher‑level systems.

---

### 3. Determinism

Given the same input:

* Curate always produces the same `ScopeGraph`
* queries always return the same scopes
* ranges are stable and reproducible

This property is critical for:

* editor tooling
* AI context construction
* caching and indexing

---

## Core Data Model

### Scope

A `Scope` represents a **contiguous structural region** of source code.

Each scope has:

* a stable `id`
* an optional `parent_id`
* a `kind` label (e.g. `function`, `class`, `if`)
* a 1‑based inclusive line range `[start, end]`
* a `header_lines` count

Scopes are **pure data**. They contain no text and no behavior beyond simple range helpers.

---

### ScopeGraph

A `ScopeGraph` is an immutable container of scopes with one invariant:

> Any two scopes are either **nested** or **disjoint**.

There is always a root `module` scope covering the entire file.

The graph itself contains **no indices or relations** beyond parent references.

---

## Producer Layer

### Responsibility

A *producer* is responsible for converting raw input into a `ScopeGraph`.

Responsibilities:

* parse source text
* identify structural constructs
* emit scopes with correct ranges
* guarantee a valid `ScopeGraph` for any input

Non‑responsibilities:

* cursor handling
* navigation
* querying
* relevance decisions

---

### Tree‑sitter Producer

The current implementation uses **Tree‑sitter** as the parsing backend.

The Tree‑sitter producer:

* loads a grammar for a given language
* walks the syntax tree
* applies language‑specific structural rules
* emits scopes accordingly

Tree‑sitter specific logic is fully isolated under:

```
curate/producers/treesitter/
```

---

### Language Rules

Language behavior is described using **data‑only rule definitions**:

* `NodePolicy` – how a syntax node participates in scope construction
* `WrapperRule` – how wrapper nodes forward start positions
* `LanguageRules` – a complete ruleset for a grammar

Rules:

* contain no Tree‑sitter imports
* perform no I/O
* are safe to serialize and inspect

---

### Language Registry

A central registry binds together:

* language identifier (e.g. `"python"`)
* grammar loader
* structural rules

This registry is the **only place** where language names are coupled to Tree‑sitter details.

---

## Index Layer

### Responsibility

The `Index` is a derived, immutable structure built from a `ScopeGraph`.

Its purpose is to provide **fast navigation primitives**:

* parent / children lookup
* next / previous scope
* kind‑based traversal
* efficient lookup by source line

The index contains no business logic and no semantics.

---

### Performance Guarantees

The index enables:

* O(1) parent/child access
* O(1) next/prev access
* O(log n + depth) lookup of deepest scope at a line

All performance optimizations are confined to this layer.

---

## Query Layer

### Responsibility

The query layer answers questions about **relationships between scopes**.

Queries are defined by:

* a cursor position
* an axis (e.g. `parent`, `siblings`, `ancestors`)
* optional filters (`kinds`, `max_items`)

The query layer:

* never parses source text
* never inspects syntax nodes
* operates purely on structural data

---

### Relations

Relations are implemented as small, composable functions:

* `self`
* `parent`
* `children`
* `ancestors`
* `descendants`
* `siblings`
* `next` / `prev`
* `next_same_kind` / `prev_same_kind`
* `all_of_kind`

This design is inspired by relational and functional programming models.

---

## Engine Layer

The engine orchestrates the full pipeline:

1. produce a `ScopeGraph`
2. build an `Index`
3. resolve a `Query`
4. project scopes into ranges

The engine is the **only module** that coordinates multiple layers.

---

## Skeletons and Projections

Curate does **not** define skeletons.

Instead, it provides the primitives required to build them:

* precise scope ranges
* header/body separation
* structural relations

Skeletons (e.g. headers‑only views, AI context summaries) are **projections built on top of Curate**, not part of the core.

This keeps Curate neutral and reusable.

---

## Intended Consumers

Curate is designed to be used by:

* editor tooling (folding, navigation)
* static analysis pipelines
* project indexers
* AI context builders

All consumers operate **above** the core and interpret its output according to their own needs.

---

## Non‑Goals

Curate explicitly avoids:

* semantic analysis
* symbol resolution
* type inference
* relevance scoring
* language‑specific heuristics outside producers

These are higher‑level concerns by design.

---

## Summary

Curate is a small, strict, deterministic core that:

* extracts structural facts
* preserves clean abstractions
* scales to new producers and consumers

It is designed to be *boring, predictable, and reusable* — a solid foundation rather than a feature‑rich application.
