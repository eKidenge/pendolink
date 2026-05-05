from django.db import models
from django.conf import settings

class ReportedContent(models.Model):
    CONTENT_TYPES = [
        ('profile', 'Profile'),
        ('photo', 'Photo'),
        ('message', 'Message'),
        ('user', 'User'),
    ]
    
    REPORT_REASONS = [
        ('fake_profile', 'Fake Profile'),
        ('inappropriate_photo', 'Inappropriate Photo'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('underage', 'Underage User'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_reports')
    
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reported_content'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['reported_user']),
        ]

class UserFlag(models.Model):
    FLAG_TYPES = [
        ('suspicious', 'Suspicious Activity'),
        ('fake', 'Likely Fake'),
        ('spam', 'Spam Account'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flags')
    flag_type = models.CharField(max_length=20, choices=FLAG_TYPES)
    reason = models.TextField()
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flags_made')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_flags'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

class ModerationAction(models.Model):
    ACTION_TYPES = [
        ('warning', 'Warning Issued'),
        ('photo_removed', 'Photo Removed'),
        ('profile_hidden', 'Profile Hidden'),
        ('temp_ban', 'Temporary Ban'),
        ('perm_ban', 'Permanent Ban'),
        ('restored', 'Account Restored'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    reason = models.TextField()
    duration_days = models.IntegerField(null=True, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='moderation_actions')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'moderation_actions'
        ordering = ['-created_at']