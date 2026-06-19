from app.agents.base_agent import BaseAgent


class EmailAgent(BaseAgent):

    def write_email(
        self,
        request: str
    ):

        prompt = f"""
You are an expert email writer.

Write a professional email.

Request:

{request}
"""

        return self.run(prompt)


email_agent = EmailAgent()