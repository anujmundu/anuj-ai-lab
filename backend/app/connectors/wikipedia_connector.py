class WikipediaConnector:

    def search(
        self,
        topic: str
    ):

        return {
            "topic": topic,
            "summary": f"{topic} is a topic retrieved from the Wikipedia connector."
        }


wikipedia_connector = WikipediaConnector()