from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allows access to object owner or admin"""
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object owners can edit, others can only read"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False

class HasPremiumAccess(permissions.BasePermission):
    """Check if user has premium subscription"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow access if user is premium
        return request.user.has_premium()

class CanLike(permissions.BasePermission):
    """Check if user can perform like action (rate limiting)"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Reset daily likes if needed
        request.user.reset_daily_likes()
        
        # Check if user has likes remaining
        if request.user.likes_remaining_today > 0:
            return True
        
        # Premium users have unlimited likes
        return request.user.has_premium()

class CanMessage(permissions.BasePermission):
    """Check if user can send messages"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Free users have limited messages per day
        if not request.user.has_premium():
            # Check daily message limit (implement similar to likes)
            pass
        
        return True

class CanSeeWhoLiked(permissions.BasePermission):
    """Check if user can see who liked them"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.has_premium()

class VerifiedUserOnly(permissions.BasePermission):
    """Only allow verified users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified