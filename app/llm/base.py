from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """
    Abstract LLM Interface
    All LLM providers must implement this.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass