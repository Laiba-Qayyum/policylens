from ui.styles import STYLE

SIGNUP_SELECTORS = [
    ".pl-hero",
    ".pl-hero-title",
    ".pl-flow",
    ".pl-step",
    ".pl-arrow",
    ".pl-form-title",
    ".pl-address",
    ".pl-trust",
]


def test_the_sign_up_page_has_its_split_screen_styles():
    for selector in SIGNUP_SELECTORS:
        assert selector in STYLE


def test_the_flow_animation_stops_for_reduced_motion():
    reduced = STYLE.split("prefers-reduced-motion")[1]

    assert ".pl-arrow" in reduced
    assert ".pl-step" in reduced


def test_the_sign_up_layout_stacks_on_small_screens():
    assert "@media (max-width: 800px)" in STYLE
