from app.rag.context_builder import context_builder
from app.rag.prompt_builder import prompt_builder
from app.rag.prompt_renderer import prompt_renderer


def test_prompt_builder_basic():
    context = "ChromaDB is an open-source vector database."
    components = prompt_builder.build_prompt(
        question="What is ChromaDB?",
        context=context,
        conversation=None,
    )
    rendered = prompt_renderer.render(components)
    assert "What is ChromaDB?" in rendered
    assert context in rendered
