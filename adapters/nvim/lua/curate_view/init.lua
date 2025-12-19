-- adapters/nvim/lua/curate_view/init.lua
--
-- Neovim adapter entrypoint for Curate (Python engine).
-- Lua is glue; Python is truth.

local M = {}

--- Setup Curate view adapter.
--- @param opts table|nil
---   opts.keymaps: table|nil
---   opts.client: table|nil  (forwarded to curate_view.client.setup)
function M.setup(opts)
  opts = opts or {}

  if opts.client then
    require("curate_view.client").setup(opts.client)
  end

  require("curate_view.keymaps").setup(opts.keymaps)
end

-- Backwards compatible "just require it":
-- If user does `require("curate_view")`, install defaults immediately.
M.setup()

return M
