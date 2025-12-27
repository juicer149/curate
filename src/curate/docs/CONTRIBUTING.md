# Contributing to Curate

Thank you for your interest in contributing to **Curate**.

Curate is not a typical editor plugin.
It is a **structural reasoning engine** with strict architectural boundaries.

This document explains **how to contribute without breaking the design**.

---

## 1. Core Philosophy (Read This First)

Curate is built on a deliberate separation of concerns:

* **Structure is fact**
* **Behavior is rule**
* **Evaluation is mechanical**

This maps directly to three traditions:

* **Prolog** — structure as relations
* **Lisp** — rules as data
* **C** — deterministic execution

If a contribution blurs these boundaries, it will not be accepted.

---

## 2. Architectural Layers

Before writing code, understand where it belongs.

```
Text
 ↓
Structure Producers        (language-specific)
 ↓
Scope Facts               (language-agnostic)
 ↓
Derived Indices            (cached relations)
 ↓
Queries + Rules + Intent   (language-agnostic)
 ↓
Set of Fold Ranges
 ↓
Normalization              (mechanical)
```

Each layer has strict responsibilities.

---

## 3. What You May Contribute

### 3.1 Structure Producers (Most Welcome)

Examples:

* Markdown producer
* Tree-sitter producer
* Comment-based structure
* Documentation-specific parsers

**Rules:**

* Producers may parse text.
* Producers may emit scopes and parent relations.
* Producers must NOT implement folding logic.
* Producers must NOT inspect editor intent.

File location:

```
curate/producers/
```

---

### 3.2 Rules (Policy as Data)

Rules define *how scopes behave*, not *what scopes are*.

Examples:

* Different header sizes
* Alternative navigation semantics
* Doc-only folding
* Editor-specific policies

**Rules must:**

* Be pure (no side effects)
* Be deterministic
* Be passed explicitly (dependency injection)

**Rules must NOT:**

* Parse text
* Traverse scope trees
* Inspect AST nodes

File location:

```
curate/rules.py
```

---

### 3.3 Queries (Relations Only)

Queries answer structural questions:

* Which scope contains this line?
* What is the ancestor at level N?
* What are the children of this scope?

**Queries must NOT:**

* Apply folding policy
* Inspect editor intent
* Depend on language-specific details

File location:

```
curate/query.py
```

---

### 3.4 Folding Policy

Folding translates *facts + rules* into *sets of ranges*.

**Rules:**

* Folding returns a SET, not a list
* Order is irrelevant
* No traversal logic beyond immediate relations

**Folding must NOT:**

* Perform normalization
* Inspect source text
* Parse syntax

File location:

```
curate/folding.py
```

---

### 3.5 Engine and Normalization

These are mechanical layers.

**Engine:**

* wires components together
* performs no semantic decisions

**Normalization:**

* sorts ranges
* merges overlaps
* enforces invariants

Contributions here should be rare.

---

## 4. What You Must NOT Do

The following changes will be rejected:

* Adding `if kind == "function"` logic to folding
* Importing global rules instead of injecting them
* Making editors or file formats visible to core logic
* Adding heuristics (“probably”, “guess”, “try”)
* Making folding depend on syntax details
* Introducing mutable global state

Curate is intentionally **not clever**.

---

## 5. Tests and Contracts

### 5.1 Tests Are Contracts

Tests describe **observable behavior**, not implementation details.

If you change tests:

* You are changing the contract.
* Justify it explicitly in the PR.

### 5.2 Required Tests for Contributions

* New producers → structural tests
* New rules → rule-level unit tests
* New policies → folding tests

No contribution is accepted without tests.

---

## 6. Dependency Injection Is Mandatory

If your change introduces:

* configuration
* variation
* alternatives

Then the dependency **must be explicit**.

Example (good):

```python
evaluate(graph, idx, rules, intent)
```

Example (bad):

```python
from rules import DEFAULT_RULES
```

---

## 7. Naming and Style Guidelines

* Prefer **nouns** for data (`Scope`, `Intent`)
* Prefer **verbs** for queries (`select_scope_at_line`)
* Avoid overloaded terms (“smart”, “advanced”, “magic”)
* Use explicit names over short ones

Clarity beats brevity.

---

## 8. How to Propose Design Changes

For non-trivial changes:

1. Open an issue
2. Describe:

   * Which layer is affected
   * Which invariant is preserved
   * Which invariant is changed (if any)
3. Reference `LOGIC.md`

Large refactors without discussion will be rejected.

---

## 9. Code Review Expectations

Pull requests are evaluated on:

* Architectural correctness
* Clarity of responsibility
* Preservation of invariants
* Test coverage
* Long-term maintainability

Performance matters, but **correctness and clarity come first**.

---

## 10. Mental Model to Keep in Mind

When contributing, always ask:

* Is this a **fact**, a **rule**, or an **evaluation**?
* Am I introducing knowledge at the wrong layer?
* Would this still make sense if the language was not Python?

If you cannot answer these questions clearly, pause and reconsider.

---

## 11. Final Note

Curate values:

* Boring correctness
* Explicit design
* Long-lived abstractions

It intentionally avoids:

* clever hacks
* hidden behavior
* implicit coupling

If this resonates with you, your contributions are very welcome.

---

*Structure over syntax.
Rules over heuristics.
Clarity over convenience.*
