# Curate — Structural Logic and Cost Model

This document describes the *logic*, *cost model*, and *design rationale* behind Curate.

It is intentionally separate from ARCHITECTURE.md.

* ARCHITECTURE.md describes **what exists**
* LOGIC.md describes **why it exists this way**

Curate is not optimized for maximal feature coverage or asymptotic micro‑benchmarks.
It is optimized for **minimal structural complexity**, **predictable cost**, and **long‑term correctness**.

---

## Core Principle

> **Minimize what exists before optimizing how fast it runs.**

The fastest operation is the one that never needs to happen.
The most robust invariant is the one that never needs to be maintained.

Curate therefore focuses on:

* minimizing representations
* minimizing invariants
* minimizing hidden state
* concentrating unavoidable cost at construction time

---

## What Problem Curate Solves

Curate answers exactly one question:

> **What structural regions exist, and how are they nested?**

Curate does **not**:

* interpret meaning
* classify semantics
* assign importance
* evaluate execution
* optimize behavior

It extracts *structure* from text and records it as immutable facts.

---

## Structural Units and the Meaning of `n`

All performance characteristics in Curate depend on a single quantity:

> **`n = number of structural scopes`**

Crucially:

* `n` is **not** number of lines
* `n` is **not** number of tokens
* `n` is **not** number of syntax tree nodes

Scopes represent **structural regions that own space**:

* modules
* blocks
* classes
* functions
* control structures (`if`, `for`, `while`, etc.)

As a result:

* `n` grows with *conceptual structure*, not file size
* flat code does not inflate `n`
* deeply nested code increases `n`

In real-world, hand-written code:

* `n < 50` is common
* `n < 100` is typical
* `n > 200` is unusual
* `n > 500` is extremely rare
* `n > 1000` almost always indicates generated or structurally poor code

Structural depth is similarly bounded; deep nesting is a code smell, not a Curate problem.

---

## Laminar Structure by Construction

Curate enforces laminar structure **by construction**, not by validation.

Each scope has a hierarchical tuple ID:

```
(0,)            # root
(0, 0)          # first child
(0, 0, 1)       # second child of that child
```

This encoding guarantees:

* parent/child relations via prefix algebra
* no partial overlaps
* deterministic ordering
* no cycles

No runtime checks are required to maintain these properties.

Correctness is achieved by representation choice, not defensive logic.

---

## Compile-Time vs Query-Time Cost

Curate explicitly separates **construction cost** from **query cost**.

### Construction (Compile Time)

Paid once per input:

* parsing
* syntax tree traversal
* scope extraction
* hierarchical ID assignment
* deterministic ordering

This is the only phase where structure is created.

### Queries (Runtime)

After construction:

* no structure is created
* no caches are mutated
* no invariants are maintained

Queries operate purely over immutable facts.

This separation yields:

* predictable performance
* zero invalidation logic
* clear debugging boundaries
* transparent cost model

---

## Why Relations Are O(n)

All structural relations (`parent`, `ancestors`, `descendants`, etc.) are implemented as linear scans.

This is deliberate.

Given that:

* `n` is small and structurally bounded
* scopes are file‑local
* comparisons are simple tuple and interval checks
* memory access is cache‑friendly

…the constant factors dominate, not asymptotic complexity.

Empirically, these operations execute in microseconds and are suitable for interactive use (editors, AI context selection, navigation).

---

## Why There Are No Indexes in Core

Indexes are not free optimizations.
They are **alternative representations** with their own:

* state
* invariants
* lifecycle
* invalidation rules

Curate core intentionally contains **no indexes**:

* `Scope` and `ScopeSet` are the sole source of truth
* relations are algebraic and verifiable
* no auxiliary state can become stale

If a consumer requires faster queries for a specific workload, indexes may be built **outside Curate**:

* in adapters
* in workspace layers
* in editor‑ or application‑specific code

This keeps Curate minimal while preserving extensibility.

---

## Locality and Hierarchical Cost Containment

Tuple‑based IDs provide **locality by construction**.

Structural cost distributes vertically, not horizontally:

* large functions increase cost *locally*
* deep nesting affects only its subtree
* unrelated files and modules remain unaffected

This ensures:

* poor structure has local cost
* good structure is rewarded
* global performance remains stable

Curate mirrors the project hierarchy directly:

* project → folders → files → scopes

Structural complexity at one level does not leak into others.

---

## Project Structure as a Performance Multiplier

Because Curate reflects structure faithfully, performance correlates with architectural quality:

* well‑structured projects → low `n` at every level
* small files → small local scope sets
* shallow nesting → cheap traversal

This creates a reinforcing effect:

> **Better structure → lower structural cost → better tooling behavior**

This applies to:

* navigation
* context extraction
* tokenization
* AI prompting

Curate does not attempt to normalize or hide poor structure.
It makes it visible and local.

---

## Structural Cost as Signal

Curate treats structural cost as *information*, not noise.

* large files produce larger local `n`
* deeply nested code produces deeper hierarchies
* complexity remains observable

This is intentional.

Curate aligns performance with structural reality rather than masking it with abstraction.

---

## Design Summary

* Structure is extracted once and never mutated
* Complexity is eliminated by representation choice
* Linear traversal is preferred over persistent indexes
* Cost is local, predictable, and transparent
* Extensions may add indexes; core remains minimal

Curate optimizes for **clarity, correctness, and long‑term system health**, not micro‑benchmarked asymptotic performance.

---

> **Curate records where structure exists.
> Others decide what to do with it.**
