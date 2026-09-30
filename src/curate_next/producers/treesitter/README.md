# Tree-sitter producer

This directory implements the **Tree-sitter producer backend** for Curate.

The Tree-sitter producer:

- parses source text using Tree-sitter
- walks the syntax tree
- emits **raw structural observations** (`RawScope`)
- does NOT derive hierarchy, laminarity, or addresses

All structural derivation happens in Curate core.

---

## Responsibilities

The Tree-sitter producer is responsible for:

- loading a Tree-sitter grammar
- traversing the syntax tree
- identifying syntax nodes that represent **structural regions**
- emitting raw spans using `(row, col)` positions

It is NOT responsible for:

- assigning addresses
- enforcing laminar structure
- sorting scopes
- creating root/module scopes
- handling files, folders, or workspaces
- interpreting semantics

---

## Output

The producer emits a `RawScopeSet` containing zero or more `RawScope` values.

Each `RawScope` contains:

- `label`: syntax node type (verbatim)
- `start`: `Position(row, col)`
- `end`: `Position(row, col)`
- optional `meta` payload (opaque to core)

Raw scopes may overlap and may be incomplete.

---

## Language configuration

Language-specific behavior is defined via JSON files under:

```

curate_next/producers/treesitter/languages/

```

Each `*.lang.json` file specifies:

- which node types to include
- which to exclude
- whether only multiline nodes should be emitted

These rules describe **structural shape**, not meaning.

---

## Failure and degradation

If Tree-sitter:

- is not installed
- fails to load a grammar
- fails to parse source text
- encounters an internal error

The producer MUST:

- return a valid `RawScopeSet`
- degrade structurally (possibly empty)

It MUST NOT raise exceptions to the caller.

Structural totality is guaranteed by Curate’s fallback `noop` producer,
not by Tree-sitter itself.
