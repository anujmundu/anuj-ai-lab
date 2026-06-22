from app.file_connectors.pdf_connector import pdf_connector


class PDFTool:

    def read(
        self,
        filepath: str
    ):

        return pdf_connector.read(
            filepath
        )


pdf_tool = PDFTool()