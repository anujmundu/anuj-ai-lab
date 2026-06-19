from fastapi import APIRouter

from app.workflows.summarize_workflow import (
    summarize_workflow
)

router = APIRouter(
    prefix="/workflow",
    tags=["Workflow"]
)


@router.get("/summarize")
def summarize():

    text = (
        "Artificial intelligence is transforming healthcare, "
        "education and software development."
    )

    return summarize_workflow.execute(
        text
    )