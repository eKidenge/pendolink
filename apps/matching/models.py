from django.db import models
from django.conf import settings

class Like(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes_given')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes_received')
    created_at = models.DateTimeField(auto_now_add=True)
    is_mutual = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'likes'
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"

class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user2')
    compatibility_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    last_interaction = models.DateTimeField(auto_now=True)
    
    # Additional metadata
    matched_by = models.CharField(max_length=20, default='mutual_like')  # mutual_like, ai_predicted
    ai_confidence = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'matches'
        unique_together = ['user1', 'user2']
    
    def __str__(self):
        return f"Match: {self.user1.username} & {self.user2.username}"

class Pass(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passes_given')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='passes_received')
    reason = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'passes'
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        return f"{self.from_user.username} passed on {self.to_user.username}"

class SuggestionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    suggested_users = models.JSONField()  # List of user IDs
    scores = models.JSONField()  # List of scores
    created_at = models.DateTimeField(auto_now_add=True)
    was_displayed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'suggestion_history'
        ordering = ['-created_at']