import json
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


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


document_loader = DocumentLoader()