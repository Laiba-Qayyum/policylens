import logging

import pytest

from src.log import get_logger, setup_logging


def test_line_shows_tenant_id(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging("INFO")
    get_logger("policylens", "acme").info("document uploaded")
    assert "tenant=acme document uploaded" in capsys.readouterr().err


def test_logs_without_tenant_use_dash(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging("INFO")
    logging.getLogger("some_library").info("started")
    assert "tenant=- started" in capsys.readouterr().err


def test_level_filters_lower_messages(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging("WARNING")
    get_logger("policylens", "acme").info("hidden")
    assert "hidden" not in capsys.readouterr().err
