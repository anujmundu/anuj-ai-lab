from PyPDF2 import PdfReader


class PDFConnector:

    def read(
        self,
        filepath: str
    ):

        try:

            reader = PdfReader(filepath)

            text = ""

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:

                    text += extracted

            return text

        except Exception as e:

            return f"PDF read error: {str(e)}"


pdf_connector = PDFConnector()