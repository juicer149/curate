# curate

[![test](https://github.com/juicer149/curate/actions/workflows/test.yml/badge.svg)](https://github.com/juicer149/curate/actions/workflows/test.yml)

Structural view of source code: turn a file into a tree of nested scopes,
then let tools ask "where am I?" and act on the answer.

The first consumer is Neovim folding. Put the cursor anywhere, press a key,
and the enclosing scope folds. Press again and the next scope out folds.

```
source ──► producer ──► RawFact(label, span) ──► curate() ──► ScopeSet ──► consumer
           tree-sitter                           laminar,      addresses,     nvim folds,
                                                 O(n log n)    at / chain     (later: RAG)
```

- **Producers** know a language. They emit raw facts: a label and a line span.
- **The core** knows no language. It selects a properly nested (laminar) set of
  scopes under a policy and gives each one an address in a prefix algebra.
- **Consumers** ask questions such as `chain(scopes, line)`: every scope that
  contains a line, innermost first.

## Install

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
{"line": 16, "chain": [
  {"address": [0, 1], "label": "if", "start": 15, "end": 17},
  {"address": [0], "label": "function", "start": 7, "end": 19}
]}
```

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
    load=_load,                 # returns the tree_sitter.Language
)
```

Nothing else is registered; the file name is the lookup. Add the grammar
package to the `treesitter` extra and the filetype to the Neovim plugin's
`languages`.

## Neovim

The plugin lives in the repo, in `adapters/nvim`. Add it to the runtime path
and call `setup`:

```lua
vim.opt.rtp:append("~/path/to/curate/adapters/nvim")
require("curate_view").setup()
```

| Key          | Action                                   |
|--------------|------------------------------------------|
| `<leader>f`  | fold the next enclosing scope            |
| `<leader>F`  | fold out to the outermost scope          |
| `<leader>u`  | unfold one level                         |
| `<leader>U`  | unfold everything (`zE`)                 |

Folds are ordinary manual folds owned by Neovim, so `za`, `zo` and friends keep
working, and several folds can exist at once. The plugin uses
`<repo>/.venv/bin/curate` when it exists and `curate` on `PATH` otherwise.

Options:

```lua
require("curate_view").setup({
  cmd = { "curate" },          -- command prefix
  languages = { python = "python", markdown = "markdown" },  -- filetype -> language
  keymaps = false,             -- or a table overriding the defaults
})
```

Run the headless tests with `make test-nvim`.

## Performance

Tree-sitter producer on generated Python, one process, `make bench`:

| lines   | scopes | producer | curate | chain  | total  |
|--------:|-------:|---------:|-------:|-------:|-------:|
| 1 000   | 159    | 7 ms     | 0.4 ms | 0.03 ms| 7 ms   |
| 10 000  | 1 549  | 72 ms    | 4 ms   | 0.4 ms | 76 ms  |
| 100 000 | 15 459 | 960 ms   | 43 ms  | 3.4 ms | 1.0 s  |

Parsing dominates. Process start-up adds about 40 ms per call from the editor.

## Status

- Languages: Python, Markdown.
- Next: fold text and appearance, more languages, a visibility plan that
  decides what to show rather than what to hide, and scope-aware retrieval
  for RAG.

See [docs/DESIGN.md](docs/DESIGN.md) for how the core works,
[docs/VISION.md](docs/VISION.md) for the longer picture and
[docs/PITFALLS.md](docs/PITFALLS.md) for editor hazards found along the way.

## License

MIT, see [LICENSE](LICENSE).
