from django.urls import path
from features.dtypes.views import DtypeView, GetDtypeByIdView

urlpatterns = [
    path("create/", DtypeView.as_view()),
    path("update/<int:id>/", DtypeView.as_view()),
    path("delete/<int:id>/", DtypeView.as_view()),
    path("all/", DtypeView.as_view()),
    path("search/<int:id>/", GetDtypeByIdView.as_view()),

]