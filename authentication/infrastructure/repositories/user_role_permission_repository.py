from authentication.models import UserRolePermission


class UserRolePermissionRepository:

    @staticmethod
    def get_by_role(role_id: int) -> list[UserRolePermission]:
        return list(
            UserRolePermission.objects.select_related("feature", "feature__module")
            .filter(userRole_id=role_id)
            .order_by("id")
        )

    @staticmethod
    def bulk_save(role_id: int, permissions: list[dict]) -> None:
        """
        Replaces all permissions for a role.
        permissions: list of dicts like:
        [{ "feature_id": 1, "can_view": True, "can_create": False, ... }, ...]
        """
        # Delete existing permissions for this role
        UserRolePermission.objects.filter(userRole_id=role_id).delete()

        # Get next available ID
        max_id = (
            UserRolePermission.objects.order_by("-id")
            .values_list("id", flat=True)
            .first()
            or 0
        )

        # Create new permission records
        new_permissions = []
        for i, perm in enumerate(permissions):
            new_permissions.append(
                UserRolePermission(
                    id=max_id + 1 + i,
                    userRole_id=role_id,
                    feature_id=perm["feature_id"],
                    can_view=perm.get("can_view", True),
                    can_create=perm.get("can_create", False),
                    can_edit=perm.get("can_edit", False),
                    can_delete=perm.get("can_delete", False),
                )
            )

        UserRolePermission.objects.bulk_create(new_permissions)

    @staticmethod
    def delete_by_role(role_id: int) -> None:
        UserRolePermission.objects.filter(userRole_id=role_id).delete()
