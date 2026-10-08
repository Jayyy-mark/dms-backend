from django.urls import path

from features.logs.views import LogView, ExportLogPdfView

urlpatterns = [
    path("all/", LogView.as_view()),
    path("export-pdf/", ExportLogPdfView.as_view()),
]