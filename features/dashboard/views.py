from rest_framework.views import APIView, Response, Request
from .helpers import (
    getDepartmentCount,
    getDocumentCount,
    getStaffCount,
    getUserCount,
    getCategoryCount,
    getBuildingCount,
    getPermanentDocumentCount,
    getTemporaryDocumentCount,
    getRecentUploadsCount,
    getExpiredArchivesCount,
    getDocumentTrafficSummary,
    getStaffPerformanceSummary,
    getCategoryDocumentSummary,
)
from common.security.authorization.roles import Roles


class DashboardView(APIView):

    def get(self, request: Request) -> Response:
        # Determine department scope for non-admin users
        department_id = None
        if request.user.role not in Roles.PRIVILEGED:
            staff = getattr(request.user, "staff", None)
            if staff is not None:
                department_id = staff.department_id

        return Response({
            "summary": {
                "count": {
                    "staffs": getStaffCount(department_id=department_id),
                    "documents": getDocumentCount(department_id=department_id),
                    "departments": getDepartmentCount(),
                }
            }
        })


class DashboardAnalyticsView(APIView):
    """Return all KPI analytics data for the dashboard overview cards."""

    def get(self, request: Request) -> Response:
        department_id = None
        if request.user.role not in Roles.PRIVILEGED:
            staff = getattr(request.user, "staff", None)
            if staff is not None:
                department_id = staff.department_id

        return Response({
            "analytics": {
                "users": getUserCount(),
                "staffs": getStaffCount(department_id=department_id),
                "documents": getDocumentCount(department_id=department_id),
                "departments": getDepartmentCount(),
                "categories": getCategoryCount(),
                "buildings": getBuildingCount(),
                "permanent_documents": getPermanentDocumentCount(department_id=department_id),
                "temporary_documents": getTemporaryDocumentCount(department_id=department_id),
                "recent_uploads": getRecentUploadsCount(department_id=department_id),
                "expired_archives": getExpiredArchivesCount(department_id=department_id),
            }
        })


class DashboardTrafficView(APIView):
    """Return departmental traffic and file type breakdown across periods."""

    def get(self, request: Request) -> Response:
        department_id = None
        if request.user.role not in Roles.PRIVILEGED:
            staff = getattr(request.user, "staff", None)
            if staff is not None:
                department_id = staff.department_id

        traffic_data = getDocumentTrafficSummary(department_id=department_id)
        return Response({"traffic": traffic_data})


class DashboardStaffPerformanceView(APIView):
    """Return staff counts and top uploaders per period."""

    def get(self, request: Request) -> Response:
        department_id = None
        if request.user.role not in Roles.PRIVILEGED:
            staff = getattr(request.user, "staff", None)
            if staff is not None:
                department_id = staff.department_id

        performance_data = getStaffPerformanceSummary(department_id=department_id)
        return Response({"performance": performance_data})


class DashboardCategorySummaryView(APIView):
    """Return hierarchical category tree and aggregated document counts per period."""

    def get(self, request: Request) -> Response:
        department_id = None
        if request.user.role not in Roles.PRIVILEGED:
            staff = getattr(request.user, "staff", None)
            if staff is not None:
                department_id = staff.department_id

        department_name = request.query_params.get("department_name")

        summary_data = getCategoryDocumentSummary(
            department_id=department_id,
            department_name=department_name,
        )
        return Response({"category_summary": summary_data})