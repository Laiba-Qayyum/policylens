from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.client import ApiError, PolicyLensClient

APP = str(Path(__file__).parent.parent / "ui" / "app.py")
ANSWER = {
    "answer": "15 days [1]",
    "sources": [{"source": "returns.txt", "page": 1}],
    "competing": [],
    "verified": True,
}
EMPTY_DOCS = {"documents": [], "total_chunks": 0}
EMPTY_ACTIVITY = {
    "events": [],
    "summary": {"uploads": 0, "questions": 0, "verified_questions": 0},
}


def ask_through_the_page(monkeypatch: pytest.MonkeyPatch, result=None, error=None) -> AppTest:
    def fake_ask(self, tenant, question):
        if error:
            raise error
        return result

    monkeypatch.setattr(PolicyLensClient, "ask", fake_ask)
    monkeypatch.setattr(PolicyLensClient, "documents", lambda self, tenant: EMPTY_DOCS)
    monkeypatch.setattr(PolicyLensClient, "activity", lambda self, tenant: EMPTY_ACTIVITY)
    page = AppTest.from_file(APP).run()
    page.text_input(key="question").set_value("How many days?")
    return page.button(key="ask").click().run()


def test_shows_the_answer_and_its_source(monkeypatch):
    page = ask_through_the_page(monkeypatch, ANSWER)

    assert any("15 days" in m.value for m in page.markdown)
    assert any("returns.txt, page 1" in c.value for c in page.caption)


def test_no_warning_when_the_answer_is_verified(monkeypatch):
    assert not ask_through_the_page(monkeypatch, ANSWER).warning


def test_warns_when_the_answer_is_unverified(monkeypatch):
    page = ask_through_the_page(monkeypatch, {**ANSWER, "verified": False})

    assert any("Unverified" in w.value for w in page.warning)


def test_lists_competing_files(monkeypatch):
    result = {**ANSWER, "competing": ["new.txt", "old.txt"]}

    page = ask_through_the_page(monkeypatch, result)

    assert any("new.txt, old.txt" in i.value for i in page.info)


def test_shows_an_api_error_instead_of_crashing(monkeypatch):
    page = ask_through_the_page(monkeypatch, error=ApiError("Cannot reach the API"))

    assert any("Cannot reach the API" in e.value for e in page.error)
