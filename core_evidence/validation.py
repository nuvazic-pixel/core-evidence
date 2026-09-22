from dataclasses import dataclass
from enum import Enum
from typing import Sequence
from .models import EvidenceItem, EvidenceState


class ValidationOutcome(str, Enum):
    READY = "READY"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ValidationReport:
    outcome: ValidationOutcome
    missing_keys: tuple[str, ...] = ()
    invalid_state_keys: tuple[str, ...] = ()
    conflicting_keys: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


class EvidenceGate:
    @staticmethod
    def evaluate(items: Sequence[EvidenceItem], required_keys: Sequence[str]) -> ValidationReport:
        reasons = []
        ids = [i.item_id for i in items]
        if len(ids) != len(set(ids)):
            return ValidationReport(ValidationOutcome.REJECTED, reasons=("Duplicate item_id detected.",))

        grouped: dict[str, list[EvidenceItem]] = {}
        for item in items:
            grouped.setdefault(item.key, []).append(item)
        conflicts = tuple(k for k, values in grouped.items() if len(values) > 1)
        if conflicts:
            return ValidationReport(ValidationOutcome.REJECTED, conflicting_keys=conflicts, reasons=("Key collision detected.",))

        missing, invalid = [], []
        for key in required_keys:
            if key not in grouped:
                missing.append(key)
            elif grouped[key][0].state in (EvidenceState.UNKNOWN, EvidenceState.HYPOTHESIS):
                invalid.append(key)
        if missing or invalid:
            return ValidationReport(ValidationOutcome.NEEDS_CLARIFICATION, tuple(missing), tuple(invalid))
        return ValidationReport(ValidationOutcome.READY)
