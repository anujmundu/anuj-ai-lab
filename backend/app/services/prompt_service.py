from pathlib import Path


PROMPTS_DIR = Path("prompts")


class PromptService:

    def load_prompt(
        self,
        name: str,
        **kwargs
    ) -> str:

        file_path = PROMPTS_DIR / f"{name}.txt"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Prompt '{name}' not found"
            )

        template = file_path.read_text(
            encoding="utf-8"
        )

        return template.format(
            **kwargs
        )


prompt_service = PromptService()