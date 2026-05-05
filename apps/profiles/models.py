from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    interests = models.JSONField(default=list)  # List of interests
    personality_traits = models.JSONField(default=dict)  # e.g., {"extrovert": 0.8, "openness": 0.7}
    
    # Profile details
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=200, blank=True)
    height = models.IntegerField(null=True, blank=True)  # in cm
    religion = models.CharField(max_length=50, blank=True)
    ethnicity = models.CharField(max_length=50, blank=True)
    
    # Media
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    photos = models.JSONField(default=list)  # List of photo URLs
    
    # Preferences
    age_min = models.IntegerField(default=18, validators=[MinValueValidator(18), MaxValueValidator(100)])
    age_max = models.IntegerField(default=60, validators=[MinValueValidator(18), MaxValueValidator(100)])
    distance_max = models.IntegerField(default=50)  # in km
    
    # Status
    is_active = models.BooleanField(default=True)
    is_complete = models.BooleanField(default=False)
    
    # Stats
    profile_views = models.IntegerField(default=0)
    match_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def calculate_completion(self):
        fields_completed = sum([
            1 if self.bio else 0,
            1 if self.interests else 0,
            1 if self.profile_picture else 0,
            1 if self.occupation else 0,
            1 if self.age_min and self.age_max else 0,
        ])
        self.is_complete = fields_completed >= 3
        self.save()
        return fields_completed

class UserPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='user_photos/')
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    moderation_status = models.CharField(max_length=20, default='pending')  # pending, approved, rejected
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_photos'
        ordering = ['order']

class Interest(models.Model):
    CATEGORY_CHOICES = [
        ('sports', 'Sports'),
        ('music', 'Music'),
        ('arts', 'Arts'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel'),
        ('tech', 'Technology'),
        ('books', 'Books'),
        ('movies', 'Movies'),
        ('fitness', 'Fitness'),
        ('social', 'Social Causes'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'interests'
    
    def __str__(self):
        return self.name