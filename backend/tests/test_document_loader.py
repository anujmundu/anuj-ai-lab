from app.rag.document_loader import document_loader

text = document_loader.load(
    "sample.txt"
)

print(text)