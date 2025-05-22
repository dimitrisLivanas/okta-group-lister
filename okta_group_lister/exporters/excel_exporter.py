import logging
import pandas as pd
from colorama import Fore
from .base import Exporter

logger = logging.getLogger(__name__)

class ExcelExporter(Exporter):
    def export(self) -> None:
        filename = f"{self.base_filename}.xlsx"
        try:
            df = pd.DataFrame([
                {
                    "ID": member.id,
                    "Login": member.login,
                    "Email": member.email,
                    "FirstName": member.first_name,
                    "LastName": member.last_name,
                }
                for member in self.members
            ])
            df.to_excel(filename, index=False)
            print(f"{Fore.GREEN}Successfully exported group members to: {filename}{Fore.RESET}")
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            print(f"{Fore.RED}Error exporting to Excel: {e}. Check file path and permissions.{Fore.RESET}") 