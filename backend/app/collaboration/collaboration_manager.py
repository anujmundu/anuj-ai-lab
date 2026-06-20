from app.agents.email_agent import email_agent
from app.agents.summarizer_agent import summarizer_agent
from app.planner.planner import planner


class CollaborationManager:

    def collaborate(
        self,
        goal: str
    ):

        plan = planner.create_plan(
            goal
        )

        summary = summarizer_agent.summarize(
            goal
        )

        email = email_agent.write_email(
            f"Write an email about {goal}"
        )

        return {
            "goal": goal,
            "plan": plan,
            "summary": summary,
            "email": email,
            "status": "completed"
        }


collaboration_manager = CollaborationManager()