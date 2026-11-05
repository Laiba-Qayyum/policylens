from pathlib import Path

from streamlit.proto.TextInput_pb2 import TextInput
from streamlit.testing.v1 import AppTest

from src.client import PolicyLensClient

APP = str(Path(__file__).parent.parent / "ui" / "app.py")


def test_the_page_has_an_api_key_box_that_hides_what_is_typed(monkeypatch):
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

    assert page.text_input(key="api_key").proto.type == TextInput.PASSWORD
