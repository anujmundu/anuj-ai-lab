from app.agents.base_agent import BaseAgent


class CodeReviewAgent(BaseAgent):

    def review_code(
        self,
        code: str
    ):

        prompt = f"""
You are a senior software engineer.

Review the following code.

Provide:

- Bugs
- Improvements
- Best practices

Code:

{code}
"""

        return self.run(prompt)


code_review_agent = CodeReviewAgent()