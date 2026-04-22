from abc import ABC, abstractmethod


class BasePublisher(ABC):
    platform_name = "unknown"

    @abstractmethod
    def publish(self, text: str, media: dict | None = None) -> dict:
        pass