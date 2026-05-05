from rest_framework import serializers
from .models import ReportedContent, UserFlag, ModerationAction
from apps.users.serializers import UserSerializer

class ReportedContentSerializer(serializers.ModelSerializer):
    reported_by_details = UserSerializer(source='reported_by', read_only=True)
    reported_user_details = UserSerializer(source='reported_user', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    resolved_by_details = UserSerializer(source='resolved_by', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportedContent
        fields = [
            'id', 'content_type', 'content_id', 'reported_by', 'reported_by_details',
            'reported_user', 'reported_user_details', 'reason', 'reason_display',
            'description', 'status', 'status_display', 'assigned_to', 'assigned_to_details',
            'resolution_notes', 'resolved_by', 'resolved_by_details', 'resolved_at',
            'time_ago', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reported_by', 'created_at', 'updated_at']
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at)

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedContent
        fields = ['content_type', 'content_id', 'reported_user', 'reason', 'description']
    
    def validate_reported_user(self, value):
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError("You cannot report yourself")
        return value

class UserFlagSerializer(serializers.ModelSerializer):
    flagged_by_details = UserSerializer(source='flagged_by', read_only=True)
    flag_type_display = serializers.CharField(source='get_flag_type_display', read_only=True)
    
    class Meta:
        model = UserFlag
        fields = [
            'id', 'user', 'flag_type', 'flag_type_display', 'reason', 'flagged_by',
            'flagged_by_details', 'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = ['flagged_by', 'created_at']

class ModerationActionSerializer(serializers.ModelSerializer):
    performed_by_details = UserSerializer(source='performed_by', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = ModerationAction
        fields = [
            'id', 'user', 'action_type', 'action_type_display', 'reason', 'duration_days',
            'performed_by', 'performed_by_details', 'notes', 'created_at'
        ]
        read_only_fields = ['performed_by', 'created_at']