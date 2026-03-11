from abc import ABC, abstractmethod
from typing import List


class BaseVectorStore(ABC):
    """
    Abstract Vector Store Interface
    """

    @abstractmethod
    def upsert(self, documents: List[str]) -> dict:
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[str]:
        pass