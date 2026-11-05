from pathlib import Path

from streamlit.proto.TextInput_pb2 import TextInput
from streamlit.testing.v1 import AppTest

from src.client import ApiError, PolicyLensClient

APP = str(Path(__file__).parent.parent / "ui" / "app.py")
KEY = "K" * 32
DOCS = {"documents": [], "total_chunks": 0}
ACTIVITY = {"events": [], "summary": {"uploads": 0, "questions": 0, "verified_questions": 0}}


def stub_api(monkeypatch, create_error=None, documents_error=None) -> dict:
    seen = {"created": [], "documents": []}

    def fake_create(self, name):
        seen["created"].append(name)
        if create_error:
            raise create_error
        return {"tenant": name, "api_key": KEY}

    def fake_documents(self, tenant):
        seen["documents"].append((tenant, dict(self._headers)))
        if documents_error:
            raise documents_error
        return DOCS

    monkeypatch.setattr(PolicyLensClient, "create_workspace", fake_create)
    monkeypatch.setattr(PolicyLensClient, "documents", fake_documents)
    monkeypatch.setattr(PolicyLensClient, "activity", lambda self, tenant: ACTIVITY)
    return seen


def html_of(page: AppTest) -> str:
    return "\n".join(m.value for m in page.markdown)


def sign_up(page: AppTest, company: str = "Acme Corporation") -> AppTest:
    page.text_input(key="company").set_value(company)
    return page.button(key="create").click().run()


def sign_in(page: AppTest, name: str, key: str) -> AppTest:
    page.text_input(key="signin_name").set_value(name)
    page.text_input(key="signin_key").set_value(key)
    return page.button(key="signin").click().run()


def continue_to_the_dashboard(page: AppTest) -> AppTest:
    page = page.checkbox(key="saved").check().run()
    return page.button(key="continue").click().run()


def test_a_signed_out_visitor_sees_the_sign_up_form_not_the_dashboard(monkeypatch):
    stub_api(monkeypatch)

    page = AppTest.from_file(APP).run()

    assert "Create your PolicyLens workspace" in html_of(page)
    assert "Your company policies. One intelligent place." in html_of(page)
    assert "Welcome to PolicyLens" not in html_of(page)


def test_the_workspace_address_follows_the_company_name(monkeypatch):
    stub_api(monkeypatch)
    page = AppTest.from_file(APP).run()

    page = page.text_input(key="company").set_value("Acme Corporation").run()

    assert "acme-corporation" in html_of(page)


def test_an_unusable_company_name_shows_a_message_and_creates_nothing(monkeypatch):
    seen = stub_api(monkeypatch)

    page = sign_up(AppTest.from_file(APP).run(), "\u65e5\u672c\u8a9e")

    assert any("letters or numbers" in e.value for e in page.error)
    assert seen["created"] == []


def test_creating_a_workspace_shows_the_key_once(monkeypatch):
    seen = stub_api(monkeypatch)

    page = sign_up(AppTest.from_file(APP).run())

    assert seen["created"] == ["acme-corporation"]
    assert [c.value for c in page.code] == [KEY]
    assert page.checkbox(key="saved").value is False


def test_continue_is_blocked_until_the_key_is_saved(monkeypatch):
    stub_api(monkeypatch)
    page = sign_up(AppTest.from_file(APP).run())

    assert page.button(key="continue").disabled is True

    page = page.checkbox(key="saved").check().run()

    assert page.button(key="continue").disabled is False


def test_continuing_opens_the_dashboard_with_the_new_key(monkeypatch):
    seen = stub_api(monkeypatch)
    page = sign_up(AppTest.from_file(APP).run())

    page = continue_to_the_dashboard(page)

    assert "Welcome to PolicyLens" in html_of(page)
    assert "acme-corporation" in html_of(page)
    assert seen["documents"][-1] == ("acme-corporation", {"X-API-Key": KEY.encode()})


def test_the_key_is_not_shown_again_after_continuing(monkeypatch):
    stub_api(monkeypatch)
    page = sign_up(AppTest.from_file(APP).run())

    page = continue_to_the_dashboard(page)

    assert not page.code
    assert KEY not in html_of(page)


def test_rerunning_the_page_does_not_create_the_workspace_again(monkeypatch):
    seen = stub_api(monkeypatch)
    page = sign_up(AppTest.from_file(APP).run())

    page.run()
    page.run()

    assert seen["created"] == ["acme-corporation"]


def test_a_taken_name_shows_the_server_message_and_no_key(monkeypatch):
    stub_api(monkeypatch, create_error=ApiError("That workspace name is already taken"))

    page = sign_up(AppTest.from_file(APP).run())

    assert any("already taken" in e.value for e in page.error)
    assert not page.code


def test_signing_in_with_a_valid_pair_opens_the_dashboard(monkeypatch):
    seen = stub_api(monkeypatch)

    page = sign_in(AppTest.from_file(APP).run(), "acme", "secret-key-1234567")

    assert "Welcome to PolicyLens" in html_of(page)
    assert seen["documents"][0] == ("acme", {"X-API-Key": b"secret-key-1234567"})


def test_a_wrong_pair_shows_one_generic_message_and_stays_signed_out(monkeypatch):
    stub_api(monkeypatch, documents_error=ApiError("Invalid or missing API key"))

    page = sign_in(AppTest.from_file(APP).run(), "acme", "wrong-secret-9999")

    messages = " ".join(e.value for e in page.error)
    assert "don't match" in messages
    assert "wrong-secret-9999" not in messages
    assert "workspace" not in page.session_state
    assert "Welcome to PolicyLens" not in html_of(page)


def test_an_unreachable_server_is_reported_as_such_when_signing_in(monkeypatch):
    stub_api(monkeypatch, documents_error=ApiError("Cannot reach the API at http://x"))

    page = sign_in(AppTest.from_file(APP).run(), "acme", "secret-key-1234567")

    assert any("Cannot reach" in e.value for e in page.error)


def test_the_sign_in_key_box_hides_what_is_typed(monkeypatch):
    stub_api(monkeypatch)

    page = AppTest.from_file(APP).run()

    assert page.text_input(key="signin_key").proto.type == TextInput.PASSWORD


def test_the_signed_in_dashboard_has_no_key_box(monkeypatch):
    stub_api(monkeypatch)
    page = AppTest.from_file(APP)
    page.session_state["workspace"] = "acme"
    page.session_state["workspace_key"] = "test-key-1234567890"

    page = page.run()

    assert [t for t in page.text_input if t.key == "api_key"] == []
    assert "acme" in html_of(page)


def test_signing_out_returns_to_the_sign_up_page(monkeypatch):
    stub_api(monkeypatch)
    page = AppTest.from_file(APP)
    page.session_state["workspace"] = "acme"
    page.session_state["workspace_key"] = "test-key-1234567890"
    page = page.run()

    page = page.button(key="signout").click().run()

    assert "Create your PolicyLens workspace" in html_of(page)
    assert "Welcome to PolicyLens" not in html_of(page)


def test_the_key_file_names_the_workspace_and_says_it_cannot_be_recovered():
    from ui.signup import key_file

    text = key_file("acme", KEY)

    assert "acme" in text
    assert KEY in text
    assert "cannot be recovered" in text
