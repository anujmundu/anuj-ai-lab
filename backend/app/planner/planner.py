from app.planner.task import Task


class Planner:

    def create_plan(
        self,
        goal: str
    ):

        goal_lower = goal.lower()

        if "ai assistant" in goal_lower:

            tasks = [
                Task(title="Design architecture"),
                Task(title="Create agents"),
                Task(title="Implement memory"),
                Task(title="Build APIs"),
                Task(title="Test workflows")
            ]

        else:

            tasks = [
                Task(title="Analyze requirements"),
                Task(title="Create implementation plan"),
                Task(title="Execute tasks"),
                Task(title="Verify results")
            ]

        return {
            "goal": goal,
            "tasks": tasks
        }


planner = Planner()