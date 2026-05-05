from rest_framework.throttling import SimpleRateThrottle

class LikeThrottle(SimpleRateThrottle):
    scope = 'like'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            # Premium users have higher limits
            if request.user.has_premium():
                return None  # No throttle for premium users
            
            return f"like_{request.user.id}"
        return None

class MessageThrottle(SimpleRateThrottle):
    scope = 'message'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            if request.user.has_premium():
                return None
            
            return f"message_{request.user.id}"
        return None

class DiscoveryThrottle(SimpleRateThrottle):
    scope = 'discovery'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"discovery_{request.user.id}"
        return None