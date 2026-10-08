from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from authentication.application.user_role_service import UserRoleService


class UserRoleController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserRoleService()

    def get(self, request: Request):
        roles = self.service.get_all_roles()
        return Response({"roles": roles}, status=status.HTTP_200_OK)

    def post(self, request: Request):
        name = request.data.get("name")
        if not name or not name.strip():
            return Response(
                {"message": "Role name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            role = self.service.create_role(name.strip())
            return Response(
                {"message": "User role created", "role": role},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserRoleDetailController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserRoleService()

    def delete(self, request: Request, id: int):
        try:
            self.service.delete_role(id)
            return Response(
                {"message": "User role deleted"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
