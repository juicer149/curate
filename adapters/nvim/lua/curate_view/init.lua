-- curate_view: Neovim adapter for Curate.
--
-- Zoom out through the structural path at the cursor:
--
--   buffer text + cursor line
--     -> `curate chain - --line N`     (Python: producer -> curation -> ScopeSet)
--     -> chain of scopes, innermost first
--     -> one manual fold over chain[level]
--
-- <leader>F folds the function at the cursor, or else the whole file down to
-- its outline (`curate outline`): functions one line each, classes showing
-- their methods, every Markdown heading visible.
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
  -- The filetype is sent as the language; Curate resolves it against its
  -- language files. Map here only filetypes whose name Curate does not know.
  languages = {}, -- filetype -> Curate language
  -- Closed folds show their first line with its own highlighting and a
  -- dimmed line count. Set in windows where curate_view folds; false = leave
  -- foldtext alone.
  foldtext = true,
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

local FOLDTEXT = "v:lua.require'curate_view'.foldtext()"

local function ensure_manual_folds()
  -- Only switch when needed: re-setting fold options can reopen other folds.
  if vim.wo.foldmethod ~= "manual" then
    vim.wo.foldmethod = "manual"
  end
  vim.wo.foldenable = true
  if CONFIG.foldtext and vim.wo.foldtext ~= FOLDTEXT then
    vim.wo.foldtext = FOLDTEXT
    vim.opt_local.fillchars:append({ fold = " " })
  end
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
-- Fold text
-- ============================================================================

-- Highlight group per byte of a line, from Tree-sitter when the buffer has a
-- parser and a highlights query, else from legacy syntax. Empty when neither.
local function line_highlights(buf, lnum, line)
  local groups = {}
  local row = lnum - 1

  local ok, parser = pcall(vim.treesitter.get_parser, buf)
  if ok and parser then
    -- Parse just this row where supported (injections included); a full
    -- parse is incremental and cached otherwise.
    if not pcall(parser.parse, parser, { row, 0, row + 1, 0 }) then
      pcall(parser.parse, parser)
    end
    parser:for_each_tree(function(tree, ltree)
      local query = vim.treesitter.query.get(ltree:lang(), "highlights")
      if not query then
        return
      end
      for id, node in query:iter_captures(tree:root(), buf, row, row + 1) do
        local name = query.captures[id]
        if name:sub(1, 1) ~= "_" and name ~= "spell" and name ~= "nospell" then
          local sr, sc, er, ec = node:range()
          if sr <= row and er >= row then
            local from = sr < row and 0 or sc
            local to = er > row and #line or ec
            for c = from, to - 1 do
              groups[c] = "@" .. name .. "." .. ltree:lang()
            end
          end
        end
      end
    end)
    if next(groups) ~= nil then
      return groups
    end
  end

  if vim.bo[buf].syntax ~= "" then
    for c = 0, #line - 1 do
      local id = vim.fn.synID(lnum, c + 1, 1)
      if id ~= 0 then
        groups[c] = vim.fn.synIDattr(vim.fn.synIDtrans(id), "name")
      end
    end
  end
  return groups
end

-- { {text, hl}, ... } for one buffer line, tabs expanded.
local function line_chunks(buf, lnum)
  local line = vim.api.nvim_buf_get_lines(buf, lnum - 1, lnum, false)[1] or ""
  local groups = line_highlights(buf, lnum, line)
  local tab = string.rep(" ", vim.bo[buf].tabstop)

  local chunks, text, group = {}, "", nil
  for c = 0, #line - 1 do
    local g = groups[c]
    if g ~= group and text ~= "" then
      table.insert(chunks, { text, group or "Folded" })
      text = ""
    end
    group = g
    local ch = line:sub(c + 1, c + 1)
    text = text .. (ch == "\t" and tab or ch)
  end
  if text ~= "" then
    table.insert(chunks, { text, group or "Folded" })
  end
  return chunks
end

-- The fold text for lines start..end: the first line as it looks in the
-- buffer, then a dimmed count of the lines the fold holds.
function M.render_fold(buf, start, finish)
  local chunks = line_chunks(buf, start)
  table.insert(chunks, { " ··· " .. (finish - start + 1), "Comment" })
  return chunks
end

-- 'foldtext' entry point (set by ensure_manual_folds).
function M.foldtext()
  return M.render_fold(vim.api.nvim_get_current_buf(), vim.v.foldstart, vim.v.foldend)
end

-- ============================================================================
-- Python bridge
-- ============================================================================

-- Run `curate <args>` on the buffer's text; the decoded JSON, or nil after
-- telling the user what went wrong.
local function run(buf, args)
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  local source = table.concat(lines, "\n") .. "\n"
  local cmd = vim.list_extend(vim.deepcopy(CONFIG.cmd), args)

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
  if not decoded_ok or type(data) ~= "table" then
    notify("invalid JSON from curate", vim.log.levels.ERROR)
    return nil
  end
  return data
end

-- The language to ask Curate for: the filetype, unless mapped in setup().
local function buffer_language(buf)
  local ft = vim.bo[buf].filetype
  if ft == "" then
    notify("buffer has no filetype")
    return nil
  end
  return CONFIG.languages[ft] or ft
end

local function fetch_chain(buf, line, language)
  local data = run(buf, { "chain", "-", "--line", tostring(line), "--language", language })
  if not data or type(data.chain) ~= "table" then
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

  local language = buffer_language(buf)
  if not language then
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

-- Fold the whole file down to its outline: functions as one line each,
-- classes and Markdown headings visible with their contents folded.
-- Replaces the folds in the window.
function M.outline()
  local buf = vim.api.nvim_get_current_buf()
  local language = buffer_language(buf)
  if not language then
    return
  end
  local data = run(buf, { "outline", "-", "--language", language })
  if not data or type(data.folds) ~= "table" then
    return
  end

  local line = cursor_line()
  ensure_manual_folds()
  pcall(vim.cmd, "normal! zE")
  STATE[buf] = nil
  for _, f in ipairs(data.folds) do
    create_fold(f)
  end
  pcall(vim.api.nvim_win_set_cursor, 0, { line, 0 })
  if #data.folds == 0 then
    notify("nothing to fold in the outline")
  end
end

-- Inside a function or method: fold it, as the outline shows it (zooming
-- through the scopes on the way, so <leader>u steps back in).
-- Anywhere else, or pressed again: the outline of the whole file.
function M.fold_max()
  local st = current_state()
  if not st then
    return
  end

  -- The outermost scope at the cursor that the outline folds whole.
  local target = 0
  for i, s in ipairs(st.chain) do
    if s.outline == "closed" then
      target = i
    end
  end

  if target > st.level then
    ensure_manual_folds()
    while st.level < target do
      st.level = st.level + 1
      create_fold(st.chain[st.level])
    end
    restore_cursor(st)
    return
  end

  M.outline()
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
-- opts.languages table, filetype -> Curate language, for filetypes Curate
--                does not know by name (default: none; the filetype is sent)
-- opts.foldtext  true (default): first line + line count; false: leave it alone
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
      fold_max = "Curate: fold this function, or outline the file",
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
