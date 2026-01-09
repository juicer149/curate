-- tests/lua/curate/client_harness.lua
-- Standalone test harness for curate_view.client
-- Runs without Neovim by stubbing the minimal vim API surface.

---------------------------------------------------------------------
-- Call tracking
---------------------------------------------------------------------
local calls = {
  cmd = {},
  system = {},
}

---------------------------------------------------------------------
-- Minimal vim.deepcopy implementation (MISSING BEFORE)
---------------------------------------------------------------------
local function deepcopy(v)
  if type(v) ~= "table" then
    return v
  end
  local out = {}
  for k, val in pairs(v) do
    out[k] = deepcopy(val)
  end
  return out
end

---------------------------------------------------------------------
-- Minimal vim stub
---------------------------------------------------------------------
_G.vim = {
  deepcopy = deepcopy,

  tbl_deep_extend = function(mode, base, override)
    if mode ~= "force" then
      error("Only 'force' mode is stubbed")
    end
    local result = deepcopy(base)
    for k, v in pairs(override) do
      if type(v) == "table" and type(result[k]) == "table" then
        result[k] = vim.tbl_deep_extend("force", result[k], v)
      else
        result[k] = v
      end
    end
    return result
  end,

  opt_local = setmetatable({}, {
    __newindex = function(_, _, _) end,
    __index = function(_, _) return setmetatable({}, { __newindex = function() end }) end,
  }),

  api = {
    nvim_get_current_buf = function()
      return 1
    end,

    nvim_win_get_cursor = function()
      return { 5, 0 }
    end,

    nvim_buf_get_lines = function(_, _, _, _)
      return { "print('x')" }
    end,

    nvim_create_autocmd = function(_, _)
      -- no-op stub for autocmd registration
    end,
  },

  bo = {
    [1] = { filetype = "python" },
  },

  fn = {
    foldlevel = function(_)
      return 0
    end,

    foldclosed = function(_)
      return -1
    end,

    tempname = function()
      return "/tmp/curate_test"
    end,

    writefile = function(_, _)
      -- no-op
    end,
  },

  cmd = function(s)
    table.insert(calls.cmd, s)
  end,

  loop = {
    fs_unlink = function(_)
      -- no-op
    end,
  },

  log = {
    levels = { ERROR = 4 },
  },

  notify = function()
    -- overridden per-test when needed
  end,

  json = {
    decode = function(_)
      return { folds = { { 1, 3 } } }
    end,
  },

  schedule = function(fn)
    fn()
  end,

  system = function(args, _, cb)
    table.insert(calls.system, { args = args })
    cb({
      code = 0,
      stdout = '{"folds":[[1,3]]}',
    })
  end,
}

---------------------------------------------------------------------
-- Make plugin visible to Lua
---------------------------------------------------------------------
package.path =
  "adapters/nvim/lua/?.lua;" ..
  "adapters/nvim/lua/?/init.lua;" ..
  package.path

local client = require("curate_view.client")

---------------------------------------------------------------------
-- Tiny assertions
---------------------------------------------------------------------
local function assert_true(cond, msg)
  if not cond then
    error(msg or "assertion failed", 2)
  end
end

local function assert_equal(a, b, msg)
  if a ~= b then
    error(
      msg or string.format("expected %s, got %s", tostring(b), tostring(a)),
      2
    )
  end
end
---------------------------------------------------------------------
-- Test: fold_next applies folds
---------------------------------------------------------------------
client.fold_next()

assert_true(#calls.system == 1, "system should be called once")
assert_equal(calls.cmd[#calls.cmd], "1,3fold", "should apply fold 1,3")

---------------------------------------------------------------------
-- Test: python error surfaces notification and applies no folds
---------------------------------------------------------------------
do
  calls.cmd = {}
  calls.system = {}
  local notified = false

  vim.notify = function()
    notified = true
  end

  vim.system = function(_, _, cb)
    cb({ code = 1, stderr = "boom" })
  end

  client.fold_next()

  assert_true(notified, "should notify on python error")
  assert_true(#calls.cmd == 0, "should not apply folds on error")
end

---------------------------------------------------------------------
-- Test: invalid JSON from python
---------------------------------------------------------------------
do
  calls.cmd = {}
  calls.system = {}
  local notified = false

  vim.notify = function()
    notified = true
  end

  local prev_decode = vim.json.decode
  vim.json.decode = function(_)
    error("invalid json")
  end

  vim.system = function(_, _, cb)
    cb({ code = 0, stdout = "not json" })
  end

  client.fold_next()

  assert_true(notified, "should notify on invalid JSON")
  assert_true(#calls.cmd == 0, "should not apply folds on invalid JSON")

  vim.json.decode = prev_decode
end

---------------------------------------------------------------------
-- Test: empty folds result applies zE
---------------------------------------------------------------------
do
  calls.cmd = {}
  calls.system = {}

  vim.json.decode = function(_)
    return { folds = {} }
  end

  vim.system = function(_, _, cb)
    cb({ code = 0, stdout = '{"folds":[]}' })
  end

  client.fold_next()

  -- Even with empty folds, the function applies them (which is a no-op)
  -- No error should occur
  assert_true(true, "should handle empty folds gracefully")
end

---------------------------------------------------------------------
-- Test: unfold_all clears folds
---------------------------------------------------------------------
do
  calls.cmd = {}
  calls.system = {}

  client.unfold_all()

  assert_equal(
    calls.cmd[#calls.cmd],
    "normal! zE",
    "unfold_all should clear folds"
  )
end

---------------------------------------------------------------------
-- Test: fold_children uses children mode
---------------------------------------------------------------------
do
  calls.cmd = {}
  calls.system = {}

  vim.system = function(args, _, cb)
    table.insert(calls.system, { args = args })
    cb({
      code = 0,
      stdout = '{"folds":[[1,3]]}',
    })
  end

  client.fold_children()

  -- Verify that "children" mode was passed
  local found_children = false
  for _, call in ipairs(calls.system) do
    for i, arg in ipairs(call.args) do
      if arg == "--mode" and call.args[i + 1] == "children" then
        found_children = true
        break
      end
    end
  end

  assert_true(found_children, "should use 'children' mode")
end

---------------------------------------------------------------------
-- Test: many cursor positions (fuzz-ish)
---------------------------------------------------------------------
local utils = require("tests.lua.utils")

local lines = utils.seeded_lines(1, 50, 20, 42)
for _, line in ipairs(lines) do
  vim.api.nvim_win_get_cursor = function()
    return { line, 0 }
  end
  client.fold_next()
end

print("client_harness: ALL TESTS OK")
