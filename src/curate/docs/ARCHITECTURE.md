# ARCHITECTURE.md

## Overview

Curate is a structural analysis engine for source code.
Its core responsibility is to reduce source text into **nested scopes**, and to apply user intent as deterministic operations over this structure.

Curate deliberately avoids syntax-specific, editor-specific, or language-specific semantics in its core.
All intelligence is expressed in terms of **scopes, ownership, and containment**.

Folding is the first consumer of this model, not its defining feature.

---

## Core Abstraction: Scopes

The fundamental abstraction in Curate is the **scope**.

A scope represents a contiguous interval of source lines that are logically owned by a single structural entity (e.g. module, class, function, docstring).

Formally, a scope is defined as:

```
Scope = (id, parent_id, start_line, end_line, role)
```

Where:

* `start_line` and `end_line` define a **closed interval** of line numbers
* `parent_id` establishes ownership
* `role` classifies the scope (e.g. code, documentation)

A scope contains *no behavior*.
It is an inert fact.

---

## Scopes as Sets

Each scope corresponds to a finite set of line numbers:

```
S = { start, start+1, …, end }
```

All structural reasoning in Curate is based on **set inclusion**, not syntax.

This allows Curate to abstract away:

* indentation
* AST shape
* token-level structure

These mechanisms exist only to *produce* scopes, not to reason about them.

---

## Laminär Structure (Non-Overlapping Invariant)

All scopes in a file form a **laminar family of sets**.

For any two scopes A and B, exactly one of the following holds:

* A ⊂ B
* B ⊂ A
* A ∩ B = ∅

Partial overlap is forbidden.

This invariant guarantees:

* deterministic parent relationships
* tree-shaped navigation
* predictable folding behavior

The `ScopeGraph` is therefore a tree (with an explicit root scope).

---

## Ownership and Containment

Ownership is defined purely by **set inclusion**.

If:

```
child ⊂ parent
```

then the parent scope owns the child scope.

There is no concept of “siblings by syntax” or “blocks by indentation” in the core model.
Only containment matters.

---

## Documentation as Sub-Scopes

Documentation (e.g. docstrings) is modeled as **normal scopes with a distinct role**.

This enables:

* logical LOC = physical LOC − documentation scopes
* folding policies that treat documentation differently
* zero special cases in the engine

All distinctions are expressed via rules, not structural hacks.

---

## ScopeGraph: Fact Database

The `ScopeGraph` is an immutable container for all scopes in a file.

It represents a **fact database**, not a semantic model.

Responsibilities:

* store scopes
* preserve laminar invariants
* provide a stable base for indexing and querying

The graph itself performs no interpretation.

---

## Indexing and Queries

Indexes (e.g. parent lookup, children lookup) are derived mechanically from the `ScopeGraph`.

Queries such as:

* “children of this scope”
* “smallest scope containing this line”

are pure operations over facts.

They do not encode folding behavior, navigation intent, or editor semantics.

---

## Intent: User Interaction Model

User interaction is expressed as **intent**, not commands.

```
Intent = (cursor_line, level, mode)
```

Where:

* `cursor_line` identifies a position in the source
* `level` describes upward traversal in the ownership hierarchy
* `mode` selects the operation (`self`, `children`, etc.)

Intent is editor-agnostic and language-agnostic.

---

## Rules: Policy as Data

All folding semantics are expressed as **rules**, not control flow.

Rules define:

* which scopes are navigable
* which scopes are foldable
* how headers relate to bodies

Rules are immutable, explicit, and passed as values.

Changing behavior means changing rules, not engine logic.

---

## Engine: Deterministic Application

The engine coordinates:

1. structure production
2. indexing
3. intent evaluation
4. rule application
5. output normalization

It never makes semantic decisions.

The engine is a referee, not a player.

---

## Adapters

Adapters (CLI, Neovim, etc.) are responsible for:

* collecting external state
* translating it into intent
* invoking the engine
* applying results in the host environment

Adapters do not interpret scopes or rules.

Python is the source of truth.

---

## Design Principles

* Facts are inert; intelligence lives elsewhere
* Policy is data, not control flow
* Structure precedes behavior
* Silence is better than guessing
* Adapters translate intent; they do not contain logic

---

## Summary

Curate reduces source code to a laminar family of line-interval scopes.

All higher-level behavior emerges from applying intent and rules to this structure.

This model is:

* language-agnostic
* editor-agnostic
* mathematically well-defined
* resistant to feature creep

Folding is an application.
The scope model is the system.
