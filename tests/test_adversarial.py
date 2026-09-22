import pytest
from core_evidence.models import EvidenceItem, EvidenceState, Provenance
from core_evidence.validation import EvidenceGate, ValidationOutcome
from core_evidence.verifier import EvidenceVerifier


def prov(parents=()):
    return Provenance("test", "2026-09-22T20:00:00+00:00", "test", parents)


def test_fake_derived_rejected():
    with pytest.raises(ValueError):
        EvidenceItem("x", "depth", 0.6, EvidenceState.DERIVED, prov())


def test_nan_rejected():
    with pytest.raises(ValueError):
        EvidenceItem("x", "temp", float("nan"), EvidenceState.CONFIRMED, prov())


def test_key_collision_rejected():
    a = EvidenceItem("1", "depth", 0.6, EvidenceState.CONFIRMED, prov())
    b = EvidenceItem("2", "depth", 0.8, EvidenceState.HYPOTHESIS, prov())
    assert EvidenceGate.evaluate([a, b], ["depth"]).outcome == ValidationOutcome.REJECTED


def test_cycle_rejected():
    a = EvidenceItem("a", "a", 1, EvidenceState.DERIVED, prov(("b",)))
    b = EvidenceItem("b", "b", 2, EvidenceState.DERIVED, prov(("a",)))
    valid, reason = EvidenceVerifier.validate_dag([a, b])
    assert valid is False
    assert "Cycle" in reason
