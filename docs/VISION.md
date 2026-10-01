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
- resolves every scope containing the cursor, innermost first
- returns their line ranges; the editor decides what to fold

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

### v1 — tree-sitter, zoom folding, outline (current)

**Done**

- tree-sitter producer, one file per language (Python, Markdown)
- language-free core: laminar selection and addresses in O(n log n)
- `at` / `chain` queries and the `curate chain` CLI
- `curate outline`: the file's skeleton, with each language deciding which
  scopes show (first step of a visibility plan)
- Neovim plugin: fold outward scope by scope, unfold inward, fold to the
  outline; fold text shows the line with its own highlighting and a count

**Next**

- more languages: one file each in `producers/treesitter/languages/`
  (HTML, CSS, JavaScript, JSON, YAML)
- a summary in the fold text: a function's docstring, a section's first
  sentence; the same "name + one line" a RAG context needs
- a visibility plan: decide what to show, not only what to hide

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

A first prototype exists in git history (`git show 6195b54:src/curate_next/`):
a container tree in the same address space as scopes (folder → file → module),
and filesystem ingest with pluggable path rules (gitignore, binary files,
manifest). It was removed because it no longer matched the core; the ideas are
the starting point for this step.

---

### v3 — More languages, and a fallback

Tree-sitter turned out to be the right backend from the start, so the
original plan (heuristic backends first, real parsers later) collapsed into
one step: a language is a file in `producers/treesitter/languages/`.

- HTML, CSS, JavaScript, JSON, YAML as language files
- injections: JavaScript in `<script>`, CSS in `<style>`, code blocks in
  Markdown, parsed with their own grammar
- an indentation-only producer for files with no grammar, so every file has
  some structure

The engine interface does not change; only producers are added.

---

### v4 — Structure as context

The same scopes that fold a file can choose what a reader, human or model,
needs to see.

- a summary per scope: name plus first docstring line or sentence
  (first shown in fold text)
- context selection for RAG: the scope at hand in full, its ancestors as
  names and summaries, siblings as names only
- workspace addresses from v2, so a scope is addressable across a project
- a long-running process holding parsed trees, when per-call start-up
  starts to matter

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
