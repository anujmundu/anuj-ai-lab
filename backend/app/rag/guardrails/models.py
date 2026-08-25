from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GuardrailAction(str, Enum):
    ALLOW = "allow"
    MASK = "mask"
    BLOCK = "block"


@dataclass(slots=True, frozen=True)
class InjectionCheckResult:
    is_safe: bool
    risk_score: float
    detected_patterns: list[str] = field(default_factory=list)
    action: GuardrailAction = GuardrailAction.ALLOW


@dataclass(slots=True, frozen=True)
class PIISanitizeResult:
    sanitized_text: str
    detected_types: list[str] = field(default_factory=list)
    redaction_count: int = 0
