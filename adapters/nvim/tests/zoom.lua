-- Headless tests for curate_view (zoom in/out through the structural path).
--
--   make test-nvim
--   nvim --headless --clean -u NONE -c "luafile adapters/nvim/tests/zoom.lua"
--
-- Runs against tests/fixtures/python_minimal.py, whose line numbers are fixed:
--   top() 7-19 > inner() 11-13, if 15-17;  class C 22-24 > m() 23-24
--   outline: 7-19 (top, whole) and 23-24 (m; the class line stays open)
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
  for _ = 1, 4 do -- U steps back one outline level per press
    cv.unfold_all()
  end
  fn(function(step, want) expect(name .. ": " .. step, want) end)
end

case("zoom out and in", function(check)
  at(16); cv.fold_next(); check("f on if", "15-17")
  cv.fold_next(); check("f again: enclosing function", "7-19")
  cv.fold_next(); check("f at outermost: unchanged", "7-19")
  cv.unfold_next(); check("u: back to the if", "15-17")
  cv.unfold_next(); check("u: nothing folded", "")
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

case("F gives the outline wherever the cursor is", function(check)
  at(16); cv.fold_max(); check("F inside top()", "7-19 23-24")
  cv.unfold_all()
  at(24); cv.fold_max(); check("F inside m()", "7-19 23-24")
  cv.unfold_all()
  at(20); cv.fold_max(); check("F on a blank line", "7-19 23-24")
end)

case("F folds one step further, U one step back", function(check)
  at(20); cv.fold_max(); check("F: outline", "7-19 23-24")
  at(24); cv.fold_max(); check("F again, anywhere: classes fold whole", "7-19 22-24")
  cv.fold_max(); check("F at the top: unchanged", "7-19 22-24")
  cv.unfold_all(); check("U: back to the outline", "7-19 23-24")
  cv.unfold_all(); check("U again: everything open", "")
end)

case("u on a class folded by F shows its methods", function(check)
  cv.fold_max(); cv.fold_max(); check("F F: classes whole", "7-19 22-24")
  at(22); cv.unfold_next(); check("u on class C: m() stays folded", "7-19 23-24")
end)

case("f between the scopes inside a function", function(check)
  at(14); cv.fold_next(); check("f on the blank line in top(): its scopes", "11-13 15-17")
  cv.fold_next(); check("f again: top() itself", "7-19")
  cv.unfold_next(); check("u: back to its scopes", "11-13 15-17")
  cv.unfold_next(); check("u: nothing folded", "")
  at(9); cv.fold_next(); check("f on a statement between them", "11-13 15-17")
  cv.unfold_all()
  at(7); cv.fold_next(); check("f on the def line: the function", "7-19")
end)

case("outline replaces earlier folds and u opens one", function(check)
  at(12); cv.fold_next(); check("f in inner()", "11-13")
  at(20); cv.fold_max(); check("F: outline only", "7-19 23-24")
  at(7); cv.unfold_next(); check("u on top()", "23-24")
end)

local function line_now()
  return vim.api.nvim_win_get_cursor(0)[1]
end

local function equal_line(name, want)
  count = count + 1
  if line_now() ~= want then
    failures = failures + 1
    print(string.format("FAIL %s\n     want line %d\n     got  line %d", name, want, line_now()))
  end
end

case("j/k jump between visible defs and classes", function(check)
  cv.fold_max(); check("F: outline", "7-19 23-24")
  at(1); cv.next_head(); equal_line("j from the top: top()", 7)
  cv.next_head(); equal_line("j skips inner(), hidden in top()", 22)
  cv.next_head(); equal_line("j: m()", 23)
  cv.prev_head(); equal_line("k: back to class C", 22)
  cv.unfold_all()
  at(8); cv.next_head(); equal_line("j with nothing folded: inner()", 11)
end)

-- Markdown: F folds one heading level per press, U goes back.
vim.o.hidden = true
vim.cmd("edit " .. root .. "/tests/fixtures/markdown_minimal.md")
vim.bo.filetype = "markdown"

case("Markdown: F one heading level at a time, U back", function(check)
  at(1); cv.fold_max(); check("F: every heading shows", "1-4 5-8 9-12 13-16 17-19")
  cv.fold_max(); check("F: ### into ##", "1-4 5-12 13-16 17-19")
  cv.fold_max(); check("F: ## into #", "1-16 17-19")
  cv.fold_max(); check("F at the top: unchanged", "1-16 17-19")
  cv.unfold_all(); check("U: ## back", "1-4 5-12 13-16 17-19")
  cv.unfold_all(); check("U: ### back", "1-4 5-8 9-12 13-16 17-19")
  cv.unfold_all(); check("U: everything open", "")
end)

case("Markdown: u on a folded section opens one level", function(check)
  at(1); cv.fold_max(); cv.fold_max(); check("F F: ### into ##", "1-4 5-12 13-16 17-19")
  at(5); cv.unfold_next(); check("u on ## Install: its ### stays folded", "1-4 5-8 9-12 13-16 17-19")
end)

vim.cmd("edit " .. root .. "/tests/fixtures/python_minimal.py")
vim.bo.filetype = "python"

-- Fold text: first line as in the buffer, then a dimmed line count.
local function text_of(chunks)
  local out = {}
  for _, c in ipairs(chunks) do table.insert(out, c[1]) end
  return table.concat(out)
end

local function equal(name, got, want)
  count = count + 1
  if got ~= want then
    failures = failures + 1
    print(string.format("FAIL %s\n     want [%s]\n     got  [%s]", name, tostring(want), tostring(got)))
  end
end

case("fold text", function(check)
  at(16); cv.fold_max()
  equal("foldtext is set where curate folds", vim.wo.foldtext, "v:lua.require'curate_view'.foldtext()")
  local chunks = cv.render_fold(0, 7, 19)
  equal("first line + count", text_of(chunks), "def top(): ··· 13")
  equal("count is dimmed", chunks[#chunks][2], "Comment")
  equal("no Folded background", vim.wo.winhighlight:find("Folded:CurateFolded", 1, true) ~= nil, true)
  equal("indented line keeps its indent", text_of(cv.render_fold(0, 23, 24)), "    def m(self): ··· 2")
end)

-- The filetype is sent as the language; unknown ones get a message, not a fold.
local messages = {}
vim.notify = function(msg) table.insert(messages, msg) end

local function notified(name, text)
  count = count + 1
  local hit = false
  for _, m in ipairs(messages) do
    if m:find(text, 1, true) then hit = true end
  end
  if not hit then
    failures = failures + 1
    print(string.format("FAIL %s\n     want message containing [%s]\n     got  [%s]",
      name, text, table.concat(messages, " | ")))
  end
  messages = {}
end

case("filetype decides the language", function(check)
  vim.bo.filetype = "lua"
  at(16); cv.fold_next(); check("f with an unknown filetype", "")
  notified("unknown filetype", "no structure support for language 'lua'")
  vim.bo.filetype = ""
  cv.fold_next(); check("f without a filetype", "")
  notified("no filetype", "buffer has no filetype")
  vim.bo.filetype = "python"
end)

print(string.format("%d checks, %d failed", count, failures))
vim.cmd(failures == 0 and "qa!" or "cquit 1")
