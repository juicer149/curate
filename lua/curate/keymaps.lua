-- lua/curate/keymaps.lua
--
-- Curate keybindings.
--
-- Philosophy:
--   - Keys express *intent*
--   - Python decides *what that intent means semantically*

local M = {}
local map = vim.keymap.set
local curate = require("curate.client")

local DEFAULT_KEYS = {
  local_fold = "<leader>f",
  minimum    = "<leader>F",
  code       = "<leader>fc",
  docs       = "<leader>fd",
}

function M.setup(keys)
  keys = vim.tbl_deep_extend("force", DEFAULT_KEYS, keys or {})

  map("n", keys.local_fold, curate.fold_local, {
    desc = "Curate: fold local entity",
  })

  map("n", keys.minimum, curate.fold_minimum, {
    desc = "Curate: minimum view",
  })

  map("n", keys.code, curate.fold_code, {
    desc = "Curate: code only",
  })

  map("n", keys.docs, curate.fold_docs, {
    desc = "Curate: docs only",
  })
end

return M
