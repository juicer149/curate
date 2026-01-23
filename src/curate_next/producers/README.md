# curate_next.producers

`curate_next.producers` defines **producer backends**.

A *producer* is a pure function that converts:

```

(source text, language key) → ScopeSet

```

Producers are **implementation details**.  
Curate core does not interpret, validate, or reason about their output.

---

## Core contract

Every producer MUST obey the following contract:

### Function signature

```python
def build_scope_set(*, source: str, language: str) -> ScopeSet
```

### Guarantees

A producer MUST:

* Always return a `ScopeSet`
* Always include a **root scope**:

  * `address == (0,)`
  * `start == 1`
  * `end >= 1`
* Never mutate input
* Never rely on global state
* Never raise uncaught exceptions to callers

If a producer cannot operate (missing dependency, parse failure, unknown
language, internal error), it must **degrade structurally**, not fail.

---

## Structural, not semantic

Producers:

* MAY use syntax trees (e.g. Tree-sitter)
* MAY load grammars, rules, or schemas
* MAY drop nodes based on structural rules

Producers MUST NOT:

* Assign semantic meaning
* Infer intent
* Apply editor or UX policy
* Depend on files, paths, projects, or workspaces

Curate treats all producers as **black boxes that emit structure**.

---

## Producer selection

Producers are selected by **string key** via the registry:

```python
from curate_next.producers.registry import PRODUCERS
```

Example keys:

* `"treesitter"`
* `"noop"`

Selection happens in `compile_scope_set`.
No producer should contain dispatch logic.

---

## Fallback behavior

Curate defines a mandatory fallback producer:

### `noop`

The `noop` producer:

* Ignores language
* Emits exactly one scope:

  * module-level
  * covering the entire source

This guarantees that **Curate is total**:
there is always a structural result.

Any failure in other producers must degrade to this behavior.

---

## Adding a new producer

To add a new producer:

1. Create a module:

```text
curate_next/producers/my_producer/
```

2. Implement:

```python
def build_scope_set(*, source: str, language: str) -> ScopeSet
```

3. Register it lazily in `producers/registry.py`:

```python
def _my_producer():
    from .my_producer import build_scope_set
    return build_scope_set

PRODUCERS["my_producer"] = _my_producer
```

4. Do **not** modify `compile_scope_set`

If the registry entry exists, the producer is usable.

---

## Design philosophy

> If structure exists, it should be representable.
>
> If structure cannot be derived, return the smallest valid structure.

Producers are **mechanical**, **replaceable**, and **boring by design**.

That is a feature.
