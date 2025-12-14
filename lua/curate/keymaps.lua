-- lua/curate/keymaps.lua
--
-- Curate keybindings.
--
-- This file defines the user-facing interaction model.
-- All bindings map directly to semantic actions in the Python engine.
--
-- Philosophy:
--   - Keys express *intent*
--   - Python decides *what that intent means semantically*

local map = vim.keymap.set
local curate = require("curate.client")

-- Fold the most local entity (function / block / doc body)
map("n", "<leader>f", curate.fold_local, {
  desc = "Curate: fold local entity",
})

-- Fold the current scope to its minimum representation (heads only)
map("n", "<leader>F", curate.fold_minimum, {
  desc = "Curate: fold scope (minimum view)",
})

-- Fold all code in the current scope (docs-only view)
map("n", "<leader>fc", curate.fold_code, {
  desc = "Curate: fold code in scope",
})

-- Fold all documentation in the current scope (code-only view)
map("n", "<leader>fd", curate.fold_docs, {
  desc = "Curate: fold docs in scope",
})
