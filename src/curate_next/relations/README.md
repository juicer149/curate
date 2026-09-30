# curate_next.relations

`curate_next.relations` defines **pure structural relations** over Curate facts.

Relations answer questions such as:

- “What is the parent of this scope?”
- “Which scopes are directly nested inside this one?”
- “Which scopes are descendants?”
- “How deep is this scope?”
- “Is this the root?”

They operate **purely on structural addresses** and depend only on:

- `Scope.address`
- `ScopeSet` invariants

They do NOT depend on:

- syntax trees
- source text
- languages
- producers
- files or folders
- semantic interpretation

---

## Core idea

Curate encodes hierarchy **directly** in `Address`.

Because of this:

- parent/child relationships are algebraic
- ancestor/descendant queries are prefix checks
- no auxiliary indexes are required for correctness

`relations` is the layer that exposes this algebra.

---

## Design principles

Relations are:

- **Pure**
  No mutation, no side effects.

- **Deterministic**
  Same inputs → same outputs.

- **Interpretation-free**
  They do not classify, rank, or assign meaning.

- **Invariant-driven**
  Correctness relies on core invariants
  (e.g. contiguous child indices, unique addresses).

If a consumer needs faster queries for a specific workload,
indexes may be built **outside Curate** as optimizations.

---

## Core API (`relations.core`)

The core module exposes **explicit, typed functions**:

```python
parent(scopes, scope)        -> Scope | None
children(scopes, scope)      -> tuple[Scope, ...]
ancestors(scopes, scope)     -> tuple[Scope, ...]
descendants(scopes, scope)   -> tuple[Scope, ...]
is_root(scope)               -> bool
depth(scope)                 -> int
```

All functions operate on:

* a `ScopeSet`
* a single `Scope`

They do not maintain state and do not build indexes.

---

## Dispatch adapter (`relations.dispatch`)

For dynamic use-cases (CLI, UI, LSP, config-driven systems),
`relations.dispatch` provides a **string-based adapter**:

```python
relation(scopes, scope, name: str)
```

Example:

```python
relation(scopes, scope, "ancestors")
relation(scopes, scope, "children")
```

This adapter exists solely to decouple **selection** from **implementation**.

---

## Non-goals

`curate_next.relations` is NOT:

* a query language
* a search engine
* a filtering system
* a policy layer
* a semantic analyzer
* a performance-optimized index

It is algebra over structure — nothing more.

---

## Summary

Because hierarchy is already encoded:

> If the address tells you everything,
> relations become simple math.

This module keeps that math explicit, small, and honest.
