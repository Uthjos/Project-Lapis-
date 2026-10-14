from src.data_file_manage import JSONExporter


class ExporterFactory:
    @staticmethod
    def createExporter(format: str):

        # add different file formats here
        exporters = {
            "json": JSONExporter
        }

        exporter_class = exporters.get(format.lower())

        if exporter_class is None:
            raise ValueError(f"Unknown exporter {format}")

        return exporter_class