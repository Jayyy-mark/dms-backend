from dataclasses import dataclass
from typing import Optional


@dataclass
class PermissionResponseContract:
    id: int
    feature_name: str
    feature_id: int
    can_view: bool
    can_create: bool
    can_edit: bool
    can_delete: bool
    module_name: Optional[str] = None
