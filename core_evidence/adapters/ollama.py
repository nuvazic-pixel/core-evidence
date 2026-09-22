import json
import urllib.request
from typing import Sequence
from core_evidence.verifier import RawClaim
from .base import SYSTEM_PROMPT, parse_raw_claims

class OllamaAdapter:
    def __init__(self, model_name: str = "llama3:latest", host: str = "http://localhost:11434", timeout: float = 60.0):
        self.model_name, self.host, self.timeout = model_name, host.rstrip("/"), timeout

    def extract_claims(self, source_text: str, schema_keys: Sequence[str]) -> list[RawClaim]:
        prompt = f"{SYSTEM_PROMPT}\nRequested Keys: {json.dumps(list(schema_keys))}\nSource Text: {json.dumps(source_text)}"
        payload = {"model": self.model_name, "prompt": prompt, "format": "json", "stream": False}
        req = urllib.request.Request(f"{self.host}/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode())
        return parse_raw_claims(data.get("response", "[]"), schema_keys)
