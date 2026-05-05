from django.urls import path
from .views import (
    DiscoveryView, LikeUserView, PassUserView, 
    MyMatchesView, UnlikeUserView,
    dashboard_page, discover_page, matches_page  # Add these imports
)

urlpatterns = [
    # Template pages (for browser)
    path('dashboard/', dashboard_page, name='dashboard'),
    path('discover/', discover_page, name='discover'),
    path('matches/', matches_page, name='matches'),
    
    # API endpoints (for AJAX/mobile)
    path('api/discover/', DiscoveryView.as_view(), name='api_discover'),
    path('api/like/<int:to_user_id>/', LikeUserView.as_view(), name='api_like'),
    path('api/pass/<int:to_user_id>/', PassUserView.as_view(), name='api_pass'),
    path('api/matches/', MyMatchesView.as_view(), name='api_matches'),
    path('api/unlike/<int:to_user_id>/', UnlikeUserView.as_view(), name='api_unlike'),
]