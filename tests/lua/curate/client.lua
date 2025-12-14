-- Module wrapper to expose client functions for tests.
-- In real usage, this would live in plugin runtimepath; for tests we embed here.

local M = {}

-- Inline the client implementation to avoid external dependency during tests.

---------------------------------------------------------------------
-- Helpers: buffer → tempfile
---------------------------------------------------------------------
local function write_buffer_to_tempfile(buf)
  local tmp = vim.fn.tempname() .. ".py"
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  vim.fn.writefile(lines, tmp)
  return tmp
end

---------------------------------------------------------------------
-- Helpers: folding application
---------------------------------------------------------------------
local function apply_folds(folds)
  for _, fold in ipairs(folds or {}) do
    local start_line = tonumber(fold.start)
    local end_line = tonumber(fold["end"])
    if start_line and end_line and start_line < end_line then
      vim.cmd(string.format("%d,%dfold", start_line, end_line))
    end
  end
end

---------------------------------------------------------------------
-- Core runner
---------------------------------------------------------------------
local function run_curate(action)
  local buf = vim.api.nvim_get_current_buf()
  local cursor_line = vim.api.nvim_win_get_cursor(0)[1]
  if vim.fn.foldlevel(cursor_line) > 0 then
    vim.cmd("normal! zE")
    return
  end
  local tmp = write_buffer_to_tempfile(buf)
  vim.system({
    "python3",
    "-m", "curate",
    tmp,
    "--line", tostring(cursor_line),
    "--action", action,
  }, { text = true }, function(res)
    pcall(vim.loop.fs_unlink, tmp)
    if res.code ~= 0 then
      vim.schedule(function()
        vim.notify("Curate error:\n" .. (res.stderr or res.stdout or ""), vim.log.levels.ERROR)
      end)
      return
    end
    local ok, payload = pcall(vim.json.decode, res.stdout or "")
    if not ok then
      vim.schedule(function()
        vim.notify("Curate returned invalid JSON", vim.log.levels.ERROR)
      end)
      return
    end
    vim.schedule(function()
      vim.cmd("normal! zE")
      apply_folds(payload.folds)
    end)
  end)
end

function M.toggle_local() run_curate("local") end
function M.toggle_minimum() run_curate("minimum") end
function M.toggle_code() run_curate("code") end
function M.toggle_docs() run_curate("docs") end

return M
