from typing import Protocol, Sequence
from .verifier import RawClaim


class ModelAdapter(Protocol):
    """Untrusted model boundary: adapters may only propose RawClaim objects."""

    def extract_claims(self, source_text: str, schema_keys: Sequence[str]) -> list[RawClaim]:
        ...
