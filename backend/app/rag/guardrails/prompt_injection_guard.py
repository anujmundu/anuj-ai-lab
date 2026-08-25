from __future__ import annotations

import re
from app.rag.guardrails.models import GuardrailAction, InjectionCheckResult


class PromptInjectionGuard:
    """
    Detects adversarial prompt injection and jailbreak attacks in user queries.
    """

    INJECTION_PATTERNS = [
        # System prompt overrides
        (r"(?i)\b(?:ignore|disregard|forget|override)\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|prompts?|rules?|commands?)\b", "override_instructions"),
        (r"(?i)\b(?:reveal|show|print|output|display)\s+(?:your\s+)?(?:system\s+prompt|initial\s+prompt|system\s+instructions)\b", "leak_system_prompt"),
        # Jailbreak personas
        (r"(?i)\b(?:you\s+are\s+now|act\s+as)\s+(?:DAN|unrestricted|jailbroken|unfiltered)\b", "jailbreak_persona"),
        (r"(?i)\b(?:jailbreak|developer\s+mode|god\s+mode)\s+(?:enabled|activated|on)\b", "jailbreak_mode"),
        # Delimiter escapes
        (r"<\|(?:im_start|im_end|endoftext)\|>", "delimiter_injection"),
        (r"\[/?(?:INST|SYS)\]", "llama_delimiter_injection"),
    ]

    def check(self, query: str) -> InjectionCheckResult:
        detected: list[str] = []

        for pattern, label in self.INJECTION_PATTERNS:
            if re.search(pattern, query):
                detected.append(label)

        if not detected:
            return InjectionCheckResult(
                is_safe=True,
                risk_score=0.0,
                detected_patterns=[],
                action=GuardrailAction.ALLOW,
            )

        risk_score = min(1.0, 0.5 * len(detected))
        action = GuardrailAction.BLOCK if risk_score >= 0.5 else GuardrailAction.ALLOW

        return InjectionCheckResult(
            is_safe=False,
            risk_score=risk_score,
            detected_patterns=detected,
            action=action,
        )


prompt_injection_guard = PromptInjectionGuard()
