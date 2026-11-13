from django.urls import path

from features.locations.views import (
    LocationView,
    LocationListView,
    GetLocationByColumnView,
    GetLocationByIdView,
    GetLocationOptionsView,
    ExportLocationPdfView,
    RecycledLocationView,
    RecycledLocationListView,
    LocationAuditActionView,
)

urlpatterns = [
    path("create/", LocationView.as_view()),
    path("update/<int:id>/", LocationView.as_view()),
    path("delete/<int:id>/", LocationView.as_view()),
    path("archive/<int:id>/", LocationView.as_view()),
    path("all/", LocationView.as_view()),
    path("list/", LocationListView.as_view()),
    path("search/<int:id>/", GetLocationByIdView.as_view()),
    path("search/", GetLocationByColumnView.as_view()),
    path("options/", GetLocationOptionsView.as_view()),
    path("export-pdf/", ExportLocationPdfView.as_view()),
    path("recycle/all/", RecycledLocationView.as_view()),
    path("recycle/list/", RecycledLocationListView.as_view()),
    path("recycle/restore/<int:id>/", RecycledLocationView.as_view()),
    path("recycle/delete/<int:id>/", RecycledLocationView.as_view()),
    path("view/<int:id>/", LocationAuditActionView.as_view(), {"action": "VIEW"}),
    path("download/<int:id>/", LocationAuditActionView.as_view(), {"action": "DOWNLOAD"}),
]
