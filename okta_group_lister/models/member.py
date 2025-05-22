from typing import Dict, Any
from tabulate import tabulate
from colorama import Fore, Style

class Member:
    def __init__(self, id: str, login: str, email: str, first_name: str, last_name: str):
        self.id = id
        self.login = login
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or "-"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Member':
        profile = data['profile']
        return cls(
            id=data['id'],
            login=profile.get('login', '-'),
            email=profile.get('email', '-'),
            first_name=profile.get('firstName', '-'),
            last_name=profile.get('lastName', '-')
        )

    def display(self) -> None:
        print(f"\n{Fore.BLUE}Member:{Style.RESET_ALL}")
        print(tabulate(
            [[
                f"{Fore.CYAN}{self.id}{Style.RESET_ALL}",
                f"{Fore.GREEN}{self.login}{Style.RESET_ALL}",
                self.email,
                self.full_name
            ]],
            headers=["ID", "Login", "Email", "Name"],
            tablefmt="grid"
        )) 