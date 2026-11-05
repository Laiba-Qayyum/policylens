from ui.signup import signin_credentials


def test_a_company_name_becomes_the_workspace_address():
    assert signin_credentials("Laiba Co", "k")[0] == "laiba-co"


def test_an_existing_address_is_left_alone():
    assert signin_credentials("laiba-coo0", "k")[0] == "laiba-coo0"
    assert signin_credentials("my_co", "k")[0] == "my_co"


def test_capitals_and_spaces_around_the_address_are_ignored():
    assert signin_credentials("  Laiba-Co ", "k")[0] == "laiba-co"


def test_spaces_and_line_breaks_around_the_key_are_removed():
    assert signin_credentials("acme", "  abc \n")[1] == "abc"
