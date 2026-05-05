from rest_framework import serializers
from .models import Like, Match, Pass, SuggestionHistory
from apps.profiles.serializers import ProfileSerializer

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'from_user', 'to_user', 'created_at', 'is_mutual']
        read_only_fields = ['from_user', 'created_at', 'is_mutual']

class MatchSerializer(serializers.ModelSerializer):
    user1_profile = ProfileSerializer(source='user1.profile', read_only=True)
    user2_profile = ProfileSerializer(source='user2.profile', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'user1', 'user2', 'user1_profile', 'user2_profile', 'compatibility_score',
            'created_at', 'is_active', 'last_interaction', 'matched_by', 'ai_confidence',
            'last_message', 'unread_count'
        ]
    
    def get_last_message(self, obj):
        if hasattr(obj, 'conversation') and obj.conversation.messages.exists():
            from apps.chat.serializers import MessageSerializer
            return MessageSerializer(obj.conversation.messages.last()).data
        return None
    
    def get_unread_count(self, obj):
        if hasattr(obj, 'conversation') and self.context.get('request'):
            user = self.context['request'].user
            return obj.conversation.messages.filter(is_read=False).exclude(sender=user).count()
        return 0

class DiscoverySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    age = serializers.IntegerField()
    match_score = serializers.FloatField()
    distance = serializers.FloatField()
    bio = serializers.CharField()
    interests = serializers.ListField()
    profile_picture = serializers.CharField()
    photos = serializers.ListField()
    is_verified = serializers.BooleanField()
    is_premium = serializers.BooleanField()
    is_online = serializers.BooleanField()

class PassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = ['id', 'from_user', 'to_user', 'reason', 'created_at']
        read_only_fields = ['from_user', 'created_at']