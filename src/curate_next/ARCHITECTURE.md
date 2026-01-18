# Curate — Structural Fact Engine

Curate extracts **structural facts** from syntax trees.

Curate answers one question only:

> **“What structural regions exist, and how are they nested?”**

Everything else is *explicitly* out of scope.

Curate is designed to be a **stable, minimal, long-lived intermediate representation (IR)** that higher layers can depend on without fear of semantic drift.

---

## What Curate is NOT

Curate is intentionally **not**:

- an interpreter (no meaning, no execution)
- a docstring classifier
- a query engine or policy layer
- a formatter, linter, or type checker
- a file, folder, or workspace manager
- a semantic analyzer of any kind

Curate does **not** decide what is “important”, “documentation”, “header”, or “noise”.

Those decisions belong strictly to **layers above** Curate.

---

## Mental model: Curate is Mario

Curate should be understood like a **Mario level**.

- The code file is the level.
- Structural blocks are platforms.
- Nesting is vertical movement.
- Sibling scopes are horizontal movement.

Mario can:

- run left/right across sibling structures
- jump up and down between nested structures
- reason about *where* he is structurally

Mario **cannot**:

- understand the story written on a sign
- interpret what an object “means”
- care whether a decoration is important or not

Curate plays the same role:

> It describes **where structure exists**, not **what it means**.

---

## Core responsibilities

Curate does **exactly three things**:

1. **Select a producer**  
   (e.g. Tree-sitter for a given language)

2. **Traverse the syntax tree**

3. **Emit structural facts**

Nothing more.

---

## Core files

`curate_next/` (core)

- `__init__.py`  
  Minimal public surface.

- `facts.py`  
  Structural ontology.  
  Defines *what a fact is*.

- `compile.py`  
  Compilation facade.  
  Selects producer, emits facts.

Everything else (queries, workspaces, interpretation) lives above.

---

## Structural facts

Curate emits **facts, not interpretations**.

Each fact is a `Scope`.

A `Scope` contains:

- `kind`  
  The syntax-tree `node.type`, **verbatim**, producer-defined.

- `start`, `end`  
  **1-based inclusive** line spans.

- `id`  
  A **hierarchical structural address**: `tuple[int, ...]`

No other data is stored.

---

## Hierarchical ids (laminar by construction)

The `id` encodes structure directly.

- The root scope is always:
  ```text
  (0,)
````

* Children append one element:

  ```text
  (0,) → (0, 0) → (0, 0, 1)
  ```

* The parent id is always:

  ```py
  scope.id[:-1]
  ```

### Consequences

Because hierarchy is encoded in the id:

* Parent/child/ancestor relations are **algebraic**
* No index is required for correctness
* Ordering is deterministic
* Laminar structure is guaranteed by construction

Higher layers may add indexes **only as optimizations**, never as sources of truth.

---

## Determinism guarantees

For the same input:

* The same scopes are emitted
* In the same order
* With the same ids
* With the same spans

This makes Curate suitable for:

* caching
* incremental recomputation
* editor integration
* AI context building

---

## Strings and docstrings (important)

Curate **does not classify docstrings**.

Instead:

* All emitted scopes are derived **solely from syntax-tree structure**
* A scope exists *only if the syntax tree describes a structural region*

### Why only certain strings appear

In Python, Tree-sitter represents **docstrings** as:

```text
block
└─ expression_statement
   └─ string
```

This pattern is **structural**, not semantic:

* It occupies space
* It forms its own region
* It is not part of an executable expression

Inline strings such as:

* assignment values
* call arguments
* return values

are nested inside **executable expressions** (`assignment`, `call`, `return_statement`)
and do **not** form independent structural regions.

Curate therefore:

* emits strings that form **standalone structural blocks**
* ignores strings that are merely **expression operands**

This is **not interpretation**.

It is a direct consequence of following the syntax tree *as structure*.

---

### Semantic difference (but not Curate’s concern)

* A docstring block cannot be executed as an expression
  (except via special mechanisms like `doctest`)
* An inline string literal is always part of execution

Curate records this **structural distinction only**.

Whether a string is “documentation”, “header”, or “noise” is decided **later**.

---

## Producers

Curate supports multiple syntax-tree **producers** via a small plugin surface.

A producer must:

* accept `source: str` (+ optional `language: str`)
* emit a `ScopeSet`
* guarantee determinism and laminar structure
* derive facts **only from syntax-tree structure**
* never raise on parse failure
  (fallback to at least a module/root scope)

### Tree-sitter

Tree-sitter is the primary producer because it provides:

* consistent syntax trees
* broad language support
* a unified structural model

Language-specific configuration lives under:

```
curate_next/producers/
```

Rules describe **what counts as a structural region**, not what it means.

---

## Why this responsibility boundary exists

Curate stops **exactly** at structure because:

* Structure is stable
* Semantics are subjective
* Policies change
* Use-cases differ (editor, AI, refactoring, folding, navigation)

By freezing structure at the lowest possible level:

* Higher layers can evolve independently
* No semantic decision becomes irreversible
* The IR remains valid across contexts

Curate is therefore a **foundation**, not a feature.

---

## REPL example

```py
>>> from curate_next import compile_scope_set
>>>
>>> src = """
... \"\"\"
... Module documentation
... \"\"\"
...
... class Foo:
...     \"\"\"
...     Class docstring
...     \"\"\"
...     def bar(self):
...         \"\"\"
...         Function docstring
...         \"\"\"
...         return "inline string"
... """
>>>
>>> scopes = compile_scope_set(source=src, language="python")
>>> for s in scopes:
...     print(s.id, s.kind, s.start, s.end)
```

Output shows:

* module
* class block
* function block
* docstring strings

But **not** inline expression strings.

This is intentional.

---

## Summary

Curate:

* records **where structure exists**
* encodes hierarchy **directly**
* emits **facts only**
* never interprets meaning

Like Mario:

> Curate builds the level.
> Others decide how to play it.
