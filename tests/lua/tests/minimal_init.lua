-- tests/lua/tests/minimal_init.lua
--
-- Fully isolated Neovim init for running Lua tests.
-- No user config, no plugins, no UI.

-- Hard stop: do NOT load user config
vim.env.NVIM_APPNAME = "curate-test"

-- Basic sanity
vim.opt.swapfile = false
vim.opt.shada = ""
vim.opt.termguicolors = false

-- Runtime paths
local root = vim.fn.getcwd()

vim.opt.runtimepath = {
  vim.fn.stdpath("data") .. "/site",
  root,
  root .. "/lua",
}

-- Ensure vim.inspect exists (defensive)
if not vim.inspect then
  vim.inspect = require("vim.inspect")
end

-- Load plenary test harness
require("plenary.busted")

-- Silence notifications
vim.notify = function() end
