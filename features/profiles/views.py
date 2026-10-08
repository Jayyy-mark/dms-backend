from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import update_session_auth_hash

from authentication.models import MogUser
from authentication.presentation.user_serializer import UserSerializer
from features.staffs.models import Staff
from features.staffs.serializers import StaffSerializer
from features.shared.helpers.helper import log_action


def get_user_staff(user):
    """Resolve linked staff object for the authenticated user."""
    staff = getattr(user, "staff", None)
    if not staff and getattr(user, "staff_id", None):
        staff = Staff.objects.filter(id=user.staff_id).first()
    if not staff and user.email:
        staff = Staff.objects.filter(staff_email=user.email).first()
    return staff


class ProfileInfoUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        return self._update(request)

    def post(self, request):
        return self._update(request)

    def _update(self, request):
        user = request.user
        data = request.data

        staff_name = (data.get("staff_name") or data.get("full_name") or "").strip()
        email = (data.get("email") or data.get("staff_email") or "").strip()
        phone = (data.get("staff_ph_number") or data.get("phone") or "").strip()
        username = (data.get("username") or "").strip()

        staff = get_user_staff(user)

        # 1. Email validation & update
        if email and email.lower() != user.email.lower():
            if MogUser.objects.exclude(id=user.id).filter(email__iexact=email).exists():
                return views.Response(
                    {"message": "This email address is already in use by another user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if staff and Staff.objects.exclude(id=staff.id).filter(staff_email__iexact=email).exists():
                return views.Response(
                    {"message": "This email address is already registered to another staff member."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = email
            if staff:
                staff.staff_email = email

        # 2. Username validation & update
        if username and username != user.username:
            if MogUser.objects.exclude(id=user.id).filter(username__iexact=username).exists():
                return views.Response(
                    {"message": "This username is already taken."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.username = username

        # 3. Staff specific fields validation & update
        if staff:
            if staff_name and staff_name != staff.staff_name:
                if Staff.objects.exclude(id=staff.id).filter(staff_name__iexact=staff_name).exists():
                    return views.Response(
                        {"message": "A staff member with this name already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                staff.staff_name = staff_name

            if phone and phone != staff.staff_ph_number:
                if Staff.objects.exclude(id=staff.id).filter(staff_ph_number=phone).exists():
                    return views.Response(
                        {"message": "This phone number is already registered to another staff member."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                staff.staff_ph_number = phone

            staff.save()

        user.save()

        try:
            log_action(user, "update", "profile", user.id, "Updated personal profile information")
        except Exception:
            pass

        return views.Response(
            {
                "message": "Personal information updated successfully!",
                "user": UserSerializer(user).data,
                "staff": StaffSerializer(staff).data if staff else None,
            },
            status=status.HTTP_200_OK,
        )


class ProfileAddressUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        return self._update(request)

    def post(self, request):
        return self._update(request)

    def _update(self, request):
        user = request.user
        address = (request.data.get("staff_address") or request.data.get("address") or "").strip()

        if not address:
            return views.Response(
                {"message": "Address is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        staff = get_user_staff(user)
        if not staff:
            return views.Response(
                {"message": "No associated staff record found to update address."},
                status=status.HTTP_404_NOT_FOUND,
            )

        staff.staff_address = address
        staff.save()

        try:
            log_action(user, "update", "profile", staff.id, "Updated profile address")
        except Exception:
            pass

        return views.Response(
            {
                "message": "Address updated successfully!",
                "staff": StaffSerializer(staff).data,
            },
            status=status.HTTP_200_OK,
        )


class ProfilePasswordUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        return self._update(request)

    def post(self, request):
        return self._update(request)

    def _update(self, request):
        user = request.user
        data = request.data

        old_password = data.get("old_password")
        new_password = data.get("new_password")
        retype_new_password = (
            data.get("retype_new_password")
            or data.get("confirm_password")
            or data.get("retype_password")
        )

        if not old_password or not new_password or not retype_new_password:
            return views.Response(
                {"message": "Old password, new password, and retyped new password are all required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return views.Response(
                {"message": "The old password you entered is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != retype_new_password:
            return views.Response(
                {"message": "New password and retyped new password do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if old_password == new_password:
            return views.Response(
                {"message": "New password cannot be the same as your old password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            return views.Response(
                {"message": " ".join(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        try:
            update_session_auth_hash(request, user)
        except Exception:
            pass

        try:
            log_action(user, "update", "profile", user.id, "Changed account password")
        except Exception:
            pass

        return views.Response(
            {"message": "Password changed successfully!"},
            status=status.HTTP_200_OK,
        )
