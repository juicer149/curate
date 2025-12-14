# Test Strategy & Guarantees

Curate separates concerns between a Python semantic engine and a thin Lua Neovim client. Tests focus on observable contracts and invariants, not internal implementation.

## Layers

- Python unit tests (pytest): analyzer, views, foldplan, query, engine.
- Lua tests:
  - Smoke (Busted): environment sanity.
  - Client harness (plain Lua): real client behavior with stubbed `vim`.

## Contracts

- JSON schema from `python -m curate`:
  - Payload includes `folds: [{start: int, end: int}, ...]`.
  - `start < end`; ranges are inclusive and non-overlapping.
- Views:
  - `DOCS_ONLY`: shows doc lines (including propagated docstrings).
  - `CODE_ONLY`: hides doc lines.
  - `MINIMUM`: shows only heads of code entities.
- Analyzer docstrings:
  - Head = first 1–2 non-empty lines.
  - Body = remainder after first blank line or after first two lines.
  - Doc lines never belong to code bodies.
- Lua client:
  - Clears folds when already folded.
  - Applies fold ranges via manual folds.
  - Notifies on engine error or invalid JSON.

## Commands

- Run everything: `make test-all`
- Python: `pytest -q`
- Lua smoke: `~/.luarocks/bin/busted tests/lua --pattern=_spec.lua -v`
- Lua harness: `make test-lua-client`

