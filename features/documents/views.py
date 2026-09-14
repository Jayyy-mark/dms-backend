from django.utils import timezone

from django.shortcuts import render
from rest_framework.views import APIView, Request, Response
from django.db.models import Q
from features.documents.serializers import (
    DocumentSerializer,
    DocumentSearchSerializer,
    DocumentUpdateSerializer,
    DeepSearchDocumentSerializer,
)
from features.documents.models import Document
from features.shared.helpers.helper import generateId, toApiResponse, log_action
from features.documents.helpers import setDocumentFilters, deepSearch
from common.security.authorization.roles import Roles


def get_department_filter(request) -> Q:
    """
    Returns a Q filter that restricts documents to the requesting user's department.
    For admin / super admin roles: returns an empty Q() (no restriction).
    For all other roles: filters by staff__department_id.
    If the user has no linked staff, returns a filter that matches nothing (safe fallback).
    """
    if request.user.role in Roles.PRIVILEGED:
        return Q()

    staff = getattr(request.user, "staff", None)
    if staff is None or staff.department_id is None:
        # No department linked — return nothing to prevent data leakage
        return Q(pk__in=[])

    return Q(staff__department_id=staff.department_id)



# <!--==============================
#   DOCUMENTS VIEWS
# ================================-->
class DocumentView(APIView):

    def toModel(self, data):
        return {
            "document_id": data["document_id"],
            "document_name": data["document_name"],
            "document": data["document"],
            "staff_id": data["staff_id"],
            "dtype_id": data["dtype_id"],
            "category_id": data["category_id"],
            "description": data["description"],
        }

    def post(self, request: Request) -> Response:
        serializer = DocumentSerializer(data=request.data)
        serializer.initial_data["document_id"] = generateId(
            Document, "document_id", "DOC"
        )
        print("this is document data ", serializer.initial_data)
        serializer.is_valid(raise_exception=True)

        document = serializer.save()

        if document:
            log_action(
                user=request.user,
                action="CREATE",
                model_name="documents",
                object_id=document.id,
                description=f"Upload {document.document_name}",
            )

        return toApiResponse(
            data=DocumentSerializer(document).data,
            message=f"{document.document_name} has been created!",
        )

    def get(self, request: Request) -> Response:

        dept_filter = get_department_filter(request)
        documents = Document.objects.select_related(
            "staff", "category", "dtype"
        ).filter(dept_filter, is_archived=False, is_recycled=False)
        res = DocumentSerializer(documents, many=True)

        return Response({"documents": res.data})

    def put(self, request: Request, id: int) -> Response:

        document = Document.objects.get(id=id)
        print("this is data from upate document : ", request.data)
        serializer = DocumentUpdateSerializer(instance=document, data=request.data)
        serializer.is_valid(raise_exception=True)
        print("this is data from upate document : ", serializer.validated_data)
        document = serializer.save()

        if document:
            log_action(
                user=request.user,
                action="UPDATE",
                model_name="documents",
                object_id=document.id,
                description=f"Updated {document.document_name}",
            )

        return Response(
            {
                "document": DocumentSerializer(document).data,
                "message": f"{document.document_name} has been updated!",
            }
        )

    def patch(self, request: Request, id: int) -> Response:

        document = Document.objects.select_related("staff", "dtype", "category").get(
            id=id
        )
        document.is_archived = True
        document.archived_at = timezone.now()

        archived_document = document.save()

        log_action(
            user=request.user,
            action="ARCHIVE",
            model_name="documents",
            object_id=document.id,
            description=f"Archived {document.document_name}",
        )

        return Response(
            {
                "document": DocumentSerializer(archived_document).data,
                "message": f"{document.document_name} has been archived!",
            }
        )

    def delete(self, request: Request, id: int) -> Response:

        document = Document.objects.get(id=id)
        document.is_recycled = True
        document.recycled_at = timezone.now()
        recycled_document = document.save()

        print("this is document data ", recycled_document)

        log_action(
            user=request.user,
            action="DELETE",
            model_name="documents",
            object_id=document.id,
            description=f"Deleted {document.document_name}",
        )

        return Response({"message": f"{document.document_name} has been deleted!"})


class GetDocumentByIdView(APIView):

    def get(self, request: Request, id: int) -> Response:

        document = Document.objects.select_related("staff", "category", "dtype").get(
            id=id
        )

        return Response({"document": DocumentSerializer(document).data})


class GetDocumentByColumnView(APIView):

    def get(self, request: Request) -> Response:

        serializer = DocumentSearchSerializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)

        filters, category_qs = setDocumentFilters(serializer.validated_data)
        dept_filter = get_department_filter(request)

        documents = (
            Document.objects.select_related(
                "staff", "category", "dtype", "staff__department"
            )
            .filter(dept_filter)
            .filter(filters)
            .filter(is_archived=False, is_recycled=False)
        )
        print("this is document data : ", DocumentSerializer(documents, many=True).data)
        if category_qs:
            documents = documents.filter(category__in=category_qs)

        return Response({"documents": DocumentSerializer(documents, many=True).data})


# <!--==============================
#  ARCHIVED DOCUMENTS VIEWS
# ================================-->
class ArchivedDocumentView(APIView):

    def get(self, request: Request) -> Response:

        dept_filter = get_department_filter(request)
        archived_documents = Document.objects.select_related(
            "staff", "category", "dtype"
        ).filter(dept_filter, is_archived=True)

        return Response(
            {"documents": DocumentSerializer(archived_documents, many=True).data}
        )

    def patch(self, request: Request, id: int) -> Response:

        document = Document.objects.select_related("staff", "dtype", "category").get(
            id=id
        )
        document.is_archived = False
        document.archived_at = None
        document.restore_at = timezone.now()

        restored_document = document.save()

        log_action(
            user=request.user,
            action="RESTORE",
            model_name="archives",
            object_id=document.id,
            description=f"Restored {document.document_name}",
        )

        return Response(
            {
                "document": DocumentSerializer(restored_document).data,
                "message": f"{document.document_name} has been restore!",
            }
        )

    def delete(self, request: Request, id: int) -> Response:

        document = Document.objects.select_related("staff", "category", "dtype").get(
            id=id
        )

        document.is_archived = False
        document.archived_at = None

        document.is_recycled = True
        document.recycled_at = timezone.now()

        recycled_document = document.save()

        log_action(
            user=request.user,
            action="DELETE",
            model_name="archives",
            object_id=document.id,
            description=f"Deleted {document.document_name}",
        )

        return Response(
            {
                "document": recycled_document,
                "message": f"{document.document_name} has been deleted!",
            }
        )


class GetArchivedDocumentByColumnView(APIView):

    def get(self, request: Request) -> Response:

        serializer = DocumentSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        filters, category_qs = setDocumentFilters(serializer.validated_data)
        dept_filter = get_department_filter(request)

        print("this is filters ", filters)
        documents = (
            Document.objects.select_related(
                "staff", "category", "dtype", "staff__department"
            )
            .filter(dept_filter)
            .filter(filters)
            .filter(is_archived=True)
        )

        print("this is document data : ", documents)
        if category_qs:
            documents = documents.filter(category__in=category_qs)

        return Response({"documents": DocumentSerializer(documents, many=True).data})


# <!--==============================
#  RECYCLED DOCUMENTS VIEWS
# ================================-->
class RecycledDocumentView(APIView):

    def get(self, request: Request) -> Response:

        dept_filter = get_department_filter(request)
        recycled_documents = Document.objects.select_related(
            "staff", "category", "dtype"
        ).filter(dept_filter, is_recycled=True)

        return Response(
            {"documents": DocumentSerializer(recycled_documents, many=True).data}
        )

    def patch(self, request: Request, id: int) -> Response:

        document = Document.objects.select_related("staff", "dtype", "category").get(
            id=id
        )
        document.is_recycled = False
        document.recycled_at = None
        document.restore_at = timezone.now()

        restored_document = document.save()

        log_action(
            user=request.user,
            action="RESTORE",
            model_name="recycled documents",
            object_id=document.id,
            description=f"Restored {document.document_name}",
        )

        return Response(
            {
                "document": DocumentSerializer(restored_document).data,
                "message": f"{document.document_name} has been restored!",
            }
        )

    def delete(self, request: Request, id: int) -> Response:

        document = Document.objects.select_related("staff", "category", "dtype").get(
            id=id
        )

        num, _ = document.delete()

        if num < 0:
            return Response({"message": f"Failed to delete {document.document_name}"})

        log_action(
            user=request.user,
            action="DELETE",
            model_name="recycled documents",
            object_id=document.id,
            description=f"Deleted {document.document_name}",
        )

        return Response({"message": f"{document.document_name} has been deleted!"})


class GetRecycledDocumentByColumnView(APIView):

    def get(self, request: Request) -> Response:

        serializer = DocumentSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        filters, category_qs = setDocumentFilters(serializer.validated_data)
        dept_filter = get_department_filter(request)

        documents = (
            Document.objects.select_related(
                "staff", "category", "dtype", "staff__department"
            )
            .filter(dept_filter)
            .filter(filters)
            .filter(is_recycled=True)
        )

        if category_qs:
            documents = documents.filter(category__in=category_qs)

        return Response({"documents": DocumentSerializer(documents, many=True).data})


class GetExpiredDocumentView(APIView):

    def get(self, request: Request) -> Response:

        today = timezone.now().date()
        print("this is today ", today)

        dept_filter = get_department_filter(request)
        expired_documents = Document.objects.select_related(
            "staff", "category", "dtype"
        ).filter(dept_filter, expired_at=today)

        return Response(
            {"documents": DocumentSerializer(expired_documents, many=True).data}
        )


# <!--==============================
#  DEEP SEARCH DOCUMENTS VIEWS
# ================================-->
class DeepSearchDocumentView(APIView):

    def get(self, request: Request) -> Response:

        serializer = DeepSearchDocumentSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        filters, category_qs = setDocumentFilters(serializer.validated_data)
        dept_filter = get_department_filter(request)

        documents = Document.objects.select_related(
            "staff", "category", "dtype", "staff__department"
        ).filter(dept_filter).filter(filters)

        if category_qs:
            documents = documents.filter(category__in=category_qs)

        matched_documents = deepSearch(documents, serializer.validated_data.get("text"))

        return Response({"documents": matched_documents})
