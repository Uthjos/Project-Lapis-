from abc import ABC, abstractmethod


class AbstractExporter(ABC):

    @staticmethod
    @abstractmethod
    def export(data, filename: str) -> None:...