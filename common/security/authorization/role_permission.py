from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    """
    Role-based permission
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        # request.user is the Django User
        # request.auth is the JWT token
        if not request.user or not request.auth:
            return False

        # Read role from token claim
        token_role = request.auth.get("role")  # SimpleJWT token behaves like a dict
        return token_role in self.allowed_roles
