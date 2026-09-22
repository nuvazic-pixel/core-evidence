import json
from typing import Protocol, Sequence
from core_evidence.verifier import RawClaim

SYSTEM_PROMPT = """You are an untrusted extraction model.
Extract claims ONLY for the requested schema keys.
Rules:
1. Return exact value, unit if applicable, exact verbatim source_quote, and [start,end] span where possible.
2. Never guess. Missing/not explicit => value=null, source_quote=null, source_span=null.
3. Mark interpretation_flag="approximate" for uncertainty, projection, draft status, or conflicting information; otherwise "exact".
4. Never output EvidenceState or decide truth/certainty.
Return JSON as either an array or {"claims": [...]} with fields key,value,unit,source_quote,source_span,interpretation_flag.
"""

class ModelAdapter(Protocol):
    def extract_claims(self, source_text: str, schema_keys: Sequence[str]) -> list[RawClaim]: ...


def parse_raw_claims(raw_json: str, allowed_keys: Sequence[str] | None = None) -> list[RawClaim]:
    try:
        parsed = json.loads(raw_json)
    except (json.JSONDecodeError, TypeError):
        return []
    if isinstance(parsed, dict):
        parsed = parsed.get("claims", parsed.get("items", []))
    if not isinstance(parsed, list):
        return []
    allowed = set(allowed_keys) if allowed_keys is not None else None
    claims = []
    for item in parsed:
        if not isinstance(item, dict) or not isinstance(item.get("key"), str):
            continue
        if allowed is not None and item["key"] not in allowed:
            continue
        span = item.get("source_span")
        span_tuple = None
        if isinstance(span, list) and len(span) == 2 and all(isinstance(x, int) and not isinstance(x, bool) for x in span):
            span_tuple = (span[0], span[1])
        claims.append(RawClaim(item["key"], item.get("value"), item.get("unit"), item.get("source_quote"), span_tuple, item.get("interpretation_flag")))
    return claims
