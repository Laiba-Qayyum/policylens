from datetime import date
from pathlib import Path

import pytest

from src.cli import parse_args


def test_parse_args_reads_tenant_files_and_question() -> None:
    args = parse_args(
        ["--tenant", "acme", "--file", "a.txt", "--file", "b.txt", "--question", "How many days?"]
    )

    assert args.tenant == "acme"
    assert args.files == [Path("a.txt"), Path("b.txt")]
    assert args.question == "How many days?"
    assert args.min_score == 0.15


def test_parse_args_requires_a_question() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--tenant", "acme", "--file", "a.txt"])


def test_parse_args_reads_a_date_after_the_at_sign() -> None:
    args = parse_args(
        ["--tenant", "acme", "--file", "a.txt@2025-01-01", "--file", "b.txt", "--question", "q"]
    )

    assert args.files == [Path("a.txt"), Path("b.txt")]
    assert args.dates == {Path("a.txt"): date(2025, 1, 1)}


def test_parse_args_rejects_a_bad_date() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--tenant", "acme", "--file", "a.txt@not-a-date", "--question", "q"])
