import json


class JSONExporter:
    def export(self, data, fileName):
        json_data = json.dumps(data, indent=4)

        with open(fileName, 'w') as outfile:
            outfile.write(json_data)
