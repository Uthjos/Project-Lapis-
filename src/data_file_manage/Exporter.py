from abc import ABC, abstractmethod


class AbstractExporter(ABC):
    @abstractmethod
    @staticmethod
    def export(data, filename: str):
        pass