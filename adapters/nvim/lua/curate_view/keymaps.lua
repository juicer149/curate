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
local DEFAULT_KEYS = {
  local_fold = "<leader>f",   -- fold children at current scope
  parent     = "<leader>ff",  -- fold children one level up
  self_fold  = "<leader>F",   -- fold self/maximal at current scope
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
  end, { desc = "Curate: fold children (local)" })

  map("n", keys.parent, function()
    client.fold_parent()
  end, { desc = "Curate: fold children (parent)" })

  map("n", keys.self_fold, function()
    client.fold_self()
  end, { desc = "Curate: fold self (maximal)" })
end

return M
