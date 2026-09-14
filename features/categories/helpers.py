from rest_framework.response import Response
from rest_framework import status

def toApiResponse(data)->Response:
    return Response(data=data,status=status.HTTP_201_CREATED)