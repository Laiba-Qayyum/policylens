import argparse
from pathlib import Path

DEFAULT_MIN_SCORE = 0.15  # chosen from scripts/eval_cutoffs.py on a small sample


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask a question about your documents.")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--file", dest="files", type=Path, action="append", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--min-score", type=float, default=DEFAULT_MIN_SCORE)
    return parser.parse_args(argv)
