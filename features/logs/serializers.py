from authentication.models import MogUser
from features.logs.models import AuditLog
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=MogUser
        fields="__all__"

class LogSerializer(serializers.ModelSerializer):

    user_id=serializers.IntegerField()
    user = UserSerializer()

    class Meta:
        model=AuditLog
        fields="__all__"