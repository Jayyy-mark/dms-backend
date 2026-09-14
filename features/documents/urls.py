from django.urls import path

from features.documents.views import (
    GetExpiredDocumentView,
    DocumentView,
    GetRecycledDocumentByColumnView,
    GetDocumentByColumnView,
    GetArchivedDocumentByColumnView,
    GetDocumentByIdView,
    ArchivedDocumentView,
    RecycledDocumentView,
    DeepSearchDocumentView,
)

urlpatterns = [
    path("create/", DocumentView.as_view()),
    path("update/<int:id>/", DocumentView.as_view()),
    path("delete/<int:id>/", DocumentView.as_view()),
    path("archive/<int:id>/", DocumentView.as_view()),
    path("all/", DocumentView.as_view()),
    path("search/<int:id>/", GetDocumentByIdView.as_view()),
    path("search/", GetDocumentByColumnView.as_view()),
    path("deepsearch/", DeepSearchDocumentView.as_view()),
    path("archive/all/", ArchivedDocumentView.as_view()),
    path("archive/delete/<int:id>/", ArchivedDocumentView.as_view()),
    path("archive/restore/<int:id>/", ArchivedDocumentView.as_view()),
    path("archive/search/", GetArchivedDocumentByColumnView.as_view()),
    path("recycle/all/", RecycledDocumentView.as_view()),
    path("recycle/delete/<int:id>/", RecycledDocumentView.as_view()),
    path("recycle/restore/<int:id>/", RecycledDocumentView.as_view()),
    path("recycle/search/", GetRecycledDocumentByColumnView.as_view()),
    path("expire/all/", GetExpiredDocumentView.as_view()),
]
