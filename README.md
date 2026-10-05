# curate

[![test](https://github.com/juicer149/curate/actions/workflows/test.yml/badge.svg)](https://github.com/juicer149/curate/actions/workflows/test.yml)

Structural view of code and documents: turn a file into a tree of nested scopes,
then let tools ask "where am I?" and act on the answer.

The first consumer is Neovim: fold and navigate a file by its structure.
Zoom out from the cursor one scope at a time, fold the whole file level by
level (functions, then classes; or `###`, then `##`), and jump between the
definitions or headings that are visible. Python and Markdown for now.

![Python: outline, then zoom out from a loop](docs/assets/python.gif)
![Markdown: heading levels, then zoom out from a section](docs/assets/markdown.gif)

## Quick start (Neovim)

Needs Neovim 0.10+ and Python 3.10+. Neovim's own tree-sitter parsers are not
needed: curate parses with tree-sitter on the Python side.

1. Clone and install. This creates `.venv` inside the repo, and the plugin
   finds it on its own:

   ```sh
   git clone https://github.com/juicer149/curate ~/src/curate
   cd ~/src/curate
   make install
   ```

2. Add the plugin. With [lazy.nvim](https://github.com/folke/lazy.nvim):

   ```lua
   {
     dir = "~/src/curate/adapters/nvim",
     name = "curate_view",
     config = function()
       require("curate_view").setup()
     end,
   }
   ```

   Without a plugin manager:

   ```lua
   vim.opt.rtp:append("~/src/curate/adapters/nvim")
   require("curate_view").setup()
   ```

3. Open a `.py` or `.md` file and press `<leader>F` for its outline.
   The [keys](#keys) are below.

## How it works

```
source ──► producer ──► RawFact(label, span) ──► curate() ──► ScopeSet ──► consumer
           tree-sitter                           laminar,      addresses,     nvim folds,
                                                 O(n log n)    at / chain,    (later: RAG)
                                                               outline
```

- **Producers** know a language. They emit raw facts: a label and a line span.
- **The core** knows no language. It selects a properly nested (laminar) set of
  scopes under a policy and gives each one an address in a prefix algebra.
- **Consumers** ask questions such as `chain(scopes, line)`: every scope that
  contains a line, innermost first.

## Install (CLI and library)

```sh
git clone https://github.com/juicer149/curate
cd curate
make install        # .venv with .[dev,treesitter]
make test
```

Python 3.10+. Tree-sitter is an optional extra; the core has no dependencies.

## CLI

```sh
curate chain tests/fixtures/python_minimal.py --line 16
```

```json
{"line": 16, "children": [], "chain": [
  {"address": [0, 1], "label": "if", "start": 15, "end": 17, "outline": null},
  {"address": [0], "label": "function", "start": 7, "end": 19, "outline": "closed"}
]}
```

```sh
curate outline tests/fixtures/python_minimal.py
```

```json
{"folds": [{"start": 7, "end": 19}, {"start": 23, "end": 24}],
 "level": 1, "levels": 2, "heads": [7, 11, 22, 23]}
```

`chain` is the structural path at a line, innermost first. `outline` is the
set of line ranges to fold so that only the file's skeleton shows: functions
fold whole, classes keep their line and show their methods, Markdown keeps
every heading. The ranges never overlap. Each language decides which of its
scopes are part of the outline, and `"outline"` in `chain` says how a scope
shows there. `--level N` folds further, one nesting level per step (level 2
in Python folds classes whole); `"levels"` is how many the file has and
`"heads"` the naming line of every outline entry. `"children"` in `chain` are
the scopes directly inside the innermost one, which the line lies between.
A scope whose naming line is not its first (a decorated `def`) also has
`"head"`.

Lines are 1-based and inclusive. The language comes from the file suffix
(`.py`, `.md`) unless `--language` is given; `FILE` may be `-` for stdin, which
needs `--language`. Exit code 1 when the producer fails, 2 when the language
cannot be told; both with a message on stderr.

## Languages

| Language | Names            | Suffixes            | Scopes                                   |
|----------|------------------|---------------------|------------------------------------------|
| Python   | `python`, `py`   | `.py`, `.pyi`       | classes, functions, compound statements |
| Markdown | `markdown`, `md` | `.md`, `.markdown`  | sections, labelled `h1`–`h6`             |

Each language is one file in
[`src/curate/producers/treesitter/languages/`](src/curate/producers/treesitter/languages/).
To add one, create `<name>.py` there with:

```python
NAMES = ("rust", "rs")          # first is the canonical name
EXTENSIONS = (".rs",)
SPEC = LanguageSpec(
    scopes={"function_item": "function", "impl_item": "impl"},
    outline={"impl": "open", "function": "closed"},  # optional
    load=_load,                 # returns the tree_sitter.Language
)
```

Nothing else is registered; the file name is the lookup. Add the grammar
package to the `treesitter` extra. The Neovim plugin sends the buffer's
filetype as the language, so a filetype that matches one of `NAMES` works
without touching the plugin.

## Neovim

The plugin lives in the repo, in `adapters/nvim`; see
[Quick start](#quick-start-neovim) to install it.

### Keys

Lowercase keys work on the scopes around the cursor, uppercase keys on the
whole file:

| Key          | Works on      | Action |
|--------------|---------------|--------|
| `<leader>f`  | the cursor    | zoom out: fold the enclosing scope, then the one around it, and so on |
| `<leader>u`  | the cursor    | zoom back in, one scope per press |
| `<leader>F`  | the file      | fold one level further per press: first the outline, then one nesting level at a time |
| `<leader>U`  | the file      | unfold one level per press, back to the outline, then everything |
| `<leader>j`  | the file      | jump to the next visible `def`, `class` or heading |
| `<leader>k`  | the file      | jump to the previous one |

**Zooming (`f`, `u`).** Inside an `if`, the first `<leader>f` folds the `if`,
the next its function, then the class. On a line *between* the scopes inside
one, a blank line between two methods or a statement between two `if`s, the
first press folds those scopes to their first lines and the next folds the
scope itself. Outside every scope, `<leader>f` does nothing. On a `def` or
`class` line it folds that definition.

**Levels (`F`, `U`).** `<leader>F` never unfolds and does not care where the
cursor is. Its first press gives the outline: in Python, functions one line
each and classes showing their methods; in Markdown, every heading. Each
press after that folds one nesting level whole, from the inside out: a Python
class becomes one line; in Markdown the `###` sections fold into their `##`,
then the `##` into their `#`. `<leader>U` takes the same steps back.

Decorators stay on their own lines above a folded definition, so
`@dataclass` or `@login_required` is still visible.

Folds are ordinary manual folds owned by Neovim, so `za`, `zo` and friends keep
working, and several folds can exist at once. A closed fold shows its first
line with the buffer's own highlighting and a dimmed count of the lines it
holds, e.g. `def add(self, item): ··· 9`, without the colorscheme's `Folded`
background. To get that back: `:hi link CurateFolded Folded`.

### Changing keys

`keymaps` is merged with the defaults, so name only the keys you change.
`false` drops one key; `keymaps = false` sets none, and you map the functions
yourself:

```lua
require("curate_view").setup({
  keymaps = {
    next_head = "]]",   -- instead of <leader>j
    prev_head = "[[",   -- instead of <leader>k
    unfold_all = false, -- no key for this one
  },
})

-- or, with keymaps = false:
local curate = require("curate_view")
vim.keymap.set("n", "<leader>f", curate.fold_next)   -- zoom out
vim.keymap.set("n", "<leader>u", curate.unfold_next) -- zoom in
vim.keymap.set("n", "<leader>F", curate.fold_max)    -- fold the file one level
vim.keymap.set("n", "<leader>U", curate.unfold_all)  -- unfold the file one level
vim.keymap.set("n", "<leader>j", curate.next_head)   -- next def, class or heading
vim.keymap.set("n", "<leader>k", curate.prev_head)   -- previous one
```

### Other options

```lua
require("curate_view").setup({
  cmd = { "curate" },                -- default: <repo>/.venv/bin/curate if it exists, else curate on PATH
  languages = { mdx = "markdown" },  -- only filetypes Curate does not know by name
  foldtext = false,                  -- keep your own 'foldtext' (default: true)
})
```

### When nothing happens

Messages start with `curate:`.

- `could not run …`: the command was not found. Run `make install` in the
  repo so that `.venv/bin/curate` exists, or set `cmd`.
- `no structure support for language '…'`: the buffer's filetype is not a
  language curate knows (`:set filetype?`). Map it with `languages`.
- `no enclosing scope here`: `<leader>f` outside every scope; there is
  nothing around the cursor to fold.

Run the headless tests with `make test-nvim`.

## Performance

Tree-sitter producer on generated Python, one process, `make bench`:

| lines   | scopes | producer | curate | chain  | total  |
|--------:|-------:|---------:|-------:|-------:|-------:|
| 1 000   | 159    | 7 ms     | 0.4 ms | 0.01 ms| 7 ms   |
| 10 000  | 1 549  | 66 ms    | 4 ms   | 0.06 ms| 70 ms  |
| 100 000 | 15 459 | 890 ms   | 47 ms  | 0.9 ms | 0.93 s |
| 1 000 000 | 154 832 | 10.4 s | 0.52 s | 12 ms | 10.9 s |

Parsing dominates, and every column grows linearly up to a million lines
(`make bench-huge` adds that row). Process start-up adds about 40 ms per
call from the editor.

## Status

- Languages: Python, Markdown.
- Neovim: zoom folding from the cursor, outline levels for the whole file,
  jumps between definitions and headings, fold text that keeps decorators.
- Next: more languages (HTML, CSS, JavaScript, JSON, YAML), a docstring or
  first-paragraph summary in the fold text, a visibility plan that decides
  what to show rather than what to hide, and scope-aware retrieval for RAG.

`examples/demo.py` shows the core on hand-made facts, without tree-sitter.

See [docs/DESIGN.md](docs/DESIGN.md) for how the core works,
[docs/VISION.md](docs/VISION.md) for the longer picture and
[docs/PITFALLS.md](docs/PITFALLS.md) for editor hazards found along the way.

## License

MIT, see [LICENSE](LICENSE).
