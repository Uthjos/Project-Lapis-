import json
from pathlib import Path

from .exporter import AbstractExporter


class JsonExporter(AbstractExporter):
    @staticmethod
    def export(data, filename) -> None:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
