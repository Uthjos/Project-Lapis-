from typing import ClassVar

from .exporter import AbstractExporter
from .json_exporter import JsonExporter


class ExporterFactory:
    _exporters: ClassVar[dict[str, type[AbstractExporter]]] = {"json": JsonExporter}

    @classmethod
    def get_exporter(cls, fmt: str) -> type[AbstractExporter]:
        exporter = cls._exporters.get(fmt.lower())
        if exporter is None:
            raise ValueError(f"Unknown exporter {fmt}")
        return exporter
