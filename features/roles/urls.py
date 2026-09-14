from django.urls import path
from features.roles.views import RoleView, GetRoleByIdView

urlpatterns = [
    path("all/", RoleView.as_view()),
    path("create/", RoleView.as_view()),
    path("update/<int:id>/", RoleView.as_view()),
    path("delete/<int:id>/", RoleView.as_view()),
    path("search/<int:id>/", GetRoleByIdView.as_view()),
    path("search/", RoleView.as_view()),
]
