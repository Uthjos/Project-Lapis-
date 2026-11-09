from pathlib import Path

from src.data_file_manage.json_parser import Parser


def get_file_format(file_path):
    return Path(file_path).suffix.lower().lstrip(".")


class ParserFactory:
    @staticmethod
    def create_parser(file_name: str):
        filetype = get_file_format(file_name)
        parsers = {"json": Parser}

        parser = parsers.get(filetype)
        if parser is None:
            raise ValueError(f"Unknown parser {filetype}")

        return parser
