import argparse
import json
import sys

from .engine import fold_for_cursor, Action
from .query import best_entity_at_line
from .api import analyze_text


def main(argv=None):
    parser = argparse.ArgumentParser(prog="curate")
    parser.add_argument("file")
    parser.add_argument("--line", type=int, required=True)
    parser.add_argument("--action", required=True)
    args = parser.parse_args(argv)

    action_map = {
        "local": Action.TOGGLE_LOCAL,
        "minimum": Action.TOGGLE_MINIMUM,
        "code": Action.TOGGLE_CODE,
        "docs": Action.TOGGLE_DOCS,
    }

    try:
        action = action_map[args.action]
    except KeyError:
        sys.stderr.write("Unknown action: {}\n".format(args.action))
        return 2

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
