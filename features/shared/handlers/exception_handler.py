from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from features.staffs.domain.exceptions import RepositoryException

def custom_exception_handler(exc, context):
    
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "success" : False,
            "message" : "Request Failed!",
            "errors" : response.data,
        }, status=response.status_code)
    
    if isinstance(exc, RepositoryException):
        return Response({
            "success" : False,
            "message" : str(exc),
            "error" :None,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        "success" : False,
        "message" : "Internal Server Error",
        "errors" : None,
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)