from django.urls import path
from features.rooms.views import RoomView, GetRoomByIdView

urlpatterns = [
    path("all/", RoomView.as_view()),
    path("create/", RoomView.as_view()),
    path("update/<int:id>/", RoomView.as_view()),
    path("delete/<int:id>/", RoomView.as_view()),
    path("search/<int:id>/", GetRoomByIdView.as_view()),
    path("search/", RoomView.as_view()),
]
