import json

from .Exporter import AbstractExporter


class JSONExporter(AbstractExporter):
    @staticmethod
    def export(data, fileName: str):
        with open(fileName, 'w', encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4)
