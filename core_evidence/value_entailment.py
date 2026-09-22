import re
from typing import Any, Optional


UNIT_CONVERSIONS = {
    "m": 1.0, "meter": 1.0, "meters": 1.0, "metri": 1.0,
    "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01, "centimetri": 0.01,
    "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001, "milimetri": 0.001,
    "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
}


def parse_numeric_with_unit(text: str):
    match = re.search(r"(-?\d+(?:[.,]\d+)?)\s*([a-zA-Z]+)?", text)
    if not match:
        return None
    raw, unit = match.groups()
    return float(raw.replace(",", ".")), (unit.lower() if unit else "")


class ValueEntailmentVerifier:
    @staticmethod
    def verify_entailment(value: Any, unit: Optional[str], quote: str) -> bool:
        if value is None:
            return True
        # bool must precede numeric: bool is a subclass of int in Python.
        if isinstance(value, bool):
            q = quote.lower()
            positives = ("yes", "true", "da", "present", "confirmed")
            negatives = ("no", "false", "nu", "not", "absent", "none")
            return any(k in q for k in (positives if value else negatives))
        if isinstance(value, (int, float)):
            parsed = parse_numeric_with_unit(quote)
            if not parsed:
                return False
            quote_value, quote_unit = parsed
            if unit and quote_unit:
                claim_unit = unit.lower()
                if claim_unit in UNIT_CONVERSIONS and quote_unit in UNIT_CONVERSIONS:
                    return abs(value * UNIT_CONVERSIONS[claim_unit] - quote_value * UNIT_CONVERSIONS[quote_unit]) < 1e-9
                if claim_unit != quote_unit:
                    return False
            return abs(float(value) - quote_value) < 1e-9
        if isinstance(value, str):
            return value.casefold().strip() in quote.casefold()
        return False
