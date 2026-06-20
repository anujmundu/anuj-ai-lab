from app.executor.workflow_executor import workflow_executor


class ExecutorService:

    def run_workflow(
        self,
        goal: str
    ):

        return workflow_executor.execute(
            goal
        )


executor_service = ExecutorService()