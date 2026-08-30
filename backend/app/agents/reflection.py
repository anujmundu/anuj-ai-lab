from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from app.agents.models import AgentStep


@dataclass(slots=True)
class ReflectionResult:
    is_successful: bool
    should_retry: bool
    feedback: str
    suggested_fix: str | None = None


class ReflectionEvaluator:
    """
    Critiques intermediate tool observations and decides whether to continue, retry, or adjust strategy.
    """

    def evaluate_step(self, step: AgentStep) -> ReflectionResult:
        """Evaluate a single executed agent step."""
        if not step.success:
            return ReflectionResult(
                is_successful=False,
                should_retry=True,
                feedback=f"Action '{step.action}' failed with error: {step.observation}",
                suggested_fix="Inspect error message, adjust parameters or try alternative tool.",
            )

        if step.observation is None or step.observation == "":
            return ReflectionResult(
                is_successful=False,
                should_retry=True,
                feedback=f"Action '{step.action}' returned empty observation.",
                suggested_fix="Verify input parameters or query terms.",
            )

        # Check for error in structured dict observation
        if isinstance(step.observation, dict):
            if step.observation.get("exit_code", 0) != 0 or step.observation.get("stderr"):
                return ReflectionResult(
                    is_successful=False,
                    should_retry=False,
                    feedback=f"Sandbox execution failed: {step.observation.get('stderr') or 'Non-zero exit code'}",
                    suggested_fix="Fix syntax or runtime logic in the script.",
                )
            if step.observation.get("timed_out"):
                return ReflectionResult(
                    is_successful=False,
                    should_retry=True,
                    feedback="Execution timed out.",
                    suggested_fix="Optimize execution efficiency or increase timeout limit.",
                )

        # Check for genuine traceback errors in text
        obs_str = str(step.observation)
        if "Traceback (most recent call last):" in obs_str or "SyntaxError:" in obs_str or "ZeroDivisionError:" in obs_str:
            return ReflectionResult(
                is_successful=False,
                should_retry=False,
                feedback=f"Observation indicates runtime error: {step.observation}",
                suggested_fix="Fix syntax or runtime logic in the script.",
            )

        return ReflectionResult(
            is_successful=True,
            should_retry=False,
            feedback=f"Step {step.step_number} completed successfully.",
            suggested_fix=None,
        )


reflection_evaluator = ReflectionEvaluator()
