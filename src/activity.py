import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from src.tenants import SAFE_ID


def _now() -> datetime:
    return datetime.now(UTC)


class ActivityLog:
    def __init__(self, directory: Path | None = None, clock: Callable[[], datetime] = _now) -> None:
        self._directory = directory
        self._clock = clock
        self._events: dict[str, list[dict]] = {}
        if directory is not None:
            directory.mkdir(parents=True, exist_ok=True)
            for file in sorted(directory.glob("*.jsonl")):
                if SAFE_ID.fullmatch(file.stem):
                    lines = file.read_text(encoding="utf-8").splitlines()
                    self._events[file.stem] = [json.loads(line) for line in lines if line]

    def record(
        self, tenant_id: str, kind: str, detail: str = "", verified: bool | None = None
    ) -> None:
        if self._directory is not None and not SAFE_ID.fullmatch(tenant_id):
            raise ValueError(f"invalid tenant id: {tenant_id!r}")
        event = {
            "time": self._clock().isoformat(),
            "kind": kind,
            "detail": detail,
            "verified": verified,
        }
        self._events.setdefault(tenant_id, []).append(event)
        if self._directory is not None:
            with (self._directory / f"{tenant_id}.jsonl").open("a", encoding="utf-8") as file:
                file.write(json.dumps(event) + "\n")

    def recent(self, tenant_id: str, limit: int = 20) -> list[dict]:
        return list(reversed(self._events.get(tenant_id, [])))[:limit]

    def summary(self, tenant_id: str) -> dict[str, int]:
        events = self._events.get(tenant_id, [])
        questions = [e for e in events if e["kind"] == "question"]
        return {
            "uploads": sum(e["kind"] == "upload" for e in events),
            "questions": len(questions),
            "verified_questions": sum(e["verified"] is True for e in questions),
        }
