from abc import ABC, abstractmethod
class BaseAgent(ABC):
    name = "base"
    description = ""
    @abstractmethod
    async def handle(self, prompt: str, **kwargs) -> dict:
        raise NotImplementedError
