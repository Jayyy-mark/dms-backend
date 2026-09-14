#<!--================================
#   REQUIRED IMPORTS
#=================================-->
from django.urls import path
from dj_rest_auth.views import LoginView, UserDetailsView, LogoutView
from dj_rest_auth.registration.views import RegisterView

from authentication.presentation.user_controller import UserController
from authentication.presentation.cookie_controller import CookieTokenRefreshView
from authentication.presentation.mobile_auth_controller import MobileLoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="signup"),
    path("user/", UserDetailsView.as_view(), name="user-details"),
    path("users/<int:id>/", UserController.as_view(), name="user-update"),
    path("users/<int:id>/", UserController.as_view(), name="user-delete"),
    path("users/", UserController.as_view(), name="users"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("mobile/login/", MobileLoginView.as_view(), name="mobile_login"),
    path("mobile/token/refresh/", TokenRefreshView.as_view(), name="mobile_token_refresh"),
]