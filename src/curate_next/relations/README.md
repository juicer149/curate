# curate.relations

`curate.relations` defines **pure structural relations** over Curate facts.

Relations answer questions such as:

- “What is the parent of this scope?”
- “Which scopes are nested inside this one?”
- “How deep is this scope?”
- “Is this the root?”

They operate **purely on structural addresses** and do not depend on:
- syntax trees
- source text
- languages
- files or folders
- semantic interpretation

---

## Core idea

Curate encodes hierarchy **directly** in `Scope.address`.

Because of this, many structural relationships can be derived
*algebraically*, without indexes, caches, or auxiliary data structures.

`relations` is the layer that exposes those derivations.

---

## Design principles

Relations are:

- **Pure**  
  No mutation, no side effects.

- **Deterministic**  
  Same inputs → same outputs.

- **Interpretation-free**  
  They do not classify, rank, or assign meaning.

- **Index-free by design**  
  Correctness depends only on `Scope.address` invariants.

If a consumer needs faster queries for a specific workload,
indexes can be built **outside Curate**.

---

## Core API (`relations.core`)

The core module exposes **explicit, typed functions**:

```python
parent(scopes, scope)        -> Scope | None
children(scopes, scope)      -> tuple[Scope, ...]
siblings(scopes, scope)      -> tuple[Scope, ...]
ancestors(scopes, scope)     -> tuple[Scope, ...]
descendants(scopes, scope)   -> tuple[Scope, ...]
is_root(scope)               -> bool
depth(scope)                 -> int
```

All functions operate on:

* a `ScopeSet`
* a single `Scope`

They do not maintain state and do not require indexes.

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

Supported relation names can be queried via:

```python
available_relations()
```

This adapter is intentionally minimal:

* no query language
* no chaining
* no predicates

It exists purely to decouple **selection** from **implementation**.

---

## Why not a query language?

Curate deliberately avoids a general query DSL here.

Reasons:

* relations are small and finite
* composition is better handled by the caller
* complexity grows faster than usefulness
* explicit functions are easier to reason about and test

If a higher layer wants a richer query system,
it can be built **on top of this module**.

---

## What this module is NOT

`curate.relations` is **not**:

* a search engine
* a filtering system
* a policy layer
* a semantic analyzer
* a performance-optimized index

It is algebra over structure — nothing more.

---

## Summary

`relations` exists because hierarchy is already encoded.

> If the address tells you everything,
> relations become simple math.

This module keeps that math explicit, small, and honest.
