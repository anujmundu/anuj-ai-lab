from enum import Enum


class RetrievalMode(str, Enum):

    STANDARD = "standard"

    ADAPTIVE = "adaptive"

    MULTI_QUERY = "multi_query"

    HYDE = "hyde"
    