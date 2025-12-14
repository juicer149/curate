-- tests/lua/utils.lua
-- Shared deterministic helpers for Lua tests

local M = {}

-- Deterministic seeded line generator
-- Matches Python fuzzing style
function M.seeded_lines(min_line, max_line, count, seed)
  math.randomseed(seed)

  local out = {}
  for _ = 1, count do
    table.insert(out, math.random(min_line, max_line))
  end

  table.sort(out)
  return out
end

return M
