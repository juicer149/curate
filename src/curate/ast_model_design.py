"""
curate/ast_model_design.py

This file is intentionally NON-EXECUTABLE.

It exists to document the conceptual AST model used by Curate
for semantic folding, before implementation details leak into code.

The goal of this model is to:
- cleanly separate CODE vs DOCS
- avoid special-casing in fold logic
- keep folding policy orthogonal to structure
- match Python AST semantics without mirroring it directly


=====================================================================
CORE IDEA
=====================================================================

Curate models source code as a tree of semantic branches.

Each branch represents a *structural unit* that can be folded.

Crucially:
- Code structure (module / class / function) is PRIMARY
- Documentation (docstrings) is SECONDARY
- These are modeled as separate objects, not as siblings


=====================================================================
AST BRANCH
=====================================================================

An AstBranch represents a single foldable semantic unit.

It does NOT know about children or traversal.
It only describes its own span and how it should fold.

Pseudo-definition:

    AstBranch:
        kind: "module" | "class" | "function" | "doc"
        head: (start_line, end_line | None)
        body: (start_line, end_line) | None
        span: (start_line, end_line)

Semantics:

- head:
    Lines that should always remain visible when folded.
    Examples:
      - class/function/module: 1 line (signature)
      - docstring: 2 lines (opening quotes + summary)

- body:
    The foldable portion of the branch.
    If body is None, the branch has nothing to fold.

- span:
    The full inclusive range covering head + body.


---------------------------------------------------------------------
Examples
---------------------------------------------------------------------

Class definition:

    class X:
        def a(): ...
        def b(): ...

AstBranch(kind="class"):
    head = (lineno, lineno)
    body = (lineno + 1, end_lineno)
    span = (lineno, end_lineno)


Docstring:

    '''
    Summary line
    More text
    '''

AstBranch(kind="doc"):
    head = (start, start + 1)
    body = (start + 2, end)
    span = (start, end)

If a docstring is only one or two lines long:
    body = None


=====================================================================
AST TREE
=====================================================================

An AstTree represents a semantic scope with structure.

Pseudo-definition:

    AstTree:
        primary: AstBranch          # code structure
        docs: AstBranch | None      # documentation for this scope
        children: tuple[AstTree]    # nested code scopes


Key rules:

- `primary` is always navigable
- `docs` is foldable but NOT navigable
- `docs` is NOT a child
- children are ONLY code scopes (class/function/module)


---------------------------------------------------------------------
Example mapping
---------------------------------------------------------------------

Source:

    class A:
        '''
        Docs
        '''
        def f(): ...

Tree:

    AstTree(
        primary = class A,
        docs = docstring of A,
        children = [
            AstTree(
                primary = function f,
                docs = docstring of f,
                children = []
            )
        ]
    )


=====================================================================
NAVIGATION SEMANTICS
=====================================================================

Cursor navigation always targets PRIMARY branches.

Rules:
- If cursor is inside a docstring, the enclosing primary scope is selected
- Doc branches never participate in navigation
- level traversal walks PRIMARY parents only

This keeps navigation intuitive and stable.


=====================================================================
FOLDING SEMANTICS
=====================================================================

Folding is a POLICY applied to the tree.
The tree itself contains no folding logic.

Policies operate on branches.

Examples:

-------------------------------------------------
fold_children = False  (uppercase F)
-------------------------------------------------

Fold the target scope itself:

    fold(target.primary.body)
    fold(target.docs.body)   # optional, policy-dependent


-------------------------------------------------
fold_children = True   (lowercase f)
-------------------------------------------------

Fold all immediate children:

    for child in target.children:
        fold(child.primary.body)
        fold(child.docs.body)


-------------------------------------------------
action = "docs"
-------------------------------------------------

Fold documentation only:

    fold(target.docs.body)
    for child in target.children:
        fold(child.docs.body)


-------------------------------------------------
action = "code"
-------------------------------------------------

Fold code only:

    fold(target.primary.body)
    for child in target.children:
        fold(child.primary.body)


Because docs and code are separate objects,
no special-casing by node kind is required.


=====================================================================
WHY THIS MODEL
=====================================================================

This design deliberately:

- avoids "if kind == doc" checks during folding
- prevents docs from polluting navigation
- keeps AST concerns separate from UX policy
- allows future secondary branches:
    - decorators
    - comments
    - type annotations
    - regions
    - LSP symbols

Most importantly:

    STRUCTURE is stable.
    POLICY is flexible.


=====================================================================
STATUS
=====================================================================

This file is a DESIGN CONTRACT.

Implementation must conform to this model,
not the other way around.
"""
