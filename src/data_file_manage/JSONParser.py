import json
from pathlib import Path


class Parser:
    @staticmethod
    def parse_file(file_path: str | Path) -> dict:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            return data
