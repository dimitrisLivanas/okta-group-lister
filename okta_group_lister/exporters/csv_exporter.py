import csv
import logging
from colorama import Fore
from .base import Exporter

logger = logging.getLogger(__name__)

class CSVExporter(Exporter):
    def export(self) -> None:
        filename = f"{self.base_filename}.csv"
        fieldnames = ["ID", "Login", "Email", "FirstName", "LastName"]
        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for member in self.members:
                    writer.writerow({
                        "ID": member.id,
                        "Login": member.login,
                        "Email": member.email,
                        "FirstName": member.first_name,
                        "LastName": member.last_name,
                    })
            print(f"{Fore.GREEN}Successfully exported group members to: {filename}{Fore.RESET}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            print(f"{Fore.RED}Error exporting to CSV: {e}. Check file path and permissions.{Fore.RESET}") 