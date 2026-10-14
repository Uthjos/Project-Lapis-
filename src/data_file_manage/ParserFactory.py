from pathlib import Path

from src.data_file_manage import JSONParser


def get_file_format (file_path):
    return Path(file_path).suffix.lower().lstrip('.')


class ParserFactory:
    @staticmethod
    def createParser(file_name: str):
        filetype = get_file_format(format)
        parsers = {
            'json': JSONParser,
        }

        parser = parsers.get(filetype)
        if parser is None:
            raise ValueError(f"Unknown exporter {filetype}")

        return parser