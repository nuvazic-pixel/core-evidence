import datetime
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class EvidenceState(str, Enum):
    CONFIRMED = "CONFIRMED"
    DERIVED = "DERIVED"
    HYPOTHESIS = "HYPOTHESIS"
    UNKNOWN = "UNKNOWN"


def _validate_json_serializable(value: Any) -> None:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise ValueError("Float values cannot be NaN or Infinity.")
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_serializable(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("Dictionary keys must be strings.")
            _validate_json_serializable(item)
    else:
        try:
            json.dumps(value, allow_nan=False)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Value of type {type(value)} is not strictly JSON serializable.") from exc


@dataclass(frozen=True)
class Provenance:
    source_id: str
    timestamp: str
    method: str
    parent_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("Provenance.source_id cannot be empty.")
        if not self.method.strip():
            raise ValueError("Provenance.method cannot be empty.")
        try:
            datetime.datetime.fromisoformat(self.timestamp)
        except ValueError as exc:
            raise ValueError(f"Invalid ISO timestamp: {self.timestamp}") from exc


@dataclass(frozen=True)
class EvidenceItem:
    item_id: str
    key: str
    value: Any
    state: EvidenceState
    provenance: Provenance

    def __post_init__(self) -> None:
        if not self.item_id.strip():
            raise ValueError("EvidenceItem.item_id cannot be empty.")
        if not self.key.strip():
            raise ValueError("EvidenceItem.key cannot be empty.")
        _validate_json_serializable(self.value)
        if self.state == EvidenceState.DERIVED and not self.provenance.parent_ids:
            raise ValueError("DERIVED evidence requires at least one parent_id.")

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "key": self.key,
            "value": self.value,
            "state": self.state.value,
            "provenance": {
                "source_id": self.provenance.source_id,
                "timestamp": self.provenance.timestamp,
                "method": self.provenance.method,
                "parent_ids": list(self.provenance.parent_ids),
            },
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_canonical_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)
