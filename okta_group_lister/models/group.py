from typing import Dict, Any
from tabulate import tabulate
from colorama import Fore, Style

class Group:
    def __init__(self, id: str, name: str, description: str = ""):
        self.id = id
        self.name = name
        self.description = description

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Group':
        return cls(
            id=data['id'],
            name=data['profile']['name'],
            description=data['profile'].get('description', '')
        )

    def display(self) -> None:
        print(f"\n{Fore.BLUE}Group:{Style.RESET_ALL}")
        print(tabulate(
            [[
                f"{Fore.CYAN}{self.id}{Style.RESET_ALL}",
                f"{Fore.GREEN}{self.name}{Style.RESET_ALL}",
                self.description
            ]],
            headers=["ID", "Name", "Description"],
            tablefmt="grid"
        )) 