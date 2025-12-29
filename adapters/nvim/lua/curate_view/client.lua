-- adapters/nvim/lua/curate_view/client.lua
--
-- Neovim ↔ Curate bridge.
-- This is the ONLY layer that talks to Python.
--
-- Contract:
-- - Input is always source text (written to a temp file)
-- - Output is JSON: { folds = [[start, end], ...] }
-- - Lua expresses intent (cursor / level / mode / language)
-- - Python decides meaning

local M = {}

-- =====================================================================
-- Defaults (DATA ONLY – no vim calls here!)
-- =====================================================================

local DEFAULTS = {
  -- Command used to invoke Curate
  cmd = { "curate" },

  -- File extension per filetype when writing temp files
  ext_by_ft = {
    python   = ".py",
    lua      = ".lua",
    markdown = ".md",
    md       = ".md",
  },

  -- Map Neovim 'filetype' → Curate 'language'
  language_by_ft = {
    python   = "python",
    lua      = "lua",
    markdown = "markdown",
    md       = "markdown",
  },

  -- Notify on errors
  notify = true,
}

local CONFIG = vim.deepcopy(DEFAULTS)

-- =====================================================================
-- Setup
-- =====================================================================

function M.setup(opts)
  CONFIG = vim.tbl_deep_extend(
    "force",
    vim.deepcopy(DEFAULTS),
    opts or {}
  )
end

-- =====================================================================
-- Fold safety / policy
-- =====================================================================

--- Lock buffer into deterministic manual fold behavior.
local function ensure_manual_folds()
  vim.opt_local.foldmethod = "manual"
  vim.opt_local.foldenable = true
  vim.opt_local.foldlevel = 99

  -- CRITICAL: prevent Neovim from auto-opening folds
  vim.opt_local.foldopen = ""
end

--- @return boolean
local function buffer_has_folds()
  return vim.fn.foldlevel(1) > 0 or vim.fn.foldclosed(1) ~= -1
end

-- =====================================================================
-- Helpers: buffer → tempfile
-- =====================================================================

local function write_buffer_to_tempfile(buf)
  local ft  = vim.bo[buf].filetype
  local ext = (CONFIG.ext_by_ft and CONFIG.ext_by_ft[ft]) or ".txt"

  local tmp = vim.fn.tempname() .. ext
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)

  vim.fn.writefile(lines, tmp)
  return tmp
end

-- =====================================================================
-- Helpers: apply folds
-- =====================================================================

local function apply_folds(folds)
  ensure_manual_folds()

  for _, r in ipairs(folds or {}) do
    local a = tonumber(r[1])
    local b = tonumber(r[2])

    -- Curate contract: 1-based inclusive, fold only if a < b
    if a and b and a < b then
      vim.cmd(string.format("%d,%dfold", a, b))
    end
  end
end

local function notify_err(msg)
  if CONFIG.notify then
    vim.notify(msg, vim.log.levels.ERROR)
  end
end

-- =====================================================================
-- Core runner
-- =====================================================================

local function run_curate(mode, level)
  local buf = vim.api.nvim_get_current_buf()
  local cursor_line = vim.api.nvim_win_get_cursor(0)[1]

  ensure_manual_folds()

  -- -------------------------------------------------------------------
  -- TOGGLE BEHAVIOR (EXPLICIT, INTENTIONAL)
  -- -------------------------------------------------------------------
  if buffer_has_folds() then
    vim.cmd("normal! zE")
    return
  end

  -- -------------------------------------------------------------------
  -- Prepare Curate call
  -- -------------------------------------------------------------------
  local tmp = write_buffer_to_tempfile(buf)

  local ft = vim.bo[buf].filetype
  local language =
    (CONFIG.language_by_ft and CONFIG.language_by_ft[ft])
    or "unknown"

  local cmd = vim.deepcopy(CONFIG.cmd)

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

  -- -------------------------------------------------------------------
  -- Run
  -- -------------------------------------------------------------------
  vim.system(cmd, { text = true }, function(res)
    pcall(vim.loop.fs_unlink, tmp)

    if res.code ~= 0 then
      vim.schedule(function()
        notify_err(
          "Curate error:\n" ..
          (res.stderr or res.stdout or "")
        )
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
      apply_folds(payload.folds)
    end)
  end)
end

-- =====================================================================
-- Public API (intent only)
-- =====================================================================

function M.fold_local()
  run_curate("children", 0)
end

function M.fold_parent()
  run_curate("children", 1)
end

function M.fold_self()
  run_curate("self", 0)
end

return M
