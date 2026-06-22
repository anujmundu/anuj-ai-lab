class NewsConnector:

    def get_news(self):

        return {
            "headlines": [
                "AI is transforming healthcare.",
                "FastAPI adoption continues to grow.",
                "Open-source LLMs are becoming more popular."
            ]
        }


news_connector = NewsConnector()