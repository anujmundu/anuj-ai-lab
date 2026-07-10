class MemoryRetriever:

    def __init__(self, repository):
        self.repository = repository

    def relevant(self, query: str):
        return self.repository.search(query)

    def recent(self, limit=5):
        return self.repository.get_recent(limit)