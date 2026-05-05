from django.urls import path
from .views import (
    DashboardOverviewView, UserGrowthView, RevenueAnalyticsView,
    LocationHeatmapView, AIPerformanceView, RealTimeAnalyticsView
)

urlpatterns = [
    path('overview/', DashboardOverviewView.as_view(), name='overview'),
    path('user-growth/', UserGrowthView.as_view(), name='user-growth'),
    path('revenue/', RevenueAnalyticsView.as_view(), name='revenue'),
    path('location-heatmap/', LocationHeatmapView.as_view(), name='location-heatmap'),
    path('ai-performance/', AIPerformanceView.as_view(), name='ai-performance'),
    path('realtime/', RealTimeAnalyticsView.as_view(), name='realtime'),
]