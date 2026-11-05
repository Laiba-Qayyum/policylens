import hashlib
import json
import re
import secrets
from pathlib import Path

NAME = re.compile(r"[a-z0-9_-]{1,64}")
_NO_MATCH = "0" * 64


def _fingerprint(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class TenantRegistry:
    def __init__(self, directory: Path | None = None) -> None:
        self._file = directory / "registry.json" if directory is not None else None
        self._hashes: dict[str, str] = {}
        if self._file is not None and self._file.exists():
            self._hashes = json.loads(self._file.read_text(encoding="utf-8"))

    def exists(self, name: str) -> bool:
        return name in self._hashes

    def create(self, name: str) -> str:
        if not NAME.fullmatch(name):
            raise ValueError("Use 1 to 64 lowercase letters, digits, - or _")
        if name in self._hashes:
            raise FileExistsError(f"Workspace already exists: {name}")
        key = secrets.token_urlsafe(24)
        self._hashes[name] = _fingerprint(key)
        self._save()
        return key

    def check(self, name: str, key: str) -> bool:
        stored = self._hashes.get(name, _NO_MATCH)
        return secrets.compare_digest(_fingerprint(key), stored) and name in self._hashes

    def _save(self) -> None:
        if self._file is None:
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        temp = self._file.with_suffix(".tmp")
        temp.write_text(json.dumps(self._hashes), encoding="utf-8")
        temp.replace(self._file)
