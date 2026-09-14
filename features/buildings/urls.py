from django.urls import path
from features.buildings.views import BuildingView, GetBuildingByIdView

urlpatterns = [
    path("create/", BuildingView.as_view()),
    path("update/<int:id>/", BuildingView.as_view()),
    path("delete/<int:id>/", BuildingView.as_view()),
    path("all/", BuildingView.as_view()),
    path("search/<int:id>/", GetBuildingByIdView.as_view()),

]