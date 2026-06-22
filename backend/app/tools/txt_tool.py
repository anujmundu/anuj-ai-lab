from app.file_connectors.txt_connector import txt_connector


class TXTTool:

    def read(
        self,
        filepath: str
    ):

        return txt_connector.read(
            filepath
        )


txt_tool = TXTTool()