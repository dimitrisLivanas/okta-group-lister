from typing import List
from .base import Exporter
from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .excel_exporter import ExcelExporter
from ..models.member import Member

def get_exporter(format: str, members: List[Member], group_name: str) -> Exporter:
    exporters = {
        "csv": CSVExporter,
        "json": JSONExporter,
        "excel": ExcelExporter
    }
    return exporters[format.lower()](members, group_name)
