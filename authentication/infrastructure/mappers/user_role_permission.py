from authentication.domain.user_role_permission_entity import UserRolePermissionEntity
from authentication.models import UserRolePermission


class UserRolePermissionMapper:

    @staticmethod
    def toEntity(permission: UserRolePermission):

        return UserRolePermissionEntity(
            id=permission.id,
            can_create=permission.can_create,
            can_edit=permission.can_edit,
            can_delete=permission.can_delete,
            can_view=permission.can_view,
            feature=permission.feature,
            userRole=permission.userRole,
        )
