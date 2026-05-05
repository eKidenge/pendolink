from rest_framework import serializers
from .models import DailyMetric, LocationMetric, UserActivityLog, AIPerformanceMetric

class DailyMetricSerializer(serializers.ModelSerializer):
    formatted_date = serializers.SerializerMethodField()
    formatted_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyMetric
        fields = [
            'id', 'date', 'formatted_date', 'total_users', 'new_users', 'active_users',
            'premium_users', 'total_likes', 'total_matches', 'total_messages',
            'match_rate', 'avg_compatibility_score', 'total_revenue_kes', 'total_revenue_usd',
            'new_subscriptions', 'ai_recommendation_ctr', 'avg_match_quality',
            'formatted_revenue', 'created_at', 'updated_at'
        ]
    
    def get_formatted_date(self, obj):
        return obj.date.strftime("%B %d, %Y")
    
    def get_formatted_revenue(self, obj):
        return f"KES {obj.total_revenue_kes:,.2f}"

class LocationMetricSerializer(serializers.ModelSerializer):
    engagement_score = serializers.SerializerMethodField()
    
    class Meta:
        model = LocationMetric
        fields = ['id', 'town', 'date', 'user_count', 'active_user_count', 'match_count', 'engagement_score']
    
    def get_engagement_score(self, obj):
        if obj.user_count > 0:
            return round((obj.active_user_count / obj.user_count) * 100, 1)
        return 0

class UserActivityLogSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivityLog
        fields = ['id', 'user', 'action', 'metadata', 'ip_address', 'user_agent', 'created_at', 'time_ago']
        read_only_fields = ['created_at']
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at)

class AIPerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPerformanceMetric
        fields = [
            'id', 'date', 'model_version', 'precision', 'recall', 'f1_score',
            'avg_recommendations_per_user', 'click_through_rate', 'match_conversion_rate', 'created_at'
        ]