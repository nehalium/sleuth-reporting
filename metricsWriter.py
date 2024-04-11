from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import pandas as pd


class MetricsWriter:
    output_dir = "output"
    metric_type = "Unknown"

    def __init__(self, metric_type):
        self.metric_type = metric_type

    def write_to_excel(self, metrics, items):
        self.ensure_path()
        df = pd.DataFrame(metrics)
        writer = pd.ExcelWriter(self.get_file_name(), engine="xlsxwriter")
        df.to_excel(writer, sheet_name=self.metric_type)
        for item in items:
            df.query(f"slug == '{item["slug"]}'").transpose().to_excel(writer, sheet_name=item["name"][:30])
        writer.close()

    def ensure_path(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def get_file_name(self):
        return f"{self.output_dir}/sleuth-by-{self.metric_type.lower()}-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx"
