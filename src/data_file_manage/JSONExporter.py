import json
from pathlib import Path

from .Exporter import AbstractExporter


class JSONExporter(AbstractExporter):
    @staticmethod
    def export(data, fileName) -> None:
        path = Path(fileName)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(fileName, 'w', encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
