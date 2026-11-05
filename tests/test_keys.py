import pytest

from src.keys import parse_api_keys

GOOD_A = "a" * 16
GOOD_B = "b" * 16


def test_parses_one_key_per_tenant():
    assert parse_api_keys(f"acme:{GOOD_A},beta:{GOOD_B}") == {"acme": GOOD_A, "beta": GOOD_B}


def test_ignores_spaces_around_entries():
    assert parse_api_keys(f" acme : {GOOD_A} ") == {"acme": GOOD_A}


def test_an_empty_value_is_an_error():
    with pytest.raises(ValueError, match="No API keys"):
        parse_api_keys("   ")


def test_an_entry_without_a_colon_is_an_error():
    with pytest.raises(ValueError, match="tenant:key"):
        parse_api_keys(GOOD_A)


def test_a_short_key_is_an_error():
    with pytest.raises(ValueError, match="at least 16"):
        parse_api_keys("acme:short")


def test_an_unsafe_tenant_name_is_an_error():
    with pytest.raises(ValueError, match="tenant name"):
        parse_api_keys(f"../evil:{GOOD_A}")
