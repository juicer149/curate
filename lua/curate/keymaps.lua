-- lua/curate/keymaps.lua
--
-- Curate keybindings.
--
-- Philosophy:
--   - Keys express *intent*
--   - Python decides *what that intent means semantically*

local map = vim.keymap.set
local curate = require("curate.client")

-- Fold / unfold the most local entity
map("n", "<leader>f", curate.toggle_local, {
  desc = "Curate: toggle local entity",
})

-- Fold / unfold scope to minimum view
map("n", "<leader>F", curate.toggle_minimum, {
  desc = "Curate: toggle scope (minimum view)",
})

-- Fold / unfold code in scope
map("n", "<leader>fc", curate.toggle_code, {
  desc = "Curate: toggle code in scope",
})

-- Fold / unfold docs in scope
map("n", "<leader>fd", curate.toggle_docs, {
  desc = "Curate: toggle docs in scope",
})
