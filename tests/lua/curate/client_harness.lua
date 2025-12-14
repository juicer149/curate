-- Standalone test harness for curate Neovim client (no Busted)
-- Stubs minimal vim API, loads client module, and checks core behaviours.

local calls = { cmd = {}, system = {} }

_G.vim = {
  api = {
    nvim_get_current_buf = function() return 1 end,
    nvim_win_get_cursor = function(_) return {5, 0} end,
    nvim_buf_get_lines = function(_, _, _, _) return {"print('x')"} end,
  },
  fn = {
    foldlevel = function(_) return 0 end,
    tempname = function() return "/tmp/curate_test" end,
    writefile = function(_, _) end,
  },
  cmd = function(s) table.insert(calls.cmd, s) end,
  loop = { fs_unlink = function(_) end },
  log = { levels = { ERROR = 4 } },
  notify = function() end,
  json = { decode = function(s) return { folds = { { start = 1, ["end"] = 3 } } } end },
  schedule = function(fn) fn() end,
  system = function(args, opts, cb)
    table.insert(calls.system, { args = args })
    cb({ code = 0, stdout = '{"folds":[{"start":1,"end":3}]}' })
  end,
}

package.path = "./lua/?.lua;./lua/?/init.lua;" .. package.path
local client = require("curate.client")

local function assert_true(cond, msg)
  if not cond then error(msg or "assertion failed", 0) end
end

local function assert_equal(a, b, msg)
  if a ~= b then
    error(msg or string.format("expected %s, got %s", tostring(b), tostring(a)), 0)
  end
end

client.fold_code()
assert_true(#calls.system == 1, "system should be called once")
assert_true(calls.cmd[#calls.cmd] == "1,3fold", "last cmd should apply 1,3fold")

vim.fn.foldlevel = function(_) return 1 end
client.fold_docs()
assert_true(calls.cmd[#calls.cmd] == "normal! zE", "should clear folds when folded")

print("client_harness: OK")

-- Test: python error code surfaces error and applies no folds
do
  vim.fn.foldlevel = function(_) return 0 end
  local notified = false
  calls.cmd = {}
  vim.notify = function(_) notified = true end
  vim.system = function(_, _, cb)
    cb({ code = 1, stderr = "boom" })
  end
  client.fold_local()
  assert_true(notified, "should notify on python error")
  assert_true(#calls.cmd == 0, "should not apply folds on error")
end

-- Restore default success stub
vim.system = function(args, opts, cb)
  table.insert(calls.system, { args = args })
  cb({ code = 0, stdout = '{"folds":[{"start":1,"end":3}]}' })
end

-- Test: invalid JSON from python
do
  local notified = false
  calls.cmd = {}
  vim.notify = function(_) notified = true end
  local prev_decode = vim.json.decode
  vim.json.decode = function(_) error("invalid json") end
  vim.system = function(_, _, cb)
    cb({ code = 0, stdout = "not json at all" })
  end
  client.fold_code()
  assert_true(notified, "should notify on invalid JSON")
  assert_true(#calls.cmd == 0, "should not apply folds on invalid JSON")
  vim.json.decode = prev_decode
end

-- Reset notify/system
vim.notify = function() end
vim.system = function(args, opts, cb)
  table.insert(calls.system, { args = args })
  cb({ code = 0, stdout = '{"folds":[{"start":1,"end":3}]}' })
end

-- Test: toggle clears folds when already folded
do
  vim.fn.foldlevel = function(_) return 1 end
  calls.cmd = {}
  client.fold_docs()
  assert_equal(calls.cmd[#calls.cmd], "normal! zE", "should clear folds when already folded")
end

-- Reset foldlevel
vim.fn.foldlevel = function(_) return 0 end

-- Test: empty folds result does nothing (but does not error)
do
  calls.cmd = {}
  local prev_decode = vim.json.decode
  vim.json.decode = function(_) return { folds = {} } end
  vim.system = function(_, _, cb)
    cb({ code = 0, stdout = '{"folds": []}' })
  end
  client.fold_minimum()
  assert_equal(calls.cmd[#calls.cmd], "normal! zE", "should only clear folds when no folds returned")
  vim.json.decode = prev_decode
end

print("client_harness: ALL TESTS OK")
