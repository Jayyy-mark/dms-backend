from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from authentication.models import UserRole, Feature, UserRolePermission


def check_feature_permission(user, feature_name: str, action: str) -> bool:
    """
    Checks if a user has permission for a specific feature and action ('view', 'create', 'edit', 'delete').
    Also ensures the feature is enabled globally in the features table.
    """
    if not user or not user.is_authenticated:
        return False

    # Check if feature is globally enabled
    try:
        feature = Feature.objects.get(name=feature_name)
        if not feature.status:
            return False
    except Feature.DoesNotExist:
        # If the feature is not explicitly tracked in DB, allow
        return True

    user_role_name = getattr(user, "role", None)
    if not user_role_name:
        return False

    try:
        user_role = UserRole.objects.get(name__iexact=user_role_name)
    except UserRole.DoesNotExist:
        return False

    try:
        perm = UserRolePermission.objects.get(userRole=user_role, feature=feature)
    except UserRolePermission.DoesNotExist:
        return False

    normalized_action = action.lower()
    if normalized_action in ["view"]:
        return bool(perm.can_view)
    elif normalized_action in ["create", "add"]:
        return bool(perm.can_create)
    elif normalized_action in ["edit", "update"]:
        return bool(perm.can_edit)
    elif normalized_action in ["delete"]:
        return bool(perm.can_delete)

    return False


# Map URL path prefixes to feature keys
PATH_FEATURE_PREFIXES = [
    ("/api/auth/users/", "users"),
    ("/api/staff/", "employees"),
    ("/api/department/", "departments"),
    ("/api/building/", "buildings"),
    ("/api/room/", "rooms"),
    ("/api/stype/", "staff_types"),
    ("/api/role/", "roles"),
    ("/api/rank/", "ranks"),
    ("/api/category/", "categories"),
    ("/api/document/", "documents"),
    ("/api/dtype/", "dtypes"),
    ("/api/location/", "locations"),
    ("/api/log/", "logs"),
    ("/api/chat/", "chatbot"),
    ("/api/chats/", "chatbot"),
]


class HasFeaturePermission(BasePermission):
    """
    DRF BasePermission subclass that enforces permissions based on:
    1. view.feature_name (if explicitly declared on the view)
    2. or request.path prefix mapping
    """

    def has_permission(self, request: Request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # Determine feature name
        feature_name = getattr(view, "feature_name", None)
        if not feature_name:
            path = request.path
            for prefix, feat in PATH_FEATURE_PREFIXES:
                if path.startswith(prefix):
                    feature_name = feat
                    break

        # If not matching any governed feature, grant permission (fall back to IsAuthenticated)
        if not feature_name:
            return True

        # Map HTTP method to action
        method = request.method.upper()
        if method in ["GET", "HEAD", "OPTIONS"]:
            action = "view"
        elif method == "POST":
            action = "create"
        elif method in ["PUT", "PATCH"]:
            action = "edit"
        elif method == "DELETE":
            action = "delete"
        else:
            action = "view"

        return check_feature_permission(request.user, feature_name, action)
