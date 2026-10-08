from dataclasses import dataclass
from typing import Optional
from .module_entity import ModuleEntity


@dataclass
class FeatureEntity:

    id: int
    name: str
    module: Optional[ModuleEntity] = None
    status: Optional[bool] = True
