# Curate — Vision

Curate is a **structural navigation and folding system** for code and files.

It treats **everything as scoped text** and allows the user to move between
different *views* of that structure using a small, consistent set of commands.

Curate is not a file explorer.  
It is not a formatter.  
It is not a language server.

Curate is a **view engine**.

---

## Core Idea

> Code, files, and folders are all hierarchical structures.
>
> If you can describe them as spans, you can navigate them the same way.

Curate reduces all inputs to the same abstraction:

```

Text → Structure → Spans → View

```

Everything else follows from this.

---

## Design Principles

### 1. Structure over text

Curate never reasons about characters, tokens, or syntax in the editor.

It operates only on:

- line ranges
- parent / child relationships
- ownership of scopes

This makes the engine:

- editor-agnostic
- language-agnostic
- predictable
- testable

---

### 2. Folding is a view, not a mutation

Folding does **not** change the file.

It changes how much of the structure is currently visible.

Unfolding is not undo — it is switching views.

There is no hidden state.

---

### 3. One navigation language everywhere

The same mental model applies to:

- a Python function
- a class
- a module
- a directory
- a project tree

The user does not learn new commands for new domains.

Only the structure changes — the navigation does not.

---

### 4. Minimal command vocabulary

Curate intentionally uses very few concepts:

| Concept | Meaning |
|------|-------|
| fold | hide structure |
| view | reveal structure |
| level | move up the hierarchy |

Everything else is composition.

---

### 5. The engine decides *what*, the editor decides *how*

Curate’s engine:

- understands structure
- computes spans
- returns fold ranges

The editor client:

- applies folds
- handles keymaps
- owns UI and interaction

The boundary is explicit and stable.

---

## Architecture

### Engine (Python)

The engine:

- parses source input
- builds a tree of structural nodes
- resolves the smallest node covering the cursor
- returns line ranges to fold

The engine:

- is stateless
- does not cache editor state
- does not depend on Neovim

It can be run:

- from the CLI
- from Neovim
- from any other editor

---

### Client (Editor glue)

The editor client:

- sends text and cursor position
- requests a semantic action
- applies returned fold ranges

The client never:

- reinterprets structure
- duplicates engine logic
- guesses spans

---

## Version Roadmap

### v1 — Python AST Folding (current)

**Scope**

- Python only
- AST-based structure
- Node types:
  - module
  - class
  - function
  - docstring

**Intent**

- prove the model
- lock command semantics
- validate performance and UX

No filesystem integration.

---

### v2 — Filesystem as structure

Folders and files become first-class scopes.

- directories behave like parent nodes
- files behave like leaf scopes
- `__init__.py` and README files may act as doc nodes
- folding from the top of a file may exit to a directory view

This creates a unified navigation surface for:

- code
- projects
- repositories

---

### v3 — Generic language backends

Introduce heuristic backends for non-Python files:

| Type | Strategy |
|----|---------|
| Markdown | headings |
| YAML | indentation |
| JSON | braces |
| Unknown | indentation-only |

These backends prioritize:

- speed
- predictability
- correctness over completeness

---

### v4 — Full multi-language support

Replace heuristics with proper parsers:

- Tree-sitter
- language-native ASTs

The engine interface does not change.  
Only the backend does.

---

## What Curate Is Not

Curate is not:

- an IDE
- a replacement for LSP
- a formatter
- a code generator
- a project manager

Curate does not:

- infer types
- rename symbols
- modify code
- manage git state

It is intentionally narrow.

---

## Why Curate Exists

Modern editors expose powerful structure,
but each feature invents its own navigation language.

Curate provides:

- one abstraction
- one set of motions
- one way to zoom in and out

It is designed for users who:

- think in scopes
- navigate by structure
- want fewer modes, not more

---

## Philosophy

> Everything is text.
>
> Text has structure.
>
> Structure defines view.
