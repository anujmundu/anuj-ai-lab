class TXTConnector:

    def read(
        self,
        filepath: str
    ):

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()


txt_connector = TXTConnector()