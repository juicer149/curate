# curate_next.producers

`curate_next.producers` defines **producer backends**.

A *producer* is a pure function that converts:

```

(source: str, language: str) → RawScopeSet

```

Producers emit **raw structural observations**.
They do **not** derive structure, hierarchy, or addresses.

Producers are **implementation details**.
Curate core treats all producers as **opaque sources of raw facts**.

---

## Core contract (important)

Every producer MUST obey the following contract.

### Function signature

```python
def build_raw_scope_set(*, source: str, language: str) -> RawScopeSet
```

### Guarantees

A producer MUST:

* Always return a `RawScopeSet`
* Never raise uncaught exceptions to the caller
* Never assign structural addresses
* Never enforce laminarity
* Never depend on global or workspace state
* Never mutate input

If a producer cannot operate (missing dependency, parse failure,
unknown language, internal error), it MUST **degrade structurally**,
not fail.

Structural degradation means:

> Return the smallest valid set of raw structural facts.

---

## Raw facts, not structure

Producers emit **raw facts** (`RawScope`), not derived structure.

A `RawScope` contains:

* `label` — producer-defined (e.g. syntax node type)
* `start`, `end` — source positions (`row`, optional `col`)
* optional `meta` — opaque payload for higher layers

Raw facts:

* may overlap
* may be incomplete
* may be malformed
* carry **no addresses**
* make **no laminar guarantees**

Curate core is responsible for:

* enforcing laminarity
* assigning addresses
* normalizing spans
* deriving structure

---

## Structural, not semantic

Producers:

* MAY use syntax trees (e.g. Tree-sitter)
* MAY load grammars, rules, or schemas
* MAY drop nodes based on **structural rules**

Producers MUST NOT:

* Assign semantic meaning
* Infer intent
* Apply editor or UX policy
* Decide importance
* Reason about files, folders, or workspaces

Curate treats producers as **mechanical extractors of structure**.

---

## Producer selection

Producers are selected by **string key** via the registry:

```python
from curate_next.producers.registry import PRODUCERS
```

Example keys:

* `"treesitter"`
* `"noop"`

Selection happens exclusively in `compile_scope_set`.

No producer should contain:

* dispatch logic
* fallback logic
* environment detection

---

## Fallback behavior (noop)

Curate defines a mandatory fallback producer:

### `noop`

The `noop` producer:

* requires no external dependencies
* ignores language
* emits exactly one raw scope:

  * `label = "module"`
  * `start = Position(1)`
  * `end = Position(total_lines)`

This is **not an error case**.

It is a first-class structural baseline that guarantees Curate’s
**totality**.

Any failure in other producers must degrade to this behavior.

---

## Adding a new producer

To add a new producer:

1. Create a module:

```
curate_next/producers/my_producer/
```

2. Implement:

```python
def build_raw_scope_set(*, source: str, language: str) -> RawScopeSet
```

3. Register it lazily in `producers/registry.py`:

```python
def _my_producer():
    from .my_producer import build_raw_scope_set
    return build_raw_scope_set

PRODUCERS["my_producer"] = _my_producer
```

4. Do **not** modify `compile_scope_set`

If the registry entry exists, the producer is usable.

---

## Design philosophy

> If structure exists, it should be representable.
> If structure cannot be derived, return the smallest valid structure.

Producers are **mechanical**, **replaceable**, and **boring by design**.

That is a feature.
