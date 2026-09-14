from django.urls import path
from features.ranks.views import RankView, GetRankByIdView

urlpatterns = [
    path("all/", RankView.as_view()),
    path("create/", RankView.as_view()),
    path("update/<int:id>/", RankView.as_view()),
    path("delete/<int:id>/", RankView.as_view()),
    path("search/<int:id>/", GetRankByIdView.as_view()),
    path("search/", RankView.as_view()),
]
