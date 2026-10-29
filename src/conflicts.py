from datetime import date

from src.ingestion import Chunk


def find_competing_sources(chunks: list[Chunk]) -> list[str]:
    """Files of the same document type that may disagree, newest first."""
    by_type: dict[str, dict[str, date]] = {}
    for chunk in chunks:
        by_type.setdefault(chunk.doc_type, {})[chunk.source] = chunk.doc_date

    competing: list[str] = []
    for sources in by_type.values():
        if len(sources) > 1:
            competing += sorted(sources, key=lambda s: sources[s], reverse=True)
    return competing
