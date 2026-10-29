from datetime import date

from src.ingestion import Chunk
from src.prompts import build_prompt

CHUNK = Chunk(
    "Rail travel is standard class only.", "travel.pdf", 5, "policy", "1.0", date(2026, 1, 1)
)
YES_NO_RULE = "Start your answer with Yes or No"


def test_yes_no_question_gets_the_yes_no_rule():
    assert YES_NO_RULE in build_prompt("Can I book first class?", [CHUNK])


def test_other_question_does_not_get_the_yes_no_rule():
    assert YES_NO_RULE not in build_prompt("How long do I have to claim?", [CHUNK])


def test_empty_question_does_not_crash():
    assert YES_NO_RULE not in build_prompt("", [CHUNK])
