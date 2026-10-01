-- Headless tests for curate_view (zoom in/out through the structural path).
--
--   make test-nvim
--   nvim --headless --clean -u NONE -c "luafile adapters/nvim/tests/zoom.lua"
--
-- Runs against tests/fixtures/python_minimal.py, whose line numbers are fixed:
--   top() 7-19 > inner() 11-13, if 15-17;  class C 22-24 > m() 23-24
-- CURATE_CMD overrides the command (default: the adapter's own lookup).

local root = vim.fn.getcwd()
vim.opt.rtp:append(root .. "/adapters/nvim")
local cv = require("curate_view")
cv.setup({ cmd = os.getenv("CURATE_CMD") and { os.getenv("CURATE_CMD") } or nil, keymaps = false })

vim.cmd("edit " .. root .. "/tests/fixtures/python_minimal.py")
vim.bo.filetype = "python"
vim.notify = function() end -- keep test output clean

local failures, count = 0, 0

local function closed()
  local out, l, n = {}, 1, vim.api.nvim_buf_line_count(0)
  while l <= n do
    local s = vim.fn.foldclosed(l)
    if s ~= -1 then
      local e = vim.fn.foldclosedend(l)
      table.insert(out, s .. "-" .. e)
      l = e + 1
    else
      l = l + 1
    end
  end
  return table.concat(out, " ")
end

local function at(line)
  vim.api.nvim_win_set_cursor(0, { line, 0 })
end

local function expect(name, want)
  count = count + 1
  local got = closed()
  if got ~= want then
    failures = failures + 1
    print(string.format("FAIL %s\n     want [%s]\n     got  [%s]", name, want, got))
  end
end

local function case(name, fn)
  cv.unfold_all()
  fn(function(step, want) expect(name .. ": " .. step, want) end)
end

case("zoom out and in", function(check)
  at(16); cv.fold_next(); check("f on if", "15-17")
  cv.fold_next(); check("f again: enclosing function", "7-19")
  cv.fold_next(); check("f at outermost: unchanged", "7-19")
  cv.unfold_next(); check("u: back to the if", "15-17")
  cv.unfold_next(); check("u: nothing folded", "")
end)

case("fold_max steps back down", function(check)
  at(24); cv.fold_max(); check("F from m()", "22-24")
  cv.unfold_next(); check("u: m() still folded", "23-24")
end)

case("a new position starts a new zoom", function(check)
  at(7); cv.fold_next(); check("f on the def line", "7-19")
  cv.unfold_all()
  at(16); cv.fold_next(); check("f on the if after U", "15-17")
end)

case("folds elsewhere stay", function(check)
  at(12); cv.fold_next(); check("f in inner()", "11-13")
  at(24); cv.fold_next(); check("f in m(): both folded", "11-13 23-24")
  cv.unfold_next(); check("u: only m() opens", "11-13")
end)

case("continue from an earlier fold", function(check)
  at(12); cv.fold_next(); cv.fold_next(); check("f f in inner()", "7-19")
  at(24); cv.fold_next(); check("f in m()", "7-19 23-24")
  at(12); cv.unfold_next(); check("u on the earlier fold", "11-13 23-24")
  cv.fold_next(); check("f there again: no duplicate", "7-19 23-24")
end)

case("edits invalidate the cache", function(check)
  at(16); cv.fold_next(); cv.unfold_next()
  vim.api.nvim_buf_set_lines(0, 0, 0, false, { "# inserted" })
  at(17); cv.fold_next(); check("f after inserting a line above", "16-18")
  vim.api.nvim_buf_set_lines(0, 0, 1, false, {})
end)

case("no scope on a blank line", function(check)
  at(20); cv.fold_next(); check("f between functions", "")
end)

print(string.format("%d checks, %d failed", count, failures))
vim.cmd(failures == 0 and "qa!" or "cquit 1")
