import pytest

from src.chunking import chunk_text


def numbered_text(count: int) -> str:
    return " ".join(str(i) for i in range(count))


def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n ") == []


def test_short_text_is_one_chunk():
    assert chunk_text("one two three", size=10, overlap=2) == ["one two three"]


def test_chunks_have_at_most_size_words():
    for chunk in chunk_text(numbered_text(25), size=10, overlap=2):
        assert len(chunk.split()) <= 10


def test_chunks_overlap():
    chunks = chunk_text(numbered_text(20), size=10, overlap=3)
    assert chunks[0].split()[-3:] == chunks[1].split()[:3]


def test_no_words_are_lost():
    text = numbered_text(25)
    chunks = chunk_text(text, size=10, overlap=2)
    assert set(" ".join(chunks).split()) == set(text.split())


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("a b c", size=5, overlap=5)
