"""
How Curate scales with file size.

Generates Python files of ~100 to ~100,000 lines (classes, methods, nested
if/for/while/with) and times each stage separately:

    producer  source -> RawFactSet   (Tree-sitter parse + tree walk)
    curate    RawFactSet -> ScopeSet (laminar selection + addresses)
    chain     ScopeSet -> path at the middle line

Run from the repo root:

    .venv/bin/python scripts/bench_scaling.py
    .venv/bin/python scripts/bench_scaling.py --producer ast   # without tree-sitter
"""

from __future__ import annotations

import argparse
import ast
import random
import time

from curate.curation import curate
from curate.facts import RawFact, RawFactSet
from curate.geometry import Span
from curate.producers import PRODUCERS
from curate.relations import chain

SIZES = (100, 1_000, 10_000, 100_000)


def generate(n_lines: int, seed: int = 1) -> str:
    rnd = random.Random(seed)
    out: list[str] = []

    def body(indent: int, depth: int, budget: int) -> None:
        pad = "    " * indent
        while budget > 0:
            if depth < 4 and budget > 4 and rnd.random() < 0.18:
                header = rnd.choice(["if x:", "for i in range(3):", "while x:", "with open(p) as f:"])
                out.append(pad + header)
                used = rnd.randint(2, min(12, budget - 1))
                body(indent + 1, depth + 1, used)
                budget -= used + 1
                if header == "if x:" and budget > 2 and rnd.random() < 0.4:
                    out.append(pad + "else:")
                    body(indent + 1, depth + 1, 2)
                    budget -= 3
            else:
                out.append(pad + f"y = {rnd.randint(0, 99)}")
                budget -= 1

    while len(out) < n_lines:
        if rnd.random() < 0.3:
            out.append(f"class C{len(out)}:")
            for _ in range(rnd.randint(1, 5)):
                out.append(f"    def m{len(out)}(self):")
                body(2, 1, rnd.randint(4, 25))
                out.append("")
        else:
            out.append(f"def f{len(out)}(x):")
            body(1, 1, rnd.randint(4, 30))
            out.append("")
    return "\n".join(out) + "\n"


_AST_KINDS = {
    ast.ClassDef: "class", ast.FunctionDef: "function", ast.If: "if",
    ast.For: "for", ast.While: "while", ast.With: "with", ast.Try: "try",
}


def ast_producer(*, source: str, language: str) -> RawFactSet:
    """Stand-in producer using Python's ast (no tree-sitter needed)."""
    return RawFactSet.from_iter(
        RawFact(_AST_KINDS[type(n)], Span(n.lineno, n.end_lineno))
        for n in ast.walk(ast.parse(source))
        if type(n) in _AST_KINDS
    )


def best_of(fn, runs: int) -> tuple[float, object]:
    best, result = float("inf"), None
    for _ in range(runs):
        t = time.perf_counter()
        result = fn()
        best = min(best, time.perf_counter() - t)
    return best, result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--producer", default="treesitter", choices=("treesitter", "ast"))
    ap.add_argument("--huge", action="store_true", help="also run 1 000 000 lines (~10 s)")
    args = ap.parse_args()
    sizes = SIZES + ((1_000_000,) if args.huge else ())

    produce = ast_producer if args.producer == "ast" else PRODUCERS["treesitter"]()

    print(f"producer: {args.producer}  (best of 5; 1 run from 100k lines)\n")
    print(f"{'lines':>8} {'scopes':>7} {'producer':>10} {'curate':>10} {'chain':>9} {'total':>10}")
    for n in sizes:
        src = generate(n)
        lines = src.count("\n")
        runs = 5 if n <= 10_000 else 1

        t_prod, raw = best_of(lambda: produce(source=src, language="python"), runs)
        t_cur, ss = best_of(lambda: curate(raw.items), runs)
        t_chain, _ = best_of(lambda: chain(ss, lines // 2), runs)

        total = t_prod + t_cur + t_chain
        print(
            f"{lines:>8} {len(raw.items):>7} "
            f"{t_prod * 1e3:>8.1f}ms {t_cur * 1e3:>8.1f}ms "
            f"{t_chain * 1e3:>7.2f}ms {total * 1e3:>8.1f}ms"
        )


if __name__ == "__main__":
    main()
