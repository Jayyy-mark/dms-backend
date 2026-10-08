from authentication.infrastructure.repositories.user_role_repository import UserRoleRepository
from authentication.infrastructure.repositories.user_role_permission_repository import UserRolePermissionRepository
from authentication.infrastructure.repositories.feature_repository import FeatureRepository


class UserRoleService:

    def __init__(self):
        self.role_repo = UserRoleRepository()
        self.perm_repo = UserRolePermissionRepository()
        self.feature_repo = FeatureRepository()

    def get_all_roles(self):
        roles = self.role_repo.all()
        return [{"id": r.id, "name": r.name} for r in roles]

    def create_role(self, name: str):
        role = self.role_repo.create(name)
        return {"id": role.id, "name": role.name}

    def delete_role(self, role_id: int):
        self.perm_repo.delete_by_role(role_id)
        self.role_repo.delete(role_id)

    def get_permissions_for_role(self, role_id: int):
        """Returns permissions keyed by feature name for a specific role."""
        permissions = self.perm_repo.get_by_role(role_id)
        result = {}
        for perm in permissions:
            feature_name = perm.feature.name if perm.feature else None
            if feature_name:
                result[feature_name] = {
                    "can_view": perm.can_view,
                    "can_create": perm.can_create,
                    "can_edit": perm.can_edit,
                    "can_delete": perm.can_delete,
                }
        return result

    def save_permissions_for_role(self, role_id: int, permissions_data: dict):
        """
        permissions_data: dict keyed by feature_name ->
        { can_view, can_create, can_edit, can_delete }
        """
        # Get all features to map names to IDs
        features = self.feature_repo.all()
        feature_map = {f.name: f.id for f in features}

        perm_list = []
        for feature_name, perms in permissions_data.items():
            feature_id = feature_map.get(feature_name)
            if feature_id is not None:
                perm_list.append({
                    "feature_id": feature_id,
                    "can_view": perms.get("can_view", True),
                    "can_create": perms.get("can_create", False),
                    "can_edit": perms.get("can_edit", False),
                    "can_delete": perms.get("can_delete", False),
                })

        self.perm_repo.bulk_save(role_id, perm_list)

    def get_my_permissions(self, user_role_name: str):
        """Returns permissions and feature status for the current user's role."""
        role_entity = self.role_repo.get_by_name(user_role_name)

        # Get feature status map
        features = self.feature_repo.all()
        feature_status = {f.name: f.status for f in features}

        if not role_entity:
            # Role not found — return all permissions as true (admin fallback)
            permissions = {}
            for f in features:
                permissions[f.name] = {
                    "can_view": True,
                    "can_create": True,
                    "can_edit": True,
                    "can_delete": True,
                }
            return {
                "role_name": user_role_name,
                "permissions": permissions,
                "feature_status": feature_status,
            }

        # Get permissions for this role
        perm_records = self.perm_repo.get_by_role(role_entity.id)
        permissions = {}
        for perm in perm_records:
            if perm.feature:
                permissions[perm.feature.name] = {
                    "can_view": perm.can_view,
                    "can_create": perm.can_create,
                    "can_edit": perm.can_edit,
                    "can_delete": perm.can_delete,
                }

        return {
            "role_name": user_role_name,
            "permissions": permissions,
            "feature_status": feature_status,
        }
