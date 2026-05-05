import json
from django.db.models import Q
from django.core.cache import cache
from .models import CompatibilityScore, UserEmbedding

class CompatibilityScorer:
    def __init__(self):
        self.weights = {
            'interests': 0.40,
            'personality': 0.25,
            'behavior': 0.20,
            'location': 0.15
        }
    
    def calculate_compatibility(self, user1_id, user2_id):
        """Calculate compatibility score between two users"""
        # Check cache
        cache_key = f"compat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Get or create score from database
        score, created = CompatibilityScore.objects.get_or_create(
            user1_id=min(user1_id, user2_id),
            user2_id=max(user1_id, user2_id)
        )
        
        if created or not score.total_score:
            # Calculate scores
            interest_score = self._calculate_interest_similarity(user1_id, user2_id)
            personality_score = self._calculate_personality_fit(user1_id, user2_id)
            behavior_score = self._calculate_behavior_prediction(user1_id, user2_id)
            location_score = self._calculate_location_score(user1_id, user2_id)
            
            # Calculate total
            total = (
                interest_score * self.weights['interests'] +
                personality_score * self.weights['personality'] +
                behavior_score * self.weights['behavior'] +
                location_score * self.weights['location']
            )
            
            # Update database
            score.interest_score = interest_score
            score.personality_score = personality_score
            score.behavior_score = behavior_score
            score.location_score = location_score
            score.total_score = total
            score.save()
        
        # Cache for 24 hours
        cache.set(cache_key, {
            'total_score': score.total_score,
            'interest_score': score.interest_score,
            'personality_score': score.personality_score,
            'behavior_score': score.behavior_score,
            'location_score': score.location_score
        }, 86400)
        
        return {
            'total_score': score.total_score,
            'interest_score': score.interest_score,
            'personality_score': score.personality_score,
            'behavior_score': score.behavior_score,
            'location_score': score.location_score
        }
    
    def _calculate_interest_similarity(self, user1_id, user2_id):
        """Calculate interest overlap percentage"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        
        interests1 = set(user1.profile.interests if hasattr(user1, 'profile') else [])
        interests2 = set(user2.profile.interests if hasattr(user2, 'profile') else [])
        
        if not interests1 or not interests2:
            return 50  # Default 50% if no interests
        
        intersection = interests1.intersection(interests2)
        union = interests1.union(interests2)
        
        return (len(intersection) / len(union)) * 100 if union else 50
    
    def _calculate_personality_fit(self, user1_id, user2_id):
        """Calculate personality compatibility"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        
        traits1 = user1.profile.personality_traits if hasattr(user1, 'profile') else {}
        traits2 = user2.profile.personality_traits if hasattr(user2, 'profile') else {}
        
        if not traits1 or not traits2:
            return 65  # Default
        
        total = 0
        count = 0
        
        for trait in traits1:
            if trait in traits2:
                diff = abs(traits1[trait] - traits2[trait])
                score = 100 - diff
                total += score
                count += 1
        
        return total / count if count > 0 else 70
    
    def _calculate_behavior_prediction(self, user1_id, user2_id):
        """Predict match success based on behavior patterns"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from apps.matching.models import Like, Match
        
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        
        # Check if they've liked similar people
        user1_likes = set(Like.objects.filter(from_user=user1).values_list('to_user_id', flat=True))
        user2_likes = set(Like.objects.filter(from_user=user2).values_list('to_user_id', flat=True))
        
        similar_likes = user1_likes.intersection(user2_likes)
        like_similarity = (len(similar_likes) / max(len(user1_likes), len(user2_likes), 1)) * 100
        
        # Check response rates
        user1_matches = Match.objects.filter(user1=user1).count() + Match.objects.filter(user2=user1).count()
        user2_matches = Match.objects.filter(user1=user2).count() + Match.objects.filter(user2=user2).count()
        
        # Activity level
        from datetime import timedelta
        from django.utils import timezone
        
        recent_activity1 = user1.last_active > timezone.now() - timedelta(days=7)
        recent_activity2 = user2.last_active > timezone.now() - timedelta(days=7)
        
        activity_bonus = 20 if recent_activity1 and recent_activity2 else 10
        
        # Combine scores
        score = (like_similarity * 0.6) + activity_bonus
        
        return min(score, 100)
    
    def _calculate_location_score(self, user1_id, user2_id):
        """Calculate location compatibility based on distance"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from math import radians, sin, cos, sqrt, asin
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return R * c
        
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        
        loc1 = hasattr(user1, 'location') and user1.location
        loc2 = hasattr(user2, 'location') and user2.location
        
        if loc1 and loc2 and loc1.latitude and loc1.longitude and loc2.latitude and loc2.longitude:
            distance = haversine(
                float(loc1.latitude), float(loc1.longitude),
                float(loc2.latitude), float(loc2.longitude)
            )
            
            # Score decreases with distance
            if distance <= 5:
                return 100
            elif distance <= 10:
                return 90
            elif distance <= 25:
                return 75
            elif distance <= 50:
                return 60
            elif distance <= 100:
                return 40
            else:
                return 20
        
        return 50  # Default if no location
    
    def update_model_with_feedback(self, user, feedback_data):
        """Update AI model with user feedback to improve future matches"""
        # Store feedback for ML model training
        from .models import AIFeedback
        AIFeedback.objects.create(
            user=user,
            match_id=feedback_data.get('match_id'),
            rating=feedback_data.get('rating'),
            was_successful=feedback_data.get('was_successful', False),
            chat_messages_count=feedback_data.get('chat_messages_count', 0),
            feedback_text=feedback_data.get('feedback_text', '')
        )
        return True

class RecommendationEngine:
    def __init__(self, user):
        self.user = user
    
    def get_recommendations(self, limit=20):
        """Get AI-powered recommendations for user"""
        from apps.matching.services import DiscoveryService
        
        # Use discovery service to get potential matches
        discovery = DiscoveryService(self.user)
        potential = discovery.get_potential_matches(limit * 2)
        
        # Score and sort
        scorer = CompatibilityScorer()
        for user_data in potential:
            score = scorer.calculate_compatibility(self.user.id, user_data['id'])
            user_data['ai_score'] = score['total_score']
        
        # Sort by AI score
        potential.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        
        # Log recommendations
        from .models import AIRecommendationLog
        AIRecommendationLog.objects.create(
            user=self.user,
            recommended_users=[u['id'] for u in potential[:limit]],
            scores=[u.get('ai_score', 0) for u in potential[:limit]],
            context={'timestamp': 'auto'}
        )
        
        return potential[:limit]