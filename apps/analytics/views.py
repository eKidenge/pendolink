from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import DailyMetric, LocationMetric, UserActivityLog
from .serializers import LocationMetricSerializer
from apps.permissions.permissions import IsAdminUser

class DashboardOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        metrics = DailyMetric.objects.filter(date__gte=start_date, date__lte=end_date)
        
        data = {
            'total_users': metrics.aggregate(Sum('total_users'))['total_users__sum'] or 0,
            'active_users_7d': metrics.filter(date__gte=end_date - timedelta(days=7)).aggregate(
                avg_active=Avg('active_users')
            )['avg_active'] or 0,
            'total_matches_30d': metrics.aggregate(Sum('total_matches'))['total_matches__sum'] or 0,
            'total_revenue_30d': float(metrics.aggregate(Sum('total_revenue_kes'))['total_revenue_kes__sum'] or 0),
            'avg_match_rate': metrics.aggregate(Avg('match_rate'))['match_rate__avg'] or 0,
        }
        return Response(data)

class UserGrowthView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = DailyMetric.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
        
        data = {
            'dates': [m.date.strftime('%Y-%m-%d') for m in metrics],
            'total_users': [m.total_users for m in metrics],
            'new_users': [m.new_users for m in metrics],
            'active_users': [m.active_users for m in metrics],
        }
        return Response(data)

class RevenueAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        days = int(request.GET.get('days', 90))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = DailyMetric.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
        
        data = {
            'dates': [m.date.strftime('%Y-%m-%d') for m in metrics],
            'daily_revenue': [float(m.total_revenue_kes) for m in metrics],
            'new_subscriptions': [m.new_subscriptions for m in metrics],
        }
        return Response(data)

class LocationHeatmapView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        date = request.GET.get('date', timezone.now().date())
        metrics = LocationMetric.objects.filter(date=date).order_by('-user_count')[:20]
        serializer = LocationMetricSerializer(metrics, many=True)
        return Response(serializer.data)

class AIPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        metrics = DailyMetric.objects.filter(date__gte=start_date, date__lte=end_date)
        
        data = {
            'avg_ai_ctr': metrics.aggregate(Avg('ai_recommendation_ctr'))['ai_recommendation_ctr__avg'] or 0,
            'avg_match_quality': metrics.aggregate(Avg('avg_match_quality'))['avg_match_quality__avg'] or 0,
        }
        return Response(data)

class RealTimeAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        today = timezone.now().date()
        
        activity_stats = UserActivityLog.objects.filter(
            created_at__date=today
        ).values('action').annotate(count=models.Count('id'))
        
        return Response({
            'activity_breakdown': list(activity_stats),
            'timestamp': timezone.now().isoformat(),
        })