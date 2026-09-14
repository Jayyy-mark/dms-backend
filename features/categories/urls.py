from features.categories.views import CategoryView, GetCategoryByIdView

from django.urls import path

urlpatterns = [
    path("create/", CategoryView.as_view()),
    path("update/<int:id>/", CategoryView.as_view()),
    path("delete/<int:id>/", CategoryView.as_view()),
    path("all/", CategoryView.as_view()),
    path("search/<int:id>/", GetCategoryByIdView.as_view()),
]
