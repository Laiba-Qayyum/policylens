from datetime import date

from src.answering import answer_question
from src.ingestion import Chunk
from src.tenants import TenantStores


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3) -> list[Chunk]:
        words = query.lower().split()
        hits = [c for c in self.chunks if any(w in c.text.lower() for w in words)]
        return hits[:k]


class FakeLLM:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.reply


def make_chunk(text: str) -> Chunk:
    return Chunk(text, "policy.pdf", 2, "policy", "1.0", date(2026, 1, 1))


def make_stores() -> TenantStores:
    stores = TenantStores(FakeStore)
    stores.add("acme", [make_chunk("annual leave is 20 days")])
    stores.add("globex", [make_chunk("globex leave is 30 days")])
    return stores


def test_returns_llm_reply_with_its_sources() -> None:
    llm = FakeLLM("20 days [1]")

    answer = answer_question("acme", "annual leave", make_stores(), llm)

    assert answer.text == "20 days [1]"
    assert [c.text for c in answer.sources] == ["annual leave is 20 days"]


def test_prompt_contains_only_this_tenants_text() -> None:
    llm = FakeLLM("ok")

    answer_question("acme", "leave", make_stores(), llm)

    assert "annual leave is 20 days" in llm.prompts[0]
    assert "globex" not in llm.prompts[0]


def test_no_results_means_i_dont_know_and_no_llm_call() -> None:
    llm = FakeLLM("should not be used")

    answer = answer_question("acme", "parking", make_stores(), llm)

    assert answer.text == "I don't know."
    assert answer.sources == []
    assert llm.prompts == []
