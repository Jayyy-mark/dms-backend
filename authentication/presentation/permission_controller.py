from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from authentication.application.user_role_service import UserRoleService


class PermissionController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserRoleService()

    def get(self, request: Request, role_id: int):
        try:
            permissions = self.service.get_permissions_for_role(role_id)
            return Response({"permissions": permissions}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request: Request, role_id: int):
        permissions_data = request.data.get("permissions", {})
        if not permissions_data:
            return Response(
                {"message": "permissions data is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            self.service.save_permissions_for_role(role_id, permissions_data)
            return Response(
                {"message": "Permissions saved successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MyPermissionController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserRoleService()

    def get(self, request: Request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"message": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_role_name = getattr(user, "role", None)
        if not user_role_name:
            return Response(
                {"message": "User has no role assigned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = self.service.get_my_permissions(user_role_name)
        return Response(result, status=status.HTTP_200_OK)
