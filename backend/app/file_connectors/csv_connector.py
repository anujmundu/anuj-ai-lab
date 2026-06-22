import csv


class CSVConnector:

    def read(
        self,
        filepath: str
    ):

        rows = []

        with open(
            filepath,
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                rows.append(
                    row
                )

        return rows


csv_connector = CSVConnector()