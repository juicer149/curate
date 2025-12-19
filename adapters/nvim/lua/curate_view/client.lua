-- adapters/nvim/lua/curate_view/client.lua
--
-- Neovim ↔ Curate (Python) bridge.
-- This file is the ONLY layer that talks to Python.

local M = {}

local DEFAULTS = {
  -- Command used to invoke Curate.
  -- Prefer "python3 -m curate" since it works without installing the script.
  cmd = { "python3", "-m", "curate" },

  -- If you prefer the console_script entrypoint, set:
  -- cmd = { "curate" },

  -- Optional: file extension per filetype when writing temp files.
  ext_by_ft = {
    python = ".py",
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

--- @param folds table[]|nil
local function apply_folds(folds)
  for _, f in ipairs(folds or {}) do
    local a = tonumber(f.start)
    local b = tonumber(f["end"])

    -- Ignore invalid or zero/negative-length folds.
    -- Curate contract: start/end are 1-based and inclusive, and we only fold if start < end.
    if a and b and a < b then
      vim.cmd(string.format("%d,%dfold", a, b))
    end
  end
end

local function notify_err(msg)
  if not CONFIG.notify then return end
  vim.notify(msg, vim.log.levels.ERROR)
end

-- ------------------------------------------------------------
-- Core runner
-- ------------------------------------------------------------

--- Run Curate with a semantic action.
--- Toggle UX:
--- - If cursor is already inside a fold → clear folds (zE)
--- - Else → compute folds and apply them
--- @param action string One of: "local", "minimum", "code", "docs" (or whatever your CLI supports)
local function run_curate(action)
  local buf = vim.api.nvim_get_current_buf()
  local cursor_line = vim.api.nvim_win_get_cursor(0)[1]

  -- If we're already inside any fold, clear folds instead (simple toggle).
  if vim.fn.foldlevel(cursor_line) > 0 then
    vim.cmd("normal! zE")
    return
  end

  local tmp = write_buffer_to_tempfile(buf)

  local cmd = vim.deepcopy(CONFIG.cmd)
  -- Append args: <path> --line N --action <action>
  table.insert(cmd, tmp)
  table.insert(cmd, "--line")
  table.insert(cmd, tostring(cursor_line))
  table.insert(cmd, "--action")
  table.insert(cmd, action)

  -- Run asynchronously
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
    if not ok or type(payload) ~= "table" then
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
-- Public API
-- ------------------------------------------------------------

function M.fold_local()
  run_curate("local")
end

function M.fold_minimum()
  run_curate("minimum")
end

function M.fold_code()
  run_curate("code")
end

function M.fold_docs()
  run_curate("docs")
end

return M
