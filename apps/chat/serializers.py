from rest_framework import serializers
from .models import Conversation, Message, MessageAttachment
from apps.matching.serializers import MatchSerializer

class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageAttachment
        fields = ['id', 'file', 'file_type', 'file_name', 'file_size', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_profile_picture = serializers.SerializerMethodField()
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_username', 'sender_profile_picture',
            'content', 'is_read', 'read_at', 'created_at', 'attachments'
        ]
        read_only_fields = ['sender', 'is_read', 'read_at', 'created_at']
    
    def get_sender_profile_picture(self, obj):
        if hasattr(obj.sender, 'profile') and obj.sender.profile.profile_picture:
            return obj.sender.profile.profile_picture.url
        return None

class ConversationSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    match_info = MatchSerializer(source='match', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'match', 'match_info', 'other_user', 'is_active', 'last_message',
            'last_message_time', 'unread_count', 'created_at', 'updated_at'
        ]
    
    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other_user = obj.match.user2 if obj.match.user1 == request.user else obj.match.user1
            from apps.users.serializers import UserSerializer
            return UserSerializer(other_user).data
        return None
    
    def get_last_message(self, obj):
        if obj.messages.exists():
            return obj.messages.last().content
        return None
    
    def get_last_message_time(self, obj):
        if obj.messages.exists():
            return obj.messages.last().created_at
        return obj.updated_at
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']
    
    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Message too long (max 1000 characters)")
        return value.strip()