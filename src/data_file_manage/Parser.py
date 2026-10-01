import json
class Parser:

    # acts as an initializer as this class does not have stored data
    def __init__(self):
        pass

    @staticmethod
    def parse_file(file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)
            return data