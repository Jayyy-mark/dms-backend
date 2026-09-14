from django.urls import path
from .views import (
    DashboardView,
    DashboardAnalyticsView,
    DashboardTrafficView,
    DashboardStaffPerformanceView,
    DashboardCategorySummaryView,
)

urlpatterns = [
    path("summary/", DashboardView.as_view()),
    path("analytics/", DashboardAnalyticsView.as_view()),
    path("traffic/", DashboardTrafficView.as_view()),
    path("staff-performance/", DashboardStaffPerformanceView.as_view()),
    path("category-summary/", DashboardCategorySummaryView.as_view()),
]