from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PromptExperiment(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    prompt_name: str

    input_text: str

    output_text: str

    model_name: str

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )