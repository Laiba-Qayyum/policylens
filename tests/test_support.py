from datetime import date

from src.citations import best_support
from src.ingestion import Chunk


def make(text: str, page: int) -> Chunk:
    return Chunk(text, "doc.pdf", page, "policy", "1.0", date(2026, 1, 1))


def test_picks_the_chunk_sharing_most_words_with_the_reply():
    flights = make("All flights must be booked through the preferred travel agencies", 6)
    advances = make("Advances must be approved by the Head of School or Associate Director", 7)
    reply = "The Head of School or Associate Director must approve an advance. [1]"
    assert best_support(reply, [flights, advances]) is advances


def test_numbers_count_as_matches():
    hotel = make("A hotel stay costs at most 150 per night including breakfast", 5)
    mileage = make("Mileage is 40p per mile", 4)
    assert best_support("150 per night [2]", [mileage, hotel]) is hotel


def test_returns_none_when_nothing_matches():
    chunk = make("Rail travel is standard class only", 5)
    assert best_support("I don't know.", [chunk]) is None
