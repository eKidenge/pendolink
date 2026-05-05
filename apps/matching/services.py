from django.db.models import Q
from django.utils import timezone
from .models import Like, Match, Pass
from apps.ai_engine.services import CompatibilityScorer

class MatchingService:
    def __init__(self, user):
        self.user = user
    
    def like_user(self, to_user_id):
        """Process a like from current user to another user"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            to_user = User.objects.get(id=to_user_id)
            
            # Check if already liked
            if Like.objects.filter(from_user=self.user, to_user=to_user).exists():
                return {'success': False, 'error': 'Already liked this user'}
            
            # Check if passed
            if Pass.objects.filter(from_user=self.user, to_user=to_user).exists():
                return {'success': False, 'error': 'You passed on this user'}
            
            # Create like
            like = Like.objects.create(from_user=self.user, to_user=to_user)
            
            # Check for mutual like
            mutual_like = Like.objects.filter(from_user=to_user, to_user=self.user).exists()
            
            if mutual_like:
                # Create match
                scorer = CompatibilityScorer()
                score = scorer.calculate_compatibility(self.user.id, to_user.id)
                
                match = Match.objects.create(
                    user1=self.user,
                    user2=to_user,
                    compatibility_score=score['total_score'],
                    matched_by='mutual_like'
                )
                
                # Update like as mutual
                like.is_mutual = True
                like.save()
                
                # Create conversation for match
                from apps.chat.models import Conversation
                Conversation.objects.create(match=match)
                
                return {
                    'success': True,
                    'is_match': True,
                    'match_id': match.id,
                    'conversation_id': match.conversation.id if hasattr(match, 'conversation') else None
                }
            
            return {'success': True, 'is_match': False}
            
        except User.DoesNotExist:
            return {'success': False, 'error': 'User not found'}
    
    def pass_user(self, to_user_id):
        """Process a pass from current user to another user"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            to_user = User.objects.get(id=to_user_id)
            
            # Create pass
            Pass.objects.get_or_create(from_user=self.user, to_user=to_user)
            
            return {'success': True}
            
        except User.DoesNotExist:
            return {'success': False, 'error': 'User not found'}
    
    def unlike_user(self, to_user_id):
        """Remove a like"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            to_user = User.objects.get(id=to_user_id)
            like = Like.objects.filter(from_user=self.user, to_user=to_user).first()
            
            if like:
                # Check if there's a match
                match = Match.objects.filter(
                    (Q(user1=self.user) & Q(user2=to_user)) |
                    (Q(user1=to_user) & Q(user2=self.user))
                ).first()
                
                if match:
                    match.delete()
                
                like.delete()
                return {'success': True}
            
            return {'success': False, 'error': 'Like not found'}
            
        except User.DoesNotExist:
            return {'success': False, 'error': 'User not found'}

class DiscoveryService:
    def __init__(self, user):
        self.user = user
    
    def get_potential_matches(self, limit=20):
        """Get potential matches for the user"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get users to exclude (already liked, passed, matched, or self)
        liked_users = Like.objects.filter(from_user=self.user).values_list('to_user_id', flat=True)
        passed_users = Pass.objects.filter(from_user=self.user).values_list('to_user_id', flat=True)
        matched_users = Match.objects.filter(
            Q(user1=self.user) | Q(user2=self.user)
        ).values_list('user1_id', 'user2_id')
        
        matched_ids = set()
        for u1, u2 in matched_users:
            if u1 == self.user.id:
                matched_ids.add(u2)
            else:
                matched_ids.add(u1)
        
        excluded = set(list(liked_users) + list(passed_users) + list(matched_ids))
        excluded.add(self.user.id)
        
        # Get preferences
        preferences = self.user.profile if hasattr(self.user, 'profile') else None
        
        # Query potential matches
        potential = User.objects.filter(
            is_active=True,
            profile__is_active=True
        ).exclude(id__in=excluded)
        
        # Apply age filter
        if preferences and preferences.age_min and preferences.age_max:
            from datetime import date
            today = date.today()
            min_birth_year = today.year - preferences.age_max
            max_birth_year = today.year - preferences.age_min
            potential = potential.filter(
                date_of_birth__year__gte=min_birth_year,
                date_of_birth__year__lte=max_birth_year
            )
        
        # Apply looking for filter
        if self.user.looking_for:
            potential = potential.filter(gender=self.user.looking_for)
        
        # Apply gender filter
        if preferences and hasattr(preferences, 'looking_for_gender') and preferences.looking_for_gender:
            potential = potential.filter(gender=preferences.looking_for_gender)
        
        # Limit results
        potential = potential[:limit]
        
        # Calculate match scores
        scorer = CompatibilityScorer()
        results = []
        
        for user in potential:
            score = scorer.calculate_compatibility(self.user.id, user.id)
            results.append({
                'id': user.id,
                'username': user.username,
                'age': self._calculate_age(user.date_of_birth),
                'match_score': score['total_score'],
                'distance': self._calculate_distance(user),
                'bio': user.profile.bio if hasattr(user, 'profile') else '',
                'interests': user.profile.interests if hasattr(user, 'profile') else [],
                'profile_picture': user.profile.profile_picture.url if hasattr(user, 'profile') and user.profile.profile_picture else None,
                'photos': user.profile.photos if hasattr(user, 'profile') else [],
                'is_verified': user.is_verified,
                'is_premium': user.is_premium,
                'is_online': self._is_online(user),
            })
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results
    
    def _calculate_age(self, date_of_birth):
        if date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
        return None
    
    def _calculate_distance(self, user):
        """Calculate distance between users using haversine formula"""
        from math import radians, sin, cos, sqrt, asin
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return R * c
        
        # Get user locations
        user1_loc = hasattr(self.user, 'location') and self.user.location
        user2_loc = hasattr(user, 'location') and user.location
        
        if user1_loc and user2_loc and user1_loc.latitude and user1_loc.longitude and user2_loc.latitude and user2_loc.longitude:
            return round(haversine(
                float(user1_loc.latitude), float(user1_loc.longitude),
                float(user2_loc.latitude), float(user2_loc.longitude)
            ), 1)
        
        return 999  # Unknown distance
    
    def _is_online(self, user):
        """Check if user was active in last 5 minutes"""
        from django.utils import timezone
        from datetime import timedelta
        return user.last_active and user.last_active > timezone.now() - timedelta(minutes=5)

def update_user_matching_radius(user):
    """Update user's matching radius based on location"""
    # Simple implementation - can be expanded
    if hasattr(user, 'location') and user.location:
        # Update radius based on location density
        pass
    return True

# Add to existing services.py file

class MatchService:
    def __init__(self, user):
        self.user = user
    
    def get_active_matches(self):
        """Get all active matches for user"""
        return Match.objects.filter(
            Q(user1=self.user) | Q(user2=self.user),
            is_active=True
        ).order_by('-created_at')
    
    def unmatch(self, match_id):
        """Unmatch a user"""
        try:
            match = Match.objects.get(
                Q(user1=self.user) | Q(user2=self.user),
                id=match_id,
                is_active=True
            )
            match.is_active = False
            match.save()
            
            # Archive conversation
            if hasattr(match, 'conversation'):
                match.conversation.is_active = False
                match.conversation.save()
            
            return {'success': True}
        except Match.DoesNotExist:
            return {'success': False, 'error': 'Match not found'}
    
    def get_match_compatibility(self, match_id):
        """Get compatibility details for a match"""
        try:
            match = Match.objects.get(id=match_id)
            other_user = match.user2 if match.user1 == self.user else match.user1
            
            from apps.ai_engine.models import CompatibilityScore
            score = CompatibilityScore.objects.filter(
                user1=min(self.user.id, other_user.id),
                user2=max(self.user.id, other_user.id)
            ).first()
            
            if score:
                return {
                    'overall': score.total_score,
                    'interests': score.interest_score,
                    'personality': score.personality_score,
                    'behavior': score.behavior_score,
                    'location': score.location_score
                }
            
            return {'overall': match.compatibility_score}
        except Match.DoesNotExist:
            return {'overall': 0}