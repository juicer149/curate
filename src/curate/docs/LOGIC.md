# Curate Logic Specification

This document defines the **logical model, invariants, and evaluation semantics** of Curate.
It is intentionally independent of implementation details, programming language, and editor integration.

Curate is designed as a **structural reasoning engine**, not an editor plugin.

---

## 1. Core Idea

Curate computes **foldable ranges** from plain text by reasoning about **structure**, not syntax.

The system is built around three ideas:

1. **Facts** describe structure (Prolog-style).
2. **Rules** describe behavior (Lisp-style).
3. **Evaluation** is mechanical and deterministic (C-style).

The editor provides *intent*; Curate provides *decisions*.

---

## 2. Structural Facts (Prolog Analogy)

### 2.1 Scope

A *scope* is a contiguous region of text that owns a semantic body.

Formally:

```
scope(
  id:        Integer,
  parent_id: Integer | null,
  start:     Integer,  // 1-based, inclusive
  end:       Integer,  // 1-based, inclusive
  role:      Role      // "code" | "doc"
)
```

These facts are immutable.

No scope contains policy.
No scope contains editor semantics.
No scope contains language-specific behavior.

### 2.2 Parent Relation

Structure is expressed purely through the parent relation:

```
parent(child_id, parent_id)
```

This induces a tree (or forest with a single root).

### 2.3 Language Independence

Scopes may originate from:

* Python AST
* Markdown headings
* Docstrings
* Tree-sitter
* Any future parser

All such producers must emit the **same shape of facts**.

---

## 3. Derived Facts

Some relations are derived once for efficiency but are still considered facts:

* `by_id: id → Scope`
* `children: parent_id → (Scope, …)`

These are cached, immutable, and side-effect free.

They do not encode policy.

---

## 4. Rules (Lisp Analogy)

Rules describe *how* scopes behave.
They are **data**, not control flow.

A rule set defines, per role:

* How many lines constitute the header
* Whether a scope is navigable

Example (conceptual):

```python
RuleSet(
  header_size = f(scope) -> int,
  navigable   = f(scope) -> bool
)
```

### 4.1 Why Rules Are Data

* They can be injected (dependency injection)
* Multiple rule sets can coexist
* User configuration is possible
* Testing alternative semantics is trivial

Rules must be:

* Pure
* Deterministic
* Side-effect free

Rules must **never**:

* Create scopes
* Change structure
* Parse text

---

## 5. Queries (Prolog Analogy)

Queries operate on facts and derived facts.

They answer questions such as:

* “Which navigable scope contains this line?”
* “What is the ancestor at level *N*?”
* “What are the immediate children of this scope?”

Queries:

* Do not fold
* Do not interpret intent
* Do not apply policy

They only *observe structure*.

---

## 6. Folding Semantics (Policy Evaluation)

Folding is expressed as **set evaluation**.

The result of folding is a **set of ranges**:

```
{ (start, end), (start, end), ... }
```

Order is irrelevant.
Duplicates are irrelevant.
Overlaps are resolved later.

### 6.1 Body Computation

For a scope:

```
body_start = scope.start + header_size(scope)
body_end   = scope.end
```

If `body_start > body_end`, the scope has no foldable body.

### 6.2 Folding Modes

The system defines a neutral axis:

* `"self"`     → fold the selected scope itself
* `"children"` → fold the immediate children of the selected scope

These modes describe **what is targeted**, not how it is displayed.

Future axes (orthogonal) may include:

* code vs docs
* recursive vs shallow
* mixed strategies

---

## 7. Intent Model

The editor sends **intent**, not semantics.

Intent consists of:

```
Intent(
  cursor: Integer,  // sight
  level:  Integer,  // power (repetition)
  mode:   FoldMode  // self | children
)
```

Interpretation:

1. Cursor selects a base scope.
2. Level selects an ancestor.
3. Mode selects a folding policy.

The editor never decides *what* folds.
Curate never decides *why* the user acted.

---

## 8. Evaluation Pipeline

The complete evaluation is:

```
Text
  ↓
Structure Producer
  ↓
Scope Facts
  ↓
Derived Indices
  ↓
Queries + Rules + Intent
  ↓
Set of Ranges
  ↓
Normalization
```

Each step is:

* Pure
* Deterministic
* Testable in isolation

---

## 9. Normalization (C Philosophy)

Normalization is mechanical post-processing:

* Sort ranges
* Merge overlaps
* Enforce start < end

No semantics are introduced here.

This step exists solely to satisfy editor APIs.

---

## 10. Invariants

The following must always hold:

* Structure producers never apply policy
* Rules never inspect language syntax
* Queries never fold
* Folding never traverses arbitrarily
* Engine never decides semantics
* Same input → same output

Violating any invariant is a design error.

---

## 11. Non-Goals

Curate explicitly does **not**:

* Parse or understand language semantics
* Infer meaning from identifiers
* Perform heuristics
* Guess user intent
* Mutate source text

Curate folds **structure**, not text.

---

## 12. Design Summary

* **Prolog** → structure as relations
* **Lisp**   → rules as data
* **C**      → mechanical execution

This separation is intentional and non-negotiable.

---

## 13. Final Note

This document is a **contract**, not documentation.

Implementations may change.
Languages may change.
Editors may change.

The logic described here must not.

---
