import json
import logging
from colorama import Fore
from .base import Exporter

logger = logging.getLogger(__name__)

class JSONExporter(Exporter):
    def export(self) -> None:
        filename = f"{self.base_filename}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([member.__dict__ for member in self.members], f, indent=2)
            print(f"{Fore.GREEN}Successfully exported group members to: {filename}{Fore.RESET}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            print(f"{Fore.RED}Error exporting to JSON: {e}. Check file path and permissions.{Fore.RESET}") 