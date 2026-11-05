import pytest

from src.registry import TenantRegistry


def test_a_new_workspace_gets_a_key_that_opens_it():
    registry = TenantRegistry()

    key = registry.create("acme")

    assert len(key) >= 16
    assert registry.check("acme", key)


def test_a_wrong_key_or_an_unknown_workspace_is_rejected():
    registry = TenantRegistry()
    key = registry.create("acme")

    assert not registry.check("acme", "wrong-key-wrong-key-123")
    assert not registry.check("ghost", key)


def test_each_workspace_gets_its_own_key():
    registry = TenantRegistry()

    first = registry.create("acme")
    second = registry.create("globex")

    assert first != second
    assert not registry.check("globex", first)


def test_a_name_cannot_be_created_twice():
    registry = TenantRegistry()
    registry.create("acme")

    with pytest.raises(FileExistsError):
        registry.create("acme")


@pytest.mark.parametrize("name", ["", "Acme", "../evil", "has space", "a" * 65])
def test_invalid_names_are_rejected(name):
    with pytest.raises(ValueError):
        TenantRegistry().create(name)


def test_exists_tells_whether_a_workspace_was_created():
    registry = TenantRegistry()
    registry.create("acme")

    assert registry.exists("acme")
    assert not registry.exists("ghost")


def test_the_key_is_not_stored_but_still_works_after_a_restart(tmp_path):
    first = TenantRegistry(tmp_path)
    key = first.create("acme")

    stored = "".join(p.read_text(encoding="utf-8") for p in tmp_path.rglob("*") if p.is_file())

    assert key not in stored
    assert TenantRegistry(tmp_path).check("acme", key)


def test_a_key_with_non_ascii_characters_is_rejected_not_an_error():
    registry = TenantRegistry()
    registry.create("acme")

    assert not registry.check("acme", "s\u00e9cret-key-123456")


def test_an_invalid_name_writes_nothing(tmp_path):
    with pytest.raises(ValueError):
        TenantRegistry(tmp_path).create("../evil")

    assert list(tmp_path.rglob("*.json")) == []
