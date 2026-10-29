import argparse
from datetime import date
from pathlib import Path

DEFAULT_MIN_SCORE = 0.15  # chosen from scripts/eval_cutoffs.py on a small sample


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask a question about your documents.")
    parser.add_argument("--tenant", required=True)
    parser.add_argument(
        "--file", dest="files", action="append", required=True, help="PATH or PATH@YYYY-MM-DD"
    )
    parser.add_argument("--question", required=True)
    parser.add_argument("--min-score", type=float, default=DEFAULT_MIN_SCORE)
    args = parser.parse_args(argv)

    paths: list[Path] = []
    args.dates = {}
    for value in args.files:
        if "@" in value:
            path_text, date_text = value.rsplit("@", 1)
            path = Path(path_text)
            try:
                args.dates[path] = date.fromisoformat(date_text)
            except ValueError:
                parser.error(f"invalid date in --file {value!r}: use YYYY-MM-DD")
        else:
            path = Path(value)
        paths.append(path)
    args.files = paths
    return args
