from app.executor.step import Step


class WorkflowExecutor:

    def execute(
        self,
        goal: str
    ):

        goal_lower = goal.lower()

        if "blog" in goal_lower:

            steps = [
                Step(order=1, description="Research topic"),
                Step(order=2, description="Create outline"),
                Step(order=3, description="Write content"),
                Step(order=4, description="Review content")
            ]

        else:

            steps = [
                Step(order=1, description="Analyze requirements"),
                Step(order=2, description="Design solution"),
                Step(order=3, description="Implement solution"),
                Step(order=4, description="Verify output")
            ]

        for step in steps:
            step.status = "completed"

        return {
            "goal": goal,
            "steps": steps,
            "status": "completed"
        }


workflow_executor = WorkflowExecutor()