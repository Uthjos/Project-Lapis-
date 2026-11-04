from .Exporter import AbstractExporter
from .JSONExporter import JSONExporter


class ExporterFactory:
    def __init__(self):
        # add different file formats here
        _exporters = {"json": JSONExporter}


    @classmethod
    def get_exporter(cls, format: str) -> type[AbstractExporter]:
        exporter = cls._exporters(format.lower())
        if exporter is None:
            raise ValueError(f"Unknown exporter {format}")
        return exporter