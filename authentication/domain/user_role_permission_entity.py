from dataclasses import dataclass
from typing import Optional
from .feature_entity import FeatureEntity
from .user_role_entity import UserRoleEntity


@dataclass
class UserRolePermissionEntity:

    id: int
    feature: Optional[FeatureEntity] = None
    userRole: Optional[UserRoleEntity] = None
    can_view: Optional[bool] = True
    can_edit: Optional[bool] = True
    can_create: Optional[bool] = True
    can_delete: Optional[bool] = True
