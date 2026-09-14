from django.urls import path

from features.logs.views import LogView

urlpatterns = [
    path("all/", LogView.as_view()),
]