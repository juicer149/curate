# Curate — Vision

Curate is a **view engine for structured text**: code, documents and, later,
whole repositories.

It turns a file into a set of nested scopes and answers one question well:

> What structural regions exist, and how are they nested?

Everything a reader sees, in an editor or in a model's context window, is
then a *view* of that structure: what to show in full, what to shorten to a
line, what to leave out.

---

## Core Idea

> Code, documents and folders are all hierarchies of regions.
>
> If you can describe them as nested line ranges, you can navigate,
> fold and select them the same way.

```
Text → Facts → Scopes → Plan → View
```

- **Facts** are observations: "lines 22–31 are a function named `discounts`,
  its docstring is on line 23". Many sources may observe the same file.
- **Scopes** are the curated result: nested or disjoint, never crossing,
  each with an address.
- **A plan** decides what to show, for a focus and a budget.
- **A view** is how an adapter shows it: folds in Neovim, a map of a
  codebase, a block of context for a model.

---

## Design Principles

### 1. Structure over text

The core reasons about line ranges, containment and ownership. It never
interprets meaning. This keeps it language-agnostic, editor-agnostic,
predictable and testable.

### 2. Producers observe, curation decides

Producers (tree-sitter today; Python `ast` and LSP later) emit raw facts.
They may overlap, disagree or be incomplete. Curation turns them into one
consistent structure. The same rule applies to relations: several sources
may report that `discounts` calls `subtotal`; curation keeps one edge and
prefers the most reliable source.

### 3. Folding is a view, not a mutation

Folding and selecting never change a file. Unfolding is not undo; it is
switching to another view.

### 4. One navigation language everywhere

The same keys work in a Python function, a class, a Markdown section, and
later a directory or a map of a whole codebase. Only the structure changes.

### 5. A small vocabulary, two scopes of action

Lowercase keys act on the scopes around the cursor, uppercase keys on the
whole file (or map):

| Key | Acts on | Meaning |
|-----|---------|---------|
| `f` | cursor | zoom out: fold the enclosing scope |
| `u` | cursor | zoom back in |
| `F` | file   | fold one level further (outline, then one nesting level at a time) |
| `U` | file   | unfold one level |
| `j` / `k` | file | next / previous visible definition or heading |

Each key moves one way only. Nothing depends on hidden history.

### 6. The engine decides *what*, the editor decides *how*

The engine computes structure and plans. Adapters apply folds, draw maps,
handle keys and own all UI state. No adapter ever computes structure on its
own.

### 7. Minimize what exists

Keep representations, invariants and hidden state few. Pay costs at
construction time. Optimize only what is measured: parsing dominates, and
process start-up is the only cost a user notices.

---

## Layers

Decisions about importance, documentation or context never enter the core.
They live in the layers above it.

| Layer | Contains | Rule |
|-------|----------|------|
| 0. Structural IR | `RawFact` → `ScopeSet`: spans, head line, name, doc span, addresses | geometry and observations only; stateless; no dependencies |
| 1. Relations | symbols (definitions, references, imports), edges between named scopes, edge curation | non-laminar facts, kept beside the IR, never inside it |
| 2. Plan | outline, levels, focus, budget, levels of detail | the only place that decides what matters |
| 3. Workspace | files, ignore rules, cache (SQLite), indexing | all state and I/O |
| 4. Adapters | CLI, Neovim, MCP | how a plan is shown |

A doc span belongs in layer 0: "the docstring is on lines 23–24" is an
observation. Choosing to show it is layer 2.

---

## Where Curate Is Now (0.5 → 0.6)

- tree-sitter producer, one file per language: Python, Markdown
- curation into laminar scopes with addresses, O(n log n)
- head lines: a decorated definition folds from its `def`, decorators stay
  visible
- `curate chain` (path at a line, and the scopes it lies between) and
  `curate outline` (levels, heads)
- Neovim: zoom from the cursor, outline levels for the file, jumps between
  definitions and headings, fold text with the buffer's own highlighting
- tests for the core, the CLI contract and the Neovim adapter, in CI

---

## Where Curate Is Going

### Levels of detail

Every named scope can be shown at a few levels, each costing lines (later
tokens):

```
full  →  header + docs  →  header  →  hidden
```

A scope owns only its own lines: its span minus its children's. A visible
scope always shows its ancestors at least as headers, so a method never
appears without its class.

### Focus and distance

Every view starts from a focus: the named scope at the cursor. Unnamed
scopes (`if`, `for`) belong to the nearest named scope around them. Other
scopes are near or far in two ways:

- **containment**: around and inside the focus, from the scope tree
- **reference**: what the focus uses (calls, imports, constants), in the
  same file or others, as a weighted graph; documentation headings with the
  same name join with a lower weight

### The plan

Given a focus and a budget: start with everything in full. While it does
not fit, take the farthest scopes one level down; when they are headers,
leave them out; then move one step closer. The focus is never shortened.
The result is a list of line ranges with their levels, computed once and
shown in different ways.

### The map (for a person)

A read-only navigation mode, in the spirit of oil.nvim but for structure:

- rows are named scopes: the focus first, then what it contains and uses,
  ordered by distance, each with its file and line
- rows unfold with the same keys as a file (`f`/`u`, `F`/`U`, `j`/`k`)
- a preview on the right shows the selected scope with the plan applied
- `Enter` goes to the scope in its real file and leaves the mode;
  `q` returns exactly to where the map was opened; `.` makes a row the new
  focus
- editing happens in the real files, so nothing is mirrored or synced
- the map is built from a cache that is warmed in the background when files
  are opened, and only changed files are parsed again

### The context (for a model)

The same plan printed as text: the focus in full, nearby scopes as header
and docs, far ones as headers, each excerpt marked with its file and lines.
Served on the command line and as an MCP server.

---

## Roadmap

Each phase is usable on its own and ends in a release.

### Phase 0 — Foundation (0.6.0)

- demo GIFs in the README; release 0.6.0
- ruff and mypy in CI
- split the Neovim adapter into modules (bridge, folds, fold text, zoom,
  outline) with no change in behaviour
- this layer model written into DESIGN.md

### Phase 1 — Names, docs and identity

- `LanguageSpec` gains `name(node)` and `doc(node)`; facts and scopes carry
  `name` and a doc span
- `named_owner` and `qualname` (`Order.discounts`)
- a scope's identity is `file::qualname` (`#2` for duplicates), stable
  across edits, unlike addresses
- `chain` and `outline` report names

### Phase 2 — The plan within one file (0.7.0)

- `plan.py`: own lines, levels of detail, the ancestor rule, degrade
  farthest first
- `curate view FILE --line N --budget 500`
- Neovim: a focus mode that folds the file by the plan

### Phase 3 — Relations within one file

- tree-sitter symbols from the grammar's tags query (`@definition.*`,
  `@reference.call`, `@name`) plus an import query per language
- each symbol owned by its named scope; edges within the file
- the plan's distance combines tree and edges
- `curate symbols FILE` for inspection

### Phase 4 — Workspace and cache

- files from `git ls-files --cached --others --exclude-standard`, plus
  `.curateignore`; a fallback walk outside git
- SQLite through the standard library (`sqlite3`), all SQL in one module:
  tables for files, scopes, symbols and edges; WAL mode; a schema version
- `curate index [FILE ...]`: parse only what changed
- name index and weighted graph: same file, imported module, global match,
  documentation heading; edge curation by source

### Phase 5 — The map on the command line (0.8.0)

- `curate map FILE --line N` returns rows as a tree, with `has_more` and a
  cap per level
- `curate map --expand ID` for one row's children

### Phase 6 — The map in Neovim (0.9.0)

- the map mode as described above, in its own tab
- background indexing on `BufReadPost` and `BufWritePost`, asynchronous,
  one job at a time
- headless tests: `q` restores the cursor exactly, `Enter` lands on the
  right line, rows unfold and fold

### Phase 7 — Python `ast` as a second source

- precise imports and docstrings when a file parses; tree-sitter otherwise
- the same symbol format; edge curation picks the better answer

### Phase 8 — LSP refinement

- the Neovim adapter asks a running language server for
  `callHierarchy/outgoingCalls` and passes the edges to curate, which
  curates them with the highest priority
- silent fallback to tree-sitter and `ast` when no server runs

### Phase 9 — Context for models

- `curate context FILE --line N --budget 500`
- an MCP server with `context` and `map`

### Phase 10 — A long-running process

- `curate serve`: JSON lines over stdin/stdout, started with the map and
  stopped with it, holding parsed trees in memory
- the JSON contract from phase 5 stays the same

### Later

- directories as scopes (folder → file → class → function), so the map
  can start from a repository
- more languages as language files (JavaScript, TypeScript, Lua, HTML, CSS,
  JSON, YAML), and injections (code blocks in Markdown)
- an indentation-only producer for files with no grammar
- a structural motion set: parent, next sibling, first child

---

## Open Decisions

- Does the map start at the focus, or at the focus under its ancestors?
- Are module-level constants enough, as the tags query gives them?
- Is the budget a setting or a per-call argument?
- Line budget first; when do tokens replace lines?

---

## Prior Art

- **aider's repository map** ranks tree-sitter tags with PageRank and fits
  a token budget.
- **Zed's multibuffers** show excerpts of many files in one editable buffer.
- **oil.nvim** treats a directory as an editable buffer.
- **Emacs narrowing** and **NrrwRgn** show a region of a file on its own.

Curate's part is the combination: levels of detail per scope, ordered by
distance in both the scope tree and the reference graph, with one plan
driving folding, navigation and model context.

---

## What Curate Is Not

Curate is not an IDE, a language server, a formatter, a code generator or a
project manager.

Curate does not:

- infer types (it may ask a language server that does)
- rename symbols or edit code; the map only shows
- manage git state

The core stays narrow on purpose. Everything that decides, remembers or
displays lives in a layer above it.

---

## Why Curate Exists

Editors expose plenty of structure, but each feature invents its own
navigation language: outlines, symbol pickers, folds, reference lists. Models
receive code as files, cut at arbitrary lines.

Curate offers one abstraction, one set of motions, one way to zoom in and
out, and one plan that serves a person and a model alike.

---

## Philosophy

> Everything is text.
>
> Text has structure.
>
> Structure defines view.
