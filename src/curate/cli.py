import json
import argparse
from .engine import fold_for_cursor, Action
from .query import best_entity_at_line
from .api import analyze_text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--line", type=int, required=True)
    p.add_argument("--action", required=True)
    args = p.parse_args()

    action_map = {
        "local": Action.TOGGLE_LOCAL,
        "minimum": Action.TOGGLE_MINIMUM,
        "code": Action.TOGGLE_CODE,
        "docs": Action.TOGGLE_DOCS,
    }

    action = action_map[args.action]

    src = open(args.file, "r", encoding="utf8").read()
    root = analyze_text(src)
    folds = fold_for_cursor(src, args.line, action)
    entity = best_entity_at_line(root, args.line)

    payload = {
        "action": args.action,
        "cursor_line": args.line,
        "entity": {
            "kind": entity.kind if entity else None,
            "name": entity.name if entity else None,
        },
        "folds": [
            {"start": a, "end": b}
            for a, b in folds
        ],
    }

    print(json.dumps(payload))
