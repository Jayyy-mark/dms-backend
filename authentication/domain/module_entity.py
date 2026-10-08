from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ModuleEntity:

    id: int
    name: str
    status: Optional[bool] = True
