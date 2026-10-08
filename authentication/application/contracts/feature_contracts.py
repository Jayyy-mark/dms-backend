from dataclasses import dataclass
from typing import Optional


@dataclass
class FeatureResponseContract:
    id: int
    name: str
    status: bool
    module_id: Optional[int] = None
    module_name: Optional[str] = None
