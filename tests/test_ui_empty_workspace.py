from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.client import ApiError, PolicyLensClient

APP = str(Path(__file__).parent.parent / "ui" / "app.py")
EMPTY_DOCS = {"documents": [], "total_chunks": 0}
DOCS = {"documents": [{"source": "hr.pdf", "chunks": 4}], "total_chunks": 4}
ACTIVITY = {"events": [], "summary": {"uploads": 0, "questions": 0, "verified_questions": 0}}


def open_page(monkeypatch, docs=EMPTY_DOCS, error=None) -> AppTest:
    def fake_documents(self, tenant):
        if error:
            raise error
        return docs

    monkeypatch.setattr(PolicyLensClient, "documents", fake_documents)
    monkeypatch.setattr(PolicyLensClient, "activity", lambda self, tenant: ACTIVITY)
    page = AppTest.from_file(APP)
    page.session_state["workspace"] = "acme"
    page.session_state["workspace_key"] = "test-key-1234567890"
    return page.run()


def test_a_workspace_without_documents_is_told_to_upload_first(monkeypatch):
    page = open_page(monkeypatch)

    assert any("Upload a document first" in i.value for i in page.info)


def test_the_hint_is_gone_once_there_is_a_document(monkeypatch):
    page = open_page(monkeypatch, docs=DOCS)

    assert not any("Upload a document first" in i.value for i in page.info)


def test_no_hint_when_the_api_cannot_be_reached(monkeypatch):
    page = open_page(monkeypatch, error=ApiError("Cannot reach the API"))

    assert not any("Upload a document first" in i.value for i in page.info)


def test_the_documents_tab_says_to_click_upload_after_choosing_files(monkeypatch):
    page = open_page(monkeypatch, docs=DOCS)

    assert any("click Upload" in c.value for c in page.caption)
