# Testing Curate

This document describes the testing strategy, structure, and commands used in the
Curate project.

Curate consists of two distinct parts:

- A **Python semantic engine** (editor-agnostic)
- A **Lua / Neovim client** (thin, IO-only adapter)

The test suite reflects this separation.

---

## Overview

The goals of the test suite are:

- Verify **semantic correctness** of folding decisions
- Ensure **strict invariants** (no invalid or overlapping folds)
- Guarantee **deterministic behaviour** (even for fuzz tests)
- Validate **CLI contracts** (JSON schema, error handling)
- Test the **Lua client without requiring Neovim**
- Track **performance characteristics** of core operations

All tests are runnable locally with a single command.

---

## Running All Tests

```bash
make test-all
````

This runs:

1. Python unit, fuzz, property, and benchmark tests (pytest)
2. Lua smoke tests (busted)
3. Lua client harness tests (standalone Lua)

---

## Python Tests

### Structure

```
tests/
├── example_model.py
├── test_cli.py
├── test_engine.py
├── test_engine_fuzz.py
├── test_engine_properties.py
├── test_engine_schema.py
├── test_engine_benchmark.py
├── test_views_and_query.py
├── utils.py
└── conftest.py
```

---

### Example Model

`tests/example_model.py` is a **stable, known input** used across tests.

It intentionally contains:

* Module docstring
* Multiple classes
* Methods with docstrings and bodies
* Multiple scopes in a single file

All tests derive line numbers and expectations from this file.

---

### Unit Tests

Files:

* `test_engine.py`
* `test_views_and_query.py`

These verify:

* Correct entity detection
* Scope resolution
* View generation (minimum / docs / code)
* Fold plans for known cursor positions

These tests use **explicit line numbers** and assert exact semantic behaviour.

---

### Schema & Contract Tests

File:

* `test_engine_schema.py`

Validates that **all engine outputs**:

* Return JSON-serializable payloads
* Use inclusive fold ranges (`start <= end`)
* Never overlap
* Are strictly ordered

This ensures the Python engine is a reliable API for editor clients.

---

### Fuzz / Property Tests (Deterministic)

File:

* `test_engine_fuzz.py`
* `test_engine_properties.py`

These tests:

* Generate many cursor positions
* Cover all actions (`local`, `minimum`, `code`, `docs`)
* Assert invariants (no crashes, no invalid folds)

Important characteristics:

* **Seeded randomness**
* Fully reproducible
* No flaky behaviour

Fuzzing is used to *expand coverage*, not to introduce nondeterminism.

---

### CLI Tests

File:

* `test_cli.py`

Tests the public CLI interface:

* `python -m curate --help`
* Valid file invocation
* Invalid paths
* Invalid actions

Asserts:

* Exit codes
* JSON output on success
* Non-JSON output on error

This locks down the CLI as a stable integration surface.

---

### Benchmarks

File:

* `test_engine_benchmark.py`

Uses `pytest-benchmark` to measure:

* `fold_for_cursor` performance on real input

Benchmarks are run as part of the normal test suite and produce output like:

```
test_toggle_local_benchmark  ~500 µs
```

This provides early warning for accidental performance regressions.

---

## Lua Tests

### Structure

```
tests/lua/
├── busted_helper.lua
├── smoke_spec.lua
├── utils.lua
└── curate/
    ├── client.lua
    └── client_harness.lua
```

---

### Smoke Test (Busted)

File:

* `smoke_spec.lua`

Verifies that:

* The Lua test environment is working
* Busted is correctly installed

This is intentionally minimal.

---

### Lua Utilities

File:

* `tests/lua/utils.lua`

Provides:

* Seeded, deterministic helpers
* Used for fuzz-like iteration in Lua tests

This mirrors the Python-side philosophy.

---

### Lua Client Harness (No Neovim Required)

File:

* `tests/lua/curate/client_harness.lua`

This is the most important Lua test.

It:

* Stubs the minimal `vim` API
* Loads the real `curate.client` module
* Simulates:

  * Cursor movement
  * Fold application
  * Python subprocess calls
  * Error cases
  * Invalid JSON
  * Empty fold results

No Neovim instance is required.

The harness validates that the Lua client:

* Never crashes
* Applies folds correctly
* Clears folds when toggling
* Surfaces Python errors to the user
* Remains stateless and deterministic

---

## Design Principles Behind the Tests

* **Editor-agnostic core**
  Python logic is tested independently of Neovim.

* **Thin Lua layer**
  Lua contains no semantic logic and is tested via stubs.

* **Determinism over randomness**
  All fuzzing is seeded and reproducible.

* **Contracts over implementation**
  Tests assert behaviour and invariants, not internal details.

* **Performance is observable**
  Benchmarks exist alongside correctness tests.

---

## Coverage Notes

Not all modules are fully covered by design.

Lower coverage areas include:

* `render_text`
* `blocks`
* CLI glue code

These are intentionally deprioritized in favour of:

* Engine correctness
* Folding semantics
* Client stability

Coverage is considered **meaningful**, not maximal.

---

## Summary

The Curate test suite provides:

* Strong correctness guarantees
* Deterministic fuzz testing
* Real performance measurements
* Editor-independent validation
* A fully testable Neovim client

All of this is runnable locally with:

```bash
make test-all
```
