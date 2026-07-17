from app.rag.contradiction_detector import (
    contradiction_detector,
)

from app.rag.nli_adapter_config import (
    NLIAdapterConfig,
)


class NLIAdapter:
    """
    Natural Language Inference abstraction.

    Responsibilities

    • Provide a stable NLI interface
    • Hide backend implementation
    • Return standardized probabilities

    Current backend

    • Heuristic contradiction detector

    Future backends

    • DeBERTa MNLI
    • RoBERTa MNLI
    • ModernBERT
    • OpenAI NLI
    """

    def __init__(
        self,
        config: NLIAdapterConfig | None = None,
    ):

        self.config = (
            config
            or NLIAdapterConfig()
        )

    # --------------------------------------------------

    def infer(
        self,
        *,
        contradiction: dict,
    ):

        if not self.config.enabled:

            return {}

        result = contradiction

        response = {

            "backend": self.config.backend,

            "entailment": result.get(
                "support",
                0.0,
            ),

            "neutral": result.get(
                "neutral",
                0.0,
            ),

            "contradiction": result.get(
                "contradiction",
                0.0,
            ),

            "label": result.get(
                "label",
                "unknown",
            ),
        }
        
        if "score" in result:

            response["score"] = result["score"]
        
        if self.config.include_confidence:

            response["confidence"] = (
                result
                .get(
                    "diagnostics",
                    {},
                )
                .get(
                    "confidence",
                    {},
                )
            )

        if self.config.include_explanation:

            response["explanation"] = (
                result.get(
                    "explanation",
                    {},
                )
            )

        if self.config.include_diagnostics:

            response["diagnostics"] = (
                result.get(
                    "diagnostics",
                    {},
                )
            )

        return response


nli_adapter = (
    NLIAdapter()
)