import re

from app.rag.chunk_config import ChunkingConfig
from app.rag.chunk_models import Chunk
from app.rag.chunk_strategy import ChunkStrategy


class TextChunker:

    def split_paragraphs(
        self,
        text: str,
        config: ChunkingConfig
    ) -> list[str]:

        return [
            paragraph.strip()
            for paragraph in text.split(
                config.paragraph_separator
            )
            if paragraph.strip()
        ]

    def split_sentences(
        self,
        paragraph: str,
        config: ChunkingConfig
    ) -> list[str]:

        return [
            sentence.strip()
            for sentence in re.split(
                config.sentence_regex,
                paragraph
            )
            if sentence.strip()
        ]

    def _chunk_statistics(
        self,
        text: str
    ) -> Chunk:

        return Chunk(
            text=text,
            characters=len(text),
            words=len(text.split())
        )

    def build_chunks(
        self,
        sentences: list[str],
        config: ChunkingConfig
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        current_sentences: list[str] = []

        current_length = 0

        for sentence in sentences:

            sentence_length = len(sentence)

            additional_length = (
                sentence_length
                if not current_sentences
                else sentence_length + 1
            )

            if (
                current_sentences
                and current_length + additional_length > config.chunk_size
            ):

                chunk_text = " ".join(
                    current_sentences
                )

                chunks.append(
                    self._chunk_statistics(
                        chunk_text
                    )
                )

                if config.overlap_sentences > 0:

                    overlap_count = min(
                        config.overlap_sentences,
                        len(current_sentences)
                    )

                    current_sentences = current_sentences[
                        -overlap_count:
                    ]

                    current_length = sum(
                        len(sentence)
                        for sentence in current_sentences
                    )

                    if len(current_sentences) > 1:

                        current_length += (
                            len(current_sentences) - 1
                        )

                else:

                    current_sentences = []

                    current_length = 0

            current_sentences.append(
                sentence
            )

            current_length += additional_length

        if current_sentences:

            chunks.append(
                self._chunk_statistics(
                    " ".join(
                        current_sentences
                    )
                )
            )

        return chunks

    def chunk(
        self,
        text: str,
        config: ChunkingConfig | None = None
    ) -> list[str]:

        config = config or ChunkingConfig()

        if config.strategy != ChunkStrategy.SENTENCE:

            raise ValueError(
                f"Unsupported strategy: {config.strategy}"
            )

        all_chunks: list[Chunk] = []

        paragraphs = self.split_paragraphs(
            text,
            config
        )

        for paragraph in paragraphs:

            sentences = self.split_sentences(
                paragraph,
                config
            )

            paragraph_chunks = self.build_chunks(
                sentences,
                config
            )

            all_chunks.extend(
                paragraph_chunks
            )

        return [
            chunk.text
            for chunk in all_chunks
        ]


text_chunker = TextChunker()