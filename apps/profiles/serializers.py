from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, UserPhoto, Interest

User = get_user_model()

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'category', 'icon']

class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ['id', 'image', 'is_primary', 'order', 'moderation_status', 'uploaded_at']
        read_only_fields = ['moderation_status', 'uploaded_at']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    age = serializers.SerializerMethodField()
    is_premium = serializers.BooleanField(source='user.is_premium', read_only=True)
    is_verified = serializers.BooleanField(source='user.is_verified', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'username', 'email', 'bio', 'interests', 'personality_traits',
            'occupation', 'education', 'height', 'religion', 'ethnicity',
            'profile_picture', 'photos', 'age_min', 'age_max', 'distance_max',
            'is_active', 'is_complete', 'is_premium', 'is_verified', 'age',
            'profile_views', 'match_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'profile_views', 'match_rate', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        if obj.user.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - obj.user.date_of_birth.year - (
                (today.month, today.day) < (obj.user.date_of_birth.month, obj.user.date_of_birth.day)
            )
        return None

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = ['id', 'image', 'is_primary', 'order']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)