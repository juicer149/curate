-- lua/curate/client.lua
--
-- Curate Neovim client.
--
-- Architectural role:
--   - This file is the *only* bridge between Neovim and the Python engine.
--   - It invokes `python -m curate` asynchronously.
--   - It receives semantic folding decisions as JSON over stdout.
--   - It applies folds using Neovim's manual fold mechanism.
--
-- Design principles:
--   - No editor state is sent to Python (only text + cursor line).
--   - No semantic logic exists in Lua.
--   - Communication happens exclusively via CLI + JSON.
--
-- This makes the Python engine editor-agnostic and the Lua client dumb and fast.

local M = {}

-- ------------------------------------------------------------
-- Helpers: buffer → tempfile
-- ------------------------------------------------------------

--- Write the current buffer contents to a temporary file.
---
--- Why a tempfile?
---   - Works for unsaved buffers
---   - Avoids stdin edge cases
---   - Keeps Python side simple and debuggable
---
--- @param buf number Neovim buffer handle
--- @return string path to temporary file
local function write_buffer_to_tempfile(buf)
  local tmp = vim.fn.tempname() .. ".py"
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  vim.fn.writefile(lines, tmp)
  return tmp
end

-- ------------------------------------------------------------
-- Helpers: folding application
-- ------------------------------------------------------------

--- Apply fold ranges returned by Curate.
---
--- Each fold is a table:
---   { start = <line>, end = <line> }
---
--- Lines are 1-based and inclusive.
---
--- @param folds table[]|nil
local function apply_folds(folds)
  for _, fold in ipairs(folds or {}) do
    local start_line = tonumber(fold.start)
    local end_line = tonumber(fold["end"])

    -- Defensive: ignore invalid or zero-length folds
    if start_line and end_line and start_line < end_line then
      vim.cmd(string.format("%d,%dfold", start_line, end_line))
    end
  end
end

-- ------------------------------------------------------------
-- Core runner
-- ------------------------------------------------------------

--- Run the Curate engine with a given semantic action.
---
--- This function is intentionally stateless:
---   - No caching
---   - No memory of previous folds
---
--- Toggle behaviour:
---   - If the cursor is already inside a fold, we clear folds (zE)
---   - Otherwise, we ask Curate to compute folds and apply them
---
--- @param action string One of: "local", "minimum", "code", "docs"
local function run_curate(action)
  local buf = vim.api.nvim_get_current_buf()
  local cursor_line = vim.api.nvim_win_get_cursor(0)[1]

  -- Simple toggle UX:
  -- If we're already in a folded region, clear folds instead.
  if vim.fn.foldlevel(cursor_line) > 0 then
    vim.cmd("normal! zE")
    return
  end

  -- Always operate on a temp file so unsaved buffers work
  local tmp = write_buffer_to_tempfile(buf)

  -- Run Curate asynchronously
  vim.system({
    "python3",
    "-m", "curate",
    tmp,
    "--line", tostring(cursor_line),
    "--action", action,
  }, { text = true }, function(res)
    -- Always clean up the tempfile (best effort)
    pcall(vim.loop.fs_unlink, tmp)

    -- Non-zero exit code → surface error to user
    if res.code ~= 0 then
      vim.schedule(function()
        vim.notify(
          "Curate error:\n" .. (res.stderr or res.stdout or ""),
          vim.log.levels.ERROR
        )
      end)
      return
    end

    -- Parse JSON payload
    local ok, payload = pcall(vim.json.decode, res.stdout or "")
    if not ok then
      vim.schedule(function()
        vim.notify(
          "Curate returned invalid JSON",
          vim.log.levels.ERROR
        )
      end)
      return
    end

    -- Apply folds on the main thread
    vim.schedule(function()
      -- Clear existing folds before applying new ones
      vim.cmd("normal! zE")
      apply_folds(payload.folds)
    end)
  end)
end

-- ------------------------------------------------------------
-- Public API
-- ------------------------------------------------------------

--- Fold the most local semantic entity under the cursor.
function M.fold_local()
  run_curate("local")
end

--- Fold the current scope into its minimum (heads-only) view.
function M.fold_minimum()
  run_curate("minimum")
end

--- Fold documentation in the current scope.
function M.fold_code()
  run_curate("code")
end

--- Fold code in the current scope.
function M.fold_docs()
  run_curate("docs")
end

return M
