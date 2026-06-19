from app.agents.summarizer_agent import summarizer_agent
from app.workflows.base_workflow import BaseWorkflow


class SummarizeWorkflow(BaseWorkflow):

    def execute(
        self,
        text: str
    ):

        response = summarizer_agent.summarize(
            text
        )

        return {
            "workflow": "summarize",
            "response": response
        }


summarize_workflow = SummarizeWorkflow()