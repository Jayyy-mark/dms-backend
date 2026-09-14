from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework import status

class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh access token using refresh token stored in HttpOnly cookie
    """

    def post(self, request, *args, **kwargs):
        refresh_cookie_name = settings.REST_AUTH.get(
            "JWT_AUTH_REFRESH_COOKIE",
            "mogApp_refresh_cookie",
        )

        access_cookie_name = settings.REST_AUTH.get(
            "JWT_AUTH_COOKIE",
            "mogApp_cookie",
        )

        refresh_token = request.COOKIES.get(refresh_cookie_name)

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(
            data={"refresh": refresh_token}
        )
        serializer.is_valid(raise_exception=True)

        access_token = serializer.validated_data["access"]

        response = Response(
            {"detail": "Access token refreshed"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key=access_cookie_name,
            value=access_token,
            httponly=True,
            secure=settings.REST_AUTH.get("JWT_AUTH_SECURE", False),
            samesite=settings.REST_AUTH.get("JWT_AUTH_SAMESITE", "Lax"),
            max_age=60 * 15,  # 15 minutes
            path="/",
        )

        return response
