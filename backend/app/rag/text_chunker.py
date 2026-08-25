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

    def _chunk_sentence(
        self,
        text: str,
        config: ChunkingConfig,
    ) -> list[str]:
        all_chunks: list[Chunk] = []
        paragraphs = self.split_paragraphs(text, config)

        for paragraph in paragraphs:
            sentences = self.split_sentences(paragraph, config)
            paragraph_chunks = self.build_chunks(sentences, config)
            all_chunks.extend(paragraph_chunks)

        return [chunk.text for chunk in all_chunks]

    def _chunk_paragraph(
        self,
        text: str,
        config: ChunkingConfig,
    ) -> list[str]:
        paragraphs = self.split_paragraphs(text, config)
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for p in paragraphs:
            if current and current_len + len(p) > config.chunk_size:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(p)
            current_len += len(p)

        if current:
            chunks.append("\n\n".join(current))

        return chunks

    def _chunk_markdown(
        self,
        text: str,
        config: ChunkingConfig,
    ) -> list[str]:
        # Split by markdown headers (#, ##, ###) while preserving the header line
        sections = re.split(r"(?=(?:^|\n)#{1,6}\s+)", text)
        sections = [s.strip() for s in sections if s.strip()]

        chunks: list[str] = []
        for section in sections:
            if len(section) <= config.chunk_size:
                chunks.append(section)
            else:
                # If section is too large, fallback to sentence-level chunking
                chunks.extend(self._chunk_sentence(section, config))

        return chunks if chunks else [text]

    def _chunk_code(
        self,
        text: str,
        config: ChunkingConfig,
    ) -> list[str]:
        # Split by function / class boundaries (def, class, function, export)
        blocks = re.split(r"(?=(?:^|\n)(?:def |class |async def |function |export ))", text)
        blocks = [b.strip() for b in blocks if b.strip()]

        chunks: list[str] = []
        for block in blocks:
            if len(block) <= config.chunk_size:
                chunks.append(block)
            else:
                chunks.extend(self._chunk_sentence(block, config))

        return chunks if chunks else [text]

    def _chunk_fixed(
        self,
        text: str,
        config: ChunkingConfig,
    ) -> list[str]:
        step = max(1, config.chunk_size - (config.overlap_sentences * 50))
        return [
            text[i : i + config.chunk_size].strip()
            for i in range(0, len(text), step)
            if text[i : i + config.chunk_size].strip()
        ]

    def chunk(
        self,
        text: str,
        config: ChunkingConfig | None = None
    ) -> list[str]:

        config = config or ChunkingConfig()

        strategy = config.strategy
        if isinstance(strategy, str):
            try:
                strategy = ChunkStrategy(strategy.lower())
            except ValueError:
                pass

        if strategy == ChunkStrategy.SENTENCE:
            return self._chunk_sentence(text, config)

        if strategy == ChunkStrategy.PARAGRAPH:
            return self._chunk_paragraph(text, config)

        if strategy == ChunkStrategy.MARKDOWN:
            return self._chunk_markdown(text, config)

        if strategy == ChunkStrategy.CODE:
            return self._chunk_code(text, config)

        if strategy in {ChunkStrategy.FIXED, ChunkStrategy.RECURSIVE}:
            return self._chunk_fixed(text, config)

        raise ValueError(
            f"Unsupported strategy: {config.strategy}"
        )


text_chunker = TextChunker()