from django.db import models
from django.conf import settings

class CompatibilityScore(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compat_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compat_as_user2')
    
    # Component scores
    interest_score = models.FloatField(default=0.0)
    personality_score = models.FloatField(default=0.0)
    behavior_score = models.FloatField(default=0.0)
    location_score = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    
    # Model metadata
    model_version = models.CharField(max_length=50, default='v1.0')
    confidence = models.FloatField(default=0.0)
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'compatibility_scores'
        unique_together = ['user1', 'user2']
        indexes = [
            models.Index(fields=['user1', 'total_score']),
            models.Index(fields=['user2', 'total_score']),
        ]

class UserEmbedding(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    embedding_vector = models.JSONField()  # Store embedding as list
    dimension = models.IntegerField(default=128)
    model_version = models.CharField(max_length=50, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_embeddings'

class AIFeedback(models.Model):
    match = models.ForeignKey('matching.Match', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)  # 1-5 stars
    was_successful = models.BooleanField(default=False)
    chat_messages_count = models.IntegerField(default=0)
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_feedback'
        unique_together = ['match', 'user']

class AIRecommendationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommended_users = models.JSONField()
    scores = models.JSONField()
    context = models.JSONField(default=dict)  # location, time, etc.
    was_clicked = models.BooleanField(default=False)
    clicked_user = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_recommendation_logs'
        ordering = ['-created_at']