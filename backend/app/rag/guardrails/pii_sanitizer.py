from __future__ import annotations

import re
from app.rag.guardrails.models import PIISanitizeResult


class PIISanitizer:
    """
    Detects and redacts sensitive PII (emails, API keys, phone numbers, SSNs, credit cards).
    """

    PATTERNS = [
        ("api_key", r"\b(?:sk-[a-zA-Z0-9]{20,}|(?:ghp|gho|glpat|AKIA)[a-zA-Z0-9]{16,})\b", "[REDACTED_API_KEY]"),
        ("email", r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", "[REDACTED_EMAIL]"),
        ("credit_card", r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[REDACTED_CARD]"),
        ("ssn", r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
        ("phone", r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    ]

    def sanitize(self, text: str) -> PIISanitizeResult:
        sanitized = text
        detected: list[str] = []
        count = 0

        for ptype, pattern, replacement in self.PATTERNS:
            matches = list(re.finditer(pattern, sanitized))
            if matches:
                detected.append(ptype)
                count += len(matches)
                sanitized = re.sub(pattern, replacement, sanitized)

        return PIISanitizeResult(
            sanitized_text=sanitized,
            detected_types=detected,
            redaction_count=count,
        )


pii_sanitizer = PIISanitizer()
