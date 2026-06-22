from app.connectors.wikipedia_connector import wikipedia_connector


class WikipediaTool:

    def search(
        self,
        topic: str
    ):

        return wikipedia_connector.search(
            topic
        )


wikipedia_tool = WikipediaTool()