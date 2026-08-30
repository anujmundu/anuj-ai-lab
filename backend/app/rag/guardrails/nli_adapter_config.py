from dataclasses import dataclass


@dataclass(slots=True)
class NLIAdapterConfig:
    """
    Configuration for the Natural Language
    Inference (NLI) abstraction layer.

    This module provides a stable interface
    between the hallucination detector and
    future transformer-based NLI models.

    Current implementation uses heuristic
    contradiction estimation.

    Future implementations may use:

    • DeBERTa MNLI
    • RoBERTa MNLI
    • ModernBERT NLI
    • OpenAI NLI APIs
    """

    # --------------------------------------------------
    # Master Switches
    # --------------------------------------------------

    enabled: bool = True

    include_explanation: bool = True

    include_confidence: bool = True

    include_diagnostics: bool = True

    # --------------------------------------------------
    # Backend
    # --------------------------------------------------

    backend: str = "heuristic"