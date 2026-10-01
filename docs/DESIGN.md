# Curate — core design

Curate is a small core library for deriving **structural hierarchy**
from unstructured or semi-structured sources.

It provides a **conservative structural intermediate representation (IR)**
that sits between *observation* (parsers, scanners, analyzers)
and *consumption* (editors, analysis, navigation, AI context selection).

Curate is intentionally **not a framework**.
It models structure explicitly, minimally, and deterministically.

---

## Design principles

Curate is built around a strict separation of concerns:

- **Representation** — what structure *is*
- **Observations** — what has been *seen*
- **Policy** — how conflicting observations are *resolved*
- **Derivation** — what can be *computed* from accepted structure

These concerns are separated at the module level.
Only one module (`curation`) is permitted to make structural decisions.

Key goals:

- deterministic behavior
- explicit invariants
- minimal internal state
- no hidden coupling
- suitability as a stable, long-lived structural IR

Indexing, caching, optimization, traversal helpers,
and domain interpretation are intentionally left to consumers.

---

## Structural representation

### Address (hierarchy)

Curate represents hierarchy using **addresses**, not explicit trees.

An `Address` is a tuple of non-negative integers:

```text
()        → root
(0)       → first child of root
(0, 2)    → third child of first child
```

Hierarchy is **implicit**, defined purely by prefix relations:

* ancestry is prefix inclusion
* sibling order is explicit
* parent/child relations are algebraic
* no pointers or stored relations exist

Addresses are immutable value objects and are the *only*
representation of hierarchy in Curate.

Conceptually similar to:

* outline numbering (1, 1.2, 1.2.3)
* filesystem paths
* prefix-based coordinate systems

---

### Span (geometry)

Curate models structure over sources using **spans**.

A `Span` is a **closed, inclusive interval** over integer coordinates:

```text
[start, end]
```

Spans support:

* containment
* overlap detection
* length computation

Geometry is **purely mathematical**.
It encodes no hierarchy, syntax, or semantics.

The coordinate system itself (lines, bytes, tokens, character offsets, etc.)
is defined by producers, not by Curate.

---

## Observations vs structure

Curate distinguishes strictly between **observed data**
and **derived structure**.

### Raw facts (observations)

Raw facts represent *claims* about structure, not truth.

Defined in `facts.py`:

* `RawFact`

  * `label`
  * `span`
* `RawFactSet`

  * unordered collection of observations

Properties:

* may overlap
* may contradict each other
* may be incomplete
* may be empty

Raw facts:

* do **not** form a tree
* carry no hierarchy
* carry no guarantees

They are input data only.

---

### Scopes (curated structure)

Scopes are the result of curation.

Defined in `facts.py`:

* `Scope`

  * `address`
  * `label`
  * `span`
* `ScopeSet`

  * immutable, internally consistent structure

Properties:

* spans are **laminar**
* addresses are unique
* sibling indices are contiguous per parent (starting at 0)
* hierarchy is implicit via address prefixes

Scopes are **derived artifacts** and are never emitted directly
by producers.

---

### Structural axiom: parenthood

Curate enforces a strict geometric axiom for hierarchy:

> A scope may be the parent of another scope **if and only if**
> the parent’s span fully contains the child’s span.

Formally:

```text
parent.span ⊇ child.span
```

This axiom is fundamental.

Implications:

* Hierarchy represents **total geometric ownership**
* Partial overlap is **never** a parent–child relation
* Containment is not merely allowed — it is **required** for hierarchy
* Parent–child relations cannot lie

This invariant is enforced:

* during curation (address assignment selects the deepest containing parent)
* by validation (illegal hierarchies are rejected)
* by tests (both positive and negative cases)

As a result:

> If a scope is a child, then it is fully contained. Period.

Other relationships (traits, overlays, mixins, cross-cutting concerns)
may overlap geometrically but **must not** be encoded as hierarchy.
Such relationships belong in separate semantic or relational layers.

---

## Laminarity (important)

Curate uses **laminar structure** as its core geometric constraint.

Given two spans `A = [a,b]` and `C = [c,d]`,
they are considered *laminar-compatible* if:

* they are **disjoint**, or
* one **fully contains** the other (nesting)

Spans are **not compatible** if they:

* partially overlap without containment
  (“crossing intervals”)

### Consequences

* Nesting is **allowed and preserved**
* Hierarchical structure can emerge from containment
* Crossing observations are rejected by policy
* Laminarity is enforced *before* address assignment

This allows Curate to derive deep hierarchies
without storing explicit trees or relations.

---

### Duplicate span policy

If two observations have **exactly identical geometry**
(i.e. the same `[start, end]`):

* they are treated as **conflicting**
* only the first accepted observation is kept
* later duplicates are dropped deterministically

This avoids artificial nesting chains such as:

```text
A → A → A
```

when multiple producers report the same structural region.

This behavior is **policy**, not a representational invariant.

---

## Policy layer (curation)

Curation is the **only place** where Curate makes structural decisions.

Defined in `curation.py` and `policy.py`.

Responsibilities:

1. **Laminar selection**
   Select a subset of raw facts that are mutually laminar
   (allowing nesting, rejecting crossings and duplicates).

2. **Root derivation**
   Derive a single root scope that covers all accepted structure.

3. **Address assignment**
   Assign deterministic addresses based on geometric containment.

4. **ScopeSet construction**
   Produce an immutable, internally consistent structural result.

Important notes:

* Laminar selection is a *policy decision*, not pure mathematics
* Address assignment is deterministic
* Structural invariants are established by construction
* Alternative policies are possible in principle
* No other module may introduce structural choices

---

## Root scope and coordinate systems

The root scope is derived conservatively.

* If curated facts exist:
  the root span is the **minimal span covering all facts**:

  ```text
  [min(start), max(end)]
  ```

* If no facts exist:
  a degenerate span `[1, 1]` is used

Curate does **not** assume any particular coordinate system
beyond what producers supply.

---

## Derived relations

Relations are **computed**, not stored.

Defined in `relations/relations.py`.

Examples:

* parent
* children
* ancestors
* descendants
* `at(scopes, line)`: the deepest scope containing a line
* `chain(scopes, line)`: every scope containing a line, innermost first
  (what the Neovim adapter folds, level by level)

All relations are derived solely from:

* `Scope.address`
* prefix algebra over `Address`

Properties:

* pure functions
* no mutation
* no indexes
* no caching

Some relation helpers rely on core invariants
(e.g. contiguous sibling indices).
Violating those invariants results in undefined behavior.

Consumers requiring faster traversal or lookup
are expected to build derived indexes externally.

### Outline

`outline_folds(scopes, kinds)` in `outline.py` is the first view built on
these relations: the line ranges to fold so that only a file's skeleton
shows. It stays language-free; the caller passes which labels are outline
entries and whether each is `"open"` (its header and the entries inside it
show) or `"closed"` (folded whole). Language files supply those kinds.

---

## Producers (adapters)

Producers adapt external systems into raw facts.

Defined in `producers/`.

Producer contract:

* emit `RawFactSet`
* may return empty results
* do not assign structure
* do not inject roots

Producers may fail (a missing grammar, say). `compile_scopes` catches
the error, reports it through `on_error`, and falls back to no facts,
so compilation itself is total.

Included:

* `treesitter` — one file per language under `languages/`, each with a
  `LanguageSpec` mapping node types to scope labels (Python, Markdown);
  a language may add its own labelling rule, as Markdown does for
  heading levels; tree-sitter is imported lazily
* `noop` — emits no facts; the guaranteed fallback

Other producers (regex scanners, AST adapters, domain extractors)
plug into the same registry.

---

## The pipeline

Curate’s pipeline is linear and explicit:

```text
external system
      ↓
   producer
      ↓
  RawFactSet
      ↓
   curation
      ↓
   ScopeSet
      ↓
relations / consumers
```

Key properties:

* no hidden state
* no backchannels
* no implicit coupling
* each stage has a single responsibility

The helper in `compile.py` exists solely to compose this
pipeline conveniently.

---

## What Curate does *not* model

Curate intentionally excludes:

* syntax
* semantics
* meaning
* language rules
* filesystems
* editors
* UI concerns
* AI models

Those systems operate *around* Curate, not inside it.

---

## Why this separation matters

Because structure is:

* stable across tools
* independent of interpretation
* reusable across domains

The same `ScopeSet` can power:

* editor folding
* outlines
* cursor focus
* visibility planning
* AI context selection

without knowing *why* those consumers exist.

---

## Status

The core, the tree-sitter producer, the `curate chain` CLI and the
Neovim adapter (`adapters/nvim`) live in this repository. Filesystem
ingestion and AI context selection are planned layers on top; see
[VISION.md](VISION.md).
