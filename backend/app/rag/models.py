from pydantic import BaseModel


class DocumentRequest(BaseModel):
    id: str
    text: str