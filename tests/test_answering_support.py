from datetime import date

from src.answering import answer_question
from src.ingestion import Chunk


def make(text: str, page: int) -> Chunk:
    return Chunk(text, "doc.pdf", page, "policy", "1.0", date(2026, 1, 1))


class FakeStores:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks

    def search(self, tenant_id, query, k=3, min_score=-1.0):
        return self.chunks


class FakeLLM:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    def complete(self, prompt: str) -> str:
        return self.reply


FLIGHTS = make("All flights must be booked through the preferred travel agencies", 6)
ADVANCES = make("Advances must be approved by the Head of School or Associate Director", 7)


def test_source_is_the_chunk_that_matches_the_reply_not_the_one_cited():
    reply = "The Head of School or Associate Director must approve it. [1]"
    answer = answer_question(
        "t", "Who approves an advance?", FakeStores([FLIGHTS, ADVANCES]), FakeLLM(reply)
    )
    assert answer.sources == [ADVANCES]
    assert answer.verified is True


def test_falls_back_to_the_cited_chunk_when_nothing_matches():
    answer = answer_question(
        "t", "Who approves an advance?", FakeStores([FLIGHTS, ADVANCES]), FakeLLM("Okay. [1]")
    )
    assert answer.sources == [FLIGHTS]
