class TextChunker:

    def chunk(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> list[str]:

        chunks = []

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append(chunk.strip())

            start += chunk_size - overlap

        return chunks


text_chunker = TextChunker()