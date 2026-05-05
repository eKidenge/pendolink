from rest_framework import serializers
from .models import CompatibilityScore, UserEmbedding, AIFeedback, AIRecommendationLog

class CompatibilityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompatibilityScore
        fields = [
            'id', 'user1', 'user2', 'interest_score', 'personality_score',
            'behavior_score', 'location_score', 'total_score', 'model_version',
            'confidence', 'last_calculated'
        ]
        read_only_fields = ['last_calculated']

class UserEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmbedding
        fields = ['id', 'user', 'embedding_vector', 'dimension', 'model_version', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class AIFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFeedback
        fields = ['id', 'match', 'user', 'rating', 'was_successful', 'chat_messages_count', 'feedback_text', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AIRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendationLog
        fields = ['id', 'user', 'recommended_users', 'scores', 'context', 'was_clicked', 'clicked_user', 'created_at']
        read_only_fields = ['user', 'created_at']