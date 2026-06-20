from app.agents.router_agent import router_agent
from app.executor.workflow_executor import workflow_executor
from app.planner.planner import planner


class AutonomousAssistant:

    def run(
        self,
        goal: str
    ):

        plan = planner.create_plan(
            goal
        )

        execution = workflow_executor.execute(
            goal
        )

        result = router_agent.route(
            goal
        )

        return {
            "goal": goal,
            "plan": plan,
            "execution": execution,
            "response": result,
            "status": "completed"
        }


autonomous_assistant = AutonomousAssistant()