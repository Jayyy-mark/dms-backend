from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import exceptions

User = get_user_model()


class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")
        password = attrs.get("password")

        identifier = email or username
        if identifier and password:
            user = (
                User.objects.filter(email__iexact=identifier).first()
                or User.objects.filter(username__iexact=identifier).first()
            )
            if user and user.check_password(password):
                if not user.is_active:
                    raise exceptions.ValidationError("Your account has been banned.")

                # Normalize email for email-based authentication in case username was provided
                attrs["email"] = user.email

        return super().validate(attrs)
