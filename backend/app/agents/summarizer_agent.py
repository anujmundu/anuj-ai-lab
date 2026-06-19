from app.agents.base_agent import BaseAgent
from app.memory.conversation_memory import conversation_memory


class SummarizerAgent(BaseAgent):

    def summarize(
        self,
        text: str
    ):

        history = conversation_memory.recent_context()

        prompt = f"""
Previous interactions:

{history}

You are an expert summarizer.

Summarize the following text into concise bullet points.

Text:

{text}
"""

        response = self.run(
            prompt
        )

        conversation_memory.save_interaction(
            user_input=text,
            assistant_response=response
        )

        return response


summarizer_agent = SummarizerAgent()