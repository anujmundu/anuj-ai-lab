import json
from pathlib import Path
import pandas as pd
from pypdf import PdfReader

_whisper_singleton = None


def _get_whisper_model():
    global _whisper_singleton
    if _whisper_singleton is None:
        try:
            from faster_whisper import WhisperModel
            _whisper_singleton = WhisperModel("tiny", device="cpu", compute_type="int8")
        except Exception:
            _whisper_singleton = None
    return _whisper_singleton


class DocumentLoader:
    """
    Structured and multi-modal document loader.
    Converts diverse document formats into clean, structured Markdown text.
    """

    SUPPORTED_TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".markdown",
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".html",
        ".xml",
        ".yaml",
        ".yml",
        ".log",
    }

    SUPPORTED_AUDIO_VIDEO_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".mp3",
        ".wav",
        ".m4a",
        ".ogg",
        ".flac",
    }

    def load(self, file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix in self.SUPPORTED_TEXT_EXTENSIONS:
            return self._load_text(path)

        if suffix == ".json":
            return self._load_json(path)

        if suffix == ".csv":
            return self._load_csv(path)

        if suffix in {".tsv", ".tab"}:
            return self._load_tsv(path)

        if suffix == ".pdf":
            return self._load_pdf(path)

        if suffix in {".docx", ".doc"}:
            return self._load_docx(path)

        if suffix in self.SUPPORTED_AUDIO_VIDEO_EXTENSIONS:
            return self._load_media(path)

        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def _load_json(self, path: Path) -> str:
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2)

    def _load_csv(self, path: Path) -> str:
        try:
            df = pd.read_csv(path)
            return df.to_markdown(index=False)
        except Exception:
            df = pd.read_csv(path)
            return df.to_string(index=False)

    def _load_tsv(self, path: Path) -> str:
        try:
            df = pd.read_csv(path, sep="\t")
            return df.to_markdown(index=False)
        except Exception:
            df = pd.read_csv(path, sep="\t")
            return df.to_string(index=False)

    def _load_pdf(self, path: Path) -> str:
        reader = PdfReader(path)
        pages_text = []

        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                pages_text.append(
                    f"--- Page {page_num} ---\n{page_text.strip()}"
                )

        return "\n\n".join(pages_text)

    def _load_docx(self, path: Path) -> str:
        try:
            import docx
            doc = docx.Document(path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as err:
            return f"# Document: {path.name}\n\nCould not extract text: {err}"

    def _load_media(self, path: Path) -> str:
        """Transcribes audio and video files into structured Markdown transcript with VAD filtering."""
        try:
            model = _get_whisper_model()
            if model is not None:
                segments, info = model.transcribe(
                    str(path),
                    beam_size=1,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=400),
                )
                lines = [
                    f"# Media Transcript: {path.name}",
                    f"**Detected Language:** {info.language} ({info.language_probability:.2f})\n",
                ]
                for seg in segments:
                    start_min, start_sec = divmod(int(seg.start), 60)
                    end_min, end_sec = divmod(int(seg.end), 60)
                    lines.append(f"[{start_min:02d}:{start_sec:02d} -> {end_min:02d}:{end_sec:02d}] {seg.text.strip()}")
                return "\n\n".join(lines) if len(lines) > 2 else f"# Media Transcript: {path.name}\n\nNo speech detected in media file."
        except Exception as err:
            try:
                import whisper
                fallback_model = whisper.load_model("tiny")
                res = fallback_model.transcribe(str(path))
                return f"# Media Transcript: {path.name}\n\n{res.get('text', '')}"
            except Exception as e:
                return f"# Media File: {path.name}\n\nAudio/Video transcription notice: {err} ({e})"

        return f"# Media File: {path.name}\n\nTranscription engine unavailable."


document_loader = DocumentLoader()