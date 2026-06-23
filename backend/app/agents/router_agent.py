from app.agents.code_review_agent import code_review_agent
from app.agents.email_agent import email_agent
from app.agents.summarizer_agent import summarizer_agent
from app.agents.tool_agent import tool_agent
from app.memory.memory_service import memory_service
from app.services.state_service import state_service


class RouterAgent:

    def route(
        self,
        query: str
    ):

        query_lower = query.lower()

        # ---------------- Memory Commands ----------------

        if query_lower in [
            "last answer",
            "previous answer",
            "what was my last answer"
        ]:

            memory = memory_service.get_memory()

            for item in reversed(memory):

                if item["role"] == "assistant":

                    return item

            return {
                "message": "No previous answer found"
            }

        if query_lower in [
            "last question",
            "previous question",
            "what was my last question"
        ]:

            memory = memory_service.get_memory()

            for item in reversed(memory):

                if item["role"] == "user":

                    return item

            return {
                "message": "No previous question found"
            }

        if query_lower in [
            "again",
            "repeat"
        ]:

            memory = memory_service.get_memory()

            for item in reversed(memory):

                if item["role"] == "assistant":

                    return item

            return {
                "message": "Nothing to repeat"
            }

        # ---------------- Store User Query ----------------

        memory_service.add_message(
            "user",
            query
        )

        # ---------------- Normal Routing ----------------

        if (
            any(op in query for op in ["+", "-", "*", "/"])
            or "time" in query_lower
            or "weather" in query_lower
            or "news" in query_lower
            or "currency" in query_lower
            or "wiki" in query_lower
            or "search" in query_lower
        ):

            response = tool_agent.route(
                query
            )

            state_service.update_state(
                active_agent="tool",
                current_task=query,
                status="completed",
                last_response=str(
                    response["response"]
                )
            )

            memory_service.add_message(
                "assistant",
                response
            )

            return response

        elif "email" in query_lower:

            response = email_agent.write_email(
                query
            )

            result = {
                "agent": "email",
                "response": response
            }

            state_service.update_state(
                active_agent="email",
                current_task=query,
                status="completed",
                last_response=response
            )

            memory_service.add_message(
                "assistant",
                result
            )

            return result

        elif "code" in query_lower:

            response = code_review_agent.review_code(
                query
            )

            result = {
                "agent": "code-review",
                "response": response
            }

            state_service.update_state(
                active_agent="code-review",
                current_task=query,
                status="completed",
                last_response=response
            )

            memory_service.add_message(
                "assistant",
                result
            )

            return result

        else:

            response = summarizer_agent.summarize(
                query
            )

            result = {
                "agent": "summarizer",
                "response": response
            }

            state_service.update_state(
                active_agent="summarizer",
                current_task=query,
                status="completed",
                last_response=response
            )

            memory_service.add_message(
                "assistant",
                result
            )

            return result


router_agent = RouterAgent()