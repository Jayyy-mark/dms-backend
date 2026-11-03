from django.urls import path
from features.staffs.views import StaffView, StaffListView, GetStaffByIdView

urlpatterns = [
    path("all/", StaffView.as_view()),
    path("list/", StaffListView.as_view()),
    path("create/", StaffView.as_view()),
    path("update/<int:id>/", StaffView.as_view()),
    path("delete/<int:id>/", StaffView.as_view()),
    path("search/<int:id>/", GetStaffByIdView.as_view()),
    path("search/", StaffView.as_view()),
]
