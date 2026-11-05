from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.client import PolicyLensClient

APP = str(Path(__file__).parent.parent / "ui" / "app.py")


def test_the_page_has_animations_that_respect_reduced_motion(monkeypatch):
    monkeypatch.setattr(
        PolicyLensClient, "documents", lambda self, tenant: {"documents": [], "total_chunks": 0}
    )
    monkeypatch.setattr(
        PolicyLensClient,
        "activity",
        lambda self, tenant: {
            "events": [],
            "summary": {"uploads": 0, "questions": 0, "verified_questions": 0},
        },
    )

    page = AppTest.from_file(APP).run()
    html = "\n".join(m.value for m in page.markdown)

    assert "@keyframes" in html
    assert "prefers-reduced-motion" in html
