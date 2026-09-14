from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code

        if status_code == status.HTTP_401_UNAUTHORIZED:
            return Response(
                {"error": "You are not authenticated. Please log in to continue."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if status_code == status.HTTP_403_FORBIDDEN:
            return Response(
                {"error": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if status_code == status.HTTP_404_NOT_FOUND:
            return Response(
                {"error": "The requested resource was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            return Response(
                {"error": "This action is not allowed on this endpoint."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return Response(
                {"error": "Too many requests. Please slow down and try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if status_code >= 500:
            return Response(
                {"error": "A server error occurred. Please try again later."},
                status=status_code,
            )

        return response

    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            {"error": "The requested record does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            return Response(
                exc.message_dict,
                status=status.HTTP_400_BAD_REQUEST,
            )
        messages = exc.messages if hasattr(exc, "messages") else [str(exc)]
        return Response(
            {"non_field_errors": messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, IntegrityError):
        msg = str(exc)
        if "Duplicate entry" in msg or "unique constraint" in msg.lower():
            return Response(
                {"error": "A record with this value already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            {"error": "A database integrity error occurred."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"error": "An unexpected error occurred. Please try again."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
