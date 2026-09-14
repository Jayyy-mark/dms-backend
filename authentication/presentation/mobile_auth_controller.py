from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.presentation.user_serializer import UserSerializer

User = get_user_model()

class MobileLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email") or request.data.get("username")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attempt standard authentication
        user = authenticate(request, username=email, password=password)
        if user is None:
            user = authenticate(request, email=email, password=password)
        
        # Fallback to direct model password check if backend requires specific kwarg
        if user is None:
            try:
                candidate = User.objects.get(email=email)
                if candidate.check_password(password):
                    user = candidate
            except User.DoesNotExist:
                pass

        if user is None or not user.is_active:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate simplejwt tokens
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )
