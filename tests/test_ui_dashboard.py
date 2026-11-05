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


def test_the_overview_shows_the_real_counts(monkeypatch):
    page = open_page(monkeypatch)

    assert {m.label: m.value for m in page.metric} == {
        "Documents": "2",
        "Chunks": "5",
        "Questions": "2",
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

    html = page_html(open_page(monkeypatch, docs=evil))

    assert "&lt;script&gt;" in html
    assert "<script>" not in html


def test_an_unreachable_api_shows_an_error_and_no_numbers(monkeypatch):
    page = open_page(monkeypatch, error=ApiError("Cannot reach the API at http://x"))

    assert any("Cannot reach the API" in e.value for e in page.error)
    assert not page.metric


def test_the_numbers_include_the_question_just_asked(monkeypatch):
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

    assert {m.label: m.value for m in page.metric}["Questions"] == "1"
