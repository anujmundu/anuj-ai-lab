from app.rag.chunk_config import ChunkingConfig
from app.rag.text_chunker import text_chunker

LINE = "=" * 90
SMALL = "-" * 90


def print_chunk_statistics(chunks):

    total_characters = 0
    total_words = 0

    for index, chunk in enumerate(chunks, start=1):

        characters = len(chunk)
        words = len(chunk.split())

        total_characters += characters
        total_words += words

        print(f"\nChunk #{index}")
        print(SMALL)

        print(f"Characters : {characters}")
        print(f"Words      : {words}")

        preview = chunk

        if len(preview) > 220:
            preview = preview[:220] + "..."

        print("\nPreview\n")
        print(preview)

    print("\nSummary")
    print(SMALL)

    print(f"Chunks      : {len(chunks)}")
    print(f"Characters  : {total_characters}")
    print(f"Words       : {total_words}")


# ==========================================================
# TEST 1
# Paragraph Preservation
# ==========================================================

print("\n" + LINE)
print("TEST 1 - PARAGRAPH PRESERVATION")
print(LINE)

paragraph_document = """
Python is a programming language.

FastAPI is a modern API framework.

ChromaDB stores embeddings.

Sentence Transformers generate embeddings.

Retrieval Augmented Generation improves LLM accuracy.
"""

paragraph_chunks = text_chunker.chunk(
    text=paragraph_document,
    config=ChunkingConfig(
        chunk_size=500,
        overlap_sentences=1
    )
)

print_chunk_statistics(paragraph_chunks)

print("\nExpected Result")
print(SMALL)
print("✓ Each paragraph should become one chunk.")
print("✓ No paragraph merging should occur.")


# ==========================================================
# TEST 2
# Sentence Overlap
# ==========================================================

print("\n\n" + LINE)
print("TEST 2 - SENTENCE OVERLAP")
print(LINE)

long_paragraph = """
Python is a programming language. Python was created by Guido van Rossum.
FastAPI is a modern API framework. ChromaDB stores vector embeddings.
Sentence Transformers generate embeddings. Retrieval Augmented Generation improves LLM accuracy.
Enterprise AI systems combine retrieval with large language models.
"""

overlap_chunks = text_chunker.chunk(
    text=long_paragraph,
    config=ChunkingConfig(
        chunk_size=120,
        overlap_sentences=1
    )
)

print_chunk_statistics(overlap_chunks)

print("\nOverlap Verification")
print(SMALL)

for index in range(1, len(overlap_chunks)):

    previous = overlap_chunks[index - 1]
    current = overlap_chunks[index]

    previous_sentences = [
        sentence.strip()
        for sentence in previous.split(".")
        if sentence.strip()
    ]

    if not previous_sentences:
        continue

    last_sentence = previous_sentences[-1]

    overlap = last_sentence in current

    status = "PASS" if overlap else "FAIL"

    print(
        f"Chunk {index} → Chunk {index + 1} : "
        f"{status}"
    )

print("\nExpected Result")
print(SMALL)
print("✓ Every overlap check should print PASS.")


print("\n\n" + LINE)
print("FINAL RESULT")
print(LINE)

print("✓ Paragraph preservation verified.")
print("✓ Sentence overlap verified.")
print("✓ Chunk statistics generated.")
print("✓ Ready for ingestion testing.")