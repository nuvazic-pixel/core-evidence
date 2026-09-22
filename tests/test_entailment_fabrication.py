from core_evidence.models import EvidenceState
from core_evidence.verifier import RawClaim, EvidenceVerifier
from core_evidence.boundary import EvidenceBoundary
from core_evidence.validation import ValidationOutcome


def test_quote_true_but_value_fabricated_must_never_be_ready():
    source = "The trench depth is exactly 0.80 m. The conduit diameter is 110 mm."
    quote = "The trench depth is exactly 0.80 m."
    claim = RawClaim(
        key="trench_depth", value=9.5, unit="m",
        source_quote=quote, source_span=(0, len(quote)),
    )
    result = EvidenceVerifier.verify_claim(claim, source)
    assert result.is_valid_attribution is True
    assert result.is_entailed is False
    assert result.assigned_state == EvidenceState.HYPOTHESIS

    items, report = EvidenceBoundary("test_model").process_proposals([claim], source, ["trench_depth"])
    assert report.outcome == ValidationOutcome.NEEDS_CLARIFICATION
    assert items[0].state == EvidenceState.HYPOTHESIS


def test_equivalent_units_are_entailed():
    source = "The trench depth is exactly 80 cm."
    quote = source
    claim = RawClaim("trench_depth", 0.8, "m", quote, (0, len(quote)))
    result = EvidenceVerifier.verify_claim(claim, source)
    assert result.is_entailed is True
    assert result.assigned_state == EvidenceState.CONFIRMED
