from app.search.search_connector import search_connector


class SearchTool:

    def search(
        self,
        query: str
    ):

        return search_connector.search(
            query
        )


search_tool = SearchTool()