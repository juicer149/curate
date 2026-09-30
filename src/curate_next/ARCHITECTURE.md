# Curate — Structural Intermediate Representation (IR)

Curate extracts **structural facts** from source code.

Curate answers **one question only**:

> **“What structural regions exist, and how are they nested?”**

Everything else is *explicitly* out of scope.

Curate is designed to be a **stable, minimal, long-lived intermediate representation (IR)**
that higher layers can depend on without fear of semantic drift.

---

## What Curate is NOT

Curate is intentionally **not**:

- an interpreter or evaluator
- a semantic analyzer
- a docstring classifier
- a formatter, linter, or type checker
- a query engine or policy layer
- a file, folder, or workspace manager
- an editor integration

Curate does **not** decide what is:

- “important”
- “documentation”
- “header”
- “noise”
- “context”

All such decisions belong strictly to **layers above** Curate.

---

## Core idea: structure as geometry

Curate treats source code as **geometry**, not meaning.

A code file is understood as a set of **regions**:

- each region spans a contiguous range of lines
- regions may contain other regions
- containment is **laminar**:
  - nested or disjoint
  - never partially overlapping

From this geometry, Curate derives **structural addresses**.

---

## Mental model: Curate is Mario

Curate should be understood like a **Mario level**.

- The source file is the level.
- Structural regions are platforms.
- Nesting is vertical movement.
- Sibling regions are horizontal movement.

Mario can:

- move left/right across siblings
- jump up/down between nested regions
- reason about *where he is structurally*

Mario cannot:

- read the story on a sign
- interpret what an object “means”
- decide whether something is important

Curate plays the same role:

> It describes **where structure exists**, not **what it means**.

---

## Structural addresses (postal codes)

Each structural region is identified by a **hierarchical address**.

An address is a tuple of integers:

```

(0,)
(0, 1)
(0, 1, 0)
(0, 1, 0, 2)

```

Addresses behave like postal codes:

- each prefix identifies a broader enclosing region
- each additional segment narrows the region
- addresses encode **hierarchy**, not identity
- no segment implies meaning, ownership, or importance

The address does **not** describe:

- semantic role
- execution order
- uniqueness across files

It describes **where a region lives structurally**, and nothing more.

---

## Address algebra (invariants)

Addresses form a simple algebra:

- **parent** = remove last segment
- **child** = append an integer
- **ancestors** = successive prefixes
- **descendants** = addresses sharing a prefix

Because hierarchy is encoded algebraically:

- parent/child relations require no indexes
- ordering is deterministic
- laminarity is guaranteed by construction

Indexes may be added by higher layers **only as optimizations**,
never as sources of truth.

---

## Two layers of facts: Raw vs Derived

Curate deliberately separates **observation** from **structure**.

### Raw facts (`RawScope`)

Raw facts are emitted by **producers**.

A `RawScope` contains:

- `label` — producer-defined (e.g. syntax node type)
- `start`, `end` — source positions (`row`, optional `col`)
- optional `meta` payload (opaque to core)

Raw facts:

- may overlap
- may be malformed
- may be incomplete
- carry **no addresses**
- make **no laminar guarantees**

Raw facts represent **what was observed**, not what is structurally valid.

---

### Derived facts (`Scope`)

Derived facts are produced by **core derivation**.

A `Scope` contains:

- `address` — hierarchical structural address
- `label`
- `start`, `end` — **line-based** inclusive spans
- optional `meta` (carried through, not interpreted)

Derived facts guarantee:

- deterministic laminar structure
- contiguous child indices per parent
- valid line spans within the document
- exactly one root scope per file

Derived facts represent **structure**, not observation.

---

## Position handling and projection

Producers may report spans using `(row, col)` precision.

Core **does not reason in two dimensions**.

Instead:

- raw positions are **projected** to line spans:
  - `start_line = start.row`
  - `end_line = end.row`
- laminarity, ordering, and containment are defined **only on lines**

Column precision is preserved in metadata for higher layers
(e.g. cursor matching), but never affects structural derivation.

This projection is intentional and conservative.

---

## Derivation: the structural motor

Core derivation:

- accepts a `RawScopeSet`
- normalizes spans to document bounds
- enforces laminarity via a containment stack
- assigns deterministic addresses
- drops invalid or crossing regions consistently

Derivation is:

- **total** (never raises)
- deterministic
- policy-free
- independent of any syntax tree

Core does **not** know about:
- files
- folders
- workspaces
- editors
- languages

---

## Totality guarantee (important)

`compile_scope_set` is a **total function**.

For any input:

- any source text
- any language key
- any producer key
- any runtime environment

Curate guarantees:

- compilation **always returns a `ScopeSet`**
- a root/module scope is always present
- missing or failing producers never break structure

This is achieved via a first-class fallback producer: **`noop`**.

---

## Producers

Producers are responsible for **emitting raw structural facts**.

A producer must:

- accept `source: str` and `language: str`
- emit a `RawScopeSet`
- never assign addresses
- never enforce laminar policy
- never raise on failure

### No-op producer (structural baseline)

Curate includes a built-in `noop` producer.

The noop producer:

- requires no dependencies
- does not inspect syntax
- emits exactly one raw scope:
  - label: `"module"`
  - span: entire file

This is **not an error case**.

It is a structural baseline that guarantees Curate’s totality
and allows safe use in editors, tests, and constrained environments.

---

## Determinism guarantees

For the same input:

- the same scopes are derived
- in the same order
- with the same addresses
- with the same line spans

This makes Curate suitable for:

- caching
- incremental recomputation
- editor integration
- AI context selection

---

## Workspace and multi-file structure

Curate core operates on **single files only**.

Multi-file and workspace structure is handled by a **separate layer**.

The workspace layer:

- assigns addresses to folders and files
- treats files as parents of module scopes
- prefixes file-level addresses onto core-derived addresses

No changes to core or address algebra are required.

Workspace is a **larger coordinate space**, not a new model.

---

## Why this boundary exists

Curate stops **exactly** at structure because:

- structure is stable
- semantics are subjective
- policies change
- use cases differ (editors, AI, navigation, folding)

By freezing structure at the lowest possible level:

- higher layers can evolve independently
- no semantic decision becomes irreversible
- the IR remains valid across contexts

Curate is therefore a **foundation**, not a feature.

---

## Summary

Curate:

- records **where structure exists**
- encodes hierarchy **algebraically**
- emits **facts only**
- never interprets meaning

Like Mario:

> Curate builds the level.  
> Others decide how to play it.
