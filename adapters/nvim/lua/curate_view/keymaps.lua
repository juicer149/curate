-- adapters/nvim/lua/curate_view/keymaps.lua
--
-- Keymaps express *intent*.
-- Python decides *meaning*.

local M = {}

local map = vim.keymap.set
local client = require("curate_view.client")

-- ---------------------------------------------------------------------
-- Default keybindings
-- ---------------------------------------------------------------------
--
-- Semantics:
--
--   f   → fold local scope
--   ff  → same intent, but one level up
--   fff → two levels up
--
-- Lua does NOT interpret levels.
-- It only counts invocations and forwards them to Python.
--
-- Python:
--   - decides how levels map to AST
--   - clamps to root if needed
--   - may ignore levels for languages that don't support it
--
local DEFAULT_KEYS = {
  local_fold = "<leader>f",
  minimum    = "<leader>F",
  code       = "<leader>fc",
  docs       = "<leader>fd",
}

-- ---------------------------------------------------------------------
-- Setup keymaps
-- ---------------------------------------------------------------------
--- Setup Curate keymaps.
--- @param keys table|nil Optional key overrides
function M.setup(keys)
  keys = vim.tbl_deep_extend("force", DEFAULT_KEYS, keys or {})

  map("n", keys.local_fold, function()
    client.fold_local()
  end, {
    desc = "Curate: fold local semantic scope",
  })

  map("n", keys.minimum, function()
    client.fold_minimum()
  end, {
    desc = "Curate: minimum (heads-only) view",
  })

  map("n", keys.code, function()
    client.fold_code()
  end, {
    desc = "Curate: fold code (keep docs visible)",
  })

  map("n", keys.docs, function()
    client.fold_docs()
  end, {
    desc = "Curate: fold docs (keep code visible)",
  })
end

return M
