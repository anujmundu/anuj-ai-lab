from sqlmodel import Session, select

from app.models.prompt_experiment import PromptExperiment


class ExperimentService:

    def create_experiment(
        self,
        session: Session,
        prompt_name: str,
        input_text: str,
        output_text: str,
        model_name: str
    ):

        experiment = PromptExperiment(
            prompt_name=prompt_name,
            input_text=input_text,
            output_text=output_text,
            model_name=model_name
        )

        session.add(experiment)
        session.commit()
        session.refresh(experiment)

        return experiment

    def get_experiments(
        self,
        session: Session
    ):

        statement = select(PromptExperiment)

        return session.exec(statement).all()


experiment_service = ExperimentService()