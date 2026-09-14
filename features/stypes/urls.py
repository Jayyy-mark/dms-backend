from django.urls import path
from features.stypes.views import StypeView, GetStypeByIdView

urlpatterns = [
    path("all/", StypeView.as_view()),
    path("create/", StypeView.as_view()),
    path("update/<int:id>/", StypeView.as_view()),
    path("delete/<int:id>/", StypeView.as_view()),
    path("search/<int:id>/", GetStypeByIdView.as_view()),
    path("search/", StypeView.as_view()),
]
