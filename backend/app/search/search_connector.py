from app.connectors.wikipedia_connector import wikipedia_connector


class SearchConnector:

    def search(
        self,
        query: str
    ):

        return wikipedia_connector.search(
            query
        )


search_connector = SearchConnector()