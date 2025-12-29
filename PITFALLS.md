# Curate – Design Notes & Known Pitfalls

This document records non-obvious behaviors and assumptions discovered
while integrating Curate with real editors (primarily Neovim).

These are not bugs in Curate itself, but editor-level hazards that affect
structural tooling.

## Destructive Normal-Mode Commands (Neovim)

### Issue

Certain default Neovim normal-mode commands *mutate the buffer* while
appearing navigation-like.

The most critical examples are:

- `J`  (join lines)
- `gJ` (join lines without inserting space)

When used in fold-heavy or structure-aware contexts, these commands may
silently modify **hidden text**, leading to corrupted structure,
unexpected diffs, and loss of semantic integrity.

This behavior is especially dangerous when working with structural
folding tools such as Curate, where parts of the buffer may be visually
collapsed.

### Observed Failure Mode

- A user folds structural regions (classes, functions, docstrings).
- The user navigates using normal-mode commands.
- A single accidental `J` or `gJ` joins *physical buffer lines*.
- Hidden content inside folds is modified without visual feedback.
- The file becomes dirty, often without the user understanding why.

This can manifest as:
- flattened or mangled folded regions
- unexpected whitespace or line joins
- editors refusing to quit due to “unsaved changes”
- silent source corruption

### Root Cause

- `J` / `gJ` operate on **buffer lines**, not visual lines.
- Folding hides intermediate content but does not protect it.
- Vim treats these commands as editing operations, not navigation.
- The visual model presented to the user does not reflect the mutation.

This is **legacy Vim behavior** and **not a Curate bug**.

### Design Assumption

Curate assumes the following invariant:

> **Navigation must never mutate buffer state.**

Structural tools rely on the guarantee that navigation and inspection
are read-only operations.

Curate does not and should not attempt to guard against editor-level
mutations.

### Recommended Mitigations

It is strongly recommended to neutralize these commands in editor
configuration when using Curate or other structure-aware tooling.

#### Option 1: Disable the commands entirely

```lua
vim.keymap.set("n", "J", "<Nop>", { silent = true })
vim.keymap.set("n", "gJ", "<Nop>", { silent = true })
````

#### Option 2: Make navigation case-insensitive (recommended)

Map destructive uppercase motions to their safe lowercase equivalents:

```lua
vim.keymap.set("n", "H", "h", { silent = true })
vim.keymap.set("n", "J", "j", { silent = true })
vim.keymap.set("n", "K", "k", { silent = true })
vim.keymap.set("n", "L", "l", { silent = true })
```

This preserves navigation ergonomics while guaranteeing that
uppercase motion keys cannot mutate buffer contents.

### Non-Issues

Not all editing operators are problematic in this context.

Examples that are generally safe and intentionally mutating:

* `<<` / `>>` (indent adjustment)
* `=` formatting operators (e.g. `=ap`)

These commands clearly express editing intent and do not silently
interact with folded regions in a destructive way.

---

**Summary**

This pitfall highlights a fundamental tension between legacy modal
editing and modern structural tooling.

By enforcing a strict separation between navigation and mutation,
Curate can operate deterministically and safely — but this requires
editor-level safeguards.
