-- adapters/nvim/lua/curate_view/client.lua
--
-- Neovim ↔ Curate bridge.
-- This is the ONLY layer that talks to Python.
--
-- Contract:
-- - Input is always source text (we write a temp file and pass its path)
-- - Output is JSON: { "folds": [[start, end], ...] }
-- - Lua expresses intent (cursor/level/mode/language). Python decides meaning.

local M = {}

local DEFAULTS = {
  -- Command used to invoke Curate.
  -- Prefer "python3 -m curate" since it works without installing the script.
  cmd = { "python3", "-m", "curate" },

  -- Optional: file extension per filetype when writing temp files.
  ext_by_ft = {
    python = ".py",
    lua = ".lua",
    markdown = ".md",
    md = ".md",
  },

  -- Map Neovim 'filetype' -> Curate 'language'
  -- Unknown languages fall back to Curate's safe backend.
  language_by_ft = {
    python = "python",
    lua = "lua",
    markdown = "markdown",
    md = "markdown",
  },

  -- Notifications
  notify = true,
}

local CONFIG = vim.deepcopy(DEFAULTS)

--- Merge user config.
--- @param opts table|nil
function M.setup(opts)
  CONFIG = vim.tbl_deep_extend("force", vim.deepcopy(DEFAULTS), opts or {})
end

-- ------------------------------------------------------------
-- Helpers: buffer → tempfile
-- ------------------------------------------------------------

--- @param buf number
--- @return string tmp_path
local function write_buffer_to_tempfile(buf)
  local ft = vim.bo[buf].filetype
  local ext = (CONFIG.ext_by_ft and CONFIG.ext_by_ft[ft]) or ".txt"
  local tmp = vim.fn.tempname() .. ext

  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  vim.fn.writefile(lines, tmp)

  return tmp
end

-- ------------------------------------------------------------
-- Helpers: fold application
-- ------------------------------------------------------------

--- @param folds any[]|nil JSON array: [[start,end], ...]
local function apply_folds(folds)
  for _, r in ipairs(folds or {}) do
    local a = tonumber(r[1])
    local b = tonumber(r[2])

    -- Curate contract: 1-based inclusive ranges, and only fold if a < b
    if a and b and a < b then
      vim.cmd(string.format("%d,%dfold", a, b))
    end
  end
end

local function notify_err(msg)
  if not CONFIG.notify then
    return
  end
  vim.notify(msg, vim.log.levels.ERROR)
end

-- ------------------------------------------------------------
-- Core runner
-- ------------------------------------------------------------

--- Run Curate.
--- Toggle UX:
--- - If cursor is already inside a fold → clear folds (zE)
--- - Else → compute folds and apply them
--- @param mode '"self"'|'"children"'
--- @param level number
local function run_curate(mode, level)
  local buf = vim.api.nvim_get_current_buf()
  local cursor_line = vim.api.nvim_win_get_cursor(0)[1]

  -- If we're already inside any fold, clear folds instead (simple toggle).
  if vim.fn.foldlevel(cursor_line) > 0 then
    vim.cmd("normal! zE")
    return
  end

  local tmp = write_buffer_to_tempfile(buf)

  local ft = vim.bo[buf].filetype
  local language = (CONFIG.language_by_ft and CONFIG.language_by_ft[ft]) or "unknown"

  local cmd = vim.deepcopy(CONFIG.cmd)
  -- Args: <path> --line N --level L --mode <mode> --language <language> --output json
  table.insert(cmd, tmp)
  table.insert(cmd, "--line")
  table.insert(cmd, tostring(cursor_line))
  table.insert(cmd, "--level")
  table.insert(cmd, tostring(level or 0))
  table.insert(cmd, "--mode")
  table.insert(cmd, mode)
  table.insert(cmd, "--language")
  table.insert(cmd, language)
  table.insert(cmd, "--output")
  table.insert(cmd, "json")

  vim.system(cmd, { text = true }, function(res)
    -- Always clean up temp file (best-effort)
    pcall(vim.loop.fs_unlink, tmp)

    if res.code ~= 0 then
      vim.schedule(function()
        notify_err("Curate error:\n" .. (res.stderr or res.stdout or ""))
      end)
      return
    end

    local ok, payload = pcall(vim.json.decode, res.stdout or "")
    if not ok or type(payload) ~= "table" or type(payload.folds) ~= "table" then
      vim.schedule(function()
        notify_err("Curate returned invalid JSON")
      end)
      return
    end

    vim.schedule(function()
      -- Clear existing folds before applying new ones
      vim.cmd("normal! zE")
      apply_folds(payload.folds)
    end)
  end)
end

-- ------------------------------------------------------------
-- Public API (intent only)
-- ------------------------------------------------------------

--- children/local on current scope
function M.fold_local()
  run_curate("children", 0)
end

--- children/local one level up
function M.fold_parent()
  run_curate("children", 1)
end

--- self/maximal on current scope
function M.fold_self()
  run_curate("self", 0)
end

return M
