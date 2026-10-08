from dataclasses import dataclass
from typing import Optional


@dataclass
class ModuleResponseContract:
    id: int
    name: str
    status: bool


@dataclass
class ModuleCreateContract:
    name: str
    status: Optional[bool] = True


@dataclass
class ModuleUpdateContract:
    id: int
    name: str
    status: bool
