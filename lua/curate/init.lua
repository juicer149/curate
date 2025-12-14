-- lua/curate/init.lua
--
-- Curate Neovim plugin entrypoint.
--
-- This module exists only to wire together the Lua-side components.
-- All real behaviour lives in:
--   - curate.client  (engine bridge)
--   - curate.keymaps (UX bindings)

require("curate.keymaps")
