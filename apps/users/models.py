from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='P')
    looking_for = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    last_active = models.DateTimeField(auto_now=True)
    likes_remaining_today = models.IntegerField(default=10)
    last_like_reset = models.DateTimeField(default=timezone.now)
    
    id_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # DO NOT add groups or user_permissions fields here - they come from AbstractUser
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return self.username
    
    def has_premium(self):
        if self.is_premium and self.premium_until:
            return self.premium_until > timezone.now()
        return self.is_premium
    
    def reset_daily_likes(self):
        today = timezone.now().date()
        if self.last_like_reset.date() < today:
            self.likes_remaining_today = 10 if not self.has_premium() else 100
            self.last_like_reset = timezone.now()
            self.save()