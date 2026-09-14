from django.urls import path

from features.locations.views import (
    LocationView,
    GetLocationByColumnView,
    GetLocationByIdView,
    GetLocationOptionsView,
)

urlpatterns = [
    path("create/", LocationView.as_view()),
    path("update/<int:id>/", LocationView.as_view()),
    path("delete/<int:id>/", LocationView.as_view()),
    path("archive/<int:id>/", LocationView.as_view()),
    path("all/", LocationView.as_view()),
    path("search/<int:id>/", GetLocationByIdView.as_view()),
    path("search/", GetLocationByColumnView.as_view()),
    path("options/", GetLocationOptionsView.as_view()),
]
