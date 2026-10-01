-- curate_view: Neovim adapter for Curate.
--
-- Zoom out through the structural path at the cursor:
--
--   buffer text + cursor line
--     -> `curate chain - --line N`     (Python: producer -> curation -> ScopeSet)
--     -> chain of scopes, innermost first
--     -> one manual fold over chain[level]
--
-- Curate knows nothing about Neovim; this file knows nothing about Tree-sitter.
-- The chain is cached per buffer and changedtick: only the first keypress at a
-- position calls Python, zooming further is instant.
--
-- Setup (lazy.nvim):
--   { dir = "~/path/to/curate/adapters/nvim", name = "curate_view",
--     config = function() require("curate_view").setup() end }

local M = {}

-- ============================================================================
-- Configuration
-- ============================================================================

-- The repository's own virtualenv if present, else `curate` on PATH.
-- This file lives at <repo>/adapters/nvim/lua/curate_view/init.lua.
local function default_cmd()
  local file = debug.getinfo(1, "S").source:sub(2)
  local repo = vim.fn.fnamemodify(file, ":p:h:h:h:h:h")
  local venv = repo .. "/.venv/bin/curate"
  if vim.fn.executable(venv) == 1 then
    return { venv }
  end
  return { "curate" }
end

local DEFAULTS = {
  cmd = nil, -- resolved in setup(): default_cmd()
  languages = { python = "python", markdown = "markdown" }, -- filetype -> Curate language
  keymaps = {
    fold_next = "<leader>f",
    fold_max = "<leader>F",
    unfold_next = "<leader>u",
    unfold_all = "<leader>U",
  },
}

local CONFIG = vim.deepcopy(DEFAULTS)
CONFIG.cmd = default_cmd()

-- ============================================================================
-- Per-buffer state
-- ============================================================================
-- STATE[buf] = {
--   tick   = changedtick the chain was computed for,
--   anchor = cursor line the chain was computed for,
--   chain  = { {start=, ["end"]=, label=, address=}, ... } innermost first,
--   level  = number of folds this zoom has created: chain[1..level] are folded,
-- }

local STATE = {}

vim.api.nvim_create_autocmd("BufWipeout", {
  callback = function(args)
    STATE[args.buf] = nil
  end,
})

local function notify(msg, level)
  vim.notify("curate: " .. msg, level or vim.log.levels.INFO)
end

-- ============================================================================
-- Folds
-- ============================================================================

local function ensure_manual_folds()
  -- Only switch when needed: re-setting fold options can reopen other folds.
  if vim.wo.foldmethod ~= "manual" then
    vim.wo.foldmethod = "manual"
  end
  vim.wo.foldenable = true
end

local function create_fold(s)
  vim.cmd(string.format("%d,%dfold", s.start, s["end"]))
end

-- Delete the closed fold that starts at s.start. Nested folds stay.
local function delete_fold(s)
  pcall(vim.api.nvim_win_set_cursor, 0, { s.start, 0 })
  pcall(vim.cmd, "normal! zd")
end

local function restore_cursor(st)
  pcall(vim.api.nvim_win_set_cursor, 0, { st.anchor, 0 })
end

-- ============================================================================
-- Python bridge
-- ============================================================================

local function fetch_chain(buf, line, language)
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  local source = table.concat(lines, "\n") .. "\n"

  local cmd = vim.list_extend(vim.deepcopy(CONFIG.cmd), {
    "chain", "-", "--line", tostring(line), "--language", language,
  })

  local ok, res = pcall(function()
    return vim.system(cmd, { text = true, stdin = source }):wait()
  end)
  if not ok then
    notify("could not run " .. CONFIG.cmd[1] .. " (" .. tostring(res) .. ")", vim.log.levels.ERROR)
    return nil
  end
  if res.code ~= 0 then
    notify(vim.trim(res.stderr or "unknown error"), vim.log.levels.ERROR)
    return nil
  end

  local decoded_ok, data = pcall(vim.json.decode, res.stdout or "")
  if not decoded_ok or type(data) ~= "table" or type(data.chain) ~= "table" then
    notify("invalid JSON from curate", vim.log.levels.ERROR)
    return nil
  end

  -- A one-line scope cannot be folded; skip it so every keypress changes the view.
  local chain = {}
  for _, s in ipairs(data.chain) do
    if s["end"] > s.start then
      table.insert(chain, s)
    end
  end
  return chain
end

-- ============================================================================
-- State
-- ============================================================================

local function cursor_line()
  return vim.api.nvim_win_get_cursor(0)[1]
end

-- The cached chain belongs to one position. It is valid while the text is
-- unchanged and the cursor is where the zoom started: on the anchor line, or
-- anywhere inside the fold the zoom has closed (you cannot move inside it).
local function still_valid(st, buf)
  if not st or #st.chain == 0 then
    return false
  end
  if st.tick ~= vim.api.nvim_buf_get_changedtick(buf) then
    return false
  end
  local line = cursor_line()
  if st.level == 0 then
    return line == st.anchor
  end
  local s = st.chain[st.level]
  return line >= s.start and line <= s["end"]
end

local function current_state()
  local buf = vim.api.nvim_get_current_buf()
  local st = STATE[buf]
  if still_valid(st, buf) then
    return st
  end

  local ft = vim.bo[buf].filetype
  local language = CONFIG.languages[ft]
  if not language then
    notify("no structure support for filetype '" .. ft .. "'")
    return nil
  end

  local line = cursor_line()
  local chain = fetch_chain(buf, line, language)
  if not chain then
    return nil
  end

  -- Neovim owns the folds: if the cursor is inside a closed fold that is one
  -- of the chain's scopes (folded earlier), continue the zoom from there.
  local level = 0
  local fs, fe = vim.fn.foldclosed(line), vim.fn.foldclosedend(line)
  if fs ~= -1 then
    for i, s in ipairs(chain) do
      if s.start == fs and s["end"] == fe then
        level = i
        break
      end
    end
  end

  st = {
    tick = vim.api.nvim_buf_get_changedtick(buf),
    anchor = line,
    chain = chain,
    level = level,
  }
  STATE[buf] = st
  return st
end

-- ============================================================================
-- Public API
-- ============================================================================

-- Zoom out one level: fold the next enclosing scope.
function M.fold_next()
  local st = current_state()
  if not st then
    return
  end
  if #st.chain == 0 then
    notify("no enclosing scope here")
    return
  end
  if st.level >= #st.chain then
    notify("already at the outermost scope")
    return
  end
  ensure_manual_folds()
  st.level = st.level + 1
  create_fold(st.chain[st.level])
  restore_cursor(st)
end

-- Zoom straight out to the outermost scope (creating every level on the way,
-- so zooming back in steps through them).
function M.fold_max()
  local st = current_state()
  if not st or #st.chain == 0 then
    return
  end
  ensure_manual_folds()
  while st.level < #st.chain do
    st.level = st.level + 1
    create_fold(st.chain[st.level])
  end
  restore_cursor(st)
end

-- Zoom in one level: delete the outermost fold of the current zoom.
-- Elsewhere (a fold made earlier, or after an edit) open the closed fold under
-- the cursor; nested folds inside it stay.
function M.unfold_next()
  local buf = vim.api.nvim_get_current_buf()
  local st = STATE[buf]
  if still_valid(st, buf) and st.level > 0 then
    delete_fold(st.chain[st.level])
    st.level = st.level - 1
    restore_cursor(st)
    return
  end
  if vim.fn.foldclosed(cursor_line()) ~= -1 then
    pcall(vim.cmd, "normal! zd")
  end
end

-- Open everything in the buffer.
function M.unfold_all()
  STATE[vim.api.nvim_get_current_buf()] = nil
  pcall(vim.cmd, "normal! zE")
end

-- opts.cmd       list, command that runs Curate (default: repo .venv, else PATH)
-- opts.languages table, filetype -> Curate language
-- opts.keymaps   table of action -> key, or false to set no keymaps
function M.setup(opts)
  opts = opts or {}
  CONFIG = vim.tbl_deep_extend("force", vim.deepcopy(DEFAULTS), opts)
  CONFIG.cmd = opts.cmd or default_cmd()
  if opts.keymaps == false then
    CONFIG.keymaps = false
  end

  if CONFIG.keymaps then
    local descs = {
      fold_next = "Curate: zoom out one scope",
      fold_max = "Curate: zoom out to outermost scope",
      unfold_next = "Curate: zoom in one scope",
      unfold_all = "Curate: unfold all",
    }
    for action, key in pairs(CONFIG.keymaps) do
      if key and M[action] then
        vim.keymap.set("n", key, M[action], { desc = descs[action] })
      end
    end
  end
end

return M
