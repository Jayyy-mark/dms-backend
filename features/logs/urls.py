from django.urls import path

from features.logs.views import LogView, LogListView, LogStatsView, ExportLogPdfView

urlpatterns = [
    path("all/", LogView.as_view()),
    path("list/", LogListView.as_view()),
    path("stats/", LogStatsView.as_view()),
    path("export-pdf/", ExportLogPdfView.as_view()),
]