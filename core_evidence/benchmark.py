import json
from pathlib import Path
from .boundary import EvidenceBoundary
from .metrics import MetricsCalculator

def run_benchmark_for_adapter(adapter, adapter_name: str, cases_path: Path):
    boundary, results = EvidenceBoundary(adapter_name), []
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for case in cases:
        claims = adapter.extract_claims(case["text"], case["required"])
        items, report = boundary.process_proposals(claims, case["text"], case["required"])
        results.append({"case_id":case["case_id"],"expected":case["expected"],"actual_items":items,"gate_outcome":report.outcome.value})
    return MetricsCalculator.evaluate_benchmark_run(results), results
