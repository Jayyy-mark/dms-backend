#<!--================================
#   REQUIRED IMPORTS
#=================================-->
from django.urls import path
from dj_rest_auth.views import LoginView, UserDetailsView, LogoutView
from rest_framework import permissions

class CustomLoginView(LoginView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
from authentication.presentation.user_controller import UserController, CustomRegisterView
from authentication.presentation.cookie_controller import CookieTokenRefreshView
from authentication.presentation.mobile_auth_controller import MobileLoginView
from authentication.presentation.module_controller import (
    ModuleController,
    FeatureToggleController,
    FeatureBulkController,
)
from authentication.presentation.user_role_controller import (
    UserRoleController,
    UserRoleDetailController,
)
from authentication.presentation.permission_controller import (
    PermissionController,
    MyPermissionController,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", CustomRegisterView.as_view(), name="signup"),
    path("user/", UserDetailsView.as_view(), name="user-details"),
    path("users/<int:id>/", UserController.as_view(), name="user-update"),
    path("users/<int:id>/", UserController.as_view(), name="user-delete"),
    path("users/", UserController.as_view(), name="users"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("mobile/login/", MobileLoginView.as_view(), name="mobile_login"),
    path("mobile/token/refresh/", TokenRefreshView.as_view(), name="mobile_token_refresh"),

    # Module & Feature management
    path("modules/", ModuleController.as_view(), name="modules"),
    path("modules/features/<int:id>/", FeatureToggleController.as_view(), name="feature-toggle"),
    path("modules/features/bulk/", FeatureBulkController.as_view(), name="feature-bulk"),

    # User Role management
    path("user-roles/", UserRoleController.as_view(), name="user-roles"),
    path("user-roles/<int:id>/", UserRoleDetailController.as_view(), name="user-role-detail"),

    # Permissions
    path("permissions/my/", MyPermissionController.as_view(), name="my-permissions"),
    path("permissions/<int:role_id>/", PermissionController.as_view(), name="role-permissions"),
]