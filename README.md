# core-evidence

Deterministic evidence verification and trust boundary for probabilistic AI systems.

## Principle

LLMs are untrusted proposers. They may propose claims, values, quotes and spans, but they do not assign their own epistemic state. Deterministic verification validates attribution and value entailment before an EvidenceItem can reach the gate.

## v0.2 scope

- immutable evidence models
- deterministic validation gate
- quote/span attribution verification
- value entailment for strings, booleans and numeric values with units
- provenance DAG integrity checks
- append-only-by-contract JSONL journal
- adversarial tests
- provider-neutral model adapter protocol

Critical benchmark target: **False READY = 0**.

## Status

Initial repository bootstrap. LLM adapters and benchmark execution follow only after the deterministic boundary passes adversarial tests.
