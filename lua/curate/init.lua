-- lua/curate/init.lua
--
-- Curate Neovim plugin entrypoint.
--
-- This module wires together the Lua-side components.
-- It is intentionally minimal and fully backwards-compatible.

local M = {}

function M.setup(opts)
  opts = opts or {}
  require("curate.keymaps").setup(opts.keymaps)
end

-- Backwards compatibility:
-- If user just `require("curate")`, install defaults immediately.
M.setup()

return M
