from rest_framework.views import APIView, Request, Response
from features.logs.models import AuditLog
from features.logs.serializers import LogSerializer


class LogView(APIView):

    def get(self, request:Request)->Response:

        logs = AuditLog.objects.select_related("user").all().order_by("-created_at")

        return Response({
            "logs" : LogSerializer(logs, many=True).data
        })
