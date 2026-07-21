from __future__ import annotations

from app.rag.prompt_optimizer_models import PromptComponent


class PromptRenderer:
    """
    Renders PromptComponents into the final prompt string
    that will be sent to the language model.

    The renderer is presentation-only:
    - It does not modify components.
    - It does not optimize prompts.
    - It does not analyze prompts.
    - It does not perform budgeting.
    """

    def render(
        self,
        components: list[PromptComponent],
    ) -> str:
        """
        Render prompt components into a single prompt string.
        """

        rendered_sections: list[str] = []

        for component in components:

            if not component.text.strip():
                continue

            rendered_sections.append(
                self._render_component(component)
            )

        return "\n\n".join(rendered_sections)

    def _render_component(
        self,
        component: PromptComponent,
    ) -> str:
        """
        Render a single PromptComponent.
        """

        title = component.component_type.value.upper()

        return (
            f"### {title}\n\n"
            f"{component.text.strip()}"
        )


prompt_renderer = PromptRenderer()