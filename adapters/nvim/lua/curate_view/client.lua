-- adapters/nvim/lua/curate_view/client.lua
--
-- Neovim ↔ Curate bridge.
--
-- Design principles:
-- - Lua owns UX + state (level progression)
-- - Python owns structure + semantics
-- - No implicit toggles
-- - No editor-based fold detection
-- - Deterministic, mechanical behavior

local M = {}

-- =====================================================================
-- Constants
-- =====================================================================

local MAX_LEVEL = 999

-- =====================================================================
-- Defaults (DATA ONLY – no vim calls here!)
-- =====================================================================

local DEFAULTS = {
  cmd = { "curate" },

  ext_by_ft = {
    python   = ".py",
    lua      = ".lua",
    markdown = ".md",
    md       = ".md",
  },

  language_by_ft = {
    python   = "python",
    lua      = "lua",
    markdown = "markdown",
    md       = "markdown",
  },

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
-- Per-buffer state
-- =====================================================================

local STATE = {}

local function buf_state(buf)
  STATE[buf] = STATE[buf] or { level = 0 }
  return STATE[buf]
end

-- Cleanup on buffer destruction (buffer numbers are reused!)
vim.api.nvim_create_autocmd("BufWipeout", {
  callback = function(args)
    STATE[args.buf] = nil
  end,
})

local function current_state()
  local buf = vim.api.nvim_get_current_buf()
  return buf, buf_state(buf)
end

-- =====================================================================
-- Fold ownership / policy
-- =====================================================================

local function ensure_manual_folds()
  vim.opt_local.foldmethod = "manual"
  vim.opt_local.foldenable = true
  vim.opt_local.foldlevel = 99
  vim.opt_local.foldopen = ""
end

-- Clear only Curate-owned manual folds
local function clear_folds()
  vim.cmd("normal! zE")
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
  clear_folds()

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
  table.insert(cmd, tostring(level))
  table.insert(cmd, "--mode")
  table.insert(cmd, mode)
  table.insert(cmd, "--language")
  table.insert(cmd, language)
  table.insert(cmd, "--output")
  table.insert(cmd, "json")

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
-- Public API — mechanical, explicit intent
-- =====================================================================

-- Fold deeper (zoom out)
function M.fold_next()
  local _, state = current_state()
  state.level = state.level + 1
  run_curate("self", state.level)
end

-- Fold to maximal scope immediately
function M.fold_max()
  local _, state = current_state()
  state.level = MAX_LEVEL
  run_curate("self", state.level)
end

-- Unfold one level (zoom in)
function M.unfold_next()
  local _, state = current_state()
  state.level = math.max(0, state.level - 1)

  if state.level == 0 then
    clear_folds()
  else
    run_curate("self", state.level)
  end
end

-- Fully unfold everything
function M.unfold_all()
  local _, state = current_state()
  state.level = 0
  clear_folds()
end

-- Fold immediate children; does not participate in level progression
function M.fold_children()
  local _, state = current_state()
  state.level = 0
  run_curate("children", 0)
end

return M
