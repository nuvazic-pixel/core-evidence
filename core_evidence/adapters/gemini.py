import json
import os
import urllib.request
from typing import Sequence
from core_evidence.verifier import RawClaim
from .base import SYSTEM_PROMPT, parse_raw_claims

class GeminiAdapter:
    """Zero-dependency Gemini REST adapter. API key is read from GEMINI_API_KEY."""
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: str | None = None, timeout: float = 60.0):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.timeout = timeout

    def extract_claims(self, source_text: str, schema_keys: Sequence[str]) -> list[RawClaim]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        prompt = f"{SYSTEM_PROMPT}\nRequested Keys: {json.dumps(list(schema_keys))}\nSource Text: {json.dumps(source_text)}"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json"}}
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode())
        try:
            raw = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            return []
        return parse_raw_claims(raw, schema_keys)
