from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.core.cache import cache
from .services import CompatibilityScorer, RecommendationEngine
from .serializers import AIFeedbackSerializer

class AIRecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        limit = request.GET.get('limit', 20)
        recommender = RecommendationEngine(request.user)
        recommendations = recommender.get_recommendations(int(limit))
        return Response(recommendations)
    
    def post(self, request):
        serializer = AIFeedbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            scorer = CompatibilityScorer()
            scorer.update_model_with_feedback(request.user, serializer.validated_data)
            return Response({'status': 'feedback received'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompatibilityCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        other_user_id = request.data.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id required'}, status=400)
        
        scorer = CompatibilityScorer()
        score = scorer.calculate_compatibility(request.user.id, other_user_id)
        cache_key = f"compat_{request.user.id}_{other_user_id}"
        cache.set(cache_key, score, 86400)
        return Response(score)