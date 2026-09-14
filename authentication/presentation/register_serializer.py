from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=False)  # optional if you want
    role = serializers.CharField(required=False)
    staff_id = serializers.IntegerField(required=False, allow_null=True)

    def save(self, request):
        user = super().save(request)
        # Save extra fields
        user.username = self.validated_data.get("username", "")
        user.role = self.validated_data.get("role")
        user.staff_id = self.validated_data.get("staff_id", "")
        user.save()
        return user
