import os
import re
from abc import ABC, abstractmethod
from typing import List
from ..models.member import Member

class Exporter(ABC):
    def __init__(self, members: List[Member], group_name: str):
        self.members = members
        self.group_name = group_name
        self.sanitized_group_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", group_name)
        self.base_filename = os.path.join(os.path.expanduser("~"), f"{self.sanitized_group_name}_members")

    @abstractmethod
    def export(self) -> None:
        pass 