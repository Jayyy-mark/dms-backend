from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers


PRIVILEGED_ROLES = {"admin", "super admin", "super_admin", "superadmin"}


class OptionalIntegerField(serializers.IntegerField):
    """Coerce empty strings and null-like values to None before integer parsing."""

    def to_internal_value(self, data):
        if data in ("", None, "null", "undefined"):
            return None
        return super().to_internal_value(data)


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    staff_id = OptionalIntegerField(required=False, allow_null=True, default=None)

    def validate(self, data):
        data = super().validate(data)
        role_normalized = (data.get("role") or "").strip().lower()
        staff_id = data.get("staff_id")

        if role_normalized and role_normalized not in PRIVILEGED_ROLES and not staff_id:
            raise serializers.ValidationError(
                {"staff_id": "A staff member must be selected for this role."}
            )
        return data

    def save(self, request):
        user = super().save(request)
        # Save extra fields
        user.username = self.validated_data.get("username", "")
        user.role = self.validated_data.get("role")
        staff_id = self.validated_data.get("staff_id")
        user.staff_id = staff_id if staff_id not in ("", None) else None
        user.save()
        return user
