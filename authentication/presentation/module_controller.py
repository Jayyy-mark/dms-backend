from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from authentication.application.module_service import ModuleService


class ModuleController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ModuleService()

    def get(self, request: Request):
        modules = self.service.get_all_modules_with_features()
        return Response({"modules": modules}, status=status.HTTP_200_OK)


class FeatureToggleController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ModuleService()

    def put(self, request: Request, id: int):
        new_status = request.data.get("status")
        if new_status is None:
            return Response(
                {"message": "status field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            feature = self.service.toggle_feature_status(id, new_status)
            return Response(
                {
                    "message": "Feature status updated",
                    "feature": feature,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeatureBulkController(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ModuleService()

    def put(self, request: Request):
        action = request.data.get("action")
        if action == "enable_all":
            self.service.bulk_update_features(True)
        elif action == "disable_all":
            self.service.bulk_update_features(False)
        elif action == "reset":
            self.service.reset_features()
        else:
            return Response(
                {"message": "Invalid action. Use 'enable_all', 'disable_all', or 'reset'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": f"Action '{action}' completed successfully"},
            status=status.HTTP_200_OK,
        )
