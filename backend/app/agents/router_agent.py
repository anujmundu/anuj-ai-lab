from app.agents.code_review_agent import code_review_agent
from app.agents.email_agent import email_agent
from app.agents.summarizer_agent import summarizer_agent


class RouterAgent:

    def route(
        self,
        query: str
    ):

        query_lower = query.lower()

        if "email" in query_lower:
            return {
                "agent": "email",
                "response": email_agent.write_email(query)
            }

        elif "code" in query_lower:
            return {
                "agent": "code-review",
                "response": code_review_agent.review_code(query)
            }

        else:
            return {
                "agent": "summarizer",
                "response": summarizer_agent.summarize(query)
            }


router_agent = RouterAgent()