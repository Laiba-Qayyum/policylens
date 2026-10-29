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
