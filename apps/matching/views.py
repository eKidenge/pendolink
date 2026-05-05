from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Like, Match, Pass
from .serializers import LikeSerializer, MatchSerializer, DiscoverySerializer
from .services import DiscoveryService, MatchingService
from apps.ai_engine.services import CompatibilityScorer
from apps.chat.models import Conversation

User = get_user_model()

# ==================== TEMPLATE VIEWS ====================

@login_required
def dashboard_page(request):
    """Main dashboard with stats and recommendations"""
    user = request.user
    
    # Get real stats from database
    matches_count = Match.objects.filter(
        Q(user1=user) | Q(user2=user),
        is_active=True
    ).count()
    
    likes_received = Like.objects.filter(to_user=user).count()
    profile_views = 0  # Can add profile view tracking later
    
    # Calculate compatibility score (average of existing matches)
    compatibility_score = 0
    matches = Match.objects.filter(Q(user1=user) | Q(user2=user), is_active=True)
    if matches.exists():
        total = sum(m.compatibility_score for m in matches)
        compatibility_score = int(total / matches.count())
    else:
        compatibility_score = 85  # Default
    
    # Get recent matches with details
    recent_matches = Match.objects.filter(
        Q(user1=user) | Q(user2=user),
        is_active=True
    ).order_by('-created_at')[:5]
    
    matches_data = []
    for match in recent_matches:
        other_user = match.user2 if match.user1 == user else match.user1
        conversation = Conversation.objects.filter(match=match).first()
        
        # Calculate age
        age = None
        if other_user.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - other_user.date_of_birth.year
        
        matches_data.append({
            'id': other_user.id,
            'username': other_user.username,
            'profile_picture': None,
            'age': age,
            'distance': '5',
            'compatibility': int(match.compatibility_score),
            'conversation_id': conversation.id if conversation else None
        })
    
    # Get AI recommendations for dashboard
    discovery_service = DiscoveryService(user)
    recommendations_raw = discovery_service.get_potential_matches(limit=4)
    
    recommendations = []
    for rec in recommendations_raw:
        recommendations.append({
            'id': rec['id'],
            'username': rec['username'],
            'age': rec['age'],
            'match_score': rec['match_score'],
            'distance': rec['distance'],
            'bio': rec.get('bio', ''),
            'profile_picture': rec.get('profile_picture'),
            'is_online': rec.get('is_online', False),
            'top_interests': rec.get('interests', [])[:3]
        })
    
    return render(request, 'dashboard/index.html', {
        'user': user,
        'matches_count': matches_count,
        'likes_received': likes_received,
        'profile_views': profile_views,
        'compatibility_score': compatibility_score,
        'recommendations': recommendations,
        'recent_matches': matches_data,
        'activities': []
    })

@login_required
def discover_page(request):
    """Discovery page for swiping on profiles"""
    user = request.user
    discovery_service = DiscoveryService(user)
    profiles_data = discovery_service.get_potential_matches(limit=20)
    
    return render(request, 'dashboard/discover.html', {
        'user': user,
        'profiles': profiles_data
    })

@login_required
def matches_page(request):
    """Matches page showing all mutual matches"""
    user = request.user
    
    # Get all active matches
    active_matches = Match.objects.filter(
        Q(user1=user) | Q(user2=user),
        is_active=True
    ).order_by('-created_at')
    
    active_matches_data = []
    for match in active_matches:
        other_user = match.user2 if match.user1 == user else match.user1
        conversation = Conversation.objects.filter(match=match).first()
        
        # Calculate age
        age = None
        if other_user.date_of_birth:
            from datetime import date
            today = date.today()
            age = today.year - other_user.date_of_birth.year
        
        # Get common interests
        common_interests = []
        if hasattr(user, 'profile') and hasattr(other_user, 'profile'):
            user_interests = set(user.profile.interests)
            other_interests = set(other_user.profile.interests)
            common_interests = list(user_interests.intersection(other_interests))[:4]
        
        active_matches_data.append({
            'id': other_user.id,
            'username': other_user.username,
            'age': age,
            'distance': '5',  # Calculate actual distance
            'compatibility': int(match.compatibility_score),
            'profile_picture': None,
            'matched_at': match.created_at,
            'conversation_id': conversation.id if conversation else None,
            'common_interests': common_interests
        })
    
    # Get total likes stats
    total_likes_given = Like.objects.filter(from_user=user).count()
    total_likes_received = Like.objects.filter(to_user=user).count()
    
    # Calculate match rate
    match_rate = 0
    if total_likes_given > 0:
        match_rate = int((matches_count / total_likes_given) * 100)
    
    return render(request, 'dashboard/matches.html', {
        'user': user,
        'active_matches': active_matches_data,
        'expired_matches': [],
        'total_likes_given': total_likes_given,
        'total_likes_received': total_likes_received,
        'match_rate': match_rate,
        'avg_response_time': '2h'
    })

# ==================== API VIEWS ====================

class DiscoveryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DiscoverySerializer
    
    def get_queryset(self):
        discovery_service = DiscoveryService(self.request.user)
        return discovery_service.get_potential_matches()

class LikeUserView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LikeSerializer
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        matching_service = MatchingService(request.user)
        
        # Check daily likes limit
        request.user.reset_daily_likes()
        if request.user.likes_remaining_today <= 0 and not request.user.has_premium():
            return Response({'error': 'Daily likes limit reached'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Create like
        result = matching_service.like_user(to_user_id)
        
        if result['success']:
            # Decrement likes remaining
            request.user.likes_remaining_today -= 1
            request.user.save()
            
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class PassUserView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        matching_service = MatchingService(request.user)
        
        result = matching_service.pass_user(to_user_id)
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class MyMatchesView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MatchSerializer
    
    def get_queryset(self):
        return Match.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user),
            is_active=True
        ).order_by('-created_at')

class UnlikeUserView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, to_user_id):
        matching_service = MatchingService(request.user)
        result = matching_service.unlike_user(to_user_id)
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)