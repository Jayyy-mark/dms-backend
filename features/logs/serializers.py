from authentication.models import MogUser
from features.logs.models import AuditLog
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=MogUser
        # Only expose safe fields (never the password hash / permissions)
        fields=[
            "id",
            "user_id",
            "username",
            "email",
            "role",
            "is_active",
            "is_staff",
            "last_login",
            "date_joined",
        ]

class LogSerializer(serializers.ModelSerializer):

    user_id=serializers.IntegerField(allow_null=True)
    user = UserSerializer(allow_null=True)

    class Meta:
        model=AuditLog
        fields="__all__"