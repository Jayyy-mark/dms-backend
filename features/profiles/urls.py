from django.urls import path
from features.profiles.views import (
    ProfileInfoUpdateView,
    ProfileAddressUpdateView,
    ProfilePasswordUpdateView,
)

urlpatterns = [
    path("user/profile/info/update/", ProfileInfoUpdateView.as_view(), name="profile-info-update"),
    path("user/profile/info/update", ProfileInfoUpdateView.as_view()),
    path("user/profile/address/update/", ProfileAddressUpdateView.as_view(), name="profile-address-update"),
    path("user/profile/address/update", ProfileAddressUpdateView.as_view()),
    path("user/profile/password/update/", ProfilePasswordUpdateView.as_view(), name="profile-password-update"),
    path("user/profile/password/update", ProfilePasswordUpdateView.as_view()),
]
