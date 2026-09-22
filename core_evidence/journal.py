from pathlib import Path
from typing import Sequence
from .models import EvidenceItem


class EventJournal:
    """Append-only-by-contract JSONL journal."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def append(self, item: EvidenceItem) -> str:
        payload = item.to_canonical_json()
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        return payload

    def append_batch(self, items: Sequence[EvidenceItem]) -> list[str]:
        # Serialize everything before touching the file.
        payloads = [item.to_canonical_json() for item in items]
        block = "".join(payload + "\n" for payload in payloads)
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(block)
        return payloads

    def read_all_canonical(self) -> list[str]:
        return [line.strip() for line in self.file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
