import datetime
from typing import Sequence
from .models import EvidenceItem, Provenance
from .validation import EvidenceGate, ValidationReport
from .verifier import RawClaim, EvidenceVerifier


class EvidenceBoundary:
    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    def process_proposals(self, claims: Sequence[RawClaim], source_text: str, required_keys: Sequence[str]) -> tuple[list[EvidenceItem], ValidationReport]:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        items = []
        for idx, claim in enumerate(claims):
            verification = EvidenceVerifier.verify_claim(claim, source_text)
            items.append(EvidenceItem(
                item_id=f"claim_{idx}_{claim.key}",
                key=claim.key,
                value=claim.value,
                state=verification.assigned_state,
                provenance=Provenance(self.source_id, now, "proposal_verified"),
            ))
        return items, EvidenceGate.evaluate(items, required_keys)
