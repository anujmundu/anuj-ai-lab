from app.planner.planner import planner


class PlannerService:

    def generate_plan(
        self,
        goal: str
    ):

        return planner.create_plan(goal)


planner_service = PlannerService()