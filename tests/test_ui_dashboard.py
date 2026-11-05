import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.client import ApiError, PolicyLensClient

APP = str(Path(__file__).parent.parent / "ui" / "app.py")
DOCS = {
    "documents": [{"source": "hr.pdf", "chunks": 4}, {"source": "returns.txt", "chunks": 1}],
    "total_chunks": 5,
}
ACTIVITY = {
    "events": [
        {"time": "2026-11-05T12:17:50+00:00", "kind": "question", "detail": "", "verified": True},
        {"time": "2026-11-05T12:10:00+00:00", "kind": "question", "detail": "", "verified": False},
        {
            "time": "2026-11-05T12:00:00+00:00",
            "kind": "upload",
            "detail": "hr.pdf",
            "verified": None,
        },
    ],
    "summary": {"uploads": 1, "questions": 2, "verified_questions": 1},
}
NO_ACTIVITY = {
    "events": [],
    "summary": {"uploads": 0, "questions": 0, "verified_questions": 0},
}
ANSWER = {
    "answer": "15 days [1]",
    "sources": [{"source": "returns.txt", "page": 1}],
    "competing": [],
    "verified": True,
}


def open_page(monkeypatch, docs=DOCS, activity=ACTIVITY, error=None) -> AppTest:
    def fake_documents(self, tenant):
        if error:
            raise error
        return docs

    def fake_activity(self, tenant):
        if error:
            raise error
        return activity

    monkeypatch.setattr(PolicyLensClient, "documents", fake_documents)
    monkeypatch.setattr(PolicyLensClient, "activity", fake_activity)
    return AppTest.from_file(APP).run()


def page_html(page: AppTest) -> str:
    return "\n".join(m.value for m in page.markdown)


def cards(page: AppTest) -> dict[str, str]:
    pattern = r'<div class="pl-num">(.*?)</div><div class="pl-label">(.*?)</div>'
    return {label: value for value, label in re.findall(pattern, page_html(page))}


def test_the_overview_cards_show_the_real_counts(monkeypatch):
    assert cards(open_page(monkeypatch)) == {
        "Documents": "2",
        "Indexed chunks": "5",
        "Questions asked": "2",
        "Answers with a valid citation": "1 of 2",
    }


def test_the_documents_tab_lists_each_file_with_its_chunks(monkeypatch):
    html = page_html(open_page(monkeypatch))

    assert "hr.pdf" in html
    assert "4 chunks" in html
    assert "returns.txt" in html


def test_the_activity_tab_describes_each_event_in_plain_words(monkeypatch):
    html = page_html(open_page(monkeypatch))

    assert "Uploaded hr.pdf" in html
    assert "Question answered, citation valid" in html
    assert "Question answered, no valid citation" in html
    assert "2026-11-05 12:17 UTC" in html


def test_file_names_are_escaped_before_they_reach_the_html(monkeypatch):
    evil = {"documents": [{"source": "<script>x</script>.pdf", "chunks": 1}], "total_chunks": 1}
    events = {
        "events": [
            {
                "time": "2026-11-05T12:00:00+00:00",
                "kind": "upload",
                "detail": "<b>x</b>.pdf",
                "verified": None,
            }
        ],
        "summary": {"uploads": 1, "questions": 0, "verified_questions": 0},
    }

    html = page_html(open_page(monkeypatch, docs=evil, activity=events))

    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;" in html
    assert "<script>" not in html
    assert "<b>x</b>" not in html


def test_an_unreachable_api_shows_an_error_and_no_cards(monkeypatch):
    page = open_page(monkeypatch, error=ApiError("Cannot reach the API at http://x"))

    assert any("Cannot reach the API" in e.value for e in page.error)
    assert cards(page) == {}


def test_the_cards_include_the_question_just_asked(monkeypatch):
    asked = []
    monkeypatch.setattr(PolicyLensClient, "ask", lambda self, tenant, q: asked.append(q) or ANSWER)
    monkeypatch.setattr(PolicyLensClient, "documents", lambda self, tenant: DOCS)
    monkeypatch.setattr(
        PolicyLensClient,
        "activity",
        lambda self, tenant: {
            "events": [],
            "summary": {
                "uploads": 0,
                "questions": len(asked),
                "verified_questions": len(asked),
            },
        },
    )
    page = AppTest.from_file(APP).run()
    page.text_input(key="question").set_value("How many days?")

    page = page.button(key="ask").click().run()

    assert cards(page)["Questions asked"] == "1"


def test_the_overview_shows_the_citation_rate_as_a_ring(monkeypatch):
    html = page_html(open_page(monkeypatch))

    assert '<div class="pl-ring-label">50%</div>' in html


def test_the_citation_rate_with_no_questions_does_not_divide_by_zero(monkeypatch):
    html = page_html(open_page(monkeypatch, activity=NO_ACTIVITY))

    assert "No questions yet" in html


def test_the_overview_lists_recent_activity_as_a_table(monkeypatch):
    html = page_html(open_page(monkeypatch))

    assert '<table class="pl-table">' in html
    assert "Document uploaded" in html
    assert "Question asked" in html
    assert "Citation valid" in html
    assert "No valid citation" in html


def test_the_page_says_when_the_api_is_connected(monkeypatch):
    connected = page_html(open_page(monkeypatch))
    broken = page_html(open_page(monkeypatch, error=ApiError("Cannot reach the API")))

    assert "API connected" in connected
    assert "API connected" not in broken


def test_the_page_has_a_welcome_header(monkeypatch):
    assert "Welcome to PolicyLens" in page_html(open_page(monkeypatch))
