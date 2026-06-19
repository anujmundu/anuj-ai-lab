from app.agents.base_agent import BaseAgent


class SummarizerAgent(BaseAgent):

    def summarize(
        self,
        text: str
    ):

        prompt = f"""
You are an expert summarizer.

Summarize the following text into concise bullet points.

Text:

{text}
"""

        return self.run(prompt)


summarizer_agent = SummarizerAgent()