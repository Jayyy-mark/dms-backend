from django.urls import path
from features.departments.views import DepartmentView, GetDepartmentByIdView

urlpatterns = [
    path("all/", DepartmentView.as_view()),
    path("create/", DepartmentView.as_view()),
    path("update/<int:id>/", DepartmentView.as_view()),
    path("delete/<int:id>/", DepartmentView.as_view()),
    path("search/<int:id>/", GetDepartmentByIdView.as_view()),
    path("search/", DepartmentView.as_view()), # search with query params
]
