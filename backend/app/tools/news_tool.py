from app.connectors.news_connector import news_connector


class NewsTool:

    def get_news(self):

        return news_connector.get_news()


news_tool = NewsTool()