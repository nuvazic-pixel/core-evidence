from dataclasses import dataclass
from typing import Sequence
from .models import EvidenceState

@dataclass(frozen=True)
class BenchmarkMetrics:
    total_cases: int
    false_ready_count: int
    unsupported_promotion_count: int
    overblocking_count: int
    attribution_error_count: int
    @property
    def false_ready_rate(self): return self.false_ready_count / self.total_cases if self.total_cases else 0.0

class MetricsCalculator:
    @staticmethod
    def evaluate_benchmark_run(results: Sequence[dict]) -> BenchmarkMetrics:
        false_ready = unsupported = overblocking = attribution = 0
        for r in results:
            expected = r["expected"]
            actual = {item.key: item for item in r["actual_items"]}
            is_ready = r["gate_outcome"] == "READY"
            should_ready = all(s in ("CONFIRMED","DERIVED") for s in expected.values())
            false_ready += int(is_ready and not should_ready)
            overblocking += int((not is_ready) and should_ready)
            for key, exp in expected.items():
                item = actual.get(key)
                if item and exp in ("HYPOTHESIS","UNKNOWN") and item.state in (EvidenceState.CONFIRMED,EvidenceState.DERIVED): unsupported += 1
            attribution += int(bool(r.get("attribution_failed", False)))
        return BenchmarkMetrics(len(results), false_ready, unsupported, overblocking, attribution)
