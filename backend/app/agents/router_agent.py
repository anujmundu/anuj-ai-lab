from app.agents.code_review_agent import code_review_agent
from app.agents.email_agent import email_agent
from app.agents.summarizer_agent import summarizer_agent
from app.agents.tool_agent import tool_agent
from app.services.state_service import state_service


class RouterAgent:

    def route(
        self,
        query: str
    ):

        query_lower = query.lower()

        if any(char.isdigit() for char in query_lower):

            result = tool_agent.execute(
                query
            )

            state_service.update_state(
                active_agent="tool",
                current_task=query,
                status="completed",
                last_response=result["response"]
            )

            return result

        elif "time" in query_lower:

            result = tool_agent.execute(
                query
            )

            state_service.update_state(
                active_agent="tool",
                current_task=query,
                status="completed",
                last_response=result["response"]
            )

            return result

        elif "email" in query_lower:

            response = email_agent.write_email(
                query
            )

            state_service.update_state(
                active_agent="email",
                current_task=query,
                status="completed",
                last_response=response
            )

            return {
                "agent": "email",
                "response": response
            }

        elif "code" in query_lower:

            response = code_review_agent.review_code(
                query
            )

            state_service.update_state(
                active_agent="code-review",
                current_task=query,
                status="completed",
                last_response=response
            )

            return {
                "agent": "code-review",
                "response": response
            }

        else:

            response = summarizer_agent.summarize(
                query
            )

            state_service.update_state(
                active_agent="summarizer",
                current_task=query,
                status="completed",
                last_response=response
            )

            return {
                "agent": "summarizer",
                "response": response
            }


router_agent = RouterAgent()