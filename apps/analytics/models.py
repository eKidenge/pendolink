from django.db import models
from django.conf import settings

class UserActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=100)  # login, like, match, message, etc.
    metadata = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activity_logs'
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['created_at']),
        ]

class DailyMetric(models.Model):
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    premium_users = models.IntegerField(default=0)
    
    # Engagement metrics
    total_likes = models.IntegerField(default=0)
    total_matches = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    
    # Match metrics
    match_rate = models.FloatField(default=0.0)
    avg_compatibility_score = models.FloatField(default=0.0)
    
    # Revenue metrics
    total_revenue_kes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_subscriptions = models.IntegerField(default=0)
    
    # AI performance
    ai_recommendation_ctr = models.FloatField(default=0.0)  # Click-through rate
    avg_match_quality = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_metrics'
        indexes = [
            models.Index(fields=['date']),
        ]

class LocationMetric(models.Model):
    town = models.CharField(max_length=100)
    date = models.DateField()
    
    user_count = models.IntegerField(default=0)
    active_user_count = models.IntegerField(default=0)
    match_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'location_metrics'
        unique_together = ['town', 'date']

class AIPerformanceMetric(models.Model):
    date = models.DateField()
    model_version = models.CharField(max_length=50)
    
    # Performance metrics
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    
    # Engagement metrics
    avg_recommendations_per_user = models.FloatField(default=0.0)
    click_through_rate = models.FloatField(default=0.0)
    match_conversion_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_performance_metrics'
        unique_together = ['date', 'model_version']