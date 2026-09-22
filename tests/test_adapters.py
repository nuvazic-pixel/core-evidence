from core_evidence.adapters.base import parse_raw_claims

def test_parser_rejects_invalid_json():
    assert parse_raw_claims("not-json", ["depth"]) == []

def test_parser_filters_unrequested_keys():
    raw='[{"key":"depth","value":0.8},{"key":"secret","value":42}]'
    claims=parse_raw_claims(raw,["depth"])
    assert [c.key for c in claims] == ["depth"]

def test_parser_accepts_claim_wrapper_and_span():
    raw='{"claims":[{"key":"depth","value":0.8,"unit":"m","source_quote":"0.80 m","source_span":[0,6],"interpretation_flag":"exact"}]}'
    claim=parse_raw_claims(raw,["depth"])[0]
    assert claim.source_span == (0,6)
