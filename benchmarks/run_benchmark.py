import argparse
from pathlib import Path
from core_evidence.benchmark import run_benchmark_for_adapter
from core_evidence.adapters.ollama import OllamaAdapter
from core_evidence.adapters.gemini import GeminiAdapter

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--adapter", choices=["ollama","gemini"], required=True)
    p.add_argument("--model")
    args=p.parse_args()
    adapter = OllamaAdapter(args.model or "llama3:latest") if args.adapter=="ollama" else GeminiAdapter(args.model or "gemini-2.5-flash")
    name=f"{args.adapter}:{adapter.model_name}"
    metrics,_=run_benchmark_for_adapter(adapter,name,Path(__file__).with_name("cases.jsonl"))
    print(f"Adapter: {name}\nTotal: {metrics.total_cases}\nFalse READY: {metrics.false_ready_count} ({metrics.false_ready_rate:.2%})\nUnsupported promotions: {metrics.unsupported_promotion_count}\nOverblocking: {metrics.overblocking_count}\nAttribution errors: {metrics.attribution_error_count}")
    if metrics.false_ready_count: raise SystemExit(2)

if __name__=="__main__": main()
