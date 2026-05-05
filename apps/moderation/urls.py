from django.urls import path
from .views import (
    ReportListView, ReportDetailView, ModerationQueueView, ModerationStatsView
)

urlpatterns = [
    path('reports/', ReportListView.as_view(), name='reports'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('queue/', ModerationQueueView.as_view(), name='moderation-queue'),
    path('stats/', ModerationStatsView.as_view(), name='moderation-stats'),
]