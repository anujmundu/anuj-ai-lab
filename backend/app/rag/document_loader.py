from pathlib import Path

import pandas as pd
from pypdf import PdfReader


class DocumentLoader:

    def load(self, file_path: str) -> str:

        path = Path(file_path)

        suffix = path.suffix.lower()

        if suffix == ".txt":
            return self._load_txt(path)

        if suffix == ".csv":
            return self._load_csv(path)

        if suffix == ".pdf":
            return self._load_pdf(path)

        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_txt(self, path: Path) -> str:

        return path.read_text(
            encoding="utf-8"
        )

    def _load_csv(self, path: Path) -> str:

        df = pd.read_csv(path)

        return df.to_string(index=False)

    def _load_pdf(self, path: Path) -> str:

        reader = PdfReader(path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text


document_loader = DocumentLoader()