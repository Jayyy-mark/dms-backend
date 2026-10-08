from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from dj_rest_auth.registration.views import RegisterView
from rest_framework.exceptions import PermissionDenied

from authentication.application.user_service import UserService
from authentication.infrastructure.user_repository import UserRepository
from authentication.presentation.permissions import HasFeaturePermission, check_feature_permission


class CustomRegisterView(RegisterView):
    def post(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            if not check_feature_permission(request.user, "users", "create"):
                return Response(
                    {"error": "You do not have permission to add users.", "message": "Permission denied: create user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().post(request, *args, **kwargs)


class UserController(APIView):
    permission_classes = [HasFeaturePermission]
    feature_name = "users"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())
    
    def get(self, request: Request, id:int = None):
        if id is None:
            users = self.service.all()
            return Response({
                "users" : [
                    u.__dict__ for u in users
                ]
            },status=status.HTTP_200_OK)
        
        user = self.service.getUserById(id=id)

        if not user:
            return Response(
                {"message" : "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {"user" : user.__dict__},
            status=status.HTTP_200_OK
        )
    
    def delete(self, request: Request, id:int)->str:
        message = self.service.delete(id)

        return Response({
            "message" : message
        },status=status.HTTP_200_OK)
    
    def put(self, request: Request, id: int):
        data = request.data
        username = data.get("username")
        email = data.get("email")
        role = data.get("role")
        
        if not username or not email or not role:
            return Response(
                {"message": "username, email and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            updated_user = self.service.update(id=id, username=username, email=email, role=role)
            return Response(
                {"message": "User updated successfully", "user": updated_user.__dict__},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )