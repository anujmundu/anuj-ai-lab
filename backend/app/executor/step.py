from pydantic import BaseModel


class Step(BaseModel):

    order: int

    description: str

    status: str = "pending"