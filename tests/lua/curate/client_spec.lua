-- tests/lua/curate/client_spec.lua
--
-- Tests for the Neovim ↔ Curate Lua client.
-- These tests mock all Neovim APIs and only verify integration logic.

local client = require("curate.client")

describe("curate.client", function()
  local original_vim

  before_each(function()
    -- Spara global vim så vi kan återställa efter testet
    original_vim = vim

    -- Mocka vim API
    vim = {
      api = {
        nvim_get_current_buf = function() return 1 end,
        nvim_win_get_cursor = function() return { 29, 0 } end,
        nvim_buf_get_lines = function()
          return {
            "def f():",
            "    pass",
          }
        end,
      },
      fn = {
        tempname = function() return "/tmp/curate_test" end,
        writefile = function() end,
        foldlevel = function() return 0 end,
      },
      loop = {
        fs_unlink = function() end,
      },
      cmd = function(_) end,
      notify = function(_) end,
      json = {
        decode = function()
          return {
            folds = {
              { start = 29, ["end"] = 30 },
            },
          }
        end,
      },
      schedule = function(fn) fn() end,
    }

    -- Mocka async system-call
    vim.system = function(_, _, cb)
      cb({
        code = 0,
        stdout = '{"folds":[{"start":29,"end":30}]}',
      })
    end
  end)

  after_each(function()
    -- Återställ vim globalt
    vim = original_vim
  end)

  it("applies folds returned by curate", function()
    local commands = {}

    vim.cmd = function(cmd)
      table.insert(commands, cmd)
    end

    client.fold_local()

    assert.are.same(
      {
        "normal! zE",
        "29,30fold",
      },
      commands
    )
  end)
end)
