# Curate – Neovim Lua Integration

This directory contains the **Neovim-facing Lua client** for Curate.

The Lua code is intentionally small, dumb, and editor-specific.
All semantic logic lives in Python.

> Lua expresses *intent*.  
> Python decides *meaning*.

---

## Overview

The Lua integration is split into three layers:

```

lua/curate/
├── client.lua   -- Bridge to the Python engine
├── keymaps.lua  -- User-facing keybindings
└── init.lua     -- Public plugin entrypoint

````

### Design goals

- No semantic logic in Lua
- No editor state sent to Python
- Stateless, deterministic behavior
- Easy to test and reason about
- Safe to call repeatedly

---

## `client.lua` – Engine Bridge

`client.lua` is the **only file that talks to Python**.

Responsibilities:

- Serialize the current buffer to a temporary file
- Call `python -m curate` asynchronously
- Parse JSON from stdout
- Apply folds using Neovim’s manual folding (`:fold`)
- Implement simple toggle UX:
  - If cursor is already in a fold → clear folds (`zE`)
  - Otherwise → compute and apply folds

It exposes a minimal API:

```lua
require("curate.client").fold_local()
require("curate.client").fold_minimum()
require("curate.client").fold_code()
require("curate.client").fold_docs()
````

These map directly to Python actions:

| Lua function   | Python action |
| -------------- | ------------- |
| `fold_local`   | `local`       |
| `fold_minimum` | `minimum`     |
| `fold_code`    | `code`        |
| `fold_docs`    | `docs`        |

No state is cached. Every call is independent.

---

## `keymaps.lua` – UX Policy

`keymaps.lua` defines **how users interact** with Curate in Neovim.

Key points:

* Keybindings express *intent*, not implementation
* Defaults are provided
* Users may override keys via `setup()`

### Default keybindings

| Action       | Default key  |
| ------------ | ------------ |
| Fold local   | `<leader>f`  |
| Minimum view | `<leader>F`  |
| Code only    | `<leader>fc` |
| Docs only    | `<leader>fd` |

Internally this file exports:

```lua
require("curate.keymaps").setup({
  -- optional overrides
})
```

---

## `init.lua` – Public Plugin API

`init.lua` is the **only module users should require**.

It exposes a single entrypoint:

```lua
require("curate").setup(opts)
```

### Default behavior (backwards compatible)

If the user does **nothing** except:

```lua
require("curate")
```

→ default keymaps are installed immediately.

This ensures older configs continue to work.

### With configuration

```lua
require("curate").setup({
  keymaps = {
    local_fold = "<leader>cf",
    minimum    = "<leader>cF",
    code       = "<leader>cc",
    docs       = "<leader>cd",
  },
})
```

Only the provided keys are overridden.

---

## Recommended Neovim Plugin Spec

Example using a local checkout:

```lua
{
  dir = "~/code/packages/curate",
  name = "curate",
  ft = { "python" },
  config = function()
    require("curate").setup()
  end,
}
```

Curate is filetype-scoped and only loads for Python buffers.

---

## Error Handling

The Lua client handles errors defensively:

* Python non-zero exit → `vim.notify(ERROR)`
* Invalid JSON → `vim.notify(ERROR)`
* Temporary files are always cleaned up (best-effort)
* No folds are applied on error

Failures are visible but never crash Neovim.

---

## Testing

The Lua client is tested via a **standalone harness**:

```
tests/lua/curate/client_harness.lua
```

This harness:

* Stubs the `vim` API
* Loads the real client code
* Verifies behavior for:

  * Happy path
  * Python errors
  * Invalid JSON
  * Empty folds
  * Fold toggle behavior

No Neovim runtime or Plenary is required.

---

## Philosophy

The Lua side of Curate follows a strict rule:

> **Lua is glue. Python is truth.**

This keeps the editor integration:

* predictable
* debuggable
* easy to evolve

Future editors can reuse the same Python engine
with a different UI layer.
