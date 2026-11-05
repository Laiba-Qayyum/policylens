import pytest

from ui.signup import company_error, workspace_slug


@pytest.mark.parametrize(
    ("company", "slug"),
    [
        ("Acme Corporation", "acme-corporation"),
        ("  Acme & Sons, Ltd.  ", "acme-sons-ltd"),
        ("Caf\u00e9 M\u00fcnster", "cafe-munster"),
        ("UPPER_case-1", "upper-case-1"),
        ("../evil", "evil"),
        ("\u65e5\u672c\u8a9e", ""),
        ("", ""),
    ],
)
def test_workspace_slug_turns_a_company_name_into_a_safe_address(company, slug):
    assert workspace_slug(company) == slug


def test_a_long_name_is_cut_to_64_characters():
    assert workspace_slug("a" * 100) == "a" * 64


def test_cutting_a_long_name_never_leaves_a_trailing_dash():
    assert workspace_slug("a" * 63 + " b") == "a" * 63


@pytest.mark.parametrize("company", ["", "   "])
def test_an_empty_company_name_asks_for_a_name(company):
    assert "Enter" in company_error(company)


def test_a_name_without_letters_or_numbers_explains_why():
    assert "letters or numbers" in company_error("\u65e5\u672c\u8a9e")


def test_a_usable_company_name_has_no_error():
    assert company_error("Acme Corporation") is None
