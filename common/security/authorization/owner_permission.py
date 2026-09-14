# common/security/authorization/owner_permission.py
from rest_framework.permissions import BasePermission

class IsOwnerPermission(BasePermission):
    """
    Allows access only to object owner
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not hasattr(user, "payload"):
            return False

        return obj.user_id == user.payload.get("user_id")
