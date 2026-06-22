from app.file_connectors.csv_connector import csv_connector


class CSVTool:

    def read(
        self,
        filepath: str
    ):

        return csv_connector.read(
            filepath
        )


csv_tool = CSVTool()