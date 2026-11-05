from datetime import UTC, datetime

import pytest

from src.activity import ActivityLog


def ticking_clock():
    seconds = iter(range(1, 100))
    return lambda: datetime(2026, 1, 1, 0, 0, next(seconds), tzinfo=UTC)


def make_log(directory=None) -> ActivityLog:
    return ActivityLog(directory, clock=ticking_clock())


def test_recent_returns_the_newest_event_first():
    log = make_log()
    log.record("acme", "upload", "a.pdf")
    log.record("acme", "question", verified=True)

    events = log.recent("acme")

    assert [e["kind"] for e in events] == ["question", "upload"]
    assert events[1] == {
        "time": "2026-01-01T00:00:01+00:00",
        "kind": "upload",
        "detail": "a.pdf",
        "verified": None,
    }


def test_recent_respects_the_limit():
    log = make_log()
    for name in ["a.pdf", "b.pdf", "c.pdf"]:
        log.record("acme", "upload", name)

    assert [e["detail"] for e in log.recent("acme", limit=2)] == ["c.pdf", "b.pdf"]


def test_an_unknown_tenant_has_no_events():
    assert make_log().recent("ghost") == []


def test_tenants_have_separate_logs():
    log = make_log()
    log.record("acme", "upload", "a.pdf")
    log.record("beta", "upload", "b.pdf")

    assert [e["detail"] for e in log.recent("acme")] == ["a.pdf"]
    assert [e["detail"] for e in log.recent("beta")] == ["b.pdf"]


def test_summary_counts_uploads_questions_and_verified_questions():
    log = make_log()
    log.record("acme", "upload", "a.pdf")
    log.record("acme", "question", verified=True)
    log.record("acme", "question", verified=False)
    log.record("acme", "question", verified=True)

    assert log.summary("acme") == {"uploads": 1, "questions": 3, "verified_questions": 2}


def test_summary_of_an_unknown_tenant_is_all_zero():
    assert make_log().summary("ghost") == {"uploads": 0, "questions": 0, "verified_questions": 0}


def test_events_survive_a_restart(tmp_path):
    first = make_log(tmp_path)
    first.record("acme", "upload", "a.pdf")
    first.record("acme", "question", verified=True)

    second = make_log(tmp_path)

    assert second.recent("acme") == first.recent("acme")
    assert second.summary("acme")["questions"] == 1


def test_an_unsafe_tenant_id_is_rejected_and_writes_nothing(tmp_path):
    log = make_log(tmp_path)

    with pytest.raises(ValueError):
        log.record("../evil", "upload", "a.pdf")

    assert list(tmp_path.iterdir()) == []
