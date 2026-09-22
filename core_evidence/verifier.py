from dataclasses import dataclass
from typing import Optional, Sequence, Set
from .models import EvidenceItem, EvidenceState
from .value_entailment import ValueEntailmentVerifier


@dataclass(frozen=True)
class RawClaim:
    key: str
    value: str | int | float | bool | None
    unit: Optional[str] = None
    source_quote: Optional[str] = None
    source_span: Optional[tuple[int, int]] = None
    interpretation_flag: Optional[str] = None


@dataclass(frozen=True)
class VerificationResult:
    is_valid_attribution: bool
    is_entailed: bool
    assigned_state: EvidenceState
    failure_reason: Optional[str] = None


class EvidenceVerifier:
    @staticmethod
    def verify_claim(claim: RawClaim, source_text: str) -> VerificationResult:
        if claim.value is None or not claim.source_quote:
            return VerificationResult(True, True, EvidenceState.UNKNOWN, "No value or quote provided.")

        quote = claim.source_quote
        if claim.source_span is not None:
            start, end = claim.source_span
            if start < 0 or end > len(source_text) or start >= end:
                return VerificationResult(False, False, EvidenceState.HYPOTHESIS, "Span out of bounds.")
            if source_text[start:end] != quote:
                return VerificationResult(False, False, EvidenceState.HYPOTHESIS, "Span text mismatch.")
        if quote not in source_text:
            return VerificationResult(False, False, EvidenceState.HYPOTHESIS, "Quote missing from source.")

        if not ValueEntailmentVerifier.verify_entailment(claim.value, claim.unit, quote):
            return VerificationResult(True, False, EvidenceState.HYPOTHESIS, "Value is not entailed by quote.")

        markers = ("approximately", "about", "around", "appears", "seems", "estimated", "aprox", "circa", "might", "may")
        if claim.interpretation_flag == "approximate" or any(k in quote.casefold() for k in markers):
            return VerificationResult(True, True, EvidenceState.HYPOTHESIS, "Quote contains uncertainty markers.")
        return VerificationResult(True, True, EvidenceState.CONFIRMED)

    @staticmethod
    def validate_dag(items: Sequence[EvidenceItem], known_parent_ids: Optional[Set[str]] = None) -> tuple[bool, Optional[str]]:
        ids = [item.item_id for item in items]
        if len(ids) != len(set(ids)):
            return False, "Duplicate item_id detected."
        current = set(ids)
        known = set(known_parent_ids or ())
        all_ids = current | known
        for item in items:
            if item.item_id in item.provenance.parent_ids:
                return False, f"Item '{item.item_id}' references itself."
            for parent in item.provenance.parent_ids:
                if parent not in all_ids:
                    return False, f"Parent ID '{parent}' is missing."

        adj = {item_id: [] for item_id in current}
        degree = {item_id: 0 for item_id in current}
        for item in items:
            for parent in item.provenance.parent_ids:
                if parent in current:
                    adj[parent].append(item.item_id)
                    degree[item.item_id] += 1
        queue = [node for node, d in degree.items() if d == 0]
        visited = 0
        while queue:
            node = queue.pop()
            visited += 1
            for child in adj[node]:
                degree[child] -= 1
                if degree[child] == 0:
                    queue.append(child)
        return (True, None) if visited == len(current) else (False, "Cycle detected in Evidence DAG.")
